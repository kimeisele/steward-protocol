"""
THE BIORHYTHM PROTOCOL - Consciousness States (Gunas + Turiya)
==============================================================

"sattvaṁ rajas tama iti guṇāḥ prakṛti-sambhavāḥ
nibadhnanti mahā-bāho dehe dehinam avyayam"

"Material nature consists of three modes—goodness, passion and ignorance.
When the eternal living entity comes in contact with nature, O mighty-armed
Arjuna, he becomes conditioned by these modes."
— Bhagavad Gita 14.5

SHASTRA FOUNDATION (BG 14.5-27):
================================

The Three Gunas (Modes of Material Nature):
- TAMAS (ignorance): Inertia, darkness, delusion [BG 14.8]
- RAJAS (passion): Activity, desire, attachment [BG 14.7]
- SATTVA (goodness): Illumination, knowledge, happiness [BG 14.6]

Beyond the Gunas:
- TURIYA (transcendental): Beyond the three modes [BG 14.26]
    "māṁ ca yo 'vyabhicāreṇa bhakti-yogena sevate
    sa guṇān samatītyaitān brahma-bhūyāya kalpate"
    "One who engages in full devotional service, unfailing in all
    circumstances, at once transcends the modes of material nature..."

SOFTWARE MAPPING:
================

    CONSCIOUSNESS LEVEL         STATE       ACTIVITY
    ───────────────────────────────────────────────────
    0.0 - 0.2                   Tamas       Hibernate (heartbeat only)
    0.2 - 0.5                   Rajas       React (respond to triggers)
    0.5 - 0.8                   Sattva      Reflect (organize, reinforce)
    0.8 - 1.0                   Turiya      Deep Think (full OODA loop)

INPUT WEIGHTS (Prakriti Composition):
=====================================

    Synaptic urgency (0.5): How urgent are the learned patterns?
    Prakriti health (0.3): System guna state (from senses)
    Kala rhythm (0.2): Cosmic time influence (optional)

    consciousness = 0.5 * urgency + 0.3 * health + 0.2 * rhythm

MAHAMANTRA MAPPING:
===================

    Position 9 (PRAHLADA) - Transcendence through devotion
    → Prahlada's consciousness remained in Turiya even in danger
    → He transcended the gunas through pure bhakti

    Quarter: KARMA (positions 8-11) - Action in consciousness

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x8f74e400"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)


# =============================================================================
# SHASTRA CONSTANTS
# =============================================================================

# Bhagavad Gita References
BG_GUNA_CHAPTER: Final[str] = "14"  # The Three Modes of Material Nature
BG_TAMAS_VERSE: Final[str] = "14.8"
BG_RAJAS_VERSE: Final[str] = "14.7"
BG_SATTVA_VERSE: Final[str] = "14.6"
BG_TURIYA_VERSE: Final[str] = "14.26"  # Transcending the modes

# Consciousness thresholds (as per opus_assistant biorhythm)
THRESHOLD_TAMAS_MAX: Final[float] = 0.2    # Below this: hibernate
THRESHOLD_RAJAS_MAX: Final[float] = 0.5    # Below this: react
THRESHOLD_SATTVA_MAX: Final[float] = 0.8   # Below this: reflect
# Above 0.8: Turiya (transcendental)

# Input weights for consciousness calculation
WEIGHT_URGENCY: Final[float] = 0.5   # Synaptic urgency
WEIGHT_HEALTH: Final[float] = 0.3    # Prakriti health
WEIGHT_RHYTHM: Final[float] = 0.2    # Kala rhythm


# =============================================================================
# GUNA (Mode of Nature)
# =============================================================================

class Guna(str, Enum):
    """
    The Three Gunas (Modes of Material Nature) + Turiya.

    BG 14.5: The three modes bind the eternal soul to the material body.
    BG 14.26: Pure devotional service transcends all three modes.
    """
    TAMAS = "tamas"      # Ignorance - inertia, darkness
    RAJAS = "rajas"      # Passion - activity, desire
    SATTVA = "sattva"    # Goodness - knowledge, harmony
    TURIYA = "turiya"    # Transcendental - beyond the modes

    @classmethod
    def from_level(cls, level: float) -> "Guna":
        """
        Derive guna from consciousness level (0.0-1.0).

        0.0-0.2: TAMAS (hibernate)
        0.2-0.5: RAJAS (react)
        0.5-0.8: SATTVA (reflect)
        0.8-1.0: TURIYA (transcend)
        """
        if level < THRESHOLD_TAMAS_MAX:
            return cls.TAMAS
        elif level < THRESHOLD_RAJAS_MAX:
            return cls.RAJAS
        elif level < THRESHOLD_SATTVA_MAX:
            return cls.SATTVA
        else:
            return cls.TURIYA

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "tamas": "तमस्",
            "rajas": "रजस्",
            "sattva": "सत्त्व",
            "turiya": "तुरीय",
        }[self.value]

    @property
    def bg_verse(self) -> str:
        """Get Bhagavad Gita verse reference."""
        return {
            Guna.TAMAS: BG_TAMAS_VERSE,
            Guna.RAJAS: BG_RAJAS_VERSE,
            Guna.SATTVA: BG_SATTVA_VERSE,
            Guna.TURIYA: BG_TURIYA_VERSE,
        }[self]

    @property
    def activity_level(self) -> str:
        """Get the activity mode for this guna."""
        return {
            Guna.TAMAS: "hibernate",
            Guna.RAJAS: "react",
            Guna.SATTVA: "reflect",
            Guna.TURIYA: "transcend",
        }[self]

    @property
    def description(self) -> str:
        """Get human-readable description."""
        return {
            Guna.TAMAS: "Ignorance - heartbeat only, minimal activity",
            Guna.RAJAS: "Passion - quick perception, respond to triggers",
            Guna.SATTVA: "Goodness - organize, reinforce, steady practice",
            Guna.TURIYA: "Transcendental - full OODA loop, deep thinking",
        }[self]

    @property
    def threshold_range(self) -> Tuple[float, float]:
        """Get the consciousness level range for this guna."""
        return {
            Guna.TAMAS: (0.0, THRESHOLD_TAMAS_MAX),
            Guna.RAJAS: (THRESHOLD_TAMAS_MAX, THRESHOLD_RAJAS_MAX),
            Guna.SATTVA: (THRESHOLD_RAJAS_MAX, THRESHOLD_SATTVA_MAX),
            Guna.TURIYA: (THRESHOLD_SATTVA_MAX, 1.0),
        }[self]


# =============================================================================
# CONSCIOUSNESS STATE
# =============================================================================

@dataclass
class ConsciousnessState:
    """
    Current state of consciousness.

    Includes:
    - Level (0.0-1.0)
    - Derived guna
    - Input factors
    - Timestamp
    """
    level: float = 0.5  # Default: middle consciousness
    guna: Guna = Guna.RAJAS  # Default: active state

    # Input factors (what computed this level)
    urgency: float = 0.0    # Synaptic urgency
    health: float = 0.7     # Prakriti health (default healthy)
    rhythm: float = 0.5     # Kala rhythm

    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate and derive guna."""
        self.level = max(0.0, min(1.0, self.level))
        self.guna = Guna.from_level(self.level)

    @classmethod
    def compute(
        cls,
        urgency: float = 0.0,
        health: float = 0.7,
        rhythm: float = 0.5,
    ) -> "ConsciousnessState":
        """
        Compute consciousness state from input factors.

        consciousness = 0.5 * urgency + 0.3 * health + 0.2 * rhythm
        """
        level = (
            WEIGHT_URGENCY * urgency +
            WEIGHT_HEALTH * health +
            WEIGHT_RHYTHM * rhythm
        )
        return cls(
            level=level,
            urgency=urgency,
            health=health,
            rhythm=rhythm,
        )

    @property
    def is_hibernating(self) -> bool:
        """Is consciousness in hibernate mode?"""
        return self.guna == Guna.TAMAS

    @property
    def is_transcendent(self) -> bool:
        """Is consciousness in transcendental state?"""
        return self.guna == Guna.TURIYA

    @property
    def activity_mode(self) -> str:
        """Get current activity mode."""
        return self.guna.activity_level


# =============================================================================
# BIORHYTHM TICK RESULT
# =============================================================================

@dataclass
class BiorhythmTick:
    """
    Result of a biorhythm tick.

    The biorhythm "ticks" periodically, updating consciousness.
    """
    tick_number: int
    previous_state: ConsciousnessState
    current_state: ConsciousnessState
    state_changed: bool = False

    @property
    def consciousness_delta(self) -> float:
        """Change in consciousness level."""
        return self.current_state.level - self.previous_state.level

    @property
    def guna_changed(self) -> bool:
        """Did the guna change?"""
        return self.previous_state.guna != self.current_state.guna


# =============================================================================
# BIORHYTHM PROTOCOL - The Interface
# =============================================================================

@runtime_checkable
class BiorhythmProtocol(Protocol):
    """
    The Biorhythm Protocol - How consciousness MUST behave.

    The biorhythm is NOT polling. It's a continuous consciousness
    spectrum that determines system activity level.

    SHASTRA BASIS:
        BG 14.5: The three modes condition the eternal soul.
        BG 14.26: Devotional service transcends the modes.

    SOFTWARE MAPPING:
        - Tamas: System hibernation (heartbeat only)
        - Rajas: Quick reactions to triggers
        - Sattva: Organized, reflective operation
        - Turiya: Full cognitive processing (OODA loop)
    """

    @property
    def consciousness_level(self) -> float:
        """Current consciousness level (0.0-1.0)."""
        ...

    @property
    def consciousness_state(self) -> ConsciousnessState:
        """Current full consciousness state."""
        ...

    @property
    def guna(self) -> Guna:
        """Current guna (mode of nature)."""
        ...

    @property
    def tick_count(self) -> int:
        """Number of ticks processed."""
        ...

    def tick(
        self,
        urgency: float = 0.0,
        health: float = 0.7,
        rhythm: float = 0.5,
    ) -> BiorhythmTick:
        """
        Process a biorhythm tick.

        Updates consciousness based on input factors.
        Returns the tick result with state change info.
        """
        ...

    def set_urgency(self, urgency: float) -> None:
        """Update synaptic urgency factor."""
        ...

    def set_health(self, health: float) -> None:
        """Update prakriti health factor (from senses/entropy)."""
        ...

    def set_rhythm(self, rhythm: float) -> None:
        """Update kala rhythm factor."""
        ...


# =============================================================================
# BIORHYTHM PROTOCOL DEFINITION - Self-Reference
# =============================================================================

class BiorhythmProtocolDef(MahamantraProtocolBase):
    """
    The Biorhythm Protocol.

    Position 9 (PRAHLADA) - The transcendent devotee.
    Level -1 (SUBSTRATE) - Foundational consciousness layer.
    Quarter KARMA - Action through consciousness.

    SHASTRA: BG 14.5-27 (The Three Modes of Material Nature)
    """

    __protocol_identity__ = ProtocolIdentity(
        name="BiorhythmProtocol",
        mahajana="prahlada",  # Transcended the gunas
        position=9,
        level=Level.SUBSTRATE,
        quarter=Quarter.KARMA,  # Position 9 is in KARMA quarter
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "guna_classification",
            "consciousness_level",
            "consciousness_state",
            "biorhythm_tick",
            "activity_mode",
            "transcendence_detection",
        ],
        requires=["CoreProtocol", "EntropyProtocol"],
        opcodes=["INVOKE"],  # Prahlada's opcode - invocation
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_consciousness(
    urgency: float = 0.0,
    health: float = 0.7,
    rhythm: float = 0.5,
) -> float:
    """
    Compute consciousness level from inputs.

    Formula: 0.5 * urgency + 0.3 * health + 0.2 * rhythm
    """
    return (
        WEIGHT_URGENCY * urgency +
        WEIGHT_HEALTH * health +
        WEIGHT_RHYTHM * rhythm
    )


def level_to_guna(level: float) -> Guna:
    """Convert consciousness level to guna."""
    return Guna.from_level(level)


# =============================================================================
# VALIDATION
# =============================================================================

_valid, _violations = BiorhythmProtocolDef.validate()
assert _valid, f"BiorhythmProtocol failed validation: {_violations}"

# Verify threshold consistency
assert THRESHOLD_TAMAS_MAX < THRESHOLD_RAJAS_MAX, "Tamas must be below Rajas"
assert THRESHOLD_RAJAS_MAX < THRESHOLD_SATTVA_MAX, "Rajas must be below Sattva"
assert THRESHOLD_SATTVA_MAX < 1.0, "Sattva max must be below 1.0"

# Verify guna count (3 gunas + turiya = 4)
assert len(Guna) == 4, "Must have exactly 4 gunas (3 material + turiya)"

# Verify weights sum to 1.0
assert abs(WEIGHT_URGENCY + WEIGHT_HEALTH + WEIGHT_RHYTHM - 1.0) < 0.001, "Weights must sum to 1.0"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Shastra constants
    "BG_GUNA_CHAPTER",
    "BG_TAMAS_VERSE",
    "BG_RAJAS_VERSE",
    "BG_SATTVA_VERSE",
    "BG_TURIYA_VERSE",
    "THRESHOLD_TAMAS_MAX",
    "THRESHOLD_RAJAS_MAX",
    "THRESHOLD_SATTVA_MAX",
    "WEIGHT_URGENCY",
    "WEIGHT_HEALTH",
    "WEIGHT_RHYTHM",
    # Enums
    "Guna",
    # Data classes
    "ConsciousnessState",
    "BiorhythmTick",
    # Protocols
    "BiorhythmProtocol",
    # Protocol definition
    "BiorhythmProtocolDef",
    # Convenience functions
    "compute_consciousness",
    "level_to_guna",
]
