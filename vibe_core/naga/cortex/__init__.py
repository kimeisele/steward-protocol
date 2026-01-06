"""
NAGA Cortex - The Central Nervous System.

HOLON: Lazy loading to prevent import cycles.

"Das Nervensystem, nicht das Gehirn" - NAGAs observe, correlate, inform.

The Cortex is the INTELLIGENCE HUB that:
1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
2. CORRELATES patterns across multiple signal sources
3. DECIDES what action is needed (but does NOT execute directly)
4. INFORMS target systems (Shuddhi, Envoy, Manas) with intelligence

Usage:
    from vibe_core.naga.cortex import NagaCortex
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex as _NagaCortex
    from vibe_core.naga.cortex.decisions import (
        CortexDecision as _CortexDecision,
        DecisionAction as _DecisionAction,
        DispatchResult as _DispatchResult,
    )
    from vibe_core.naga.cortex.signals import (
        CommitSignal as _CommitSignal,
        CorrelatedContext as _CorrelatedContext,
        FloodSignal as _FloodSignal,
        NagaSignal as _NagaSignal,
        SignalType as _SignalType,
        StateSignal as _StateSignal,
    )

_LAZY_MAP = {
    "NagaCortex": ("vibe_core.naga.cortex.cortex_main", "NagaCortex"),
    "CortexDecision": ("vibe_core.naga.cortex.decisions", "CortexDecision"),
    "DecisionAction": ("vibe_core.naga.cortex.decisions", "DecisionAction"),
    "DispatchResult": ("vibe_core.naga.cortex.decisions", "DispatchResult"),
    "NagaSignal": ("vibe_core.naga.cortex.signals", "NagaSignal"),
    "FloodSignal": ("vibe_core.naga.cortex.signals", "FloodSignal"),
    "CommitSignal": ("vibe_core.naga.cortex.signals", "CommitSignal"),
    "StateSignal": ("vibe_core.naga.cortex.signals", "StateSignal"),
    "SignalType": ("vibe_core.naga.cortex.signals", "SignalType"),
    "CorrelatedContext": ("vibe_core.naga.cortex.signals", "CorrelatedContext"),
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
    "NagaCortex",
    "NagaSignal",
    "FloodSignal",
    "CommitSignal",
    "StateSignal",
    "SignalType",
    "CorrelatedContext",
    "CortexDecision",
    "DecisionAction",
    "DispatchResult",
]
