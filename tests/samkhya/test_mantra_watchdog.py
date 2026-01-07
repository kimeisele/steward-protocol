import pytest

from vibe_core.protocols.universal import DriftContext, MantraInstruction, SovereignContext
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

    def test_hari_nama_encoding(self, watchdog):
        """Verify the 16-Bit Instruction Set execution."""
        resonance = watchdog.chant(frequency=432.0)

        assert resonance.frequency == 432.0
        assert resonance.signature == "avatar_sig_108"
        assert resonance.amplitude == 1.0

        # Verify instructions exist in Enum
        assert MantraInstruction.BIT_01_HARE_SIGSTOP == "SIGSTOP"
        assert MantraInstruction.BIT_16_HARE_YIELD == "YIELD"

    def test_japa_round(self, watchdog):
        """Verify the Japa Loop (108 beads)."""
        score = watchdog.chant_round(beads=108)

        assert score.status == "ALIGNED"
        assert score.score == 1.0  # Mock perfect alignment
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

        # Should have reset beads
        assert watchdog._beads_chanted == 0
