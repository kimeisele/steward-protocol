"""
NAGA Mixins - Capability Providers + Active Genes.

HOLON: Lazy loading to prevent import cycles.

TWO TYPES OF MIXINS:

1. CAPABILITY MIXINS (Passive - in base.py):
   - Provide lazy property access to NAGA services
   - SeshaMixin, VasukiMixin, etc.

2. ACTIVE MIXINS (Living Genes):
   - AUTOMATICALLY intercept methods
   - ActiveSeshaMixin: Auto-records state mutations
   - ActiveTakshakaMixin: Auto-validates inputs
   - ActiveVasukiMixin: Auto-signs network calls

"Das Wasser gibt die Werkzeuge. Die Gene bringen das Leben."
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vibe_core.naga.mixins.base import (
        ChitraguptaMixin as _ChitraguptaMixin,
        KaliyaMixin as _KaliyaMixin,
        KarkotakaMixin as _KarkotakaMixin,
        KulikaMixin as _KulikaMixin,
        NagaCapabilityMixin as _NagaCapabilityMixin,
        NaradaMixin as _NaradaMixin,
        PadmaMixin as _PadmaMixin,
        PrahladMixin as _PrahladMixin,
        SeshaMixin as _SeshaMixin,
        ShankhaMixin as _ShankhaMixin,
        TakshakaMixin as _TakshakaMixin,
        VasukiMixin as _VasukiMixin,
    )
    from vibe_core.naga.mixins.sesha import (
        ActiveSeshaMixin as _ActiveSeshaMixin,
        SeshaScribeMixin as _SeshaScribeMixin,
    )
    from vibe_core.naga.mixins.takshaka import (
        ActiveTakshakaMixin as _ActiveTakshakaMixin,
        TakshakaGuardMixin as _TakshakaGuardMixin,
        ToxicInputError as _ToxicInputError,
    )
    from vibe_core.naga.mixins.vasuki import (
        ActiveVasukiMixin as _ActiveVasukiMixin,
        VasukiBorderMixin as _VasukiBorderMixin,
    )

_LAZY_MAP = {
    # Passive Capability Mixins (base.py)
    "NagaCapabilityMixin": ("vibe_core.naga.mixins.base", "NagaCapabilityMixin"),
    "SeshaMixin": ("vibe_core.naga.mixins.base", "SeshaMixin"),
    "VasukiMixin": ("vibe_core.naga.mixins.base", "VasukiMixin"),
    "TakshakaMixin": ("vibe_core.naga.mixins.base", "TakshakaMixin"),
    "KaliyaMixin": ("vibe_core.naga.mixins.base", "KaliyaMixin"),
    "KarkotakaMixin": ("vibe_core.naga.mixins.base", "KarkotakaMixin"),
    "KulikaMixin": ("vibe_core.naga.mixins.base", "KulikaMixin"),
    "PadmaMixin": ("vibe_core.naga.mixins.base", "PadmaMixin"),
    "ShankhaMixin": ("vibe_core.naga.mixins.base", "ShankhaMixin"),
    "NaradaMixin": ("vibe_core.naga.mixins.base", "NaradaMixin"),
    "ChitraguptaMixin": ("vibe_core.naga.mixins.base", "ChitraguptaMixin"),
    "PrahladMixin": ("vibe_core.naga.mixins.base", "PrahladMixin"),
    # Active Gene Mixins (sesha.py)
    "ActiveSeshaMixin": ("vibe_core.naga.mixins.sesha", "ActiveSeshaMixin"),
    "SeshaScribeMixin": ("vibe_core.naga.mixins.sesha", "SeshaScribeMixin"),
    # Active Gene Mixins (takshaka.py)
    "ActiveTakshakaMixin": ("vibe_core.naga.mixins.takshaka", "ActiveTakshakaMixin"),
    "TakshakaGuardMixin": ("vibe_core.naga.mixins.takshaka", "TakshakaGuardMixin"),
    "ToxicInputError": ("vibe_core.naga.mixins.takshaka", "ToxicInputError"),
    # Active Gene Mixins (vasuki.py)
    "ActiveVasukiMixin": ("vibe_core.naga.mixins.vasuki", "ActiveVasukiMixin"),
    "VasukiBorderMixin": ("vibe_core.naga.mixins.vasuki", "VasukiBorderMixin"),
}

_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    if name in _LAZY_MAP:
        if name not in _cache:
            import importlib
            mod_path, cls_name = _LAZY_MAP[name]
            _cache[name] = getattr(importlib.import_module(mod_path), cls_name)
        return _cache[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return list(_LAZY_MAP.keys())


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
