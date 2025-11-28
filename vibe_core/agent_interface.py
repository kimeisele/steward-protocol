"""
AGENT SYSTEM INTERFACE - The Bridge Between Kernel and Agents
==============================================================

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
from typing import Any, Dict, List, Optional, IO
from pathlib import Path

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

    def __init__(self, kernel: "VibeKernel", agent_id: str):
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

    def _get_agent_config(self) -> Dict[str, Any]:
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
            raise RuntimeError(
                f"DependencyManager not available. "
                f"Agent {self.agent_id} cannot add dependencies."
            )

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

    def get_config(self, key: str, default: Any = None) -> Any:
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

    def get_all_config(self) -> Dict[str, Any]:
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

    def record_event(self, event_type: str, details: Dict[str, Any]) -> str:
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
        # PHASE 2.5: Whitelist - Only these agents can publish to root
        PUBLISH_WHITELIST = ["scribe"]

        if self.agent_id not in PUBLISH_WHITELIST:
            raise PermissionError(
                f"Agent {self.agent_id} is not authorized to publish to project root. "
                f"Only {PUBLISH_WHITELIST} can publish artifacts."
            )

        # Resolve source path (in sandbox)
        source = self.vfs.get_sandbox_path() / sandbox_path

        if not source.exists():
            raise FileNotFoundError(
                f"Source file not found in sandbox: {sandbox_path} "
                f"(resolved to: {source})"
            )

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
