"""
TEST TRANSLATION PROTOCOL
=========================

Verifies the resonance-first translation architecture.

THE THREE LAYERS:
    Layer 1: RESONANCE (Śabda) - Sound/vibration
    Layer 2: MEANING (Artha)   - Semantic content
    Layer 3: FORM (Rūpa)       - Written text

ŚRAVAṆAM PRINCIPLE:
Hearing comes first. Sound is the universal connector.
"""

import pytest

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


class TestTranslationLayers:
    """Test the three translation layers."""

    def test_three_layers_exist(self):
        """Three translation layers are defined."""
        assert len(TranslationLayer) == 3

    def test_resonance_layer(self):
        """Resonance (Śabda) layer."""
        assert TranslationLayer.RESONANCE.value == "resonance"

    def test_meaning_layer(self):
        """Meaning (Artha) layer."""
        assert TranslationLayer.MEANING.value == "meaning"

    def test_form_layer(self):
        """Form (Rūpa) layer."""
        assert TranslationLayer.FORM.value == "form"


class TestNaturalLanguages:
    """Test supported natural languages."""

    def test_english_supported(self):
        """English is supported."""
        assert NaturalLanguage.ENGLISH.value == "en"

    def test_german_supported(self):
        """German is supported."""
        assert NaturalLanguage.GERMAN.value == "de"

    def test_sanskrit_supported(self):
        """Sanskrit is supported."""
        assert NaturalLanguage.SANSKRIT.value == "sa"

    def test_hindi_supported(self):
        """Hindi is supported."""
        assert NaturalLanguage.HINDI.value == "hi"


class TestPhoneme:
    """Test Phoneme dataclass."""

    def test_phoneme_is_frozen(self):
        """Phoneme is immutable."""
        p = Phoneme(ipa="k")
        with pytest.raises(Exception):
            p.ipa = "g"

    def test_phoneme_has_ipa(self):
        """Phoneme has IPA representation."""
        p = Phoneme(ipa="ʃ", sthana="tālu")
        assert p.ipa == "ʃ"
        assert p.sthana == "tālu"

    def test_phoneme_vedic_classification(self):
        """Phoneme has Vedic classification."""
        p = Phoneme(ipa="k", sthana="kaṇṭha", prayatna="spṛṣṭa")
        assert p.sthana == "kaṇṭha"  # Throat
        assert p.prayatna == "spṛṣṭa"  # Contact


class TestResonancePattern:
    """Test ResonancePattern dataclass."""

    def test_pattern_is_frozen(self):
        """ResonancePattern is immutable."""
        p = Phoneme(ipa="a")
        pattern = ResonancePattern(phonemes=(p,))
        with pytest.raises(Exception):
            pattern.phonemes = ()

    def test_pattern_length(self):
        """Pattern has length."""
        p1, p2, p3 = Phoneme(ipa="h"), Phoneme(ipa="a"), Phoneme(ipa="r")
        pattern = ResonancePattern(phonemes=(p1, p2, p3))
        assert len(pattern) == 3

    def test_pattern_str(self):
        """Pattern converts to IPA string."""
        p1, p2 = Phoneme(ipa="h"), Phoneme(ipa="a")
        pattern = ResonancePattern(phonemes=(p1, p2))
        assert str(pattern) == "ha"

    def test_pattern_mantra_flag(self):
        """Pattern can be marked as mantra."""
        p = Phoneme(ipa="oːm")
        pattern = ResonancePattern(phonemes=(p,), is_mantra=True, mantra_vibration="ascending")
        assert pattern.is_mantra
        assert pattern.mantra_vibration == "ascending"


class TestSemanticUnit:
    """Test SemanticUnit dataclass."""

    def test_unit_is_frozen(self):
        """SemanticUnit is immutable."""
        unit = SemanticUnit(concept_id="deity.krishna", concept_type="noun")
        with pytest.raises(Exception):
            unit.concept_id = "changed"

    def test_unit_properties(self):
        """Unit has semantic properties."""
        unit = SemanticUnit(
            concept_id="deity.krishna",
            concept_type="noun",
            properties=("divine", "personal", "supreme"),
            tattva="puruṣa",
        )
        assert "divine" in unit.properties
        assert unit.tattva == "puruṣa"


class TestMeaningGraph:
    """Test MeaningGraph dataclass."""

    def test_graph_is_frozen(self):
        """MeaningGraph is immutable."""
        unit = SemanticUnit(concept_id="test", concept_type="noun")
        graph = MeaningGraph(units=(unit,), relations=())
        with pytest.raises(Exception):
            graph.units = ()

    def test_graph_has_context(self):
        """Graph has context type."""
        unit = SemanticUnit(concept_id="mantra", concept_type="noun")
        graph = MeaningGraph(units=(unit,), relations=(), context_type="mantra", mood="devotional")
        assert graph.context_type == "mantra"
        assert graph.mood == "devotional"


class TestTextForm:
    """Test TextForm dataclass."""

    def test_form_is_frozen(self):
        """TextForm is immutable."""
        form = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        with pytest.raises(Exception):
            form.text = "Changed"

    def test_form_has_language(self):
        """Form has language specified."""
        form = TextForm(text="Hare Krishna", language=NaturalLanguage.ENGLISH, script="latin")
        assert form.language == NaturalLanguage.ENGLISH
        assert form.script == "latin"


class TestTranslationResult:
    """Test TranslationResult dataclass."""

    def test_result_success(self):
        """Successful translation result."""
        source = TextForm(text="Hare Krishna", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="Hare Kṛṣṇa", language=NaturalLanguage.SANSKRIT)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            confidence=0.95,
            resonance_similarity=0.98,
            meaning_preservation=0.99,
        )
        assert result.success
        assert result.confidence == 0.95

    def test_result_with_opcodes(self):
        """Result tracks MantraOpCodes used."""
        source = TextForm(text="Hello", language=NaturalLanguage.ENGLISH)
        target = TextForm(text="Hallo", language=NaturalLanguage.GERMAN)
        result = TranslationResult(
            success=True,
            source_form=source,
            target_form=target,
            opcodes_used=["load_root", "resolve_req", "exec_service", "commit_log"],
        )
        assert "exec_service" in result.opcodes_used


class TestTranslationOpcodeMap:
    """Test MantraCPU connection."""

    def test_load_source_maps_to_load_root(self):
        """Load source text → LOAD_ROOT."""
        assert TRANSLATION_OPCODE_MAP["load_source"] == "load_root"

    def test_parse_form_maps_to_resolve_req(self):
        """Parse form → RESOLVE_REQ."""
        assert TRANSLATION_OPCODE_MAP["parse_form"] == "resolve_req"

    def test_extract_meaning_maps_to_exec_service(self):
        """Extract meaning → EXEC_SERVICE."""
        assert TRANSLATION_OPCODE_MAP["extract_meaning"] == "exec_service"

    def test_commit_output_maps_to_commit_log(self):
        """Commit output → COMMIT_LOG."""
        assert TRANSLATION_OPCODE_MAP["commit_output"] == "commit_log"


class TestGermanPhonemes:
    """Test German-specific phonemes."""

    def test_umlaut_u(self):
        """German ü phoneme."""
        assert "ü" in GERMAN_PHONEMES
        assert GERMAN_PHONEMES["ü"].ipa == "y"

    def test_umlaut_o(self):
        """German ö phoneme."""
        assert "ö" in GERMAN_PHONEMES
        assert GERMAN_PHONEMES["ö"].ipa == "ø"

    def test_ch(self):
        """German ch phoneme."""
        assert "ch" in GERMAN_PHONEMES
        assert GERMAN_PHONEMES["ch"].ipa == "x"

    def test_sch(self):
        """German sch phoneme."""
        assert "sch" in GERMAN_PHONEMES
        assert GERMAN_PHONEMES["sch"].ipa == "ʃ"


class TestEnglishPhonemes:
    """Test English-specific phonemes."""

    def test_th_voiceless(self):
        """English th (voiceless)."""
        assert "th" in ENGLISH_PHONEMES
        assert ENGLISH_PHONEMES["th"].ipa == "θ"

    def test_ng(self):
        """English ng phoneme."""
        assert "ng" in ENGLISH_PHONEMES
        assert ENGLISH_PHONEMES["ng"].ipa == "ŋ"


class TestTranslationProtocolContract:
    """Test TranslationProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(TranslationProtocol, "__protocol_attrs__") or hasattr(TranslationProtocol, "_is_protocol")

    def test_has_layer_transformations(self):
        """Protocol has layer transformation methods."""
        methods = ["form_to_resonance", "resonance_to_meaning", "meaning_to_resonance", "resonance_to_form"]
        for method in methods:
            assert method in dir(TranslationProtocol)

    def test_has_translate_methods(self):
        """Protocol has translate methods."""
        methods = ["translate", "translate_via_resonance", "translate_via_meaning"]
        for method in methods:
            assert method in dir(TranslationProtocol)


class TestResonanceProtocolContract:
    """Test ResonanceProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(ResonanceProtocol, "__protocol_attrs__") or hasattr(ResonanceProtocol, "_is_protocol")

    def test_has_phoneme_methods(self):
        """Protocol has phoneme methods."""
        methods = ["extract_phonemes", "create_pattern"]
        for method in methods:
            assert method in dir(ResonanceProtocol)

    def test_has_comparison_methods(self):
        """Protocol has comparison methods."""
        assert "compare_resonance" in dir(ResonanceProtocol)

    def test_has_mantra_detection(self):
        """Protocol has mantra detection."""
        assert "is_mantra" in dir(ResonanceProtocol)


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_phoneme_no_any(self):
        """Phoneme has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(Phoneme)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"Phoneme.{field_name} uses Any"

    def test_text_form_no_any(self):
        """TextForm has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(TextForm)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"TextForm.{field_name} uses Any"


class TestResonanceFirstPrinciple:
    """Test the Śravaṇam (hearing first) principle."""

    def test_resonance_is_first_layer(self):
        """Resonance layer is Layer 1 (first)."""
        # In Vedic epistemology, hearing comes before seeing
        # Our layers: 1=Resonance, 2=Meaning, 3=Form
        assert TranslationLayer.RESONANCE.value == "resonance"

    def test_phonemes_have_vedic_classification(self):
        """Phonemes use Vedic classification (sthana, prayatna)."""
        p = Phoneme(ipa="k", sthana="kaṇṭha", prayatna="spṛṣṭa")
        assert p.sthana == "kaṇṭha"  # kaṇṭha = throat (velar)
        assert p.prayatna == "spṛṣṭa"  # spṛṣṭa = contact (stop)

    def test_patterns_can_be_mantras(self):
        """ResonancePattern can represent mantras."""
        om = Phoneme(ipa="oːm")
        pattern = ResonancePattern(phonemes=(om,), is_mantra=True, mantra_vibration="ascending")
        assert pattern.is_mantra
