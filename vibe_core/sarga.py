"""
DEPRECATED: Use mahajana import.

ONE IMPORT, BRAHMA OWNS:
    from vibe_core.protocols.mahajanas.brahma.types.sarga import Element, Cycle, SargaPhase

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    sarga = mahamantra.<quarter>.brahma  # FIXME: specify correct quarter.types.sarga

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# Re-export from canonical location (BRAHMA owns creation/sarga)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xf501cdbf"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.brahma.types.sarga import *
from vibe_core.protocols.mahajanas.brahma.types.sarga import (
    Element,
    Cycle,
    SargaPhase,
    SargaBootSequence,
    get_sarga,
)
