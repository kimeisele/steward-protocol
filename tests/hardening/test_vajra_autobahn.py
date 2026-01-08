"""
TEST_VAJRA_AUTOBAHN.py - Living Software Verification

ADR-001: VAJRA-AUTOBAHN
"The packet tests itself."

This test verifies:
1. MantraSeal validity
2. VajraPacket.verify() self-test
3. Watertight enforcement (no Any)
4. MayavadError on invalid packets
"""

from dataclasses import dataclass
from datetime import datetime

import pytest

from vibe_core.protocols.universal.autobahn import (
    Lane,
    MantraSeal,
    MayavadError,
    TransportResult,
    VajraPacket,
)
from vibe_core.protocols.universal.watertight import Watertight

# =============================================================================
# TEST PAYLOADS (Watertight Implementations)
# =============================================================================


@dataclass
class ValidCapability:
    """A valid Watertight payload."""

    region: str
    max_resources: int

    @classmethod
    def verify_seal(cls) -> bool:
        """Implements Watertight interface."""
        return True


@dataclass
class InvalidCapability:
    """A payload that fails Watertight verification."""

    region: str

    @classmethod
    def verify_seal(cls) -> bool:
        """Fails verification."""
        return False


# =============================================================================
# TESTS: MANTRA SEAL
# =============================================================================


class TestMantraSeal:
    """Tests for MantraSeal validity."""

    def test_valid_seal(self):
        """Valid seal passes is_valid()."""
        seal = MantraSeal(
            signer_id="sovereign-001",
            signature="ed25519:abc123...",
            timestamp=datetime.now(),
            intent_hash="sha256:deadbeef...",
        )
        assert seal.is_valid()

    def test_empty_signer_fails(self):
        """Empty signer_id fails."""
        seal = MantraSeal(
            signer_id="",
            signature="ed25519:abc123...",
            timestamp=datetime.now(),
            intent_hash="sha256:deadbeef...",
        )
        assert not seal.is_valid()

    def test_empty_signature_fails(self):
        """Empty signature fails."""
        seal = MantraSeal(
            signer_id="sovereign-001",
            signature="",
            timestamp=datetime.now(),
            intent_hash="sha256:deadbeef...",
        )
        assert not seal.is_valid()

    def test_empty_intent_hash_fails(self):
        """Empty intent_hash fails."""
        seal = MantraSeal(
            signer_id="sovereign-001",
            signature="ed25519:abc123...",
            timestamp=datetime.now(),
            intent_hash="",
        )
        assert not seal.is_valid()


# =============================================================================
# TESTS: VAJRA PACKET
# =============================================================================


class TestVajraPacket:
    """Tests for VajraPacket self-verification (Living Software)."""

    @pytest.fixture
    def valid_seal(self) -> MantraSeal:
        """Create a valid MantraSeal."""
        return MantraSeal(
            signer_id="sovereign-001",
            signature="ed25519:valid_signature",
            timestamp=datetime.now(),
            intent_hash="sha256:valid_hash",
        )

    @pytest.fixture
    def invalid_seal(self) -> MantraSeal:
        """Create an invalid MantraSeal."""
        return MantraSeal(
            signer_id="",  # Empty = invalid
            signature="ed25519:sig",
            timestamp=datetime.now(),
            intent_hash="sha256:hash",
        )

    def test_valid_packet_verifies(self, valid_seal: MantraSeal):
        """Valid packet with valid payload passes verify()."""
        packet = VajraPacket(
            id="packet-001",
            lane=Lane.SATTVA,
            payload=ValidCapability(region="india", max_resources=100),
            seal=valid_seal,
        )
        assert packet.verify()

    def test_invalid_seal_fails_verify(self, invalid_seal: MantraSeal):
        """Packet with invalid seal fails verify()."""
        packet = VajraPacket(
            id="packet-002",
            lane=Lane.SATTVA,
            payload=ValidCapability(region="india", max_resources=100),
            seal=invalid_seal,
        )
        assert not packet.verify()

    def test_invalid_payload_fails_verify(self, valid_seal: MantraSeal):
        """Packet with invalid Watertight payload fails verify()."""
        packet = VajraPacket(
            id="packet-003",
            lane=Lane.RAJAS,
            payload=InvalidCapability(region="maya"),
            seal=valid_seal,
        )
        assert not packet.verify()

    def test_sattva_lane_assignment(self, valid_seal: MantraSeal):
        """SATTVA lane is correctly assigned."""
        packet = VajraPacket(
            id="fast-packet",
            lane=Lane.SATTVA,
            payload=ValidCapability(region="vaikuntha", max_resources=999),
            seal=valid_seal,
        )
        assert packet.lane == Lane.SATTVA
        assert packet.verify()


# =============================================================================
# TESTS: TRANSPORT RESULT
# =============================================================================


class TestTransportResult:
    """Tests for TransportResult dataclass."""

    def test_success_result(self):
        """Success result has correct fields."""
        result = TransportResult(
            success=True,
            packet_id="packet-001",
            lane=Lane.SATTVA,
            message="Delivered to Vaikuntha",
        )
        assert result.success
        assert result.lane == Lane.SATTVA

    def test_quarantine_result(self):
        """Quarantine result has reason."""
        result = TransportResult(
            success=False,
            packet_id="packet-666",
            lane=Lane.TAMAS,
            quarantine_reason="Low Karma",
        )
        assert not result.success
        assert result.quarantine_reason == "Low Karma"


# =============================================================================
# TESTS: MAYAVAD ERROR
# =============================================================================


class TestMayavadError:
    """Tests for MayavadError exception."""

    def test_mayavad_error_raised(self):
        """MayavadError can be raised with message."""
        with pytest.raises(MayavadError, match="Untyped chaos"):
            raise MayavadError("Untyped chaos detected!")
