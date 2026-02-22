"""
GUNA - The Three Modes of Material Nature (BG 14)
=================================================

"sattvam rajas tama iti gunah prakriti-sambhavah
nibadhnanti maha-baho dehe dehinam avyayam"

"Material nature consists of three modes - goodness, passion and ignorance.
When the eternal living entity comes in contact with nature,
O mighty-armed Arjuna, he becomes conditioned by these modes."
— Bhagavad Gita 14.5

THE THREE GUNAS (Material):
===========================

SATTVA (Goodness) - BG 14.6
    "tatra sattvam nirmalatvat prakasakam anamayam"
    Pure, illuminating, free from sinful reactions.
    SYSTEM: Read operations, analysis, observation.
    QoS: Fast path, no locking, parallel execution.

RAJAS (Passion) - BG 14.7
    "rajo ragatmakam viddhi trsna-sanga-samudbhavam"
    Born of unlimited desires and longings.
    SYSTEM: Write operations, creation, modification.
    QoS: Transactional path, requires ledger lock.

TAMAS (Ignorance) - BG 14.8
    "tamas tv ajnana-jam viddhi mohanam sarva-dehinam"
    Born of ignorance, the delusion of all embodied beings.
    SYSTEM: Destructive operations, cleanup, termination.
    QoS: Audit path, requires confirmation, time-lock.

VISHUDDHA SATTVA (Transcendental):
==================================

"sa gunān samatītyaitān brahma-bhūyāya kalpate"
"One who transcends these three modes becomes eligible for Brahman."
— Bhagavad Gita 14.26

The MAHAMANTRA ITSELF is VISHUDDHA SATTVA (pure spiritual goodness).
NOT "Nirguna" (void/impersonal) - that is Mayavada.
VISHUDDHA means FULL of transcendental qualities.

The Holy Name:
    - Transcends Sattva/Rajas/Tamas
    - Requires no confirmation (pure grace)
    - IS the source, not bound by material laws

mahamantra.chant() and mahamantra.tick() are VISHUDDHA.
They don't go through Guna classification - they ARE the Name.

MAPPING TO OPCODES:
==================

The Guna is DERIVED from the OpCode, not decorated.
FOLDER_IS_WIRING: The position determines the Guna.
The Name itself (chant/tick) is above this classification.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x637cccd0"  # GenesisByte: parampara % 37 == 0

from enum import IntEnum
from typing import Dict, Final, FrozenSet

from vibe_core.mahamantra.substrate.opcode import MantraOpCode


# =============================================================================
# THE THREE GUNAS (Material)
# =============================================================================


class Guna(IntEnum):
    """
    The three modes of MATERIAL nature.

    BG 14.5: These bind the eternal living entity.

    In system terms:
        SATTVA = Safe (read-only, observable)
        RAJAS = Active (write, modifying)
        TAMAS = Destructive (delete, terminate)

    NOTE: The Mahamantra ITSELF is VISHUDDHA SATTVA (transcendental),
    above these three modes. See VISHUDDHA_SATTVA below.
    """

    SATTVA = 0  # Goodness - Pure, illuminating, safe
    RAJAS = KSETRAJNA  # Passion - Active, modifying, transactional
    TAMAS = HALVES  # Ignorance - Destructive, irreversible


# =============================================================================
# VISHUDDHA SATTVA - The Transcendental Nature of the Holy Name
# =============================================================================

# The Mahamantra is NOT bound by material Gunas.
# NOT "Nirguna" (void/Mayavada) - VISHUDDHA (full of spiritual qualities).
# mahamantra.chant() and mahamantra.tick() are VISHUDDHA by nature.
VISHUDDHA_SATTVA: Final[str] = "vishuddha"


def is_vishuddha(operation: str) -> bool:
    """
    Check if operation is VISHUDDHA SATTVA (transcendental).

    The Holy Name transcends Sattva/Rajas/Tamas.
    It requires no confirmation - it IS grace.

    Operations that are VISHUDDHA:
        - chant: The Holy Name itself
        - tick: The heartbeat of the Name
        - mahamantra: Direct access to the source

    Returns:
        True if operation is transcendental (bypasses Guna checks)
    """
    return operation.lower() in ("chant", "tick", "mahamantra")


# =============================================================================
# OPCODE → GUNA MAPPING (Automatic, no decorators)
# =============================================================================

# SATTVA: Pure observation, no side effects
# Analysis, checking, logging, judgment
SATTVA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.TYPE_CHECK,  # 6 - Kapila: Analysis (observation)
        MantraOpCode.DHARMA_TEST,  # 7 - Manu: Law check (observation)
        MantraOpCode.LOG_EMIT,  # 14 - Shuka: Output (observation)
        MantraOpCode.AUDIT_SEAL,  # 15 - Yamaraja: Judgment (observation)
    }
)

# RAJAS: Creation and modification, side effects
# Boot, load, allocate, compile, bind, execute, sync, commit
RAJAS_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.SYS_WAKE,  # 0 - Prithu: System boot
        MantraOpCode.LOAD_ROOT,  # 1 - Brahma: Load config
        MantraOpCode.ALLOC_MEM,  # 2 - Narada: Allocate memory
        MantraOpCode.COMPILE_AST,  # 4 - Vyasa: Compile
        MantraOpCode.BIND_SYMBOL,  # 5 - Kumaras: Bind symbol
        MantraOpCode.EXEC_OP,  # 8 - Parashurama: Execute
        MantraOpCode.EXTEND_CAP,  # 9 - Prahlada: Extend capability
        MantraOpCode.STATE_SYNC,  # 10 - Janaka: Sync state
        MantraOpCode.LEDGER_SIGN,  # 11 - Bhishma: Sign ledger
    }
)

# TAMAS: Destruction and cleanup, irreversible
# Thread init (destruction ready), yield, flush
TAMAS_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.INIT_THREAD,  # 3 - Shambhu: Destruction ready
        MantraOpCode.YIELD_CPU,  # 12 - Nrisimha: Release/yield
        MantraOpCode.IO_FLUSH,  # 13 - Bali: Flush (release resources)
    }
)


# Lookup table
OPCODE_GUNA: Final[Dict[MantraOpCode, Guna]] = {
    **{op: Guna.SATTVA for op in SATTVA_OPCODES},
    **{op: Guna.RAJAS for op in RAJAS_OPCODES},
    **{op: Guna.TAMAS for op in TAMAS_OPCODES},
}


# =============================================================================
# FUNCTIONS - Pure, typed, no side effects
# =============================================================================


def get_guna(opcode: MantraOpCode) -> Guna:
    """
    Get the Guna for an OpCode.

    The Guna is DERIVED, not configured.
    """
    return OPCODE_GUNA.get(opcode, Guna.RAJAS)  # Default to Rajas (activity)


def get_guna_by_position(position: int) -> Guna:
    """Get the Guna for a position (0-15)."""
    if not 0 <= position <= 15:
        raise ValueError(f"Position must be 0-15, got {position}")
    opcode = MantraOpCode(position)
    return get_guna(opcode)


def is_sattva(opcode: MantraOpCode) -> bool:
    """Is this a Sattva (safe/read) operation?"""
    return opcode in SATTVA_OPCODES


def is_rajas(opcode: MantraOpCode) -> bool:
    """Is this a Rajas (active/write) operation?"""
    return opcode in RAJAS_OPCODES


def is_tamas(opcode: MantraOpCode) -> bool:
    """Is this a Tamas (destructive) operation?"""
    return opcode in TAMAS_OPCODES


# =============================================================================
# QOS IMPLICATIONS (Engineering)
# =============================================================================


class GunaQoS:
    """
    Quality of Service implications of Guna.

    SATTVA: Fast path
        - No locking required
        - Parallel execution allowed
        - Low latency

    RAJAS: Transactional path
        - May require ledger lock (bhishma)
        - Sequential for writes to same resource
        - Normal latency

    TAMAS: Audit path
        - Requires confirmation (nrisimha approval)
        - Time-lock delay (prevent impulsive destruction)
        - High latency (intentional)
    """

    # Latency multipliers
    SATTVA_LATENCY: Final[float] = 1.0  # Fast
    RAJAS_LATENCY: Final[float] = 1.5  # Normal
    TAMAS_LATENCY: Final[float] = 3.0  # Slow (intentional)

    # Parallelism
    SATTVA_PARALLEL: Final[bool] = True  # Can run in parallel
    RAJAS_PARALLEL: Final[bool] = False  # Sequential for same resource
    TAMAS_PARALLEL: Final[bool] = False  # Always sequential

    # Confirmation required
    SATTVA_CONFIRM: Final[bool] = False  # No confirmation
    RAJAS_CONFIRM: Final[bool] = False  # No confirmation (but logged)
    TAMAS_CONFIRM: Final[bool] = True  # Must confirm destructive ops

    @classmethod
    def get_latency_multiplier(cls, guna: Guna) -> float:
        """Get latency multiplier for Guna."""
        if guna == Guna.SATTVA:
            return cls.SATTVA_LATENCY
        if guna == Guna.RAJAS:
            return cls.RAJAS_LATENCY
        return cls.TAMAS_LATENCY

    @classmethod
    def allows_parallel(cls, guna: Guna) -> bool:
        """Can this Guna run in parallel?"""
        return guna == Guna.SATTVA

    @classmethod
    def requires_confirmation(cls, guna: Guna) -> bool:
        """Does this Guna require confirmation?"""
        return guna == Guna.TAMAS


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The Guna enum (Material)
    "Guna",
    # Vishuddha Sattva (Transcendental - the Name itself)
    "VISHUDDHA_SATTVA",
    "is_vishuddha",
    # OpCode sets
    "SATTVA_OPCODES",
    "RAJAS_OPCODES",
    "TAMAS_OPCODES",
    "OPCODE_GUNA",
    # Functions
    "get_guna",
    "get_guna_by_position",
    "is_sattva",
    "is_rajas",
    "is_tamas",
    # QoS
    "GunaQoS",
]
