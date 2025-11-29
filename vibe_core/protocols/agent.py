"""
VibeAgent Protocol - Interface Definition

All agents running in VibeOS must implement this protocol.
This is the contract between the kernel and cartridges.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import asyncio
import logging


@dataclass
class AgentResponse:
    """Standard response from an agent"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class Capability(str, Enum):
    """Standard capabilities that agents can declare"""

    CONTENT_GENERATION = "content_generation"
    BROADCASTING = "broadcasting"
    GOVERNANCE = "governance"
    VOTING = "voting"
    REGISTRY = "registry"
    LICENSING = "licensing"
    LEDGER = "ledger"
    RESEARCH = "research"
    AUDITING = "auditing"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentManifest:
    """STEWARD Protocol Agent Identity & Capabilities (ARCH-050)"""

    agent_id: str
    name: str
    version: str
    author: str
    description: str
    domain: str  # e.g., "GOVERNANCE", "MEDIA", "RESEARCH"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "domain": self.domain,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
        }


class VibeAgent(ABC):
    """
    Base Protocol for All Agents in VibeOS

    Every cartridge must implement this interface to run in the kernel.
    The kernel uses these methods to:
    1. Discover and load agents
    2. Query capabilities and status
    3. Submit and process tasks
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str = "1.0.0",
        author: str = "Steward Protocol",
        description: str = "",
        domain: str = "",
        capabilities: Optional[List[str]] = None,
        config: Optional[Any] = None,
    ):
        """Initialize a VibeAgent"""
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.domain = domain
        self.capabilities = capabilities or []
        self.config = config
        self.kernel = None  # Will be injected by VibeKernel.boot()
        self.kernel_pipe = None  # IPC Pipe for Process Isolation

        # Phase 4: Filesystem & Network (injected by kernel)
        self.vfs = None  # Virtual Filesystem
        self.network = None  # Network Proxy

    def set_kernel(self, kernel: "VibeKernel") -> None:
        """
        Kernel Injection Pattern

        Called by VibeKernel.boot() to give agents access to the kernel.
        This allows agents to:
        - Query other agents via kernel.agent_registry
        - Submit tasks via kernel.scheduler.submit_task()
        - Access ledger via kernel.ledger
        """
        self.kernel = kernel

    def set_kernel_pipe(self, pipe: Any) -> None:
        """
        Inject IPC Pipe for Process Isolation.

        Phase 4b: MONKEY PATCH builtins to redirect to VFS/Network Proxy.

        This is system call interception at Python level.
        Agents use open() and requests.get() as normal,
        but we redirect them to sandboxed versions.
        """
        import logging

        logger = logging.getLogger(f"AGENT.{self.agent_id}")

        self.kernel_pipe = pipe

        # Phase 4: Initialize VFS and Network for this agent
        try:
            from vibe_core.vfs import VirtualFileSystem
            from vibe_core.network_proxy import KernelNetworkProxy

            self.vfs = VirtualFileSystem(self.agent_id)

            # Network proxy wrapper
            class AgentNetworkProxy:
                def __init__(self, agent_id, kernel_network):
                    self.agent_id = agent_id
                    self._kernel_network = kernel_network

                def request(self, method, url, **kwargs):
                    return self._kernel_network.request(
                        self.agent_id, method, url, **kwargs
                    )

                def get(self, url, **kwargs):
                    return self._kernel_network.get(self.agent_id, url, **kwargs)

                def post(self, url, **kwargs):
                    return self._kernel_network.post(self.agent_id, url, **kwargs)

            self.network = AgentNetworkProxy(self.agent_id, KernelNetworkProxy())

            # ============================================================
            # MONKEY PATCH: Override builtins.open
            # ============================================================
            import builtins

            original_open = builtins.open
            vfs = self.vfs  # Capture in closure
            agent_id = self.agent_id

            def vfs_open(file, mode="r", *args, **kwargs):
                """
                Intercepted open() that redirects to VFS.

                WARNING: This does NOT intercept C-level file operations
                (e.g., sqlite3, pandas). Those must be configured explicitly.
                """
                # Only intercept string paths
                if isinstance(file, str):
                    logger.info(f"[VFS-INTERCEPT] {agent_id} open('{file}', '{mode}')")
                    try:
                        return vfs.open(file, mode, *args, **kwargs)
                    except PermissionError as e:
                        logger.warning(
                            f"[VFS-BLOCKED] {agent_id} denied access to '{file}': {e}"
                        )
                        raise
                else:
                    # File-like object, pass through
                    return original_open(file, mode, *args, **kwargs)

            # Replace open in builtins
            builtins.open = vfs_open
            logger.info(f"🔧 {self.agent_id}: Monkey-patched builtins.open → VFS")

            # ============================================================
            # MONKEY PATCH: Override requests module
            # ============================================================
            try:
                import sys
                import requests as original_requests

                network = self.network  # Capture in closure

                class VFSRequests:
                    """
                    Wrapper that redirects all requests to network proxy.
                    """

                    def __init__(self):
                        # Preserve original for internal use if needed
                        self._original = original_requests

                    def request(self, method, url, **kwargs):
                        logger.info(f"[NET-INTERCEPT] {agent_id} {method} {url}")
                        try:
                            return network.request(method, url, **kwargs)
                        except PermissionError as e:
                            logger.warning(
                                f"[NET-BLOCKED] {agent_id} denied {url}: {e}"
                            )
                            raise

                    def get(self, url, **kwargs):
                        return self.request("GET", url, **kwargs)

                    def post(self, url, **kwargs):
                        return self.request("POST", url, **kwargs)

                    def put(self, url, **kwargs):
                        return self.request("PUT", url, **kwargs)

                    def delete(self, url, **kwargs):
                        return self.request("DELETE", url, **kwargs)

                    # Preserve common attributes
                    Session = original_requests.Session
                    Response = original_requests.Response
                    HTTPError = original_requests.HTTPError

                # Replace requests in sys.modules
                sys.modules["requests"] = VFSRequests()
                logger.info(
                    f"🔧 {self.agent_id}: Monkey-patched requests → Network Proxy"
                )

            except ImportError:
                logger.debug(
                    f"⚠️  requests module not available, skipping network patch"
                )

        except Exception as e:
            logger.error(
                f"❌ Failed to initialize VFS/Network for {self.agent_id}: {e}"
            )
            import traceback

            traceback.print_exc()

    def get_sandbox_path(self) -> str:
        """
        Get absolute path to agent's sandbox directory.

        This is for C-extensions (sqlite3, pandas, etc.) that bypass
        Python monkey-patching and need explicit paths.

        Returns:
            Absolute path to sandbox (e.g., /tmp/vibe_os/agents/{agent_id})
        """
        if self.vfs:
            return str(self.vfs.get_sandbox_path())
        else:
            # Fallback if VFS not initialized yet
            from pathlib import Path

            return str(Path(f"/tmp/vibe_os/agents/{self.agent_id}").resolve())

    def send_to_kernel(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the Kernel via IPC.
        """
        if self.kernel_pipe:
            self.kernel_pipe.send(message)
        elif self.kernel:
            # Fallback for legacy in-process mode (if needed)
            pass
        else:
            logging.warning(f"Agent {self.agent_id} has no kernel connection")

    @abstractmethod
    def process(self, task: "Task") -> Dict[str, Any]:
        """
        Process a Task from the kernel scheduler

        Args:
            task: Task object with agent_id, payload, id

        Returns:
            Dictionary with task result {status, output, error, ...}
        """
        pass

    def get_manifest(self) -> AgentManifest:
        """
        Return this agent's manifest (identity + capabilities)

        Called by kernel.manifest_registry during boot.
        This is how the kernel discovers what you can do.
        """
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
        )

    def report_status(self) -> Dict[str, Any]:
        """
        Report current agent status (optional)

        Used by introspection and monitoring.
        Default implementation is minimal.
        Override for detailed status reporting.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "capabilities": self.capabilities,
        }

    async def emit_event(
        self,
        event_type: str,
        message: str = "",
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Emit an event for real-time monitoring (Canto 10: Pulse System)

        This allows agents to broadcast their state changes to the event bus.
        Events are visualized in real-time on the Live Darshan dashboard.

        Args:
            event_type: Type of event (THOUGHT, ACTION, ERROR, VIOLATION, etc.)
            message: Human-readable event description
            task_id: Optional task ID associated with this event
            details: Optional dictionary with additional event details

        Example:
            await agent.emit_event("THOUGHT", "Planning response", task_id="t123")
            await agent.emit_event("ACTION", "Posting to Twitter")
            await agent.emit_event("ERROR", "Failed to validate signature", details={"error": "..."})
        """
        try:
            # Import here to avoid circular dependency
            from vibe_core.event_bus import emit_event

            await emit_event(
                event_type=event_type,
                agent_id=self.agent_id,
                message=message,
                task_id=task_id,
                details=details or {},
            )
        except Exception as e:
            logger = logging.getLogger("VibeAgent")
            logger.warning(f"⚠️  Failed to emit event: {e}")

    def emit_event_sync(
        self,
        event_type: str,
        message: str = "",
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Synchronous wrapper for emit_event (for use in non-async contexts)

        This is a convenience method for agents that operate in sync contexts.
        It tries to emit via the event bus if an event loop is available.

        Args:
            event_type: Type of event
            message: Event description
            task_id: Optional task ID
            details: Optional event details
        """
        try:
            # Try to get running loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule the coroutine
                asyncio.create_task(
                    self.emit_event(event_type, message, task_id, details)
                )
            else:
                # No running loop, try to run in new task
                asyncio.run(self.emit_event(event_type, message, task_id, details))
        except RuntimeError:
            # No event loop available, silently skip
            pass
        except Exception as e:
            logger = logging.getLogger("VibeAgent")
            logger.debug(f"⚠️  Sync event emission failed: {e}")
