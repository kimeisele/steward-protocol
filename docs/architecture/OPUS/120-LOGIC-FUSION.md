# OPUS-120: Logic Fusion - Kill the Clone

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-118 (Split-Brain Surgery)

## Summary

"द्वैतं न विद्यते किञ्चित्" - "Duality does not truly exist."

OPUS-118 unified the TYPES. OPUS-120 unifies the LOGIC.

Two files (`circuit_executor.py` and `circuit_engine.py`) contained ~1400 lines
of nearly identical code. This was architectural debt - a clone that had to die.

**The Lobotomy**: Replace the clone with a thin re-export proxy. One brain, many names.

## The Problem

After OPUS-118:

```
CLONE DETECTED
==============

vibe_core/circuit_executor.py         [1416 lines]
vibe_core/cortex/engines/circuit_engine.py  [1424 lines]

DIFF: ~8 lines (99.5% IDENTICAL)

Both contain:
  - CognitiveCircuitExecutor class
  - InvariantChecker class
  - MetaCircuitManager class
  - All the same logic, duplicated

WHY IS THIS BAD?
  - Changes must be made in TWO places
  - Bugs can exist in one but not the other
  - Cognitive load for developers
  - Wastes ~56KB of source code
```

## The Solution

### Architecture Decision

**Which one is the "real" brain?**

| Location | Used By | Verdict |
|----------|---------|---------|
| `vibe_core/circuit_executor.py` | verify_agent_birth.py, tests, deterministic_executor | LEGACY |
| `vibe_core/cortex/engines/circuit_engine.py` | engines/__init__.py, unified_cli | CANONICAL |

The `cortex/engines/` location is semantically correct - the Circuit Executor IS
part of the cognitive system. The root-level file is a legacy artifact.

### The Proxy Pattern

```
BEFORE (Two Brains):
┌────────────────────────────────────────────────────────────────────┐
│  vibe_core/circuit_executor.py        [1416 lines of LOGIC]       │
│  vibe_core/cortex/engines/circuit_engine.py  [1424 lines of LOGIC]│
│                                                                    │
│  DUPLICATION: 99.5%                                               │
└────────────────────────────────────────────────────────────────────┘

AFTER (One Brain + Alias):
┌────────────────────────────────────────────────────────────────────┐
│  vibe_core/cortex/engines/circuit_engine.py  [1424 lines - TRUTH] │
│                           ↑                                        │
│                           │ re-export                              │
│                           │                                        │
│  vibe_core/circuit_executor.py  [75 lines - PROXY ONLY]           │
└────────────────────────────────────────────────────────────────────┘

REDUCTION: 1416 → 75 lines (-94.7%)
```

### The Proxy Code

```python
# vibe_core/circuit_executor.py (AFTER)
"""
OPUS-120: LEGACY PROXY - LOGIC FUSION

The actual implementation has moved to the Cortex:
  -> vibe_core/cortex/engines/circuit_engine.py

"The shell remains, but the ghost has moved to the Cortex."
"""

# Re-export canonical types
from vibe_core.circuit_types import (
    CircuitExecutionResult,
    CircuitState,
    InvariantViolation,
    TaskLedgerEntry,
    ErrorRecoveryAttempt,
)

# Import everything from the Cortex engine (the canonical location)
from vibe_core.cortex.engines.circuit_engine import (
    CognitiveCircuitExecutor,
    InvariantChecker,
    MetaCircuitManager,
    create_circuit_executor,
    create_circuit_executor_with_meta,
)
```

## Verification

```python
# Both import paths work
from vibe_core.circuit_executor import CognitiveCircuitExecutor
from vibe_core.cortex.engines.circuit_engine import CognitiveCircuitExecutor as CE2

# And they are the SAME class (critical for isinstance)
assert CognitiveCircuitExecutor is CE2  # ✅ True
```

## Migration Path

**Old code** (still works):
```python
from vibe_core.circuit_executor import CognitiveCircuitExecutor
```

**New code** (preferred):
```python
from vibe_core.cortex.engines import CognitiveCircuitExecutor
```

Both are valid. The new path is preferred for new code.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│           OPUS-120: Logic Fusion Architecture                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  THE CANONICAL BRAIN:                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  vibe_core/cortex/engines/circuit_engine.py                     │   │
│  │  ─────────────────────────────────────────────────              │   │
│  │  • CognitiveCircuitExecutor  (THE implementation)               │   │
│  │  • InvariantChecker          (THE checker)                      │   │
│  │  • MetaCircuitManager        (THE manager)                      │   │
│  │  • create_circuit_executor() (THE factory)                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           ↑                                             │
│                           │ imports from                                │
│                           │                                             │
│  THE PROXY (Legacy Compatibility):                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  vibe_core/circuit_executor.py                                  │   │
│  │  ─────────────────────────────────────────────────              │   │
│  │  • Re-exports everything from cortex/engines                    │   │
│  │  • 75 lines (was 1416)                                          │   │
│  │  • "The shell remains, but the ghost has moved"                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  CANONICAL TYPES (from OPUS-118):                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  vibe_core/circuit_types.py                                     │   │
│  │  ─────────────────────────────────────────────────              │   │
│  │  • CircuitState, CircuitExecutionResult                         │   │
│  │  • InvariantViolation, TaskLedgerEntry, ErrorRecoveryAttempt    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines in circuit_executor.py | 1416 | 75 | -94.7% |
| Duplicate code | 2840 lines | 0 lines | -100% |
| Import paths | 2 separate | 2 unified | Same class |
| isinstance() reliability | Broken | Fixed | ✅ |

## The Philosophical Foundation

From Advaita Vedanta:

**"What appears as two is actually one. The duality was always an illusion."**

The two files appeared different but contained the same essence. By removing
the illusion of separation, we reveal the underlying unity.

OPUS-118 unified the **nouns** (types).
OPUS-120 unified the **verbs** (logic).

The system is now non-dual.

## Related

- OPUS-118: Split-Brain Surgery (unified types)
- OPUS-120: Logic Fusion (unified logic)

## Future: OPUS-121+

Possible next steps:
- **OPUS-121: Event Horizon** - Apply same pattern to Event class duplication
- **OPUS-122: Import Audit** - Scan for other redundant files
- **Deprecation Warning** - Add warning when importing from legacy path

---

## @HARNESS

**Files**:
- `/home/user/steward-protocol/vibe_core/cortex/engines/circuit_engine.py`
  - `CognitiveCircuitExecutor` class - THE canonical implementation
  - `InvariantChecker` class - THE canonical checker
  - `MetaCircuitManager` class - THE canonical manager
  - `create_circuit_executor()` - THE canonical factory
  - `create_circuit_executor_with_meta()` - THE canonical meta factory
- `/home/user/steward-protocol/vibe_core/circuit_executor.py`
  - PROXY ONLY - re-exports everything from circuit_engine.py
  - 75 lines (was 1416) - 94.7% reduction

**Wiring Pattern**:
```python
# CANONICAL PATH (preferred for new code)
from vibe_core.cortex.engines import CognitiveCircuitExecutor

# LEGACY PATH (still works, backward compatible)
from vibe_core.circuit_executor import CognitiveCircuitExecutor

# Both import the SAME class object
from vibe_core.circuit_executor import CognitiveCircuitExecutor as CE1
from vibe_core.cortex.engines.circuit_engine import CognitiveCircuitExecutor as CE2
assert CE1 is CE2  # True - thin proxy pattern
```

**Migration Strategy**:
- Old code using `circuit_executor.py` continues to work (re-export proxy)
- New code should import from `cortex/engines/circuit_engine.py`
- No API changes, no breaking changes
