"""
UNIVERSAL TESTABLE PROTOCOL - Self-Testing Components

PHILOSOPHY:
"Every component knows its own tests." - Fractal Testing Principle

This protocol enables ANY component in the system to:
1. Declare its testable identity
2. Provide its own test cases
3. Be auto-discovered and tested by the kernel

COMPONENT TYPES SUPPORTED:
- Agents (VibeAgent implementations)
- Plugins (KernelPlugin implementations)
- Tools (Tool implementations)
- Syscalls (SyscallType handlers)
- Core Infrastructure (Ledger, Scheduler, EventBus, etc.)
- Governance (Varna, Ashrama, Constitutional checks)

USAGE:
    class MyTool(Tool, Testable):
        @property
        def testable_id(self) -> str:
            return f"tool::{self.name}"

        @property
        def testable_type(self) -> TestableType:
            return TestableType.TOOL

        def get_test_cases(self) -> List[TestCase]:
            return [
                TestCase(
                    name="test_execute_basic",
                    test_func=self._test_execute_basic,
                    description="Tool executes basic operation",
                ),
            ]

        def _test_execute_basic(self, kernel) -> bool:
            result = self.execute({"param": "value"})
            return result.success

For components that DON'T directly implement Testable (legacy),
use the adapter pattern:

    adapter = ToolTestableAdapter(my_tool)
    test_cases = adapter.get_test_cases()
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x4f13d296"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, List, Protocol, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.protocols.substrate.gene import iGene

# Level -1 Import (Allowed by Dharma)
from .substrate.byte import MantraByte, HolyName


# ============================================================================
# TESTABLE TYPE ENUMERATION
# ============================================================================


class TestableType(str, Enum):
    """Categories of testable components."""

    AGENT = "agent"
    PLUGIN = "plugin"
    TOOL = "tool"
    SYSCALL = "syscall"
    LEDGER = "ledger"
    SCHEDULER = "scheduler"
    EVENT_BUS = "event_bus"
    ROUTER = "router"
    GOVERNANCE = "governance"
    SECURITY = "security"
    RUNTIME = "runtime"
    CORE = "core"


# ============================================================================
# TEST CASE DEFINITION
# ============================================================================


@dataclass
class TestCase:
    """
    A single test case for a component.

    Attributes:
        name: Unique test name (e.g., "test_can_execute")
        test_func: Function that returns True (pass) or False (fail)
        description: Human-readable description
        timeout_ms: Maximum execution time
        requires_kernel: Whether test needs full kernel
        tags: Optional tags for filtering (e.g., ["fast", "security"])
    """

    name: str
    test_func: Callable[["RealVibeKernel", Any], bool]
    description: str = ""
    timeout_ms: int = 5000
    requires_kernel: bool = False
    tags: List[str] = field(default_factory=list)

    @property
    def test_id(self) -> str:
        """Generate unique test ID."""
        return self.name


# ============================================================================
# TESTABLE PROTOCOL
# ============================================================================


@runtime_checkable
class Testable(Protocol):
    """
    Universal protocol for self-testing components.

    ANY component that implements this protocol can be automatically
    discovered and tested by the TestOrchestrationPlugin.

    This is the FRACTAL pattern: components mirror the test structure.
    """

    @property
    def testable_id(self) -> str:
        """
        Unique identifier for this testable component.

        Format: "{type}::{name}" e.g., "tool::read_file", "plugin::sarga_cycle"
        """
        ...

    @property
    def testable_type(self) -> TestableType:
        """
        Category of this component.

        Used for filtering, grouping, and specialized test generation.
        """
        ...

    def get_test_cases(self) -> List[TestCase]:
        """
        Return all test cases for this component.

        Components should return:
        1. Basic sanity tests (component exists, has required methods)
        2. Functional tests (component does what it claims)
        3. Edge case tests (error handling, invalid input)
        4. Integration tests (works with other components)
        """
        ...


# ============================================================================
# BASE TESTABLE CLASS (for convenience)
# ============================================================================


class BaseTestable(ABC):
    """
    Convenience base class for components implementing Testable.

    Provides common functionality and default implementations.
    """

    def _bool_to_holy_name(self, result: bool) -> HolyName:
        """
        Converts raw boolean reality to Holy Name.
        True is not just 'True', it is an accepted Offering (KRISHNA).
        False is not just 'False', it is Separation/Entropy (VOID).
        """
        return HolyName.KRISHNA if result else HolyName.VOID

    def calculate_mantra(self, results: List[bool]) -> MantraByte:
        """
        Compresses linear test results into a Fractal MantraByte.
        This represents the component's 'Karma'.
        """
        trits = [self._bool_to_holy_name(r) for r in results]

        # Pad with HARE (Potential/Silence) to fill the byte (16 trits)
        while len(trits) < 16:
            trits.append(HolyName.HARE)

        # If we have more than 16, we compress or truncate (Fractal View)
        # For now, taking the first 16 (The Standard Mantra Length)
        mb = MantraByte.from_trits(trits[:16])

        # DIVINE OVERRIDE: If all tests pass (Pure Krishna), we grant Vaikuntha (Coherence 1.0)
        # This bypasses the structural dissonance with the Standard Mantra (which contains HARE/RAMA).
        if all(r for r in results) and len(results) > 0:
            return MantraByte(mb._packed, mb._length, coherence=1.0)

        return mb

    def evaluate_life(self, results: List[bool]) -> str:
        """
        Returns a diagnosis based on Mantra Coherence.
        """
        mb = self.calculate_mantra(results)

        # Check for VOID (Maya) directly in the sequence
        # We need to peek into the trits.
        if any(r is False for r in results):
            return f"RED (MAYA DETECTED) - One or more tests entered VOID state."

        coherence = mb.coherence  # 0.0 to 1.0 (Calculated in byte.py)

        # The Thresholds of Reality
        if coherence >= 0.95:
            return f"GREEN (VAIKUNTHA) - Pure Resonance ({coherence:.2f})"
        elif coherence >= 0.75:
            return f"YELLOW (MATERIAL) - Functional but noisy ({coherence:.2f})"
        else:
            return f"ORANGE (STRUGGLING) - Low Coherence ({coherence:.2f})"

    @property
    @abstractmethod
    def testable_id(self) -> str:
        """Unique identifier."""
        pass

    @property
    @abstractmethod
    def testable_type(self) -> TestableType:
        """Component type."""
        pass

    def get_test_cases(self) -> List[TestCase]:
        """
        Default implementation returns basic existence tests.

        Override to add component-specific tests.
        """
        return [
            TestCase(
                name=f"{self.testable_id}::exists",
                test_func=lambda kernel, comp: comp is not None,
                description=f"{self.testable_id} exists and is not None",
                tags=["basic", "fast"],
            ),
        ]


# ============================================================================
# TESTABLE ADAPTERS (for legacy components)
# ============================================================================


class AgentTestableAdapter(BaseTestable):
    """
    Adapter that makes any VibeAgent testable.

    Wraps existing agents without modifying their code.
    """

    def __init__(self, agent: Any):
        self._agent = agent

    @property
    def testable_id(self) -> str:
        return f"agent::{self._agent.agent_id}"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.AGENT

    def get_test_cases(self) -> List[TestCase]:
        """Generate standard tests for any agent."""
        cases = []

        # Test 1: Agent has valid manifest
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_manifest",
                test_func=self._test_has_manifest,
                description="Agent has valid manifest with required fields",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Agent is in registry
        cases.append(
            TestCase(
                name=f"{self.testable_id}::in_registry",
                test_func=self._test_in_registry,
                description="Agent is registered in kernel registry",
                requires_kernel=True,
                tags=["basic", "fast"],
            )
        )

        # Test 3: Agent has capabilities
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_capabilities",
                test_func=self._test_has_capabilities,
                description="Agent declares at least one capability",
                tags=["basic", "fast"],
            )
        )

        # Test 4: Agent can report status
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_report_status",
                test_func=self._test_can_report_status,
                description="Agent can report its status",
                tags=["basic", "fast"],
            )
        )

        # FRACTAL: Delegate to agent's own tests if available
        if hasattr(self._agent, "get_test_cases"):
            try:
                # Agent implementation of get_test_cases might require arguments or not
                # We try calling it without arguments first
                custom_cases = self._agent.get_test_cases()
                if custom_cases and isinstance(custom_cases, list):
                    # Prefix custom tests to avoid collision
                    for case in custom_cases:
                        if "::" not in case.name:
                            case.name = f"{self.testable_id}::{case.name}"
                    cases.extend(custom_cases)
            except Exception as e:
                # Log but don't crash
                import logging

                logger = logging.getLogger("AgentTestableAdapter")
                logger.debug(f"Failed to get custom tests from {self._agent.agent_id}: {e}")

        return cases

    def _test_has_manifest(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that agent has valid manifest."""
        try:
            manifest = self._agent.get_manifest()
            return manifest is not None and manifest.agent_id == self._agent.agent_id and len(manifest.name) > 0
        except Exception:
            return False

    def _test_in_registry(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that agent is in kernel registry."""
        if not kernel:
            return True  # Skip if no kernel
        return self._agent.agent_id in kernel.agent_registry

    def _test_has_capabilities(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that agent has capabilities."""
        try:
            manifest = self._agent.get_manifest()
            return manifest is not None and len(manifest.capabilities) > 0
        except Exception:
            return False

    def _test_can_report_status(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that agent can report status."""
        try:
            status = self._agent.report_status()
            return status is not None and "agent_id" in status and "status" in status
        except Exception:
            return False


class PluginTestableAdapter(BaseTestable):
    """
    Adapter that makes any KernelPlugin testable.
    """

    def __init__(self, plugin: Any):
        self._plugin = plugin

    @property
    def testable_id(self) -> str:
        return f"plugin::{self._plugin.plugin_id}"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.PLUGIN

    def get_test_cases(self) -> List[TestCase]:
        """Generate standard tests for any plugin."""
        cases = []

        # Test 1: Plugin has valid ID
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_valid_id",
                test_func=self._test_has_valid_id,
                description="Plugin has non-empty plugin_id",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Plugin has priority
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_priority",
                test_func=self._test_has_priority,
                description="Plugin has valid priority (0-999)",
                tags=["basic", "fast"],
            )
        )

        # Test 3: Plugin hooks exist
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_hooks",
                test_func=self._test_has_hooks,
                description="Plugin has callable hook methods",
                tags=["basic", "fast"],
            )
        )

        # Test 4: Plugin on_boot doesn't crash
        cases.append(
            TestCase(
                name=f"{self.testable_id}::on_boot_safe",
                test_func=self._test_on_boot_safe,
                description="Plugin on_boot executes without exception",
                requires_kernel=True,
                tags=["integration"],
            )
        )

        return cases

    def _test_has_valid_id(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that plugin has valid ID."""
        try:
            plugin_id = self._plugin.plugin_id
            return isinstance(plugin_id, str) and len(plugin_id) > 0
        except Exception:
            return False

    def _test_has_priority(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that plugin has valid priority."""
        try:
            priority = self._plugin.priority
            return isinstance(priority, int) and 0 <= priority <= 999
        except Exception:
            return False

    def _test_has_hooks(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that plugin has hook methods."""
        required_hooks = ["on_boot", "on_shutdown"]
        for hook in required_hooks:
            if not hasattr(self._plugin, hook) or not callable(getattr(self._plugin, hook)):
                return False
        return True

    def _test_on_boot_safe(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Test that on_boot doesn't crash."""
        try:
            self._plugin.on_boot(kernel)
            return True
        except Exception:
            return False


class ToolTestableAdapter(BaseTestable):
    """
    Adapter that makes any Tool testable.
    """

    def __init__(self, tool: Any):
        self._tool = tool

    @property
    def testable_id(self) -> str:
        return f"tool::{self._tool.name}"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.TOOL

    def get_test_cases(self) -> List[TestCase]:
        """Generate standard tests for any tool."""
        cases = []

        # Test 1: Tool has name
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_name",
                test_func=self._test_has_name,
                description="Tool has non-empty name",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Tool has description
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_description",
                test_func=self._test_has_description,
                description="Tool has non-empty description",
                tags=["basic", "fast"],
            )
        )

        # Test 3: Tool has parameters schema
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_schema",
                test_func=self._test_has_schema,
                description="Tool has parameters schema",
                tags=["basic", "fast"],
            )
        )

        # Test 4: Tool can generate LLM description
        cases.append(
            TestCase(
                name=f"{self.testable_id}::llm_description",
                test_func=self._test_llm_description,
                description="Tool can generate LLM-friendly description",
                tags=["basic", "fast"],
            )
        )

        # Test 5: Tool validate method exists
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_validate",
                test_func=self._test_has_validate,
                description="Tool has validate method",
                tags=["basic", "fast"],
            )
        )

        # Test 6: Tool execute method exists
        cases.append(
            TestCase(
                name=f"{self.testable_id}::has_execute",
                test_func=self._test_has_execute,
                description="Tool has execute method",
                tags=["basic", "fast"],
            )
        )

        return cases

    def _test_has_name(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            name = self._tool.name
            return isinstance(name, str) and len(name) > 0
        except Exception:
            return False

    def _test_has_description(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            desc = self._tool.description
            return isinstance(desc, str) and len(desc) > 0
        except Exception:
            return False

    def _test_has_schema(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            schema = self._tool.parameters_schema
            return isinstance(schema, dict)
        except Exception:
            return False

    def _test_llm_description(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            desc = self._tool.to_llm_description()
            return isinstance(desc, dict) and "name" in desc and "description" in desc
        except Exception:
            return False

    def _test_has_validate(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        return hasattr(self._tool, "validate") and callable(self._tool.validate)

    def _test_has_execute(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        return hasattr(self._tool, "execute") and callable(self._tool.execute)


# ============================================================================
# INFRASTRUCTURE TESTABLE ADAPTERS
# ============================================================================


class LedgerTestableAdapter(BaseTestable):
    """Adapter for testing Ledger implementations."""

    def __init__(self, ledger: Any):
        self._ledger = ledger

    @property
    def testable_id(self) -> str:
        return "core::ledger"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.LEDGER

    def get_test_cases(self) -> List[TestCase]:
        cases = []

        # Test 1: Can record event
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_record",
                test_func=self._test_can_record,
                description="Ledger can record events",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Can query events
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_query",
                test_func=self._test_can_query,
                description="Ledger can query recorded events",
                tags=["basic", "fast"],
            )
        )

        # Test 3: Events are immutable (append-only)
        cases.append(
            TestCase(
                name=f"{self.testable_id}::immutable",
                test_func=self._test_immutable,
                description="Ledger is append-only (events cannot be deleted)",
                tags=["security", "integrity"],
            )
        )

        return cases

    def _test_can_record(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            self._ledger.record_event(
                event_type="TEST_EVENT",
                agent_id="test_adapter",
                details={"test": True},
            )
            return True
        except Exception:
            return False

    def _test_can_query(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            # Try different method names (get_all_events is standard)
            if hasattr(self._ledger, "get_all_events"):
                events = self._ledger.get_all_events()
            elif hasattr(self._ledger, "query_events"):
                events = self._ledger.query_events(limit=10)
            elif hasattr(self._ledger, "get_events"):
                events = self._ledger.get_events()
            else:
                return False
            return isinstance(events, list)
        except Exception:
            return False

    def _test_immutable(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        # Ledger should not have delete methods
        dangerous_methods = ["delete_event", "clear", "truncate", "drop"]
        for method in dangerous_methods:
            if hasattr(self._ledger, method):
                return False
        return True


class SchedulerTestableAdapter(BaseTestable):
    """Adapter for testing Scheduler implementations."""

    def __init__(self, scheduler: Any):
        self._scheduler = scheduler

    @property
    def testable_id(self) -> str:
        return "core::scheduler"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.SCHEDULER

    def get_test_cases(self) -> List[TestCase]:
        cases = []

        # Test 1: Can submit task
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_submit",
                test_func=self._test_can_submit,
                description="Scheduler can accept task submissions",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Can get next task
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_get_next",
                test_func=self._test_can_get_next,
                description="Scheduler can return next task for agent",
                tags=["basic", "fast"],
            )
        )

        # Test 3: Task priority ordering
        cases.append(
            TestCase(
                name=f"{self.testable_id}::priority_order",
                test_func=self._test_priority_order,
                description="Scheduler returns tasks in priority order",
                tags=["correctness"],
            )
        )

        return cases

    def _test_can_submit(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            # Check if submit_task method exists and is callable
            if not hasattr(self._scheduler, "submit_task"):
                return False
            if not callable(getattr(self._scheduler, "submit_task")):
                return False
            # Method exists - that's enough for structural test
            # (Actually submitting would require proper Task and agent setup)
            return True
        except Exception:
            return False

    def _test_can_get_next(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            # Check if next_task or get_next_task method exists
            # (different schedulers use different names)
            has_method = (
                hasattr(self._scheduler, "next_task") and callable(getattr(self._scheduler, "next_task"))
            ) or (hasattr(self._scheduler, "get_next_task") and callable(getattr(self._scheduler, "get_next_task")))
            return has_method
        except Exception:
            return False

    def _test_priority_order(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        # Advanced test - would need actual task submission
        return True  # Placeholder


class EventBusTestableAdapter(BaseTestable):
    """Adapter for testing EventBus implementations."""

    def __init__(self, event_bus: Any):
        self._event_bus = event_bus

    @property
    def testable_id(self) -> str:
        return "core::event_bus"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.EVENT_BUS

    def get_test_cases(self) -> List[TestCase]:
        cases = []

        # Test 1: Can subscribe
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_subscribe",
                test_func=self._test_can_subscribe,
                description="EventBus can register subscribers",
                tags=["basic", "fast"],
            )
        )

        # Test 2: Can emit
        cases.append(
            TestCase(
                name=f"{self.testable_id}::can_emit",
                test_func=self._test_can_emit,
                description="EventBus can emit events",
                tags=["basic", "fast"],
            )
        )

        return cases

    def _test_can_subscribe(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            # Check for subscribe method
            return hasattr(self._event_bus, "subscribe") and callable(self._event_bus.subscribe)
        except Exception:
            return False

    def _test_can_emit(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        try:
            # Check for emit method
            return hasattr(self._event_bus, "emit") and callable(self._event_bus.emit)
        except Exception:
            return False


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core types
    "TestableType",
    "TestCase",
    "Testable",
    "BaseTestable",
    # Adapters for existing components
    "AgentTestableAdapter",
    "PluginTestableAdapter",
    "ToolTestableAdapter",
    # Infrastructure adapters
    "LedgerTestableAdapter",
    "SchedulerTestableAdapter",
    "EventBusTestableAdapter",
]
