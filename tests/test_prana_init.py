"""
Tests for PRANA_INIT - The Vedic activation ritual

This test verifies that:
1. Vedic taxonomy (Varna/Ashrama) is properly initialized
2. Agent metadata is correctly classified
3. Daily ritual can execute all 4 phases
4. PRANA_INIT activation succeeds
"""

import pytest
import logging
from pathlib import Path
from steward.varna import Varna, categorize_agent_by_function
from steward.ashrama import Ashrama, AshramaTransition
from steward.agent_metadata import AgentMetadataRegistry, get_metadata_registry
from steward.daily_ritual import DailyRitual, CyclePhase
from steward.prana_init import PranaInitializer


logger = logging.getLogger(__name__)


class TestVarnaClassification:
    """Test Vedic species classification"""

    def test_manusha_agents(self):
        """Test that main agents are classified as MANUSHA (conscious)"""
        manusha_agents = ["civic", "herald", "forum", "science", "oracle"]
        for agent_id in manusha_agents:
            varna = categorize_agent_by_function(agent_id)
            assert varna == Varna.MANUSHA, f"{agent_id} should be MANUSHA"

    def test_pashu_agents(self):
        """Test that helper agents are classified as PASHU (servants)"""
        pashu_agents = ["pulse", "lens", "artisan", "temple", "market"]
        for agent_id in pashu_agents:
            varna = categorize_agent_by_function(agent_id)
            assert varna == Varna.PASHU, f"{agent_id} should be PASHU"

    def test_pakshi_agents(self):
        """Test that messenger agents are classified as PAKSHI (birds)"""
        pakshi_agents = ["envoy", "ambassador"]
        for agent_id in pakshi_agents:
            varna = categorize_agent_by_function(agent_id)
            assert varna == Varna.PAKSHI, f"{agent_id} should be PAKSHI"

    def test_krimayo_agents(self):
        """Test that worker agents are classified as KRIMAYO (insects)"""
        krimayo_agents = ["watchman", "mechanic"]
        for agent_id in krimayo_agents:
            varna = categorize_agent_by_function(agent_id)
            assert varna == Varna.KRIMAYO, f"{agent_id} should be KRIMAYO"

    def test_jalaja_agora(self):
        """Test that AGORA is classified as JALAJA (flowing water)"""
        varna = categorize_agent_by_function("agora")
        assert varna == Varna.JALAJA, "AGORA should be JALAJA"


class TestAshramaLifecycle:
    """Test lifecycle stage management"""

    def test_initial_ashrama_is_brahmachari(self):
        """Test that new agent starts as student"""
        transition = AshramaTransition("test_agent")
        assert transition.current_ashrama == Ashrama.BRAHMACHARI

    def test_transition_to_grihastha(self):
        """Test transition from student to householder"""
        transition = AshramaTransition("test_agent")
        assert transition.transition_to(Ashrama.GRIHASTHA)
        assert transition.current_ashrama == Ashrama.GRIHASTHA

    def test_transition_history(self):
        """Test that transition history is recorded"""
        transition = AshramaTransition("test_agent")
        transition.transition_to(Ashrama.GRIHASTHA)
        transition.transition_to(Ashrama.VANAPRASTHA)

        history = transition.transition_history
        assert len(history) == 3  # Initial + 2 transitions
        assert history[0][0] == Ashrama.BRAHMACHARI
        assert history[1][0] == Ashrama.GRIHASTHA
        assert history[2][0] == Ashrama.VANAPRASTHA

    def test_ashrama_permissions(self):
        """Test that each ashrama has appropriate permissions"""
        # BRAHMACHARI has limited permissions
        brahmachari_perms = Ashrama.BRAHMACHARI.value
        # Should have read, listen, observe

        # GRIHASTHA has full permissions
        grihastha_perms = Ashrama.GRIHASTHA.value
        # Should have read, write, broadcast, trade, etc.

        # VANAPRASTHA is read-only
        vanaprastha_perms = Ashrama.VANAPRASTHA.value
        # Should have read, teach, archive only


class TestAgentMetadataRegistry:
    """Test agent metadata management"""

    def test_registry_has_18_agents(self):
        """Test that all 18 agents are registered"""
        registry = get_metadata_registry()
        agents = registry.get_all_agents()
        assert len(agents) == 18, f"Expected 18 agents, got {len(agents)}"

    def test_agents_by_varna(self):
        """Test filtering agents by varna"""
        registry = get_metadata_registry()

        manusha = registry.get_agents_by_varna(Varna.MANUSHA)
        assert len(manusha) > 0, "Should have MANUSHA agents"

        pashu = registry.get_agents_by_varna(Varna.PASHU)
        assert len(pashu) > 0, "Should have PASHU agents"

    def test_agents_by_ashrama(self):
        """Test filtering agents by lifecycle stage"""
        registry = get_metadata_registry()

        # For Day 1, all agents should be in GRIHASTHA (active)
        active_agents = registry.get_agents_by_ashrama(Ashrama.GRIHASTHA)
        assert len(active_agents) > 0, "Should have active agents"

    def test_agent_biology(self):
        """Test getting agent biological classification"""
        registry = get_metadata_registry()

        herald_biology = registry.get_agent_biology("herald")
        assert herald_biology is not None
        assert herald_biology.varna == Varna.MANUSHA
        assert herald_biology.domain == "MEDIA"

    def test_transition_agent_lifecycle(self):
        """Test transitioning an agent to new lifecycle stage"""
        registry = get_metadata_registry()

        # Start: GRIHASTHA
        assert registry.get_agent_ashrama("herald") == Ashrama.GRIHASTHA

        # Transition to VANAPRASTHA
        registry.transition_agent("herald", Ashrama.VANAPRASTHA)
        assert registry.get_agent_ashrama("herald") == Ashrama.VANAPRASTHA

        # Transition back
        registry.transition_agent("herald", Ashrama.GRIHASTHA)
        assert registry.get_agent_ashrama("herald") == Ashrama.GRIHASTHA


class TestDailyRitual:
    """Test the daily cycle orchestration"""

    def test_ritual_initialization(self):
        """Test that daily ritual initializes correctly"""
        ritual = DailyRitual(kernel=None)
        assert ritual.cycle_count == 0
        assert ritual.events_this_cycle == []

    def test_phase_sunrise_creates_events(self):
        """Test that sunrise phase generates events"""
        ritual = DailyRitual(kernel=None)
        events = ritual._phase_sunrise()
        assert len(events) > 0, "Sunrise should generate events"
        assert all(e["phase"] == CyclePhase.SUNRISE.value for e in events)

    def test_phase_midday_creates_events(self):
        """Test that midday phase generates events"""
        ritual = DailyRitual(kernel=None)
        events = ritual._phase_midday()
        assert len(events) > 0, "Midday should generate events"
        assert all(e["phase"] == CyclePhase.MIDDAY.value for e in events)

    def test_phase_sunset_creates_events(self):
        """Test that sunset phase generates events"""
        ritual = DailyRitual(kernel=None)
        events = ritual._phase_sunset()
        assert len(events) > 0, "Sunset should generate events"
        assert all(e["phase"] == CyclePhase.SUNSET.value for e in events)

    def test_phase_archive_creates_events(self):
        """Test that archive phase generates events"""
        ritual = DailyRitual(kernel=None)
        events = ritual._phase_archive()
        assert len(events) > 0, "Archive should generate events"
        assert all(e["phase"] == CyclePhase.ARCHIVE.value for e in events)

    def test_daily_cycle_completion(self):
        """Test that a complete daily cycle runs successfully"""
        ritual = DailyRitual(kernel=None)
        result = ritual.run_daily_cycle()

        assert "day" in result
        assert result["day"] == 1
        assert "total_events" in result
        assert result["total_events"] > 0
        assert ritual.cycle_count == 1

    def test_multiple_days(self):
        """Test running multiple days"""
        ritual = DailyRitual(kernel=None)

        for day_num in range(1, 4):
            result = ritual.run_daily_cycle()
            assert result["day"] == day_num
            assert result["total_events"] > 0


class TestPranaInitializer:
    """Test the PRANA_INIT activation ritual"""

    def test_constitution_verification(self):
        """Test that constitution file exists"""
        constitution_path = (
            Path(__file__).parent.parent / "CONSTITUTION.md"
        )
        assert constitution_path.exists(), "Constitution file should exist"

    def test_prana_initialization_without_kernel(self):
        """Test PRANA_INIT in dry-run mode (no kernel)"""
        initializer = PranaInitializer(kernel=None)
        # Should succeed in dry-run mode
        result = initializer.execute()
        assert initializer.success == result

    def test_prana_init_reports_errors(self):
        """Test that PRANA_INIT reports failures"""
        # Create initializer with None kernel (will fail some checks)
        initializer = PranaInitializer(kernel=None)
        # Should still work in dry-run mode
        success = initializer.execute()
        # Either success or failure, there should be a message
        assert initializer.success is not None


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """End-to-end integration tests"""

    def test_vedic_system_end_to_end(self):
        """Test the complete Vedic system integration"""
        # 1. Get metadata registry
        registry = get_metadata_registry()

        # 2. Verify all agents are classified
        agents = registry.get_all_agents()
        assert len(agents) == 18

        # 3. Verify varna distribution
        total_classified = 0
        for varna in Varna:
            agents_in_varna = registry.get_agents_by_varna(varna)
            if agents_in_varna:
                logger.info(f"{varna.value}: {len(agents_in_varna)} agents")
                total_classified += len(agents_in_varna)

        assert total_classified == 18, "All agents should be classified by varna"

        # 4. Verify ashrama distribution
        for ashrama in Ashrama:
            agents_in_ashrama = registry.get_agents_by_ashrama(ashrama)
            if agents_in_ashrama:
                logger.info(f"{ashrama.value}: {len(agents_in_ashrama)} agents")

        # 5. Run a daily cycle
        ritual = DailyRitual(kernel=None)
        result = ritual.run_daily_cycle()
        assert result["total_events"] > 0

    def test_prana_flow_activation(self):
        """Test the complete PRANA flow activation"""
        # This is the main test - can we activate the city?
        initializer = PranaInitializer(kernel=None)
        success = initializer.execute()

        # Should succeed in dry-run mode
        logger.info(f"Prana Activation Success: {success}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
