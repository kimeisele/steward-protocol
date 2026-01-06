"""
NAGA CLI Hooks - Level -2 Observers

HOLON: Lazy loading to prevent import cycles.

These hooks wrap CLI execution at Level -2, enabling:
- Security validation (Takshaka)
- Capability enforcement (CapabilityHook)
- Performance profiling (Chitragupta)
- Audit logging (Sesha)

SAMUDRA MANTHAN: Each NAGA pulls the rope (HookChain) in coordination.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vibe_core.naga.hooks.capability_cli import CapabilityCLIHook as _CapabilityCLIHook
    from vibe_core.naga.hooks.chitragupta_cli import ChitraguptaCLIHook as _ChitraguptaCLIHook
    from vibe_core.naga.hooks.sesha_cli import SeshaCLIHook as _SeshaCLIHook
    from vibe_core.naga.hooks.takshaka_cli import TakshakaCLIHook as _TakshakaCLIHook

_LAZY_MAP = {
    "TakshakaCLIHook": ("vibe_core.naga.hooks.takshaka_cli", "TakshakaCLIHook"),
    "CapabilityCLIHook": ("vibe_core.naga.hooks.capability_cli", "CapabilityCLIHook"),
    "ChitraguptaCLIHook": ("vibe_core.naga.hooks.chitragupta_cli", "ChitraguptaCLIHook"),
    "SeshaCLIHook": ("vibe_core.naga.hooks.sesha_cli", "SeshaCLIHook"),
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
    "TakshakaCLIHook",
    "CapabilityCLIHook",
    "ChitraguptaCLIHook",
    "SeshaCLIHook",
]
