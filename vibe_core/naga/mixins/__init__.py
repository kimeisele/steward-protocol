"""
NAGA Mixins - Capability Providers + Active Genes.

TWO TYPES OF MIXINS:

1. CAPABILITY MIXINS (Passive - in base.py):
   - Provide lazy property access to NAGA services
   - SeshaMixin, VasukiMixin, etc.
   - Used by Flood Classes for manual surgical overrides

2. ACTIVE MIXINS (Living Genes):
   - AUTOMATICALLY intercept methods
   - ActiveSeshaMixin: Auto-records state mutations to Ledger
   - ActiveTakshakaMixin: Auto-validates inputs before execution
   - ActiveVasukiMixin: Auto-signs outbound network calls

The Ashvamedha Strategy:
    Active Mixins are the "living horses" that claim territory.
    Wherever they go, NAGA sovereignty follows.

"Das Wasser gibt die Werkzeuge. Die Gene bringen das Leben."
"""

# Passive Capability Mixins (legacy, for manual flooding)
from .base import (
    ChitraguptaMixin,
    KaliyaMixin,
    KarkotakaMixin,
    KulikaMixin,
    NagaCapabilityMixin,
    NaradaMixin,
    PadmaMixin,
    PrahladMixin,
    SeshaMixin,
    ShankhaMixin,
    TakshakaMixin,
    VasukiMixin,
)

# Active Gene Mixins (auto-interception)
from .sesha import ActiveSeshaMixin, SeshaScribeMixin
from .takshaka import ActiveTakshakaMixin, TakshakaGuardMixin, ToxicInputError
from .vasuki import ActiveVasukiMixin, VasukiBorderMixin

__all__ = [
    # Passive Capability Mixins
    "NagaCapabilityMixin",
    "SeshaMixin",
    "VasukiMixin",
    "TakshakaMixin",
    "KaliyaMixin",
    "KarkotakaMixin",
    "KulikaMixin",
    "PadmaMixin",
    "ShankhaMixin",
    "NaradaMixin",
    "ChitraguptaMixin",
    "PrahladMixin",
    # Active Gene Mixins
    "ActiveSeshaMixin",
    "SeshaScribeMixin",
    "ActiveTakshakaMixin",
    "TakshakaGuardMixin",
    "ToxicInputError",
    "ActiveVasukiMixin",
    "VasukiBorderMixin",
]
