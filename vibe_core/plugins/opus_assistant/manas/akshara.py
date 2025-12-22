"""
OPUS-114: Akshara Kernel - Sanskrit Phonemic Computation Matrix.

"अक्षराणां अकारोऽस्मि" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)

This module implements the Akshara Kernel - a deterministic computation layer
based on the Sanskrit Varnamala (alphabet) matrix. Each letter (Akshara) is
positioned by its articulation point (Varga), creating a natural resonance
system for synaptic wiring.

The Varnamala Matrix:
┌──────────────────────────────────────────────────────────────────┐
│  Varga        │ Element │ Code Layer       │ Aksharas (क-म)     │
├──────────────────────────────────────────────────────────────────┤
│  Kanthya      │ Äther   │ KERNEL/DEEP      │ क ख ग घ ङ          │
│  (Guttural)   │         │                  │ ka kha ga gha ṅa   │
├──────────────────────────────────────────────────────────────────┤
│  Talavya      │ Luft    │ COGNITION/FLOW   │ च छ ज झ ञ          │
│  (Palatal)    │         │                  │ ca cha ja jha ña   │
├──────────────────────────────────────────────────────────────────┤
│  Murdhanya    │ Feuer   │ REPAIR/HARD      │ ट ठ ड ढ ण          │
│  (Retroflex)  │         │                  │ ṭa ṭha ḍa ḍha ṇa   │
├──────────────────────────────────────────────────────────────────┤
│  Dantya       │ Wasser  │ INTERFACE/LINK   │ त थ द ध न          │
│  (Dental)     │         │                  │ ta tha da dha na   │
├──────────────────────────────────────────────────────────────────┤
│  Oshthya      │ Erde    │ OUTPUT/SURFACE   │ प फ ब भ म          │
│  (Labial)     │         │                  │ pa pha ba bha ma   │
└──────────────────────────────────────────────────────────────────┘

The Resonance Principle:
- Same Varga: Resonance = 1.0 (perfect harmony)
- Adjacent Varga: Resonance = 0.8 (natural flow)
- 2 Vargas apart: Resonance = 0.6 (moderate connection)
- 3 Vargas apart: Resonance = 0.4 (weak connection)
- 4 Vargas apart: Resonance = 0.2 (minimal connection)

Dharmic Score = Synaptic Weight × Resonance

This creates a phonetically-grounded computation where:
- KERNEL triggers (ङ/ṅa) resonate best with KERNEL actions
- OUTPUT actions (म/ma) flow naturally from INTERFACE triggers
- Cross-layer connections are weighted by articulatory distance
"""

import json
import logging
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MANAS.Akshara")


# =============================================================================
# VARGA (ARTICULATION CLASSES) - The 5 Layers
# =============================================================================


class Varga(IntEnum):
    """
    The 5 Vargas (articulation classes) of Sanskrit consonants.

    Ordered by articulation position from throat (0) to lips (4).
    This ordering is used for resonance calculation.
    """

    KANTHYA = 0  # Guttural (Throat) - KERNEL/DEEP
    TALAVYA = 1  # Palatal (Palate) - COGNITION/FLOW
    MURDHANYA = 2  # Retroflex (Cerebral) - REPAIR/HARD
    DANTYA = 3  # Dental (Teeth) - INTERFACE/LINK
    OSHTHYA = 4  # Labial (Lips) - OUTPUT/SURFACE


# Sanskrit-to-English mapping for Vargas
VARGA_NAMES = {
    Varga.KANTHYA: ("कण्ठ्य", "Kanthya", "Guttural", "Throat"),
    Varga.TALAVYA: ("तालव्य", "Talavya", "Palatal", "Palate"),
    Varga.MURDHANYA: ("मूर्धन्य", "Murdhanya", "Retroflex", "Cerebral"),
    Varga.DANTYA: ("दन्त्य", "Dantya", "Dental", "Teeth"),
    Varga.OSHTHYA: ("ओष्ठ्य", "Oshthya", "Labial", "Lips"),
}

# Code layer mapping
VARGA_LAYERS = {
    Varga.KANTHYA: "KERNEL",  # Deep system, core processing
    Varga.TALAVYA: "COGNITION",  # Flow, decision making
    Varga.MURDHANYA: "REPAIR",  # Hard work, fixing issues
    Varga.DANTYA: "INTERFACE",  # Links, connections
    Varga.OSHTHYA: "OUTPUT",  # Surface, user-facing
}

# Element mapping (Pancha Bhuta - Five Elements)
VARGA_ELEMENTS = {
    Varga.KANTHYA: ("आकाश", "Akasha", "Ether"),
    Varga.TALAVYA: ("वायु", "Vayu", "Air"),
    Varga.MURDHANYA: ("अग्नि", "Agni", "Fire"),
    Varga.DANTYA: ("जल", "Jala", "Water"),
    Varga.OSHTHYA: ("पृथ्वी", "Prithvi", "Earth"),
}


# =============================================================================
# AKSHARA (PHONEME/LETTER) - The Atomic Unit
# =============================================================================


@dataclass(frozen=True)
class Akshara:
    """
    An Akshara (अक्षर) - imperishable letter/phoneme.

    Each Akshara is an atomic unit with:
    - Devanagari representation (देवनागरी)
    - IAST transliteration
    - Varga (articulation class)
    - Position within Varga (0-4)
    - Voicing and aspiration properties
    """

    devanagari: str  # e.g., "क"
    iast: str  # e.g., "ka"
    varga: Varga  # e.g., KANTHYA
    position: int  # 0-4 within Varga
    voiced: bool = False  # Whether voiced (ग, घ, ङ)
    aspirated: bool = False  # Whether aspirated (ख, घ)

    @property
    def layer(self) -> str:
        """Get the code layer this Akshara belongs to."""
        return VARGA_LAYERS[self.varga]

    @property
    def element(self) -> str:
        """Get the element (Bhuta) for this Akshara."""
        return VARGA_ELEMENTS[self.varga][1]

    @property
    def is_nasal(self) -> bool:
        """Check if this is a nasal (anunasika) consonant (ङ, ञ, ण, न, म)."""
        return self.position == 4

    def resonance_with(self, other: "Akshara") -> float:
        """
        Calculate resonance with another Akshara.

        Based on articulatory distance (Varga difference).
        Same Varga = 1.0, Adjacent = 0.8, etc.
        """
        distance = abs(self.varga - other.varga)
        # Resonance decreases with distance
        resonance_map = {
            0: 1.0,  # Same Varga - perfect resonance
            1: 0.8,  # Adjacent - strong resonance
            2: 0.6,  # Two apart - moderate
            3: 0.4,  # Three apart - weak
            4: 0.2,  # Maximum distance - minimal
        }
        return resonance_map.get(distance, 0.1)

    def __repr__(self) -> str:
        return f"Akshara({self.devanagari}/{self.iast})"


# =============================================================================
# VARNAMALA (ALPHABET MATRIX) - The Complete Grid
# =============================================================================


class Varnamala:
    """
    The Varnamala (वर्णमाला) - Sanskrit Alphabet Matrix.

    This is the 5×5 consonant matrix (25 Vyanjanas) plus special characters.
    Each position has phonetic significance based on articulation.

    Matrix Layout (Ka-varga to Pa-varga):

         Sparsha (Stops)                    Nasal
         Unvoiced  Voiced
         [-asp] [+asp] [-asp] [+asp]
    कण्ठ्य  क      ख      ग      घ      ङ    (Throat)
    तालव्य  च      छ      ज      झ      ञ    (Palate)
    मूर्धन्य ट      ठ      ड      ढ      ण    (Cerebrum)
    दन्त्य   त      थ      द      ध      न    (Teeth)
    ओष्ठ्य   प      फ      ब      भ      म    (Lips)
    """

    _instance: Optional["Varnamala"] = None

    def __init__(self):
        """Initialize the Varnamala matrix."""
        self._matrix: Dict[Varga, List[Akshara]] = {}
        self._by_devanagari: Dict[str, Akshara] = {}
        self._by_iast: Dict[str, Akshara] = {}
        self._build_matrix()

    @classmethod
    def get(cls) -> "Varnamala":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_matrix(self) -> None:
        """Build the complete Varnamala matrix."""
        # Ka-varga (Gutturals) - KERNEL layer
        self._matrix[Varga.KANTHYA] = [
            Akshara("क", "ka", Varga.KANTHYA, 0, voiced=False, aspirated=False),
            Akshara("ख", "kha", Varga.KANTHYA, 1, voiced=False, aspirated=True),
            Akshara("ग", "ga", Varga.KANTHYA, 2, voiced=True, aspirated=False),
            Akshara("घ", "gha", Varga.KANTHYA, 3, voiced=True, aspirated=True),
            Akshara("ङ", "ṅa", Varga.KANTHYA, 4, voiced=True, aspirated=False),  # Nasal
        ]

        # Ca-varga (Palatals) - COGNITION layer
        self._matrix[Varga.TALAVYA] = [
            Akshara("च", "ca", Varga.TALAVYA, 0, voiced=False, aspirated=False),
            Akshara("छ", "cha", Varga.TALAVYA, 1, voiced=False, aspirated=True),
            Akshara("ज", "ja", Varga.TALAVYA, 2, voiced=True, aspirated=False),
            Akshara("झ", "jha", Varga.TALAVYA, 3, voiced=True, aspirated=True),
            Akshara("ञ", "ña", Varga.TALAVYA, 4, voiced=True, aspirated=False),  # Nasal
        ]

        # Ta-varga (Retroflexes) - REPAIR layer
        self._matrix[Varga.MURDHANYA] = [
            Akshara("ट", "ṭa", Varga.MURDHANYA, 0, voiced=False, aspirated=False),
            Akshara("ठ", "ṭha", Varga.MURDHANYA, 1, voiced=False, aspirated=True),
            Akshara("ड", "ḍa", Varga.MURDHANYA, 2, voiced=True, aspirated=False),
            Akshara("ढ", "ḍha", Varga.MURDHANYA, 3, voiced=True, aspirated=True),
            Akshara("ण", "ṇa", Varga.MURDHANYA, 4, voiced=True, aspirated=False),  # Nasal
        ]

        # Ta-varga (Dentals) - INTERFACE layer
        self._matrix[Varga.DANTYA] = [
            Akshara("त", "ta", Varga.DANTYA, 0, voiced=False, aspirated=False),
            Akshara("थ", "tha", Varga.DANTYA, 1, voiced=False, aspirated=True),
            Akshara("द", "da", Varga.DANTYA, 2, voiced=True, aspirated=False),
            Akshara("ध", "dha", Varga.DANTYA, 3, voiced=True, aspirated=True),
            Akshara("न", "na", Varga.DANTYA, 4, voiced=True, aspirated=False),  # Nasal
        ]

        # Pa-varga (Labials) - OUTPUT layer
        self._matrix[Varga.OSHTHYA] = [
            Akshara("प", "pa", Varga.OSHTHYA, 0, voiced=False, aspirated=False),
            Akshara("फ", "pha", Varga.OSHTHYA, 1, voiced=False, aspirated=True),
            Akshara("ब", "ba", Varga.OSHTHYA, 2, voiced=True, aspirated=False),
            Akshara("भ", "bha", Varga.OSHTHYA, 3, voiced=True, aspirated=True),
            Akshara("म", "ma", Varga.OSHTHYA, 4, voiced=True, aspirated=False),  # Nasal
        ]

        # Build lookup indices
        for varga_letters in self._matrix.values():
            for akshara in varga_letters:
                self._by_devanagari[akshara.devanagari] = akshara
                self._by_iast[akshara.iast] = akshara

    def get_by_devanagari(self, char: str) -> Optional[Akshara]:
        """Get Akshara by Devanagari character."""
        return self._by_devanagari.get(char)

    def get_by_iast(self, iast: str) -> Optional[Akshara]:
        """Get Akshara by IAST transliteration."""
        return self._by_iast.get(iast)

    def get_varga(self, varga: Varga) -> List[Akshara]:
        """Get all Aksharas in a Varga."""
        return self._matrix.get(varga, [])

    def get_nasal(self, varga: Varga) -> Optional[Akshara]:
        """Get the nasal (anunasika) of a Varga."""
        varga_letters = self._matrix.get(varga, [])
        if varga_letters:
            return varga_letters[4]  # Nasal is always position 4
        return None

    def get_all_aksharas(self) -> List[Akshara]:
        """Get all 25 Aksharas in matrix order."""
        result = []
        for varga in Varga:
            result.extend(self._matrix[varga])
        return result

    def resonance(self, akshara1: Akshara, akshara2: Akshara) -> float:
        """Calculate resonance between two Aksharas."""
        return akshara1.resonance_with(akshara2)

    def varga_resonance(self, varga1: Varga, varga2: Varga) -> float:
        """Calculate resonance between two Vargas."""
        distance = abs(varga1 - varga2)
        resonance_map = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}
        return resonance_map.get(distance, 0.1)


# =============================================================================
# OPUS-115: DYNAMIC PATH-TO-VARGA MAPPING - The Body IS the Code
# =============================================================================

# Path patterns for each Varga layer
# The folder structure encodes the layer - no manual mapping needed!
PATH_VARGA_PATTERNS: Dict[Varga, List[str]] = {
    # KANTHYA (KERNEL) - Deep Core, Foundation
    # Throat: where sound originates, where the system originates
    Varga.KANTHYA: [
        "vibe_core/runtime/",  # Runtime kernel
        "vibe_core/governance/",  # Core governance
        "vibe_core/protocols/",  # Core protocols
        "vibe_core/store/",  # Data store (foundation)
        "vibe_core/state/",  # State management
        "vibe_core/scheduling/",  # Core scheduling
        "vibe_core/vajra/",  # Vajra (thunderbolt - core power)
        "vibe_core/steward/",  # Steward (core manager)
        "vibe_core/config/",  # Core configuration
        ".opus_state/",  # OPUS kernel state
        ".prakriti/",  # Prakriti (nature - core)
    ],
    # TALAVYA (COGNITION) - Decision/Flow, Intelligence
    # Palate: where sound is shaped, where decisions are shaped
    Varga.TALAVYA: [
        "vibe_core/llm/",  # LLM reasoning
        "vibe_core/cortex/",  # Cortex (brain)
        "vibe_core/plugins/opus_assistant/manas/",  # MANAS cognition
        "vibe_core/plugins/opus_assistant/vidya/",  # Vidya (knowledge)
        "vibe_core/knowledge/",  # Knowledge base
        "vibe_core/agents/",  # Agent reasoning
        "vibe_core/playbook/",  # Playbook (decision trees)
        "vibe_core/shadow_labs/",  # Shadow Labs (research)
    ],
    # MURDHANYA (REPAIR) - Hard Work, Fixing, Testing
    # Retroflex: tongue curls back (effort), fixing requires effort
    Varga.MURDHANYA: [
        "vibe_core/plugins/doctor/",  # Doctor (fixing)
        "vibe_core/plugins/test_mode/",  # Test mode
        "vibe_core/plugins/test_orchestration/",  # Test orchestration
        "vibe_core/specialists/",  # Specialists (experts at fixing)
        "vibe_core/plugins/opus_assistant/narasimha/",  # Narasimha (destroyer of bugs)
        "tests/",  # Test suite
        "**/tests/",  # Any test folder
        "*_test.py",  # Test files
        "test_*.py",  # Test files
    ],
    # DANTYA (INTERFACE) - Links, Connections, Documentation
    # Dental: tongue touches teeth (connection point)
    Varga.DANTYA: [
        "vibe_core/gateway/",  # API gateway
        "vibe_core/loaders/",  # Data loaders
        "vibe_core/plugins/interface/",  # Interface plugin
        "vibe_core/plugins/envoy/",  # Envoy (connections)
        "vibe_core/plugins/nexus_holon/",  # Nexus (connections)
        "vibe_core/cartridges/",  # Cartridges (connectors)
        "vibe_core/tools/",  # Tools (interfaces)
        "docs/",  # Documentation (human interface)
        "*.md",  # Markdown files (human interface)
    ],
    # OSHTHYA (OUTPUT) - Surface, User-facing, Manifestation
    # Labial: lips produce output, user sees output
    Varga.OSHTHYA: [
        "vibe_core/cli/",  # CLI (user output)
        "vibe_core/phoenix/",  # Phoenix (regeneration output)
        "vibe_core/plugins/opus_assistant/render/",  # Rendering
        "vibe_core/plugins/opus_assistant/cli/",  # OPUS CLI
        "vibe_core/plugins/opus_assistant/templates/",  # Output templates
        "vibe_core/settings/",  # User settings
        "*.json",  # JSON output files
        "*.yaml",  # YAML output files
        "*.yml",  # YAML output files
    ],
}


# =============================================================================
# OPUS-117: OPUS DOCUMENT NUMBER → VARGA MAPPING - Fractal Integration
# =============================================================================

# OPUS doc number ranges mapped to Vargas
# This enables DisharmonyDetector to watch the watchers
OPUS_DOC_VARGA_RANGES: Dict[Tuple[int, int], Varga] = {
    # 000-019: KANTHYA (Kernel/Foundation)
    # Core system design, extraction, boot sequence, unification
    (0, 19): Varga.KANTHYA,
    # 020-039: MURDHANYA (Hardening/Repair)
    # Security audits, container migration, test architecture
    (20, 39): Varga.MURDHANYA,
    # 040-059: TALAVYA (Cognition/MANAS)
    # VEDA framework, MANAS cognitive architecture, SUTRA
    (40, 59): Varga.TALAVYA,
    # 060-079: DANTYA (Interface/Flow)
    # DRISHTI, VAJRA wiring, JNANA, interface patterns
    (60, 79): Varga.DANTYA,
    # 080-108: OSHTHYA (Output/Future)
    # Runtime state, cognitive circuits, autonomy loop
    (80, 108): Varga.OSHTHYA,
}


def map_opus_doc_to_varga(doc_number: int) -> Varga:
    """
    OPUS-117: Map an OPUS document number to its Varga.

    The OPUS doc numbering scheme encodes the layer:
    - 000-019: KANTHYA (Kernel/Foundation)
    - 020-039: MURDHANYA (Hardening/Repair)
    - 040-059: TALAVYA (Cognition/MANAS)
    - 060-079: DANTYA (Interface/Flow)
    - 080-108: OSHTHYA (Output/Future)

    Args:
        doc_number: OPUS document number (0-108)

    Returns:
        The Varga for this document range
    """
    for (min_num, max_num), varga in OPUS_DOC_VARGA_RANGES.items():
        if min_num <= doc_number <= max_num:
            return varga
    # Default: OSHTHYA for numbers > 108
    return Varga.OSHTHYA


def get_opus_doc_layer(doc_number: int) -> str:
    """Get the layer name for an OPUS document."""
    return VARGA_LAYERS[map_opus_doc_to_varga(doc_number)]


def get_opus_doc_akshara(doc_number: int) -> Akshara:
    """Get the representative Akshara for an OPUS document."""
    varga = map_opus_doc_to_varga(doc_number)
    varnamala = Varnamala.get()
    nasal = varnamala.get_nasal(varga)
    return nasal if nasal else varnamala.get_varga(varga)[0]


def extract_opus_doc_number(path: str) -> Optional[int]:
    """
    Extract OPUS document number from a path.

    Matches patterns like:
    - docs/architecture/OPUS/054-SUTRA.md → 54
    - 116-SILENT-OBSERVER.md → 116

    Args:
        path: File path

    Returns:
        Document number or None if not an OPUS doc
    """
    import re

    # Look for NNN- pattern in the filename
    match = re.search(r"(\d{3})-.*\.md$", path)
    if match:
        return int(match.group(1))
    return None


def map_path_to_varga(path: str) -> Varga:
    """
    OPUS-115: Dynamically derive Varga from file path.

    The folder structure IS the body - each path belongs to a layer.
    No manual mapping needed - the code's location determines its nature.

    Mapping hierarchy:
    1. Exact prefix match (most specific)
    2. Glob pattern match
    3. Default to TALAVYA (cognition - the middle ground)

    Args:
        path: File path (relative to workspace root)

    Returns:
        The Varga that this path belongs to
    """
    import fnmatch

    # Normalize path (remove leading ./ prefix, not individual chars)
    if path.startswith("./"):
        path = path[2:]
    if path.startswith("/"):
        path = path[1:]

    # PHASE 1: Check folder prefix patterns first (most specific)
    for varga in [Varga.KANTHYA, Varga.TALAVYA, Varga.MURDHANYA, Varga.DANTYA, Varga.OSHTHYA]:
        patterns = PATH_VARGA_PATTERNS.get(varga, [])
        for pattern in patterns:
            # Prefix match (folder paths ending with /)
            if pattern.endswith("/"):
                if path.startswith(pattern) or path.startswith(pattern.rstrip("/")):
                    return varga

    # PHASE 2: Check glob patterns (file extensions, etc.)
    for varga in [Varga.KANTHYA, Varga.TALAVYA, Varga.MURDHANYA, Varga.DANTYA, Varga.OSHTHYA]:
        patterns = PATH_VARGA_PATTERNS.get(varga, [])
        for pattern in patterns:
            if "*" in pattern:
                if fnmatch.fnmatch(path, pattern):
                    return varga
                # Also check just the filename
                if "/" in path:
                    filename = path.split("/")[-1]
                    if fnmatch.fnmatch(filename, pattern):
                        return varga

    # Default: TALAVYA (cognition) - the middle ground
    # Unknown code is cognitive until proven otherwise
    return Varga.TALAVYA


def get_path_layer(path: str) -> str:
    """Get the layer name for a path."""
    return VARGA_LAYERS[map_path_to_varga(path)]


def get_path_element(path: str) -> str:
    """Get the element (Bhuta) for a path."""
    return VARGA_ELEMENTS[map_path_to_varga(path)][1]


def get_path_akshara(path: str) -> Akshara:
    """Get the representative Akshara for a path."""
    varga = map_path_to_varga(path)
    varnamala = Varnamala.get()
    nasal = varnamala.get_nasal(varga)
    return nasal if nasal else varnamala.get_varga(varga)[0]


# =============================================================================
# TRIGGER/ACTION MAPPING - Connecting Code to Varnamala
# =============================================================================


# Semantic trigger types mapped to Vargas (non-path-based triggers)
# OPUS-115: file_changed triggers are now handled dynamically by map_path_to_varga()
TRIGGER_VARGA_MAP: Dict[str, Varga] = {
    # KERNEL (Kanthya) - Core system triggers
    "trigger:test_failure": Varga.KANTHYA,
    "trigger:build_failure": Varga.KANTHYA,
    "trigger:meru_test": Varga.KANTHYA,
    # COGNITION (Talavya) - Decision/analysis triggers
    "trigger:intent_stuck": Varga.TALAVYA,
    "trigger:intent_expired": Varga.TALAVYA,
    "trigger:idle_detected": Varga.TALAVYA,
    # REPAIR (Murdhanya) - Error/fix triggers
    "trigger:error_detected": Varga.MURDHANYA,
    "trigger:lint_failure": Varga.MURDHANYA,
    "trigger:duplicate_class_detected": Varga.MURDHANYA,
    # INTERFACE (Dantya) - Gap/link triggers
    "trigger:gap_detected:missing_code": Varga.DANTYA,
    "trigger:gap_detected:missing_doc": Varga.DANTYA,
    "trigger:gap_detected:missing_test": Varga.DANTYA,
    "trigger:gap_detected:stale_doc": Varga.DANTYA,
    "trigger:gap_detected:missing_harness": Varga.DANTYA,
    "trigger:sutra:missing_code": Varga.DANTYA,
    "trigger:sutra:missing_doc": Varga.DANTYA,
    "trigger:sutra:stale": Varga.DANTYA,
    "trigger:sutra:missing_harness": Varga.DANTYA,
    # OUTPUT (Oshthya) - Misc triggers (file_changed now uses dynamic mapping!)
    "trigger:karma_low": Varga.OSHTHYA,
    # OPUS-117: DISHARMONY TRIGGERS (Silent Observer)
    # Disharmony triggers are REPAIR layer - they need fixing
    "trigger:disharmony:critical": Varga.MURDHANYA,
    "trigger:disharmony:high": Varga.MURDHANYA,
    "trigger:disharmony:medium": Varga.MURDHANYA,
    "trigger:disharmony:low": Varga.MURDHANYA,
    "trigger:disharmony_code:critical": Varga.MURDHANYA,
    "trigger:disharmony_code:high": Varga.MURDHANYA,
    "trigger:disharmony_doc:critical": Varga.MURDHANYA,
    "trigger:disharmony_doc:high": Varga.MURDHANYA,
}

# Map action categories to Vargas
ACTION_VARGA_MAP: Dict[str, Varga] = {
    # KERNEL (Kanthya) - Core actions
    "action:run_tests": Varga.KANTHYA,
    "action:check_lint": Varga.KANTHYA,
    "action:auto_retry": Varga.KANTHYA,
    # COGNITION (Talavya) - Analysis actions
    "action:analyze_error": Varga.TALAVYA,
    "action:log_diagnostic": Varga.TALAVYA,
    # REPAIR (Murdhanya) - Fix actions
    "action:auto_fix": Varga.MURDHANYA,
    "action:consolidate": Varga.MURDHANYA,
    # INTERFACE (Dantya) - Creation actions
    "action:create_code": Varga.DANTYA,
    "action:create_doc": Varga.DANTYA,
    "action:create_test": Varga.DANTYA,
    "action:create_harness": Varga.DANTYA,
    "action:update_docs": Varga.DANTYA,
    # OUTPUT (Oshthya) - Notification actions
    "action:notify_operator": Varga.OSHTHYA,
    "action:escalate_to_operator": Varga.OSHTHYA,
    "action:report_to_operator": Varga.OSHTHYA,
    # OPUS-117: DISHARMONY ACTIONS (Silent Observer)
    # Refactoring and moving are REPAIR operations
    "action:refactor_code": Varga.MURDHANYA,
    "action:move_code": Varga.MURDHANYA,
    # Doc operations are INTERFACE layer
    "action:renumber_doc": Varga.DANTYA,
    "action:refocus_doc": Varga.DANTYA,
    "action:update_doc": Varga.DANTYA,
}


def get_trigger_varga(trigger: str) -> Varga:
    """
    Get the Varga for a trigger pattern.

    OPUS-115: For file_changed triggers, dynamically derive Varga from path.
    The file's location determines its nature, not a static map.
    """
    # Exact match first (semantic triggers)
    if trigger in TRIGGER_VARGA_MAP:
        return TRIGGER_VARGA_MAP[trigger]

    # OPUS-115: Dynamic path-based Varga for file_changed triggers
    if trigger.startswith("trigger:file_changed:"):
        # Extract path from trigger: "trigger:file_changed:vibe_core/cli/main.py"
        path = trigger[len("trigger:file_changed:") :]
        # Remove glob patterns for mapping
        path = path.replace("**", "").replace("*", "")
        if path:
            return map_path_to_varga(path)
        return Varga.OSHTHYA  # Fallback if path is empty

    # Pattern matching for gap triggers
    if trigger.startswith("trigger:gap_detected:"):
        return Varga.DANTYA  # INTERFACE layer

    # Pattern matching for sutra triggers
    if trigger.startswith("trigger:sutra:"):
        return Varga.DANTYA  # INTERFACE layer

    # Default: COGNITION layer (middle ground)
    return Varga.TALAVYA


def get_action_varga(action: str) -> Varga:
    """Get the Varga for an action pattern."""
    if action in ACTION_VARGA_MAP:
        return ACTION_VARGA_MAP[action]

    # Default: COGNITION layer
    return Varga.TALAVYA


def get_trigger_akshara(trigger: str) -> Akshara:
    """
    Get the representative Akshara for a trigger.

    Returns the nasal (anunasika) of the trigger's Varga,
    as nasals are the "binding" consonants that connect sounds.
    """
    varga = get_trigger_varga(trigger)
    varnamala = Varnamala.get()
    nasal = varnamala.get_nasal(varga)
    return nasal if nasal else varnamala.get_varga(varga)[0]


def get_action_akshara(action: str) -> Akshara:
    """Get the representative Akshara for an action."""
    varga = get_action_varga(action)
    varnamala = Varnamala.get()
    nasal = varnamala.get_nasal(varga)
    return nasal if nasal else varnamala.get_varga(varga)[0]


# =============================================================================
# RESONANCE CALCULATION - The Dharmic Score
# =============================================================================


def calculate_resonance(trigger: str, action: str) -> float:
    """
    Calculate the resonance between a trigger and action.

    Based on the articulatory distance between their Vargas.

    Args:
        trigger: Canonical trigger string
        action: Canonical action string

    Returns:
        Resonance value (0.2 - 1.0)
    """
    trigger_varga = get_trigger_varga(trigger)
    action_varga = get_action_varga(action)
    return Varnamala.get().varga_resonance(trigger_varga, action_varga)


def calculate_dharmic_score(
    trigger: str,
    action: str,
    synaptic_weight: float,
) -> float:
    """
    Calculate the Dharmic Score for a trigger-action pair.

    OPUS-133 SIDDHI Enhancement:
    Base formula: Dharmic Score = Synaptic Weight × Resonance

    But when weight > SIDDHI_THRESHOLD (0.85), experience begins to
    override resonance. A pattern proven 10+ times has earned trust.

    Siddhi Formula:
    - siddhi_factor = (weight - 0.85) / 0.15  (0.0 at 0.85, 1.0 at 1.0)
    - effective_resonance = resonance + siddhi_factor * (1 - resonance)
    - This lifts low resonance toward 1.0 for mastered patterns

    Example: weight=0.95, resonance=0.2
    - Without Siddhi: 0.95 × 0.2 = 0.19 (BLOCK)
    - With Siddhi: siddhi=0.67, eff_res=0.2+0.67×0.8=0.74 → 0.95×0.74=0.70 (EXECUTE)

    Args:
        trigger: Canonical trigger string
        action: Canonical action string
        synaptic_weight: The learned synaptic weight (0.0 - 1.0)

    Returns:
        Dharmic score (0.0 - 1.0)
    """
    resonance = calculate_resonance(trigger, action)

    # OPUS-133: SIDDHI - Mastery overrides dogma
    SIDDHI_THRESHOLD = 0.85  # Weight at which mastery kicks in

    if synaptic_weight > SIDDHI_THRESHOLD:
        # Calculate siddhi factor (0.0 at threshold, 1.0 at max weight)
        siddhi_factor = (synaptic_weight - SIDDHI_THRESHOLD) / (1.0 - SIDDHI_THRESHOLD)

        # Lift resonance toward 1.0 based on mastery
        # This allows proven patterns to override phonetic dissonance
        effective_resonance = resonance + siddhi_factor * (1.0 - resonance)

        return synaptic_weight * effective_resonance

    return synaptic_weight * resonance


# =============================================================================
# AKSHARA GRAPH - JSON-Persistent Relationship Structure
# =============================================================================


@dataclass
class AksharaNode:
    """A node in the Akshara graph representing a trigger or action."""

    pattern: str  # e.g., "trigger:test_failure"
    akshara: str  # e.g., "ङ"
    varga: str  # e.g., "KANTHYA"
    layer: str  # e.g., "KERNEL"
    element: str  # e.g., "Akasha"
    node_type: str  # "trigger" or "action"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pattern": self.pattern,
            "akshara": self.akshara,
            "varga": self.varga,
            "layer": self.layer,
            "element": self.element,
            "node_type": self.node_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AksharaNode":
        """Create from dictionary."""
        return cls(
            pattern=data["pattern"],
            akshara=data["akshara"],
            varga=data["varga"],
            layer=data["layer"],
            element=data["element"],
            node_type=data["node_type"],
        )


@dataclass
class AksharaEdge:
    """An edge in the Akshara graph representing a connection."""

    source: str  # Source pattern
    target: str  # Target pattern
    weight: float  # Synaptic weight
    resonance: float  # Akshara resonance
    dharmic_score: float  # weight × resonance

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "resonance": self.resonance,
            "dharmic_score": self.dharmic_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AksharaEdge":
        """Create from dictionary."""
        return cls(
            source=data["source"],
            target=data["target"],
            weight=data["weight"],
            resonance=data["resonance"],
            dharmic_score=data["dharmic_score"],
        )


class AksharaGraph:
    """
    The Akshara Graph - A JSON-persistent graph structure for Akshara relationships.

    This provides a graph view of the synaptic connections, with nodes representing
    triggers and actions, and edges representing learned associations with resonance.

    The graph can be:
    1. Exported to JSON for visualization or analysis
    2. Queried for paths between triggers and actions
    3. Analyzed for resonance patterns
    """

    def __init__(self, workspace: Path):
        """Initialize the Akshara graph."""
        self._workspace = workspace
        self._graph_file = workspace / ".opus_state" / "akshara_graph.json"
        self._nodes: Dict[str, AksharaNode] = {}
        self._edges: List[AksharaEdge] = []

    def build_from_synapses(self, synapses: Dict[str, Any]) -> None:
        """
        Build the graph from synapses.json data.

        Args:
            synapses: The loaded synapses.json content
        """
        weights = synapses.get("weights", {})
        varnamala = Varnamala.get()

        self._nodes.clear()
        self._edges.clear()

        # Build nodes and edges
        for trigger, actions in weights.items():
            # Create trigger node if not exists
            if trigger not in self._nodes:
                trigger_akshara = get_trigger_akshara(trigger)
                trigger_varga = get_trigger_varga(trigger)
                self._nodes[trigger] = AksharaNode(
                    pattern=trigger,
                    akshara=trigger_akshara.devanagari,
                    varga=trigger_varga.name,
                    layer=VARGA_LAYERS[trigger_varga],
                    element=VARGA_ELEMENTS[trigger_varga][1],
                    node_type="trigger",
                )

            # Create action nodes and edges
            for action, weight in actions.items():
                if action not in self._nodes:
                    action_akshara = get_action_akshara(action)
                    action_varga = get_action_varga(action)
                    self._nodes[action] = AksharaNode(
                        pattern=action,
                        akshara=action_akshara.devanagari,
                        varga=action_varga.name,
                        layer=VARGA_LAYERS[action_varga],
                        element=VARGA_ELEMENTS[action_varga][1],
                        node_type="action",
                    )

                # Create edge
                resonance = calculate_resonance(trigger, action)
                dharmic = calculate_dharmic_score(trigger, action, weight)
                self._edges.append(
                    AksharaEdge(
                        source=trigger,
                        target=action,
                        weight=weight,
                        resonance=resonance,
                        dharmic_score=dharmic,
                    )
                )

    def save(self) -> None:
        """Save the graph to JSON."""
        self._graph_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "schema": "akshara-graph-v1",
            "description": "OPUS-114: Akshara Graph - Sanskrit Phonemic Computation Matrix",
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges],
            "meta": {
                "vargas": {v.name: VARGA_NAMES[v] for v in Varga},
                "elements": {v.name: VARGA_ELEMENTS[v] for v in Varga},
                "layers": VARGA_LAYERS,
                "total_nodes": len(self._nodes),
                "total_edges": len(self._edges),
            },
        }

        self._graph_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info(f"📊 Akshara Graph saved: {len(self._nodes)} nodes, {len(self._edges)} edges")

    def load(self) -> bool:
        """Load the graph from JSON."""
        if not self._graph_file.exists():
            return False

        try:
            data = json.loads(self._graph_file.read_text())
            self._nodes = {k: AksharaNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
            self._edges = [AksharaEdge.from_dict(e) for e in data.get("edges", [])]
            return True
        except Exception as e:
            logger.warning(f"Failed to load Akshara graph: {e}")
            return False

    def get_edges_for_trigger(self, trigger: str) -> List[AksharaEdge]:
        """Get all edges originating from a trigger."""
        return [e for e in self._edges if e.source == trigger]

    def get_edges_by_dharmic_score(self, min_score: float = 0.0) -> List[AksharaEdge]:
        """Get edges sorted by Dharmic score."""
        filtered = [e for e in self._edges if e.dharmic_score >= min_score]
        return sorted(filtered, key=lambda e: e.dharmic_score, reverse=True)

    def get_varga_connections(self) -> Dict[str, Dict[str, int]]:
        """Get connection counts between Vargas."""
        connections: Dict[str, Dict[str, int]] = {}

        for edge in self._edges:
            source_node = self._nodes.get(edge.source)
            target_node = self._nodes.get(edge.target)

            if source_node and target_node:
                s_varga = source_node.varga
                t_varga = target_node.varga

                if s_varga not in connections:
                    connections[s_varga] = {}
                if t_varga not in connections[s_varga]:
                    connections[s_varga][t_varga] = 0
                connections[s_varga][t_varga] += 1

        return connections

    def to_dict(self) -> Dict[str, Any]:
        """Export the graph as a dictionary."""
        return {
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges],
        }


# =============================================================================
# INTEGRATION HELPERS - For use in SynapticMemory
# =============================================================================


def enhance_recommendations_with_resonance(
    trigger: str,
    recommendations: List[Tuple[str, float]],
) -> List[Tuple[str, float, float, float]]:
    """
    Enhance synaptic recommendations with resonance data.

    Args:
        trigger: The trigger pattern
        recommendations: List of (action, weight) tuples

    Returns:
        List of (action, weight, resonance, dharmic_score) tuples,
        sorted by dharmic_score descending
    """
    enhanced = []
    for action, weight in recommendations:
        resonance = calculate_resonance(trigger, action)
        dharmic = calculate_dharmic_score(trigger, action, weight)
        enhanced.append((action, weight, resonance, dharmic))

    # Sort by dharmic score (not just weight!)
    enhanced.sort(key=lambda x: x[3], reverse=True)
    return enhanced


def get_resonant_actions(trigger: str, min_resonance: float = 0.6) -> List[str]:
    """
    Get actions that resonate well with a trigger.

    Args:
        trigger: The trigger pattern
        min_resonance: Minimum resonance threshold

    Returns:
        List of action patterns with good resonance
    """
    trigger_varga = get_trigger_varga(trigger)
    resonant = []

    for action, action_varga in ACTION_VARGA_MAP.items():
        if Varnamala.get().varga_resonance(trigger_varga, action_varga) >= min_resonance:
            resonant.append(action)

    return resonant


# =============================================================================
# DIAGNOSTIC/DEBUG HELPERS
# =============================================================================


def print_varnamala_matrix() -> str:
    """Print the complete Varnamala matrix for debugging."""
    lines = ["", "═══════════════════════════════════════════════════════"]
    lines.append("       VARNAMALA - The Sanskrit Consonant Matrix        ")
    lines.append("═══════════════════════════════════════════════════════")

    varnamala = Varnamala.get()

    for varga in Varga:
        varga_info = VARGA_NAMES[varga]
        layer = VARGA_LAYERS[varga]
        element = VARGA_ELEMENTS[varga]

        letters = varnamala.get_varga(varga)
        dev = " ".join(a.devanagari for a in letters)
        iast = " ".join(f"{a.iast:4}" for a in letters)

        lines.append("")
        lines.append(f"  {varga_info[0]} ({varga_info[1]}) - {layer}")
        lines.append(f"  Element: {element[0]} ({element[1]})")
        lines.append(f"  Letters: {dev}")
        lines.append(f"           {iast}")

    lines.append("")
    lines.append("═══════════════════════════════════════════════════════")

    return "\n".join(lines)


def print_resonance_matrix() -> str:
    """Print the Varga resonance matrix."""
    lines = ["", "  Varga Resonance Matrix (Dharmic Harmony)"]
    lines.append("  ─────────────────────────────────────────")

    header = "          " + " ".join(f"{v.name[:4]:>6}" for v in Varga)
    lines.append(header)

    varnamala = Varnamala.get()
    for v1 in Varga:
        row = f"  {v1.name[:6]:>6} │"
        for v2 in Varga:
            res = varnamala.varga_resonance(v1, v2)
            row += f" {res:5.2f}"
        lines.append(row)

    return "\n".join(lines)
