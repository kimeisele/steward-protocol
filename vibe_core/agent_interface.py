"""
AGENT SYSTEM INTERFACE - The Bridge Between Kernel and Agents
==============================================================
"""

from __future__ import annotations

__doc__ = """

Goal: Provide agents with standardized API to access kernel capabilities
Strategy: Inject this interface as agent.system in every registered agent

Philosophy:
"Agents don't touch the kernel directly. They speak through the interface."

Architecture:
    ┌─────────────┐
    │   KERNEL    │  ← Has VFS, Config, Dependency Mgmt
    ├─────────────┤
    │   SYSTEM    │  ← AgentSystemInterface (THIS FILE)
    │  INTERFACE  │
    ├─────────────┤
    │   AGENTS    │  ← Use self.system.* methods
    └─────────────┘

Usage (in agent code):
    # Dependency Management
    self.system.add_dependency("pandas", ">=2.0.0")
    deps = self.system.get_dependencies()

    # File I/O (sandboxed via VFS)
    self.system.write_file("proposals/prop_001.json", content)
    content = self.system.read_file("proposals/prop_001.json")

    # Config Access
    frequency = self.system.get_config("posting_frequency_hours")
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import IO, TYPE_CHECKING, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel import VibeKernel

logger = logging.getLogger("AGENT_INTERFACE")


class AgentSystemInterface:
    """
    System interface injected into every agent.

    This is the ONLY way agents should interact with:
    - Filesystem (via VFS)
    - Dependencies (via DependencyManager)
    - Configuration (via Config)
    - Kernel capabilities

    Agents that bypass this interface violate system architecture.
    """

    def __init__(self, kernel: VibeKernel, agent_id: str):
        """
        Initialize system interface for an agent.

        Args:
            kernel: Reference to VibeKernel
            agent_id: Agent identifier

        Note: This is called by kernel during agent registration.
        """
        self.kernel = kernel
        self.agent_id = agent_id

        # VFS: Sandboxed filesystem for this agent
        from vibe_core.vfs import VirtualFileSystem

        self.vfs = VirtualFileSystem(agent_id)

        # 🍎 STATE: Namespaced state service (ADR-204)
        from vibe_core.state.state_service import get_state_service

        self.state = get_state_service(agent_id=agent_id)

        # Config: Agent-specific configuration
        # Access via kernel's CityConfig.agents.{agent_id}
        self.config = self._get_agent_config()

        # Dependency Manager: Shared across all agents (singleton)
        from vibe_core.dependency_manager import DependencyManager

        try:
            self._dep_manager = DependencyManager()
        except Exception as e:
            logger.warning(f"⚠️  DependencyManager unavailable for {agent_id}: {e}")
            self._dep_manager = None

        logger.info(f"🔌 SystemInterface initialized for {agent_id}")

    def _get_agent_config(self) -> Dict[str, object]:
        """Get agent-specific configuration from kernel."""
        try:
            # Access kernel's config (CityConfig)
            if hasattr(self.kernel, "config") and self.kernel.config:
                city_config = self.kernel.config

                # Get agent-specific config (e.g., HeraldConfig)
                if hasattr(city_config, "agents"):
                    agent_configs = city_config.agents

                    # Get config for this agent
                    if hasattr(agent_configs, self.agent_id):
                        agent_config = getattr(agent_configs, self.agent_id)
                        # Convert Pydantic model to dict
                        return agent_config.model_dump() if hasattr(agent_config, "model_dump") else {}

            logger.debug(f"ℹ️  No specific config found for {self.agent_id}, using defaults")
            return {}

        except Exception as e:
            logger.warning(f"⚠️  Failed to load config for {self.agent_id}: {e}")
            return {}

    # ============================================================================
    # DEPENDENCY MANAGEMENT
    # ============================================================================

    def add_dependency(self, package: str, version: Optional[str] = None) -> None:
        """
        Add a dependency to pyproject.toml.

        Args:
            package: Package name (e.g., "pandas")
            version: Version constraint (e.g., ">=2.0.0")

        Example:
            self.system.add_dependency("pandas", ">=2.0.0")
            self.system.add_dependency("requests")

        Note: This replaces creating requirements.txt files.
        """
        if not self._dep_manager:
            raise RuntimeError(f"DependencyManager not available. Agent {self.agent_id} cannot add dependencies.")

        logger.info(f"📦 {self.agent_id} requesting dependency: {package} {version or ''}")
        self._dep_manager.add_dependency(package, version)

    def get_dependencies(self) -> List[str]:
        """
        Get all project dependencies.

        Returns:
            List of dependency strings (e.g., ["pandas>=2.0.0"])
        """
        if not self._dep_manager:
            return []

        return self._dep_manager.get_dependencies()

    def has_dependency(self, package: str) -> bool:
        """
        Check if a dependency exists.

        Args:
            package: Package name

        Returns:
            True if dependency exists
        """
        if not self._dep_manager:
            return False

        return self._dep_manager.has_dependency(package)

    # ============================================================================
    # FILESYSTEM (VFS - SANDBOXED)
    # ============================================================================

    def write_file(self, path: str, content: str) -> None:
        """
        Write a file in agent's sandbox.

        Args:
            path: Relative path within sandbox (e.g., "proposals/prop_001.json")
            content: File content

        Example:
            self.system.write_file("proposals/prop_001.json", json.dumps(data))

        Note: File is written to /tmp/vibe_os/agents/{agent_id}/{path}
        """
        logger.debug(f"📝 {self.agent_id} writing file: {path}")
        self.vfs.write_text(path, content)

    def read_file(self, path: str) -> str:
        """
        Read a file from agent's sandbox.

        Args:
            path: Relative path within sandbox

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If path escapes sandbox
        """
        logger.debug(f"📖 {self.agent_id} reading file: {path}")
        return self.vfs.read_text(path)

    def file_exists(self, path: str) -> bool:
        """Check if file exists in sandbox."""
        return self.vfs.exists(path)

    def list_files(self, path: str = ".") -> List[str]:
        """
        List files in a directory within sandbox.

        Args:
            path: Directory path (default: root of sandbox)

        Returns:
            List of filenames
        """
        return self.vfs.listdir(path)

    def open_file(self, path: str, mode: str = "r", **kwargs) -> IO:
        """
        Open a file within sandbox (context manager support).

        Args:
            path: File path
            mode: File mode (r, w, a, rb, wb, etc.)

        Returns:
            File handle

        Example:
            with self.system.open_file("data.json", "w") as f:
                json.dump(data, f)
        """
        return self.vfs.open(path, mode, **kwargs)

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    def get_config(self, key: str, default: object = None) -> object:
        """
        Get agent-specific configuration value.

        Args:
            key: Config key (e.g., "posting_frequency_hours")
            default: Default value if key not found

        Returns:
            Config value or default

        Example:
            frequency = self.system.get_config("posting_frequency_hours", 2)
        """
        return self.config.get(key, default)

    def get_all_config(self) -> Dict[str, object]:
        """Get all configuration for this agent."""
        return self.config.copy()

    # ============================================================================
    # KERNEL INTEGRATION
    # ============================================================================

    def get_agent_manifest(self, agent_id: str):
        """
        Get manifest of another agent.

        Args:
            agent_id: Agent to query

        Returns:
            AgentManifest or None
        """
        return self.kernel.get_agent_manifest(agent_id)

    def find_agents_by_capability(self, capability: str):
        """
        Find agents with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with that capability
        """
        return self.kernel.find_agents_by_capability(capability)

    def record_event(self, event_type: str, details: Dict[str, object]) -> str:
        """
        Record an event in the immutable ledger.

        Args:
            event_type: Type of event (e.g., "proposal_created")
            details: Event-specific data

        Returns:
            Event ID

        Example:
            event_id = self.system.record_event(
                "proposal_created",
                {"title": "...", "action": "..."}
            )
        """
        return self.kernel.ledger.record_event(event_type, self.agent_id, details)

    def get_sandbox_path(self) -> Path:
        """
        Get absolute path to agent's sandbox directory.

        Returns:
            Path to /tmp/vibe_os/agents/{agent_id}

        Note: Only use this for debugging. Normal file I/O should use write_file/read_file.
        """
        return self.vfs.get_sandbox_path()

    def publish_artifact(self, sandbox_path: str, target_path: str) -> bool:
        """
        Publish an artifact from agent sandbox to project root.

        CRITICAL SECURITY: Only whitelisted agents can publish to root.
        This prevents unauthorized writes while allowing controlled publishing.

        Args:
            sandbox_path: Path relative to agent sandbox (e.g., "docs/README.md")
            target_path: Path relative to project root (e.g., "README.md")

        Returns:
            True if published successfully

        Raises:
            PermissionError: If agent is not authorized to publish
            FileNotFoundError: If source file doesn't exist in sandbox

        Example:
            # Scribe writes to sandbox, then publishes to root
            self.system.write_file("docs/README.md", content)
            self.system.publish_artifact("docs/README.md", "README.md")
        """
        # SECURITY: Capability-Based Access Control
        # Instead of a hardcoded whitelist, we check if the agent has the 'publish_root' capability.
        if not self.kernel._check_agent_capability(self.agent_id, "publish_root"):
            raise PermissionError(
                f"Agent {self.agent_id} is not authorized to publish to project root. "
                f"Requires 'publish_root' capability."
            )

        # Resolve source path (in sandbox)
        source = self.vfs.get_sandbox_path() / sandbox_path

        if not source.exists():
            raise FileNotFoundError(f"Source file not found in sandbox: {sandbox_path} (resolved to: {source})")

        # Resolve target path (in project root)
        target = (Path(".") / target_path).resolve()
        project_root = Path(".").resolve()

        # SECURITY: Path Traversal Protection
        # Ensure target is within project root (prevent ../../../etc/passwd)
        if not str(target).startswith(str(project_root)):
            raise PermissionError(
                f"Path traversal attempt blocked: {target_path} "
                f"(resolves to: {target}, outside project root: {project_root})"
            )

        # Create target directory if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        # Atomic copy (copy2 preserves metadata)
        import shutil

        shutil.copy2(source, target)

        logger.info(f"📤 {self.agent_id} published artifact: {sandbox_path} → {target_path}")
        return True

    # ============================================================================
    # DATA EXCHANGE (PHASE 4: WIRING - INTER-AGENT COMMUNICATION)
    # ============================================================================

    def publish_data(self, key: str, value: object) -> str:
        """
        Publish data for other agents to consume.

        This enables consent-based data exchange between agents without
        direct kernel access (Article V: Consent).

        Args:
            key: Data identifier (e.g., "citizens", "stats", "config")
            value: Data to publish (must be JSON-serializable)

        Returns:
            event_id: Audit trail event ID

        Example:
            # Civic publishes citizen list
            self.system.publish_data("citizens", ["alice", "bob"])

            # Archivist publishes statistics
            self.system.publish_data("stats", {"total_events": 42})

        Note: Published data is accessible via request_data() by other agents.
        """
        # Initialize agent's data store if needed
        if self.agent_id not in self.kernel._data_store:
            self.kernel._data_store[self.agent_id] = {}

        # Publish the data
        self.kernel._data_store[self.agent_id][key] = value

        # Audit trail
        event_id = self.record_event(
            "DATA_PUBLISHED",
            {
                "key": key,
                "value_type": type(value).__name__,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(f"📤 {self.agent_id} published data: {key} (type: {type(value).__name__})")
        return event_id

    def request_data(self, agent_id: str, key: str, default: object = None) -> object:
        """
        Request data from another agent.

        This replaces direct kernel.agent_registry access, ensuring
        consent-based data exchange (Article V: Consent).

        Args:
            agent_id: Agent to request data from (e.g., "civic", "archivist")
            key: Data key to request (e.g., "citizens", "stats")
            default: Value to return if data doesn't exist

        Returns:
            Requested data or default

        Raises:
            ValueError: If agent_id or key doesn't exist AND no default provided

        Example:
            # Herald requests citizen list from Civic
            citizens = self.system.request_data("civic", "citizens")

            # Forum requests stats from Archivist (with fallback)
            stats = self.system.request_data("archivist", "stats", default={})

        Note: Agent must have published the data via publish_data() first.
        """
        # Check if agent has published any data
        if agent_id not in self.kernel._data_store:
            if default is not None:
                logger.debug(
                    f"📥 {self.agent_id} requested data from {agent_id} "
                    f"(key: {key}) - agent has no published data, using default"
                )
                return default
            raise ValueError(
                f"Agent '{agent_id}' has not published any data. "
                f"Available agents: {list(self.kernel._data_store.keys())}"
            )

        # Check if key exists
        if key not in self.kernel._data_store[agent_id]:
            if default is not None:
                logger.debug(
                    f"📥 {self.agent_id} requested data from {agent_id} (key: {key}) - key not found, using default"
                )
                return default
            raise ValueError(
                f"Agent '{agent_id}' has not published data under key '{key}'. "
                f"Available keys: {list(self.kernel._data_store[agent_id].keys())}"
            )

        # Get the data
        value = self.kernel._data_store[agent_id][key]

        # Audit trail
        self.record_event(
            "DATA_REQUESTED",
            {
                "source_agent": agent_id,
                "key": key,
                "value_type": type(value).__name__,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(f"📥 {self.agent_id} requested data from {agent_id}: {key} (type: {type(value).__name__})")
        return value

    def list_published_data(self, agent_id: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all published data keys (for discovery).

        Args:
            agent_id: Specific agent to query (default: all agents)

        Returns:
            {agent_id: [key1, key2, ...]}

        Example:
            # Discover what Civic has published
            civic_data = self.system.list_published_data("civic")
            # Returns: {"civic": ["citizens", "licenses"]}

            # Discover all published data
            all_data = self.system.list_published_data()
        """
        if agent_id:
            if agent_id in self.kernel._data_store:
                return {agent_id: list(self.kernel._data_store[agent_id].keys())}
            return {agent_id: []}

        # Return all agents and their keys
        return {aid: list(data.keys()) for aid, data in self.kernel._data_store.items()}

    def call_agent(self, agent_id: str, payload: Dict[str, object]) -> object:
        """
        Call another agent synchronously (governed inter-agent communication).

        This replaces direct kernel.agent_registry access for agent-to-agent
        calls, ensuring proper audit trail (Article V: Consent).

        Args:
            agent_id: Agent to call (e.g., "civic", "oracle")
            payload: Task payload (dict with "action" and other params)

        Returns:
            Result from the called agent's process() method

        Raises:
            ValueError: If agent doesn't exist
            RuntimeError: If agent call fails

        Example:
            # Herald checks broadcast license with Civic
            result = self.system.call_agent("civic", {
                "action": "check_license",
                "agent_id": "herald"
            })

            # Forum queries Oracle for system stats
            stats = self.system.call_agent("oracle", {
                "action": "get_stats"
            })

        Note: This is for synchronous tight-coupling scenarios. For async
        operations, use kernel.scheduler.submit_task() instead.
        """
        # Check if agent exists
        if agent_id not in self.kernel.agent_registry:
            raise ValueError(
                f"Agent '{agent_id}' not found in registry. Available agents: {list(self.kernel.agent_registry.keys())}"
            )

        # Get the agent
        target_agent = self.kernel.agent_registry[agent_id]

        # Create task
        from vibe_core.scheduling import Task

        task = Task(agent_id=agent_id, payload=payload)

        # Audit trail BEFORE call
        self.record_event(
            "AGENT_CALL_INITIATED",
            {
                "target_agent": agent_id,
                "action": payload.get("action", "unknown"),
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Call the agent
        try:
            result = target_agent.process(task)

            # Audit trail AFTER call
            self.record_event(
                "AGENT_CALL_COMPLETED",
                {
                    "target_agent": agent_id,
                    "action": payload.get("action", "unknown"),
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.info(f"📞 {self.agent_id} called {agent_id} (action: {payload.get('action', 'unknown')})")
            return result

        except Exception as e:
            # Audit trail on failure
            self.record_event(
                "AGENT_CALL_FAILED",
                {
                    "target_agent": agent_id,
                    "action": payload.get("action", "unknown"),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.error(f"❌ {self.agent_id} failed to call {agent_id}: {e}")
            raise RuntimeError(f"Agent call failed: {agent_id}.{payload.get('action', 'unknown')} - {e}") from e

    # ============================================================================
    # TOOL REGISTRY (PHASE 6: UNIVERSAL TOOL ACCESS)
    # ============================================================================

    @property
    def tools(self):
        """
        Access to the kernel's universal tool registry.

        This property provides a read-only view of all tools registered
        with the kernel. Agents use this to discover and execute tools
        without owning tool instances themselves.

        Architecture:
            Agent doesn't own tools → Agent requests tool execution from Kernel
            This enables:
            - Centralized governance (tools can be audited/blocked)
            - Tool discovery (agents see what's available)
            - YAML-based agents (no Python code needed)

        Returns:
            ToolRegistry: The kernel's tool registry

        Example:
            # List available tools
            available = self.system.tools.list_tools()
            # Returns: ["read_file", "write_file", "delegate_task", ...]

            # Get tool info
            tool = self.system.tools.get("read_file")
            print(tool.description)

            # Execute tool directly
            from vibe_core.tools import ToolCall
            result = self.system.tools.execute(
                ToolCall(tool_name="read_file", parameters={"path": "/tmp/test.txt"})
            )
        """
        return self.kernel.tool_registry

    def execute_tool(self, tool_name: str, parameters: Dict[str, object]) -> object:
        """
        Execute a tool via the kernel's tool registry.

        This is the recommended way for agents to use tools. It provides
        a clean interface and proper audit trail.

        Args:
            tool_name: Name of tool to execute (e.g., "read_file")
            parameters: Tool parameters (e.g., {"path": "/tmp/test.txt"})

        Returns:
            ToolResult: Execution result with success/output/error

        Raises:
            ValueError: If tool not found or parameters invalid
            RuntimeError: If tool execution fails critically

        Example:
            # Read a file
            result = self.system.execute_tool("read_file", {
                "path": "/tmp/config.json"
            })

            if result.success:
                content = result.output
                print(f"File content: {content}")
            else:
                logger.error(f"Failed to read file: {result.error}")

            # Write a file
            result = self.system.execute_tool("write_file", {
                "path": "/tmp/output.txt",
                "content": "Hello from agent!"
            })

        Note:
            - All tool calls are logged to kernel ledger
            - Tools respect Soul Governance (invariant checks)
            - Tools can be blocked by governance rules
        """
        from vibe_core.tools import ToolCall

        # Create tool call with caller identity for governance
        call = ToolCall(tool_name=tool_name, parameters=parameters, caller_agent_id=self.agent_id)

        # Record tool call in audit trail
        self.record_event(
            "TOOL_CALL_INITIATED",
            {
                "tool_name": tool_name,
                "parameters_summary": {k: type(v).__name__ for k, v in parameters.items()},
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Execute via kernel registry
        result = self.kernel.tool_registry.execute(call)

        # Record result
        self.record_event(
            "TOOL_CALL_COMPLETED",
            {
                "tool_name": tool_name,
                "success": result.success,
                "error": result.error if not result.success else None,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(f"🔧 {self.agent_id} executed tool '{tool_name}' (success={result.success})")

        return result

    # ============================================================================
    # EVENT BUS (Phase 2: Reactive Patterns)
    # ============================================================================

    def subscribe_to_events(self, callback: Callable, event_type: Optional[str] = None) -> str:
        """
        Subscribe to system-wide events.

        Allows this agent to react to events from other agents.
        Supports reactive patterns and loose coupling.

        Args:
            callback: Function to call when event occurs (sync or async)
            event_type: Optional event type filter (None = all events)

        Returns:
            Subscription ID (for later unsubscribe)

        Example:
            def on_proposal_created(event):
                proposal_id = event.details["proposal_id"]
                print(f"New proposal: {proposal_id}")

            self.system.subscribe_to_events(on_proposal_created, "proposal.created")
        """
        return self.kernel.subscribe_to_events(callback=callback, event_type=event_type, subscriber_id=self.agent_id)

    def unsubscribe_from_events(self, callback: Callable, event_type: Optional[str] = None):
        """
        Unsubscribe from events.

        Args:
            callback: The callback to remove
            event_type: Optional event type (must match subscribe call)
        """
        self.kernel.unsubscribe_from_events(callback, event_type)

    async def broadcast_event(
        self, event_type: str, data: Optional[Dict[str, object]] = None, message: Optional[str] = None
    ) -> Dict[str, object]:
        """
        Broadcast an event to all subscribers.

        Args:
            event_type: Type of event (e.g., "task.complete", "proposal.created")
            data: Optional event data
            message: Optional human-readable message

        Returns:
            Dict with event_id, subscriber_count, timestamp

        Example:
            await self.system.broadcast_event(
                event_type="vote.cast",
                data={"proposal_id": "p123", "vote": "yes"},
                message="Vote recorded"
            )
        """
        return await self.kernel.broadcast_event(
            event_type=event_type, broadcaster_id=self.agent_id, data=data, message=message
        )

    def get_event_history(self, limit: int = 100, event_type: Optional[str] = None) -> List[object]:
        """
        Get recent event history.

        Args:
            limit: Maximum number of events
            event_type: Optional filter by event type

        Returns:
            List of Event objects
        """
        return self.kernel.get_event_history(limit=limit, event_type=event_type)
