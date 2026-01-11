"""
Tests for Janaka Cognitive Cycle Protocol.

Owner: JANAKA (Duty/Execution)
WATERTIGHT: All types explicit, no Any.
"""

import pytest
from typing import List

from vibe_core.protocols.mahajanas.janaka import (
    # Cycle types
    CyclePhase,
    CycleStatus,
    CycleElement,
    PhaseResult,
    CycleContextState,
    RetentionConfig,
    CycleRegistryStats,
    CycleState,
    # Cycle protocols
    CognitiveCycleProtocol,
    CycleRegistryProtocol,
    CycleOwnedProtocol,
    # Null implementations
    NullCognitiveCycle,
    NullCycleRegistry,
)
from vibe_core.protocols.mahajanas.router import Mahajana


class TestCyclePhases:
    """Test CyclePhase enum."""

    def test_phase_values(self) -> None:
        """All OODA phases should be defined."""
        assert CyclePhase.PERCEIVE.value == "perceive"
        assert CyclePhase.ORIENT.value == "orient"
        assert CyclePhase.DECIDE.value == "decide"
        assert CyclePhase.ACT.value == "act"
        assert CyclePhase.PERSIST.value == "persist"
        assert CyclePhase.RECOVER.value == "recover"

    def test_status_values(self) -> None:
        """All cycle statuses should be defined."""
        assert CycleStatus.PENDING.value == "pending"
        assert CycleStatus.RUNNING.value == "running"
        assert CycleStatus.COMPLETED.value == "completed"
        assert CycleStatus.FAILED.value == "failed"
        assert CycleStatus.THROTTLED.value == "throttled"


class TestCognitiveCycleProtocol:
    """Test CognitiveCycleProtocol types and interfaces."""

    def test_owner_is_janaka(self) -> None:
        """ANTI-MAYAVAD: Cycle is owned by JANAKA (Position 10)."""
        from vibe_core.mahamantra import mahamantra
        assert mahamantra[10].guardian == Mahajana.JANAKA

    def test_null_cycle_implements_protocol(self) -> None:
        """NullCognitiveCycle should work as a drop-in replacement."""
        cycle = NullCognitiveCycle()
        assert cycle.cycle_name == "null_cycle"
        assert cycle.rate_limit_seconds == 0
        assert cycle.timeout_seconds == 0
        assert cycle.recovery_enabled is False
        assert cycle.parent_cycle_id is None

    def test_null_cycle_perceive(self) -> None:
        """NullCognitiveCycle perceive should return PhaseResult."""
        cycle = NullCognitiveCycle()
        result: PhaseResult = cycle.perceive()

        assert result["phase"] == "perceive"
        assert result["success"] is True
        assert result["elements_count"] == 0
        assert result["error_message"] == ""

    def test_null_cycle_orient(self) -> None:
        """NullCognitiveCycle orient should accept observation count."""
        cycle = NullCognitiveCycle()
        result: PhaseResult = cycle.orient(observations_count=5)

        assert result["phase"] == "orient"
        assert result["success"] is True

    def test_null_cycle_decide(self) -> None:
        """NullCognitiveCycle decide should accept orientation count."""
        cycle = NullCognitiveCycle()
        result: PhaseResult = cycle.decide(orientations_count=3)

        assert result["phase"] == "decide"
        assert result["success"] is True

    def test_null_cycle_act(self) -> None:
        """NullCognitiveCycle act should accept decision count."""
        cycle = NullCognitiveCycle()
        result: PhaseResult = cycle.act(decisions_count=2)

        assert result["phase"] == "act"
        assert result["success"] is True

    def test_null_cycle_persist(self) -> None:
        """NullCognitiveCycle persist should complete successfully."""
        cycle = NullCognitiveCycle()
        result: PhaseResult = cycle.persist()

        assert result["phase"] == "persist"
        assert result["success"] is True

    def test_null_cycle_recover(self) -> None:
        """NullCognitiveCycle recover should succeed."""
        cycle = NullCognitiveCycle()
        recovered = cycle.recover(error_phases=["perceive", "act"])
        assert recovered is True

    def test_null_cycle_orchestrate(self) -> None:
        """NullCognitiveCycle orchestrate should return context state."""
        cycle = NullCognitiveCycle()
        state = cycle.orchestrate(force=False)

        assert state is not None
        assert state["cycle_id"] == "null-cycle-0"
        assert state["cycle_name"] == "null_cycle"
        assert state["status"] == "completed"
        assert state["error_count"] == 0

    def test_null_cycle_context_state(self) -> None:
        """get_context_state should return WATERTIGHT state."""
        cycle = NullCognitiveCycle()
        state: CycleContextState = cycle.get_context_state()

        assert state["cycle_id"] == "null-cycle-0"
        assert state["phase"] == "persist"
        assert state["observations_count"] == 0
        assert state["orientations_count"] == 0
        assert state["decisions_count"] == 0
        assert state["actions_count"] == 0

    def test_null_cycle_not_running(self) -> None:
        """NullCognitiveCycle should not be running."""
        cycle = NullCognitiveCycle()
        assert cycle.is_running() is False

    def test_null_cycle_no_last_time(self) -> None:
        """NullCognitiveCycle should have no last cycle time."""
        cycle = NullCognitiveCycle()
        assert cycle.get_last_cycle_time() is None


class TestCycleRegistryProtocol:
    """Test CycleRegistryProtocol types and interfaces."""

    def test_null_registry_empty(self) -> None:
        """NullCycleRegistry should track nothing."""
        registry = NullCycleRegistry()
        assert registry.get_active_cycles() == []
        assert registry.get_completed_cycles() == []
        assert registry.get_error_cycles() == []

    def test_null_registry_stats(self) -> None:
        """NullCycleRegistry should return zero stats."""
        registry = NullCycleRegistry()
        stats: CycleRegistryStats = registry.get_stats()

        assert stats["total_cycles"] == 0
        assert stats["active_cycles"] == 0
        assert stats["completed_cycles"] == 0
        assert stats["error_cycles"] == 0
        assert stats["retention_enabled"] is True

    def test_null_registry_retention_config(self) -> None:
        """NullCycleRegistry should return default retention config."""
        registry = NullCycleRegistry()
        config: RetentionConfig = registry.get_retention_config()

        assert config["max_completed_cycles"] == 100
        assert config["max_error_cycles"] == 500
        assert config["enabled"] is True

    def test_null_registry_register_cycle(self) -> None:
        """NullCycleRegistry should accept registrations silently."""
        registry = NullCycleRegistry()
        state: CycleContextState = {
            "cycle_id": "test-123",
            "cycle_name": "test_cycle",
            "phase": "perceive",
            "status": "running",
        }
        # Should not raise
        registry.register_cycle(state)

    def test_null_registry_complete_cycle(self) -> None:
        """NullCycleRegistry should accept completions silently."""
        registry = NullCycleRegistry()
        # Should not raise
        registry.complete_cycle("test-123")

    def test_null_registry_error_cycle(self) -> None:
        """NullCycleRegistry should accept errors silently."""
        registry = NullCycleRegistry()
        # Should not raise
        registry.error_cycle("test-123", error_phases=["act"])


class TestCycleOwnedProtocol:
    """Test OwnedProtocol wrapper for cycles."""

    def test_owned_protocol_owner(self) -> None:
        """OwnedProtocol should have JANAKA as owner."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)
        assert owned.OWNER == Mahajana.JANAKA
        assert owned.owner == Mahajana.JANAKA

    def test_owned_protocol_name(self) -> None:
        """Protocol name should be 'cognitive_cycle'."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)
        assert owned.PROTOCOL_NAME == "cognitive_cycle"

    def test_owned_protocol_chant(self) -> None:
        """OwnedProtocol should be able to chant."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)

        # Initial state
        assert owned.is_chanting is False

        # Chant and verify
        owned.chant()
        assert owned.is_chanting is True

    def test_owned_protocol_state_watertight(self) -> None:
        """get_state() should return WATERTIGHT ProtocolState."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)
        state = owned.get_state()

        assert state["protocol_name"] == "cognitive_cycle"
        assert state["owner"] == "janaka"
        # No Any types allowed!

    def test_owned_protocol_gad_audit(self) -> None:
        """OwnedProtocol should pass GAD-000 audit."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)
        audit = owned.audit()

        # Basic checks should pass
        assert audit.discoverability is True  # Has name and description
        assert audit.sovereign_present is True  # Has owner

    def test_owned_protocol_cycle_access(self) -> None:
        """OwnedProtocol should provide access to underlying cycle."""
        cycle = NullCognitiveCycle()
        owned = CycleOwnedProtocol(cycle)
        assert owned.cycle is cycle


class TestWatertightTypes:
    """Test that all types are WATERTIGHT (no Any)."""

    def test_phase_result_watertight(self) -> None:
        """PhaseResult should be WATERTIGHT TypedDict."""
        result: PhaseResult = {
            "phase": "perceive",
            "success": True,
            "elements_count": 5,
            "element_types": ["str", "int"],
            "duration_ms": 100,
            "error_message": "",
        }
        assert result["phase"] == "perceive"
        assert result["success"] is True

    def test_cycle_context_state_watertight(self) -> None:
        """CycleContextState should be WATERTIGHT TypedDict."""
        state: CycleContextState = {
            "cycle_id": "test-123",
            "parent_cycle_id": "parent-456",
            "trace_id": "trace-789",
            "cycle_name": "test_cycle",
            "phase": "act",
            "status": "running",
            "observations_count": 3,
            "orientations_count": 2,
            "decisions_count": 1,
            "actions_count": 0,
            "has_result": False,
            "error_count": 0,
            "error_phases": [],
            "start_time": "2025-01-11T12:00:00",
            "elapsed_ms": 500,
        }
        assert state["cycle_id"] == "test-123"
        assert state["phase"] == "act"

    def test_retention_config_watertight(self) -> None:
        """RetentionConfig should be WATERTIGHT TypedDict."""
        config: RetentionConfig = {
            "max_completed_cycles": 200,
            "max_error_cycles": 1000,
            "max_age_seconds": 3600,
            "enabled": True,
        }
        assert config["max_completed_cycles"] == 200

    def test_cycle_registry_stats_watertight(self) -> None:
        """CycleRegistryStats should be WATERTIGHT TypedDict."""
        stats: CycleRegistryStats = {
            "total_cycles": 100,
            "active_cycles": 5,
            "completed_cycles": 90,
            "error_cycles": 5,
            "retention_enabled": True,
            "retention_max_completed": 100,
            "retention_max_errors": 500,
        }
        assert stats["total_cycles"] == 100

    def test_cycle_state_watertight(self) -> None:
        """CycleState should be WATERTIGHT TypedDict."""
        state: CycleState = {
            "protocol_name": "cognitive_cycle",
            "owner": "janaka",
            "is_chanting": True,
            "active_cycle_ids": ["cycle-1", "cycle-2"],
            "registry_stats": {
                "total_cycles": 50,
                "active_cycles": 2,
                "completed_cycles": 45,
                "error_cycles": 3,
                "retention_enabled": True,
                "retention_max_completed": 100,
                "retention_max_errors": 500,
            },
            "health": "healthy",
        }
        assert state["protocol_name"] == "cognitive_cycle"
        assert len(state["active_cycle_ids"]) == 2


class TestCycleElement:
    """Test CycleElement WATERTIGHT union type."""

    def test_cycle_element_string(self) -> None:
        """CycleElement should accept strings."""
        element: CycleElement = "observation text"
        assert element == "observation text"

    def test_cycle_element_int(self) -> None:
        """CycleElement should accept ints."""
        element: CycleElement = 42
        assert element == 42

    def test_cycle_element_float(self) -> None:
        """CycleElement should accept floats."""
        element: CycleElement = 3.14
        assert element == 3.14

    def test_cycle_element_bool(self) -> None:
        """CycleElement should accept bools."""
        element: CycleElement = True
        assert element is True

    def test_cycle_element_dict(self) -> None:
        """CycleElement should accept Dict[str, str]."""
        element: CycleElement = {"key": "value"}
        assert element["key"] == "value"

    def test_cycle_element_list(self) -> None:
        """CycleElement should accept List[str]."""
        element: CycleElement = ["a", "b", "c"]
        assert len(element) == 3

    def test_cycle_element_none(self) -> None:
        """CycleElement should accept None."""
        element: CycleElement = None
        assert element is None
