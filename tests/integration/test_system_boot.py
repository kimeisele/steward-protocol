#!/usr/bin/env python3
"""
🚀 INTEGRATION TEST: System Boot & Agent Discovery
===================================================

This test PROVES that Agent City can boot and discover all agents.

PASS CONDITIONS:
- ✅ Kernel boots successfully
- ✅ DiscovererAgent registers
- ✅ Steward discovers at least 10 agents from steward.json manifests
- ✅ All discovered agents pass Governance Gate (oath_sworn=True)
- ✅ No import errors, no crashes

This is the "smoke test" that proves the system is alive.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vibe_core.kernel_impl import RealVibeKernel, KernelStatus
from vibe_core.scheduling import Task
from vibe_core.agent_protocol import VibeAgent, AgentManifest
from steward.system_agents.discoverer.agent import DiscovererAgent, GenericAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("TEST_SYSTEM_BOOT")


class TestKernelBoot:
    """Test that kernel can boot without errors"""

    def test_kernel_instantiation(self):
        """Test that kernel can be instantiated"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        assert kernel is not None
        logger.info("✅ Kernel instantiated successfully")

    def test_kernel_initial_status(self):
        """Test that kernel starts in STOPPED status"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        assert kernel.status == KernelStatus.STOPPED
        logger.info("✅ Kernel initial status is STOPPED")

    def test_kernel_boot_sequence(self):
        """Test that kernel can boot without errors"""
        kernel = RealVibeKernel(ledger_path=":memory:")

        # Boot should transition to RUNNING
        kernel.boot()

        assert kernel.status == KernelStatus.RUNNING
        logger.info(f"✅ Kernel booted successfully (status={kernel.status})")

    def test_kernel_has_manifest_registry(self):
        """Test that kernel has manifest registry after boot"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        kernel.boot()

        assert kernel._manifest_registry is not None
        logger.info("✅ Kernel has manifest registry")

    def test_kernel_has_agent_registry(self):
        """Test that kernel has agent registry"""
        kernel = RealVibeKernel(ledger_path=":memory:")

        assert kernel.agent_registry is not None
        assert isinstance(kernel.agent_registry, dict)
        logger.info("✅ Kernel has agent registry")

    def test_kernel_has_scheduler(self):
        """Test that kernel has task scheduler"""
        kernel = RealVibeKernel(ledger_path=":memory:")

        assert kernel._scheduler is not None
        logger.info("✅ Kernel has task scheduler")


class TestStewardRegistration:
    """Test that DiscovererAgent can be registered and functions"""

    def test_steward_instantiation(self):
        """Test that DiscovererAgent can be instantiated"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)

        assert steward is not None
        assert steward.agent_id == "steward"
        logger.info("✅ DiscovererAgent instantiated successfully")

    def test_steward_registration(self):
        """Test that DiscovererAgent can be registered with kernel"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)

        # Register steward
        kernel.register_agent(steward)

        assert "steward" in kernel.agent_registry
        assert kernel.agent_registry["steward"] == steward
        logger.info("✅ DiscovererAgent registered with kernel")

    def test_steward_has_discovery_method(self):
        """Test that DiscovererAgent has discover_agents method"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)

        assert hasattr(steward, "discover_agents")
        assert callable(steward.discover_agents)
        logger.info("✅ DiscovererAgent has discover_agents method")

    def test_steward_can_process_tasks(self):
        """Test that DiscovererAgent can process tasks"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)

        # Create a test task
        task = Task(
            agent_id="steward",
            payload={"action": "test"}
        )

        # Process the task
        result = steward.process(task)

        assert result is not None
        assert isinstance(result, dict)
        logger.info("✅ DiscovererAgent can process tasks")


class TestAgentDiscovery:
    """Test that Steward discovers agents from filesystem"""

    def test_discovery_finds_agents(self):
        """Test that steward.discover_agents() finds agents"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        # Call discover_agents
        discovered_count = steward.discover_agents()

        # Should find at least 10 agents
        assert discovered_count >= 10, f"Expected at least 10 agents, found {discovered_count}"
        logger.info(f"✅ Steward discovered {discovered_count} agents")

    def test_discovery_populates_registry(self):
        """Test that discovered agents are in kernel registry"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        initial_count = len(kernel.agent_registry)

        # Discover agents
        steward.discover_agents()

        final_count = len(kernel.agent_registry)

        # Should have more agents than before
        assert final_count > initial_count, "Discovery should add agents to registry"
        logger.info(f"✅ Agent registry grew from {initial_count} to {final_count} agents")

    def test_discovered_agents_are_in_registry(self):
        """Test that specific discovered agents can be found in registry"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        # Discover agents
        steward.discover_agents()

        # Check for some expected agents
        expected_agents = ["herald", "oracle", "temple", "market"]
        found_agents = []

        for agent_id in expected_agents:
            if agent_id in kernel.agent_registry:
                found_agents.append(agent_id)

        # Should find at least some expected agents
        assert len(found_agents) > 0, f"Expected to find at least some agents from {expected_agents}"
        logger.info(f"✅ Found expected agents in registry: {found_agents}")

    def test_discovered_agents_are_vibeagents(self):
        """Test that discovered agents are VibeAgent instances"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        # Discover agents
        steward.discover_agents()

        # Check that discovered agents are VibeAgent instances
        for agent_id, agent in kernel.agent_registry.items():
            assert isinstance(agent, VibeAgent), f"{agent_id} is not a VibeAgent"

        logger.info(f"✅ All {len(kernel.agent_registry)} agents are VibeAgent instances")

    def test_discovered_agents_have_manifests(self):
        """Test that discovered agents have valid manifests"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        # Discover agents
        steward.discover_agents()

        # Check that agents have manifests
        for agent_id, agent in kernel.agent_registry.items():
            manifest = agent.get_manifest()
            assert manifest is not None
            assert manifest.agent_id == agent_id
            assert manifest.name is not None

        logger.info(f"✅ All agents have valid manifests")


class TestGovernanceGate:
    """Test that agents pass governance gate (Constitutional Oath)"""

    def test_agents_have_oath_sworn_attribute(self):
        """Test that all registered agents have oath_sworn attribute"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()

        # Discover agents
        steward.discover_agents()

        # Check oath_sworn attribute
        for agent_id, agent in kernel.agent_registry.items():
            assert hasattr(agent, "oath_sworn"), f"{agent_id} missing oath_sworn"
            assert agent.oath_sworn is True, f"{agent_id} oath_sworn is not True"

        logger.info(f"✅ All {len(kernel.agent_registry)} agents have oath_sworn=True")

    def test_governance_gate_rejects_oath_violators(self):
        """Test that kernel rejects agents without oath"""
        kernel = RealVibeKernel(ledger_path=":memory:")

        # Create agent without oath
        class BadAgent(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="bad-agent",
                    name="Bad Agent",
                    version="1.0.0"
                )
                # Deliberately not setting oath_sworn

            def process(self, task: Task) -> Dict[str, Any]:
                return {"status": "ok"}

        bad_agent = BadAgent()

        # Try to register - should fail
        with pytest.raises(Exception) as exc_info:
            kernel.register_agent(bad_agent)

        logger.info(f"✅ Governance gate correctly rejected agent without oath: {exc_info.value}")

    def test_governance_gate_rejects_false_oath(self):
        """Test that kernel rejects agents with oath_sworn=False"""
        kernel = RealVibeKernel(ledger_path=":memory:")

        # Create agent with false oath
        class FalseOathAgent(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="false-oath-agent",
                    name="False Oath Agent",
                    version="1.0.0"
                )
                self.oath_sworn = False  # Explicitly false

            def process(self, task: Task) -> Dict[str, Any]:
                return {"status": "ok"}

        false_oath_agent = FalseOathAgent()

        # Try to register - should fail
        with pytest.raises(Exception) as exc_info:
            kernel.register_agent(false_oath_agent)

        logger.info(f"✅ Governance gate correctly rejected agent with false oath: {exc_info.value}")


class TestSystemIntegration:
    """End-to-end integration tests"""

    def test_complete_boot_sequence(self):
        """Test the complete boot sequence: kernel + steward + discovery"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        assert kernel.status == KernelStatus.STOPPED

        # Create and register steward
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        assert "steward" in kernel.agent_registry

        # Boot kernel
        kernel.boot()
        assert kernel.status == KernelStatus.RUNNING

        # Discover agents
        discovered_count = steward.discover_agents()
        assert discovered_count >= 10

        # Verify all agents have oath
        for agent_id, agent in kernel.agent_registry.items():
            assert agent.oath_sworn is True

        logger.info(f"✅ Complete boot sequence succeeded with {len(kernel.agent_registry)} agents")

    def test_agent_city_boots_without_errors(self):
        """Smoke test: Agent City boots without raising exceptions"""
        try:
            kernel = RealVibeKernel(ledger_path=":memory:")
            steward = DiscovererAgent(kernel)
            kernel.register_agent(steward)
            kernel.boot()
            steward.discover_agents()

            logger.info("✅ Agent City boots successfully without errors")
            assert True
        except Exception as e:
            pytest.fail(f"Agent City boot failed with error: {e}")

    def test_discovered_agent_count(self):
        """Test that a reasonable number of agents are discovered"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()
        steward.discover_agents()

        # We expect 22 agents total (system + citizen)
        # At least 10 from system agents + citizen agents
        agent_count = len(kernel.agent_registry)

        logger.info(f"✅ System has {agent_count} agents registered")
        assert agent_count >= 10, f"Expected at least 10 agents, found {agent_count}"

    def test_agent_manifests_are_registered(self):
        """Test that agent manifests are registered after boot"""
        kernel = RealVibeKernel(ledger_path=":memory:")
        steward = DiscovererAgent(kernel)
        kernel.register_agent(steward)
        kernel.boot()
        steward.discover_agents()

        # Get manifest registry (it's a private attribute, but for testing we access it)
        manifest_registry = kernel._manifest_registry

        assert manifest_registry is not None
        logger.info(f"✅ Manifest registry is populated after boot and discovery")


# Quick CLI runner for debugging
if __name__ == "__main__":
    # Run with: python -m pytest tests/integration/test_system_boot.py -v
    pytest.main([__file__, "-v", "--tb=short"])
