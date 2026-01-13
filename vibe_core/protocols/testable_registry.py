"""
TESTABLE REGISTRY - Discovers and Registers ALL Testable Components

PHILOSOPHY:
"The kernel knows all that can be tested."

This registry automatically discovers all components that implement
the Testable protocol OR can be wrapped with adapters.

DISCOVERY SOURCES:
1. Kernel agent_registry → AgentTestableAdapter
2. Kernel _plugins → PluginTestableAdapter
3. ToolRegistry → ToolTestableAdapter
4. Kernel ledger → LedgerTestableAdapter
5. Kernel scheduler → SchedulerTestableAdapter
6. EventBus → EventBusTestableAdapter
7. Direct Testable implementations

USAGE:
    registry = TestableRegistry()
    registry.discover_from_kernel(kernel)

    # Get all test cases
    all_cases = registry.get_all_test_cases()

    # Filter by type
    tool_cases = registry.get_test_cases_by_type(TestableType.TOOL)

    # Get testables
    for testable in registry.testables:
        print(f"{testable.testable_id}: {len(testable.get_test_cases())} tests")
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0xbc5d2515"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.protocols.testable import (
    AgentTestableAdapter,
    BaseTestable,
    EventBusTestableAdapter,
    LedgerTestableAdapter,
    PluginTestableAdapter,
    SchedulerTestableAdapter,
    TestableType,
    TestCase,
    ToolTestableAdapter,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TESTABLE_REGISTRY")


class TestableRegistry:
    """
    Central registry for all testable components.

    Discovers and wraps components from:
    - Kernel (agents, plugins, ledger, scheduler)
    - Tool registries
    - Event bus
    - Any component implementing Testable protocol directly
    """

    def __init__(self):
        self._testables: Dict[str, BaseTestable] = {}
        self._discovered: Set[str] = set()

    @property
    def testables(self) -> List[BaseTestable]:
        """Get all registered testables."""
        return list(self._testables.values())

    def register(self, testable: BaseTestable) -> None:
        """
        Register a single testable component.

        Args:
            testable: Component implementing Testable protocol
        """
        testable_id = testable.testable_id
        if testable_id not in self._testables:
            self._testables[testable_id] = testable
            logger.debug(f"Registered: {testable_id}")

    def discover_from_kernel(self, kernel: "RealVibeKernel") -> Dict[str, int]:
        """
        Auto-discover all testable components from a kernel.

        Returns:
            Dictionary of component type → count discovered
        """
        counts = {
            "agents": 0,
            "plugins": 0,
            "tools": 0,
            "ledger": 0,
            "scheduler": 0,
            "event_bus": 0,
        }

        # 1. Discover Agents
        if hasattr(kernel, "agent_registry"):
            for agent_id, agent in kernel.agent_registry.items():
                if agent_id not in self._discovered:
                    adapter = AgentTestableAdapter(agent)
                    self.register(adapter)
                    self._discovered.add(agent_id)
                    counts["agents"] += 1

        # 2. Discover Plugins
        if hasattr(kernel, "_plugins"):
            for plugin in kernel._plugins:
                plugin_id = plugin.plugin_id
                if f"plugin::{plugin_id}" not in self._discovered:
                    adapter = PluginTestableAdapter(plugin)
                    self.register(adapter)
                    self._discovered.add(f"plugin::{plugin_id}")
                    counts["plugins"] += 1

        # 3. Discover Tools from kernel's tool registry
        if hasattr(kernel, "tool_registry") and kernel.tool_registry:
            # ToolRegistry stores tools in .tools attribute
            tool_dict = getattr(kernel.tool_registry, "tools", {})
            for tool_name, tool in tool_dict.items():
                if f"tool::{tool_name}" not in self._discovered:
                    adapter = ToolTestableAdapter(tool)
                    self.register(adapter)
                    self._discovered.add(f"tool::{tool_name}")
                    counts["tools"] += 1

        # Also check agent tool registries
        if hasattr(kernel, "agent_registry"):
            for agent_id, agent in kernel.agent_registry.items():
                if hasattr(agent, "tools"):
                    for tool in agent.tools:
                        tool_id = f"tool::{agent_id}::{tool.name}"
                        if tool_id not in self._discovered:
                            adapter = ToolTestableAdapter(tool)
                            # Override testable_id to include agent
                            adapter._override_id = tool_id
                            self.register(adapter)
                            self._discovered.add(tool_id)
                            counts["tools"] += 1

        # 4. Discover Ledger
        if hasattr(kernel, "ledger") and kernel.ledger:
            if "core::ledger" not in self._discovered:
                adapter = LedgerTestableAdapter(kernel.ledger)
                self.register(adapter)
                self._discovered.add("core::ledger")
                counts["ledger"] = 1

        # 5. Discover Scheduler
        if hasattr(kernel, "scheduler") and kernel.scheduler:
            if "core::scheduler" not in self._discovered:
                adapter = SchedulerTestableAdapter(kernel.scheduler)
                self.register(adapter)
                self._discovered.add("core::scheduler")
                counts["scheduler"] = 1
        # Also check _scheduler (internal)
        elif hasattr(kernel, "_scheduler") and kernel._scheduler:
            if "core::scheduler" not in self._discovered:
                adapter = SchedulerTestableAdapter(kernel._scheduler)
                self.register(adapter)
                self._discovered.add("core::scheduler")
                counts["scheduler"] = 1

        # 6. Discover EventBus
        try:
            from vibe_core.event_bus import EventBus

            # EventBus might be a singleton or module-level
            if "core::event_bus" not in self._discovered:
                adapter = EventBusTestableAdapter(EventBus)
                self.register(adapter)
                self._discovered.add("core::event_bus")
                counts["event_bus"] = 1
        except ImportError:
            pass

        logger.info(f"Discovery complete: {sum(counts.values())} components")
        return counts

    def discover_tools_from_registry(self, tool_registry: Any) -> int:
        """
        Discover tools from a standalone tool registry.

        Args:
            tool_registry: Dictionary or object with tools

        Returns:
            Number of tools discovered
        """
        count = 0
        tools = {}

        if isinstance(tool_registry, dict):
            tools = tool_registry
        elif hasattr(tool_registry, "tools"):
            tools = tool_registry.tools
        elif hasattr(tool_registry, "_tools"):
            tools = tool_registry._tools

        for tool_name, tool in tools.items():
            if f"tool::{tool_name}" not in self._discovered:
                adapter = ToolTestableAdapter(tool)
                self.register(adapter)
                self._discovered.add(f"tool::{tool_name}")
                count += 1

        return count

    def get_all_test_cases(self) -> List[TestCase]:
        """
        Get ALL test cases from ALL registered testables.

        Returns:
            List of all TestCase objects
        """
        all_cases = []
        for testable in self._testables.values():
            try:
                cases = testable.get_test_cases()
                # Prefix test names with testable_id to ensure uniqueness
                for case in cases:
                    if not case.name.startswith(testable.testable_id):
                        case.name = f"{testable.testable_id}::{case.name}"
                all_cases.extend(cases)
            except Exception as e:
                logger.warning(f"Failed to get tests from {testable.testable_id}: {e}")
        return all_cases

    def get_test_cases_by_type(self, testable_type: TestableType) -> List[TestCase]:
        """
        Get test cases filtered by component type.

        Args:
            testable_type: Type of component (AGENT, PLUGIN, TOOL, etc.)

        Returns:
            List of matching TestCase objects
        """
        cases = []
        for testable in self._testables.values():
            if testable.testable_type == testable_type:
                try:
                    cases.extend(testable.get_test_cases())
                except Exception as e:
                    logger.warning(f"Failed to get tests from {testable.testable_id}: {e}")
        return cases

    def get_testable(self, testable_id: str) -> Optional[BaseTestable]:
        """
        Get a specific testable by ID.

        Args:
            testable_id: The testable's unique ID

        Returns:
            The Testable component or None
        """
        return self._testables.get(testable_id)

    def get_testables_by_type(self, testable_type: TestableType) -> List[BaseTestable]:
        """
        Get all testables of a specific type.

        Args:
            testable_type: Type to filter by

        Returns:
            List of matching Testable components
        """
        return [t for t in self._testables.values() if t.testable_type == testable_type]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of registered testables.

        Returns:
            Dictionary with counts by type, total tests, etc.
        """
        type_counts = {}
        test_counts = {}
        total_tests = 0

        for testable in self._testables.values():
            t_type = testable.testable_type.value
            type_counts[t_type] = type_counts.get(t_type, 0) + 1

            try:
                num_tests = len(testable.get_test_cases())
                test_counts[t_type] = test_counts.get(t_type, 0) + num_tests
                total_tests += num_tests
            except Exception:
                pass

        return {
            "total_testables": len(self._testables),
            "total_tests": total_tests,
            "by_type": type_counts,
            "tests_by_type": test_counts,
        }

    def clear(self) -> None:
        """Clear all registered testables."""
        self._testables.clear()
        self._discovered.clear()


# ============================================================================
# SINGLETON INSTANCE (optional, for convenience)
# ============================================================================

_global_registry: Optional[TestableRegistry] = None


def get_global_registry() -> TestableRegistry:
    """Get or create the global testable registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = TestableRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry (for testing)."""
    global _global_registry
    if _global_registry:
        _global_registry.clear()
    _global_registry = None


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "TestableRegistry",
    "get_global_registry",
    "reset_global_registry",
]
