"""
NAGA Cortex - The Central Nervous System.

"Das Nervensystem, nicht das Gehirn" - NAGAs observe, correlate, inform.

The Cortex is the INTELLIGENCE HUB that:
1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
2. CORRELATES patterns across multiple signal sources
3. DECIDES what action is needed (but does NOT execute directly)
4. INFORMS target systems (Shuddhi, Envoy, Manas) with intelligence

Key Principle: NAGAs ENHANCE existing systems, they don't REPLACE them.
- Manas still makes decisions (NAGAs inform with context)
- Shuddhi still heals (NAGAs tell it WHAT to heal)
- Envoy still routes (NAGAs adjust confidence)

Usage:
    from vibe_core.naga.cortex import NagaCortex

    cortex = NagaCortex(naga_orchestrator)
    cortex.receive_signal(signal)  # From FloodManager/CommitWatcher
"""

from vibe_core.naga.cortex.cortex_main import NagaCortex
from vibe_core.naga.cortex.decisions import (
    CortexDecision,
    DecisionAction,
    DispatchResult,
)
from vibe_core.naga.cortex.signals import (
    CommitSignal,
    CorrelatedContext,
    FloodSignal,
    NagaSignal,
    SignalType,
    StateSignal,
)

__all__ = [
    "NagaCortex",
    # Signals
    "NagaSignal",
    "FloodSignal",
    "CommitSignal",
    "StateSignal",
    "SignalType",
    "CorrelatedContext",
    # Decisions
    "CortexDecision",
    "DecisionAction",
    "DispatchResult",
]
