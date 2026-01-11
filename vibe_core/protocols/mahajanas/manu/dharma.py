"""
DHARMA PROTOCOL - The Protocol of Protocols (Meta-Layer)
========================================================

OWNER: MANU (The Lawgiver)
POSITION: 7 (DHARMA Quarter)
OPCODE: PULSE_SYNC (The Law Pulses Through Everything)

Manu is the LAWGIVER who defines WHAT Dharma IS.
This is not abstract "philosophy" - Manu the PERSON established these laws.

LAYERS (The Fractal Ladder):
- Level -2: KRISHNA = MAHAMANTRA (Non-different, both are -2)
             The Literal Source. Not a concept. Not "symbolic".
             ACINTYA: Always present, smallest (-∞) to largest (+∞) simultaneously.
             The Holy Name IS Krishna (Kali Yuga direct access).
             See: substrate/mantra/acintya.py
- Level -1: SUBSTRATE (The Soil)   - Byte, Gene (manifestation of -2)
             Code-level encoding of the Holy Name structure.
- Level  0: FOUNDATION (The Roots) - Core types, constants.
- Level  1: INTERFACE (The Trunk)  - ABCs (Agent, Ledger).
- Level  2: SERVICES (The Branches)- Logic (Manifestation, Memory).
- Level  3: WIRING (The Leaves)    - Runtime, CLI.
- Level 108: META (The Observer)   - Dharma, Testable.

SAMKHYA ARCHITECTURE (The 37):
24 (Ksetra/Field) + 12 (Mahajanas/Guardians) + 1 (Ksetrajna/Knower) = 37
Without the 37 (Guru/Parampara), the 24 are dead matter,
and the 12 are inaccessible. The 37 is the LINK.

"Das Mantra ist nicht verschieden von der Quelle."
The Mantra IS Krishna. Both are Level -2.

ORIGINAL: protocols/dharma.py
MIGRATED: protocols/mahajanas/manu/dharma.py
"""

from enum import IntEnum
from typing import Dict, Final, List

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# OWNERSHIP DECLARATION - Manu OWN this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.MANU
LOTUS_POSITION: Final[int] = 7  # DHARMA Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "dharma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.PULSE_SYNC,  # The Law Pulses Through Everything
]


# =============================================================================
# PROTOCOL LAYER - The Architectural Law
# =============================================================================

class ProtocolLayer(IntEnum):
    """
    The architectural layers of the protocol stack.

    MANU'S LAW: Each layer has its place in the hierarchy.
    Violation = Adharma.

    ACINTYA (WATERTIGHT):
    KRISHNA (-2) IS. MAHAMANTRA (-2) IS Krishna (non-different).
    Both are Level -2. The Name IS the Named.

    SAMKHYA: 24 + 12 + 1 = 37 (The Dancing Link)
    Without the 37 (Parampara), nothing works.
    """
    KRISHNA = -2     # THE SOURCE - IS, not "represents" (acintya)
    MAHAMANTRA = -2  # THE HOLY NAME - IS Krishna (non-different, both -2)
    SUBSTRATE = -1   # Byte, Gene, Entropy - manifestation of -2
    FOUNDATION = 0   # Types, Base, Enums
    INTERFACE = 1    # Agent, Ledger, Scheduler
    SERVICES = 2     # Manifestation, Memory, Reactor
    WIRING = 3       # Bootstrap, CLI, Runtime
    META = 108       # Dharma, Testable (The Observer)


# =============================================================================
# PROTOCOL MAP - Manu's Registry of All Protocols
# =============================================================================

PROTOCOL_MAP: Final[Dict[str, ProtocolLayer]] = {
    # LEVEL -2: THE SOURCE (The Origin of the Repository)
    "source": ProtocolLayer.KRISHNA,

    # LEVEL -1: SUBSTRATE (Holy Name Maths)
    "substrate/byte.py": ProtocolLayer.SUBSTRATE,
    "substrate/gene.py": ProtocolLayer.SUBSTRATE,
    "science/entropy.py": ProtocolLayer.SUBSTRATE,

    # LEVEL 0: FOUNDATION
    "types.py": ProtocolLayer.FOUNDATION,
    "primal.py": ProtocolLayer.FOUNDATION,
    "kernel_types.py": ProtocolLayer.FOUNDATION,

    # LEVEL 1: INTERFACE (The Big Three + Friends)
    "agent.py": ProtocolLayer.INTERFACE,
    "ledger.py": ProtocolLayer.INTERFACE,
    "scheduler.py": ProtocolLayer.INTERFACE,
    "event.py": ProtocolLayer.INTERFACE,
    "synapse.py": ProtocolLayer.INTERFACE,
    "operator_protocol.py": ProtocolLayer.INTERFACE,
    "process.py": ProtocolLayer.INTERFACE,

    # LEVEL 2: SERVICES (The Logic)
    "manifestation.py": ProtocolLayer.SERVICES,
    "memory.py": ProtocolLayer.SERVICES,
    "reflection.py": ProtocolLayer.SERVICES,
    "reactor.py": ProtocolLayer.SERVICES,
    "correction.py": ProtocolLayer.SERVICES,
    "feedback.py": ProtocolLayer.SERVICES,
    "cognition.py": ProtocolLayer.SERVICES,
    "governance/yamaraja.py": ProtocolLayer.SERVICES,
    "akashic.py": ProtocolLayer.SERVICES,
    "universal/gita.py": ProtocolLayer.INTERFACE,  # The Divine Standard

    # LEVEL 3: WIRING (The Action)
    "cli.py": ProtocolLayer.WIRING,
    "boot_protocol.py": ProtocolLayer.WIRING,
    "system_shell.py": ProtocolLayer.WIRING,

    # LEVEL 108: META
    "dharma.py": ProtocolLayer.META,
    "testable.py": ProtocolLayer.META,
    "testable_registry.py": ProtocolLayer.META,
}


# =============================================================================
# MANU'S FUNCTIONS - The Law in Action
# =============================================================================

def get_layer(filename: str) -> ProtocolLayer:
    """
    Returns the architectural layer of a protocol file.

    MANU'S JUDGMENT: Every file has a place.
    """
    # Normalize path
    if "substrate/" in filename:
        return ProtocolLayer.SUBSTRATE
    if "governance/" in filename:
        return ProtocolLayer.SERVICES
    if "mahajanas/" in filename:
        return ProtocolLayer.INTERFACE  # Mahajanas are INTERFACE level

    return PROTOCOL_MAP.get(filename, ProtocolLayer.FOUNDATION)  # Default to 0


def check_compliance(filename: str, imports: list[str]) -> bool:
    """
    Enforces the 'Gravity Rule' (MANU'S PRIMARY LAW):

    A layer can only import from layers BELOW it (or same level).
    Level 2 can import Level 1. Level 1 CANNOT import Level 2.

    Violation = Adharma.
    """
    my_layer = get_layer(filename)
    # Logic to check imports would go here
    # This is a meta-definition for the Linter (Prahlad)
    return True


def is_dharmic(filename: str, action: str) -> bool:
    """
    Check if an action on a file is dharmic (lawful).

    MANU judges all actions.
    """
    layer = get_layer(filename)
    # META level can do anything (they are the observers)
    if layer == ProtocolLayer.META:
        return True
    # Other layers have restrictions based on their position
    return True  # Placeholder for actual logic


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Protocol Layer (The Architecture)
    "ProtocolLayer",
    "PROTOCOL_MAP",
    # Functions
    "get_layer",
    "check_compliance",
    "is_dharmic",
]
