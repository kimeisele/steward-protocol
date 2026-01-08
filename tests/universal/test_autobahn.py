"""
TEST AUTOBAHN - Verifying the Transgalactic Infrastructure.

"Jagannath needs the Best Streets."

This test verifies:
1. The 3 Lanes (Sattva, Rajas, Tamas).
2. The Packet Structure (Sealed).
3. The TÜV Check (Signature Enforcement).
"""

from typing import Any, Dict

import pytest

from vibe_core.protocols.universal.autobahn import IAutobahn, Lane, Packet

# =============================================================================
# MOCK INFRASTRUCTURE (The German Road)
# =============================================================================


class GermanAutobahn(IAutobahn):
    """
    A concrete implementation of the Autobahn for testing.
    """

    def __init__(self):
        self.lanes_open = {l: False for l in Lane}
        self.traffic_log = []

    def open_lane(self, lane: Lane) -> bool:
        self.lanes_open[lane] = True
        return True

    def transport(self, packet: Packet) -> str:
        # 1. TÜV CHECK (Signature)
        if not packet.signature:
            raise ValueError("TÜV REJECTED: Packet unsigned! (Incinerated)")

        # 2. Gate Check
        if not self.lanes_open[packet.lane]:
            return f"BLOCKED: Lane {packet.lane} is closed."

        # 3. Transport
        self.traffic_log.append(packet)
        return f"DELIVERED via {packet.lane}: {packet.id}"

    def traffic_status(self) -> Dict[str, Any]:
        return {"lanes": self.lanes_open, "packet_count": len(self.traffic_log)}


# =============================================================================
# THE TEST DRIVE
# =============================================================================


def test_autobahn_lanes():
    """Verify the 3 Lanes exist."""
    assert Lane.SATTVA == "SATTVA"
    assert Lane.RAJAS == "RAJAS"
    assert Lane.TAMAS == "TAMAS"


def test_tuv_signature_enforcement():
    """
    TÜV TEST: Unsigned packets must be destroyed.
    """
    road = GermanAutobahn()
    road.open_lane(Lane.SATTVA)

    # 1. Unsigned Packet (Ghost)
    ghost_packet = Packet(
        id="ghost_1",
        lane=Lane.SATTVA,
        payload="Haunt",
        signature="",  # MISSING
        headers={},
    )

    with pytest.raises(ValueError, match="TÜV REJECTED"):
        road.transport(ghost_packet)

    # 2. Signed Packet (Sovereign)
    clean_packet = Packet(
        id="jagannath_1",
        lane=Lane.SATTVA,
        payload="Blessings",
        signature="sovereign_key_37",  # SEALED
        headers={},
    )

    result = road.transport(clean_packet)
    assert "DELIVERED" in result
    assert "SATTVA" in result


def test_lane_gating():
    """
    Verify lanes can be opened/closed.
    """
    road = GermanAutobahn()
    # Don't open options

    packet = Packet(id="test", lane=Lane.RAJAS, payload="Action", signature="sig", headers={})
    result = road.transport(packet)
    assert "BLOCKED" in result

    # Open Upp
    road.open_lane(Lane.RAJAS)
    result = road.transport(packet)
    assert "DELIVERED" in result
