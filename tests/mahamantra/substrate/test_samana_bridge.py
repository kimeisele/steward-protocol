"""
TESTS: samana_bridge.py - TaskKernel ↔ ShadowReactor Integration
=================================================================

"samānas tu samānāt prāṇāt sarvāṇi prāṇāni samīkarotīti"
"Samana balances all the pranas equally."

REAL TESTS for:
1. SSOT-derived constants (MAX_KERNELS, BATCH_SIZE, etc.)
2. SamanaDispatch dataclass
3. SamanaFold dataclass
4. SamanaBridge implementation
5. Dispatch/Fold lifecycle
6. GAD-000 compliance
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from vibe_core.mahamantra.substrate.samana_bridge import (
    # Constants
    MAX_KERNELS_PER_REACTOR,
    DISPATCH_BATCH_SIZE,
    FOLD_TIMEOUT_MS,
    SAMANA_HEARTBEAT_MS,
    # Message types
    SamanaMessageType,
    # Data structures
    SamanaDispatch,
    SamanaFold,
    # Bridge
    SamanaBridge,
    # Factory
    create_samana_bridge,
)

from vibe_core.mahamantra.substrate.nadi import NadiType, NadiPriority

# Import seed constants for SSOT verification
from vibe_core.mahamantra.substrate.seed import (
    SHARANAGATI,
    WORDS,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    NADI_RESONANCE,
)


# =============================================================================
# TEST: SSOT-DERIVED CONSTANTS
# =============================================================================

class TestSamanaConstants:
    """Test that all constants are correctly derived from seed.py."""

    def test_max_kernels_equals_sharanagati(self):
        """MAX_KERNELS_PER_REACTOR must equal SHARANAGATI (6)."""
        assert MAX_KERNELS_PER_REACTOR == SHARANAGATI == 6

    def test_dispatch_batch_size_is_half_words(self):
        """DISPATCH_BATCH_SIZE = WORDS / 2 = 8 (Bhoga phase capacity)."""
        assert DISPATCH_BATCH_SIZE == WORDS // 2 == 8

    def test_fold_timeout_is_two_breaths(self):
        """FOLD_TIMEOUT_MS = PRANA_DURATION_MS × 2 = 8000ms."""
        expected = PRANA_DURATION_MS * 2
        assert FOLD_TIMEOUT_MS == expected == 8000

    def test_samana_heartbeat_is_two_seconds(self):
        """SAMANA_HEARTBEAT_MS = TICK_INTERVAL_MS × NADI_RESONANCE / 9 = 2000ms."""
        expected = (TICK_INTERVAL_MS * NADI_RESONANCE) // 9
        assert SAMANA_HEARTBEAT_MS == expected == 2000


# =============================================================================
# TEST: SAMANA MESSAGE TYPES
# =============================================================================

class TestSamanaMessageType:
    """Test message type constants."""

    def test_dispatch_type(self):
        """DISPATCH type exists."""
        assert SamanaMessageType.DISPATCH == "dispatch"

    def test_fold_type(self):
        """FOLD type exists."""
        assert SamanaMessageType.FOLD == "fold"

    def test_spawn_type(self):
        """SPAWN type exists."""
        assert SamanaMessageType.SPAWN == "spawn"

    def test_heartbeat_type(self):
        """HEARTBEAT type exists."""
        assert SamanaMessageType.HEARTBEAT == "heartbeat"


# =============================================================================
# TEST: SAMANA DISPATCH
# =============================================================================

class TestSamanaDispatch:
    """Test SamanaDispatch dataclass."""

    def test_dispatch_creation(self):
        """Can create a SamanaDispatch."""
        dispatch = SamanaDispatch(
            dispatch_id="dispatch_001",
            task_id="task_001",
            task_description="Test task",
            position=0,
            phase="bhoga",
        )
        assert dispatch.dispatch_id == "dispatch_001"
        assert dispatch.task_id == "task_001"
        assert dispatch.position == 0
        assert dispatch.phase == "bhoga"

    def test_dispatch_defaults(self):
        """SamanaDispatch has correct defaults."""
        dispatch = SamanaDispatch(
            dispatch_id="d",
            task_id="t",
            task_description="desc",
            position=0,
            phase="bhoga",
        )
        assert dispatch.priority == NadiPriority.RAJAS
        assert dispatch.timeout_ms == FOLD_TIMEOUT_MS
        assert dispatch.payload == {}

    def test_dispatch_to_nadi_payload(self):
        """Can convert dispatch to Nadi payload."""
        dispatch = SamanaDispatch(
            dispatch_id="dispatch_001",
            task_id="task_001",
            task_description="Test",
            position=5,
            phase="bhoga",
            payload={"key": "value"},
        )
        payload = dispatch.to_nadi_payload()

        assert payload["type"] == SamanaMessageType.DISPATCH
        assert payload["dispatch_id"] == "dispatch_001"
        assert payload["task_id"] == "task_001"
        assert payload["position"] == 5
        assert payload["phase"] == "bhoga"
        assert payload["payload"]["key"] == "value"

    def test_dispatch_from_nadi_payload(self):
        """Can create dispatch from Nadi payload."""
        payload = {
            "dispatch_id": "dispatch_002",
            "task_id": "task_002",
            "task_description": "From payload",
            "position": 8,
            "phase": "prasadam",
            "timeout_ms": 5000,
            "payload": {"data": 123},
            "timestamp": datetime.now().isoformat(),
        }
        dispatch = SamanaDispatch.from_nadi_payload(payload)

        assert dispatch.dispatch_id == "dispatch_002"
        assert dispatch.task_id == "task_002"
        assert dispatch.position == 8
        assert dispatch.phase == "prasadam"
        assert dispatch.payload["data"] == 123


# =============================================================================
# TEST: SAMANA FOLD
# =============================================================================

class TestSamanaFold:
    """Test SamanaFold dataclass."""

    def test_fold_creation(self):
        """Can create a SamanaFold."""
        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id="dispatch_001",
            kernel_id="kernel_001",
            status="completed",
            output="Result",
            reinforcement_signal=1.0,
        )
        assert fold.fold_id == "fold_001"
        assert fold.dispatch_id == "dispatch_001"
        assert fold.status == "completed"
        assert fold.reinforcement_signal == 1.0

    def test_fold_defaults(self):
        """SamanaFold has correct defaults."""
        fold = SamanaFold(
            fold_id="f",
            dispatch_id="d",
            kernel_id="k",
            status="completed",
        )
        assert fold.output is None
        assert fold.error is None
        assert fold.duration_ms == 0.0
        assert fold.reinforcement_signal == 0.0

    def test_fold_to_nadi_payload(self):
        """Can convert fold to Nadi payload."""
        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id="dispatch_001",
            kernel_id="kernel_001",
            status="completed",
            output="Success",
            duration_ms=150.0,
            reinforcement_signal=1.0,
        )
        payload = fold.to_nadi_payload()

        assert payload["type"] == SamanaMessageType.FOLD
        assert payload["fold_id"] == "fold_001"
        assert payload["dispatch_id"] == "dispatch_001"
        assert payload["status"] == "completed"
        assert payload["reinforcement_signal"] == 1.0

    def test_fold_from_nadi_payload(self):
        """Can create fold from Nadi payload."""
        payload = {
            "fold_id": "fold_002",
            "dispatch_id": "dispatch_002",
            "kernel_id": "kernel_002",
            "status": "failed",
            "error": "Something went wrong",
            "duration_ms": 500.0,
            "reinforcement_signal": -0.5,
            "timestamp": datetime.now().isoformat(),
        }
        fold = SamanaFold.from_nadi_payload(payload)

        assert fold.fold_id == "fold_002"
        assert fold.status == "failed"
        assert fold.error == "Something went wrong"
        assert fold.reinforcement_signal == -0.5


# =============================================================================
# TEST: SAMANA BRIDGE
# =============================================================================

class TestSamanaBridge:
    """Test SamanaBridge implementation."""

    @pytest.fixture
    def unique_id(self):
        """Generate unique ID for test isolation."""
        return uuid4().hex[:8]

    @pytest.fixture
    def bridge(self, unique_id):
        """Create a fresh SamanaBridge."""
        return SamanaBridge(f"reactor_{unique_id}")

    def test_bridge_creation(self, unique_id):
        """Can create a SamanaBridge."""
        bridge = SamanaBridge(f"reactor_{unique_id}")
        assert bridge.reactor_id == f"reactor_{unique_id}"
        assert bridge.active_kernel_count == 0
        assert bridge.can_dispatch is True

    def test_bridge_max_kernels_limit(self, unique_id):
        """Bridge respects MAX_KERNELS_PER_REACTOR."""
        bridge = SamanaBridge(f"reactor_{unique_id}", max_kernels=10)
        # Should be capped at MAX_KERNELS_PER_REACTOR
        assert bridge._max_kernels == MAX_KERNELS_PER_REACTOR

    def test_dispatch_returns_id(self, bridge):
        """dispatch() returns a dispatch_id."""
        dispatch_id = bridge.dispatch(
            task_id="task_001",
            task_description="Test task",
            position=0,
            phase="bhoga",
        )
        assert dispatch_id is not None
        assert dispatch_id.startswith("dispatch_")

    def test_dispatch_increments_pending(self, bridge):
        """dispatch() increments pending count."""
        assert bridge.pending_dispatch_count == 0

        bridge.dispatch(
            task_id="task_001",
            task_description="Test",
            position=0,
            phase="bhoga",
        )

        assert bridge.pending_dispatch_count == 1

    def test_dispatch_with_payload(self, bridge):
        """dispatch() accepts payload."""
        dispatch_id = bridge.dispatch(
            task_id="task_001",
            task_description="Test",
            position=0,
            phase="bhoga",
            payload={"custom": "data"},
        )

        # Retrieve the dispatch
        dispatch = bridge._pending_dispatches[dispatch_id]
        assert dispatch.payload["custom"] == "data"

    def test_fold_removes_pending(self, bridge):
        """fold() removes dispatch from pending."""
        dispatch_id = bridge.dispatch(
            task_id="task_001",
            task_description="Test",
            position=0,
            phase="bhoga",
        )
        assert bridge.pending_dispatch_count == 1

        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id=dispatch_id,
            kernel_id="kernel_001",
            status="completed",
        )
        result = bridge.fold(fold)

        assert result is True
        assert bridge.pending_dispatch_count == 0

    def test_fold_invalid_dispatch_fails(self, bridge):
        """fold() fails for unknown dispatch_id."""
        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id="unknown_dispatch",
            kernel_id="kernel_001",
            status="completed",
        )
        result = bridge.fold(fold)
        assert result is False

    def test_fold_callback(self, bridge):
        """Fold triggers on_fold callback."""
        callback_called = []

        def on_fold(fold: SamanaFold):
            callback_called.append(fold)

        bridge.set_on_fold(on_fold)

        dispatch_id = bridge.dispatch(
            task_id="task_001",
            task_description="Test",
            position=0,
            phase="bhoga",
        )

        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id=dispatch_id,
            kernel_id="kernel_001",
            status="completed",
        )
        bridge.fold(fold)

        assert len(callback_called) == 1
        assert callback_called[0].fold_id == "fold_001"

    def test_get_fold_by_dispatch_id(self, bridge):
        """Can retrieve completed fold by dispatch_id."""
        dispatch_id = bridge.dispatch(
            task_id="task_001",
            task_description="Test",
            position=0,
            phase="bhoga",
        )

        fold = SamanaFold(
            fold_id="fold_001",
            dispatch_id=dispatch_id,
            kernel_id="kernel_001",
            status="completed",
            output="Result",
        )
        bridge.fold(fold)

        retrieved = bridge.get_fold(dispatch_id)
        assert retrieved is not None
        assert retrieved.output == "Result"

    def test_dispatch_batch(self, bridge):
        """Can dispatch a batch of tasks."""
        tasks = [
            ("task_1", "First task", {"n": 1}),
            ("task_2", "Second task", {"n": 2}),
            ("task_3", "Third task", {"n": 3}),
        ]

        dispatch_ids = bridge.dispatch_batch(
            tasks=tasks,
            position=0,
            phase="bhoga",
        )

        assert len(dispatch_ids) == 3
        assert bridge.pending_dispatch_count == 3


# =============================================================================
# TEST: SAMANA BRIDGE GAD COMPLIANCE
# =============================================================================

class TestSamanaBridgeGAD:
    """Test GAD-000 compliance of SamanaBridge."""

    @pytest.fixture
    def bridge(self):
        """Create a fresh SamanaBridge."""
        return SamanaBridge(f"reactor_{uuid4().hex[:8]}")

    def test_gad_discover(self, bridge):
        """GAD Discoverability: discover() returns capability info."""
        discovery = bridge.discover()

        assert discovery["service"] == "samana_bridge"
        assert discovery["mahajana"] == "parashurama"
        assert discovery["position"] == 8
        assert discovery["nadi_type"] == "SAMANA"
        assert "dispatch" in discovery["capabilities"]
        assert "fold" in discovery["capabilities"]

    def test_gad_get_state(self, bridge):
        """GAD Observability: get_state() returns current state."""
        state = bridge.get_state()

        assert "reactor_id" in state
        assert "active_kernels" in state
        assert "pending_dispatches" in state
        assert "can_dispatch" in state

    def test_gad_detect_drift(self, bridge):
        """GAD Drift Detection: detect_drift() returns issues."""
        issues = bridge.detect_drift()
        assert isinstance(issues, list)

    def test_gad_detect_drift_stale_dispatch(self, bridge):
        """detect_drift() catches stale dispatches."""
        # Create a dispatch with old timestamp
        old_time = datetime.now() - timedelta(seconds=30)
        dispatch = SamanaDispatch(
            dispatch_id="old_dispatch",
            task_id="task",
            task_description="Old task",
            position=0,
            phase="bhoga",
            timestamp=old_time,
        )
        bridge._pending_dispatches["old_dispatch"] = dispatch

        issues = bridge.detect_drift()
        assert len(issues) > 0
        assert "Stale dispatch" in issues[0]

    def test_gad_audit_full_score(self, bridge):
        """GAD Audit: Must achieve 6/6 criteria, 4/4 dharma."""
        audit = bridge.audit()

        assert audit.criteria_score == 6, "Must have 6/6 GAD criteria"
        assert audit.dharma_score == 4, "Must have 4/4 Dharma principles"

    def test_gad_test_saucam(self, bridge):
        """test_saucam() validates Nadi type."""
        assert bridge.test_saucam() is True


# =============================================================================
# TEST: SAMANA BRIDGE PULSE (HEARTBEAT)
# =============================================================================

class TestSamanaBridgePulse:
    """Test pulse/heartbeat functionality."""

    @pytest.fixture
    def bridge(self):
        """Create a fresh SamanaBridge."""
        return SamanaBridge(f"reactor_{uuid4().hex[:8]}")

    def test_pulse_returns_true_when_healthy(self, bridge):
        """pulse() returns True when no stale dispatches."""
        assert bridge.pulse() is True

    def test_pulse_prunes_stale_dispatches(self, bridge):
        """pulse() prunes dispatches older than 2x timeout."""
        # Create a very old dispatch
        very_old_time = datetime.now() - timedelta(seconds=60)
        dispatch = SamanaDispatch(
            dispatch_id="stale_dispatch",
            task_id="task",
            task_description="Stale",
            position=0,
            phase="bhoga",
            timestamp=very_old_time,
        )
        bridge._pending_dispatches["stale_dispatch"] = dispatch
        assert bridge.pending_dispatch_count == 1

        # Pulse should prune it
        bridge.pulse()

        # Should be removed and replaced with timeout fold
        assert bridge.pending_dispatch_count == 0
        assert bridge.get_fold("stale_dispatch") is not None
        assert bridge.get_fold("stale_dispatch").status == "timeout"


# =============================================================================
# TEST: FACTORY FUNCTION
# =============================================================================

class TestCreateSamanaBridge:
    """Test create_samana_bridge() factory function."""

    def test_factory_creates_bridge(self):
        """create_samana_bridge() returns SamanaBridge."""
        bridge = create_samana_bridge(f"reactor_{uuid4().hex[:8]}")
        assert isinstance(bridge, SamanaBridge)

    def test_factory_respects_max_kernels(self):
        """Factory respects max_kernels parameter."""
        bridge = create_samana_bridge("reactor", max_kernels=3)
        assert bridge._max_kernels == 3

    def test_factory_caps_max_kernels(self):
        """Factory caps max_kernels at MAX_KERNELS_PER_REACTOR."""
        bridge = create_samana_bridge("reactor", max_kernels=100)
        assert bridge._max_kernels == MAX_KERNELS_PER_REACTOR


# =============================================================================
# TEST: BRIDGE STATS
# =============================================================================

class TestSamanaBridgeStats:
    """Test bridge statistics."""

    @pytest.fixture
    def bridge(self):
        """Create a fresh SamanaBridge."""
        return SamanaBridge(f"reactor_{uuid4().hex[:8]}")

    def test_stats_initial(self, bridge):
        """Initial stats are zeroed."""
        stats = bridge.get_stats()

        assert stats["active_kernels"] == 0
        assert stats["pending_dispatches"] == 0
        assert stats["dispatches_sent"] == 0
        assert stats["folds_received"] == 0

    def test_stats_after_dispatch(self, bridge):
        """Stats update after dispatch."""
        bridge.dispatch(
            task_id="task",
            task_description="Test",
            position=0,
            phase="bhoga",
        )

        stats = bridge.get_stats()
        assert stats["dispatches_sent"] == 1
        assert stats["pending_dispatches"] == 1

    def test_stats_after_fold(self, bridge):
        """Stats update after fold."""
        dispatch_id = bridge.dispatch(
            task_id="task",
            task_description="Test",
            position=0,
            phase="bhoga",
        )

        fold = SamanaFold(
            fold_id="fold",
            dispatch_id=dispatch_id,
            kernel_id="kernel",
            status="completed",
        )
        bridge.fold(fold)

        stats = bridge.get_stats()
        assert stats["folds_received"] == 1
        assert stats["pending_dispatches"] == 0
        assert stats["completed_folds"] == 1
