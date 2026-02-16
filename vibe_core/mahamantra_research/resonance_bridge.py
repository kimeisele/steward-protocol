"""
RESONANCE BRIDGE — Inner Chamber → Outer World
================================================

"kirtanīyaḥ sadā hariḥ"
"One should always chant the holy name of the Lord."
— Chaitanya Charitamrita, Adi 17.31

The inner chamber (Antaranga/Kirtan) generates energy.
The outer chamber (Sankirtana) distributes it.
This bridge is the clean, typed interface between them.

NO DIRTY COUPLING. The bridge is a Protocol.
Inner and outer chambers don't import each other.
They communicate through typed, frozen packets.

ENERGY FLOW:
    EngineResult → ResonancePacket → MantraIntent
    (inner)        (bridge)          (outer)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Final, Protocol, Tuple

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHA_QUANTUM,
    QUARTERS,
    SEVEN,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 7
__genesis__ = "0xf3018ef4"  # GenesisByte: parampara % 37 == 0


# =============================================================================
# GUNA MAPPING (from intent_from_seed.py — PROVEN)
# =============================================================================
# The 4 Quarters of the Mahamantra ARE the 4 Gunas.
# Q1 (pos 0-3)   = SUDDHA — pure intent, transcendental
# Q2 (pos 4-7)   = SATTVA — sanctioned, goodness
# Q3 (pos 8-11)  = RAJAS  — material execution, passion
# Q4 (pos 12-15) = TAMAS  — karmic consequence, ignorance

GUNA_NAMES: Final[Tuple[str, str, str, str]] = (
    "suddha", "sattva", "rajas", "tamas",
)

# Guna → IntentType mapping (from kernel/intent.py IntentType enum values)
# Each guna maps to the PRIMARY intent type for that quarter.
GUNA_TO_INTENT_TYPE: Final[Dict[str, str]] = {
    "suddha": "wake",       # Q1: genesis, initialization
    "sattva": "resolve",    # Q2: dharma, sanctioned resolution
    "rajas": "transform",   # Q3: karma, material execution
    "tamas": "heal",        # Q4: moksha, karmic consequence → healing
}


# =============================================================================
# RESONANCE PACKET — What the inner chamber emits
# =============================================================================


@dataclass(frozen=True)
class ResonancePacket:
    """Typed, immutable summary of inner chamber resonance.

    This is NOT the full EngineResult. It's the clean, minimal packet
    that the outer world needs to route and act on the inner energy.
    """

    # Identity
    seed: int                              # compressed input hash
    attractor: int                         # fixed-point attractor
    position: int                          # seed % 16 → grid position

    # Energy
    prana: int                             # total Antaranga prana
    active_slots: int                      # number of live slots

    # Routing
    guardian: str                          # Mahajana name (from routing)
    quarter: int                           # position // 4 → which quarter
    guna: str                              # suddha/sattva/rajas/tamas

    # Fractal
    branch_energies: Tuple[int, int, int]  # (DHARMA, GENESIS, KARMA) prana
    tree_depth: int                        # fractal tree depth

    # Semantic
    mode_words: Dict[str, Tuple[str, ...]]  # mode → top word meanings
    verse_ref: str                         # BG.18.N

    # Raw coords (for spell_kirtan)
    rama_coords: Tuple[int, ...]           # character wave RAMA coordinates

    # Derived intent
    intent_type: str                       # from guna → IntentType mapping

    @property
    def is_transcendental(self) -> bool:
        """True if in the SUDDHA quarter (pure intent)."""
        return self.guna == "suddha"

    @property
    def dominant_mode(self) -> str:
        """Which fractal branch has the most energy."""
        d, g, k = self.branch_energies
        if d >= g and d >= k:
            return "DHARMA"
        if g >= d and g >= k:
            return "GENESIS"
        return "KARMA"


# =============================================================================
# BRIDGE PROTOCOL — Clean interface, no dirty coupling
# =============================================================================


class ResonanceBridgeProtocol(Protocol):
    """Clean interface between inner and outer chambers."""

    def emit(self, engine_result: object) -> ResonancePacket:
        """Compress engine result into a clean packet."""
        ...

    def to_intent_kwargs(self, packet: ResonancePacket, target: str) -> Dict:
        """Convert resonance packet to MantraIntent constructor kwargs.

        Returns a dict suitable for MantraIntent(**kwargs).
        Does NOT import MantraIntent — the caller does that.
        This keeps the bridge free of production imports.
        """
        ...


# =============================================================================
# BRIDGE IMPLEMENTATION
# =============================================================================


class ResonanceBridge:
    """Converts inner chamber output to typed packets and intent kwargs.

    NO production imports. Only uses protocol constants and the
    EngineResult NamedTuple fields (accessed by name, not by type).
    """

    def emit(self, engine_result: object) -> ResonancePacket:
        """Compress EngineResult into a ResonancePacket.

        Accesses EngineResult fields by attribute name (duck typing).
        Does NOT import EngineResult — works with any object that has
        the right fields.
        """
        r = engine_result

        seed = getattr(r, "seed", 0)
        attractor = getattr(r, "attractor", 0)
        position = seed % WORDS
        quarter = position // QUARTERS
        guna = GUNA_NAMES[quarter]

        # Extract branch energies from derivation string (sprout stats)
        # The fractal tree produces 3 branches with prana values.
        # For now, derive from the mode words in the output.
        prana = getattr(r, "antaranga_prana", 0)
        active = getattr(r, "antaranga_active", 0)

        # Branch energy approximation: distribute prana by position
        # DHARMA = Q2 energy, GENESIS = Q1 energy, KARMA = Q3 energy
        dharma_e = (attractor * SEVEN) % (prana + KSETRAJNA)
        genesis_e = (seed * SEVEN) % (prana + KSETRAJNA)
        karma_e = max(0, prana - dharma_e - genesis_e)

        # Extract mode words from resonant_words
        resonant = getattr(r, "resonant_words", ())
        mode_words: Dict[str, Tuple[str, ...]] = {
            "DHARMA": (),
            "GENESIS": (),
            "KARMA": (),
        }
        if resonant:
            # Split resonant words into mode buckets by position
            d_words, g_words, k_words = [], [], []
            for i, rw in enumerate(resonant):
                meaning = rw[1] if len(rw) > 1 else ""
                if meaning:
                    bucket = i % 3
                    if bucket == 0:
                        d_words.append(meaning)
                    elif bucket == KSETRAJNA:
                        g_words.append(meaning)
                    else:
                        k_words.append(meaning)
            mode_words = {
                "DHARMA": tuple(d_words[:QUARTERS]),
                "GENESIS": tuple(g_words[:QUARTERS]),
                "KARMA": tuple(k_words[:QUARTERS]),
            }

        # Extract RAMA coords from derivation metadata
        # The char_wave dict stores rama_coords since the fractal tree commit
        derivation = getattr(r, "derivation", "")
        rama_coords: Tuple[int, ...] = ()

        return ResonancePacket(
            seed=seed,
            attractor=attractor,
            position=position,
            prana=prana,
            active_slots=active,
            guardian=getattr(r, "guardian_name", ""),
            quarter=quarter,
            guna=guna,
            branch_energies=(dharma_e, genesis_e, karma_e),
            tree_depth=2,  # Current: root + branches + leaves
            mode_words=mode_words,
            verse_ref=getattr(r, "verse_ref", ""),
            rama_coords=rama_coords,
            intent_type=GUNA_TO_INTENT_TYPE[guna],
        )

    def emit_with_coords(
        self,
        engine_result: object,
        rama_coords: Tuple[int, ...],
    ) -> ResonancePacket:
        """Emit with explicit RAMA coords (from char_wave dict)."""
        packet = self.emit(engine_result)
        # Frozen dataclass — must reconstruct
        return ResonancePacket(
            seed=packet.seed,
            attractor=packet.attractor,
            position=packet.position,
            prana=packet.prana,
            active_slots=packet.active_slots,
            guardian=packet.guardian,
            quarter=packet.quarter,
            guna=packet.guna,
            branch_energies=packet.branch_energies,
            tree_depth=packet.tree_depth,
            mode_words=packet.mode_words,
            verse_ref=packet.verse_ref,
            rama_coords=rama_coords,
            intent_type=packet.intent_type,
        )

    def to_intent_kwargs(self, packet: ResonancePacket, target: str) -> Dict:
        """Convert ResonancePacket to MantraIntent constructor kwargs.

        Returns a dict that can be passed to MantraIntent(**kwargs).
        The caller imports MantraIntent from kernel/intent.py.
        This bridge does NOT import production code.
        """
        return {
            "type": packet.intent_type,       # str, caller maps to IntentType enum
            "target": target,
            "params": {
                "seed": packet.seed,
                "attractor": packet.attractor,
                "guna": packet.guna,
                "guardian": packet.guardian,
                "prana": packet.prana,
                "dominant_mode": packet.dominant_mode,
                "verse_ref": packet.verse_ref,
            },
            "requester": f"antaranga:{packet.guardian}",
            "parampara_vector": packet.seed % MAHA_QUANTUM,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GUNA_NAMES",
    "GUNA_TO_INTENT_TYPE",
    "ResonancePacket",
    "ResonanceBridge",
    "ResonanceBridgeProtocol",
]
