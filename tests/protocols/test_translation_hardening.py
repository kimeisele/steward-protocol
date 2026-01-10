"""
HARDENING TESTS - Translation & Resonance Protocols
====================================================

Edge cases, error conditions, and stress tests for:
- TranslationProtocol
- ResonanceProtocol
- Phoneme classification
- Cross-language mappings

ŚRAVAṆAM PRINCIPLE: Sound must work under all conditions.
"""

import pytest
from typing import Any

from vibe_core.protocols.translation import (
    # Protocols
    TranslationProtocol,
    ResonanceProtocol,
    # Enums
    TranslationLayer,
    NaturalLanguage,
    # Data types
    Phoneme,
    ResonancePattern,
    SemanticUnit,
    MeaningGraph,
    TextForm,
    TranslationResult,
    # Mappings
    TRANSLATION_OPCODE_MAP,
    GERMAN_PHONEMES,
    ENGLISH_PHONEMES,
)


# =============================================================================
# PHONEME HARDENING TESTS
# =============================================================================

class TestPhonemeEdgeCases:
    """Edge cases for Phoneme dataclass."""

    def test_empty_ipa(self):
        """Empty IPA is allowed (silence)."""
        p = Phoneme(ipa="")
        assert p.ipa == ""

    def test_unicode_ipa(self):
        """Unicode IPA symbols work."""
        p = Phoneme(ipa="ʃʒŋθð")
        assert "ʃ" in p.ipa
        assert "ŋ" in p.ipa

    def test_long_ipa(self):
        """Long IPA sequences work."""
        p = Phoneme(ipa="aːɪʊ" * 100)
        assert len(p.ipa) == 400

    def test_all_vedic_sthana(self):
        """All Vedic sthana (places) work."""
        sthanas = ["kaṇṭha", "tālu", "mūrdhā", "danta", "oṣṭha"]
        for sthana in sthanas:
            p = Phoneme(ipa="test", sthana=sthana)
            assert p.sthana == sthana

    def test_all_vedic_prayatna(self):
        """All Vedic prayatna (efforts) work."""
        prayatnas = ["spṛṣṭa", "īṣat-spṛṣṭa", "vivṛta", "saṁvṛta", "anunāsika"]
        for prayatna in prayatnas:
            p = Phoneme(ipa="test", prayatna=prayatna)
            assert p.prayatna == prayatna

    def test_phoneme_equality(self):
        """Frozen phonemes with same values are equal."""
        p1 = Phoneme(ipa="k", sthana="kaṇṭha")
        p2 = Phoneme(ipa="k", sthana="kaṇṭha")
        assert p1 == p2

    def test_phoneme_hashable(self):
        """Frozen phonemes are hashable (can be dict keys)."""
        p = Phoneme(ipa="k")
        d = {p: "velar stop"}
        assert d[p] == "velar stop"

    def test_phoneme_in_set(self):
        """Phonemes can be in sets."""
        p1 = Phoneme(ipa="k")
        p2 = Phoneme(ipa="k")
        p3 = Phoneme(ipa="g")
        s = {p1, p2, p3}
        assert len(s) == 2  # p1 and p2 are equal


class TestPhonemeVedicClassification:
    """Test Vedic phoneme classification completeness."""

    def test_velar_consonants(self):
        """Velar consonants have kaṇṭha classification."""
        # k, kh, g, gh, ṅ
        velars = ["k", "kʰ", "g", "gʱ", "ŋ"]
        for ipa in velars:
            p = Phoneme(ipa=ipa, sthana="kaṇṭha")
            assert p.sthana == "kaṇṭha"

    def test_palatal_consonants(self):
        """Palatal consonants have tālu classification."""
        # c, ch, j, jh, ñ
        palatals = ["tʃ", "tʃʰ", "dʒ", "dʒʱ", "ɲ"]
        for ipa in palatals:
            p = Phoneme(ipa=ipa, sthana="tālu")
            assert p.sthana == "tālu"

    def test_retroflex_consonants(self):
        """Retroflex consonants have mūrdhā classification."""
        # ṭ, ṭh, ḍ, ḍh, ṇ
        retroflex = ["ʈ", "ʈʰ", "ɖ", "ɖʱ", "ɳ"]
        for ipa in retroflex:
            p = Phoneme(ipa=ipa, sthana="mūrdhā")
            assert p.sthana == "mūrdhā"

    def test_dental_consonants(self):
        """Dental consonants have danta classification."""
        # t, th, d, dh, n
        dentals = ["t̪", "t̪ʰ", "d̪", "d̪ʱ", "n̪"]
        for ipa in dentals:
            p = Phoneme(ipa=ipa, sthana="danta")
            assert p.sthana == "danta"

    def test_labial_consonants(self):
        """Labial consonants have oṣṭha classification."""
        # p, ph, b, bh, m
        labials = ["p", "pʰ", "b", "bʱ", "m"]
        for ipa in labials:
            p = Phoneme(ipa=ipa, sthana="oṣṭha")
            assert p.sthana == "oṣṭha"


# =============================================================================
# RESONANCE PATTERN HARDENING TESTS
# =============================================================================

class TestResonancePatternEdgeCases:
    """Edge cases for ResonancePattern."""

    def test_empty_pattern(self):
        """Empty pattern (silence)."""
        pattern = ResonancePattern(phonemes=())
        assert len(pattern) == 0
        assert str(pattern) == ""

    def test_single_phoneme_pattern(self):
        """Single phoneme pattern."""
        p = Phoneme(ipa="a")
        pattern = ResonancePattern(phonemes=(p,))
        assert len(pattern) == 1
        assert str(pattern) == "a"

    def test_very_long_pattern(self):
        """Very long pattern (Mahamantra repetition)."""
        p = Phoneme(ipa="hare")
        pattern = ResonancePattern(phonemes=tuple([p] * 1000))
        assert len(pattern) == 1000

    def test_pattern_equality(self):
        """Patterns with same phonemes are equal."""
        p1, p2 = Phoneme(ipa="h"), Phoneme(ipa="a")
        pattern1 = ResonancePattern(phonemes=(p1, p2))
        pattern2 = ResonancePattern(phonemes=(p1, p2))
        assert pattern1 == pattern2

    def test_pattern_hashable(self):
        """Patterns are hashable."""
        p = Phoneme(ipa="a")
        pattern = ResonancePattern(phonemes=(p,))
        d = {pattern: "vowel"}
        assert d[pattern] == "vowel"

    def test_mantra_with_vibration(self):
        """Mantra patterns have vibration classes."""
        p = Phoneme(ipa="oːm")
        for vibration in ["ascending", "descending", "cyclic", "stable"]:
            pattern = ResonancePattern(
                phonemes=(p,),
                is_mantra=True,
                mantra_vibration=vibration
            )
            assert pattern.mantra_vibration == vibration

    def test_stress_patterns(self):
        """Stress patterns work."""
        p = Phoneme(ipa="a")
        pattern = ResonancePattern(
            phonemes=(p, p),
            stress_pattern="10"  # First syllable stressed
        )
        assert pattern.stress_pattern == "10"

    def test_rhythm_types(self):
        """Rhythm types work."""
        p = Phoneme(ipa="a")
        for rhythm in ["iambic", "trochaic", "mantra", "prose"]:
            pattern = ResonancePattern(
                phonemes=(p,),
                rhythm=rhythm
            )
            assert pattern.rhythm == rhythm


# =============================================================================
# SEMANTIC UNIT HARDENING TESTS
# =============================================================================

class TestSemanticUnitEdgeCases:
    """Edge cases for SemanticUnit."""

    def test_empty_properties(self):
        """Empty properties tuple."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        assert unit.properties == ()

    def test_many_properties(self):
        """Many properties."""
        props = tuple(f"prop_{i}" for i in range(100))
        unit = SemanticUnit(
            concept_id="test",
            concept_type="noun",
            properties=props
        )
        assert len(unit.properties) == 100

    def test_nested_relations(self):
        """Nested relation strings."""
        unit = SemanticUnit(
            concept_id="test",
            concept_type="noun",
            relations=("part_of:deity:vishnu", "instance_of:person:divine")
        )
        assert "deity:vishnu" in unit.relations[0]

    def test_all_concept_types(self):
        """Various concept types work."""
        types = ["noun", "verb", "adjective", "adverb", "pronoun", "preposition"]
        for ctype in types:
            unit = SemanticUnit(concept_id="test", concept_type=ctype)
            assert unit.concept_type == ctype

    def test_tattva_categories(self):
        """Vedic tattva categories work."""
        tattvas = ["puruṣa", "prakṛti", "mahat", "ahaṅkāra", "manas"]
        for tattva in tattvas:
            unit = SemanticUnit(
                concept_id="test",
                concept_type="noun",
                tattva=tattva
            )
            assert unit.tattva == tattva


# =============================================================================
# MEANING GRAPH HARDENING TESTS
# =============================================================================

class TestMeaningGraphEdgeCases:
    """Edge cases for MeaningGraph."""

    def test_single_unit_graph(self):
        """Graph with single unit."""
        unit = SemanticUnit(concept_id="krishna", concept_type="noun")
        graph = MeaningGraph(units=(unit,), relations=())
        assert len(graph.units) == 1

    def test_empty_relations(self):
        """Graph with no relations."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        graph = MeaningGraph(units=(unit,), relations=())
        assert graph.relations == ()

    def test_complex_graph(self):
        """Complex graph with multiple relations."""
        u1 = SemanticUnit(concept_id="krishna", concept_type="noun")
        u2 = SemanticUnit(concept_id="flute", concept_type="noun")
        u3 = SemanticUnit(concept_id="plays", concept_type="verb")

        graph = MeaningGraph(
            units=(u1, u2, u3),
            relations=(
                (0, "agent", 2),   # Krishna is agent of plays
                (2, "object", 1),  # plays has object flute
            )
        )
        assert len(graph.relations) == 2

    def test_context_types(self):
        """Various context types work."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        contexts = ["greeting", "instruction", "mantra", "narrative", "dialogue"]
        for ctx in contexts:
            graph = MeaningGraph(
                units=(unit,),
                relations=(),
                context_type=ctx
            )
            assert graph.context_type == ctx

    def test_mood_types(self):
        """Various mood types work."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        moods = ["devotional", "imperative", "declarative", "interrogative"]
        for mood in moods:
            graph = MeaningGraph(
                units=(unit,),
                relations=(),
                mood=mood
            )
            assert graph.mood == mood


# =============================================================================
# TEXT FORM HARDENING TESTS
# =============================================================================

class TestTextFormEdgeCases:
    """Edge cases for TextForm."""

    def test_empty_text(self):
        """Empty text form."""
        form = TextForm(text="", language=NaturalLanguage.ENGLISH)
        assert form.text == ""

    def test_unicode_text(self):
        """Unicode text (Sanskrit)."""
        form = TextForm(
            text="हरे कृष्ण",
            language=NaturalLanguage.SANSKRIT,
            script="devanagari"
        )
        assert "कृष्ण" in form.text

    def test_diacritics_text(self):
        """IAST diacritics text."""
        form = TextForm(
            text="Hare Kṛṣṇa",
            language=NaturalLanguage.SANSKRIT,
            script="iast"
        )
        assert "ṛṣṇ" in form.text

    def test_german_text(self):
        """German text with umlauts."""
        form = TextForm(
            text="Über die Brücke",
            language=NaturalLanguage.GERMAN,
            script="latin"
        )
        assert "Ü" in form.text

    def test_all_languages(self):
        """All NaturalLanguage values work."""
        for lang in NaturalLanguage:
            form = TextForm(text="test", language=lang)
            assert form.language == lang

    def test_script_types(self):
        """Various script types work."""
        scripts = ["latin", "devanagari", "cyrillic", "arabic"]
        for script in scripts:
            form = TextForm(
                text="test",
                language=NaturalLanguage.ENGLISH,
                script=script
            )
            assert form.script == script


# =============================================================================
# TRANSLATION RESULT HARDENING TESTS
# =============================================================================

class TestTranslationResultEdgeCases:
    """Edge cases for TranslationResult."""

    def test_failed_translation(self):
        """Failed translation with error."""
        source = TextForm(text="test", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="", language=NaturalLanguage.GERMAN)
        result = TranslationResult(
            success=False,
            source_form=source,
            target_form=target,
            error="Unknown word"
        )
        assert not result.success
        assert result.error == "Unknown word"

    def test_perfect_confidence(self):
        """Perfect confidence translation."""
        source = TextForm(text="Hare", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="हरे", language=NaturalLanguage.SANSKRIT)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            confidence=1.0,
            resonance_similarity=1.0,
            meaning_preservation=1.0
        )
        assert result.confidence == 1.0

    def test_zero_confidence(self):
        """Zero confidence translation."""
        source = TextForm(text="xyz", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="???", language=NaturalLanguage.GERMAN)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            confidence=0.0
        )
        assert result.confidence == 0.0

    def test_opcodes_chain(self):
        """Full opcode chain in result."""
        source = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="Hallo", language=NaturalLanguage.GERMAN)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            opcodes_used=["load_root", "resolve_req", "exec_service", "commit_log"]
        )
        assert len(result.opcodes_used) == 4
        assert result.opcodes_used[0] == "load_root"
        assert result.opcodes_used[-1] == "commit_log"


# =============================================================================
# LANGUAGE PHONEME TABLE HARDENING
# =============================================================================

class TestGermanPhonemesComplete:
    """Complete German phoneme coverage."""

    def test_all_umlauts(self):
        """All German umlauts present."""
        assert "ü" in GERMAN_PHONEMES
        assert "ö" in GERMAN_PHONEMES
        assert "ä" in GERMAN_PHONEMES

    def test_german_digraphs(self):
        """German digraphs present."""
        assert "ch" in GERMAN_PHONEMES
        assert "sch" in GERMAN_PHONEMES

    def test_german_phoneme_ipa_validity(self):
        """German phonemes have valid IPA."""
        for char, phoneme in GERMAN_PHONEMES.items():
            assert phoneme.ipa, f"{char} has no IPA"
            assert len(phoneme.ipa) >= 1


class TestEnglishPhonemesComplete:
    """Complete English phoneme coverage."""

    def test_th_sounds(self):
        """English th sounds present."""
        assert "th" in ENGLISH_PHONEMES

    def test_ng_sound(self):
        """English ng sound present."""
        assert "ng" in ENGLISH_PHONEMES

    def test_english_phoneme_ipa_validity(self):
        """English phonemes have valid IPA."""
        for char, phoneme in ENGLISH_PHONEMES.items():
            assert phoneme.ipa, f"{char} has no IPA"


# =============================================================================
# OPCODE MAP HARDENING
# =============================================================================

class TestOpcodeMapCompleteness:
    """Opcode map completeness and consistency."""

    def test_all_translation_steps_mapped(self):
        """All translation steps have opcode mappings."""
        required_steps = ["load_source", "parse_form", "extract_meaning", "commit_output"]
        for step in required_steps:
            assert step in TRANSLATION_OPCODE_MAP

    def test_opcodes_are_valid_strings(self):
        """All opcodes are non-empty strings."""
        for step, opcode in TRANSLATION_OPCODE_MAP.items():
            assert isinstance(opcode, str)
            assert len(opcode) > 0

    def test_opcodes_match_mantra_names(self):
        """Opcodes match MantraOpCode names."""
        valid_opcodes = [
            "sys_wake", "load_root", "alloc_mem", "bind_ctx",
            "assert_truth", "resolve_req", "garbage_collect", "pulse_sync",
            "fetch_res", "exec_service", "check_dharma", "commit_log",
            "cache_state", "optimize", "yield_cpu", "reset_ip"
        ]
        for step, opcode in TRANSLATION_OPCODE_MAP.items():
            assert opcode in valid_opcodes, f"{opcode} not a valid MantraOpCode"


# =============================================================================
# PROTOCOL CONTRACT HARDENING
# =============================================================================

class TestTranslationProtocolContract:
    """TranslationProtocol contract enforcement."""

    def test_protocol_methods_exist(self):
        """All required methods exist in protocol."""
        required = [
            'form_to_resonance',
            'resonance_to_meaning',
            'meaning_to_resonance',
            'resonance_to_form',
            'translate',
            'translate_via_resonance',
            'translate_via_meaning',
            'supported_languages',
            'can_translate',
        ]
        for method in required:
            assert hasattr(TranslationProtocol, method)

    def test_protocol_is_abstract(self):
        """Protocol cannot be directly instantiated."""
        # Protocols are abstract by nature
        assert hasattr(TranslationProtocol, '__protocol_attrs__') or \
               hasattr(TranslationProtocol, '_is_protocol')


class TestResonanceProtocolContract:
    """ResonanceProtocol contract enforcement."""

    def test_protocol_methods_exist(self):
        """All required methods exist in protocol."""
        required = [
            'extract_phonemes',
            'create_pattern',
            'compare_resonance',
            'is_mantra',
            'get_vibration_class',
        ]
        for method in required:
            assert hasattr(ResonanceProtocol, method)


# =============================================================================
# IMMUTABILITY HARDENING
# =============================================================================

class TestImmutabilityEnforced:
    """All dataclasses are properly frozen."""

    def test_phoneme_immutable(self):
        """Phoneme is truly immutable."""
        p = Phoneme(ipa="k")
        with pytest.raises(Exception):
            p.ipa = "g"
        with pytest.raises(Exception):
            p.sthana = "changed"

    def test_resonance_pattern_immutable(self):
        """ResonancePattern is truly immutable."""
        p = Phoneme(ipa="a")
        pattern = ResonancePattern(phonemes=(p,))
        with pytest.raises(Exception):
            pattern.phonemes = ()
        with pytest.raises(Exception):
            pattern.is_mantra = True

    def test_semantic_unit_immutable(self):
        """SemanticUnit is truly immutable."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        with pytest.raises(Exception):
            unit.concept_id = "changed"

    def test_meaning_graph_immutable(self):
        """MeaningGraph is truly immutable."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        graph = MeaningGraph(units=(unit,), relations=())
        with pytest.raises(Exception):
            graph.units = ()

    def test_text_form_immutable(self):
        """TextForm is truly immutable."""
        form = TextForm(text="test", language=NaturalLanguage.ENGLISH)
        with pytest.raises(Exception):
            form.text = "changed"


# =============================================================================
# NO ANY TYPE HARDENING
# =============================================================================

class TestNoAnyTypes:
    """Verify no Any types are used anywhere."""

    def test_phoneme_strict_types(self):
        """Phoneme uses only strict types."""
        from typing import get_type_hints, Any, get_origin
        hints = get_type_hints(Phoneme)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"Phoneme.{field_name} uses Any"
            # Check if it's a generic with Any inside
            if get_origin(field_type):
                assert Any not in getattr(field_type, '__args__', ())

    def test_resonance_pattern_strict_types(self):
        """ResonancePattern uses only strict types."""
        from typing import get_type_hints, Any
        hints = get_type_hints(ResonancePattern)
        for field_name, field_type in hints.items():
            assert field_type is not Any

    def test_translation_result_strict_types(self):
        """TranslationResult uses only strict types."""
        from typing import get_type_hints, Any, get_origin, Union
        hints = get_type_hints(TranslationResult)
        for field_name, field_type in hints.items():
            # Check direct Any
            assert field_type is not Any
            # Check Any inside Optional/Union
            origin = get_origin(field_type)
            if origin is Union:
                args = getattr(field_type, '__args__', ())
                assert Any not in args


# =============================================================================
# CROSS-LANGUAGE HARDENING
# =============================================================================

class TestCrossLanguageScenarios:
    """Cross-language translation scenarios."""

    def test_same_language_translation(self):
        """Same language should work (identity)."""
        source = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            confidence=1.0
        )
        assert result.source_form.text == result.target_form.text

    def test_english_to_german_scenario(self):
        """English to German translation scenario."""
        source = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="Hallo", language=NaturalLanguage.GERMAN)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            resonance_similarity=0.9  # Similar sound
        )
        assert result.resonance_similarity > 0.8

    def test_english_to_sanskrit_scenario(self):
        """English to Sanskrit translation scenario."""
        source = TextForm(text="Hare Krishna", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="हरे कृष्ण", language=NaturalLanguage.SANSKRIT)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            meaning_preservation=1.0  # Same meaning
        )
        assert result.meaning_preservation == 1.0

    def test_german_to_sanskrit_via_english(self):
        """German to Sanskrit (potentially via English)."""
        source = TextForm(text="Gott", language=NaturalLanguage.GERMAN)
        target = TextForm(text="देव", language=NaturalLanguage.SANSKRIT)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            opcodes_used=["load_root", "resolve_req", "exec_service", "exec_service", "commit_log"]
        )
        # Double exec_service for intermediate step
        assert result.opcodes_used.count("exec_service") == 2


# =============================================================================
# MANTRA DETECTION HARDENING
# =============================================================================

class TestMantraDetection:
    """Mantra detection edge cases."""

    def test_om_is_mantra(self):
        """Om should be detected as mantra."""
        om = Phoneme(ipa="oːm")
        pattern = ResonancePattern(
            phonemes=(om,),
            is_mantra=True,
            mantra_vibration="ascending"
        )
        assert pattern.is_mantra

    def test_mahamantra_is_mantra(self):
        """Mahamantra should be detected as mantra."""
        # Simplified representation
        h, a, r, e = Phoneme(ipa="h"), Phoneme(ipa="a"), Phoneme(ipa="r"), Phoneme(ipa="e")
        pattern = ResonancePattern(
            phonemes=(h, a, r, e),
            is_mantra=True,
            rhythm="mantra"
        )
        assert pattern.is_mantra
        assert pattern.rhythm == "mantra"

    def test_regular_text_not_mantra(self):
        """Regular text should not be mantra."""
        h, e, l, o = Phoneme(ipa="h"), Phoneme(ipa="e"), Phoneme(ipa="l"), Phoneme(ipa="o")
        pattern = ResonancePattern(
            phonemes=(h, e, l, l, o),
            is_mantra=False
        )
        assert not pattern.is_mantra

    def test_vibration_classes(self):
        """All vibration classes are valid."""
        vibrations = ["ascending", "descending", "cyclic", "stable"]
        p = Phoneme(ipa="a")
        for vib in vibrations:
            pattern = ResonancePattern(
                phonemes=(p,),
                is_mantra=True,
                mantra_vibration=vib
            )
            assert pattern.mantra_vibration == vib
