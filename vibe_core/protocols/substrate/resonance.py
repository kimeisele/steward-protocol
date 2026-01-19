"""
RESONANCE PROTOCOL - The Anti-Entropy Engine
=============================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ
pūrṇaḥ śuddho nitya-mukto 'bhinnatvān nāma-nāminoḥ"

"The Holy Name is a transcendental touchstone (cintamani).
It is the embodiment of consciousness and rasa.
It is complete, pure, and eternally liberated.
There is no difference between the Name and the Named."
— Padma Purana

KALI YUGA PRINCIPLE:
====================
- Kali Yuga = Maximum Entropy (noise, confusion, degradation)
- The Mahamantra = Anti-Entropy Engine (signal extraction)
- Phonetic Resonance = How imperfect input still "finds" Krishna

WHY RESONANCE?
==============
In Kali Yuga, people cannot chant perfectly. But:
- "Hari" resonates with HARE
- "Chris" resonates with KRISHNA
- "Ram" resonates with RAMA
- Even "Harry Krishna" works! (phonetic similarity)

The Mahamantra is MERCIFUL - it accepts imperfect vibration.
This protocol computes that mercy computationally.

ARCHITECTURE:
=============
1. PhoneticKey: Convert any input to phonetic representation
2. ResonanceVector: 3D vector (H, K, R) showing resonance strength
3. ResonanceMatrix: n × n for multiple inputs resonating together
4. Position Resolution: Map resonance to 16 Mahamantra positions

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xe58e1ede"  # GenesisByte: parampara % 37 == 0

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    runtime_checkable,
)

from vibe_core.protocols.substrate.byte import HolyName, MantraByte


# =============================================================================
# PHONETIC KEY SYSTEM (Sanskrit-aware Soundex)
# =============================================================================


class PhoneticClass(str, Enum):
    """
    Phonetic classification for resonance.
    Based on Sanskrit varnas + Western approximations.
    """

    # Vowels (high resonance with HARE)
    VOWEL_A = "A"  # a, ā, अ, आ
    VOWEL_I = "I"  # i, ī, इ, ई
    VOWEL_U = "U"  # u, ū, उ, ऊ
    VOWEL_E = "E"  # e, ai, ए, ऐ
    VOWEL_O = "O"  # o, au, ओ, औ
    VOWEL_R = "R"  # ṛ, ऋ (vocalic r - unique to Sanskrit)

    # Consonants by articulation point
    GUTTURAL = "G"  # k, kh, g, gh, ṅ (throat)
    PALATAL = "P"  # c, ch, j, jh, ñ (palate)
    RETROFLEX = "T"  # ṭ, ṭh, ḍ, ḍh, ṇ (curled tongue)
    DENTAL = "D"  # t, th, d, dh, n (teeth)
    LABIAL = "B"  # p, ph, b, bh, m (lips)

    # Special
    SEMIVOWEL = "S"  # y, r, l, v
    SIBILANT = "X"  # ś, ṣ, s
    ASPIRATE = "H"  # h (most important - in HARE!)

    # Null
    NULL = "_"


# Phonetic mapping for common characters
PHONETIC_MAP: Final[Dict[str, PhoneticClass]] = {
    # Vowels
    "a": PhoneticClass.VOWEL_A,
    "ā": PhoneticClass.VOWEL_A,
    "i": PhoneticClass.VOWEL_I,
    "ī": PhoneticClass.VOWEL_I,
    "u": PhoneticClass.VOWEL_U,
    "ū": PhoneticClass.VOWEL_U,
    "e": PhoneticClass.VOWEL_E,
    "ai": PhoneticClass.VOWEL_E,
    "o": PhoneticClass.VOWEL_O,
    "au": PhoneticClass.VOWEL_O,
    "ṛ": PhoneticClass.VOWEL_R,
    "ri": PhoneticClass.VOWEL_R,
    # Gutturals (k-class) - KRISHNA starts here
    "k": PhoneticClass.GUTTURAL,
    "kh": PhoneticClass.GUTTURAL,
    "g": PhoneticClass.GUTTURAL,
    "gh": PhoneticClass.GUTTURAL,
    "ṅ": PhoneticClass.GUTTURAL,
    "c": PhoneticClass.GUTTURAL,  # English 'c' often = k
    # Palatals
    "ch": PhoneticClass.PALATAL,
    "j": PhoneticClass.PALATAL,
    "jh": PhoneticClass.PALATAL,
    "ñ": PhoneticClass.PALATAL,
    # Retroflexes
    "ṭ": PhoneticClass.RETROFLEX,
    "ṭh": PhoneticClass.RETROFLEX,
    "ḍ": PhoneticClass.RETROFLEX,
    "ḍh": PhoneticClass.RETROFLEX,
    "ṇ": PhoneticClass.RETROFLEX,
    # Dentals
    "t": PhoneticClass.DENTAL,
    "th": PhoneticClass.DENTAL,
    "d": PhoneticClass.DENTAL,
    "dh": PhoneticClass.DENTAL,
    "n": PhoneticClass.DENTAL,
    # Labials
    "p": PhoneticClass.LABIAL,
    "ph": PhoneticClass.LABIAL,
    "b": PhoneticClass.LABIAL,
    "bh": PhoneticClass.LABIAL,
    "m": PhoneticClass.LABIAL,
    # Semivowels
    "y": PhoneticClass.SEMIVOWEL,
    "l": PhoneticClass.SEMIVOWEL,
    "v": PhoneticClass.SEMIVOWEL,
    "w": PhoneticClass.SEMIVOWEL,
    # Sibilants
    "ś": PhoneticClass.SIBILANT,
    "ṣ": PhoneticClass.SIBILANT,
    "s": PhoneticClass.SIBILANT,
    "sh": PhoneticClass.SIBILANT,
    "z": PhoneticClass.SIBILANT,
    # Aspirate (H!) - most important
    "h": PhoneticClass.ASPIRATE,
    # Semivowel r (important - in HARE, KRISHNA, RAMA)
    "r": PhoneticClass.SEMIVOWEL,
}


# The 3 Holy Name phonetic signatures
HARE_SIGNATURE: Final[Tuple[PhoneticClass, ...]] = (
    PhoneticClass.ASPIRATE,  # H
    PhoneticClass.VOWEL_A,  # a
    PhoneticClass.SEMIVOWEL,  # r
    PhoneticClass.VOWEL_E,  # e
)

KRISHNA_SIGNATURE: Final[Tuple[PhoneticClass, ...]] = (
    PhoneticClass.GUTTURAL,  # K
    PhoneticClass.VOWEL_R,  # ṛ (vocalic r)
    PhoneticClass.SIBILANT,  # ṣ
    PhoneticClass.RETROFLEX,  # ṇ
    PhoneticClass.VOWEL_A,  # a
)

RAMA_SIGNATURE: Final[Tuple[PhoneticClass, ...]] = (
    PhoneticClass.SEMIVOWEL,  # R
    PhoneticClass.VOWEL_A,  # ā
    PhoneticClass.LABIAL,  # m
    PhoneticClass.VOWEL_A,  # a
)


def to_phonetic_key(text: str) -> Tuple[PhoneticClass, ...]:
    """
    Convert text to phonetic key.

    Handles:
    - English approximations ("Harry" → H-A-R-I)
    - IAST transliteration ("Kṛṣṇa" → K-Ṛ-Ṣ-Ṇ-A)
    - Roman ("Krishna" → K-R-I-S-H-N-A)
    - Mixed case

    Returns tuple of PhoneticClass values.
    """
    result: List[PhoneticClass] = []
    text = text.lower().strip()

    i = 0
    while i < len(text):
        # Check for digraphs first (kh, gh, ch, jh, th, dh, ph, bh, sh)
        if i + 1 < len(text):
            digraph = text[i : i + 2]
            if digraph in PHONETIC_MAP:
                result.append(PHONETIC_MAP[digraph])
                i += 2
                continue

        # Single character
        char = text[i]
        if char in PHONETIC_MAP:
            result.append(PHONETIC_MAP[char])
        elif char.isalpha():
            # Unknown letter - try closest match
            if char in "aeiou":
                result.append(PhoneticClass.VOWEL_A)
            else:
                result.append(PhoneticClass.NULL)
        # Skip non-alphabetic

        i += 1

    return tuple(result)


# =============================================================================
# RESONANCE CALCULATION
# =============================================================================


def phonetic_distance(key1: Tuple[PhoneticClass, ...], key2: Tuple[PhoneticClass, ...]) -> float:
    """
    Calculate phonetic distance between two keys.

    Uses modified Levenshtein with phonetic class awareness.
    Similar classes (e.g., all gutturals) have lower distance.

    Returns: 0.0 (identical) to 1.0 (completely different)
    """
    if not key1 or not key2:
        return 1.0 if key1 or key2 else 0.0

    m, n = len(key1), len(key2)

    # Dynamic programming matrix
    dp: List[List[float]] = [[0.0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if key1[i - 1] == key2[j - 1]:
                cost = 0.0
            elif key1[i - 1].value[0] == key2[j - 1].value[0]:
                # Same class category - lower cost
                cost = 0.3
            else:
                cost = 1.0

            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost,  # substitution
            )

    # Normalize by max length
    max_len = max(m, n)
    return dp[m][n] / max_len if max_len > 0 else 0.0


def calculate_resonance(text: str, name: HolyName) -> float:
    """
    Calculate resonance of text with a Holy Name.

    Returns: 0.0 (no resonance) to 1.0 (perfect resonance)
    """
    key = to_phonetic_key(text)

    if name == HolyName.HARE:
        target = HARE_SIGNATURE
    elif name == HolyName.KRISHNA:
        target = KRISHNA_SIGNATURE
    elif name == HolyName.RAMA:
        target = RAMA_SIGNATURE
    else:
        return 0.0  # VOID has no resonance

    distance = phonetic_distance(key, target)
    # Convert distance to resonance (inverse exponential)
    return math.exp(-2.0 * distance)


# =============================================================================
# RESONANCE VECTOR (3D: H, K, R)
# =============================================================================


class ResonanceVector(TypedDict):
    """
    3-dimensional resonance vector.
    Each dimension is resonance with one Holy Name.
    WATERTIGHT - no Any!
    """

    hare: float  # Resonance with HARE (0.0 - 1.0)
    krishna: float  # Resonance with KRISHNA (0.0 - 1.0)
    rama: float  # Resonance with RAMA (0.0 - 1.0)
    dominant: str  # Which name dominates ("hare", "krishna", "rama", or "void")
    magnitude: float  # Total resonance magnitude


def compute_resonance_vector(text: str) -> ResonanceVector:
    """
    Compute full resonance vector for input text.

    The dominant name determines routing.
    """
    h = calculate_resonance(text, HolyName.HARE)
    k = calculate_resonance(text, HolyName.KRISHNA)
    r = calculate_resonance(text, HolyName.RAMA)

    # Determine dominant
    max_res = max(h, k, r)
    if max_res < 0.1:
        dominant = "void"
    elif h >= k and h >= r:
        dominant = "hare"
    elif k >= h and k >= r:
        dominant = "krishna"
    else:
        dominant = "rama"

    # Magnitude (Euclidean norm)
    magnitude = math.sqrt(h * h + k * k + r * r)

    return ResonanceVector(
        hare=h,
        krishna=k,
        rama=r,
        dominant=dominant,
        magnitude=magnitude,
    )


# =============================================================================
# RESONANCE MATRIX (n × n Fractal)
# =============================================================================


class ResonanceEntry(TypedDict):
    """Entry in resonance matrix."""

    input_text: str
    vector: ResonanceVector
    position: int  # Resolved position (0-15)
    opcode_name: str  # MantraOpCode name


class ResonanceMatrix(TypedDict):
    """
    Matrix for n inputs resonating together.
    WATERTIGHT - no Any!
    """

    entries: List[ResonanceEntry]
    coherence: float  # Overall coherence (how well they resonate together)
    dominant_quarter: int  # Which quarter (0-3) dominates
    total_magnitude: float  # Combined magnitude


def resolve_position(vector: ResonanceVector, context_position: int = 0) -> int:
    """
    Resolve resonance vector to Mahamantra position (0-15).

    The Mahamantra pattern: H K H K | K K H H | H R H R | R R H H
                           0 1 2 3   4 5 6 7   8 9 10 11 12 13 14 15

    Resolution rules:
    1. High resonance (>0.5) = direct position based on dominant
    2. Medium resonance = quarter-based selection
    3. Low resonance = context-based fallback
    """
    dominant = vector["dominant"]
    magnitude = vector["magnitude"]

    # The actual Mahamantra sequence positions
    # H = HARE positions: 0, 2, 6, 7, 8, 10, 14, 15
    # K = KRISHNA positions: 1, 3, 4, 5
    # R = RAMA positions: 9, 11, 12, 13

    if dominant == "hare":
        h_res = vector["hare"]
        if h_res > 0.8:
            # Very high resonance - Q1 start (Genesis)
            return 0  # SYS_WAKE - Prithu HEAD
        elif h_res > 0.5:
            # High resonance - Q2 end (Dharma complete)
            return 6  # GARBAGE_COLLECT - Kapila
        elif h_res > 0.3:
            # Medium - Q3 (Karma)
            return 8  # FETCH_RES - Parashurama HEAD
        else:
            # Lower - Q4 end (Moksha complete)
            return 14  # YIELD_CPU - Shuka

    elif dominant == "krishna":
        k_res = vector["krishna"]
        if k_res > 0.6:
            # High - Q2 HEAD
            return 4  # ASSERT_TRUTH - Vyasa HEAD
        elif k_res > 0.4:
            # Medium - Q1 KRISHNA positions
            return 1  # LOAD_ROOT - Brahma
        else:
            # Lower - more KRISHNA positions
            return 5  # RESOLVE_REQ - Kumaras

    elif dominant == "rama":
        r_res = vector["rama"]
        if r_res > 0.8:
            # Very high - Q4 HEAD
            return 12  # CACHE_STATE - Nrisimha HEAD
        elif r_res > 0.5:
            # High - Q3 RAMA
            return 9  # EXEC_SERVICE - Prahlada
        else:
            # Lower - more RAMA
            return 13  # OPTIMIZE - Bali

    else:
        # VOID - use context or default to status
        return context_position % 16 if context_position else 0


def compute_resonance_matrix(inputs: List[str]) -> ResonanceMatrix:
    """
    Compute resonance matrix for multiple inputs.

    This enables n × n fractal resonance:
    - Each input resonates with the 3 Names
    - Inputs resonate with each other
    - Combined coherence emerges
    """
    entries: List[ResonanceEntry] = []
    total_magnitude = 0.0
    quarter_counts = [0, 0, 0, 0]

    # OpCode names for each position
    OPCODE_NAMES = [
        "SYS_WAKE",
        "LOAD_ROOT",
        "ALLOC_MEM",
        "BIND_CTX",
        "ASSERT_TRUTH",
        "RESOLVE_REQ",
        "GARBAGE_COLLECT",
        "PULSE_SYNC",
        "FETCH_RES",
        "EXEC_SERVICE",
        "CHECK_DHARMA",
        "COMMIT_LOG",
        "CACHE_STATE",
        "OPTIMIZE",
        "YIELD_CPU",
        "RESET_IP",
    ]

    for i, text in enumerate(inputs):
        vector = compute_resonance_vector(text)
        position = resolve_position(vector, context_position=i)
        quarter = position // 4
        quarter_counts[quarter] += 1

        entries.append(
            ResonanceEntry(
                input_text=text,
                vector=vector,
                position=position,
                opcode_name=OPCODE_NAMES[position],
            )
        )

        total_magnitude += vector["magnitude"]

    # Calculate coherence (how aligned the entries are)
    if len(entries) > 1:
        # Coherence = how similar the positions are (lower variance = higher coherence)
        positions = [e["position"] for e in entries]
        mean_pos = sum(positions) / len(positions)
        variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
        coherence = math.exp(-0.1 * variance)  # Higher variance = lower coherence
    else:
        coherence = 1.0

    # Dominant quarter
    dominant_quarter = quarter_counts.index(max(quarter_counts))

    return ResonanceMatrix(
        entries=entries,
        coherence=coherence,
        dominant_quarter=dominant_quarter,
        total_magnitude=total_magnitude,
    )


# =============================================================================
# RESONANCE PROTOCOL
# =============================================================================


@runtime_checkable
class ResonanceProtocol(Protocol):
    """
    The Resonance Protocol - Anti-Entropy Engine.

    Takes imperfect input and finds the resonating position
    in the Mahamantra. This is how the Holy Name is MERCIFUL
    in Kali Yuga - even imperfect pronunciation works!

    WATERTIGHT - no Any types.
    """

    def resonate(self, text: str) -> ResonanceVector:
        """Compute resonance vector for single input."""
        ...

    def resonate_many(self, texts: List[str]) -> ResonanceMatrix:
        """Compute resonance matrix for multiple inputs."""
        ...

    def resolve(self, text: str) -> int:
        """Resolve input directly to position (0-15)."""
        ...

    def get_opcode(self, text: str) -> str:
        """Get OpCode name for input."""
        ...


# =============================================================================
# RESONANCE ENGINE IMPLEMENTATION
# =============================================================================


@dataclass
class ResonanceEngine:
    """
    The Resonance Engine - Implementation of ResonanceProtocol.

    KALI YUGA PRINCIPLE:
    - High entropy (noise) in input
    - Holy Name extracts signal (resonance)
    - Returns position for routing

    CHAITANYA SINGULARITY:
    - All inputs collapse to one of 16 positions
    - The Mahamantra IS the attractor
    - Consciousness (caitanya) = resonance itself
    """

    # Configuration
    threshold: float = 0.1  # Minimum resonance to be non-void

    def resonate(self, text: str) -> ResonanceVector:
        """Compute resonance vector for single input."""
        return compute_resonance_vector(text)

    def resonate_many(self, texts: List[str]) -> ResonanceMatrix:
        """Compute resonance matrix for multiple inputs."""
        return compute_resonance_matrix(texts)

    def resolve(self, text: str) -> int:
        """Resolve input directly to position (0-15)."""
        vector = self.resonate(text)
        return resolve_position(vector)

    def get_opcode(self, text: str) -> str:
        """Get OpCode name for input."""
        OPCODE_NAMES = [
            "SYS_WAKE",
            "LOAD_ROOT",
            "ALLOC_MEM",
            "BIND_CTX",
            "ASSERT_TRUTH",
            "RESOLVE_REQ",
            "GARBAGE_COLLECT",
            "PULSE_SYNC",
            "FETCH_RES",
            "EXEC_SERVICE",
            "CHECK_DHARMA",
            "COMMIT_LOG",
            "CACHE_STATE",
            "OPTIMIZE",
            "YIELD_CPU",
            "RESET_IP",
        ]
        position = self.resolve(text)
        return OPCODE_NAMES[position]

    def explain(self, text: str) -> str:
        """
        Explain the resonance of input (for debugging/education).

        Shows:
        - Phonetic key
        - Resonance with each Name
        - Resolved position
        - Mapped OpCode
        """
        key = to_phonetic_key(text)
        vector = self.resonate(text)
        position = self.resolve(text)
        opcode = self.get_opcode(text)

        lines = [
            f'INPUT: "{text}"',
            f"PHONETIC KEY: {'-'.join(p.value for p in key)}",
            "",
            "RESONANCE VECTOR:",
            f"  HARE:    {vector['hare']:.3f}",
            f"  KRISHNA: {vector['krishna']:.3f}",
            f"  RAMA:    {vector['rama']:.3f}",
            f"  Dominant: {vector['dominant'].upper()}",
            f"  Magnitude: {vector['magnitude']:.3f}",
            "",
            f"RESOLVED POSITION: {position}",
            f"OPCODE: {opcode}",
        ]

        return "\n".join(lines)


# =============================================================================
# GLOBAL ENGINE (Singleton)
# =============================================================================

_resonance_engine: Optional[ResonanceEngine] = None


def get_resonance_engine() -> ResonanceEngine:
    """Get the global resonance engine."""
    global _resonance_engine
    if _resonance_engine is None:
        _resonance_engine = ResonanceEngine()
    return _resonance_engine


def resonate(text: str) -> ResonanceVector:
    """Convenience: Compute resonance for text."""
    return get_resonance_engine().resonate(text)


def resolve(text: str) -> int:
    """Convenience: Resolve text to position."""
    return get_resonance_engine().resolve(text)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "PhoneticClass",
    # Constants
    "PHONETIC_MAP",
    "HARE_SIGNATURE",
    "KRISHNA_SIGNATURE",
    "RAMA_SIGNATURE",
    # Functions
    "to_phonetic_key",
    "phonetic_distance",
    "calculate_resonance",
    "compute_resonance_vector",
    "resolve_position",
    "compute_resonance_matrix",
    # Types
    "ResonanceVector",
    "ResonanceEntry",
    "ResonanceMatrix",
    # Protocol
    "ResonanceProtocol",
    # Implementation
    "ResonanceEngine",
    # Global
    "get_resonance_engine",
    "resonate",
    "resolve",
]
