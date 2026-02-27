"""
ŚIKṢĀṢṬAKAM SYNTH - The Holographic Layer
=========================================

"paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"
"Let there be all victory for the chanting of the holy name of Lord Kṛṣṇa!"
— Śikṣāṣṭakam Verse 1

This layer bridges:
  - MahaKirtan (7-beat pattern: 1911-1977)
  - Siksastakam (7 effects of Verse 1)
  - Multimodal output (Guna/color/illumination)

THE 7 EFFECTS MAP TO 7 BEATS:
  Beat 1 (1911): CLEANSE_HEART_MIRROR    → Cache invalidation
  Beat 2 (1922): EXTINGUISH_FOREST_FIRE  → Zero entropy routing
  Beat 3 (1933): SPREAD_MOONLIGHT        → Graceful degradation
  Beat 4 (1944): LIFE_OF_KNOWLEDGE       → Live data structures
  Beat 5 (1955): EXPAND_BLISS_OCEAN      → Infinite scalability
  Beat 6 (1966): FULL_NECTAR_EACH_STEP   → Atomic transactions
  Beat 7 (1977): BATHE_ENTIRE_SELF       → Total transformation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    PANCHA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TRINITY,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.mantra.maha_kirtan import KirtanComputeResult

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xbf879742"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final

from .engineering import (
    ENGINEERING_EFFECTS,
    SankirtanaEffect,
)

# 512-BIT INTEGRATION
CHAITANYA_512_B: Final[int] = 512  # Chaitanya mode


# Guna-based colors (sRGB hex values)
GUNA_COLORS: Final[dict[str, str]] = {
    "sattva": "#FFFFFF",  # White - purity, goodness
    "rajas": "#FF4444",  # Red - passion, activity
    "tamas": "#222244",  # Dark blue - ignorance, inertia
    "moonlight": "#C0C0E0",  # Silver - gentle illumination
    "sunlight": "#FFD700",  # Gold - intense illumination
    "nectar": "#FFD700",  # Gold - amrita (nectar)
    "ocean": "#0066CC",  # Ocean blue - ananda (bliss)
    "lotus": "#FF69B4",  # Pink - padma (lotus)
}

# Beat-to-Effect mapping (7 beats → 7 effects)
BEAT_EFFECT_MAP: Final[dict[int, str]] = {
    KSETRAJNA: "CLEANSE_HEART_MIRROR",  # 1911 - Cache invalidation
    HALVES: "EXTINGUISH_FOREST_FIRE",  # 1922 - Zero entropy routing
    TRINITY: "SPREAD_MOONLIGHT",  # 1933 - Graceful degradation
    QUARTERS: "LIFE_OF_KNOWLEDGE",  # 1944 - Live data structures
    PANCHA: "EXPAND_BLISS_OCEAN",  # 1955 - Infinite scalability
    SHARANAGATI: "FULL_NECTAR_EACH_STEP",  # 1966 - Atomic transactions
    SEVEN: "BATHE_ENTIRE_SELF",  # 1977 - Total transformation
}

# Effect-to-Color mapping (7 effects → colors)
EFFECT_COLOR_MAP: Final[dict[str, str]] = {
    "CLEANSE_HEART_MIRROR": "#FFFFFF",  # White - purification
    "EXTINGUISH_FOREST_FIRE": "#0088FF",  # Cool blue - cooling
    "SPREAD_MOONLIGHT": "#C0C0E0",  # Silver - moonlight
    "LIFE_OF_KNOWLEDGE": "#FFFF00",  # Yellow - vidya (knowledge)
    "EXPAND_BLISS_OCEAN": "#0066CC",  # Ocean blue - ananda
    "FULL_NECTAR_EACH_STEP": "#FFD700",  # Gold - amrita
    "BATHE_ENTIRE_SELF": "#FF69B4",  # Pink → White gradient
}


@dataclass(frozen=True)
class SiksastakamOutput:
    """Multimodal output from Siksastakam synthesis."""

    # Siksastakam effect
    effect_name: str  # e.g., "CLEANSE_HEART_MIRROR"
    effect_sanskrit: str  # e.g., "ceto-darpaṇa-mārjanaṁ"
    engineering_principle: str  # e.g., "CACHE INVALIDATION"
    complexity_class: str  # e.g., "O(1)"

    # Color/Visual output
    color_hex: str  # sRGB hex color
    guna: str  # sattva/rajas/tamas

    # Illumination mode
    illumination: str  # "moonlight" or "sunlight"
    intensity: float  # 0.0-1.0

    # 512-bit integration
    bits_output: int  # 32 bits per step
    bit_pattern: int  # The actual bit pattern


class SiksastakamSynth:
    """
    Siksastakam Synthesizer - The Holographic Layer.

    Bridges MahaKirtan's 7-beat pattern with Siksastakam's 7 effects
    to produce multimodal output (numerical + color + illumination).

    512-BIT MODE:
        synth = SiksastakamSynth(use_512=True)
        # Each beat outputs 32-bit pattern
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "siksastakam_synth"

    def __init__(self, use_512: bool = False) -> None:
        """
        Initialize Siksastakam Synthesizer.

        Args:
            use_512: If True, use 512-bit mod space for "wide" mode
        """
        self.use_512 = use_512
        self.mod_space = CHAITANYA_512_B if use_512 else MAHA_QUANTUM

    def get_effect_for_beat(self, beat_number: int) -> str:
        """Get Siksastakam effect name for a beat number (1-7)."""
        if beat_number < KSETRAJNA or beat_number > SEVEN:
            return "BATHE_ENTIRE_SELF"  # Default to complete effect
        return BEAT_EFFECT_MAP[beat_number]

    def get_color_for_effect(self, effect_name: str) -> str:
        """Get color hex for an effect."""
        return EFFECT_COLOR_MAP.get(effect_name, GUNA_COLORS["sattva"])

    def get_illumination(self, resonance: float) -> str:
        """
        Determine illumination type based on resonance.

        Moonlight = gentle, efficient (high resonance, O(1))
        Sunlight = intense, brute force (low resonance, O(n))
        """
        # High resonance = moonlight (efficient), low = still building
        return "moonlight" if resonance > 0.3 else "sunlight"

    def get_guna(self, effect_name: str, resonance: float) -> str:
        """
        Determine predominant Guna based on effect and resonance.

        All Siksastakam effects lead to Sattva (goodness).
        Low resonance indicates Rajas (activity to reach Sattva).
        """
        if resonance > 0.5:
            return "sattva"
        elif resonance > 0.2:
            return "rajas"  # Still working toward sattva
        return "sattva"  # Even low resonance chanting is sattvic

    def synthesize(self, beat_number: int, seed: int, resonance: float = 0.5) -> SiksastakamOutput:
        """
        Synthesize multimodal output for a beat.

        Mapping:
            Beat Number -> Siksastakam Effect
            Effect -> Color & Guna
            Resonance -> Illumination intensity
            Seed -> Bit pattern
        """
        # 1. Get Effect
        effect_name = self.get_effect_for_beat(beat_number)

        # 2. Get Engineering Metadata (from engineering.py)
        try:
            enum_effect = getattr(SankirtanaEffect, effect_name)
            meta = ENGINEERING_EFFECTS[enum_effect]
            sanskrit = meta.sanskrit
            principle = meta.computing_principle
            complexity = meta.complexity_after
        except (AttributeError, KeyError):
            # Fallback
            sanskrit = "Unknown"
            principle = "Unknown"
            complexity = "O(?)"

        # 3. Get Color & Guna
        color = self.get_color_for_effect(effect_name)
        guna = self.get_guna(effect_name, resonance)

        # 4. Get Illumination
        illumination = self.get_illumination(resonance)

        # 5. Get Bit Pattern (Holographic)
        # Use seed + beat to generate deterministic pattern
        # If 512-bit mode, we want 32 bits. If normal, 8 bits (byte).
        # Actually SiksastakamOutput has bits_output (int).

        # Bit generation logic:
        # Mix seed with beat identifier
        mixed_seed = (seed * beat_number + SEVEN) % (HALVES**32)
        bit_pattern = mixed_seed

        return SiksastakamOutput(
            effect_name=effect_name,
            effect_sanskrit=sanskrit,
            engineering_principle=principle,
            complexity_class=complexity,
            color_hex=color,
            guna=guna,
            illumination=illumination,
            intensity=resonance,
            bits_output=32 if self.use_512 else HARE_COUNT,
            bit_pattern=bit_pattern,
        )

    def synthesize_from_result(self, kirtan_result: KirtanComputeResult) -> SiksastakamOutput:
        """Synthesize from a MahaKirtan result."""
        # Note: KirtanComputeResult must be imported only for type checking to avoid circular dep
        # But we assume the object has beat_number, seed, resonance
        return self.synthesize(
            beat_number=getattr(kirtan_result, "beat_number", KSETRAJNA),
            seed=getattr(kirtan_result, "input_seed", 0),
            resonance=getattr(kirtan_result, "resonance", 0.5),
        )
