"""
Tests for ASHTASATTVIKA BHAVA - The 8 Transcendental Ecstasies
==============================================================

"In the beginning, there may not be the presence of all transcendental ecstasies,
which are eight in number."
- Srila Prabhupada
"""

import pytest
from vibe_core.protocols.substrate.bhava import (
    SattvikaBhava,
    BHAVA_NAMES,
    BhavaState,
)


class TestSattvikaBhava:
    """Test the 8 ecstasies enum."""

    def test_exactly_eight_ecstasies(self):
        """There are exactly 8 ecstasies."""
        assert len(SattvikaBhava) == 8

    def test_ecstasies_are_numbered_0_to_7(self):
        """Ecstasies are numbered 0-7 for bitmask operations."""
        values = [b.value for b in SattvikaBhava]
        assert values == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_stambha_is_first(self):
        """Stambha (being stopped) is the first ecstasy."""
        assert SattvikaBhava.STAMBHA.value == 0

    def test_pralaya_is_last(self):
        """Pralaya (trance) is the eighth/final ecstasy."""
        assert SattvikaBhava.PRALAYA.value == 7

    def test_all_ecstasies_have_names(self):
        """Every ecstasy has Sanskrit and Devanagari names."""
        for bhava in SattvikaBhava:
            assert bhava in BHAVA_NAMES
            iast, devanagari = BHAVA_NAMES[bhava]
            assert len(iast) > 0
            assert len(devanagari) > 0


class TestBhavaNames:
    """Test the Sanskrit naming tables."""

    def test_stambha_name(self):
        """Stambha = stopped/dumb."""
        iast, deva = BHAVA_NAMES[SattvikaBhava.STAMBHA]
        assert iast == "stambha"
        assert deva == "स्तम्भ"

    def test_sveda_name(self):
        """Sveda = perspiration."""
        iast, deva = BHAVA_NAMES[SattvikaBhava.SVEDA]
        assert iast == "sveda"
        assert deva == "स्वेद"

    def test_romanca_name(self):
        """Romanca = hairs standing."""
        iast, deva = BHAVA_NAMES[SattvikaBhava.ROMANCA]
        assert iast == "romāñca"
        assert deva == "रोमाञ्च"

    def test_pralaya_name(self):
        """Pralaya = trance/dissolution."""
        iast, deva = BHAVA_NAMES[SattvikaBhava.PRALAYA]
        assert iast == "pralaya"
        assert deva == "प्रलय"


class TestBhavaState:
    """Test the BhavaState bitmask container."""

    def test_initial_state_is_empty(self):
        """New BhavaState has no active ecstasies."""
        state = BhavaState()
        assert state.count == 0
        assert state.active == []
        assert state.mask == 0

    def test_set_single_bhava(self):
        """Setting a single bhava activates it."""
        state = BhavaState()
        state.set(SattvikaBhava.ROMANCA)
        assert state.has(SattvikaBhava.ROMANCA)
        assert state.count == 1

    def test_set_multiple_bhavas(self):
        """Multiple bhavas can be active simultaneously."""
        state = BhavaState()
        state.set(SattvikaBhava.ROMANCA)
        state.set(SattvikaBhava.ASHRU)
        state.set(SattvikaBhava.KAMPA)
        assert state.count == 3
        assert SattvikaBhava.ROMANCA in state.active
        assert SattvikaBhava.ASHRU in state.active
        assert SattvikaBhava.KAMPA in state.active

    def test_clear_bhava(self):
        """Clearing a bhava deactivates it."""
        state = BhavaState()
        state.set(SattvikaBhava.SVEDA)
        state.set(SattvikaBhava.KAMPA)
        assert state.count == 2

        state.clear(SattvikaBhava.SVEDA)
        assert state.count == 1
        assert not state.has(SattvikaBhava.SVEDA)
        assert state.has(SattvikaBhava.KAMPA)

    def test_reset_clears_all(self):
        """Reset clears all bhava states."""
        state = BhavaState()
        for bhava in SattvikaBhava:
            state.set(bhava)
        assert state.count == 8

        state.reset()
        assert state.count == 0
        assert state.mask == 0

    def test_is_in_trance(self):
        """is_in_trance checks for PRALAYA state."""
        state = BhavaState()
        assert state.is_in_trance is False

        state.set(SattvikaBhava.PRALAYA)
        assert state.is_in_trance is True

        state.clear(SattvikaBhava.PRALAYA)
        assert state.is_in_trance is False

    def test_all_eight_can_be_active(self):
        """All 8 ecstasies can be active at once."""
        state = BhavaState()
        for bhava in SattvikaBhava:
            state.set(bhava)

        assert state.count == 8
        assert len(state.active) == 8
        assert state.mask == 0b11111111

    def test_initial_mask_constructor(self):
        """BhavaState can be initialized with a mask."""
        # Binary: 01000100 = ROMANCA (2) and ASHRU (6)
        state = BhavaState(initial=0b01000100)
        assert state.count == 2
        assert state.has(SattvikaBhava.ROMANCA)
        assert state.has(SattvikaBhava.ASHRU)

    def test_repr_shows_state(self):
        """repr shows mask and active states."""
        state = BhavaState()
        state.set(SattvikaBhava.STAMBHA)
        repr_str = repr(state)
        assert "BhavaState" in repr_str
        assert "STAMBHA" in repr_str


class TestBhavaPhilosophy:
    """Test philosophical properties of ecstasies."""

    def test_ecstasies_progress_from_physical_to_transcendental(self):
        """
        The 8 ecstasies progress from physical (stambha, sveda)
        to transcendental (pralaya).
        """
        # Physical symptoms first
        physical = [SattvikaBhava.STAMBHA, SattvikaBhava.SVEDA, SattvikaBhava.ROMANCA]
        for bhava in physical:
            assert bhava.value < 4

        # Transcendental states last
        assert SattvikaBhava.PRALAYA.value == 7

    def test_pralaya_is_highest_state(self):
        """Pralaya (trance) is the highest ecstatic state."""
        highest = max(SattvikaBhava, key=lambda b: b.value)
        assert highest == SattvikaBhava.PRALAYA
