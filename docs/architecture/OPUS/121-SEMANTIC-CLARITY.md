# OPUS-121: Semantic Clarity - Event vs LedgerEvent

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-118 (Split-Brain Surgery), OPUS-120 (Logic Fusion)

## Summary

"नाम रूपं च निर्दिष्टं" - "Name and form must be declared."

OPUS-121 addresses semantic ambiguity: two different `Event` classes existed
with the same name but fundamentally different purposes. This was NOT a
Split-Brain (duplicate code) - it was a **Namespace Collision**.

**The Fix**: Rename Herald's `Event` to `LedgerEvent` to clarify its distinct
purpose as a signed, persistent event for event sourcing.

## The Problem

Before OPUS-121:

```python
# Which Event is this?
from vibe_core.event_bus import Event        # Real-time pub/sub
from vibe_core.cartridges.system.herald.core.memory import Event  # Signed ledger event

# Import collision - silent disaster
```

Both called `Event`, but fundamentally different:

| Aspect | EventBus Event | Herald Event |
|--------|----------------|--------------|
| Purpose | Real-time pub/sub | Event sourcing / Audit trail |
| Persistence | None (in-memory) | JSONL ledger file |
| Signature | None | NIST P-256 cryptographic |
| Sequence | None | Monotonic counter |
| Fields | event_id, message, details | payload, signature, sequence_number |

**These are NOT duplicates - they are semantically different types.**

Merging them would be like merging `int` and `str` because both are "data types".

## The Solution

### Rename for Semantic Clarity

```python
# BEFORE: Ambiguous
class Event:  # Which one?

# AFTER: Clear semantics
class LedgerEvent:  # Signed, persistent (Herald)
# vs
class Event:  # Real-time, in-memory (EventBus)
```

### The Naming Convention

| Module | Class Name | Purpose |
|--------|------------|---------|
| `vibe_core.event_bus` | `Event` | Lightweight real-time signals |
| `vibe_core.cartridges.system.herald.core.memory` | `LedgerEvent` | Signed persistent records |

## Implementation

### memory.py

```python
@dataclass
class LedgerEvent:
    """
    OPUS-121: Renamed from Event to LedgerEvent for semantic clarity.

    Immutable, signed event representing an action taken by HERALD.
    This is the PERSISTENT event type for event sourcing.

    NOT to be confused with vibe_core.event_bus.Event which is for
    real-time, in-memory pub/sub communication.
    """
    event_type: str
    timestamp: str
    agent_id: str
    payload: Dict[str, Any]
    signature: Optional[str] = None
    sequence_number: Optional[int] = None

# Backward compatibility alias
Event = LedgerEvent
```

### scribe_tool.py

```python
# OPUS-121: Import LedgerEvent (renamed from Event)
from vibe_core.cartridges.system.herald.core.memory import LedgerEvent

# Backward compatibility alias
Event = LedgerEvent
```

## Verification

```python
from vibe_core.event_bus import Event as BusEvent
from vibe_core.cartridges.system.herald.core.memory import LedgerEvent

# Semantic separation verified
assert BusEvent is not LedgerEvent  # ✅ Different types

# Backward compatibility preserved
from vibe_core.cartridges.system.herald.core.memory import Event
assert Event is LedgerEvent  # ✅ Alias works
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│           OPUS-121: Semantic Clarity Architecture                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REAL-TIME EVENTS (Nervous System):                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  vibe_core/event_bus.py                                         │   │
│  │  ─────────────────────────────────────────────────              │   │
│  │  class Event:                                                   │   │
│  │    • Lightweight, in-memory                                     │   │
│  │    • No persistence                                             │   │
│  │    • No cryptographic signature                                 │   │
│  │    • For pub/sub communication                                  │   │
│  │    • "The nerve signal"                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  PERSISTENT EVENTS (Memory/Audit):                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  vibe_core/cartridges/system/herald/core/memory.py              │   │
│  │  ─────────────────────────────────────────────────              │   │
│  │  class LedgerEvent:  (OPUS-121: renamed from Event)             │   │
│  │    • Signed with NIST P-256                                     │   │
│  │    • Persisted to JSONL ledger                                  │   │
│  │    • Monotonic sequence numbers                                 │   │
│  │    • For event sourcing / audit trail                           │   │
│  │    • "The memory engram"                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  SEMANTIC DISTINCTION:                                                  │
│  ─────────────────────                                                  │
│  Event (Bus)      = "A signal fired across neurons"                     │
│  LedgerEvent      = "A memory carved in stone"                          │
│                                                                         │
│  One is ephemeral. One is eternal.                                      │
│  Same name was misleading. Now they speak their truth.                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/cartridges/system/herald/core/memory.py` | Renamed `Event` → `LedgerEvent`, added alias |
| `vibe_core/cartridges/system/herald/tools/scribe_tool.py` | Updated import to `LedgerEvent`, added alias |

## The Philosophical Foundation

From Sanskrit grammar (Vyakarana):

**"शब्दार्थसम्बन्धः नित्यः" - "The relationship between word and meaning is eternal."**

When two distinct concepts share a name, confusion is inevitable. The name
must reflect the essence. A nerve signal is not a memory. An `Event` in the
bus is not an `Event` in the ledger.

OPUS-121 restores semantic integrity by giving each concept its proper name.

## What This Is NOT

This is **NOT** a Split-Brain fix like OPUS-118/120. Those fixed **duplicate code**.

This fixes **namespace collision** - two legitimately different types that
unfortunately shared a name. The solution is not merger but **distinction**.

## Related

- OPUS-118: Split-Brain Surgery (unified duplicate types)
- OPUS-120: Logic Fusion (unified duplicate logic)
- OPUS-121: Semantic Clarity (distinguished different types)

## Future: OPUS-122+

Possible next steps:
- **OPUS-122: Task Analysis** - Check if `Task` class has similar issues
- **OPUS-123: Import Audit** - Automated detection of namespace collisions
