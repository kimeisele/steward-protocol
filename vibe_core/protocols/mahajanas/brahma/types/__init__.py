"""
BRAHMA Types - Position 1 (GENESIS Quarter, LOAD_ROOT)
======================================================

BRAHMA - The Creator.
Types for creation, genesis, capabilities, and identity.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x2577ebbd"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.brahma.types.sarga import (
    Element,
    Cycle,
    SargaPhase,
    SargaBootSequence,
)

from vibe_core.protocols.mahajanas.brahma.types.capability_registry import (
    CapabilityRegistry,
)

from vibe_core.protocols.mahajanas.brahma.types.identity import (
    ManifestGenerator,
)

from vibe_core.protocols.mahajanas.brahma.types.agent_interface import (
    AgentSystemInterface,
)

__all__ = [
    # sarga.py
    "Element",
    "Cycle",
    "SargaPhase",
    "SargaBootSequence",
    # capability_registry.py
    "CapabilityRegistry",
    # identity.py
    "ManifestGenerator",
    # agent_interface.py
    "AgentSystemInterface",
]
