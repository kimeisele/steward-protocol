# OPUS-167: MANAS Cognitive Kernel Refactoring

**Status:** IN_PROGRESS
**Priority:** CRITICAL
**Created:** 2025-12-21
**Author:** Claude (Opus 4.5)

---

## Executive Summary

The MANAS Cognitive Kernel has accumulated critical technical debt that prevents it from functioning as intended. This document defines THE WAY to fix it - not quick patches, but proper architectural refactoring that scales.

**Current State:** MANAS is silent. It perceives but doesn't act.
**Root Cause:** Architectural inversion - the kernel does everything instead of delegating.
**Solution:** Restore fractal architecture - Senses generate Intents, Kernel orchestrates.

---

## Problem Analysis

### 1. Size Comparison

| Component | Lines | Status |
|-----------|-------|--------|
| kernel_impl.py (Real Kernel) | 1,838 | Reference |
| cognitive_kernel.py | 2,815 | **BLOATED** |
| Cortex total | 18,845 | Complex but ok |

**Verdict:** CognitiveKernel is LARGER than the real OS kernel. Unacceptable.

### 2. Architectural Inversion

```
EXPECTED (Fractal):              ACTUAL (Monolithic):
┌─────────────┐                  ┌─────────────────────┐
│   Kernel    │ ← Orchestrates   │      Kernel         │
│   (slim)    │                  │  ┌───────────────┐  │
└──────┬──────┘                  │  │ perceive()    │  │
       │                         │  │ generate()    │  │
       ▼                         │  │ topic_map     │  │
┌─────────────┐                  │  │ ledger        │  │
│ SenseLoader │ ← Auto-discovery │  │ intent_buffer │  │
└──────┬──────┘                  │  │ 82 methods    │  │
       │                         │  └───────────────┘  │
       ▼                         └─────────────────────┘
┌─────────────┐                           │
│  [Senses]   │ ← Generate Intents        ▼
└──────┬──────┘                  ┌─────────────────────┐
       │                         │  [Senses UNUSED]    │
       ▼                         │  (only perceive())  │
   Intents                       └─────────────────────┘
```

### 3. Critical Bugs Found

| Bug | Severity | Description |
|-----|----------|-------------|
| Context Leak | CRITICAL | `generate_intents({})` - empty context passed |
| Intent Location | CRITICAL | 7 Intent() in kernel, 0 in senses |
| Unused Loaders | HIGH | SenseLoader created but manual init used |
| Method Count | HIGH | 82 public methods in one class |

### 4. OODA Cycle Broken

```python
# _perceive() phase - data collected
metadata = {
    "vibration_count": 5,
    "healing_count": 3,
    "gap_count": 2,
}

# _orient() phase - DATA DISCARDED!
new_intents = await self._intent_generator.generate_intents({})  # EMPTY!
```

---

## The Solution: Fractal Restoration

### Principle: "As Above, So Below"

The Vedic architecture is fractal. Every layer follows the same pattern:
- **Perceive** → Collect observations
- **Orient** → Understand context
- **Decide** → Choose action
- **Act** → Execute

Senses should be mini-OODA loops themselves:
```python
class BaseSense:
    def perceive(self) -> Perception: ...      # Collect
    def generate_intents(self) -> List[Intent]: ...  # Decide what to do
```

---

## Implementation Plan

### Phase 1: BaseSense Interface Fix

**File:** `vibe_core/plugins/opus_assistant/manas/cortex/base.py`

```python
class BaseSense(ABC):
    """Base class for all MANAS Senses (Jnanendriyas)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique sense identifier."""
        pass

    @abstractmethod
    def perceive(self) -> Any:
        """Collect observations from the environment."""
        pass

    @abstractmethod
    def generate_intents(self, context: Optional[Dict] = None) -> List[Intent]:
        """
        Generate intents based on perception.

        THE KEY CHANGE: Senses are responsible for intent generation,
        not the kernel. This restores the fractal architecture.
        """
        pass
```

### Phase 2: Migrate Intent Generation to Senses

Each sense gets a `generate_intents()` method:

| Sense | Current Location | New Location |
|-------|-----------------|--------------|
| PrakritiSense | `_perceive_and_generate_healing_intents()` | `prakriti_sense.generate_intents()` |
| PranaSense | `_perceive_and_generate_presence_intents()` | `prana_sense.generate_intents()` |
| SutraSense | `_perceive_and_generate_gap_intents()` | `sutra_sense.generate_intents()` |
| ShrutaSense | `_perceive_filesystem_vibrations()` | `shruta_sense.generate_intents()` |

### Phase 3: SenseLoader Integration

**File:** `cognitive_kernel.py`

```python
def _init_senses(self) -> None:
    """Initialize senses via UnifiedLoader pattern."""
    from vibe_core.loaders import SenseLoader

    senses, meta = SenseLoader.discover_and_load(
        workspace=self._workspace,
        config=self._full_config,
    )
    self._senses = senses  # Dict[str, BaseSense]

    logger.info(f"Loaded {len(senses)} senses: {list(senses.keys())}")
```

**Delete:** All manual `_init_prakriti_sense()`, `_init_dharma_sense()`, etc.

### Phase 4: OODA Context Flow Fix

```python
async def _perceive(self) -> Tuple[List[Intent], Dict]:
    """PERCEIVE: All senses generate intents."""
    all_intents = []
    metadata = {}

    for name, sense in self._senses.items():
        try:
            intents = sense.generate_intents()
            all_intents.extend(intents)
            metadata[f"{name}_count"] = len(intents)
        except Exception as e:
            logger.warning(f"Sense {name} failed: {e}")

    return all_intents, metadata

async def _orient(self, observations: List[Intent]) -> Tuple[List[Intent], Dict]:
    """ORIENT: Combine with IntentGenerator analysis."""
    context = {
        "observations": observations,
        "observation_count": len(observations),
    }

    # IntentGenerator adds semantic analysis
    generated = await self._intent_generator.generate_intents(context)

    return observations + generated, {"generated": len(generated)}
```

### Phase 5: Extract IntentBuffer Class

**New File:** `vibe_core/plugins/opus_assistant/manas/intent_buffer.py`

```python
@dataclass
class IntentBufferEntry:
    intent: Intent
    status: str = "pending"
    added_at: str = field(default_factory=...)
    executed_at: Optional[str] = None
    execution_result: Optional[Dict] = None

class IntentBuffer:
    """Manages the intent lifecycle."""

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._entries: List[IntentBufferEntry] = []
        self._load()

    def add(self, intent: Intent) -> bool: ...
    def approve(self, intent_id: str) -> bool: ...
    def reject(self, intent_id: str, reason: str) -> bool: ...
    def get_pending(self) -> List[Intent]: ...
    def cleanup_expired(self) -> int: ...

    def _load(self) -> None: ...
    def _save(self) -> None: ...
```

**Migrate from kernel:** All 18 intent-related methods.

### Phase 6: Kernel Slimdown

**Target:** < 500 lines

**Remaining responsibilities:**
1. OODA cycle orchestration
2. Sense/Action loader initialization
3. Config management
4. External API (think(), approve(), etc.)

---

## Success Criteria

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| cognitive_kernel.py lines | 2,815 | < 500 | |
| Intent() in kernel | 7 | 0 | |
| Intent() in senses | 0 | 7+ | |
| Manual _init_ methods | 10 | 0 | |
| Public methods | 82 | < 20 | |
| Tests passing | 43/43 | 43/43 | |

---

## Test Strategy

1. **Unit Tests:** Each sense's `generate_intents()` tested in isolation
2. **Integration Tests:** Full OODA cycle with mocked senses
3. **Regression:** Existing 43 tests must pass

---

## @HARNESS

```yaml
verification:
  - type: line_count
    file: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    max: 500

  - type: grep_count
    pattern: "Intent\\("
    file: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    expected: 0

  - type: grep_count
    pattern: "def _init_.*_sense"
    file: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    expected: 0

  - type: test
    command: pytest vibe_core/plugins/opus_assistant/manas/tests/ -v
    expected: all_pass
```

---

## References

- OPUS-032: MANAS Awakening (original design)
- OPUS-095: Orchestration Cycle (OODA pattern)
- OPUS-105: Genesis Fortress (UnifiedLoader)
- VEDA-4: Loader Architecture
