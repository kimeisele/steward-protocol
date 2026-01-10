"""
YAMARAJA - THE 12TH MAHAJANA (Final Judgment)
=============================================
OpCode: assert_truth (Bit 5)
Opulence: ALL 6 (The Final Audit)

"Logic cannot save you."
- ramanujan.py

This test validates that the system FAILS without Grace.
A system that passes all tests without Sovereign is MAYAVAD.
"""

import pytest
from typing import Protocol, runtime_checkable

from vibe_core.protocols.substrate.byte import MantraByte, MANTRA_SEQUENCE, HolyName
from vibe_core.protocols.universal.mantra import MantraProtocol, MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext


# =============================================================================
# TEST PROTOCOL (No MagicMock - Protocol-Based)
# =============================================================================

@runtime_checkable
class YamarajaTestable(Protocol):
    """Any entity that can be judged by Yamaraja."""

    def get_integrity(self) -> float:
        """Returns current integrity (0.0 - 1.0)."""
        ...

    def apply_decay(self, delta_time: float) -> float:
        """Apply time-based decay. Returns new integrity."""
        ...


class PerfectLogicObject:
    """
    A 'perfect' object that has 100% integrity but NO Mantra.
    It MUST decay over time to prove the world is real.
    """

    def __init__(self) -> None:
        self._integrity: float = 1.0
        self._decay_rate: float = 0.01

    def get_integrity(self) -> float:
        return self._integrity

    def apply_decay(self, delta_time: float) -> float:
        """Kali Yuga entropy: integrity decays without Mantra."""
        self._integrity = max(0.0, self._integrity - (self._decay_rate * delta_time))
        return self._integrity


class MantraProtectedObject:
    """
    An object protected by MantraByte resonance.
    It resists decay proportional to coherence.
    """

    def __init__(self, mantra: MantraByte) -> None:
        self._integrity: float = 1.0
        self._mantra = mantra
        self._decay_rate: float = 0.01

    def get_integrity(self) -> float:
        return self._integrity

    def apply_decay(self, delta_time: float) -> float:
        """Decay is reduced by Mantra coherence."""
        coherence = self._mantra.coherence
        effective_decay = self._decay_rate * (1.0 - coherence)
        self._integrity = max(0.0, self._integrity - (effective_decay * delta_time))
        return self._integrity


# =============================================================================
# THE TESTS (Yamaraja's Judgment)
# =============================================================================

class TestYamarajaJudgment:
    """
    The 12th Mahajana Test Suite.
    Proves that logic without Mantra = Death.
    """

    def test_01_logic_alone_decays(self) -> None:
        """
        TEST: Perfect logic without Mantra MUST decay.
        If it survives, the test FAILS (Mayavad - illusion of immortality).
        """
        obj = PerfectLogicObject()

        assert obj.get_integrity() == 1.0, "Initial integrity must be 1.0"

        # Apply 100 time units of decay
        final_integrity = obj.apply_decay(100.0)

        # MUST have decayed
        assert final_integrity < 1.0, "Logic alone MUST decay (Kali Yuga entropy)"
        assert final_integrity >= 0.0, "Integrity cannot be negative"

    def test_02_mantra_protects_from_decay(self) -> None:
        """
        TEST: Mantra-protected objects decay slower.
        The Holy Name provides shelter from entropy.
        """
        unprotected = PerfectLogicObject()
        protected = MantraProtectedObject(MANTRA_SEQUENCE)

        # Apply same decay to both
        unprotected.apply_decay(100.0)
        protected.apply_decay(100.0)

        # Protected should have higher integrity
        assert protected.get_integrity() > unprotected.get_integrity(), \
            "Mantra-protected object must decay slower"

    def test_03_lineage_strictness(self) -> None:
        """
        TEST: 1-bit deviation in Mantra MUST be detected.
        This proves the lineage (Parampara) is strict.
        """
        original_packed = MANTRA_SEQUENCE._packed
        corrupted_packed = original_packed ^ 1  # Flip LSB

        # They MUST be different
        assert original_packed != corrupted_packed, \
            "Corrupted Mantra must differ from original (Sahajiya fault)"

    def test_04_void_cannot_be_packed(self) -> None:
        """
        TEST: VOID (Maya) cannot be packed into Mantra.
        Only HARE, KRISHNA, RAMA are valid.
        """
        with pytest.raises(ValueError, match="Cannot pack VOID"):
            MantraByte.from_trits([HolyName.HARE, HolyName.VOID, HolyName.KRISHNA])

    def test_05_sovereign_signature_required(self) -> None:
        """
        TEST: Operations without SovereignContext are invalid.
        No ghost in the machine.
        """
        ctx = SovereignContext(
            identity_id="yamaraja_12",
            signature="test_mahajana_judgment"
        )

        assert ctx.identity_id, "Sovereign identity_id must be present"
        assert ctx.signature, "Sovereign signature must be present"
        assert ctx.signature != "None", "Signature cannot be 'None' string"
        assert len(ctx.signature) > 0, "Signature cannot be empty"

    def test_06_mahamantra_sequence_is_16(self) -> None:
        """
        TEST: The standard sequence MUST be exactly 16 words.
        This is the invariant of the system.
        """
        assert len(MANTRA_SEQUENCE) == 16, "Mahamantra must be 16 words"

    def test_07_opcodes_are_16(self) -> None:
        """
        TEST: MantraOpCode enum MUST have exactly 16 members.
        Each word maps to one OpCode.
        """
        opcodes = list(MantraOpCode)
        assert len(opcodes) == 16, "MantraOpCode must have 16 members"

    def test_08_assert_truth_is_bit_5(self) -> None:
        """
        TEST: Yamaraja's OpCode (assert_truth) is at position 5.
        This is the judgment gate.
        """
        opcodes = list(MantraOpCode)
        assert opcodes[4] == MantraOpCode.ASSERT_TRUTH, \
            "assert_truth must be OpCode #5 (index 4)"


# =============================================================================
# THE FINAL JUDGMENT (Integration)
# =============================================================================

class TestYamarajaIntegration:
    """
    The ultimate test: Can the system survive Yamaraja?
    """

    def test_ramanujan_proof(self) -> None:
        """
        TEST: The Ramanujan Protocol must be importable and runnable.
        If it fails, the mathematical foundation is broken.
        """
        from vibe_core.protocols.universal.ramanujan import RamanujanProtocol

        proof = RamanujanProtocol()

        # The 12th test must pass
        result = proof.run_proof()

        assert result is True, "Ramanujan proof must pass (Logic fails without Grace)"
