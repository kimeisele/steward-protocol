"""
TESTS: Federation Nadi Consumer (steward-protocol side)
========================================================

Tests for:
1. FederationMessage serialization/deserialization (roundtrip)
2. TTL expiry detection
3. receive() with dedup and priority sorting
4. emit() and send_message()
5. Cross-repo compatibility (agent-city format)
6. Directory structure and atomic writes
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from vibe_core.mahamantra.federation import (
    CityReport,
    FederationDirective,
    FederationMessage,
    FederationNadi,
    FederationPriority,
)
from vibe_core.mahamantra.federation.types import (
    RAJAS,
    SATTVA,
    SUDDHA,
    TAMAS,
)

# =============================================================================
# TEST: FEDERATION MESSAGE SERIALIZATION
# =============================================================================


class TestFederationMessageSerialization:
    """Test FederationMessage serialization/deserialization."""

    def test_message_creation(self):
        """Can create a FederationMessage with all fields."""
        msg = FederationMessage(
            source="moksha",
            target="steward-protocol",
            operation="city_report",
            payload={"heartbeat": 100},
            priority=SATTVA,
            correlation_id="test_123",
        )
        assert msg.source == "moksha"
        assert msg.target == "steward-protocol"
        assert msg.operation == "city_report"
        assert msg.priority == SATTVA

    def test_message_timestamp_auto_populated(self):
        """Timestamp is auto-populated on creation."""
        now = datetime.now().timestamp()
        msg = FederationMessage(
            source="s",
            target="t",
            operation="op",
        )
        assert msg.timestamp >= now
        assert msg.timestamp <= now + 1  # Within 1 second

    def test_message_default_priority_is_rajas(self):
        """Default priority is RAJAS."""
        msg = FederationMessage(source="s", target="t", operation="op")
        assert msg.priority == RAJAS

    def test_message_to_dict_roundtrip(self):
        """Message serializes and deserializes correctly."""
        original = FederationMessage(
            source="genesis",
            target="agent-city",
            operation="federation_sync",
            payload={"agent_id": "HERALD"},
            priority=SUDDHA,
            correlation_id="sync_001",
            ttl_s=1800.0,
        )

        # Roundtrip
        data = original.to_dict()
        restored = FederationMessage.from_dict(data)

        assert restored.source == original.source
        assert restored.target == original.target
        assert restored.operation == original.operation
        assert restored.payload == original.payload
        assert restored.priority == original.priority
        assert restored.correlation_id == original.correlation_id
        assert restored.ttl_s == original.ttl_s


# =============================================================================
# TEST: TTL EXPIRY
# =============================================================================


class TestTTLExpiry:
    """Test TTL expiration detection."""

    def test_ttl_zero_never_expires(self):
        """TTL=0 means never expire."""
        msg = FederationMessage(
            source="s",
            target="t",
            operation="op",
            ttl_s=0,
        )
        assert msg.is_expired is False

    def test_message_expires_after_ttl(self):
        """Message expires when current_time > timestamp + ttl_s."""
        old_time = (datetime.now() - timedelta(seconds=30)).timestamp()
        msg = FederationMessage(
            source="s",
            target="t",
            operation="op",
            timestamp=old_time,
            ttl_s=10.0,  # 10 second TTL
        )
        assert msg.is_expired is True

    def test_message_not_expired_before_ttl(self):
        """Message not expired if within TTL."""
        msg = FederationMessage(
            source="s",
            target="t",
            operation="op",
            ttl_s=3600.0,  # 1 hour
        )
        assert msg.is_expired is False


# =============================================================================
# TEST: CITY REPORT
# =============================================================================


class TestCityReport:
    """Test CityReport serialization."""

    def test_city_report_creation(self):
        """Can create a CityReport."""
        report = CityReport(
            heartbeat=100,
            timestamp=datetime.now().timestamp(),
            population=10,
            alive=8,
            dead=2,
            elected_mayor="citizen_1",
            council_seats=5,
            open_proposals=2,
            chain_valid=True,
            mission_results=[
                {"id": "m1", "status": "completed"},
            ],
        )
        assert report.heartbeat == 100
        assert report.alive == 8

    def test_city_report_to_dict_roundtrip(self):
        """CityReport serializes and deserializes."""
        original = CityReport(
            heartbeat=200,
            timestamp=datetime.now().timestamp(),
            population=50,
            alive=45,
            dead=5,
            elected_mayor="citizen_2",
            council_seats=7,
            open_proposals=3,
            chain_valid=True,
            mission_results=[{"name": "heal_lint", "status": "completed"}],
            pr_results=[{"id": "pr_1", "status": "merged"}],
        )

        data = original.to_dict()
        restored = CityReport.from_dict(data)

        assert restored.heartbeat == original.heartbeat
        assert restored.population == original.population
        assert restored.mission_results == original.mission_results


# =============================================================================
# TEST: FEDERATION DIRECTIVE
# =============================================================================


class TestFederationDirective:
    """Test FederationDirective."""

    def test_directive_creation(self):
        """Can create a FederationDirective."""
        directive = FederationDirective(
            id="dir_001",
            directive_type="create_mission",
            params={"topic": "heal_lint"},
            timestamp=datetime.now().timestamp(),
        )
        assert directive.id == "dir_001"
        assert directive.directive_type == "create_mission"

    def test_directive_to_dict_roundtrip(self):
        """Directive serializes and deserializes."""
        original = FederationDirective(
            id="dir_002",
            directive_type="freeze_agent",
            params={"agent_id": "BAD_ACTOR"},
            timestamp=datetime.now().timestamp(),
            source="steward-protocol",
        )

        data = original.to_dict()
        restored = FederationDirective.from_dict(data)

        assert restored.id == original.id
        assert restored.directive_type == original.directive_type
        assert restored.params == original.params
        assert restored.source == original.source


# =============================================================================
# TEST: FEDERATION NADI CONSUMER (MAIN)
# =============================================================================


class TestFederationNadiConsumer:
    """Test FederationNadi consumer API."""

    @pytest.fixture
    def temp_federation_dir(self):
        """Create temporary federation directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def nadi(self, temp_federation_dir):
        """Create a FederationNadi instance with temp directory."""
        return FederationNadi(temp_federation_dir)

    # =========================================================================
    # EMIT / SEND
    # =========================================================================

    def test_emit_creates_inbox_file(self, nadi):
        """emit() creates nadi_inbox.json."""
        success = nadi.emit(
            source="steward-protocol",
            target="agent-city",
            operation="federation_sync",
            payload={"agent_id": "HERALD"},
        )
        assert success is True
        assert nadi.inbox_path.exists()

    def test_emit_appends_messages(self, nadi):
        """Multiple emit() calls append to inbox."""
        nadi.emit(
            source="genesis",
            target="agent-city",
            operation="op1",
        )
        nadi.emit(
            source="dharma",
            target="agent-city",
            operation="op2",
        )

        with open(nadi.inbox_path) as f:
            data = json.load(f)
        assert len(data) == 2

    def test_send_message_atomic_write(self, nadi):
        """send_message() uses atomic writes (.tmp → rename)."""
        msg = FederationMessage(
            source="karma",
            target="agent-city",
            operation="test_op",
        )

        nadi.send_message(msg)

        # .tmp file should not exist (should be renamed)
        assert not nadi.inbox_path.with_suffix(".json.tmp").exists()
        assert nadi.inbox_path.exists()

    # =========================================================================
    # RECEIVE / DEDUP
    # =========================================================================

    def test_receive_empty_when_no_outbox(self, nadi):
        """receive() returns empty list when outbox doesn't exist."""
        messages = nadi.receive()
        assert messages == []

    def test_receive_reads_outbox_messages(self, nadi):
        """receive() reads messages from nadi_outbox.json."""
        # Create outbox manually
        msg_dict = FederationMessage(
            source="moksha",
            target="steward-protocol",
            operation="city_report",
            payload={"heartbeat": 100},
        ).to_dict()

        with open(nadi.outbox_path, "w") as f:
            json.dump([msg_dict], f)

        messages = nadi.receive()
        assert len(messages) == 1
        assert messages[0].source == "moksha"
        assert messages[0].operation == "city_report"

    def test_receive_filters_expired_messages(self, nadi):
        """receive() skips messages that have expired."""
        old_time = (datetime.now() - timedelta(seconds=30)).timestamp()

        # One fresh, one expired
        fresh = FederationMessage(
            source="moksha",
            target="steward-protocol",
            operation="op1",
            ttl_s=3600.0,
        ).to_dict()

        expired = FederationMessage(
            source="karma",
            target="steward-protocol",
            operation="op2",
            timestamp=old_time,
            ttl_s=10.0,
        ).to_dict()

        with open(nadi.outbox_path, "w") as f:
            json.dump([fresh, expired], f)

        messages = nadi.receive()
        assert len(messages) == 1
        assert messages[0].source == "moksha"

    def test_receive_dedup_by_source_timestamp(self, nadi):
        """receive() deduplicates by (source, timestamp) pair."""
        now = datetime.now().timestamp()

        # Same source and timestamp = duplicate
        msg1 = FederationMessage(
            source="moksha",
            target="steward-protocol",
            operation="city_report",
            timestamp=now,
        ).to_dict()

        msg2 = FederationMessage(
            source="moksha",
            target="steward-protocol",
            operation="different_op",
            timestamp=now,
        ).to_dict()

        with open(nadi.outbox_path, "w") as f:
            json.dump([msg1, msg2], f)

        messages = nadi.receive()
        # Should only return first one (deduped)
        assert len(messages) == 1

    def test_receive_sorts_by_priority(self, nadi):
        """receive() sorts messages by priority (highest first)."""
        now = datetime.now().timestamp()

        msg_rajas = FederationMessage(
            source="s1",
            target="t",
            operation="op",
            priority=RAJAS,
            timestamp=now,
            ttl_s=3600.0,  # 1 hour, won't expire
        ).to_dict()

        msg_sattva = FederationMessage(
            source="s2",
            target="t",
            operation="op",
            priority=SATTVA,
            timestamp=now,
            ttl_s=3600.0,
        ).to_dict()

        msg_tamas = FederationMessage(
            source="s3",
            target="t",
            operation="op",
            priority=TAMAS,
            timestamp=now,
            ttl_s=3600.0,
        ).to_dict()

        with open(nadi.outbox_path, "w") as f:
            json.dump([msg_tamas, msg_rajas, msg_sattva], f)

        messages = nadi.receive()
        # Should be ordered: SATTVA, RAJAS, TAMAS
        assert len(messages) == 3
        assert messages[0].priority == SATTVA
        assert messages[1].priority == RAJAS
        assert messages[2].priority == TAMAS

    # =========================================================================
    # MAINTENANCE
    # =========================================================================

    def test_clear_outbox(self, nadi):
        """clear_outbox() deletes nadi_outbox.json."""
        # Create a file first
        nadi.outbox_path.write_text("[]")
        assert nadi.outbox_path.exists()

        # Clear it
        success = nadi.clear_outbox()
        assert success is True
        assert not nadi.outbox_path.exists()

    def test_clear_inbox(self, nadi):
        """clear_inbox() deletes nadi_inbox.json."""
        nadi.emit("s", "t", "op")
        assert nadi.inbox_path.exists()

        success = nadi.clear_inbox()
        assert success is True
        assert not nadi.inbox_path.exists()

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def test_stats_empty_federation(self, nadi):
        """stats() returns zeros when no files exist."""
        stats = nadi.stats()
        assert stats["outbox_pending"] == 0
        assert stats["inbox_pending"] == 0
        assert stats["reports_archived"] == 0

    def test_stats_with_messages(self, nadi):
        """stats() counts messages in outbox/inbox."""
        nadi.emit("s1", "t", "op1")
        nadi.emit("s2", "t", "op2")

        # Create outbox
        outbox_msgs = [
            FederationMessage(source="moksha", target="steward", operation="op").to_dict(),
            FederationMessage(source="karma", target="steward", operation="op").to_dict(),
        ]
        with open(nadi.outbox_path, "w") as f:
            json.dump(outbox_msgs, f)

        stats = nadi.stats()
        assert stats["outbox_pending"] == 2
        assert stats["inbox_pending"] == 2

    # =========================================================================
    # DIRECTIVES
    # =========================================================================

    def test_write_directive(self, nadi):
        """write_directive() creates directive file."""
        directive = FederationDirective(
            id="dir_001",
            directive_type="create_mission",
            params={"topic": "heal"},
        )

        success = nadi.write_directive(directive)
        assert success is True

        directive_path = nadi.federation_dir / "directives" / "dir_001.json"
        assert directive_path.exists()

        with open(directive_path) as f:
            data = json.load(f)
        assert data["id"] == "dir_001"

    # =========================================================================
    # CITY REPORTS
    # =========================================================================

    def test_save_city_report(self, nadi):
        """save_city_report() stores report as JSON."""
        report = CityReport(
            heartbeat=100,
            timestamp=datetime.now().timestamp(),
            population=10,
            alive=8,
            dead=2,
            elected_mayor="citizen",
            council_seats=3,
            open_proposals=1,
            chain_valid=True,
        )

        success = nadi.save_city_report(report)
        assert success is True

        report_path = nadi.federation_dir / "reports" / "report_000100.json"
        assert report_path.exists()

    def test_get_latest_city_report(self, nadi):
        """get_latest_city_report() returns most recent report."""
        # Save multiple reports
        for i in range(1, 4):
            report = CityReport(
                heartbeat=i * 100,
                timestamp=datetime.now().timestamp(),
                population=i * 10,
                alive=i * 8,
                dead=i * 2,
                elected_mayor="citizen",
                council_seats=3,
                open_proposals=1,
                chain_valid=True,
            )
            nadi.save_city_report(report)

        latest = nadi.get_latest_city_report()
        assert latest is not None
        assert latest.heartbeat == 300


# =============================================================================
# TEST: CROSS-REPO COMPATIBILITY
# =============================================================================


class TestCrossRepoCompatibility:
    """Test compatibility with agent-city format."""

    @pytest.fixture
    def temp_federation_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def nadi(self, temp_federation_dir):
        return FederationNadi(temp_federation_dir)

    def test_agent_city_format_readable(self, nadi):
        """Can read agent-city's outbox format exactly."""
        now = datetime.now().timestamp()

        # Real format from agent-city (adapted with current timestamp)
        agent_city_msg = {
            "source": "moksha",
            "target": "steward-protocol",
            "operation": "city_report",
            "payload": {
                "heartbeat": 179,
                "population": 0,
                "alive": 0,
                "chain_valid": True,
            },
            "priority": 2,
            "correlation_id": "",
            "timestamp": now,
            "ttl_s": 900.0,
        }

        with open(nadi.outbox_path, "w") as f:
            json.dump([agent_city_msg], f)

        messages = nadi.receive()
        assert len(messages) == 1
        assert messages[0].source == "moksha"
        assert messages[0].payload["heartbeat"] == 179

    def test_steward_protocol_inbox_compatible(self, nadi):
        """Inbox format is readable by agent-city."""
        nadi.emit(
            source="steward-protocol",
            target="agent-city",
            operation="federation_sync",
            payload={"agent_id": "HERALD"},
            priority=SATTVA,
        )

        # agent-city should be able to read this
        with open(nadi.inbox_path) as f:
            data = json.load(f)

        # Should be valid array of messages
        assert isinstance(data, list)
        assert len(data) > 0

        msg = data[0]
        assert msg["source"] == "steward-protocol"
        assert msg["target"] == "agent-city"
        assert "timestamp" in msg
        assert "ttl_s" in msg
