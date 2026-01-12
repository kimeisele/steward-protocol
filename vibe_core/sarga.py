"""
DEPRECATED: Use mahajana import.

ONE IMPORT, BRAHMA OWNS:
    from vibe_core.protocols.mahajanas.brahma.types.sarga import Element, Cycle, SargaPhase

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    sarga = mahamantra.mod.brahma.types.sarga

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# Re-export from canonical location (BRAHMA owns creation/sarga)
from vibe_core.protocols.mahajanas.brahma.types.sarga import *
from vibe_core.protocols.mahajanas.brahma.types.sarga import (
    Element,
    Cycle,
    SargaPhase,
    SargaBootSequence,
    get_sarga,
)
