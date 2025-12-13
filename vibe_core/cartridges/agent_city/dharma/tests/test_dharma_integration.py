#!/usr/bin/env python3
"""
Integration Test: DHARMA Avatar (OPUS-031)
==========================================

PROOF OF LIFE test for the DHARMA cartridge.

Tests that:
1. DHARMA cartridge can be instantiated
2. Constitutional Oath is properly sworn (OathMixin)
3. Bridge to opus_assistant plugin works (or graceful fallback)
4. Economic flow works (credits are deducted for services)
5. Other agents can call DHARMA via system.call_agent()
6. All services respond correctly (seek_guidance, bless_action, check_karma, mediate)

This is NOT a mock test. We want to see the pipes are connected.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))


class TestDharmaInstantiation:
    """Tests for DHARMA cartridge instantiation."""

    def test_cartridge_importable(self):
        """DharmaCartridge can be imported."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        assert DharmaCartridge is not None

    def test_cartridge_instantiation(self):
        """DharmaCartridge can be instantiated."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        assert dharma is not None
        assert dharma.agent_id == "dharma"
        assert dharma.name == "DHARMA"
        assert dharma.domain == "GOVERNANCE"

    def test_cartridge_capabilities(self):
        """DharmaCartridge has correct capabilities."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        expected_capabilities = [
            "protocol_interpretation",
            "karmic_accounting",
            "architectural_guidance",
            "dispute_mediation",
            "action_blessing",
        ]

        for cap in expected_capabilities:
            assert cap in dharma.capabilities, f"Missing capability: {cap}"


class TestDharmaOath:
    """Tests for Constitutional Oath binding."""

    def test_oath_is_sworn(self):
        """DHARMA swears the Constitutional Oath on init."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        # OathMixin should be initialized and oath sworn
        assert hasattr(dharma, "oath_sworn"), "Missing oath_sworn attribute"
        assert dharma.oath_sworn is True, "Oath not sworn!"

    def test_oath_mixin_initialized(self):
        """OathMixin is properly initialized."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        # Check OathMixin sets agent_id (not _oath_agent_id)
        assert hasattr(dharma, "agent_id"), "agent_id not set"
        assert dharma.agent_id == "dharma"
        assert hasattr(dharma, "oath_sworn"), "oath_sworn not set"


class TestDharmaOpusBridge:
    """Tests for bridge to opus_assistant plugin."""

    def test_bridge_method_exists(self):
        """DHARMA has _get_opus_plugin method."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        assert hasattr(dharma, "_get_opus_plugin")
        assert callable(dharma._get_opus_plugin)

    def test_bridge_graceful_fallback_without_kernel(self):
        """DHARMA returns None when no kernel is available (graceful fallback)."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        # Without kernel/system, should return None gracefully
        result = dharma._get_opus_plugin()
        assert result is None  # Graceful fallback

    def test_channel_wisdom_fallback(self):
        """DHARMA provides fallback wisdom when opus is not available."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        # Channel wisdom without opus connection
        wisdom = asyncio.run(dharma._channel_opus_wisdom("test query"))

        assert wisdom is not None
        assert len(wisdom) > 0
        assert "test query" in wisdom  # Should reference the query


class TestDharmaServices:
    """Tests for DHARMA service methods."""

    def test_seek_guidance_without_bank(self):
        """seek_guidance works without bank (no credit deduction)."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        # Create task (agent_id is required first arg)
        task = Task(
            agent_id="dharma",
            payload={
                "action": "seek_guidance",
                "agent_id": "test_client",
                "query": "Should I refactor the kernel?",
            },
            task_id="test_1",
        )

        # Process task
        result = asyncio.run(dharma.process(task))

        assert result["status"] == "guidance_granted"
        assert result["seeker"] == "test_client"
        assert "guidance" in result
        assert result["cost"] == 10
        assert dharma.guidance_given == 1

    def test_bless_action_approved(self):
        """bless_action approves dharmic actions."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "bless_action",
                "agent_id": "mechanic",
                "action_type": "add_logging",
                "details": {"file": "utils.py"},
            },
            task_id="test_2",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "BLESSED"
        assert result["alignment"] == "SATTVIC"
        assert dharma.blessings_granted == 1

    def test_bless_action_denied_force(self):
        """bless_action denies forceful actions."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "bless_action",
                "agent_id": "bad_actor",
                "action_type": "force_push",  # Contains "force"
                "details": {},
            },
            task_id="test_3",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "DENIED"
        assert len(result["violations"]) > 0
        assert "Himsa" in result["violations"][0]  # Violence principle

    def test_bless_action_denied_bypass(self):
        """bless_action denies bypass actions."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "bless_action",
                "agent_id": "bad_actor",
                "action_type": "bypass_governance",
                "details": {},
            },
            task_id="test_4",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "DENIED"
        assert "Himsa" in result["violations"][0]

    def test_bless_action_denied_skip_tests(self):
        """bless_action denies skipping tests."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "bless_action",
                "agent_id": "impatient_dev",
                "action_type": "deploy",
                "details": {"skip_tests": True},
            },
            task_id="test_5",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "DENIED"
        assert any("Asteya" in v for v in result["violations"])

    def test_bless_action_denied_no_verify(self):
        """bless_action denies --no-verify."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "bless_action",
                "agent_id": "hasty_committer",
                "action_type": "commit",
                "details": {"flags": "--no-verify"},
            },
            task_id="test_6",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "DENIED"
        assert any("Aparigraha" in v for v in result["violations"])

    def test_check_karma_free(self):
        """check_karma is free and returns karma info."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "check_karma",
                "citizen_id": "herald",
            },
            task_id="test_7",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "karma_revealed"
        assert result["citizen"] == "herald"
        assert "karma_score" in result
        assert "karma_level" in result
        assert result["cost"] == 0  # FREE!
        assert dharma.karma_checks == 1

    def test_mediate_dispute(self):
        """mediate resolves disputes."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={
                "action": "mediate",
                "agent_id": "forum",
                "party_a": "herald",
                "party_b": "marketer",
                "dispute": "Content ownership disagreement",
            },
            task_id="test_8",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "mediation_complete"
        assert "herald" in result["parties"]
        assert "marketer" in result["parties"]
        assert result["ruling"]["binding"] is True
        assert "GAD-000" in result["ruling"]["principle"]
        assert dharma.disputes_mediated == 1

    def test_status_returns_info(self):
        """status action returns agent info."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={"action": "status"},
            task_id="test_9",
        )

        result = asyncio.run(dharma.process(task))

        assert result["agent_id"] == "dharma"
        assert result["status"] == "online"
        assert result["zone"] == "governance"
        assert result["oath_sworn"] is True

    def test_unknown_action_error(self):
        """Unknown actions return error."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        task = Task(
            agent_id="dharma",
            payload={"action": "unknown_action"},
            task_id="test_10",
        )

        result = asyncio.run(dharma.process(task))

        assert "error" in result
        assert "unknown_action" in result["error"]


class TestDharmaEconomy:
    """Tests for economic integration (credits)."""

    def test_service_costs_defined(self):
        """DHARMA has service costs defined."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        assert dharma.GUIDANCE_COST == 10
        assert dharma.BLESSING_COST == 5
        assert dharma.MEDIATION_COST == 20
        assert dharma.KARMA_CHECK_COST == 0

    def test_credits_collected_tracking(self):
        """DHARMA tracks total credits collected."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        # Perform services (without bank, no actual deduction)
        task1 = Task(agent_id="dharma", payload={"action": "seek_guidance", "query": "test"}, task_id="t1")
        task2 = Task(agent_id="dharma", payload={"action": "bless_action", "action_type": "test"}, task_id="t2")
        task3 = Task(agent_id="dharma", payload={"action": "check_karma", "citizen_id": "x"}, task_id="t3")

        asyncio.run(dharma.process(task1))
        asyncio.run(dharma.process(task2))
        asyncio.run(dharma.process(task3))

        # Should track: 10 + 5 + 0 = 15
        assert dharma.total_credits_collected == 15

    def test_bank_integration_insufficient_credits(self):
        """DHARMA rejects service when credits insufficient."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge
        from vibe_core.scheduling import Task

        dharma = DharmaCartridge()

        # Mock bank that rejects transfers
        mock_bank = MagicMock()
        mock_bank.transfer.side_effect = Exception("Insufficient credits")
        dharma.bank = mock_bank

        task = Task(
            agent_id="dharma",
            payload={
                "action": "seek_guidance",
                "agent_id": "broke_agent",
                "query": "Help me!",
            },
            task_id="poor_test",
        )

        result = asyncio.run(dharma.process(task))

        assert result["status"] == "insufficient_credits"
        assert result["required"] == 10


class TestDharmaKernelIntegration:
    """Integration tests with TestKernel (when available)."""

    def test_with_test_kernel(self):
        """DHARMA works with TestKernel."""
        try:
            from vibe_core.plugins.test_orchestration import TestKernel
        except ImportError:
            pytest.skip("TestKernel not available")

        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        # Create minimal kernel
        kernel = TestKernel.minimal()

        # Create DHARMA
        dharma = DharmaCartridge()

        # Register with kernel
        kernel.register_agent(dharma, spawn_process=False)

        # Verify registration
        assert dharma.system is not None
        assert dharma.oath_sworn is True

    def test_agent_can_call_dharma(self):
        """Another agent can call DHARMA via system.call_agent."""
        try:
            from vibe_core.plugins.test_orchestration import TestKernel
            from vibe_core.protocols import VibeAgent
            from vibe_core.steward import OathMixin
        except ImportError:
            pytest.skip("TestKernel not available")

        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        # Create mock client agent
        class ClientAgent(VibeAgent, OathMixin):
            def __init__(self):
                super().__init__(
                    agent_id="client",
                    name="Client Agent",
                    capabilities=["test"],
                )
                self.oath_mixin_init("client")
                self.swear_oath_sync()

            def process(self, task) -> Dict[str, Any]:
                return {"status": "ok"}

        # Create kernel and agents
        kernel = TestKernel.minimal()
        dharma = DharmaCartridge()
        client = ClientAgent()

        # Register both
        kernel.register_agent(dharma, spawn_process=False)
        kernel.register_agent(client, spawn_process=False)

        # Client calls DHARMA (if call_agent is available)
        if hasattr(client.system, "call_agent"):
            result = client.system.call_agent(
                "dharma",
                {"action": "check_karma", "citizen_id": "client"},
            )
            assert result is not None


class TestDharmaReportStatus:
    """Tests for report_status method."""

    def test_report_status(self):
        """report_status returns health info."""
        from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

        dharma = DharmaCartridge()

        status = dharma.report_status()

        assert status["agent_id"] == "dharma"
        assert status["name"] == "DHARMA"
        assert status["status"] == "healthy"
        assert status["domain"] == "GOVERNANCE"
        assert status["zone"] == "governance"
        assert "opus_bridge" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
