"""
TESTS: nadi.py - Universal Cognitive Connection Protocol
=========================================================

"prāṇasya nāḍī saṁcāraḥ" - "Prana flows through the Nadis."

REAL TESTS for:
1. SSOT-derived constants (NADI_CAPACITY, NADI_BUFFER_SIZE, etc.)
2. NadiType enum (5 Pancha Prana types)
3. NadiOp enum (9 Navadha operations)
4. NadiMessage dataclass
5. NadiConnection dataclass
6. LocalNadi implementation
7. NullNadi fallback
8. GAD-000 compliance
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from vibe_core.mahamantra.substrate.nadi import (
    # Constants
    NADI_CAPACITY,
    NADI_BUFFER_SIZE,
    NADI_HEARTBEAT_MS,
    NADI_TIMEOUT_MS,
    NADI_DAILY_CYCLES,
    NADI_MALA_CYCLE,
    # Enums
    NadiType,
    NADI_TYPE_NAMES,
    NadiOp,
    NADI_OP_TO_BHAKTI,
    NadiPriority,
    # Data structures
    NadiMessage,
    NadiConnection,
    NadiStats,
    # Protocol
    NadiProtocol,
    # Implementations
    NullNadi,
    LocalNadi,
    # Factory
    get_nadi,
)

# Import seed constants for SSOT verification
from vibe_core.mahamantra.substrate.seed import (
    NADI_RESONANCE,
    NAVA,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    SHARANAGATI,
    NavaBhakti,
    MALA,
    COSMIC_FRAME,
)


# =============================================================================
# TEST: SSOT-DERIVED CONSTANTS
# =============================================================================

class TestNadiConstants:
    """Test that all constants are correctly derived from seed.py."""

    def test_nadi_capacity_equals_nadi_resonance(self):
        """NADI_CAPACITY must equal NADI_RESONANCE (72)."""
        assert NADI_CAPACITY == NADI_RESONANCE == 72

    def test_nadi_buffer_size_is_double_capacity(self):
        """NADI_BUFFER_SIZE = NADI_RESONANCE × 2 = 144."""
        assert NADI_BUFFER_SIZE == NADI_RESONANCE * 2 == 144

    def test_nadi_heartbeat_is_one_second(self):
        """NADI_HEARTBEAT_MS = TICK_INTERVAL_MS × NADI_RESONANCE / 18 = 1000ms."""
        expected = (TICK_INTERVAL_MS * NADI_RESONANCE) // 18
        assert NADI_HEARTBEAT_MS == expected == 1000

    def test_nadi_timeout_is_24_seconds(self):
        """NADI_TIMEOUT_MS = PRANA_DURATION_MS × SHARANAGATI = 24000ms."""
        expected = PRANA_DURATION_MS * SHARANAGATI
        assert NADI_TIMEOUT_MS == expected == 24000

    def test_nadi_daily_cycles_is_300(self):
        """NADI_DAILY_CYCLES = COSMIC_FRAME / NADI_RESONANCE = 300."""
        expected = COSMIC_FRAME // NADI_RESONANCE
        assert NADI_DAILY_CYCLES == expected == 300

    def test_nadi_mala_cycle_is_108(self):
        """NADI_MALA_CYCLE = MALA = 108."""
        assert NADI_MALA_CYCLE == MALA == 108


# =============================================================================
# TEST: NADI TYPES (PANCHA PRANA)
# =============================================================================

class TestNadiType:
    """Test the 5 Nadi types (Pancha Prana)."""

    def test_pancha_nadi_types(self):
        """Must have exactly 5 types (Pancha)."""
        assert len(NadiType) == 5

    def test_prana_is_user_system(self):
        """PRANA (index 0) = User ↔ System."""
        assert NadiType.PRANA.value == 0
        assert NADI_TYPE_NAMES[0] == "prana"

    def test_apana_is_agent_agent(self):
        """APANA (index 1) = Agent ↔ Agent."""
        assert NadiType.APANA.value == 1
        assert NADI_TYPE_NAMES[1] == "apana"

    def test_vyana_is_service_service(self):
        """VYANA (index 2) = Service ↔ Service."""
        assert NadiType.VYANA.value == 2
        assert NADI_TYPE_NAMES[2] == "vyana"

    def test_udana_is_agent_mahajana(self):
        """UDANA (index 3) = Agent ↔ Mahajana."""
        assert NadiType.UDANA.value == 3
        assert NADI_TYPE_NAMES[3] == "udana"

    def test_samana_is_kernel_shadow(self):
        """SAMANA (index 4) = Kernel ↔ Shadow."""
        assert NadiType.SAMANA.value == 4
        assert NADI_TYPE_NAMES[4] == "samana"


# =============================================================================
# TEST: NADI OPERATIONS (NAVADHA BHAKTI)
# =============================================================================

class TestNadiOp:
    """Test the 9 Nadi operations (Navadha Bhakti)."""

    def test_navadha_nadi_operations(self):
        """Must have exactly 9 operations (Nava)."""
        assert len(NadiOp) == NAVA == 9

    def test_op_to_bhakti_mapping_complete(self):
        """Every NadiOp must map to a NavaBhakti."""
        for op in NadiOp:
            assert op in NADI_OP_TO_BHAKTI
            assert isinstance(NADI_OP_TO_BHAKTI[op], NavaBhakti)

    def test_receive_maps_to_sravanam(self):
        """RECEIVE → SRAVANAM (hearing)."""
        assert NADI_OP_TO_BHAKTI[NadiOp.RECEIVE] == NavaBhakti.SRAVANAM

    def test_send_maps_to_kirtanam(self):
        """SEND → KIRTANAM (chanting)."""
        assert NADI_OP_TO_BHAKTI[NadiOp.SEND] == NavaBhakti.KIRTANAM

    def test_connect_maps_to_sakhyam(self):
        """CONNECT → SAKHYAM (friendship)."""
        assert NADI_OP_TO_BHAKTI[NadiOp.CONNECT] == NavaBhakti.SAKHYAM

    def test_commit_maps_to_atma_nivedanam(self):
        """COMMIT → ATMA_NIVEDANAM (surrender)."""
        assert NADI_OP_TO_BHAKTI[NadiOp.COMMIT] == NavaBhakti.ATMA_NIVEDANAM


# =============================================================================
# TEST: NADI PRIORITY (GUNA-BASED)
# =============================================================================

class TestNadiPriority:
    """Test priority levels based on Gunas."""

    def test_four_priority_levels(self):
        """Must have 4 priority levels."""
        assert len(NadiPriority) == 4

    def test_tamas_is_lowest(self):
        """TAMAS (0) = Background/lowest."""
        assert NadiPriority.TAMAS.value == 0

    def test_suddha_is_highest(self):
        """SUDDHA (3) = Critical/highest."""
        assert NadiPriority.SUDDHA.value == 3

    def test_priority_ordering(self):
        """Priorities must be ordered: TAMAS < RAJAS < SATTVA < SUDDHA."""
        assert NadiPriority.TAMAS < NadiPriority.RAJAS
        assert NadiPriority.RAJAS < NadiPriority.SATTVA
        assert NadiPriority.SATTVA < NadiPriority.SUDDHA


# =============================================================================
# TEST: NADI MESSAGE
# =============================================================================

class TestNadiMessage:
    """Test NadiMessage dataclass."""

    def test_message_creation(self):
        """Can create a NadiMessage with all fields."""
        msg = NadiMessage(
            source="sender",
            target="receiver",
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
            payload={"key": "value"},
        )
        assert msg.source == "sender"
        assert msg.target == "receiver"
        assert msg.nadi_type == NadiType.PRANA
        assert msg.operation == NadiOp.SEND

    def test_broadcast_detection(self):
        """is_broadcast returns True when target is '*'."""
        msg = NadiMessage(
            source="sender",
            target="*",
            nadi_type=NadiType.APANA,
            operation=NadiOp.SEND,
        )
        assert msg.is_broadcast is True

        msg2 = NadiMessage(
            source="sender",
            target="specific",
            nadi_type=NadiType.APANA,
            operation=NadiOp.SEND,
        )
        assert msg2.is_broadcast is False

    def test_expiry_detection(self):
        """is_expired returns True when TTL exceeded."""
        # Not expired (TTL 0 = never expires)
        msg = NadiMessage(
            source="s",
            target="t",
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
            ttl_ms=0,
        )
        assert msg.is_expired is False

        # Create expired message
        old_time = datetime.now() - timedelta(seconds=30)
        msg_old = NadiMessage(
            source="s",
            target="t",
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
            ttl_ms=1000,  # 1 second TTL
            timestamp=old_time,
        )
        assert msg_old.is_expired is True

    def test_bhakti_property(self):
        """bhakti property returns corresponding NavaBhakti."""
        msg = NadiMessage(
            source="s",
            target="t",
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
        )
        assert msg.bhakti == NavaBhakti.KIRTANAM


# =============================================================================
# TEST: NADI CONNECTION
# =============================================================================

class TestNadiConnection:
    """Test NadiConnection dataclass."""

    def test_connection_creation(self):
        """Can create a NadiConnection."""
        conn = NadiConnection(
            connection_id="conn_001",
            source="endpoint_a",
            target="endpoint_b",
            nadi_type=NadiType.SAMANA,
        )
        assert conn.connection_id == "conn_001"
        assert conn.is_active is True

    def test_age_calculation(self):
        """age_ms returns time since establishment."""
        conn = NadiConnection(
            connection_id="conn_001",
            source="a",
            target="b",
            nadi_type=NadiType.PRANA,
        )
        # Age should be very small (just created)
        assert conn.age_ms >= 0
        assert conn.age_ms < 1000  # Less than 1 second

    def test_stale_detection(self):
        """is_stale returns True when idle > timeout."""
        old_time = datetime.now() - timedelta(seconds=30)
        conn = NadiConnection(
            connection_id="conn_001",
            source="a",
            target="b",
            nadi_type=NadiType.PRANA,
            last_activity=old_time,
        )
        assert conn.is_stale is True


# =============================================================================
# TEST: NULL NADI (ARJUNA PATTERN)
# =============================================================================

class TestNullNadi:
    """Test NullNadi fallback implementation."""

    def test_null_nadi_creation(self):
        """Can create NullNadi."""
        nadi = NullNadi("null_endpoint", NadiType.PRANA)
        assert nadi.endpoint_id == "null_endpoint"
        assert nadi.nadi_type == NadiType.PRANA

    def test_null_nadi_connect_fails(self):
        """NullNadi.connect() always returns False."""
        nadi = NullNadi()
        assert nadi.connect("any_target") is False

    def test_null_nadi_send_fails(self):
        """NullNadi.send() always returns False."""
        nadi = NullNadi()
        msg = NadiMessage(
            source="s", target="t",
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
        )
        assert nadi.send(msg) is False

    def test_null_nadi_receive_returns_none(self):
        """NullNadi.receive() always returns None."""
        nadi = NullNadi()
        assert nadi.receive() is None

    def test_null_nadi_pulse_succeeds(self):
        """NullNadi.pulse() always returns True (always healthy)."""
        nadi = NullNadi()
        assert nadi.pulse() is True

    def test_null_nadi_stats_empty(self):
        """NullNadi.get_stats() returns empty stats."""
        nadi = NullNadi("null_ep")
        stats = nadi.get_stats()
        assert stats.endpoint_id == "null_ep"
        assert stats.connections == 0
        assert stats.messages_sent == 0


# =============================================================================
# TEST: LOCAL NADI IMPLEMENTATION
# =============================================================================

class TestLocalNadi:
    """Test LocalNadi implementation."""

    @pytest.fixture
    def unique_id(self):
        """Generate unique ID for test isolation."""
        return uuid4().hex[:8]

    def test_local_nadi_creation(self, unique_id):
        """Can create LocalNadi."""
        nadi = LocalNadi(f"endpoint_{unique_id}", NadiType.PRANA)
        assert nadi.endpoint_id == f"endpoint_{unique_id}"
        assert nadi.nadi_type == NadiType.PRANA

    def test_connect_to_existing_endpoint(self, unique_id):
        """Can connect to existing endpoint."""
        nadi_a = LocalNadi(f"a_{unique_id}", NadiType.APANA)
        nadi_b = LocalNadi(f"b_{unique_id}", NadiType.APANA)

        assert nadi_a.connect(f"b_{unique_id}") is True
        assert nadi_a.is_connected(f"b_{unique_id}") is True

    def test_connect_to_nonexistent_fails(self, unique_id):
        """Cannot connect to nonexistent endpoint."""
        nadi = LocalNadi(f"a_{unique_id}", NadiType.APANA)
        assert nadi.connect("nonexistent") is False

    def test_cannot_connect_to_self(self, unique_id):
        """Cannot connect to self."""
        nadi = LocalNadi(f"self_{unique_id}", NadiType.APANA)
        assert nadi.connect(f"self_{unique_id}") is False

    def test_send_receive_flow(self, unique_id):
        """Can send and receive messages."""
        nadi_a = LocalNadi(f"sender_{unique_id}", NadiType.SAMANA)
        nadi_b = LocalNadi(f"receiver_{unique_id}", NadiType.SAMANA)

        # Connect
        nadi_a.connect(f"receiver_{unique_id}")

        # Send
        msg = NadiMessage(
            source=f"sender_{unique_id}",
            target=f"receiver_{unique_id}",
            nadi_type=NadiType.SAMANA,
            operation=NadiOp.DELEGATE,
            payload={"task": "test"},
        )
        assert nadi_a.send(msg) is True

        # Receive
        received = nadi_b.receive()
        assert received is not None
        assert received.payload["task"] == "test"

    def test_broadcast(self, unique_id):
        """Can broadcast to all connected endpoints."""
        hub = LocalNadi(f"hub_{unique_id}", NadiType.VYANA)
        spoke1 = LocalNadi(f"spoke1_{unique_id}", NadiType.VYANA)
        spoke2 = LocalNadi(f"spoke2_{unique_id}", NadiType.VYANA)

        # Hub connects to spokes
        hub.connect(f"spoke1_{unique_id}")
        hub.connect(f"spoke2_{unique_id}")

        # Broadcast
        count = hub.broadcast(NadiOp.SEND, {"msg": "hello all"})
        assert count == 2

        # Both receive
        msg1 = spoke1.receive()
        msg2 = spoke2.receive()
        assert msg1 is not None
        assert msg2 is not None

    def test_disconnect(self, unique_id):
        """Can disconnect from endpoint."""
        nadi_a = LocalNadi(f"a_{unique_id}", NadiType.APANA)
        nadi_b = LocalNadi(f"b_{unique_id}", NadiType.APANA)

        nadi_a.connect(f"b_{unique_id}")
        assert nadi_a.is_connected(f"b_{unique_id}") is True

        nadi_a.disconnect(f"b_{unique_id}")
        assert nadi_a.is_connected(f"b_{unique_id}") is False

    def test_get_connections(self, unique_id):
        """Can get list of connections."""
        nadi = LocalNadi(f"hub_{unique_id}", NadiType.PRANA)
        LocalNadi(f"c1_{unique_id}", NadiType.PRANA)
        LocalNadi(f"c2_{unique_id}", NadiType.PRANA)

        nadi.connect(f"c1_{unique_id}")
        nadi.connect(f"c2_{unique_id}")

        conns = nadi.get_connections()
        assert len(conns) == 2

    def test_stats(self, unique_id):
        """Can get endpoint statistics."""
        nadi = LocalNadi(f"stats_{unique_id}", NadiType.PRANA)
        stats = nadi.get_stats()

        assert stats.endpoint_id == f"stats_{unique_id}"
        assert stats.nadi_type == NadiType.PRANA
        assert stats.connections == 0

    def test_capacity_limit(self, unique_id):
        """Cannot exceed NADI_CAPACITY connections."""
        hub = LocalNadi(f"hub_{unique_id}", NadiType.PRANA)

        # Create many endpoints
        for i in range(NADI_CAPACITY + 5):
            LocalNadi(f"ep{i}_{unique_id}", NadiType.PRANA)

        # Connect up to capacity
        connected = 0
        for i in range(NADI_CAPACITY + 5):
            if hub.connect(f"ep{i}_{unique_id}"):
                connected += 1

        assert connected == NADI_CAPACITY  # Should stop at 72


# =============================================================================
# TEST: GAD-000 COMPLIANCE
# =============================================================================

class TestLocalNadiGAD:
    """Test GAD-000 compliance of LocalNadi."""

    @pytest.fixture
    def nadi(self):
        """Create a fresh LocalNadi for testing."""
        return LocalNadi(f"gad_{uuid4().hex[:8]}", NadiType.SAMANA)

    def test_gad_discover(self, nadi):
        """GAD Discoverability: discover() returns capability info."""
        discovery = nadi.discover()

        assert "service" in discovery
        assert discovery["service"] == "local_nadi"
        assert "mahajana" in discovery
        assert "capabilities" in discovery
        assert len(discovery["capabilities"]) == 9  # 9 NadiOps

    def test_gad_get_state(self, nadi):
        """GAD Observability: get_state() returns current state."""
        state = nadi.get_state()

        assert "endpoint_id" in state
        assert "nadi_type" in state
        assert "connections" in state
        assert "pending_messages" in state

    def test_gad_detect_drift(self, nadi):
        """GAD Drift Detection: detect_drift() returns issues."""
        issues = nadi.detect_drift()
        assert isinstance(issues, list)

    def test_gad_audit_full_score(self, nadi):
        """GAD Audit: Must achieve 6/6 criteria, 4/4 dharma."""
        audit = nadi.audit()

        assert audit.criteria_score == 6, "Must have 6/6 GAD criteria"
        assert audit.dharma_score == 4, "Must have 4/4 Dharma principles"

    def test_gad_heartbeat(self, nadi):
        """GAD Heartbeat: chant() and is_healthy() work."""
        assert nadi.chant() is True
        assert nadi.is_healthy() is True


# =============================================================================
# TEST: FACTORY FUNCTION
# =============================================================================

class TestGetNadi:
    """Test get_nadi() factory function."""

    def test_get_nadi_returns_local_nadi(self):
        """get_nadi() returns LocalNadi by default."""
        nadi = get_nadi(f"factory_{uuid4().hex[:8]}", NadiType.PRANA)
        assert isinstance(nadi, LocalNadi)

    def test_get_nadi_fallback_to_null(self):
        """get_nadi() falls back to NullNadi on error."""
        # This should not raise, even with edge cases
        nadi = get_nadi("test", NadiType.APANA, fallback_to_null=True)
        assert nadi is not None


# =============================================================================
# TEST: NADI STATS DERIVED METRICS
# =============================================================================

class TestNadiStatsDerivedMetrics:
    """Test derived metrics in NadiStats."""

    def test_resonance_ratio_empty(self):
        """resonance_ratio is 0 when no connections."""
        stats = NadiStats(
            endpoint_id="test",
            nadi_type=NadiType.PRANA,
            connections=0,
        )
        assert stats.resonance_ratio == 0.0

    def test_resonance_ratio_full(self):
        """resonance_ratio is 1.0 at NADI_CAPACITY."""
        stats = NadiStats(
            endpoint_id="test",
            nadi_type=NadiType.PRANA,
            connections=NADI_CAPACITY,
        )
        assert stats.resonance_ratio == 1.0

    def test_mala_progress(self):
        """mala_progress cycles through 0-1 every 108 messages."""
        stats = NadiStats(
            endpoint_id="test",
            nadi_type=NadiType.PRANA,
            messages_sent=54,
            messages_received=0,
        )
        assert stats.mala_progress == 0.5  # 54/108
