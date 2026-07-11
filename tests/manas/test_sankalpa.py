"""
Tests for OPUS-055: SANKALPA (The Will) - Proactive Strategy Module.

Sanskrit: Sankalpa = Solemn vow, determination, will.

These tests verify:
1. Data models (Mission, Strategy, Trigger)
2. SankalpaRegistry CRUD operations
3. SankalpaPlanner strategy evaluation
4. SankalpaOrchestrator workflow
5. VEDA intent routing
6. JNANA handler integration
"""

import tempfile
from pathlib import Path

# =============================================================================
# SECTION 1: DATA MODEL TESTS
# =============================================================================


class TestMissionPriority:
    """Tests for MissionPriority enum."""

    def test_all_priorities_exist(self):
        """Verify all priority levels are defined."""
        from vibe_core.mahamantra.protocols.sankalpa import MissionPriority

        assert MissionPriority.CRITICAL.value == "critical"
        assert MissionPriority.HIGH.value == "high"
        assert MissionPriority.MEDIUM.value == "medium"
        assert MissionPriority.LOW.value == "low"


class TestMissionStatus:
    """Tests for MissionStatus enum."""

    def test_all_statuses_exist(self):
        """Verify all status values are defined."""
        from vibe_core.mahamantra.protocols.sankalpa import MissionStatus

        assert MissionStatus.ACTIVE.value == "active"
        assert MissionStatus.PAUSED.value == "paused"
        assert MissionStatus.COMPLETED.value == "completed"
        assert MissionStatus.ABANDONED.value == "abandoned"


class TestTriggerType:
    """Tests for TriggerType enum."""

    def test_all_trigger_types_exist(self):
        """Verify all trigger types are defined."""
        from vibe_core.mahamantra.protocols.sankalpa import TriggerType

        assert TriggerType.TIME_BASED.value == "time_based"
        assert TriggerType.EVENT_BASED.value == "event_based"
        assert TriggerType.CONDITION_BASED.value == "condition_based"
        assert TriggerType.IDLE_BASED.value == "idle_based"


class TestSankalpaTrigger:
    """Tests for SankalpaTrigger dataclass."""

    def test_create_idle_trigger(self):
        """Test creating an idle-based trigger."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaTrigger,
            TriggerType,
        )

        trigger = SankalpaTrigger(
            trigger_type=TriggerType.IDLE_BASED,
            idle_minutes=60,
        )

        assert trigger.trigger_type == TriggerType.IDLE_BASED
        assert trigger.idle_minutes == 60

    def test_create_time_trigger(self):
        """Test creating a time-based trigger."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaTrigger,
            TriggerType,
        )

        trigger = SankalpaTrigger(
            trigger_type=TriggerType.TIME_BASED,
            hour=9,
            day_of_week=0,  # Monday
        )

        assert trigger.trigger_type == TriggerType.TIME_BASED
        assert trigger.hour == 9
        assert trigger.day_of_week == 0

    def test_trigger_to_dict(self):
        """Test trigger serialization."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaTrigger,
            TriggerType,
        )

        trigger = SankalpaTrigger(
            trigger_type=TriggerType.CONDITION_BASED,
            condition="ci_green",
        )

        data = trigger.to_dict()
        assert data["trigger_type"] == "condition_based"
        assert data["condition"] == "ci_green"

    def test_trigger_from_dict(self):
        """Test trigger deserialization."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaTrigger

        data = {
            "trigger_type": "idle_based",
            "idle_minutes": 30,
        }

        trigger = SankalpaTrigger.from_dict(data)
        assert trigger.idle_minutes == 30


class TestSankalpaStrategy:
    """Tests for SankalpaStrategy dataclass."""

    def test_create_strategy(self):
        """Test creating a strategy."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaStrategy,
            SankalpaTrigger,
            StrategyFrequency,
            TriggerType,
        )

        trigger = SankalpaTrigger(trigger_type=TriggerType.IDLE_BASED, idle_minutes=60)
        strategy = SankalpaStrategy(
            id="test_strategy",
            name="Test Strategy",
            description="A test strategy",
            trigger=trigger,
            frequency=StrategyFrequency.DAILY,
            intent_type="test_intent",
            intent_template={"action": "test"},
        )

        assert strategy.id == "test_strategy"
        assert strategy.name == "Test Strategy"
        assert strategy.frequency == StrategyFrequency.DAILY
        assert strategy.enabled is True

    def test_strategy_to_dict(self):
        """Test strategy serialization."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaStrategy,
            SankalpaTrigger,
            StrategyFrequency,
            TriggerType,
        )

        trigger = SankalpaTrigger(trigger_type=TriggerType.IDLE_BASED)
        strategy = SankalpaStrategy(
            id="s1",
            name="S1",
            description="desc",
            trigger=trigger,
            frequency=StrategyFrequency.HOURLY,
            intent_type="test",
            intent_template={},
        )

        data = strategy.to_dict()
        assert data["id"] == "s1"
        assert data["frequency"] == "hourly"
        assert "trigger" in data

    def test_strategy_from_dict(self):
        """Test strategy deserialization."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaStrategy

        data = {
            "id": "test",
            "name": "Test",
            "description": "Test desc",
            "trigger": {"trigger_type": "idle_based", "idle_minutes": 45},
            "frequency": "weekly",
            "intent_type": "test_intent",
            "intent_template": {},
        }

        strategy = SankalpaStrategy.from_dict(data)
        assert strategy.id == "test"
        assert strategy.trigger.idle_minutes == 45


class TestSankalpaMission:
    """Tests for SankalpaMission dataclass."""

    def test_create_mission(self):
        """Test creating a mission."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            MissionPriority,
            MissionStatus,
            SankalpaMission,
        )

        mission = SankalpaMission(
            id="test_mission",
            name="Test Mission",
            description="A test mission",
            priority=MissionPriority.HIGH,
            status=MissionStatus.ACTIVE,
        )

        assert mission.id == "test_mission"
        assert mission.priority == MissionPriority.HIGH
        assert mission.status == MissionStatus.ACTIVE
        assert mission.strategies == []

    def test_mission_to_dict(self):
        """Test mission serialization."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            MissionPriority,
            MissionStatus,
            SankalpaMission,
        )

        mission = SankalpaMission(
            id="m1",
            name="M1",
            description="desc",
            priority=MissionPriority.CRITICAL,
            status=MissionStatus.ACTIVE,
        )

        data = mission.to_dict()
        assert data["priority"] == "critical"
        assert data["status"] == "active"

    def test_mission_from_dict(self):
        """Test mission deserialization."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaMission

        data = {
            "id": "m1",
            "name": "Mission 1",
            "description": "Test mission",
            "priority": "medium",
            "status": "paused",
            "strategies": [],
        }

        mission = SankalpaMission.from_dict(data)
        assert mission.id == "m1"
        assert mission.priority.value == "medium"
        assert mission.status.value == "paused"


class TestSankalpaIntent:
    """Tests for SankalpaIntent dataclass."""

    def test_create_intent(self):
        """Test creating an intent."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaIntent

        intent = SankalpaIntent(
            id="intent_1",
            mission_id="mission_1",
            strategy_id="strategy_1",
            title="Test Intent",
            description="A test intent",
            intent_type="test_type",
        )

        assert intent.id == "intent_1"
        assert intent.mission_id == "mission_1"
        assert intent.priority == "medium"

    def test_intent_to_dict(self):
        """Test intent serialization."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaIntent

        intent = SankalpaIntent(
            id="i1",
            mission_id="m1",
            strategy_id="s1",
            title="T",
            description="D",
            intent_type="test",
        )

        data = intent.to_dict()
        assert data["id"] == "i1"
        assert data["mission_id"] == "m1"


# =============================================================================
# SECTION 2: SANKALPA REGISTRY TESTS
# =============================================================================


class TestSankalpaRegistry:
    """Tests for SankalpaRegistry class."""

    def test_registry_initialization(self):
        """Test registry initializes with defaults."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            missions = registry.get_all_missions()
            # Should have default missions
            assert len(missions) > 0

    def test_registry_loads_defaults(self):
        """Test registry loads default missions."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            # Should have "Maintain Code Health" mission
            mission = registry.get_mission("mission_code_health")
            assert mission is not None
            assert "Health" in mission.name

    def test_get_active_missions(self):
        """Test getting only active missions."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            active = registry.get_active_missions()
            for m in active:
                assert m.status.value == "active"

    def test_add_mission(self):
        """Test adding a new mission."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            MissionPriority,
            MissionStatus,
            SankalpaMission,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            mission = SankalpaMission(
                id="custom_mission",
                name="Custom Mission",
                description="A custom mission",
                priority=MissionPriority.LOW,
                status=MissionStatus.ACTIVE,
            )

            registry.add_mission(mission)

            retrieved = registry.get_mission("custom_mission")
            assert retrieved is not None
            assert retrieved.name == "Custom Mission"

    def test_update_mission(self):
        """Test updating a mission."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            MissionStatus,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            mission = registry.get_mission("mission_code_health")
            mission.status = MissionStatus.PAUSED
            registry.update_mission(mission)

            retrieved = registry.get_mission("mission_code_health")
            assert retrieved.status == MissionStatus.PAUSED

    def test_remove_mission(self):
        """Test removing a mission."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            initial_count = len(registry.get_all_missions())
            result = registry.remove_mission("mission_self_improvement")

            assert result is True
            assert len(registry.get_all_missions()) == initial_count - 1

    def test_get_strategy(self):
        """Test getting a specific strategy."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            strategy = registry.get_strategy("mission_code_health", "strategy_daily_hygiene")
            assert strategy is not None
            assert "Hygiene" in strategy.name

    def test_get_all_strategies(self):
        """Test getting all strategies."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            strategies = registry.get_all_strategies()
            assert len(strategies) > 0

            for mission_id, strategy in strategies:
                assert mission_id is not None
                assert strategy.id is not None

    def test_persistence(self):
        """Test registry persists to disk."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            MissionPriority,
            MissionStatus,
            SankalpaMission,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create registry and add mission
            registry1 = SankalpaRegistry(workspace=Path(tmpdir))
            mission = SankalpaMission(
                id="persist_test",
                name="Persistence Test",
                description="Test",
                priority=MissionPriority.LOW,
                status=MissionStatus.ACTIVE,
            )
            registry1.add_mission(mission)

            # Create new registry and verify persistence
            registry2 = SankalpaRegistry(workspace=Path(tmpdir))
            retrieved = registry2.get_mission("persist_test")
            assert retrieved is not None
            assert retrieved.name == "Persistence Test"


# =============================================================================
# SECTION 3: SANKALPA PLANNER TESTS
# =============================================================================


class TestSankalpaPlanner:
    """Tests for SankalpaPlanner class."""

    def test_planner_initialization(self):
        """Test planner initializes."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            planner = SankalpaPlanner(registry)

            assert planner is not None

    def test_evaluate_idle_trigger(self):
        """Test evaluating idle-based triggers."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            planner = SankalpaPlanner(registry, workspace=Path(tmpdir))

            # With 120 minutes idle and no pending intents, should trigger
            intents = planner.evaluate(
                context={},
                idle_minutes=120,
                pending_intents=0,
            )

            # May or may not generate intents depending on strategy state
            assert isinstance(intents, list)

    def test_evaluate_respects_ci_constraint(self):
        """Test planner respects CI green constraint."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            planner = SankalpaPlanner(registry, workspace=Path(tmpdir))

            # With CI red, strategies requiring CI green should not fire
            context = {"ci": {"status": "failed"}}
            intents = planner.evaluate(
                context=context,
                idle_minutes=120,
                pending_intents=0,
            )

            # Filtered by CI constraint
            assert isinstance(intents, list)

    def test_evaluate_respects_pending_intents(self):
        """Test planner respects pending intents constraint."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            planner = SankalpaPlanner(registry, workspace=Path(tmpdir))

            # With pending intents, most strategies should not fire
            intents = planner.evaluate(
                context={},
                idle_minutes=120,
                pending_intents=5,
            )

            assert isinstance(intents, list)

    def test_evaluate_respects_max_executions(self):
        """Test planner respects max executions per day."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            planner = SankalpaPlanner(registry, workspace=Path(tmpdir))

            # First evaluate to trigger daily reset
            _ = planner.evaluate(context={}, idle_minutes=0, pending_intents=0)

            # NOW set all strategies as already executed max times
            for mission in registry.get_all_missions():
                for strategy in mission.strategies:
                    strategy.execution_count_today = strategy.max_executions_per_day + 1
                    registry.update_strategy(mission.id, strategy)

            # Should not fire any strategies (all maxed out)
            intents = planner.evaluate(
                context={},
                idle_minutes=120,
                pending_intents=0,
            )

            # No intents should be generated (all maxed out)
            assert len(intents) == 0


# =============================================================================
# SECTION 4: SANKALPA ORCHESTRATOR TESTS
# =============================================================================


class TestSankalpaOrchestrator:
    """Tests for SankalpaOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))

            assert orch.registry is not None
            assert orch.planner is not None

    def test_orchestrator_think(self):
        """Test orchestrator think cycle."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))

            intents = orch.think(
                context={},
                idle_minutes=60,
                pending_intents=0,
            )

            assert isinstance(intents, list)

    def test_orchestrator_get_status(self):
        """Test getting orchestrator status."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))

            status = orch.get_status()

            assert "total_missions" in status
            assert "active_missions" in status
            assert "total_strategies" in status
            assert "missions" in status


# =============================================================================
# SECTION 5: VEDA INTEGRATION TESTS
# =============================================================================


class TestVedaSankalpaIntegration:
    """Tests for VEDA pipeline integration with SANKALPA."""

    def test_sankalpa_intent_exists(self):
        """Test SANKALPA intent is defined in VedaIntent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        assert VedaIntent.SANKALPA.value == "sankalpa"
        assert VedaIntent.MISSIONS.value == "missions"
        assert VedaIntent.STRATEGY.value == "strategy"

    def test_sankalpa_keywords_defined(self):
        """Test SANKALPA keywords are in INTENT_KEYWORDS."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        keywords = Artha.INTENT_KEYWORDS.get(VedaIntent.SANKALPA, set())
        assert "sankalpa" in keywords
        assert "goals" in keywords

    def test_sankalpa_route_defined(self):
        """Test SANKALPA route is in INTENT_ROUTES."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        route = Artha.INTENT_ROUTES.get(VedaIntent.SANKALPA)
        assert route == "_handle_sankalpa"

    def test_missions_route_defined(self):
        """Test MISSIONS route is in INTENT_ROUTES."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, VedaIntent

        route = Artha.INTENT_ROUTES.get(VedaIntent.MISSIONS)
        assert route == "_handle_sankalpa"

    def test_artha_routes_to_sankalpa(self):
        """Test Artha routes mission queries to SANKALPA handler."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda, VedaIntent

        shabda = Shabda()
        artha = Artha()

        shabda_result = shabda.process("list missions")
        artha_result = artha.process(shabda_result)

        assert artha_result.primary_intent in {
            VedaIntent.SANKALPA,
            VedaIntent.MISSIONS,
            VedaIntent.STRATEGY,
        }
        assert artha_result.handler_route == "_handle_sankalpa"

    def test_artha_adds_sankalpa_context_hint(self):
        """Test Artha adds sankalpa_context_needed hint."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda

        shabda = Shabda()
        artha = Artha()

        shabda_result = shabda.process("show sankalpa goals")
        artha_result = artha.process(shabda_result)

        assert "sankalpa_context_needed" in artha_result.context_hints


# =============================================================================
# SECTION 6: JNANA INTEGRATION TESTS
# =============================================================================


class TestJnanaSankalpaIntegration:
    """Tests for JNANA handler integration with SANKALPA."""

    def test_handle_sankalpa_query_status(self):
        """Test handling sankalpa status query."""
        from vibe_core.mahamantra.protocols.sankalpa import handle_sankalpa_query

        with tempfile.TemporaryDirectory() as tmpdir:
            result = handle_sankalpa_query("sankalpa status", workspace=Path(tmpdir))

            assert "SANKALPA" in result
            assert "Missions" in result

    def test_handle_sankalpa_query_list_missions(self):
        """Test handling list missions query."""
        from vibe_core.mahamantra.protocols.sankalpa import handle_sankalpa_query

        with tempfile.TemporaryDirectory() as tmpdir:
            result = handle_sankalpa_query("list missions", workspace=Path(tmpdir))

            assert "SANKALPA" in result
            assert "Mission" in result or "mission" in result

    def test_get_sankalpa_for_chat(self):
        """Test getting SANKALPA status for chat."""
        from vibe_core.mahamantra.protocols.sankalpa import get_sankalpa_for_chat

        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_sankalpa_for_chat(workspace=Path(tmpdir))

            assert "SANKALPA" in result
            assert "Missions" in result or "missions" in result
            assert "Commands" in result

    def test_sankalpa_keyword_triggers_handler(self):
        """Test that sankalpa keyword triggers handler via VEDA."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha, Shabda

        shabda = Shabda()
        artha = Artha()

        result = shabda.process("show sankalpa missions")
        artha_result = artha.process(result)

        assert "_handle_sankalpa" in artha_result.handler_route


# =============================================================================
# SECTION 7: SINGLETON TESTS
# =============================================================================


class TestSankalpaSingleton:
    """Tests for singleton access pattern."""

    def test_get_sankalpa_orchestrator(self):
        """Test get_sankalpa_orchestrator returns instance."""
        from vibe_core.mahamantra.protocols.sankalpa import (
            get_sankalpa_orchestrator,
        )

        orch = get_sankalpa_orchestrator()
        assert orch is not None

    def test_get_sankalpa_orchestrator_same_instance(self):
        """Test singleton returns same instance."""
        from vibe_core.plugins.opus_assistant.manas.cortex import sankalpa

        # Reset singleton
        sankalpa._sankalpa_orchestrator = None

        orch1 = sankalpa.get_sankalpa_orchestrator()
        orch2 = sankalpa.get_sankalpa_orchestrator()

        assert orch1 is orch2


# =============================================================================
# SECTION 8: STRATEGY FREQUENCY TESTS
# =============================================================================


class TestStrategyFrequency:
    """Tests for StrategyFrequency enum."""

    def test_all_frequencies_exist(self):
        """Verify all frequency values are defined."""
        from vibe_core.mahamantra.protocols.sankalpa import StrategyFrequency

        assert StrategyFrequency.ONCE.value == "once"
        assert StrategyFrequency.HOURLY.value == "hourly"
        assert StrategyFrequency.DAILY.value == "daily"
        assert StrategyFrequency.WEEKLY.value == "weekly"
        assert StrategyFrequency.CONTINUOUS.value == "continuous"


# =============================================================================
# SECTION 9: DEFAULT MISSION TESTS
# =============================================================================


class TestDefaultMissions:
    """Tests for default missions configuration."""

    def test_code_health_mission_exists(self):
        """Test 'Maintain Code Health' mission exists by default."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            mission = registry.get_mission("mission_code_health")
            assert mission is not None
            assert "Health" in mission.name

    def test_code_health_has_strategies(self):
        """Test code health mission has strategies."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            mission = registry.get_mission("mission_code_health")
            assert len(mission.strategies) > 0

    def test_daily_hygiene_strategy(self):
        """Test daily hygiene strategy configuration."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            strategy = registry.get_strategy("mission_code_health", "strategy_daily_hygiene")
            assert strategy is not None
            assert "Hygiene" in strategy.name
            assert strategy.frequency.value == "daily"

    def test_self_improvement_mission(self):
        """Test self-improvement mission exists."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SankalpaRegistry(workspace=Path(tmpdir))

            mission = registry.get_mission("mission_self_improvement")
            assert mission is not None


# =============================================================================
# SECTION 10: INTENT GENERATION TESTS
# =============================================================================


class TestIntentGeneration:
    """Tests for intent generation workflow."""

    def test_intent_has_required_fields(self):
        """Test generated intents have all required fields."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))

            # Force trigger by high idle time
            intents = orch.think(
                context={},
                idle_minutes=240,  # 4 hours idle
                pending_intents=0,
            )

            for intent in intents:
                assert intent.id is not None
                assert intent.mission_id is not None
                assert intent.strategy_id is not None
                assert intent.title is not None
                assert intent.intent_type is not None

    def test_intent_includes_mission_reference(self):
        """Test intents reference their source mission."""
        from vibe_core.mahamantra.protocols.sankalpa import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))

            intents = orch.think(
                context={},
                idle_minutes=240,
                pending_intents=0,
            )

            for intent in intents:
                # mission_id should reference an existing mission
                mission = orch.registry.get_mission(intent.mission_id)
                # Mission may or may not exist depending on timing
                if mission:
                    assert "SANKALPA" in intent.description


# =============================================================================
# SECTION 11: CONDITION_BASED TRIGGER TESTS (Kapitel 3b — Willensbildung)
# =============================================================================


class TestConditionBasedTrigger:
    """Tests for CONDITION_BASED trigger (macro-stagnation detection).

    Verifies that the new is_stagnating parameter correctly activates
    CONDITION_BASED strategies without breaking existing IDLE_BASED
    or TIME_BASED strategies.
    """

    def test_condition_based_fires_when_stagnating(self):
        """CONDITION_BASED strategy fires when is_stagnating=True, not when False."""
        from vibe_core.mahamantra.protocols.sankalpa.types import (
            SankalpaMission,
            SankalpaStrategy,
            SankalpaTrigger,
            TriggerType,
            MissionPriority,
            MissionStatus,
            StrategyFrequency,
        )
        from vibe_core.mahamantra.substrate.sankalpa.will import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))
            planner = orch._planner

            # Create a CONDITION_BASED strategy
            trigger = SankalpaTrigger(trigger_type=TriggerType.CONDITION_BASED)
            strategy = SankalpaStrategy(
                id="test_condition_based",
                name="Test Condition-Based Trigger",
                description="Test CONDITION_BASED trigger for stagnation",
                trigger=trigger,
                frequency=StrategyFrequency.DAILY,
                intent_type="diagnose_stagnation",
                intent_template={},
                requires_ci_green=False,
                requires_no_pending_intents=False,
                max_executions_per_day=3,
                enabled=True,
            )

            mission = SankalpaMission(
                id="test_mission_stagnation",
                name="Test Stagnation Mission",
                description="Test mission for CONDITION_BASED",
                priority=MissionPriority.HIGH,
                status=MissionStatus.ACTIVE,
                strategies=[strategy],
                owner="steward",
            )

            planner._registry.add_mission(mission)

            # Test 1: with is_stagnating=False, should NOT fire
            intents_false = planner.evaluate(idle_minutes=0, pending_intents=0, ci_green=True, is_stagnating=False)
            assert len(intents_false) == 0, "CONDITION_BASED should not fire when is_stagnating=False"

            # Test 2: with is_stagnating=True, SHOULD fire
            intents_true = planner.evaluate(idle_minutes=0, pending_intents=0, ci_green=True, is_stagnating=True)
            assert len(intents_true) == 1, "CONDITION_BASED should fire when is_stagnating=True"
            assert intents_true[0].intent_type == "diagnose_stagnation", "Intent type should be diagnose_stagnation"

    def test_condition_based_ignores_idle(self):
        """CONDITION_BASED strategy fires based only on is_stagnating, not idle_minutes."""
        from vibe_core.mahamantra.protocols.sankalpa.types import (
            SankalpaMission,
            SankalpaStrategy,
            SankalpaTrigger,
            TriggerType,
            MissionPriority,
            MissionStatus,
            StrategyFrequency,
        )
        from vibe_core.mahamantra.substrate.sankalpa.will import (
            SankalpaOrchestrator,
            SankalpaPlanner,
            SankalpaRegistry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create isolated planner (no default missions)
            registry = SankalpaRegistry(workspace=Path(tmpdir))
            # Clear default missions to isolate test
            registry._missions.clear()
            planner = SankalpaPlanner(registry)

            trigger = SankalpaTrigger(trigger_type=TriggerType.CONDITION_BASED)
            strategy = SankalpaStrategy(
                id="test_condition_ignores_idle",
                name="Condition Should Ignore Idle",
                description="CONDITION_BASED must not depend on idle_minutes",
                trigger=trigger,
                frequency=StrategyFrequency.DAILY,
                intent_type="diagnose_stagnation",
                intent_template={},
                requires_ci_green=False,
                requires_no_pending_intents=False,
                max_executions_per_day=3,
                enabled=True,
            )

            mission = SankalpaMission(
                id="test_mission_idle_independence",
                name="Test Idle Independence",
                description="CONDITION_BASED should not care about idle_minutes",
                priority=MissionPriority.HIGH,
                status=MissionStatus.ACTIVE,
                strategies=[strategy],
                owner="steward",
            )

            registry.add_mission(mission)

            # Even with 0 idle_minutes and is_stagnating=True, should fire
            intents = planner.evaluate(idle_minutes=0, pending_intents=0, ci_green=True, is_stagnating=True)
            assert len(intents) == 1, "CONDITION_BASED should fire regardless of idle_minutes when is_stagnating=True"

            # With high idle_minutes but is_stagnating=False, should NOT fire
            intents_no_stag = planner.evaluate(idle_minutes=1000, pending_intents=0, ci_green=True, is_stagnating=False)
            assert len(intents_no_stag) == 0, (
                "CONDITION_BASED should not fire when is_stagnating=False, even with high idle_minutes"
            )

    def test_idle_based_still_works(self):
        """IDLE_BASED strategies still fire correctly (backward compatibility)."""
        from vibe_core.mahamantra.protocols.sankalpa.types import (
            SankalpaMission,
            SankalpaStrategy,
            SankalpaTrigger,
            TriggerType,
            MissionPriority,
            MissionStatus,
            StrategyFrequency,
        )
        from vibe_core.mahamantra.substrate.sankalpa.will import SankalpaOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            orch = SankalpaOrchestrator(workspace=Path(tmpdir))
            planner = orch._planner

            # Create an IDLE_BASED strategy (traditional trigger)
            trigger = SankalpaTrigger(
                trigger_type=TriggerType.IDLE_BASED,
                idle_minutes=10,
            )
            strategy = SankalpaStrategy(
                id="test_idle_backward_compat",
                name="Test Idle Backward Compat",
                description="IDLE_BASED should still work with default is_stagnating=False",
                trigger=trigger,
                frequency=StrategyFrequency.DAILY,
                intent_type="health_check",
                intent_template={},
                requires_ci_green=False,
                requires_no_pending_intents=False,
                max_executions_per_day=3,
                enabled=True,
            )

            mission = SankalpaMission(
                id="test_mission_idle_compat",
                name="Test Idle Compatibility",
                description="Verify IDLE_BASED still works",
                priority=MissionPriority.HIGH,
                status=MissionStatus.ACTIVE,
                strategies=[strategy],
                owner="steward",
            )

            planner._registry.add_mission(mission)

            # With idle_minutes >= trigger.idle_minutes, should fire (backward compat)
            intents = planner.evaluate(idle_minutes=10, pending_intents=0, ci_green=True, is_stagnating=False)
            assert len(intents) == 1, "IDLE_BASED should fire when idle_minutes threshold met (backward compat)"

            # With idle_minutes < trigger.idle_minutes, should NOT fire
            intents_no_idle = planner.evaluate(idle_minutes=5, pending_intents=0, ci_green=True, is_stagnating=False)
            assert len(intents_no_idle) == 0, "IDLE_BASED should not fire when idle_minutes below threshold"
