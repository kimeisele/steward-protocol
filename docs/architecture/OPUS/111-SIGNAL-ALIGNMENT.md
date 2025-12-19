# OPUS-111: Signal Alignment

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)

## Summary

"Ein Gehirn, das seine eigene Sprache nicht versteht, ist lobotomiert."

OPUS-111 establishes the **Synaptic Vocabulary** - a canonical registry of trigger
and action patterns that ensures all components in MANAS speak the same language.

## Problem Statement

### Memory Pollution (Before)

During OPUS-110 testing, a test intent was executed:
```python
test_intent = Intent(
    intent_type='test_action',
    params={'gap_type': 'test_gap'},
)
kernel._update_synapses(test_intent, success=True)
```

This created a polluted synapse:
```json
"trigger:gap_detected:test_gap": {
    "action:test_action": 0.55
}
```

**Problem**: Test data was committed to production memory (synapses.json).

### Vocabulary Mismatch (Before)

The `_extract_trigger()` method generated dynamic strings:
```python
return f"trigger:file_changed:{parts[0]}/{parts[1]}/**"
# Generated: "trigger:file_changed:vibe_core/loaders/**"
```

But the seed synapses had different patterns:
```json
"trigger:file_changed:vibe_core/**/*.py": { ... }
```

**Problem**: These strings don't match. The synapses are dead.

## Solution

### 1. TriggerRegistry (`triggers.py`)

A canonical vocabulary of all valid trigger patterns:

```python
class TriggerPatterns(str, Enum):
    # Error triggers
    TEST_FAILURE = "trigger:test_failure"
    ERROR_DETECTED = "trigger:error_detected"

    # File change triggers (normalized buckets)
    FILE_CHANGED_CORE = "trigger:file_changed:vibe_core/**"
    FILE_CHANGED_TESTS = "trigger:file_changed:tests/**"
    FILE_CHANGED_DOCS = "trigger:file_changed:docs/**"

    # Gap triggers
    GAP_MISSING_CODE = "trigger:gap_detected:missing_code"
    GAP_MISSING_DOC = "trigger:gap_detected:missing_doc"
    # ... 24 total patterns
```

### 2. ActionPatterns

Canonical actions that MANAS can learn:

```python
class ActionPatterns(str, Enum):
    NOTIFY_OPERATOR = "action:notify_operator"
    RUN_TESTS = "action:run_tests"
    CHECK_LINT = "action:check_lint"
    # ... etc
```

### 3. Normalization Functions

```python
def normalize_file_path(path: str) -> TriggerPatterns:
    """
    "vibe_core/loaders/foo.py" → TriggerPatterns.FILE_CHANGED_CORE
    "tests/unit/test_foo.py"   → TriggerPatterns.FILE_CHANGED_TESTS
    """

def normalize_trigger(intent: Intent) -> Optional[TriggerPatterns]:
    """
    Main entry point. Returns canonical trigger or None.
    None means: Don't learn from this intent (prevents pollution).
    """
```

### 4. Refactored `_extract_trigger()`

```python
def _extract_trigger(self, intent: Intent) -> Optional[str]:
    """OPUS-111: Uses TriggerRegistry for normalization."""
    from .triggers import normalize_trigger

    pattern = normalize_trigger(intent)
    return pattern.value if pattern else None
```

**Key change**: Returns `None` for non-canonical intents instead of generating
dynamic strings. This prevents memory pollution.

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/plugins/opus_assistant/manas/triggers.py` | NEW: TriggerRegistry |
| `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py` | Refactored `_extract_trigger()` |
| `.opus_state/synapses.json` | Cleaned + migrated to schema v2 |

## Migration

### synapses.json v1 → v2

```diff
- "schema": "v1"
+ "schema": "v2"

- "trigger:file_changed:vibe_core/**/*.py"
+ "trigger:file_changed:vibe_core/**"

- "trigger:gap_detected:test_gap": { ... }  # REMOVED (pollution)

+ "vocabulary_version": "triggers.py:TriggerPatterns"
```

## Verification

```bash
python -c "
from vibe_core.plugins.opus_assistant.manas.triggers import normalize_file_path
print(normalize_file_path('vibe_core/foo.py').value)
# Output: trigger:file_changed:vibe_core/**
"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAS Cognitive Kernel                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Intent Execution                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ _update_synapses│                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐     ┌──────────────────────┐          │
│  │ _extract_trigger│────▶│ triggers.py          │          │
│  └─────────────────┘     │ normalize_trigger()  │          │
│                          │ TriggerPatterns      │          │
│                          │ ActionPatterns       │          │
│                          └──────────┬───────────┘          │
│                                     │                       │
│                                     ▼                       │
│                          ┌──────────────────────┐          │
│                          │ Canonical Pattern    │          │
│                          │ or None (no learn)   │          │
│                          └──────────┬───────────┘          │
│                                     │                       │
│                                     ▼                       │
│                          ┌──────────────────────┐          │
│                          │ synapses.json        │          │
│                          │ (schema v2)          │          │
│                          └──────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Insight

**Before**: Every intent could pollute the synaptic memory with arbitrary strings.

**After**: Only intents with canonical triggers can update synapses. Non-canonical
intents return `None` and are silently ignored (no learning, no pollution).

This is the difference between:
- A brain that remembers everything (including garbage)
- A brain that only remembers what it understands

## Related

- OPUS-108: Initial Synapses (created synapses.json)
- OPUS-110: Synaptic Learning Loop (Hebbian learning)
- OPUS-112: Future - Synaptic Routing (use learned weights for intent selection)

---

## @HARNESS

**Files**:
- `/home/user/steward-protocol/vibe_core/plugins/opus_assistant/manas/triggers.py`
  - `TriggerPatterns` enum - canonical trigger vocabulary
  - `ActionPatterns` enum - canonical action vocabulary
  - `normalize_trigger()` - normalizes intents to canonical patterns
  - `normalize_file_path()` - maps file paths to trigger buckets
- `/home/user/steward-protocol/vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`
  - `_extract_trigger()` - uses TriggerRegistry for normalization
  - `_update_synapses()` - updates synaptic weights (returns None for non-canonical)

**Wiring Pattern**:
```python
# Intent arrives → normalize → extract trigger → update synapses
intent = Intent(intent_type='file_changed', params={'path': 'vibe_core/foo.py'})
trigger = normalize_trigger(intent)  # → TriggerPatterns.FILE_CHANGED_CORE
if trigger:
    self._update_synapses(intent, success=True)  # Only canonical triggers are learned
```

**Validation**:
```bash
python -c "from vibe_core.plugins.opus_assistant.manas.triggers import normalize_file_path; print(normalize_file_path('vibe_core/foo.py').value)"
# Expected: trigger:file_changed:vibe_core/**
```
