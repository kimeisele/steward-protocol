"""
Tests for substrate/language/mantra_grid.py — 32-Step Mantra Sequencer.

Only tests what is DERIVED from seed.MAHAMANTRA, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, QUARTERS, WORDS
from vibe_core.mahamantra.substrate.language.types import SyllableVector
from vibe_core.mahamantra.substrate.language.mantra_grid import (
    GridStep,
    alignment_score,
    align_syllables_to_grid,
    build_mantra_grid,
    get_holyname_mode,
)
from vibe_core.mahamantra.substrate.seed import HolyName, MAHAMANTRA


# =============================================================================
# build_mantra_grid: 16 words × 2 beats = 32 steps
# =============================================================================


class TestBuildMantraGrid:
    """build_mantra_grid derives 32 steps from seed.MAHAMANTRA."""

    def test_exactly_32_steps(self):
        grid = build_mantra_grid()
        assert len(grid) == WORDS * HALVES  # 16 × 2 = 32

    def test_all_gridstep_type(self):
        for gs in build_mantra_grid():
            assert isinstance(gs, GridStep)

    def test_positions_sequential(self):
        grid = build_mantra_grid()
        for i, gs in enumerate(grid):
            assert gs.position == i

    def test_beats_alternate(self):
        grid = build_mantra_grid()
        for i, gs in enumerate(grid):
            assert gs.beat == i % HALVES  # 0, 1, 0, 1, ...

    def test_holy_names_from_mahamantra(self):
        grid = build_mantra_grid()
        for i, name in enumerate(MAHAMANTRA):
            assert grid[i * HALVES].holy_name == name
            assert grid[i * HALVES + KSETRAJNA].holy_name == name

    def test_modes_match_holyname_mode(self):
        mode_map = get_holyname_mode()
        for gs in build_mantra_grid():
            assert gs.mode == mode_map[gs.holy_name]

    def test_only_three_modes(self):
        modes = {gs.mode for gs in build_mantra_grid()}
        assert modes == {"DHARMA", "GENESIS", "KARMA"}

    def test_only_three_holy_names(self):
        names = {gs.holy_name for gs in build_mantra_grid()}
        assert names == {HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA}

    def test_cached(self):
        a = build_mantra_grid()
        b = build_mantra_grid()
        assert a is b  # lru_cache returns same object


# =============================================================================
# get_holyname_mode: HolyName → mode mapping
# =============================================================================


class TestGetHolynameMode:
    """get_holyname_mode exposes the canonical mapping."""

    def test_three_entries(self):
        m = get_holyname_mode()
        assert len(m) == 3

    def test_hare_is_dharma(self):
        assert get_holyname_mode()[HolyName.HARE] == "DHARMA"

    def test_krishna_is_genesis(self):
        assert get_holyname_mode()[HolyName.KRISHNA] == "GENESIS"

    def test_rama_is_karma(self):
        assert get_holyname_mode()[HolyName.RAMA] == "KARMA"

    def test_returns_dict_copy(self):
        a = get_holyname_mode()
        b = get_holyname_mode()
        assert a == b
        assert a is not b  # dict() creates new copy


# =============================================================================
# alignment_score: SyllableVector × GridStep → int
# =============================================================================


class TestAlignmentScore:
    """alignment_score: phonetic-rhythmic fit between syllable and grid step."""

    def test_stressed_on_downbeat(self):
        sv = SyllableVector(stress=1, height=3, weight=2)
        gs = GridStep(position=0, holy_name=HolyName.HARE, mode="DHARMA", beat=0)
        score = alignment_score(sv, gs)
        assert score >= 3  # stressed + downbeat = +3

    def test_unstressed_on_upbeat(self):
        sv = SyllableVector(stress=0, height=3, weight=2)
        gs = GridStep(position=1, holy_name=HolyName.HARE, mode="DHARMA", beat=KSETRAJNA)
        score = alignment_score(sv, gs)
        assert score >= 2  # unstressed + upbeat = +2

    def test_heavy_on_krishna(self):
        sv = SyllableVector(stress=0, height=3, weight=4)
        gs = GridStep(position=0, holy_name=HolyName.KRISHNA, mode="GENESIS", beat=0)
        score = alignment_score(sv, gs)
        assert score >= 2  # heavy + Krishna = +2

    def test_light_on_hare(self):
        sv = SyllableVector(stress=0, height=3, weight=HALVES)
        gs = GridStep(position=0, holy_name=HolyName.HARE, mode="DHARMA", beat=KSETRAJNA)
        score = alignment_score(sv, gs)
        assert score >= KSETRAJNA  # light + Hare = +1

    def test_high_vowel_on_hare(self):
        sv = SyllableVector(stress=0, height=QUARTERS, weight=2)
        gs = GridStep(position=0, holy_name=HolyName.HARE, mode="DHARMA", beat=KSETRAJNA)
        score = alignment_score(sv, gs)
        assert score >= KSETRAJNA  # high vowel + Hare = +1

    def test_low_vowel_on_krishna(self):
        sv = SyllableVector(stress=0, height=HALVES, weight=2)
        gs = GridStep(position=0, holy_name=HolyName.KRISHNA, mode="GENESIS", beat=KSETRAJNA)
        score = alignment_score(sv, gs)
        assert score >= KSETRAJNA  # low vowel + Krishna = +1

    def test_score_non_negative(self):
        sv = SyllableVector(stress=0, height=3, weight=2)
        for gs in build_mantra_grid():
            assert alignment_score(sv, gs) >= 0


# =============================================================================
# align_syllables_to_grid: syllable vectors → grid step indices
# =============================================================================


class TestAlignSyllablesToGrid:
    """align_syllables_to_grid: best-fit alignment onto 32-step grid."""

    def test_empty_returns_empty(self):
        assert align_syllables_to_grid(()) == ()

    def test_single_syllable(self):
        sv = (SyllableVector(stress=1, height=3, weight=2),)
        result = align_syllables_to_grid(sv)
        assert len(result) == 1
        assert 0 <= result[0] < 32

    def test_multi_syllable_count_matches(self):
        svs = (
            SyllableVector(stress=1, height=3, weight=2),
            SyllableVector(stress=0, height=4, weight=1),
            SyllableVector(stress=1, height=2, weight=3),
        )
        result = align_syllables_to_grid(svs)
        assert len(result) == 3

    def test_all_indices_within_grid(self):
        svs = tuple(SyllableVector(stress=i % 3, height=3, weight=2) for i in range(10))
        result = align_syllables_to_grid(svs)
        for idx in result:
            assert 0 <= idx < 32

    def test_deterministic(self):
        svs = (SyllableVector(1, 3, 2), SyllableVector(0, 4, 1))
        a = align_syllables_to_grid(svs)
        b = align_syllables_to_grid(svs)
        assert a == b

    def test_returns_tuple_of_ints(self):
        svs = (SyllableVector(1, 3, 2),)
        result = align_syllables_to_grid(svs)
        assert isinstance(result, tuple)
        for idx in result:
            assert isinstance(idx, int)

    def test_consecutive_indices_wrap(self):
        """Multi-syllable alignment uses consecutive grid positions (with wrapping)."""
        svs = tuple(SyllableVector(stress=0, height=3, weight=2) for _ in range(35))
        result = align_syllables_to_grid(svs)
        assert len(result) == 35
        # All indices valid even when exceeding grid size
        for idx in result:
            assert 0 <= idx < 32
