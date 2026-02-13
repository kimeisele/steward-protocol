"""
Compression Protocol Types - SSOT for MahaCompression
======================================================

All types used by MahaCompression adapter must be defined here.
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, TRINITY)

from typing import Protocol, runtime_checkable, Final, Literal, Optional, Union
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# INTENT GUNA (The 3 Modes + 1 Transcendental)
# =============================================================================

class IntentGuna(Enum):
    """The 3 Modes of Material Nature + 1 Transcendental."""
    SATTVA = "sattva"   # Creation / Goodness
    RAJAS = "rajas"     # Passion / Activity
    TAMAS = "tamas"     # Ignorance / Destruction
    SUDDHA = "suddha"   # Pure / Transcendental


# =============================================================================
# INTENT LEVEL
# =============================================================================

@dataclass(frozen=True)
class IntentLevel:
    """
    Detailed intent classification.
    """
    guna: IntentGuna
    confidence: float
    category: str
    score: int = 0  # Numeric score for ranking
    system_interpretation: str = ""  # Human-readable interpretation


# Pre-defined Intent Levels
INTENT_TAMAS: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.TAMAS,
    confidence=1.0,
    category="DESTRUCTION",
    score=0,
    system_interpretation="Ignorance/destruction mode - requires confirmation"
)

INTENT_RAJAS: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.RAJAS,
    confidence=1.0,
    category="ACTION",
    score=KSETRAJNA,
    system_interpretation="Passion/action mode - execute with caution"
)

INTENT_SATTVA: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.SATTVA,
    confidence=1.0,
    category="CREATION",
    score=HALVES,
    system_interpretation="Goodness/creation mode - clean execution"
)

INTENT_SUDDHA: Final[IntentLevel] = IntentLevel(
    guna=IntentGuna.SUDDHA,
    confidence=1.0,
    category="TRANSCENDENTAL",
    score=TRINITY,
    system_interpretation="Pure/transcendental mode - divine execution"
)

ALL_INTENT_LEVELS: Final[tuple[IntentLevel, ...]] = (
    INTENT_TAMAS,
    INTENT_RAJAS,
    INTENT_SATTVA,
    INTENT_SUDDHA,
)


# =============================================================================
# SAMSKARA (Impression/Memory Levels)
# =============================================================================

class SamskaraLevel(Enum):
    """Level of samskara (impression) encoding."""
    MICRO = "micro"    # Single event
    MESO = "meso"      # Session/conversation
    MACRO = "macro"    # Lifetime/persistent


class SamskaraScope(Enum):
    """Scope of samskara encoding."""
    MICRO = "micro"      # Session level
    MESO = "meso"        # Service level
    MACRO = "macro"      # Platform level


# Pre-defined Samskara Levels
SAMSKARA_MICRO: Final[SamskaraLevel] = SamskaraLevel.MICRO
SAMSKARA_MESO: Final[SamskaraLevel] = SamskaraLevel.MESO
SAMSKARA_MACRO: Final[SamskaraLevel] = SamskaraLevel.MACRO

ALL_SAMSKARA_LEVELS: Final[tuple[SamskaraLevel, ...]] = (
    SAMSKARA_MICRO,
    SAMSKARA_MESO,
    SAMSKARA_MACRO,
)


# =============================================================================
# COMPRESSION RESULTS
# =============================================================================

@dataclass(frozen=True)
class CompressionResult:
    """
    Watertight result of a compression operation.

    NOTE: intent_level is Optional. The compression layer compresses
    KSHETRA (data), it does not judge GUNA. Guna is a property of
    PRAKRITI (the operation/OpCode), not of the dead field.
    See substrate/guna.py: "The Guna is DERIVED from the OpCode, not decorated."

    The calling layer may set intent_level from its own OpCode context
    via guna.get_guna(opcode).
    """
    seed: int
    input_size: int
    output_size: int
    compression_ratio: float
    position: int
    intent_level: Optional[IntentLevel] = None
    summary: Optional[str] = None
    text_hash: Optional[int] = None
    length: Optional[int] = None


@dataclass(frozen=True)
class SamskaraResult:
    """
    Result of encoding system state as samskara (impression/memory).

    The samskara is a compact representation that preserves the
    essential "karmic imprint" of the data.

    NOTE: intent_level is Optional — same principle as CompressionResult.
    """
    seed: int
    data_hash: int
    item_count: int
    compression_ratio: float
    intent_level: Optional[IntentLevel] = None


@dataclass(frozen=True)
class PhysicsVerification:
    """
    Result of verifying a seed against physics constants.

    Checks alignment with:
    - MAHA_QUANTUM (137)
    - PARAMPARA (37)
    - POSITION_SUM_TOTAL (136)
    """
    seed: int
    is_aligned: bool
    quantum_score: float
    parampara_score: float
    field_score: float
    classification: str


# =============================================================================
# PROTOCOL
# =============================================================================

@runtime_checkable
class MahaCompressionProtocol(Protocol):
    """
    Protocol for MahaCompression: The Algorithm of Intent Extraction.

    Responsible for:
    1. Compressing infinite text into a finite Seed (int).
    2. Determining Mahamantra Position (0-15).
    3. extracting Intent Level (Guna).
    """

    def compress(self, text: str) -> CompressionResult:
        """
        Compress text into a Mahamantra Seed.

        Args:
            text: The input natural language or command.

        Returns:
            CompressionResult containing seed, position, and intent classification.
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "IntentGuna",
    "SamskaraLevel",
    "SamskaraScope",
    # DataClasses
    "IntentLevel",
    "CompressionResult",
    "SamskaraResult",
    "PhysicsVerification",
    # Protocol
    "MahaCompressionProtocol",
    # Pre-defined Intent Levels
    "INTENT_TAMAS",
    "INTENT_RAJAS",
    "INTENT_SATTVA",
    "INTENT_SUDDHA",
    "ALL_INTENT_LEVELS",
    # Pre-defined Samskara Levels
    "SAMSKARA_MICRO",
    "SAMSKARA_MESO",
    "SAMSKARA_MACRO",
    "ALL_SAMSKARA_LEVELS",
]
