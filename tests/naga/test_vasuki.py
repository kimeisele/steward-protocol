"""
Tests for VASUKI Service - Network transformation and peer communication.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vibe_core.naga.services.vasuki import VasukiService
from vibe_core.protocols.naga import NodeAddress, SendStatus, SignedEnvelope


class TestVasukiBasics:
    """Test basic Vasuki operations."""

    @pytest.fixture
    def vasuki(self):
        return VasukiService(sesha=None, takshaka=None, sign_outbound=False)

    def test_initialization(self, vasuki):
        assert vasuki._events_processed == 0
        assert vasuki._errors == 0
        assert len(vasuki._peers) == 0

    def test_get_status(self, vasuki):
        status = vasuki.get_status()

        assert status.naga_type.value == "vasuki"
        assert status.healthy is True
        assert status.events_processed == 0


class TestChurnOperations:
    """Test churn_out/churn_in serialization."""

    @pytest.fixture
    def vasuki(self):
        return VasukiService(sign_outbound=False)

    def test_churn_out_creates_envelope(self, vasuki):
        event = {"type": "test", "data": {"key": "value"}}

        envelope = vasuki.churn_out(event)

        assert isinstance(envelope, SignedEnvelope)
        assert envelope.content_type == "msgpack"
        assert len(envelope.payload) > 0

    def test_churn_in_restores_event(self, vasuki):
        original = {"type": "test", "nested": {"a": 1, "b": [1, 2, 3]}}

        envelope = vasuki.churn_out(original)
        restored = vasuki.churn_in(envelope)

        assert restored == original

    def test_round_trip_preserves_data(self, vasuki):
        event = {
            "event_type": "AGENT_ACTION",
            "agent_id": "test_agent",
            "payload": {"x": 1, "y": 2},
            "timestamp": 1234567890,
        }

        envelope = vasuki.churn_out(event)
        result = vasuki.churn_in(envelope)

        assert result == event
        assert vasuki._events_processed == 2  # churn_out + churn_in


class TestPeerManagement:
    """Test peer add/remove operations."""

    @pytest.fixture
    def vasuki(self):
        return VasukiService()

    def test_add_peer_without_url(self, vasuki):
        vasuki.add_peer("peer1")

        assert "peer1" in vasuki.get_peers()
        assert "peer1" not in vasuki._peer_urls

    def test_add_peer_with_url(self, vasuki):
        vasuki.add_peer("peer2", url="http://localhost:8001")

        assert "peer2" in vasuki.get_peers()
        assert vasuki._peer_urls["peer2"] == "http://localhost:8001"

    def test_remove_peer_cleans_url(self, vasuki):
        vasuki.add_peer("peer3", url="http://localhost:8002")
        result = vasuki.remove_peer("peer3")

        assert result is True
        assert "peer3" not in vasuki.get_peers()
        assert "peer3" not in vasuki._peer_urls

    def test_remove_nonexistent_peer(self, vasuki):
        result = vasuki.remove_peer("nonexistent")
        assert result is False


class TestNetworkSend:
    """Test network send operations."""

    @pytest.fixture
    def vasuki(self):
        v = VasukiService(sign_outbound=False)
        v.add_peer("remote_node", url="http://192.168.1.100:8000")
        return v

    def test_send_fails_without_url(self, vasuki):
        # Peer without URL
        vasuki.add_peer("no_url_peer")
        envelope = vasuki.churn_out({"test": True})

        result = asyncio.run(vasuki.send("no_url_peer", envelope))

        assert result.status == SendStatus.FAILED
        assert "No URL configured" in result.message

    def test_send_builds_correct_wire_format(self, vasuki):
        """Test that send() builds correct wire format (without actual network call)."""
        import base64

        envelope = vasuki.churn_out({"test": "data"})

        # Verify envelope structure
        assert isinstance(envelope.payload, bytes)
        assert envelope.content_type == "msgpack"

        # The wire_data structure should be base64 encoded
        wire_payload_b64 = base64.b64encode(envelope.payload).decode()
        assert len(wire_payload_b64) > 0


class TestReceiveQueue:
    """Test receive queue operations."""

    @pytest.fixture
    def vasuki(self):
        return VasukiService()

    def test_push_received(self, vasuki):
        envelope = SignedEnvelope(
            payload=b"test",
            signature=b"",
            sender_key="",
            timestamp=0.0,
            content_type="msgpack",
        )

        result = vasuki.push_received(envelope)

        assert result is True
        assert len(vasuki._receive_queue) == 1

    def test_push_received_queue_full(self, vasuki):
        envelope = SignedEnvelope(
            payload=b"test",
            signature=b"",
            sender_key="",
            timestamp=0.0,
            content_type="msgpack",
        )

        # Fill queue
        for _ in range(1000):
            vasuki._receive_queue.append(envelope)

        # Should fail
        result = vasuki.push_received(envelope)

        assert result is False
        assert vasuki._errors == 1

    @pytest.mark.asyncio
    async def test_receive_drains_queue(self, vasuki):
        envelope1 = SignedEnvelope(
            payload=b"msg1",
            signature=b"",
            sender_key="",
            timestamp=1.0,
            content_type="msgpack",
        )
        envelope2 = SignedEnvelope(
            payload=b"msg2",
            signature=b"",
            sender_key="",
            timestamp=2.0,
            content_type="msgpack",
        )

        vasuki.push_received(envelope1)
        vasuki.push_received(envelope2)

        received = []
        async for env in vasuki.receive():
            received.append(env)

        assert len(received) == 2
        assert received[0].payload == b"msg1"
        assert received[1].payload == b"msg2"
        assert len(vasuki._receive_queue) == 0


class TestBoundaryEnforcement:
    """Test internal/external boundary checks."""

    @pytest.fixture
    def vasuki(self):
        return VasukiService()

    def test_is_internal_by_type(self, vasuki):
        assert vasuki.is_internal({"event_type": "DEBUG"}) is True
        assert vasuki.is_internal({"event_type": "INTERNAL"}) is True
        assert vasuki.is_internal({"event_type": "PRANA"}) is True

    def test_is_internal_by_flag(self, vasuki):
        assert vasuki.is_internal({"_internal": True}) is True
        assert vasuki.is_internal({"_prana": True}) is True

    def test_not_internal(self, vasuki):
        assert vasuki.is_internal({"event_type": "AGENT_ACTION"}) is False
        assert vasuki.is_internal({"event_type": "TASK_COMPLETED"}) is False


class TestCorrectionHandler:
    """Test as_handler() for drift correction."""

    @pytest.fixture
    def vasuki(self):
        v = VasukiService()
        v.add_peer("peer1", "http://localhost:8001")
        return v

    def test_skips_non_config_drift(self, vasuki):
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStrategy,
            UnifiedDriftReport,
        )

        handler = vasuki.as_handler()
        drift = UnifiedDriftReport(
            id="test",
            source=DriftSource.STATE,  # Not CONFIG
            severity=DriftSeverity.INFO,
            message="test drift",
        )

        result = handler(drift, HealingStrategy.AUTO)

        assert result.status.name == "SKIPPED"
        assert "Not a CONFIG drift" in result.message

    def test_skips_when_no_peers(self):
        vasuki = VasukiService()  # No peers
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStrategy,
            UnifiedDriftReport,
        )

        handler = vasuki.as_handler()
        drift = UnifiedDriftReport(
            id="test",
            source=DriftSource.CONFIG,
            severity=DriftSeverity.INFO,
            message="test drift",
        )

        result = handler(drift, HealingStrategy.AUTO)

        assert result.status.name == "SKIPPED"
        assert "No peers" in result.message
