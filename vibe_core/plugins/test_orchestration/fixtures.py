"""
MINIATURWUNDERLAND - Standardized Test Fixtures for PANOPTICON+
================================================================

"Who watches the watchers?"

This module provides standardized test building blocks - the miniature
versions of real components. Tests MUST use these fixtures instead of
defining their own mock classes.

PHILOSOPHY:
- Tests should get standardized building blocks (classes, logic)
- Each fixture mirrors the real architecture
- Prevents "wild" test writing that leads to inconsistent mocks
- AI cannot create arbitrary test doubles that hide bugs

USAGE:
    from vibe_core.plugins.test_orchestration.fixtures import (
        TestAgents,
        TestKernel,
        TestPlugins,
        TestContext,
    )

    # Create agent without oath (for governance testing)
    bad_agent = TestAgents.without_oath("test-agent")

    # Create minimal kernel for isolated tests
    kernel = TestKernel.minimal()

    # Full test context with cleanup
    with TestContext() as ctx:
        ctx.kernel.register_agent(TestAgents.compliant("my-agent"))
        # ... test code ...
    # Auto-cleanup after context exits

CANONICAL LOCATION: vibe_core/plugins/test_orchestration/fixtures.py
"""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling import Task
from vibe_core.steward.oath_mixin import OathMixin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TEST_FIXTURES")


# =============================================================================
# TEST AGENTS - Standardized Agent Fixtures
# =============================================================================


class _BaseTestAgent(VibeAgent):
    """
    Base class for all test agents.

    Provides minimal implementation of VibeAgent for testing.
    DO NOT use directly - use TestAgents factory methods.
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name or f"Test Agent: {agent_id}",
            version=version,
            capabilities=capabilities or ["test"],
        )
        # Track all process calls for assertion
        self._process_calls: List[Task] = []
        self._process_responses: List[Dict[str, Any]] = []

    def process(self, task: Task) -> Dict[str, Any]:
        """Record the task and return success."""
        self._process_calls.append(task)
        response = {
            "status": "success",
            "agent_id": self.agent_id,
            "task_id": getattr(task, "task_id", "unknown"),
            "payload": getattr(task, "payload", {}),
        }
        self._process_responses.append(response)
        return response

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            capabilities=self.capabilities,
        )

    def report_status(self) -> Dict[str, Any]:
        """Return agent status."""
        return {
            "agent_id": self.agent_id,
            "status": "active",
            "process_calls": len(self._process_calls),
        }


class _CompliantTestAgent(_BaseTestAgent, OathMixin):
    """
    Test agent that is fully compliant with governance.

    Has OathMixin and swears oath on creation.
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            version=version,
            capabilities=capabilities,
        )
        # Initialize and swear oath
        self.oath_mixin_init(agent_id)
        self.swear_oath_sync()


class _NoOathTestAgent(_BaseTestAgent):
    """
    Test agent WITHOUT oath capability.

    Does not have OathMixin - no oath_sworn or oath_event attributes.
    Used to test governance gate rejection.
    """

    pass  # Deliberately no oath attributes


class _FalseOathTestAgent(_BaseTestAgent):
    """
    Test agent with oath_sworn = False.

    Has the attributes but hasn't sworn the oath.
    Used to test governance gate rejection of unsworn agents.
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            version=version,
            capabilities=capabilities,
        )
        # Has attributes but NOT sworn
        self.oath_sworn = False
        self.oath_event = None


class _InvalidOathTestAgent(_BaseTestAgent):
    """
    Test agent with invalid oath signature.

    Has oath_sworn=True but oath_event has invalid signature.
    Used to test cryptographic verification.
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            version=version,
            capabilities=capabilities,
        )
        # Fake oath - will fail signature verification
        self.oath_sworn = True
        self.oath_event = {
            "agent": agent_id,
            "constitution_hash": "FAKE_HASH_12345",
            "signature": "INVALID_SIGNATURE",
            "timestamp": "2024-01-01T00:00:00Z",
        }


class TestAgents:
    """
    Factory class for standardized test agents.

    USAGE:
        # Agent without oath (governance rejection test)
        bad = TestAgents.without_oath("bad-agent")

        # Agent with false oath
        false = TestAgents.with_false_oath("false-agent")

        # Fully compliant agent
        good = TestAgents.compliant("good-agent")

        # Agent with specific capabilities
        cap = TestAgents.with_capabilities("cap-agent", ["read", "write"])
    """

    @staticmethod
    def without_oath(
        agent_id: str = "test-no-oath",
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> VibeAgent:
        """
        Create agent WITHOUT oath capability.

        No oath_sworn or oath_event attributes.
        Governance gate MUST reject this agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable name (default: auto-generated)
            capabilities: List of capabilities (default: ["test"])

        Returns:
            VibeAgent without oath attributes
        """
        return _NoOathTestAgent(
            agent_id=agent_id,
            name=name or f"No-Oath Agent: {agent_id}",
            capabilities=capabilities,
        )

    @staticmethod
    def with_false_oath(
        agent_id: str = "test-false-oath",
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> VibeAgent:
        """
        Create agent with oath_sworn = False.

        Has the attributes but hasn't sworn the oath.
        Governance gate MUST reject this agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable name
            capabilities: List of capabilities

        Returns:
            VibeAgent with oath_sworn=False
        """
        return _FalseOathTestAgent(
            agent_id=agent_id,
            name=name or f"False-Oath Agent: {agent_id}",
            capabilities=capabilities,
        )

    @staticmethod
    def with_invalid_oath(
        agent_id: str = "test-invalid-oath",
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> VibeAgent:
        """
        Create agent with invalid oath signature.

        Has oath_sworn=True but signature is fake.
        Cryptographic verification MUST fail.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable name
            capabilities: List of capabilities

        Returns:
            VibeAgent with invalid oath signature
        """
        return _InvalidOathTestAgent(
            agent_id=agent_id,
            name=name or f"Invalid-Oath Agent: {agent_id}",
            capabilities=capabilities,
        )

    @staticmethod
    def compliant(
        agent_id: str = "test-compliant",
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> VibeAgent:
        """
        Create fully compliant agent with valid oath.

        Uses OathMixin and swears oath on creation.
        Governance gate MUST accept this agent.

        Args:
            agent_id: Unique agent identifier
            name: Human-readable name
            capabilities: List of capabilities

        Returns:
            Fully compliant VibeAgent
        """
        return _CompliantTestAgent(
            agent_id=agent_id,
            name=name or f"Compliant Agent: {agent_id}",
            capabilities=capabilities,
        )

    @staticmethod
    def with_capabilities(
        agent_id: str,
        capabilities: List[str],
        compliant: bool = True,
    ) -> VibeAgent:
        """
        Create agent with specific capabilities.

        Args:
            agent_id: Unique agent identifier
            capabilities: List of capability names
            compliant: If True, agent is oath-compliant (default: True)

        Returns:
            VibeAgent with specified capabilities
        """
        if compliant:
            return _CompliantTestAgent(
                agent_id=agent_id,
                name=f"Capability Agent: {agent_id}",
                capabilities=capabilities,
            )
        else:
            return _NoOathTestAgent(
                agent_id=agent_id,
                name=f"Capability Agent: {agent_id}",
                capabilities=capabilities,
            )

    @staticmethod
    def minimal(agent_id: str = "test-minimal") -> VibeAgent:
        """
        Create bare-minimum agent for basic tests.

        Compliant but with minimal configuration.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Minimal compliant VibeAgent
        """
        return _CompliantTestAgent(agent_id=agent_id)


# =============================================================================
# TEST PLUGINS - Standardized Plugin Fixtures
# =============================================================================


class _NoopTestPlugin(KernelPlugin):
    """Plugin that does nothing - all hooks return default values."""

    def __init__(self, plugin_id: str = "test-noop"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def priority(self) -> int:
        return 999  # Low priority - runs last


class _AllowAllTestPlugin(KernelPlugin):
    """Plugin that explicitly allows all operations."""

    def __init__(self, plugin_id: str = "test-allow-all"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def priority(self) -> int:
        return 1  # High priority - runs first

    def on_agent_pre_register(self, kernel: Any, agent: Any) -> bool:
        return True  # Allow all

    def on_task_submit(self, kernel: Any, task: Any) -> bool:
        return True  # Allow all

    def on_task_pre_assign(self, kernel: Any, agent_id: str, task: Any) -> bool:
        return True  # Allow all

    def on_capability_check(self, kernel: Any, agent_id: str, capability: str) -> Optional[bool]:
        return True  # Allow all

    def on_tool_execute(self, kernel: Any, agent_id: str, tool_name: str, parameters: dict) -> Optional[bool]:
        return True  # Allow all


class _DenyAllTestPlugin(KernelPlugin):
    """Plugin that denies all operations - for testing rejection."""

    def __init__(self, plugin_id: str = "test-deny-all"):
        self._plugin_id = plugin_id

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def priority(self) -> int:
        return 1  # High priority - runs first

    def on_agent_pre_register(self, kernel: Any, agent: Any) -> bool:
        return False  # DENY

    def on_task_submit(self, kernel: Any, task: Any) -> bool:
        return False  # DENY

    def on_task_pre_assign(self, kernel: Any, agent_id: str, task: Any) -> bool:
        return False  # DENY

    def on_capability_check(self, kernel: Any, agent_id: str, capability: str) -> Optional[bool]:
        return False  # DENY

    def on_tool_execute(self, kernel: Any, agent_id: str, tool_name: str, parameters: dict) -> Optional[bool]:
        return False  # DENY


class _RecordingTestPlugin(KernelPlugin):
    """Plugin that records all hook calls for assertion."""

    def __init__(self, plugin_id: str = "test-recording"):
        self._plugin_id = plugin_id
        self.calls: List[Dict[str, Any]] = []

    @property
    def plugin_id(self) -> str:
        return self._plugin_id

    @property
    def priority(self) -> int:
        return 50  # Medium priority

    def _record(self, hook_name: str, **kwargs) -> None:
        self.calls.append({"hook": hook_name, **kwargs})

    def on_boot(self, kernel: Any) -> None:
        self._record("on_boot")

    def on_shutdown(self, kernel: Any) -> None:
        self._record("on_shutdown")

    def on_agent_pre_register(self, kernel: Any, agent: Any) -> bool:
        self._record("on_agent_pre_register", agent_id=getattr(agent, "agent_id", "unknown"))
        return True

    def on_agent_registered(self, kernel: Any, agent_id: str) -> None:
        self._record("on_agent_registered", agent_id=agent_id)

    def on_task_submit(self, kernel: Any, task: Any) -> bool:
        self._record("on_task_submit", task_id=getattr(task, "task_id", "unknown"))
        return True

    def on_task_completed(self, kernel: Any, task_id: str, result: Any) -> None:
        self._record("on_task_completed", task_id=task_id)

    def on_task_failed(self, kernel: Any, task_id: str, error: str) -> None:
        self._record("on_task_failed", task_id=task_id, error=error)

    def get_calls(self, hook_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recorded calls, optionally filtered by hook name."""
        if hook_name:
            return [c for c in self.calls if c["hook"] == hook_name]
        return self.calls

    def clear(self) -> None:
        """Clear recorded calls."""
        self.calls = []


class TestPlugins:
    """
    Factory class for standardized test plugins.

    USAGE:
        # Plugin that does nothing
        noop = TestPlugins.noop()

        # Plugin that allows all operations
        allow = TestPlugins.allow_all()

        # Plugin that denies all operations
        deny = TestPlugins.deny_all()

        # Plugin that records all calls
        recorder = TestPlugins.recording()
        kernel.register_agent(agent)
        assert len(recorder.get_calls("on_agent_registered")) == 1
    """

    @staticmethod
    def noop(plugin_id: str = "test-noop") -> KernelPlugin:
        """Create plugin that does nothing."""
        return _NoopTestPlugin(plugin_id)

    @staticmethod
    def allow_all(plugin_id: str = "test-allow-all") -> KernelPlugin:
        """Create plugin that explicitly allows all operations."""
        return _AllowAllTestPlugin(plugin_id)

    @staticmethod
    def deny_all(plugin_id: str = "test-deny-all") -> KernelPlugin:
        """Create plugin that denies all operations."""
        return _DenyAllTestPlugin(plugin_id)

    @staticmethod
    def recording(plugin_id: str = "test-recording") -> _RecordingTestPlugin:
        """
        Create plugin that records all hook calls.

        Returns:
            Plugin with .calls list and .get_calls(hook_name) method
        """
        return _RecordingTestPlugin(plugin_id)


# =============================================================================
# TEST KERNEL - Standardized Kernel Fixtures
# =============================================================================


class TestKernel:
    """
    Factory class for standardized test kernels.

    USAGE:
        # Minimal kernel without plugins
        kernel = TestKernel.minimal()

        # Kernel with specific plugins
        kernel = TestKernel.with_plugins([my_plugin])

        # Kernel with allow-all governance
        kernel = TestKernel.permissive()
    """

    @staticmethod
    def minimal() -> "RealVibeKernel":
        """
        Create minimal kernel without plugins.

        Uses in-memory ledger, no plugins loaded.
        Good for isolated unit tests.

        Returns:
            RealVibeKernel with minimal configuration
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        return kernel

    @staticmethod
    def with_plugins(plugins: List[KernelPlugin]) -> "RealVibeKernel":
        """
        Create kernel with specific plugins.

        Args:
            plugins: List of plugins to load

        Returns:
            RealVibeKernel with specified plugins
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        kernel._plugins = plugins
        # Boot plugins
        for plugin in plugins:
            plugin.on_boot(kernel)
        return kernel

    @staticmethod
    def permissive() -> "RealVibeKernel":
        """
        Create kernel that allows all operations.

        Uses allow-all plugin - no governance restrictions.
        Good for testing features without governance interference.

        Returns:
            RealVibeKernel with allow-all plugin
        """
        return TestKernel.with_plugins([TestPlugins.allow_all()])

    @staticmethod
    def with_governance() -> "RealVibeKernel":
        """
        Create kernel with ONLY governance plugins.

        Loads ONLY steward_protocol (oath checking, capabilities).
        Does NOT load opus_assistant (MANAS/ML - 4GB+ model).

        This prevents governance tests from waiting 30s+ for ML models.
        Architectural principle: Governance tests should be fast and isolated.

        Returns:
            RealVibeKernel with governance plugins only
        """
        from vibe_core.kernel_impl import RealVibeKernel

        # Boot minimal kernel - NO automatic plugin loading
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # Manually load ONLY governance plugins
        try:
            from vibe_core.plugins.steward_protocol.plugin_main import StewardProtocolPlugin

            steward = StewardProtocolPlugin()
            steward.on_boot(kernel)
            # Kernel needs BOTH _plugins_map AND _plugins list for hooks!
            kernel._plugins_map = {"steward_protocol": steward}
            kernel._plugins = [steward]
        except ImportError:
            pass  # Steward plugin not available

        return kernel

    @staticmethod
    def with_recording() -> tuple["RealVibeKernel", _RecordingTestPlugin]:
        """
        Create kernel with recording plugin for assertions.

        Returns:
            Tuple of (kernel, recording_plugin)
            Use recording_plugin.get_calls() to verify hook calls
        """
        recorder = TestPlugins.recording()
        kernel = TestKernel.with_plugins([recorder])
        return kernel, recorder


# =============================================================================
# TEST TASKS - Standardized Task Fixtures
# =============================================================================


class TestTasks:
    """
    Factory class for standardized test tasks.

    USAGE:
        task = TestTasks.simple("herald")
        task = TestTasks.with_payload("oracle", {"query": "test"})
    """

    @staticmethod
    def simple(
        agent_id: str = "test-agent",
        task_id: Optional[str] = None,
    ) -> Task:
        """Create simple task for agent."""
        return Task(
            agent_id=agent_id,
            payload={"action": "test"},
        )

    @staticmethod
    def with_payload(
        agent_id: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ) -> Task:
        """Create task with specific payload."""
        return Task(
            agent_id=agent_id,
            payload=payload,
        )

    @staticmethod
    def batch(
        agent_id: str,
        count: int = 5,
    ) -> List[Task]:
        """Create batch of simple tasks for load testing."""
        return [
            Task(
                agent_id=agent_id,
                payload={"action": "batch", "index": i},
            )
            for i in range(count)
        ]


# =============================================================================
# TEST CONTEXT - Full Test Isolation
# =============================================================================


@dataclass
class TestContextState:
    """State managed by TestContext."""

    kernel: Any = None
    agents: Dict[str, VibeAgent] = field(default_factory=dict)
    plugins: List[KernelPlugin] = field(default_factory=list)
    recorder: Optional[_RecordingTestPlugin] = None


class IsolatedTestContext:
    """
    Context manager for full test isolation.

    Provides:
    - Isolated kernel with in-memory storage
    - Recording plugin for assertion
    - Auto-cleanup on exit
    - Helper methods for common operations

    USAGE:
        with IsolatedTestContext() as ctx:
            ctx.register_compliant_agent("my-agent")
            ctx.kernel.boot()

            # Make assertions
            assert ctx.recorder.get_calls("on_agent_registered")

        # Kernel and agents cleaned up automatically
    """

    def __init__(
        self,
        with_governance: bool = False,
        with_recording: bool = True,
    ):
        """
        Initialize test context.

        Args:
            with_governance: If True, load full governance stack
            with_recording: If True, include recording plugin
        """
        self._with_governance = with_governance
        self._with_recording = with_recording
        self._state: Optional[TestContextState] = None

    def __enter__(self) -> "IsolatedTestContext":
        """Enter context - create kernel and plugins."""
        self._state = TestContextState()

        # Create recording plugin if requested
        if self._with_recording:
            self._state.recorder = TestPlugins.recording()
            self._state.plugins.append(self._state.recorder)

        # Create kernel
        if self._with_governance:
            self._state.kernel = TestKernel.with_governance()
            if self._state.recorder:
                self._state.kernel._plugins.append(self._state.recorder)
        else:
            self._state.kernel = TestKernel.with_plugins(self._state.plugins)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context - cleanup.

        OPUS-305: Must call kernel.shutdown_async() to properly cleanup
        async logging listener and prevent test timeouts.
        """
        if self._state and self._state.kernel:
            try:
                # Properly shutdown kernel (includes async logging cleanup)
                import asyncio

                # Try to get or create event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                # Run kernel shutdown
                if hasattr(self._state.kernel, "shutdown_async"):
                    loop.run_until_complete(self._state.kernel.shutdown_async("Test context exit"))
                else:
                    # Fallback: manual plugin shutdown
                    for plugin in self._state.kernel._plugins:
                        try:
                            plugin.on_shutdown(self._state.kernel)
                        except Exception:
                            pass
            except Exception:
                pass

        # OPUS-305: Shutdown async logging listener to prevent test timeouts
        # Kernel is immutable (VISNU protection), so we call it from test context instead
        try:
            from vibe_core.utils.async_logging import shutdown_async_logging

            shutdown_async_logging()
        except Exception:
            pass

        self._state = None
        return False  # Don't suppress exceptions

    @property
    def kernel(self) -> Any:
        """Get the test kernel."""
        if not self._state:
            raise RuntimeError("TestContext not entered - use 'with TestContext() as ctx:'")
        return self._state.kernel

    @property
    def recorder(self) -> Optional[_RecordingTestPlugin]:
        """Get the recording plugin (if enabled)."""
        if not self._state:
            raise RuntimeError("TestContext not entered")
        return self._state.recorder

    @property
    def agents(self) -> Dict[str, VibeAgent]:
        """Get registered agents."""
        if not self._state:
            raise RuntimeError("TestContext not entered")
        return self._state.agents

    def register_compliant_agent(self, agent_id: str) -> VibeAgent:
        """Create and register a compliant agent."""
        agent = TestAgents.compliant(agent_id)
        self._state.kernel.register_agent(agent)
        self._state.agents[agent_id] = agent
        return agent

    def register_agent(self, agent: VibeAgent) -> None:
        """Register an existing agent."""
        self._state.kernel.register_agent(agent)
        self._state.agents[agent.agent_id] = agent

    def submit_task(self, agent_id: str, payload: Optional[Dict[str, Any]] = None) -> Task:
        """Create and submit a task."""
        task = TestTasks.with_payload(agent_id, payload or {"action": "test"})
        self._state.kernel.submit_task(task)
        return task


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Agent fixtures
    "TestAgents",
    # Plugin fixtures
    "TestPlugins",
    # Kernel fixtures
    "TestKernel",
    # Task fixtures
    "TestTasks",
    # Context manager
    "IsolatedTestContext",
    "TestContextState",
]
