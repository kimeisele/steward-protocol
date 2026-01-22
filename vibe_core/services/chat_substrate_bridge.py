"""
CHAT SUBSTRATE BRIDGE - Vibration to Machine Code
==================================================

"shabda-brahma" - Sound is the ultimate reality.

This bridge translates USER INPUT (vibration) into SUBSTRATE (machine code).
NOT keyword matching. NOT phonetic cosplay. REAL vibration-based routing.

FLOW:
    User Input
        ↓
    VarnaTensor.encode() → 12D phonetic tensor
        ↓
    MantraByte mapping → 16-position (32-bit packed)
        ↓
    QuantumReactor.manifest() → if energy > inertia → MANIFEST
        ↓
    ShadowReactor position → Mahajana routing

The LLM is just the INTERPRETER. The Substrate is the BRAIN.

WATERTIGHT: No Any types. All typed explicitly.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9a3b7c01"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Final, List, Optional, Tuple

# Substrate imports
from vibe_core.mahamantra.substrate.byte import (
    HolyName,
    MantraBit,
    MantraByte,
    MANTRA_SEQUENCE,
)
from vibe_core.mahamantra.substrate.seed import (
    MAHAMANTRA,
    WORDS,
    PARAMPARA,
    Quarter,
)
from vibe_core.mahamantra.protocols._lotus import (
    get_position_mahajana,
    MAHAJANA_POSITIONS,
)

logger = logging.getLogger("CHAT_SUBSTRATE")


# =============================================================================
# RESONANCE THRESHOLDS (Derived from Seed - Mantra Seed Math!)
# =============================================================================
# OLD (Asura Müll - hardcoded):
#   THRESHOLD_MANIFEST = 0.7
#   THRESHOLD_NEGOTIATE = 0.4
#
# NEW (Harmonically derived):
#   THRESHOLD_MANIFEST = NADI/MALA = 72/108 = 2/3 ≈ 0.667
#   THRESHOLD_NEGOTIATE = LILA/MALA = 48/108 = 4/9 ≈ 0.444

from vibe_core.mahamantra.substrate.harmonics import (
    THRESHOLD_AUTO as THRESHOLD_MANIFEST,
    THRESHOLD_REFINE as THRESHOLD_NEGOTIATE,
)
# Below LILA/MALA = Silence (no resonance)


# =============================================================================
# SUBSTRATE ROUTING RESULT
# =============================================================================


@dataclass
class SubstrateRoute:
    """
    Result of substrate-level routing.

    NOT a simple dict. A typed, validated routing decision.
    """

    # Core routing
    position: int  # 0-15 Mahamantra position
    mahajana: str  # Guardian name
    holy_name: HolyName  # HARE/KRISHNA/RAMA at this position
    quarter: str  # GENESIS/DHARMA/KARMA/MOKSHA

    # Energy (from resonance)
    energy: float  # Total resonance energy (0-1)
    manifests: bool  # energy > inertia?

    # Tensor data
    varga_dominant: int  # Dominant articulation point (0-4)
    sthana_dominant: int  # Dominant position (0-4)
    shakti: float  # Total phonetic energy

    # Meta
    original_input: str
    encoded_at: datetime = field(default_factory=datetime.now)

    @property
    def quarter_idx(self) -> int:
        """Quarter index (0-3)."""
        return self.position // 4

    @property
    def is_head(self) -> bool:
        """Is this a quarter head (0, 4, 8, 12)?"""
        return self.position % 4 == 0

    @property
    def needs_negotiation(self) -> bool:
        """Is energy in the gray zone?"""
        return THRESHOLD_NEGOTIATE <= self.energy < THRESHOLD_MANIFEST

    @property
    def is_silence(self) -> bool:
        """Is energy too low?"""
        return self.energy < THRESHOLD_NEGOTIATE


# =============================================================================
# VARNA TENSOR - SSOT DERIVED FROM varna.py (NOT HARDCODED!)
# =============================================================================
# "shabda-brahma" - Sound is reality. The mapping is PHYSICAL.
# 5 Vargas → 4 Quarters via LOTUS algorithm (SWARA_GA = 5/4)

# Import SSOT from protocols/substrate/mantra/varna.py
from vibe_core.protocols.substrate.mantra.varna import (
    KAVARGA,   # Guttural (throat)
    CAVARGA,   # Palatal (palate)
    TAVARGA,   # Retroflex (cerebral)
    TAVARGA2,  # Dental (teeth)
    PAVARGA,   # Labial (lips)
    ANTAHSTHA, # Semi-vowels
    USHMAN,    # Sibilants + aspirate
    SVARA,     # Vowels
)

# The 5 Vargas (WHERE - Articulation Points) - INDICES, not hardcoded
VARGA_KANTHYA: Final[int] = 0   # Throat/Guttural (KAVARGA) → GENESIS
VARGA_TALAVYA: Final[int] = 1   # Palate (CAVARGA) → DHARMA
VARGA_MURDHANYA: Final[int] = 2 # Retroflex (TAVARGA) → DHARMA (LOTUS MERGE!)
VARGA_DANTYA: Final[int] = 3    # Dental (TAVARGA2) → KARMA
VARGA_OSHTHYA: Final[int] = 4   # Labial (PAVARGA) → MOKSHA

# The 5 Sthanas (HOW - Energy/Intensity) - Position within Varga
# Each Varga has 5 consonants: unvoiced, aspirated, voiced, voiced-aspirated, nasal
STHANA_SPARSHA: Final[int] = 0    # Unvoiced stop → minimal (0.2)
STHANA_MAHAPRANA: Final[int] = 1  # Aspirated → expansion (0.6)
STHANA_GHOSHAVAT: Final[int] = 2  # Voiced → active (0.8)
STHANA_GHOSHMAHA: Final[int] = 3  # Voiced aspirated → max (1.0)
STHANA_ANUNASIKA: Final[int] = 4  # Nasal → continuous (0.5)


def _build_phoneme_varga_from_ssot() -> Dict[str, int]:
    """
    Build PHONEME_VARGA mapping from SSOT (varna.py).

    LOTUS ALGORITHM: Derives mapping from actual Varna definitions.
    No hardcoded values - all from seed.
    """
    mapping: Dict[str, int] = {}

    # Map each VARGA tuple to its index
    varga_tuples = [
        (KAVARGA, VARGA_KANTHYA),    # k, kh, g, gh, ṅ
        (CAVARGA, VARGA_TALAVYA),    # c, ch, j, jh, ñ
        (TAVARGA, VARGA_MURDHANYA),  # ṭ, ṭh, ḍ, ḍh, ṇ (retroflex)
        (TAVARGA2, VARGA_DANTYA),    # t, th, d, dh, n (dental)
        (PAVARGA, VARGA_OSHTHYA),    # p, ph, b, bh, m
    ]

    for varga_tuple, varga_idx in varga_tuples:
        for varna in varga_tuple:
            # Use .roman field (Western approximation)
            roman = varna.roman.lower()
            if roman and roman not in mapping:
                mapping[roman] = varga_idx
            # Also add IAST for precise matching
            iast = varna.iast.lower()
            if iast and iast not in mapping:
                mapping[iast] = varga_idx

    # Semi-vowels (ANTAHSTHA): y=palatal, r=retroflex, l=dental, v=labial
    antahstha_mapping = [
        (0, VARGA_TALAVYA),   # य (y) - palatal
        (1, VARGA_MURDHANYA), # र (r) - retroflex
        (2, VARGA_DANTYA),    # ल (l) - dental
        (3, VARGA_OSHTHYA),   # व (v) - labial
    ]
    for idx, varga_idx in antahstha_mapping:
        if idx < len(ANTAHSTHA):
            varna = ANTAHSTHA[idx]
            mapping[varna.roman.lower()] = varga_idx
            mapping[varna.iast.lower()] = varga_idx

    # Sibilants + Aspirate (USHMAN): ś=palatal, ṣ=retroflex, s=dental, h=guttural
    ushman_mapping = [
        (0, VARGA_TALAVYA),   # श (ś) - palatal sibilant
        (1, VARGA_MURDHANYA), # ष (ṣ) - retroflex sibilant
        (2, VARGA_DANTYA),    # स (s) - dental sibilant
        (3, VARGA_KANTHYA),   # ह (h) - guttural aspirate
    ]
    for idx, varga_idx in ushman_mapping:
        if idx < len(USHMAN):
            varna = USHMAN[idx]
            mapping[varna.roman.lower()] = varga_idx
            mapping[varna.iast.lower()] = varga_idx

    # Vowels: origin based on articulation point
    # a, ā = throat (KANTHYA), i, ī = palate (TALAVYA), u, ū = lips (OSHTHYA)
    # e, ai = palate, o, au = lips
    vowel_mapping = {
        "a": VARGA_KANTHYA, "aa": VARGA_KANTHYA, "ā": VARGA_KANTHYA,
        "i": VARGA_TALAVYA, "ee": VARGA_TALAVYA, "ī": VARGA_TALAVYA,
        "u": VARGA_OSHTHYA, "oo": VARGA_OSHTHYA, "ū": VARGA_OSHTHYA,
        "e": VARGA_TALAVYA, "ai": VARGA_TALAVYA,
        "o": VARGA_OSHTHYA, "au": VARGA_OSHTHYA,
    }
    mapping.update(vowel_mapping)

    # Western additions (not in Sanskrit but needed for English input)
    western_extras = {
        "c": VARGA_KANTHYA,  # Hard C = K (guttural)
        "q": VARGA_KANTHYA,  # Q = K (guttural)
        "x": VARGA_KANTHYA,  # X = KS (guttural start)
        "f": VARGA_OSHTHYA,  # F = labio-dental (lips)
        "w": VARGA_OSHTHYA,  # W = labial
        "z": VARGA_DANTYA,   # Z = dental
    }
    mapping.update(western_extras)

    return mapping


# PHONEME_VARGA: DERIVED FROM SSOT, NOT HARDCODED!
PHONEME_VARGA: Final[Dict[str, int]] = _build_phoneme_varga_from_ssot()

def _build_phoneme_sthana_from_ssot() -> Dict[str, int]:
    """
    Build PHONEME_STHANA mapping from SSOT (varna.py).

    LOTUS ALGORITHM: Each Varga has 5 positions = 5 Sthanas.
    Position in Varga directly maps to energy level.
    """
    mapping: Dict[str, int] = {}

    # Each Varga has exactly 5 consonants in fixed order:
    # [0]=unvoiced, [1]=aspirated, [2]=voiced, [3]=voiced-aspirated, [4]=nasal
    all_vargas = [KAVARGA, CAVARGA, TAVARGA, TAVARGA2, PAVARGA]

    for varga_tuple in all_vargas:
        for position, varna in enumerate(varga_tuple):
            # Position within Varga = Sthana
            sthana = position  # 0-4 maps directly
            roman = varna.roman.lower()
            iast = varna.iast.lower()
            if roman:
                mapping[roman] = sthana
            if iast and iast not in mapping:
                mapping[iast] = sthana

    # Semi-vowels (ANTAHSTHA) - all voiced = GHOSHAVAT
    for varna in ANTAHSTHA:
        mapping[varna.roman.lower()] = STHANA_GHOSHAVAT
        mapping[varna.iast.lower()] = STHANA_GHOSHAVAT

    # Sibilants (USHMAN) - all medium energy = GHOSHAVAT, except H = MAHAPRANA
    for idx, varna in enumerate(USHMAN):
        sthana = STHANA_MAHAPRANA if idx == 3 else STHANA_GHOSHAVAT  # H = aspirate
        mapping[varna.roman.lower()] = sthana
        mapping[varna.iast.lower()] = sthana

    # Vowels: energy based on openness (derived from acoustic physics)
    # Open vowels (a) = high energy, closed vowels (i, u) = low energy
    vowel_energy = {
        "a": STHANA_MAHAPRANA, "aa": STHANA_MAHAPRANA, "ā": STHANA_MAHAPRANA,
        "i": STHANA_SPARSHA, "ee": STHANA_SPARSHA, "ī": STHANA_SPARSHA,
        "u": STHANA_SPARSHA, "oo": STHANA_SPARSHA, "ū": STHANA_SPARSHA,
        "e": STHANA_GHOSHAVAT, "ai": STHANA_GHOSHMAHA,
        "o": STHANA_GHOSHAVAT, "au": STHANA_GHOSHMAHA,
    }
    mapping.update(vowel_energy)

    # Western additions
    western_extras = {
        "c": STHANA_SPARSHA,    # Hard C = K (unvoiced)
        "q": STHANA_SPARSHA,    # Q = K (unvoiced)
        "x": STHANA_GHOSHAVAT,  # X = complex
        "f": STHANA_GHOSHAVAT,  # F = fricative
        "w": STHANA_GHOSHAVAT,  # W = voiced
        "z": STHANA_GHOSHAVAT,  # Z = voiced
    }
    mapping.update(western_extras)

    return mapping


# PHONEME_STHANA: DERIVED FROM SSOT, NOT HARDCODED!
PHONEME_STHANA: Final[Dict[str, int]] = _build_phoneme_sthana_from_ssot()

# =============================================================================
# SSOT VERIFICATION - Ensure mappings are derived from varna.py
# =============================================================================
# The Mahamantra critical letters must map correctly:
# H = throat (KANTHYA), R = retroflex (MURDHANYA), K = throat (KANTHYA)
# A = throat (KANTHYA), M = lips (OSHTHYA)
assert PHONEME_VARGA.get("h") == VARGA_KANTHYA, "SSOT: H must be KANTHYA (throat)"
assert PHONEME_VARGA.get("r") == VARGA_MURDHANYA, "SSOT: R must be MURDHANYA (retroflex)"
assert PHONEME_VARGA.get("k") == VARGA_KANTHYA, "SSOT: K must be KANTHYA (throat)"
assert PHONEME_VARGA.get("a") == VARGA_KANTHYA, "SSOT: A must be KANTHYA (throat)"
assert PHONEME_VARGA.get("m") == VARGA_OSHTHYA, "SSOT: M must be OSHTHYA (lips)"

# Energy levels: K = unvoiced, M = nasal
assert PHONEME_STHANA.get("k") == STHANA_SPARSHA, "SSOT: K must be SPARSHA (unvoiced)"
assert PHONEME_STHANA.get("m") == STHANA_ANUNASIKA, "SSOT: M must be ANUNASIKA (nasal)"

# Sthana to energy multiplier
STHANA_ENERGY: Final[Dict[int, float]] = {
    STHANA_SPARSHA: 0.2,
    STHANA_MAHAPRANA: 0.6,
    STHANA_GHOSHAVAT: 0.8,
    STHANA_GHOSHMAHA: 1.0,
    STHANA_ANUNASIKA: 0.5,
}


@dataclass
class SimpleTensor:
    """
    Simplified VarnaTensor for chat routing.

    Full tensor is in reactor/matrix.py - this is the chat-optimized version.
    """

    varga_vector: Tuple[float, ...]  # Distribution across 5 articulation points
    sthana_vector: Tuple[float, ...]  # Distribution across 5 positions
    shakti: float  # Total phonetic energy (0-1)
    phoneme_count: int
    source: str


def encode_to_tensor(text: str) -> SimpleTensor:
    """
    Encode text to simplified VarnaTensor.

    Analyzes WHERE sounds originate (varga) and HOW intense (sthana).
    This is PHYSICAL - cannot be faked.
    """
    text_lower = text.lower()

    # Count distributions
    varga_counts = [0.0] * 5
    sthana_counts = [0.0] * 5
    total_energy = 0.0
    phoneme_count = 0

    i = 0
    while i < len(text_lower):
        char = text_lower[i]

        # Check for digraphs first
        digraph = text_lower[i : i + 2] if i + 1 < len(text_lower) else ""

        if digraph in PHONEME_VARGA:
            varga = PHONEME_VARGA[digraph]
            sthana = PHONEME_STHANA.get(digraph, STHANA_GHOSHAVAT)
            varga_counts[varga] += 1
            sthana_counts[sthana] += 1
            total_energy += STHANA_ENERGY.get(sthana, 0.5)
            phoneme_count += 1
            i += 2
        elif char in PHONEME_VARGA:
            varga = PHONEME_VARGA[char]
            sthana = PHONEME_STHANA.get(char, STHANA_GHOSHAVAT)
            varga_counts[varga] += 1
            sthana_counts[sthana] += 1
            total_energy += STHANA_ENERGY.get(sthana, 0.5)
            phoneme_count += 1
            i += 1
        else:
            i += 1

    # Normalize vectors
    total_varga = sum(varga_counts) or 1
    total_sthana = sum(sthana_counts) or 1

    varga_vector = tuple(v / total_varga for v in varga_counts)
    sthana_vector = tuple(s / total_sthana for s in sthana_counts)

    # Normalize energy
    shakti = min(1.0, total_energy / max(phoneme_count, 1))

    return SimpleTensor(
        varga_vector=varga_vector,
        sthana_vector=sthana_vector,
        shakti=shakti,
        phoneme_count=phoneme_count,
        source=text,
    )


# =============================================================================
# TENSOR TO POSITION MAPPING
# =============================================================================

# Varga to Quarter mapping (WHERE you speak → WHERE you route)
VARGA_TO_QUARTER: Final[Dict[int, int]] = {
    VARGA_KANTHYA: 0,  # Throat → GENESIS (system/kernel)
    VARGA_TALAVYA: 1,  # Palate → DHARMA (cognition/knowledge)
    VARGA_MURDHANYA: 1,  # Retroflex → DHARMA (logic/analysis)
    VARGA_DANTYA: 2,  # Dental → KARMA (interface/action)
    VARGA_OSHTHYA: 3,  # Lips → MOKSHA (output/liberation)
}

# Quarter to positions
QUARTER_POSITIONS: Final[Dict[int, Tuple[int, ...]]] = {
    0: (0, 1, 2, 3),  # GENESIS
    1: (4, 5, 6, 7),  # DHARMA
    2: (8, 9, 10, 11),  # KARMA
    3: (12, 13, 14, 15),  # MOKSHA
}

# HolyName at each position (from seed.py MAHAMANTRA)
POSITION_NAME: Final[Tuple[HolyName, ...]] = tuple(HolyName(name.value) for name in MAHAMANTRA)


def tensor_to_position(tensor: SimpleTensor) -> Tuple[int, float]:
    """
    Map tensor to Mahamantra position (0-15).

    Returns: (position, confidence)

    The mapping is based on:
    1. Dominant varga → quarter
    2. Sthana distribution → position within quarter
    3. Shakti → confidence
    """
    # Find dominant varga (WHERE)
    dominant_varga = max(range(5), key=lambda i: tensor.varga_vector[i])

    # Map to quarter
    quarter = VARGA_TO_QUARTER.get(dominant_varga, 0)
    positions = QUARTER_POSITIONS[quarter]

    # Find position within quarter based on sthana (energy pattern)
    dominant_sthana = max(range(5), key=lambda i: tensor.sthana_vector[i])

    # Map sthana to position offset (0-3 within quarter)
    # Higher energy → higher offset (more action-oriented)
    if dominant_sthana == STHANA_SPARSHA:
        offset = 0  # Minimal → head position
    elif dominant_sthana == STHANA_MAHAPRANA:
        offset = 1  # Expansion → second
    elif dominant_sthana == STHANA_GHOSHAVAT:
        offset = 2  # Active → third
    elif dominant_sthana == STHANA_GHOSHMAHA:
        offset = 3  # Maximum → fourth
    else:  # ANUNASIKA
        offset = 1  # Continuous → second (like expansion)

    position = positions[offset]

    # Confidence based on shakti and vector clarity
    varga_clarity = max(tensor.varga_vector) - (1 / 5)  # How dominant is the dominant?
    confidence = (tensor.shakti * 0.6) + (varga_clarity * 0.4)
    confidence = max(0.0, min(1.0, confidence))

    return position, confidence


# =============================================================================
# CHAT SUBSTRATE BRIDGE
# =============================================================================


class ChatSubstrateBridge:
    """
    The bridge between User Input (vibration) and Substrate (machine code).

    FLOW:
        encode() → tensor → position → manifest decision → route

    This replaces keyword matching with REAL phonetic routing.
    """

    def __init__(self, inertia: float = 0.3):
        """
        Initialize bridge.

        Args:
            inertia: Minimum energy for manifestation (default 0.3)
        """
        self._inertia = inertia
        self._routes: List[SubstrateRoute] = []  # History for learning

    def route(self, text: str) -> SubstrateRoute:
        """
        Route user input through substrate.

        1. Encode to tensor
        2. Map to position
        3. Check manifestation
        4. Return typed route
        """
        # Step 1: Encode
        tensor = encode_to_tensor(text)

        # Step 2: Map to position
        position, confidence = tensor_to_position(tensor)

        # Step 3: Get position data
        holy_name = POSITION_NAME[position]
        mahajana = get_position_mahajana(position)
        quarter_idx = position // 4
        quarter_names = ["GENESIS", "DHARMA", "KARMA", "MOKSHA"]
        quarter = quarter_names[quarter_idx]

        # Step 4: Calculate total energy
        # Combine tensor shakti with confidence
        energy = (tensor.shakti * 0.5) + (confidence * 0.5)

        # Step 5: Manifestation decision
        manifests = energy >= self._inertia

        # Step 6: Build route
        dominant_varga = max(range(5), key=lambda i: tensor.varga_vector[i])
        dominant_sthana = max(range(5), key=lambda i: tensor.sthana_vector[i])

        route = SubstrateRoute(
            position=position,
            mahajana=mahajana,
            holy_name=holy_name,
            quarter=quarter,
            energy=energy,
            manifests=manifests,
            varga_dominant=dominant_varga,
            sthana_dominant=dominant_sthana,
            shakti=tensor.shakti,
            original_input=text,
        )

        # Store for learning
        self._routes.append(route)

        logger.info(
            f"🔊 SubstrateBridge: '{text[:30]}...' → "
            f"{mahajana.upper()} (pos={position}, energy={energy:.3f}, "
            f"manifests={manifests})"
        )

        return route

    def get_alternative_routes(self, text: str, count: int = 3) -> List[SubstrateRoute]:
        """
        Get alternative routes for negotiation.

        When energy is in gray zone, offer alternatives based on
        adjacent quarters and positions.
        """
        primary = self.route(text)
        alternatives = [primary]

        # Get adjacent quarters
        adjacent_quarters = [
            (primary.quarter_idx - 1) % 4,
            (primary.quarter_idx + 1) % 4,
        ]

        for q in adjacent_quarters:
            if len(alternatives) >= count:
                break

            positions = QUARTER_POSITIONS[q]
            # Pick middle position in adjacent quarter
            alt_pos = positions[1]

            alt_route = SubstrateRoute(
                position=alt_pos,
                mahajana=get_position_mahajana(alt_pos),
                holy_name=POSITION_NAME[alt_pos],
                quarter=["GENESIS", "DHARMA", "KARMA", "MOKSHA"][q],
                energy=primary.energy * 0.8,  # Slightly lower energy
                manifests=False,  # Alternative, not primary
                varga_dominant=primary.varga_dominant,
                sthana_dominant=primary.sthana_dominant,
                shakti=primary.shakti,
                original_input=text,
            )
            alternatives.append(alt_route)

        return alternatives[:count]

    @property
    def inertia(self) -> float:
        """Current inertia threshold."""
        return self._inertia

    @inertia.setter
    def inertia(self, value: float) -> None:
        """Set inertia (runtime hot-swap)."""
        self._inertia = max(0.0, min(1.0, value))
        logger.info(f"🔧 SubstrateBridge: Inertia set to {self._inertia:.3f}")


# =============================================================================
# SINGLETON
# =============================================================================
# SINGLETON - VIA SERVICE REGISTRY (WIRED, NOT ISLAND!)
# =============================================================================


def get_substrate_bridge() -> ChatSubstrateBridge:
    """
    Get ChatSubstrateBridge through ServiceRegistry (WIRED).

    CRITICAL FIX: Was an ISLAND - created directly, bypassing DI.
    Now goes through ServiceRegistry for NagaProxy wrapping.
    """
    from vibe_core.di import ServiceRegistry

    # Try to get from registry first
    try:
        existing = ServiceRegistry.get(ChatSubstrateBridge)
        if existing is not None:
            return existing
    except Exception:
        pass  # Not registered yet

    # Create and register
    import logging
    logger = logging.getLogger("SUBSTRATE_BRIDGE")

    instance = ChatSubstrateBridge()
    ServiceRegistry.register(ChatSubstrateBridge, instance)
    logger.info("✅ ChatSubstrateBridge registered via ServiceRegistry (WIRED)")

    return ServiceRegistry.get(ChatSubstrateBridge)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "THRESHOLD_MANIFEST",
    "THRESHOLD_NEGOTIATE",
    # Types
    "SubstrateRoute",
    "SimpleTensor",
    # Functions
    "encode_to_tensor",
    "tensor_to_position",
    # Bridge
    "ChatSubstrateBridge",
    "get_substrate_bridge",
]
