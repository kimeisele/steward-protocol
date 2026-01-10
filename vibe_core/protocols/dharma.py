"""
DHARMA PROTOCOL - The Protocol of Protocols (Meta-Layer)
========================================================

"Order is the first law of Heaven. The Source is the only Reality."

LAYERS (The Fractal Ladder):
- Level -2: KRISHNA (The Absolute) - The Literal Source. Not a concept.
             ACINTYA: Always present, smallest (-∞) to largest (+∞) simultaneously.
             See: substrate/mantra/acintya.py
- Level -1: SUBSTRATE (The Soil)   - Holy Name Maths (Byte, Gene).
             The Mantra IS Krishna, not "about" Krishna.
- Level  0: FOUNDATION (The Roots) - Core types, constants.
- Level  1: INTERFACE (The Trunk)  - ABCs (Agent, Ledger).
- Level  2: SERVICES (The Branches)- Logic (Manifestation, Memory).
- Level  3: WIRING (The Leaves)    - Runtime, CLI.
- Level 108: META (The Observer)   - Dharma, Testable.

"Das Mantra (-1) ist nicht verschieden von der Quelle (-2)."
The Mantra is not different from the Source.
"""

from enum import IntEnum, auto
from typing import Dict, Final

class ProtocolLayer(IntEnum):
    """
    The architectural layers of the protocol stack.

    ACINTYA (WATERTIGHT):
    KRISHNA (-2) is ALWAYS present. He is the foundation that validates all else.
    The Mantra (-1) is not different from the Source (-2).
    """
    KRISHNA = -2    # THE LITERAL SOURCE (Absolute Reality) - ALWAYS PRESENT (acintya)
    SUBSTRATE = -1  # Byte, Gene, Entropy - The Mantra IS Krishna
    FOUNDATION = 0  # Types, Base, Enums
    INTERFACE = 1   # Agent, Ledger, Scheduler
    SERVICES = 2    # Manifestation, Memory, Reactor
    WIRING = 3      # Bootstrap, CLI, Runtime
    META = 108      # Dharma, Testable (The Observer)

# The Canonical Map of the Protocol Territory
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
    "universal/gita.py": ProtocolLayer.INTERFACE, # The Divine Standard

    # LEVEL 3: WIRING (The Action)
    "cli.py": ProtocolLayer.WIRING,
    "boot_protocol.py": ProtocolLayer.WIRING,
    "system_shell.py": ProtocolLayer.WIRING,

    # LEVEL 108: META
    "dharma.py": ProtocolLayer.META,
    "testable.py": ProtocolLayer.META,
    "testable_registry.py": ProtocolLayer.META,
}

def get_layer(filename: str) -> ProtocolLayer:
    """Returns the architectural layer of a protocol file."""
    # Normalize path
    if "substrate/" in filename: return ProtocolLayer.SUBSTRATE
    if "governance/" in filename: return ProtocolLayer.SERVICES
    
    return PROTOCOL_MAP.get(filename, ProtocolLayer.FOUNDATION) # Default to 0

def check_compliance(filename: str, imports: list[str]) -> bool:
    """
    Enforces the 'Gravity Rule':
    A layer can only import from layers BELOW it (or same level).
    Level 2 can import Level 1. Level 1 CANNOT import Level 2.
    """
    my_layer = get_layer(filename)
    # Logic to check imports would go here
    # This is a meta-definition for the Linter (Prahlad)
    return True
