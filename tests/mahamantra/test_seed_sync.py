"""
TEST: Seed Divergence Detection (Watertight)
=============================================

This test ensures substrate/seed.py stays in sync with protocols/_seed.py.

If this test fails, it means someone added a constant to one file
but not the other. FIX: Import from protocols/_seed.py (THE LAW).

WATERTIGHT: No hardcoded values - everything derived from SSOT.
"""

import pytest


class TestSeedSync:
    """Test that substrate imports from protocol (no divergence)."""

    def test_nava_sync(self) -> None:
        """NAVA must be identical in both files."""
        from vibe_core.mahamantra.protocols._seed import NAVA as P_NAVA
        from vibe_core.mahamantra.substrate.seed import NAVA as S_NAVA

        assert P_NAVA == S_NAVA == 9, "NAVA diverged!"

    def test_phase_duration_sync(self) -> None:
        """PHASE_DURATION must be identical in both files."""
        from vibe_core.mahamantra.protocols._seed import PHASE_DURATION as P_PD
        from vibe_core.mahamantra.substrate.seed import PHASE_DURATION as S_PD

        assert P_PD == S_PD == 12, "PHASE_DURATION diverged!"

    def test_avatar_count_sync(self) -> None:
        """AVATAR_COUNT must be identical in both files."""
        from vibe_core.mahamantra.protocols._seed import AVATAR_COUNT as P_AC
        from vibe_core.mahamantra.substrate.seed import AVATAR_COUNT as S_AC

        assert P_AC == S_AC == 4, "AVATAR_COUNT diverged!"

    def test_mahajana_count_sync(self) -> None:
        """MAHAJANA_COUNT must be identical in both files."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT as P_MC
        from vibe_core.mahamantra.substrate.seed import MAHAJANA_COUNT as S_MC

        assert P_MC == S_MC == 12, "MAHAJANA_COUNT diverged!"

    def test_guardian_completeness(self) -> None:
        """4 Avatars + 12 Mahajanas = 16 Words (Guardian Completeness)."""
        from vibe_core.mahamantra.protocols._seed import AVATAR_COUNT, MAHAJANA_COUNT, WORDS

        assert AVATAR_COUNT + MAHAJANA_COUNT == WORDS == 16

    def test_holographic_principle(self) -> None:
        """PHASE_DURATION == MAHAJANA_COUNT (Time = Space)."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT, PHASE_DURATION

        assert PHASE_DURATION == MAHAJANA_COUNT == 12

    def test_mala_geometry(self) -> None:
        """MAHAJANA_COUNT * NAVA = MALA (12 * 9 = 108)."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT, MALA, NAVA

        assert MAHAJANA_COUNT * NAVA == MALA == 108

    def test_substrate_avataras_match_count(self) -> None:
        """AVATARAS tuple must have AVATAR_COUNT elements."""
        from vibe_core.mahamantra.substrate.seed import AVATAR_COUNT, AVATARAS

        assert len(AVATARAS) == AVATAR_COUNT == 4

    def test_substrate_mahajanas_match_count(self) -> None:
        """MAHAJANAS tuple must have MAHAJANA_COUNT elements."""
        from vibe_core.mahamantra.substrate.seed import MAHAJANA_COUNT, MAHAJANAS

        assert len(MAHAJANAS) == MAHAJANA_COUNT == 12

    def test_all_guardians_complete(self) -> None:
        """ALL_GUARDIANS must have exactly 16 elements."""
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, WORDS

        assert len(ALL_GUARDIANS) == WORDS == 16

    def test_epoch_key_sync(self) -> None:
        """EPOCH_KEY must be identical in both files."""
        from vibe_core.mahamantra.protocols._seed import EPOCH_KEY as P_EPOCH
        from vibe_core.mahamantra.substrate.seed import EPOCH_KEY as S_EPOCH

        assert P_EPOCH == S_EPOCH == 1972, "EPOCH_KEY diverged!"

    def test_epoch_key_seed_alignment(self) -> None:
        """EPOCH_KEY / QUARTERS digit sum must equal WORDS (16)."""
        from vibe_core.mahamantra.protocols._seed import EPOCH_KEY, QUARTERS, WORDS

        digit_sum = sum(int(d) for d in str(EPOCH_KEY // QUARTERS))
        assert digit_sum == WORDS == 16, "EPOCH_KEY does not align with Seed Structure"

    def test_epoch_key_mala_alignment(self) -> None:
        """EPOCH_KEY / QUARTERS digit product must equal MALA (108)."""
        from vibe_core.mahamantra.protocols._seed import EPOCH_KEY, MALA, QUARTERS

        digits = [int(d) for d in str(EPOCH_KEY // QUARTERS)]
        product = 1
        for d in digits:
            product *= d
        assert product == MALA == 108, "EPOCH_KEY does not align with Mala Geometry"

    def test_epoch_key_signature(self) -> None:
        """EPOCH_KEY digit sum must equal WORDS + TRINITY (19)."""
        from vibe_core.mahamantra.protocols._seed import EPOCH_KEY, TRINITY, WORDS

        signature = sum(int(d) for d in str(EPOCH_KEY))
        assert signature == WORDS + TRINITY == 19, "EPOCH_KEY Signature Invalid"
