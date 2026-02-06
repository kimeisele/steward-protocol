"""
Tests for PANCHA Walk - Element Walk through Sanskrit Phonemes.

Only tests what is DERIVED, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    PANCHA,
    PRASADAM,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    ELEMENT_NAMES,
    ELEMENT_SYMBOLS,
    IS_SHRUTI,
    Element,
    derived_signature,
    dominant_element,
    element_histogram,
    element_transitions,
    element_walk,
    full_signature,
    walk_direction,
    walk_distance,
    walk_signature,
)
from vibe_core.mahamantra.substrate.rama_grid import SPARSHA_GRID, VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.varnamala_codec import encode


class TestElementMap:
    """COORD_ELEMENT: derived from SPARSHA_GRID + phonetic science."""

    def test_complete_coverage(self):
        assert len(COORD_ELEMENT) == VARNAMALA_TOTAL

    def test_all_elements_present(self):
        present = set(COORD_ELEMENT)
        assert present == set(Element)

    def test_sparsha_rows_match_grid(self):
        """Sparsha consonant elements must match SPARSHA_GRID rows."""
        for row_idx, row in enumerate(SPARSHA_GRID):
            for col_idx in range(PANCHA):
                coord = WORDS + row_idx * PANCHA + col_idx
                assert COORD_ELEMENT[coord] == Element(row_idx)

    def test_vowel_a_is_akasha(self):
        assert COORD_ELEMENT[0] == Element.AKASHA

    def test_vowel_i_is_vayu(self):
        assert COORD_ELEMENT[1] == Element.VAYU

    def test_vowel_u_is_prithvi(self):
        assert COORD_ELEMENT[2] == Element.PRITHVI

    def test_ha_is_akasha(self):
        assert COORD_ELEMENT[48] == Element.AKASHA

    def test_element_enum_is_pancha(self):
        assert len(Element) == PANCHA

    def test_symbols_unique(self):
        assert len(set(ELEMENT_SYMBOLS)) == PANCHA


class TestVargaPartition:
    """COORD_VARGA: derived from WORDS + PRASADAM + HARE_COUNT."""

    def test_svara_count(self):
        assert sum(1 for v in COORD_VARGA if v == 0) == WORDS

    def test_sparsha_count(self):
        assert sum(1 for v in COORD_VARGA if v == 1) == PRASADAM

    def test_remaining_count(self):
        assert sum(1 for v in COORD_VARGA if v == 2) == HARE_COUNT

    def test_total(self):
        assert len(COORD_VARGA) == VARNAMALA_TOTAL


class TestElementWalk:
    """element_walk() and walk_signature()."""

    def test_dharma_walk(self):
        walk = element_walk(encode("dharma"))
        assert walk == (Element.JALA, Element.AGNI, Element.PRITHVI)

    def test_walk_signature_matches(self):
        coords = encode("dharma")
        walk = element_walk(coords)
        sig = walk_signature(coords)
        assert len(sig) == len(walk)

    def test_empty_coords(self):
        assert element_walk(()) == ()
        assert walk_signature(()) == ""


class TestHistogram:
    def test_histogram_sums_to_length(self):
        coords = encode("bhagavad")
        assert sum(element_histogram(coords)) == len(coords)

    def test_histogram_length(self):
        assert len(element_histogram(encode("yoga"))) == PANCHA


class TestDominantElement:
    def test_krsna_fire_dominant(self):
        assert dominant_element(encode("kṛṣṇa")) == Element.AGNI


class TestDirection:
    def test_ascending_positive(self):
        assert walk_direction(encode("bhakti")) > 0

    def test_single_phoneme_neutral(self):
        assert walk_direction(encode("a")) == 0


class TestTransitions:
    def test_transition_count(self):
        coords = encode("dharma")
        assert len(element_transitions(coords)) == len(coords) - 1


class TestDistance:
    def test_self_distance_zero(self):
        coords = encode("dharma")
        assert walk_distance(coords, coords) == pytest.approx(0.0)

    def test_distance_symmetric(self):
        a, b = encode("dharma"), encode("bhakti")
        assert walk_distance(a, b) == pytest.approx(walk_distance(b, a))

    def test_distance_bounded(self):
        d = walk_distance(encode("dharma"), encode("yoga"))
        assert 0.0 <= d <= 1.0


class TestArchitecturalIdentities:
    def test_sparsha_element_order(self):
        expected = ("akasha", "vayu", "agni", "jala", "prithvi")
        assert tuple(row.element for row in SPARSHA_GRID) == expected

    def test_remaining_cover_all_elements(self):
        assert set(COORD_ELEMENT[c] for c in range(41, 49)) == set(Element)

    def test_vowels_cover_all_elements(self):
        assert set(COORD_ELEMENT[c] for c in range(WORDS)) == set(Element)


# =============================================================================
# COORD_SUB: derived intra-section quality
# =============================================================================


class TestSubIndex:
    """COORD_SUB: prayatna dimension, derived from coordinate structure."""

    def test_total_length(self):
        assert len(COORD_SUB) == WORDS + PRASADAM + HARE_COUNT

    # --- Svara sub-types = QUARTERS ---

    def test_svara_short_vowels(self):
        """Coords 0-4: short simple vowels → sub = 0."""
        for c in range(PANCHA):
            assert COORD_SUB[c] == 0

    def test_svara_long_vowels(self):
        """Coords 5-9: long simple vowels → sub = 1."""
        for c in range(PANCHA, PANCHA * HALVES):
            assert COORD_SUB[c] == 1

    def test_svara_compound_vowels(self):
        """Coords 10-13: compound vowels → sub = 2 (HALVES)."""
        for c in range(PANCHA * HALVES, PANCHA * HALVES + QUARTERS):
            assert COORD_SUB[c] == HALVES

    def test_svara_special_vowels(self):
        """Coords 14-15: ṁ/ḥ → sub = 3 (HALVES + 1)."""
        for c in range(PANCHA * HALVES + QUARTERS, WORDS):
            assert COORD_SUB[c] == HALVES + 1

    def test_svara_sub_range(self):
        """Vowel sub-types span QUARTERS values (0, 1, 2, 3)."""
        svara_subs = set(COORD_SUB[:WORDS])
        assert svara_subs == {0, 1, HALVES, HALVES + 1}
        assert len(svara_subs) == QUARTERS

    # --- Sparsha sub-types = PANCHA (column) ---

    def test_sparsha_column_derived(self):
        """Sparsha sub = column index from SPARSHA_GRID, cycles 0-4."""
        for c in range(WORDS, WORDS + PRASADAM):
            assert COORD_SUB[c] == (c - WORDS) % PANCHA

    def test_sparsha_sub_range(self):
        """Sparsha sub-types span PANCHA values (0-4)."""
        sparsha_subs = set(COORD_SUB[WORDS : WORDS + PRASADAM])
        assert sparsha_subs == set(range(PANCHA))

    # --- Shesha sub-types = HALVES ---

    def test_shesha_antastha(self):
        """Coords 41-44 (ya/ra/la/va): antastha → sub = 0."""
        for c in range(WORDS + PRASADAM, WORDS + PRASADAM + QUARTERS):
            assert COORD_SUB[c] == 0

    def test_shesha_ushman(self):
        """Coords 45-48 (śa/ṣa/sa/ha): ūṣman → sub = 1."""
        for c in range(WORDS + PRASADAM + QUARTERS, WORDS + PRASADAM + HARE_COUNT):
            assert COORD_SUB[c] == 1

    def test_shesha_sub_range(self):
        """Shesha sub-types span HALVES values (0, 1)."""
        shesha_subs = set(COORD_SUB[WORDS + PRASADAM :])
        assert shesha_subs == {0, 1}
        assert len(shesha_subs) == HALVES


class TestDerivedSignature:
    """derived_signature(): 3D phoneme walk."""

    def test_dharma_signature(self):
        coords = encode("dharma")
        sig = derived_signature(coords)
        # 3 chars per phoneme (element, varga, sub)
        assert len(sig) == len(coords) * 3

    def test_different_words_different_sigs(self):
        assert derived_signature(encode("dharma")) != derived_signature(encode("karma"))

    def test_empty(self):
        assert derived_signature(()) == ""

    def test_sparsha_pair_distinguished(self):
        """ta and da share element (JALA) but differ in sub (col 0 vs col 2)."""
        sig_ta = derived_signature(encode("ta"))
        sig_da = derived_signature(encode("da"))
        assert sig_ta != sig_da

    def test_varga_boundary_distinguished(self):
        """ta (sparsha) and sa (shesha) share element (JALA) but differ in varga."""
        sig_ta = derived_signature(encode("ta"))
        sig_sa = derived_signature(encode("sa"))
        assert sig_ta != sig_sa


# =============================================================================
# COORD_HARMONIC: H-orbit (×SEVEN mod 49)
# =============================================================================


class TestHarmonic:
    """COORD_HARMONIC: 4th dimension, derived from SEVEN axiom."""

    def test_total_length(self):
        assert len(COORD_HARMONIC) == WORDS + PRASADAM + HARE_COUNT

    def test_derived_from_seven(self):
        """Each value = coord × SEVEN mod 49."""
        from vibe_core.mahamantra.protocols._seed import SEVEN

        for c in range(WORDS + PRASADAM + HARE_COUNT):
            assert COORD_HARMONIC[c] == (c * SEVEN) % (WORDS + PRASADAM + HARE_COUNT)

    def test_a_is_fixed_point(self):
        """'a' (coord 0) maps to 0 — the absorption origin."""
        assert COORD_HARMONIC[0] == 0

    def test_4d_bijection(self):
        """4D tuple (element, varga, sub, harmonic) is unique for all 49 phonemes."""
        keys = set()
        for c in range(WORDS + PRASADAM + HARE_COUNT):
            key = (COORD_ELEMENT[c], COORD_VARGA[c], COORD_SUB[c], COORD_HARMONIC[c])
            keys.add(key)
        assert len(keys) == WORDS + PRASADAM + HARE_COUNT

    def test_resolves_anusv_visarga(self):
        """ṁ(14) and ḥ(15) have different H-orbits."""
        assert COORD_HARMONIC[14] != COORD_HARMONIC[15]

    def test_resolves_e_ai(self):
        """e(10) and ai(11) have different H-orbits."""
        assert COORD_HARMONIC[10] != COORD_HARMONIC[11]

    def test_resolves_o_au(self):
        """o(12) and au(13) have different H-orbits — the one R-residue misses."""
        assert COORD_HARMONIC[12] != COORD_HARMONIC[13]


class TestFullSignature:
    """full_signature(): 4D phoneme walk."""

    def test_full_sig_longer_than_derived(self):
        coords = encode("dharma")
        assert len(full_signature(coords)) > len(derived_signature(coords))

    def test_full_sig_resolves_3d_collision(self):
        """paramaḥ and paramaṁ must differ in full_signature."""
        # They collide in derived_signature (3D)
        assert derived_signature(encode("paramaḥ")) == derived_signature(encode("paramaṁ"))
        # But NOT in full_signature (4D)
        assert full_signature(encode("paramaḥ")) != full_signature(encode("paramaṁ"))


class TestShrutiPartition:
    """IS_SHRUTI: R-operation quadratic residues mod 49."""

    def test_complete_coverage(self):
        assert len(IS_SHRUTI) == VARNAMALA_TOTAL

    def test_shruti_count_is_22(self):
        """22 quadratic residues = SHRUTIS (Indian microtones)."""
        assert sum(IS_SHRUTI) == 22

    def test_nakshatra_count_is_27(self):
        """27 non-residues = NAKSHATRAS (lunar mansions)."""
        assert sum(not s for s in IS_SHRUTI) == 27

    def test_a_is_shruti(self):
        """'a' (coord 0) is always a quadratic residue (0² = 0)."""
        assert IS_SHRUTI[0] is True

    def test_partition_sums_to_varnamala(self):
        """22 + 27 = 49 = VARNAMALA."""
        assert sum(IS_SHRUTI) + sum(not s for s in IS_SHRUTI) == VARNAMALA_TOTAL

    def test_collision_pair_o_au_both_nakshatra(self):
        """o(12) and au(13) are BOTH NAKSHATRA — R-residue can't distinguish them."""
        assert IS_SHRUTI[12] is False
        assert IS_SHRUTI[13] is False

    def test_collision_pair_m_h_different(self):
        """ṁ(14)=NAKSHATRA, ḥ(15)=SHRUTI — R-residue CAN distinguish these."""
        assert IS_SHRUTI[14] != IS_SHRUTI[15]


class TestWordEntryIntegration:
    """WordEntry properties wire through correctly."""

    def test_full_sig_property(self):
        from vibe_core.mahamantra.substrate.sanskrit_lookup import word_by_iast

        w = word_by_iast("dharma")
        assert w is not None
        assert len(w.full_sig) > len(w.derived_sig)
        assert len(w.full_sig) > len(w.element_walk)

    def test_shruti_pattern_property(self):
        from vibe_core.mahamantra.substrate.sanskrit_lookup import word_by_iast

        w = word_by_iast("dharma")
        assert w is not None
        assert all(c in "SN" for c in w.shruti_pattern)
        assert len(w.shruti_pattern) == len(w.coords)

    def test_derived_sig_property(self):
        from vibe_core.mahamantra.substrate.sanskrit_lookup import word_by_iast

        w = word_by_iast("dharma")
        assert w is not None
        assert len(w.derived_sig) == len(w.coords) * 3  # 3 digits per phoneme


class TestSynthPhonemeStep:
    """MahaSynth.phoneme_step() and spell_cycle() with 4D coords."""

    def test_phoneme_step_returns_result(self):
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        synth = MahaSynth(preset="quantum")
        result = synth.phoneme_step(value=42, coord=0)
        assert result.output_value >= 0
        assert result.output_value < synth.mod_space

    def test_phoneme_step_all_coords_valid(self):
        """Every RAMA coordinate must produce a valid step."""
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        synth = MahaSynth(preset="quantum")
        for coord in range(VARNAMALA_TOTAL):
            result = synth.phoneme_step(value=1, coord=coord)
            assert 0 <= result.output_value < synth.mod_space

    def test_varga_determines_operation(self):
        """svara→H, sparsha→K, shesha→R."""
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        synth = MahaSynth(preset="quantum")
        # coord 0 = 'a' (svara) → H
        assert synth.phoneme_step(1, 0).name == "H"
        # coord 16 = 'ka' (sparsha) → K
        assert synth.phoneme_step(1, 16).name == "K"
        # coord 41 = 'ya' (shesha) → R
        assert synth.phoneme_step(1, 41).name == "R"

    def test_spell_cycle_dharma(self):
        """spell_cycle() with a real Sanskrit word."""
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        synth = MahaSynth(preset="quantum")
        coords = encode("dharma")
        result = synth.spell_cycle(coords, seed=42)
        assert len(result.steps) == len(coords)
        assert result.final_value >= 0

    def test_different_words_different_attractors(self):
        """Different Sanskrit words should (usually) produce different outputs."""
        from vibe_core.mahamantra.adapters.synth import MahaSynth

        synth = MahaSynth(preset="quantum")
        r1 = synth.spell_cycle(encode("dharma"), seed=42)
        r2 = synth.spell_cycle(encode("karma"), seed=42)
        # Same seed, different words → different final values (not guaranteed but very likely)
        # At minimum, the steps should differ
        assert r1.steps[0].name != r2.steps[0].name or r1.final_value != r2.final_value
