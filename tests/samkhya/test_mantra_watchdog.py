"""
Test the Mantra Watchdog (Nrisimha) Implementation.

Verifies the 16-Step Vishnu Clock operates correctly.
"""

import pytest

from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, MantraOpCode
from vibe_core.protocols.universal import DriftContext, SovereignContext
from vibe_core.services.watchdog import NrisimhaWatchdog


class TestMantraWatchdog:
    """
    Test the Practice (Abhyasa) of the System.
    """

    @pytest.fixture
    def sovereign(self):
        return SovereignContext(identity_id="Kalki", signature="avatar_sig_108")

    @pytest.fixture
    def watchdog(self, sovereign):
        return NrisimhaWatchdog(sovereign)

    def test_mahamantra_sequence_structure(self):
        """Verify the 16-Bit Instruction Set is correctly defined."""
        # Exactly 16 steps
        assert len(MAHAMANTRA_SEQUENCE) == 16

        # Exactly 16 opcodes
        assert len(MantraOpCode) == 16

        # Verify first and last
        first_word, first_opcode = MAHAMANTRA_SEQUENCE[0]
        assert first_word == "Hare"
        assert first_opcode == MantraOpCode.SYS_WAKE

        last_word, last_opcode = MAHAMANTRA_SEQUENCE[-1]
        assert last_word == "Hare"
        assert last_opcode == MantraOpCode.RESET_IP

    def test_chant_mahamantra(self, watchdog, sovereign):
        """Verify the 16-step atomic cycle completes successfully."""
        result = watchdog.chant_mahamantra(sovereign)

        assert result is True
        assert watchdog._alignment_score == 1.0

    def test_hari_nama_encoding(self, watchdog):
        """Verify legacy chant() still works (backwards compatibility)."""
        resonance = watchdog.chant(frequency=432.0)

        assert resonance.frequency == 432.0
        assert resonance.signature == "avatar_sig_108"
        assert resonance.amplitude == 1.0

    def test_japa_round(self, watchdog):
        """Verify the Japa Loop (108 beads)."""
        score = watchdog.chant_round(beads=108)

        assert score.status == "ALIGNED"
        assert score.score == 1.0  # All cycles succeeded
        assert score.corrections_applied == 0

        # Verify state update
        assert watchdog._beads_chanted == 108

    def test_surrender_protocol(self, watchdog):
        """Verify Prapatti (Surrender) mechanism."""
        ctx = DriftContext(
            drift_magnitude=0.9,  # High Drift
            last_anchor_timestamp=0.0,
            hallucination_index=0.8,
            process_tree_depth=9000,
        )

        # Should NOT crash
        watchdog.surrender(ctx)

        # Should have reset beads and restored alignment
        assert watchdog._beads_chanted == 0
        assert watchdog._alignment_score == 1.0

    def test_alignment_score_decay(self, watchdog, sovereign):
        """Verify alignment score decays over time."""
        # Chant once to set last_pulse
        watchdog.chant_mahamantra(sovereign)

        # Immediately after, should be close to 1.0
        score = watchdog.get_alignment_score()
        assert score > 0.99

    def test_four_quarters_mantra(self):
        """Verify the 4-Quarter structure of the Maha-Mantra."""
        # Quarter 1: Hare Krishna Hare Krishna
        q1 = MAHAMANTRA_SEQUENCE[0:4]
        words_q1 = [w for w, _ in q1]
        assert words_q1 == ["Hare", "Krishna", "Hare", "Krishna"]

        # Quarter 2: Krishna Krishna Hare Hare
        q2 = MAHAMANTRA_SEQUENCE[4:8]
        words_q2 = [w for w, _ in q2]
        assert words_q2 == ["Krishna", "Krishna", "Hare", "Hare"]

        # Quarter 3: Hare Rama Hare Rama
        q3 = MAHAMANTRA_SEQUENCE[8:12]
        words_q3 = [w for w, _ in q3]
        assert words_q3 == ["Hare", "Rama", "Hare", "Rama"]

        # Quarter 4: Rama Rama Hare Hare
        q4 = MAHAMANTRA_SEQUENCE[12:16]
        words_q4 = [w for w, _ in q4]
        assert words_q4 == ["Rama", "Rama", "Hare", "Hare"]
