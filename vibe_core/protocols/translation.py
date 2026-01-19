"""
TRANSLATION PROTOCOL - Resonance-First Translation
===================================================

"Śravaṇam (Hearing) comes first."

THE THREE LAYERS (Fractal):
    Layer 1: RESONANCE (Śabda)  - Sound/vibration pattern
    Layer 2: MEANING (Artha)     - Semantic content
    Layer 3: FORM (Rūpa)         - Written representation

WHY RESONANCE FIRST?
- Binary is acintya (hard to conceive)
- Sound is natural (we hear before we see)
- Mahamantra works through sound: śravaṇam kīrtanam viṣṇoḥ

TRANSLATION FLOW:
    Source (German) → Form → Resonance → Meaning → Resonance → Form → Target (English)
                              ↑                           ↑
                              └─── Universal Layer ───────┘

MANTRA CPU CONNECTION:
    Each translation step is a MantraOpCode operation.
    - LOAD_ROOT: Load source text
    - RESOLVE_REQ: Parse to resonance
    - EXEC_SERVICE: Transform meaning
    - COMMIT_LOG: Output target

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x47565ca1"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Protocol, Tuple, Union, runtime_checkable


# =============================================================================
# TRANSLATION LAYERS
# =============================================================================


class TranslationLayer(str, Enum):
    """The three layers of translation."""

    RESONANCE = "resonance"  # Śabda - Sound pattern (Layer 1)
    MEANING = "meaning"  # Artha - Semantic content (Layer 2)
    FORM = "form"  # Rūpa - Written form (Layer 3)


class NaturalLanguage(str, Enum):
    """Supported natural languages."""

    ENGLISH = "en"
    GERMAN = "de"
    SANSKRIT = "sa"
    HINDI = "hi"
    # Extensible...


# =============================================================================
# RESONANCE LAYER (Śabda) - THE UNIVERSAL CONNECTOR
# =============================================================================


@dataclass(frozen=True)
class Phoneme:
    """
    A single sound unit.

    This is the ATOMIC unit of resonance.
    All languages share phonemes (with variations).
    """

    ipa: str  # International Phonetic Alphabet
    frequency_hz: float = 0.0  # Approximate frequency
    duration_ms: float = 0.0  # Approximate duration

    # Vedic classification
    sthana: str = ""  # Place of articulation (kaṇṭha, tālu, etc.)
    prayatna: str = ""  # Effort (spṛṣṭa, īṣat-spṛṣṭa, etc.)


@dataclass(frozen=True)
class ResonancePattern:
    """
    A sequence of phonemes forming a sound pattern.

    This is the RESONANCE representation of text.
    Languages connect at this level.
    """

    phonemes: Tuple[Phoneme, ...]

    # Prosodic features
    stress_pattern: str = ""  # e.g., "10" for first syllable stressed
    rhythm: str = ""  # e.g., "iambic", "mantra"

    # Mantra properties
    is_mantra: bool = False
    mantra_vibration: str = ""  # e.g., "ascending", "descending"

    def __len__(self) -> int:
        return len(self.phonemes)

    def __str__(self) -> str:
        return "".join(p.ipa for p in self.phonemes)


# =============================================================================
# MEANING LAYER (Artha) - LANGUAGE-INDEPENDENT
# =============================================================================


@dataclass(frozen=True)
class SemanticUnit:
    """
    A unit of meaning (language-independent).

    This is what gets translated - not words, but MEANING.
    """

    concept_id: str  # Universal concept identifier
    concept_type: str  # noun, verb, adjective, etc.

    # Semantic properties
    properties: Tuple[str, ...] = ()  # e.g., ("divine", "personal")
    relations: Tuple[str, ...] = ()  # e.g., ("part_of:deity",)

    # Vedic classification (if applicable)
    tattva: str = ""  # Ontological category


@dataclass(frozen=True)
class MeaningGraph:
    """
    A graph of semantic units (meaning structure).

    This is the UNIVERSAL representation of meaning.
    All translations preserve this structure.
    """

    units: Tuple[SemanticUnit, ...]
    relations: Tuple[Tuple[int, str, int], ...]  # (from_idx, relation, to_idx)

    # Context
    context_type: str = ""  # e.g., "greeting", "instruction", "mantra"
    mood: str = ""  # e.g., "devotional", "imperative"


# =============================================================================
# FORM LAYER (Rūpa) - WRITTEN REPRESENTATION
# =============================================================================


@dataclass(frozen=True)
class TextForm:
    """
    Written form of text in a specific language.

    This is the SURFACE representation.
    """

    text: str
    language: NaturalLanguage
    script: str = "latin"  # latin, devanagari, etc.

    # Form properties
    word_count: int = 0
    character_count: int = 0


# =============================================================================
# TRANSLATION RESULT
# =============================================================================


@dataclass
class TranslationResult:
    """
    Result of a translation operation.

    Contains all three layers for transparency.
    """

    success: bool

    # The three layers
    source_form: TextForm
    target_form: TextForm
    resonance: Optional[ResonancePattern] = None
    meaning: Optional[MeaningGraph] = None

    # Metrics
    confidence: float = 0.0
    resonance_similarity: float = 0.0  # How similar the sounds are
    meaning_preservation: float = 0.0  # How much meaning was preserved

    # Mantra CPU trace
    opcodes_used: List[str] = field(default_factory=list)

    # Error info
    error: Optional[str] = None


# =============================================================================
# TRANSLATION PROTOCOL
# =============================================================================


@runtime_checkable
class TranslationProtocol(Protocol):
    """
    Protocol for resonance-first translation.

    THE FLOW:
    1. Form → Resonance (extract sound pattern)
    2. Resonance → Meaning (understand semantics)
    3. Meaning → Resonance (generate target sound)
    4. Resonance → Form (write in target language)

    MANTRA CPU:
    Each step is a MantraOpCode operation.
    """

    # =========================================================================
    # LAYER TRANSFORMATIONS
    # =========================================================================

    def form_to_resonance(self, form: TextForm) -> ResonancePattern:
        """
        Extract resonance (sound pattern) from written form.

        MantraOpCode: RESOLVE_REQ (parse)
        """
        ...

    def resonance_to_meaning(self, resonance: ResonancePattern) -> MeaningGraph:
        """
        Extract meaning from resonance.

        MantraOpCode: EXEC_SERVICE (process)
        """
        ...

    def meaning_to_resonance(self, meaning: MeaningGraph, target_lang: NaturalLanguage) -> ResonancePattern:
        """
        Generate target resonance from meaning.

        MantraOpCode: EXEC_SERVICE (generate)
        """
        ...

    def resonance_to_form(self, resonance: ResonancePattern, target_lang: NaturalLanguage) -> TextForm:
        """
        Write resonance to target form.

        MantraOpCode: COMMIT_LOG (output)
        """
        ...

    # =========================================================================
    # HIGH-LEVEL TRANSLATION
    # =========================================================================

    def translate(self, text: str, source_lang: NaturalLanguage, target_lang: NaturalLanguage) -> TranslationResult:
        """
        Translate text from source to target language.

        Full flow through all three layers.
        """
        ...

    def translate_via_resonance(
        self, text: str, source_lang: NaturalLanguage, target_lang: NaturalLanguage
    ) -> TranslationResult:
        """
        Translate emphasizing resonance preservation.

        Useful for mantras where SOUND matters most.
        """
        ...

    def translate_via_meaning(
        self, text: str, source_lang: NaturalLanguage, target_lang: NaturalLanguage
    ) -> TranslationResult:
        """
        Translate emphasizing meaning preservation.

        Useful for instructions where CONTENT matters most.
        """
        ...

    # =========================================================================
    # LANGUAGE SUPPORT
    # =========================================================================

    def supported_languages(self) -> List[NaturalLanguage]:
        """Get list of supported languages."""
        ...

    def can_translate(self, source_lang: NaturalLanguage, target_lang: NaturalLanguage) -> bool:
        """Check if translation pair is supported."""
        ...


# =============================================================================
# RESONANCE PROTOCOL (The Universal Connector)
# =============================================================================


@runtime_checkable
class ResonanceProtocol(Protocol):
    """
    Protocol for resonance (sound/vibration) operations.

    This is the UNIVERSAL layer where all languages connect.

    ŚRAVAṆAM PRINCIPLE:
    Hearing comes first. Sound is the primary reality.
    Binary is derived from vibration, not vice versa.
    """

    def extract_phonemes(self, text: str, language: NaturalLanguage) -> List[Phoneme]:
        """Extract phonemes from text."""
        ...

    def create_pattern(self, phonemes: List[Phoneme]) -> ResonancePattern:
        """Create resonance pattern from phonemes."""
        ...

    def compare_resonance(self, pattern1: ResonancePattern, pattern2: ResonancePattern) -> float:
        """
        Compare two resonance patterns.

        Returns similarity score (0.0 - 1.0).
        Higher = more similar sound.
        """
        ...

    def is_mantra(self, pattern: ResonancePattern) -> bool:
        """
        Detect if pattern is a mantra.

        Mantras have specific vibrational signatures.
        """
        ...

    def get_vibration_class(self, pattern: ResonancePattern) -> str:
        """
        Get the vibration class of a pattern.

        Classes: "ascending", "descending", "cyclic", "stable"
        """
        ...


# =============================================================================
# MANTRA CPU CONNECTION
# =============================================================================

# Translation operations map to MantraOpCodes
TRANSLATION_OPCODE_MAP: Dict[str, str] = {
    "load_source": "load_root",  # Load source text
    "parse_form": "resolve_req",  # Parse to resonance
    "extract_meaning": "exec_service",  # Process meaning
    "generate_target": "exec_service",  # Generate output
    "commit_output": "commit_log",  # Write result
}


# =============================================================================
# LANGUAGE-SPECIFIC PHONEME TABLES
# =============================================================================

# German-specific phonemes (partial)
GERMAN_PHONEMES: Dict[str, Phoneme] = {
    "ü": Phoneme(ipa="y", sthana="tālu", prayatna="saṁvṛta"),
    "ö": Phoneme(ipa="ø", sthana="tālu", prayatna="saṁvṛta"),
    "ä": Phoneme(ipa="ɛ", sthana="kaṇṭha", prayatna="vivṛta"),
    "ch": Phoneme(ipa="x", sthana="kaṇṭha", prayatna="īṣat-spṛṣṭa"),
    "sch": Phoneme(ipa="ʃ", sthana="tālu", prayatna="īṣat-spṛṣṭa"),
}

# English-specific phonemes (partial)
ENGLISH_PHONEMES: Dict[str, Phoneme] = {
    "th": Phoneme(ipa="θ", sthana="danta", prayatna="īṣat-spṛṣṭa"),
    "th_v": Phoneme(ipa="ð", sthana="danta", prayatna="īṣat-spṛṣṭa"),
    "ng": Phoneme(ipa="ŋ", sthana="kaṇṭha", prayatna="anunāsika"),
}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocols
    "TranslationProtocol",
    "ResonanceProtocol",
    # Enums
    "TranslationLayer",
    "NaturalLanguage",
    # Data types
    "Phoneme",
    "ResonancePattern",
    "SemanticUnit",
    "MeaningGraph",
    "TextForm",
    "TranslationResult",
    # Mappings
    "TRANSLATION_OPCODE_MAP",
    "GERMAN_PHONEMES",
    "ENGLISH_PHONEMES",
]
