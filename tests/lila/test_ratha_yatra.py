"""
TEST RATHA YATRA - The Festival of Chariots.

"He comes out of the Temple to meet the people."

This test verifies the JAGANNATH PROTOCOL behaviors:
1. Darshan (Observability) - Seeing the Union.
2. Prasadam (Mercy) - Graceful degradation.
3. Ratha Yatra (Action) - Flooding the streets (System-wide scan).
"""

from typing import Any, List

import pytest

from vibe_core.protocols.universal.jagannath import JagannathProtocol
from vibe_core.protocols.universal.union import EntityStatus, UnionScanResult

# =============================================================================
# MOCK IMPLEMENTATION (The Wood Form)
# =============================================================================


class MockJagannath(JagannathProtocol):
    """
    A concrete implementation of the Lord for testing.
    """

    def __init__(self, entities: List[EntityStatus]):
        self._entities = entities
        self.blessings_count = 0

    def darshan(self) -> UnionScanResult:
        """See everyone."""
        return UnionScanResult(entities=self._entities, complete=True, scanned_count=len(self._entities), ghost_count=0)

    def prasadam(self, request: Any) -> Any:
        """
        Mercy logic:
        If request is "SIN" (Error), return "MERCY" (Default).
        Else return result.
        """
        if request == "SIN":
            return "MERCY"  # Graceful fallback
        return f"GRANTED: {request}"

    def ratha_yatra(self) -> int:
        """
        Bless everyone.
        """
        count = len(self._entities)
        self.blessings_count += count
        return count

    @property
    def sovereign_form(self) -> str:
        return "sovereign_key_mock_108"


# =============================================================================
# THE FESTIVAL (Tests)
# =============================================================================


@pytest.fixture
def devotee_entities():
    return [
        EntityStatus(
            id="devotee_1",
            type="agent",
            status="ACTIVE",
            protocol="bhakti",
            is_living=True,
            tuv_score=1.0,
            last_heartbeat=None,
            certificate="valid",
        ),
        EntityStatus(
            id="devotee_2",
            type="agent",
            status="ACTIVE",
            protocol="bhakti",
            is_living=True,
            tuv_score=1.0,
            last_heartbeat=None,
            certificate="valid",
        ),
    ]


def test_darshan_observability(devotee_entities):
    """
    DARSHAN TEST: Can we see everything?
    """
    lord = MockJagannath(devotee_entities)
    vision = lord.darshan()

    assert len(vision.entities) == 2
    assert vision.scanned_count == 2
    assert vision.complete is True


def test_prasadam_mercy():
    """
    PRASADAM TEST: Do we get mercy when we fail?
    """
    lord = MockJagannath([])

    # 1. Valid Request
    result = lord.prasadam("SERVICE")
    assert result == "GRANTED: SERVICE"

    # 2. Invalid Request (Sin/Error) -> Mercy
    result = lord.prasadam("SIN")
    assert result == "MERCY", "He should give Mercy, not crash."


def test_ratha_yatra_flood(devotee_entities):
    """
    RATHA YATRA TEST: Does the chariot move?
    """
    lord = MockJagannath(devotee_entities)

    # The Festival Begins
    blessed_count = lord.ratha_yatra()

    assert blessed_count == 2
    assert lord.blessings_count == 2
    assert lord.sovereign_form == "sovereign_key_mock_108"
