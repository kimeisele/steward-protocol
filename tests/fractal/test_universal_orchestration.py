"""
TEST: Universal Test Orchestration System

This test verifies that the Universal Testable Protocol correctly:
1. Discovers ALL component types (not just agents)
2. Generates appropriate tests for each type
3. Executes tests and reports results
4. Records results to the ledger

This is a meta-test: testing the test system itself.
"""

import pytest

from tests.fractal.fractal_test_framework import FractalTestCase

# ============================================================================
# TEST: Testable Protocol
# ============================================================================


class TestTestableProtocol:
    """Test the Testable protocol and adapters."""

    def test_testable_type_enum(self):
        """TestableType enum has all required types."""
        from vibe_core.protocols.testable import TestableType

        required_types = [
            "agent",
            "plugin",
            "tool",
            "ledger",
            "scheduler",
            "event_bus",
        ]

        for t in required_types:
            assert hasattr(TestableType, t.upper()), f"Missing type: {t}"

    def test_test_case_dataclass(self):
        """TestCase dataclass has correct fields."""
        from vibe_core.protocols.testable import TestCase

        case = TestCase(
            name="test_example",
            test_func=lambda kernel, comp: True,
            description="Example test",
            tags=["fast", "basic"],
        )

        assert case.name == "test_example"
        assert case.description == "Example test"
        assert "fast" in case.tags
        assert case.timeout_ms == 5000  # Default

    def test_agent_adapter_creates_tests(self):
        """AgentTestableAdapter generates correct tests for agents."""
        from vibe_core.protocols.testable import AgentTestableAdapter, TestableType

        # Create a mock agent
        class MockAgent:
            agent_id = "test_agent"
            name = "Test Agent"
            version = "1.0.0"
            capabilities = ["testing"]

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(
                    agent_id=self.agent_id,
                    name=self.name,
                    version=self.version,
                    capabilities=self.capabilities,
                )

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "RUNNING"}

        agent = MockAgent()
        adapter = AgentTestableAdapter(agent)

        assert adapter.testable_id == "agent::test_agent"
        assert adapter.testable_type == TestableType.AGENT

        cases = adapter.get_test_cases()
        assert len(cases) >= 4  # At least 4 standard tests

        test_names = [c.name for c in cases]
        assert any("has_manifest" in name for name in test_names)
        assert any("has_capabilities" in name for name in test_names)

    def test_plugin_adapter_creates_tests(self):
        """PluginTestableAdapter generates correct tests for plugins."""
        from vibe_core.protocols.testable import PluginTestableAdapter, TestableType

        # Create a mock plugin
        class MockPlugin:
            @property
            def plugin_id(self):
                return "mock_plugin"

            @property
            def priority(self):
                return 100

            def on_boot(self, kernel):
                pass

            def on_shutdown(self, kernel):
                pass

        plugin = MockPlugin()
        adapter = PluginTestableAdapter(plugin)

        assert adapter.testable_id == "plugin::mock_plugin"
        assert adapter.testable_type == TestableType.PLUGIN

        cases = adapter.get_test_cases()
        assert len(cases) >= 3  # At least 3 standard tests

    def test_tool_adapter_creates_tests(self):
        """ToolTestableAdapter generates correct tests for tools."""
        from vibe_core.protocols.testable import TestableType, ToolTestableAdapter

        # Create a mock tool
        class MockTool:
            @property
            def name(self):
                return "mock_tool"

            @property
            def description(self):
                return "A mock tool for testing"

            @property
            def parameters_schema(self):
                return {"param1": {"type": "string"}}

            def validate(self, params):
                pass

            def execute(self, params):
                return {"success": True}

            def to_llm_description(self):
                return {"name": self.name, "description": self.description}

        tool = MockTool()
        adapter = ToolTestableAdapter(tool)

        assert adapter.testable_id == "tool::mock_tool"
        assert adapter.testable_type == TestableType.TOOL

        cases = adapter.get_test_cases()
        assert len(cases) >= 6  # Tools have 6 standard tests


# ============================================================================
# TEST: Testable Registry
# ============================================================================


class TestTestableRegistry:
    """Test the TestableRegistry discovery system."""

    def test_registry_creation(self):
        """Registry can be created and is empty initially."""
        from vibe_core.protocols.testable_registry import TestableRegistry

        registry = TestableRegistry()
        assert len(registry.testables) == 0

    def test_registry_manual_registration(self):
        """Registry accepts manual testable registration."""
        from vibe_core.protocols.testable import AgentTestableAdapter
        from vibe_core.protocols.testable_registry import TestableRegistry

        registry = TestableRegistry()

        class MockAgent:
            agent_id = "manual_agent"
            name = "Manual"
            capabilities = []

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        adapter = AgentTestableAdapter(MockAgent())
        registry.register(adapter)

        assert len(registry.testables) == 1
        assert registry.get_testable("agent::manual_agent") is not None

    def test_registry_get_all_test_cases(self):
        """Registry can collect all test cases from all testables."""
        from vibe_core.protocols.testable import AgentTestableAdapter, PluginTestableAdapter
        from vibe_core.protocols.testable_registry import TestableRegistry

        registry = TestableRegistry()

        # Add a mock agent
        class MockAgent:
            agent_id = "test_agent"
            name = "Test"
            capabilities = ["x"]

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        # Add a mock plugin
        class MockPlugin:
            @property
            def plugin_id(self):
                return "test_plugin"

            @property
            def priority(self):
                return 50

            def on_boot(self, k):
                pass

            def on_shutdown(self, k):
                pass

        registry.register(AgentTestableAdapter(MockAgent()))
        registry.register(PluginTestableAdapter(MockPlugin()))

        all_cases = registry.get_all_test_cases()
        assert len(all_cases) >= 7  # 4 agent + 4 plugin tests

    def test_registry_filter_by_type(self):
        """Registry can filter testables by type."""
        from vibe_core.protocols.testable import (
            AgentTestableAdapter,
            PluginTestableAdapter,
            TestableType,
        )
        from vibe_core.protocols.testable_registry import TestableRegistry

        registry = TestableRegistry()

        class MockAgent:
            agent_id = "a1"
            name = "A1"
            capabilities = []

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        class MockPlugin:
            @property
            def plugin_id(self):
                return "p1"

            @property
            def priority(self):
                return 50

            def on_boot(self, k):
                pass

            def on_shutdown(self, k):
                pass

        registry.register(AgentTestableAdapter(MockAgent()))
        registry.register(PluginTestableAdapter(MockPlugin()))

        agents = registry.get_testables_by_type(TestableType.AGENT)
        plugins = registry.get_testables_by_type(TestableType.PLUGIN)

        assert len(agents) == 1
        assert len(plugins) == 1

    def test_registry_summary(self):
        """Registry provides accurate summary statistics."""
        from vibe_core.protocols.testable import AgentTestableAdapter
        from vibe_core.protocols.testable_registry import TestableRegistry

        registry = TestableRegistry()

        class MockAgent:
            agent_id = "summary_test"
            name = "ST"
            capabilities = []

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        registry.register(AgentTestableAdapter(MockAgent()))

        summary = registry.get_summary()
        assert summary["total_testables"] == 1
        assert summary["total_tests"] >= 4
        assert "agent" in summary["by_type"]


# ============================================================================
# TEST: Universal Test Orchestration Plugin
# ============================================================================


@pytest.mark.xfail(reason="TestOrchestrationPlugin removed from plugins", strict=False)
class TestUniversalOrchestrationPlugin:
    """Test the Universal Test Orchestration Plugin."""

    def test_plugin_initialization(self):
        """Plugin initializes correctly."""
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin

        plugin = TestOrchestrationPlugin()
        assert plugin.plugin_id == "test_orchestration"
        assert plugin.priority == 200

    def test_plugin_runs_tests(self):
        """Plugin can run tests and return results."""
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin
        from vibe_core.protocols.testable import AgentTestableAdapter

        plugin = TestOrchestrationPlugin()

        # Manually register a testable
        class MockAgent:
            agent_id = "run_test"
            name = "RT"
            capabilities = ["test"]

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(
                    agent_id=self.agent_id,
                    name=self.name,
                    capabilities=self.capabilities,
                )

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        adapter = AgentTestableAdapter(MockAgent())
        plugin.register_testable(adapter)

        # Run tests
        results = plugin.run_all_tests()
        assert len(results) >= 4  # At least 4 agent tests

        # Check summary
        summary = plugin.get_summary()
        assert summary["total"] >= 4
        assert "passed" in summary

    def test_plugin_filters_by_type(self):
        """Plugin can filter tests by component type."""
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin
        from vibe_core.protocols.testable import (
            AgentTestableAdapter,
            PluginTestableAdapter,
            TestableType,
        )

        plugin = TestOrchestrationPlugin()

        class MockAgent:
            agent_id = "type_test"
            name = "TT"
            capabilities = []

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        class MockPlugin:
            @property
            def plugin_id(self):
                return "type_test_plugin"

            @property
            def priority(self):
                return 50

            def on_boot(self, k):
                pass

            def on_shutdown(self, k):
                pass

        plugin.register_testable(AgentTestableAdapter(MockAgent()))
        plugin.register_testable(PluginTestableAdapter(MockPlugin()))

        # Run only agent tests
        agent_results = plugin.run_tests_by_type(TestableType.AGENT)
        assert len(agent_results) >= 4
        assert all(r.testable_type == "agent" for r in agent_results)

    def test_plugin_print_summary(self):
        """Plugin generates human-readable summary."""
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin
        from vibe_core.protocols.testable import AgentTestableAdapter

        plugin = TestOrchestrationPlugin()

        class MockAgent:
            agent_id = "print_test"
            name = "PT"
            capabilities = []

            def get_manifest(self):
                from vibe_core.protocols.agent import AgentManifest

                return AgentManifest(agent_id=self.agent_id, name=self.name)

            def report_status(self):
                return {"agent_id": self.agent_id, "status": "OK"}

        plugin.register_testable(AgentTestableAdapter(MockAgent()))
        plugin.run_all_tests()

        summary_text = plugin.print_summary()
        assert "UNIVERSAL TEST ORCHESTRATION" in summary_text
        assert "Total Tests:" in summary_text
        assert "Pass Rate:" in summary_text


# ============================================================================
# TEST: Infrastructure Adapters
# ============================================================================


class TestInfrastructureAdapters:
    """Test adapters for core infrastructure components."""

    def test_ledger_adapter(self):
        """LedgerTestableAdapter generates correct tests."""
        from vibe_core.protocols.testable import LedgerTestableAdapter, TestableType

        class MockLedger:
            def record_event(self, event_type, agent_id, details):
                pass

            def query_events(self, limit=100):
                return []

        adapter = LedgerTestableAdapter(MockLedger())
        assert adapter.testable_type == TestableType.LEDGER
        assert adapter.testable_id == "core::ledger"

        cases = adapter.get_test_cases()
        assert len(cases) >= 3

    def test_scheduler_adapter(self):
        """SchedulerTestableAdapter generates correct tests."""
        from vibe_core.protocols.testable import SchedulerTestableAdapter, TestableType

        class MockScheduler:
            def submit_task(self, task):
                return "task_123"

            def get_next_task(self, agent_id):
                return None

        adapter = SchedulerTestableAdapter(MockScheduler())
        assert adapter.testable_type == TestableType.SCHEDULER
        assert adapter.testable_id == "core::scheduler"

        cases = adapter.get_test_cases()
        assert len(cases) >= 3


# ============================================================================
# INTEGRATION TEST: Full Kernel Discovery
# ============================================================================


@pytest.mark.xfail(reason="TestOrchestrationPlugin removed from plugins", strict=False)
class TestKernelIntegration(FractalTestCase):
    """Integration test with real kernel."""

    TIMEOUT = 10
    USE_REAL_KERNEL = True

    def test_real_kernel_discovery(self):
        """Real kernel discovers all component types."""
        from vibe_core.plugins.test_orchestration import TestOrchestrationPlugin

        # Check if test orchestration plugin is available
        plugin = None
        if hasattr(self.kernel, "_plugins"):
            for p in self.kernel._plugins:
                if p.plugin_id == "test_orchestration":
                    plugin = p
                    break

        if not plugin:
            # Register it manually
            plugin = TestOrchestrationPlugin()
            self.kernel.register_plugin(plugin)
            plugin.on_boot(self.kernel)

        summary = plugin.get_summary()

        # Should have discovered multiple component types
        discovery = summary.get("discovery", {})
        total = discovery.get("total_testables", 0)

        # Real kernel should have agents, plugins, ledger, scheduler
        assert total >= 1, f"Expected at least 1 testable, got {total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--timeout=30"])
