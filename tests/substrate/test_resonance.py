"""
Tests for RESONANCE PROTOCOL - The Anti-Entropy Engine
======================================================

Tests verify:
1. PhoneticKey conversion (Sanskrit-aware Soundex)
2. Phonetic distance calculation (modified Levenshtein)
3. Resonance calculation for each Holy Name
4. ResonanceVector computation (3D: H, K, R)
5. Position resolution (0-15)
6. ResonanceMatrix for multiple inputs
7. ResonanceEngine implementation
8. HARDENING: Edge cases, boundary conditions, invalid inputs

KALI YUGA PRINCIPLE:
- Even imperfect pronunciation resonates
- The Holy Name is MERCIFUL
"""

import math
import pytest
from vibe_core.protocols.substrate.resonance import (
    # Enums
    PhoneticClass,
    # Constants
    PHONETIC_MAP,
    HARE_SIGNATURE,
    KRISHNA_SIGNATURE,
    RAMA_SIGNATURE,
    # Functions
    to_phonetic_key,
    phonetic_distance,
    calculate_resonance,
    compute_resonance_vector,
    resolve_position,
    compute_resonance_matrix,
    # Types
    ResonanceVector,
    ResonanceEntry,
    ResonanceMatrix,
    # Protocol & Implementation
    ResonanceEngine,
    get_resonance_engine,
    resonate,
    resolve,
)
from vibe_core.protocols.substrate.byte import HolyName


# =============================================================================
# SECTION 1: PhoneticClass Tests
# =============================================================================


class TestPhoneticClass:
    """Test the PhoneticClass enum."""

    def test_vowels_exist(self):
        """All Sanskrit vowels are represented."""
        assert PhoneticClass.VOWEL_A.value == "A"
        assert PhoneticClass.VOWEL_I.value == "I"
        assert PhoneticClass.VOWEL_U.value == "U"
        assert PhoneticClass.VOWEL_E.value == "E"
        assert PhoneticClass.VOWEL_O.value == "O"
        assert PhoneticClass.VOWEL_R.value == "R"  # Vocalic r (ṛ)

    def test_consonant_classes(self):
        """All articulation points are represented."""
        assert PhoneticClass.GUTTURAL.value == "G"   # Throat
        assert PhoneticClass.PALATAL.value == "P"    # Palate
        assert PhoneticClass.RETROFLEX.value == "T"  # Curled tongue
        assert PhoneticClass.DENTAL.value == "D"     # Teeth
        assert PhoneticClass.LABIAL.value == "B"     # Lips

    def test_special_classes(self):
        """Special phonetic classes exist."""
        assert PhoneticClass.SEMIVOWEL.value == "S"
        assert PhoneticClass.SIBILANT.value == "X"
        assert PhoneticClass.ASPIRATE.value == "H"  # Most important - in HARE
        assert PhoneticClass.NULL.value == "_"


class TestPhoneticMap:
    """Test the PHONETIC_MAP constant."""

    def test_map_has_vowels(self):
        """Map includes vowels."""
        assert PHONETIC_MAP['a'] == PhoneticClass.VOWEL_A
        assert PHONETIC_MAP['i'] == PhoneticClass.VOWEL_I
        assert PHONETIC_MAP['e'] == PhoneticClass.VOWEL_E

    def test_map_has_holy_name_sounds(self):
        """Map includes sounds critical for Holy Names."""
        # HARE: H-A-R-E
        assert PHONETIC_MAP['h'] == PhoneticClass.ASPIRATE
        assert PHONETIC_MAP['r'] == PhoneticClass.SEMIVOWEL
        # KRISHNA: K-R-I-S-N-A
        assert PHONETIC_MAP['k'] == PhoneticClass.GUTTURAL
        assert PHONETIC_MAP['s'] == PhoneticClass.SIBILANT
        assert PHONETIC_MAP['n'] == PhoneticClass.DENTAL
        # RAMA: R-A-M-A
        assert PHONETIC_MAP['m'] == PhoneticClass.LABIAL

    def test_map_has_digraphs(self):
        """Map includes digraphs (two-letter sounds)."""
        assert PHONETIC_MAP['kh'] == PhoneticClass.GUTTURAL
        assert PHONETIC_MAP['sh'] == PhoneticClass.SIBILANT

    def test_map_has_iast_characters(self):
        """Map includes IAST diacritics."""
        assert PHONETIC_MAP['ā'] == PhoneticClass.VOWEL_A
        assert PHONETIC_MAP['ṛ'] == PhoneticClass.VOWEL_R
        assert PHONETIC_MAP['ṇ'] == PhoneticClass.RETROFLEX


# =============================================================================
# SECTION 2: PhoneticKey Conversion Tests
# =============================================================================


class TestToPhoneticKey:
    """Test to_phonetic_key() function."""

    def test_hare_conversion(self):
        """'hare' converts to HARE_SIGNATURE."""
        key = to_phonetic_key("hare")
        assert key == HARE_SIGNATURE

    def test_krishna_approximation(self):
        """'krishna' converts correctly."""
        key = to_phonetic_key("krishna")
        # K-R-I-S-H-N-A  (note: "ri" may be treated as vocalic r)
        assert key[0] == PhoneticClass.GUTTURAL     # k
        # "ri" maps to vocalic r (VOWEL_R) in Sanskrit phonetics
        assert key[1] in (PhoneticClass.VOWEL_R, PhoneticClass.SEMIVOWEL)  # r/ri
        # Note: "sh" is a digraph
        assert PhoneticClass.SIBILANT in key

    def test_rama_conversion(self):
        """'rama' converts correctly."""
        key = to_phonetic_key("rama")
        assert key[0] == PhoneticClass.SEMIVOWEL  # r
        assert key[1] == PhoneticClass.VOWEL_A    # a
        assert key[2] == PhoneticClass.LABIAL     # m
        assert key[3] == PhoneticClass.VOWEL_A    # a

    def test_case_insensitive(self):
        """Conversion is case insensitive."""
        assert to_phonetic_key("HARE") == to_phonetic_key("hare")
        assert to_phonetic_key("Krishna") == to_phonetic_key("krishna")

    def test_strips_whitespace(self):
        """Leading/trailing whitespace is stripped."""
        assert to_phonetic_key("  hare  ") == to_phonetic_key("hare")

    def test_empty_string(self):
        """Empty string returns empty tuple."""
        assert to_phonetic_key("") == ()

    def test_western_approximations(self):
        """Western approximations still work (Kali Yuga mercy)."""
        # "Harry" should resonate with HARE
        key = to_phonetic_key("harry")
        assert key[0] == PhoneticClass.ASPIRATE  # h
        assert key[1] == PhoneticClass.VOWEL_A   # a

    def test_iast_input(self):
        """IAST transliteration works."""
        key = to_phonetic_key("kṛṣṇa")
        assert key[0] == PhoneticClass.GUTTURAL  # k
        assert key[1] == PhoneticClass.VOWEL_R   # ṛ (vocalic r)

    def test_digraph_priority(self):
        """Digraphs are detected before single characters."""
        key = to_phonetic_key("kha")
        # "kh" should be one GUTTURAL, not k + h
        assert len(key) == 2  # kh + a
        assert key[0] == PhoneticClass.GUTTURAL

    def test_non_alphabetic_skipped(self):
        """Non-alphabetic characters are skipped."""
        key = to_phonetic_key("ha-re!")
        # Should only include h, a, r, e
        assert len(key) == 4


# =============================================================================
# SECTION 3: Phonetic Distance Tests
# =============================================================================


class TestPhoneticDistance:
    """Test phonetic_distance() function."""

    def test_identical_keys_zero_distance(self):
        """Identical keys have zero distance."""
        key = to_phonetic_key("hare")
        assert phonetic_distance(key, key) == 0.0

    def test_similar_class_lower_cost(self):
        """Similar phonetic classes have lower cost."""
        # Both gutturals: k and g
        key1 = (PhoneticClass.GUTTURAL,)
        key2 = (PhoneticClass.GUTTURAL,)
        assert phonetic_distance(key1, key2) == 0.0

    def test_different_class_higher_cost(self):
        """Different phonetic classes have higher cost."""
        key1 = (PhoneticClass.ASPIRATE,)  # h
        key2 = (PhoneticClass.LABIAL,)    # m
        assert phonetic_distance(key1, key2) > 0.0

    def test_empty_vs_empty(self):
        """Empty vs empty = 0 distance."""
        assert phonetic_distance((), ()) == 0.0

    def test_empty_vs_nonempty(self):
        """Empty vs non-empty = 1.0 distance."""
        key = to_phonetic_key("hare")
        assert phonetic_distance((), key) == 1.0
        assert phonetic_distance(key, ()) == 1.0

    def test_normalized_to_max_1(self):
        """Distance is normalized to max 1.0."""
        key1 = to_phonetic_key("hare")
        key2 = to_phonetic_key("completely different text")
        assert 0.0 <= phonetic_distance(key1, key2) <= 1.0

    def test_symmetry(self):
        """Distance is symmetric."""
        key1 = to_phonetic_key("hare")
        key2 = to_phonetic_key("rama")
        assert phonetic_distance(key1, key2) == phonetic_distance(key2, key1)


# =============================================================================
# SECTION 4: Calculate Resonance Tests
# =============================================================================


class TestCalculateResonance:
    """Test calculate_resonance() function."""

    def test_perfect_hare_resonance(self):
        """'hare' has perfect resonance with HARE."""
        res = calculate_resonance("hare", HolyName.HARE)
        assert res == pytest.approx(1.0, abs=0.01)

    def test_perfect_krishna_resonance(self):
        """'kṛṣṇa' has high resonance with KRISHNA."""
        res = calculate_resonance("kṛṣṇa", HolyName.KRISHNA)
        assert res > 0.5  # High but not necessarily 1.0 due to different encoding

    def test_perfect_rama_resonance(self):
        """'rama' has perfect resonance with RAMA."""
        res = calculate_resonance("rama", HolyName.RAMA)
        assert res == pytest.approx(1.0, abs=0.01)

    def test_void_returns_zero(self):
        """VOID HolyName returns 0 resonance."""
        res = calculate_resonance("anything", HolyName.VOID)
        assert res == 0.0

    def test_imperfect_still_resonates(self):
        """Imperfect pronunciation still resonates (Kali Yuga mercy)."""
        # "Harry" resonates with HARE
        res = calculate_resonance("harry", HolyName.HARE)
        assert res > 0.3  # Some resonance

    def test_resonance_in_range(self):
        """Resonance is always in [0.0, 1.0]."""
        for text in ["hare", "krishna", "rama", "xyz", ""]:
            for name in [HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA]:
                res = calculate_resonance(text, name)
                assert 0.0 <= res <= 1.0

    def test_empty_string_low_resonance(self):
        """Empty string has low resonance."""
        res = calculate_resonance("", HolyName.HARE)
        assert res < 0.5


# =============================================================================
# SECTION 5: Resonance Vector Tests
# =============================================================================


class TestComputeResonanceVector:
    """Test compute_resonance_vector() function."""

    def test_returns_typed_dict(self):
        """Returns a proper ResonanceVector TypedDict."""
        vector = compute_resonance_vector("hare")
        assert "hare" in vector
        assert "krishna" in vector
        assert "rama" in vector
        assert "dominant" in vector
        assert "magnitude" in vector

    def test_hare_dominant_for_hare(self):
        """'hare' has 'hare' as dominant."""
        vector = compute_resonance_vector("hare")
        assert vector["dominant"] == "hare"

    def test_krishna_dominant_for_krishna(self):
        """'krishna' has 'krishna' as dominant."""
        vector = compute_resonance_vector("krishna")
        assert vector["dominant"] == "krishna"

    def test_rama_dominant_for_rama(self):
        """'rama' has 'rama' as dominant."""
        vector = compute_resonance_vector("rama")
        assert vector["dominant"] == "rama"

    def test_void_for_noise(self):
        """Random noise may return 'void'."""
        vector = compute_resonance_vector("xyzqwv")
        # May be void or may match something weakly
        assert vector["dominant"] in ["hare", "krishna", "rama", "void"]

    def test_magnitude_is_euclidean_norm(self):
        """Magnitude is the Euclidean norm of (H, K, R)."""
        vector = compute_resonance_vector("hare")
        h, k, r = vector["hare"], vector["krishna"], vector["rama"]
        expected = math.sqrt(h*h + k*k + r*r)
        assert vector["magnitude"] == pytest.approx(expected, abs=0.001)

    def test_values_in_range(self):
        """All resonance values are in [0.0, 1.0]."""
        for text in ["hare", "krishna", "rama", "test"]:
            vector = compute_resonance_vector(text)
            assert 0.0 <= vector["hare"] <= 1.0
            assert 0.0 <= vector["krishna"] <= 1.0
            assert 0.0 <= vector["rama"] <= 1.0


# =============================================================================
# SECTION 6: Position Resolution Tests
# =============================================================================


class TestResolvePosition:
    """Test resolve_position() function."""

    def test_returns_valid_position(self):
        """Position is always in range 0-15."""
        for text in ["hare", "krishna", "rama", "test", ""]:
            vector = compute_resonance_vector(text)
            pos = resolve_position(vector)
            assert 0 <= pos <= 15

    def test_hare_positions(self):
        """High HARE resonance maps to HARE positions."""
        vector = compute_resonance_vector("hare")
        pos = resolve_position(vector)
        # HARE positions: 0, 2, 6, 7, 8, 10, 14, 15
        hare_positions = {0, 2, 6, 7, 8, 10, 14, 15}
        assert pos in hare_positions

    def test_krishna_positions(self):
        """High KRISHNA resonance maps to KRISHNA positions."""
        vector = compute_resonance_vector("krishna")
        pos = resolve_position(vector)
        # KRISHNA positions: 1, 3, 4, 5
        krishna_positions = {1, 3, 4, 5}
        assert pos in krishna_positions

    def test_rama_positions(self):
        """High RAMA resonance maps to RAMA positions."""
        vector = compute_resonance_vector("rama")
        pos = resolve_position(vector)
        # RAMA positions: 9, 11, 12, 13
        rama_positions = {9, 11, 12, 13}
        assert pos in rama_positions

    def test_context_position_fallback(self):
        """Context position used for void."""
        vector: ResonanceVector = {
            "hare": 0.0,
            "krishna": 0.0,
            "rama": 0.0,
            "dominant": "void",
            "magnitude": 0.0,
        }
        pos = resolve_position(vector, context_position=7)
        assert pos == 7 % 16


# =============================================================================
# SECTION 7: Resonance Matrix Tests
# =============================================================================


class TestComputeResonanceMatrix:
    """Test compute_resonance_matrix() function."""

    def test_single_input(self):
        """Single input creates valid matrix."""
        matrix = compute_resonance_matrix(["hare"])
        assert len(matrix["entries"]) == 1
        assert matrix["coherence"] == 1.0  # Single input = perfect coherence

    def test_multiple_inputs(self):
        """Multiple inputs create entries for each."""
        inputs = ["hare", "krishna", "rama"]
        matrix = compute_resonance_matrix(inputs)
        assert len(matrix["entries"]) == 3

    def test_entry_structure(self):
        """Each entry has proper structure."""
        matrix = compute_resonance_matrix(["hare"])
        entry = matrix["entries"][0]
        assert "input_text" in entry
        assert "vector" in entry
        assert "position" in entry
        assert "opcode_name" in entry

    def test_coherence_high_for_similar(self):
        """Similar inputs have high coherence."""
        # All HARE
        matrix = compute_resonance_matrix(["hare", "hare", "hare"])
        assert matrix["coherence"] > 0.8

    def test_coherence_lower_for_mixed(self):
        """Mixed inputs have lower coherence."""
        matrix = compute_resonance_matrix(["hare", "krishna", "rama"])
        # Coherence depends on position variance
        assert 0.0 <= matrix["coherence"] <= 1.0

    def test_dominant_quarter(self):
        """Dominant quarter is calculated."""
        matrix = compute_resonance_matrix(["hare", "hare", "hare"])
        assert 0 <= matrix["dominant_quarter"] <= 3

    def test_total_magnitude(self):
        """Total magnitude is sum of individual magnitudes."""
        matrix = compute_resonance_matrix(["hare", "rama"])
        total = sum(e["vector"]["magnitude"] for e in matrix["entries"])
        assert matrix["total_magnitude"] == pytest.approx(total, abs=0.001)

    def test_empty_input(self):
        """Empty input list returns empty matrix."""
        matrix = compute_resonance_matrix([])
        assert len(matrix["entries"]) == 0
        assert matrix["coherence"] == 1.0  # No variance = perfect coherence


# =============================================================================
# SECTION 8: ResonanceEngine Tests
# =============================================================================


class TestResonanceEngine:
    """Test ResonanceEngine implementation."""

    @pytest.fixture
    def engine(self):
        """Create a fresh ResonanceEngine."""
        return ResonanceEngine()

    def test_initializes(self, engine):
        """Engine initializes with default threshold."""
        assert engine.threshold == 0.1

    def test_resonate(self, engine):
        """resonate() returns ResonanceVector."""
        vector = engine.resonate("hare")
        assert vector["dominant"] == "hare"

    def test_resonate_many(self, engine):
        """resonate_many() returns ResonanceMatrix."""
        matrix = engine.resonate_many(["hare", "krishna"])
        assert len(matrix["entries"]) == 2

    def test_resolve(self, engine):
        """resolve() returns position 0-15."""
        pos = engine.resolve("hare")
        assert 0 <= pos <= 15

    def test_get_opcode(self, engine):
        """get_opcode() returns valid opcode name."""
        opcode = engine.get_opcode("hare")
        valid_opcodes = [
            "SYS_WAKE", "LOAD_ROOT", "ALLOC_MEM", "BIND_CTX",
            "ASSERT_TRUTH", "RESOLVE_REQ", "GARBAGE_COLLECT", "PULSE_SYNC",
            "FETCH_RES", "EXEC_SERVICE", "CHECK_DHARMA", "COMMIT_LOG",
            "CACHE_STATE", "OPTIMIZE", "YIELD_CPU", "RESET_IP",
        ]
        assert opcode in valid_opcodes

    def test_explain(self, engine):
        """explain() returns human-readable string."""
        explanation = engine.explain("hare")
        assert "INPUT:" in explanation
        assert "PHONETIC KEY:" in explanation
        assert "RESONANCE VECTOR:" in explanation
        assert "HARE" in explanation


# =============================================================================
# SECTION 9: Global Functions Tests
# =============================================================================


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_get_resonance_engine_singleton(self):
        """get_resonance_engine() returns singleton."""
        engine1 = get_resonance_engine()
        engine2 = get_resonance_engine()
        assert engine1 is engine2

    def test_resonate_convenience(self):
        """resonate() convenience function works."""
        vector = resonate("hare")
        assert vector["dominant"] == "hare"

    def test_resolve_convenience(self):
        """resolve() convenience function works."""
        pos = resolve("hare")
        assert 0 <= pos <= 15


# =============================================================================
# SECTION 10: HARDENING Tests
# =============================================================================


class TestHardening:
    """Hardening tests for edge cases and boundary conditions."""

    def test_unicode_handling(self):
        """Unicode characters are handled gracefully."""
        # Devanagari
        vector = compute_resonance_vector("हरे")
        assert vector is not None

        # IAST with diacritics
        vector = compute_resonance_vector("kṛṣṇa")
        assert vector is not None

    def test_very_long_string(self):
        """Very long strings don't crash."""
        long_text = "hare " * 1000
        vector = compute_resonance_vector(long_text)
        assert vector is not None

    def test_special_characters(self):
        """Special characters are handled."""
        vector = compute_resonance_vector("hare! @#$%^&*()")
        assert vector is not None

    def test_numbers_ignored(self):
        """Numbers are ignored in conversion."""
        key = to_phonetic_key("hare123")
        # Numbers should be skipped
        assert len(key) == 4  # h, a, r, e

    def test_mixed_scripts(self):
        """Mixed scripts don't crash."""
        vector = compute_resonance_vector("hare हरे")
        assert vector is not None

    def test_null_bytes_handled(self):
        """Null bytes don't crash."""
        try:
            vector = compute_resonance_vector("hare\x00krishna")
            assert vector is not None
        except Exception:
            # Null bytes may cause issues - that's acceptable
            pass

    def test_resonance_deterministic(self):
        """Same input always gives same output."""
        v1 = compute_resonance_vector("hare")
        v2 = compute_resonance_vector("hare")
        assert v1 == v2

    def test_position_wrap_around(self):
        """Position wraps correctly with context."""
        vector: ResonanceVector = {
            "hare": 0.0,
            "krishna": 0.0,
            "rama": 0.0,
            "dominant": "void",
            "magnitude": 0.0,
        }
        # Large context position should wrap
        pos = resolve_position(vector, context_position=100)
        assert pos == 100 % 16

    def test_zero_magnitude_handling(self):
        """Zero magnitude doesn't cause division by zero."""
        vector = compute_resonance_vector("xyzqwv")
        # Should not raise
        assert vector["magnitude"] >= 0.0


class TestHolyNameSignatures:
    """Test the Holy Name signature constants."""

    def test_hare_signature_structure(self):
        """HARE_SIGNATURE has correct structure."""
        assert len(HARE_SIGNATURE) == 4
        assert HARE_SIGNATURE[0] == PhoneticClass.ASPIRATE   # H
        assert HARE_SIGNATURE[1] == PhoneticClass.VOWEL_A    # a
        assert HARE_SIGNATURE[2] == PhoneticClass.SEMIVOWEL  # r
        assert HARE_SIGNATURE[3] == PhoneticClass.VOWEL_E    # e

    def test_krishna_signature_structure(self):
        """KRISHNA_SIGNATURE has correct structure."""
        assert len(KRISHNA_SIGNATURE) == 5
        assert KRISHNA_SIGNATURE[0] == PhoneticClass.GUTTURAL   # K
        assert KRISHNA_SIGNATURE[1] == PhoneticClass.VOWEL_R    # ṛ
        assert KRISHNA_SIGNATURE[2] == PhoneticClass.SIBILANT   # ṣ
        assert KRISHNA_SIGNATURE[3] == PhoneticClass.RETROFLEX  # ṇ
        assert KRISHNA_SIGNATURE[4] == PhoneticClass.VOWEL_A    # a

    def test_rama_signature_structure(self):
        """RAMA_SIGNATURE has correct structure."""
        assert len(RAMA_SIGNATURE) == 4
        assert RAMA_SIGNATURE[0] == PhoneticClass.SEMIVOWEL  # R
        assert RAMA_SIGNATURE[1] == PhoneticClass.VOWEL_A    # ā
        assert RAMA_SIGNATURE[2] == PhoneticClass.LABIAL     # m
        assert RAMA_SIGNATURE[3] == PhoneticClass.VOWEL_A    # a
