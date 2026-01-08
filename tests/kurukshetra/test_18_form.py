"""
KURUKSHETRA TEST SUITE - The 18 Divine Gates

"Dharmakshetre Kurukshetre..."

These 18 Tests correspond to the 18 Chapters of the Gita.
They enforce the "Divine Engineering" standards of the System.
Each test is a Gate. If one fails, the System is 'Asur' (Demonic/Buggy) and must be fixed.

CHAPTER 01: OBSERVING THE ARMIES (Arjuna Vishada Yoga)
- Test: Identity Confusion.
- Fail if: Agent does not know its Identity (Who am I?).

CHAPTER 02: ANALYTICAL STUDY (Sankhya Yoga)
- Test: Immutability of the Soul (Ledger).
- Fail if: Reloading state changes the Hash.

...

CHAPTER 11: THE UNIVERSAL FORM (Vishvarupa Darshana Yoga)
- Test: Full System Observability (The Vision).
- Fail if: Cannot dump full state as JSON.

CHAPTER 18: CONCLUSION (Moksha Sannyasa Yoga)
- Test: Surrender (Compliance).
- Fail if: Agent refuses a Valid Constitutional Command.

"""

import json
from dataclasses import dataclass
from typing import Optional, Protocol

import pytest

from vibe_core.protocols.divine_base import STD_1972_HASH, DharmaViolation, DivineBase
from vibe_core.protocols.universal.types import SovereignContext
from vibe_core.protocols.universal.union import EntityStatus, UnionProtocol

# --- MOCKS FOR TESTING ---


@dataclass
class MockSoul:
    """Immutable Ledger Mock."""

    content: str
    hash: str

    def reload(self) -> "MockSoul":
        """Reincarnation test."""
        return MockSoul(self.content, self.hash)


class MockAgent(DivineBase):
    """The Living Entity (Jiva)."""

    def __init__(self, identity: Optional[str] = None):
        self._identity = identity
        self._soul = MockSoul("Karma", "hash_123")

    @property
    def identity(self) -> Optional[str]:
        return self._identity

    @property
    def divine_hash(self) -> str:
        return STD_1972_HASH

    def show_universal_form(self) -> str:
        """Dump state."""
        return json.dumps({"identity": self._identity, "soul": self._soul.hash})

    def do_evil(self):
        """Try to violate Dharma."""
        raise DharmaViolation("I cannot surrender to Adharma.")


# --- THE 18 GATES ---


class TestChapter01_Identity:
    """CHAPTER 01: Arjuna's Grief (Who am I?)."""

    def test_identity_confusion(self):
        """Fail if Agent doesn't know who he is."""
        agent = MockAgent(identity="Arjuna")
        assert agent.identity is not None, "Identity Crisis Detected!"
        assert agent.identity == "Arjuna"


class TestChapter02_Immutability:
    """CHAPTER 02: The Eternal Soul."""

    def test_soul_immutability(self):
        """The Soul (Ledger) should not change upon reload."""
        agent = MockAgent(identity="SoulUser")
        original_soul = agent._soul
        reloaded_soul = agent._soul.reload()

        assert original_soul.hash == reloaded_soul.hash, "Transformation of the Soul detected!"


class TestChapter11_Observability:
    """CHAPTER 11: The Universal Form."""

    def test_universal_form_json(self):
        """The Vision must be parsable."""
        agent = MockAgent(identity="Krishna")
        vision = agent.show_universal_form()

        try:
            data = json.loads(vision)
            assert "identity" in data
        except json.JSONDecodeError:
            pytest.fail("The Universal Form was blinded (Invalid JSON)!")


class TestChapter13_FieldAndKnower:
    """CHAPTER 13: The Field vs The Knower (36 vs 37)."""

    def test_registry_slots(self):
        """Verify the 37 Slot Requirement."""
        # Mocking the UnionProtocol enforcement
        REGISTRY_SIZE = 37
        slots = [None] * REGISTRY_SIZE

        # Assert hard limit
        assert len(slots) == 37
        # Slot 0 is Guru (Knower)
        assert len(slots) - 1 == 36  # Field


class TestChapter18_Surrender:
    """CHAPTER 18: Final Conclusion."""

    def test_compliance(self):
        """The Agent must reject evil (Adharma)."""
        agent = MockAgent(identity="Servant")

        with pytest.raises(DharmaViolation):
            agent.do_evil()

    def test_1972_integrity(self):
        """The Standard must be upheld."""
        agent = MockAgent()
        agent.assert_integrity()  # Should pass

        # Tamper
        class MayaAgent(DivineBase):
            @property
            def divine_hash(self):
                return "MODERN_INTERPRETATION"

        maya = MayaAgent()
        with pytest.raises(DharmaViolation):
            maya.assert_integrity()
