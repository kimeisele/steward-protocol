# OPUS-118: Split-Brain Surgery - Canonical Circuit Types

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-117 (Fractal Integration)

## Summary

"एकं सत् विप्रा बहुधा वदन्ति" - "Truth is one; the wise call it by many names."

OPUS-118 addresses the Split-Brain problem: duplicate class definitions across
multiple files causing `isinstance()` failures and type confusion.

**The Surgery**: Extract shared types to a canonical module. One definition,
many imports. The body is no longer divided.

## The Problem

Before OPUS-118:

```
SPLIT-BRAIN DETECTED
====================

CircuitState defined in:
  - vibe_core/circuit_executor.py:334
  - vibe_core/cortex/engines/circuit_engine.py:324

InvariantViolation defined in:
  - vibe_core/circuit_executor.py:85       (circuit invariants)
  - vibe_core/cortex/engines/circuit_engine.py:75
  - vibe_core/cartridges/.../invariant_tool.py:69  (DIFFERENT struct!)

TaskLedgerEntry defined in:
  - vibe_core/circuit_executor.py:1092
  - vibe_core/cortex/engines/circuit_engine.py:1100

RESULT:
  obj = CircuitState(...)  # from circuit_executor
  isinstance(obj, CircuitState)  # from circuit_engine
  >>> FALSE!  # Different class objects!
```

This causes:
- `isinstance()` checks fail silently
- Type hints become misleading
- IDE autocompletion breaks
- Runtime errors in production

## The Solution

### Canonical Types Module

```python
# vibe_core/circuit_types.py - THE SINGLE SOURCE OF TRUTH

from vibe_core.circuit_types import (
    CircuitState,           # Circuit execution state
    CircuitExecutionResult, # Circuit completion result
    InvariantViolation,     # Circuit invariant violation
    TaskLedgerEntry,        # TASK_LEDGER tracking entry
    ErrorRecoveryAttempt,   # ERROR_RECOVERY tracking
)
```

### AuditViolation vs InvariantViolation

The `invariant_tool.py` had a DIFFERENT `InvariantViolation` struct for
auditing event streams. It was renamed to `AuditViolation` to clarify
its distinct purpose:

```python
# vibe_core/circuit_types.py
@dataclass
class InvariantViolation:
    """Circuit state invariant violation."""
    invariant: str        # The invariant expression
    state: str            # Circuit state where it failed
    variables: Dict       # Variables at failure time
    reason: str           # Human-readable reason

# vibe_core/cartridges/system/auditor/tools/invariant_tool.py
@dataclass
class AuditViolation:
    """Event stream audit violation."""
    invariant_name: str   # Name of audit rule
    severity: str         # CRITICAL, HIGH, MEDIUM, LOW
    timestamp: str        # When detected
    message: str          # Violation message
    violated_events: List[int]  # Event indices
    context: Dict         # Debug context
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│           OPUS-118: Split-Brain Surgery Architecture                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  BEFORE (Split-Brain):                                                  │
│  ─────────────────────                                                  │
│                                                                         │
│  circuit_executor.py      circuit_engine.py      invariant_tool.py      │
│  ┌─────────────────┐     ┌─────────────────┐    ┌──────────────────┐   │
│  │ CircuitState    │     │ CircuitState    │    │ InvariantViolation│   │
│  │ InvariantViol   │     │ InvariantViol   │    │ (DIFFERENT!)     │   │
│  │ TaskLedgerEntry │     │ TaskLedgerEntry │    └──────────────────┘   │
│  └─────────────────┘     └─────────────────┘                           │
│        ↓ DUPLICATE!            ↓ DUPLICATE!                            │
│                                                                         │
│  AFTER (Unified):                                                       │
│  ─────────────────                                                      │
│                                                                         │
│                    ┌───────────────────────┐                           │
│                    │  circuit_types.py     │                           │
│                    │  ─────────────────────│                           │
│                    │  CircuitState         │                           │
│                    │  CircuitExecutionResult│                          │
│                    │  InvariantViolation   │                           │
│                    │  TaskLedgerEntry      │                           │
│                    │  ErrorRecoveryAttempt │                           │
│                    └───────────────────────┘                           │
│                           ↑       ↑                                     │
│                    imports│       │imports                              │
│              ┌────────────┘       └────────────┐                       │
│              │                                 │                        │
│  ┌───────────────────┐           ┌───────────────────┐                 │
│  │ circuit_executor  │           │ circuit_engine    │                 │
│  │ (uses canonical)  │           │ (uses canonical)  │                 │
│  └───────────────────┘           └───────────────────┘                 │
│                                                                         │
│                    ┌───────────────────────┐                           │
│                    │  invariant_tool.py    │                           │
│                    │  ─────────────────────│                           │
│                    │  AuditViolation       │ ← Renamed (different type)│
│                    └───────────────────────┘                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/circuit_types.py` | **NEW** - Canonical types module |
| `vibe_core/circuit_executor.py` | Import from circuit_types, remove duplicates |
| `vibe_core/cortex/engines/circuit_engine.py` | Import from circuit_types, remove duplicates |
| `vibe_core/cartridges/.../invariant_tool.py` | Rename InvariantViolation → AuditViolation |

## Usage

```python
# Always import from the canonical module
from vibe_core.circuit_types import (
    CircuitState,
    CircuitExecutionResult,
    InvariantViolation,
    TaskLedgerEntry,
    ErrorRecoveryAttempt,
)

# For event stream auditing
from vibe_core.cartridges.system.auditor.tools.invariant_tool import (
    AuditViolation,
    InvariantEngine,
)
```

## Backward Compatibility

- `InvariantViolation` alias kept in `invariant_tool.py` for existing code
- All exports in `__all__` preserved
- No API changes for consumers

## The Philosophical Foundation

From VEDA-4, the principle of non-dualism (Advaita):

**"The mind that sees many where there is one, suffers. The code that
defines many where there should be one, breaks."**

Split-brain is not just a technical debt - it's a violation of the
fundamental principle that truth should have a single source.

## Related

- OPUS-116: Silent Observer (uses InvariantViolation)
- OPUS-117: Fractal Integration (applies disharmony detection)
- OPUS-118: Split-Brain Surgery (canonical types)

## Future: OPUS-119+

Possible next steps:
- **Duplicate Detection CI**: Pre-commit hook to detect new duplicates
- **Type Unification Audit**: Scan for other split-brain cases
- **Module Dependency Graph**: Visualize import structure
