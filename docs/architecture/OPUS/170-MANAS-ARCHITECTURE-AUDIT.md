# OPUS-170: MANAS Architecture Audit - Technical Debt Analysis

> **Status**: INVESTIGATION
> **Created**: 2025-12-21
> **Auditor**: Claude (Senior Architect Mode)
> **Scope**: Full MANAS/opus_assistant architecture review

<!-- @HARNESS
intent: "Comprehensive audit of MANAS architecture and tech debt"
files:
  - path: docs/architecture/OPUS/170-MANAS-ARCHITECTURE-AUDIT.md
    required: true
    rationale: "Master audit document"
wiring:
  - pattern: "AUDIT FINDINGS"
    in: docs/architecture/OPUS/170-MANAS-ARCHITECTURE-AUDIT.md
tests:
  - tests/architecture/test_audit_compliance.py
-->

---

## Executive Summary

**MANAS Complexity:**
- 124 Python files
- 57,820 lines of code
- Multiple God Objects (2000+ lines each)

**Critical Issues Found: 8 Categories**

---

## 1. LOADER ANTI-PATTERNS

Loaders exist but are bypassed with manual imports.

| Component | Loader | Status |
|-----------|--------|--------|
| SenseManager | SenseLoader | ✅ FIXED (OPUS-167) |
| ActionManager | ActionLoader | ❌ DOES NOT USE |
| analyzers/__init__.py | AnalyzerLoader | ❌ Manual imports |
| cortex/__init__.py | SenseLoader | ❌ Manual imports |
| dojo/__init__.py | - | ❌ Manual imports |

**Evidence:**
```python
# ActionManager has ZERO ActionLoader usage:
grep -n "ActionLoader" action_manager.py
# (no output)

# But analyzers/__init__.py manually imports all:
from .contract_analyzer import ContractAnalyzer
from .semantic_analyzer import SemanticAnalyzer
# ... 7 more manual imports
```

**Fix Pattern:** Same as OPUS-167 SenseManager refactor.

---

## 2. MISSING LOADERS

Components that SHOULD have loaders but don't.

### 2.1 BridgeLoader (MISSING)

**3 bridges exist without loader:**
```
vibe_core/plugins/opus_assistant/manas/genesis_bridge.py
vibe_core/plugins/opus_assistant/manas/logger_bridge.py
vibe_core/plugins/opus_assistant/manas/weaver_bridge.py
```

Currently hardcoded in cognitive_kernel.py:
```python
from .genesis_bridge import GenesisBridge
from .logger_bridge import LoggerBridge
from .weaver_bridge import WeaverBridge

self._genesis_bridge = GenesisBridge(...)  # MANUAL
self._weaver_bridge = WeaverBridge(...)    # MANUAL
self._logger_bridge = LoggerBridge(...)    # MANUAL
```

### 2.2 SynapseLoader (MISSING)

**4 duplicate `_load_synapses()` methods:**
```
vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py:1307
vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py:446
vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py:444
vibe_core/plugins/opus_assistant/manas/triggers.py:516
```

**6+ files reference synapses.json directly:**
- akshara.py
- viveka_action.py
- mirror.py
- synaptic_seeder.py
- triggers.py
- state_management.yaml

**Fix:** Create `SynapseLoader` or `SynapticMemory.get_instance()` pattern.

---

## 3. GOD OBJECTS

Files that violate Single Responsibility Principle.

| File | Lines | Methods | Status |
|------|-------|---------|--------|
| intent_router.py | 2,376 | 50 | ❌ CRITICAL |
| cognitive_kernel.py | 2,208 | ~40 | ❌ CRITICAL |
| viveka_action.py | 1,559 | ~30 | ⚠️ HIGH |
| sutra_sense.py | 1,549 | ~25 | ⚠️ HIGH |

**cognitive_kernel.py structure:**
- 2208 lines total
- Imports 30+ modules directly
- Orchestrates everything (OODA cycle, bridges, senses, actions)
- Should be decomposed into smaller components

**intent_router.py structure:**
- 2376 lines total
- 50 methods in single class
- Handles routing, execution, fallback, logging, etc.
- Should be split by responsibility

---

## 4. CIRCULAR IMPORT RISKS

Files that import CognitiveKernel at runtime (not TYPE_CHECKING):

```
cortex/jnana.py:697      from ..cognitive_kernel import CognitiveKernel
cortex/kriya.py:326      from ..cognitive_kernel import CognitiveKernel
cortex/kriya.py:416      from ..cognitive_kernel import IntentBufferEntry
cortex/samvada_handler.py:110  from ..cognitive_kernel import CognitiveKernel
shiva.py:43              from .cognitive_kernel import CognitiveKernel
```

These are runtime imports inside methods, which creates:
- Delayed import errors (only fail when method called)
- Circular dependency risks
- Harder to test in isolation

---

## 5. SINGLETON ABUSE

Singletons found:

```python
# CognitiveKernel
CognitiveKernel.get_instance()
CognitiveKernel.has_instance()
CognitiveKernel.reset_instance()

# Varnamala (akshara.py)
_instance: Optional["Varnamala"] = None

# SynapseVocabulary (triggers.py)
_instance: Optional["SynapseVocabulary"] = None

# MayaSimulator
_global_maya: Optional[MayaSimulator] = None
```

**Problems:**
- Global state pollution
- Hard to test (need reset between tests)
- Hidden dependencies
- Thread safety concerns

---

## 6. BROKEN CABLES (from OPUS-169)

| Cable | Status | Issue |
|-------|--------|-------|
| Akasha → Kernel | ⚠️ PARTIAL | AkashaSense created but not in decision path |
| Sanskrit Matrix → Main Loop | ❌ BROKEN | Only called from Dojo meditation.py |
| Prakriti → Sanskrit Matrix | ❌ BROKEN | Zero connection between state and learning |
| CognitiveWeaver → Akshara | ❌ BROKEN | Weaver ignores phonemic layer |

---

## 7. ABSTRACTION LAYER GAPS

Missing abstraction layers:

| Gap | Description | Fix |
|-----|-------------|-----|
| BaseBridge | No common interface for bridges | Create abstract class |
| SynapticStore | No unified synapse access | Create singleton store |
| PerceptionPipeline | Senses are independent | Create pipeline abstraction |
| ActionPipeline | Actions lack common interface | Extend ActionLoader pattern |

---

## 8. METRICS

```
OPUS_ASSISTANT STATS:
- Files: 124
- Lines: 57,820
- Avg lines/file: 466

MANAS CORE STATS:
- Files: 41 (in manas/ root)
- Lines: 41,471
- Largest: intent_router.py (2376)

LOADER COVERAGE:
- Existing: 11 loaders
- Used properly: ~4 (Sense, Analyzer, Tool, Action partially)
- Missing: 2+ (Bridge, Synapse)
```

---

## REMEDIATION PRIORITY

> **Last Updated:** 2025-12-22

### P0 - CRITICAL (Week 1)
1. [x] Create SynapseLoader (consolidate 4 duplicates) ← **DONE: OPUS-171 SynapseStore (vibe_core/state/synapse_store.py)**
2. [x] Decompose intent_router.py (2376 lines → 3-4 modules) ← **DONE: 2376 → 1000 lines**
3. [ ] Fix circular imports in cortex/*

### P1 - HIGH (Week 2)
4. [x] Create BridgeLoader for 3 bridges ← **DONE: OPUS-171 (vibe_core/loaders/bridge_loader.py)**
5. [ ] Decompose cognitive_kernel.py (2208 lines → delegation) ← **GREW to 2570 lines**
6. [ ] Remove manual imports from analyzers/__init__.py

### P2 - MEDIUM (Week 3)
7. [ ] Wire Sanskrit Matrix to main loop
8. [ ] Connect Prakriti → Sanskrit Matrix
9. [x] Integrate Akasha into decision path ← **DONE: OPUS-202 (reactor + akasha_hash)**

### P3 - LOW (Ongoing)
10. [ ] Reduce singleton usage
11. [ ] Add abstraction layers
12. [ ] Improve test coverage

---

## VERIFICATION COMMANDS

```bash
# Check for duplicate patterns
grep -rh "def _load_synapses" vibe_core/plugins/opus_assistant/manas/

# Check loader usage
grep -rn "ActionLoader" vibe_core/plugins/opus_assistant/manas/

# Count file sizes
find vibe_core/plugins/opus_assistant -name "*.py" -exec wc -l {} + | sort -rn

# Find circular import risks
grep -rn "from.*cognitive_kernel import" vibe_core/plugins/opus_assistant/manas/
```

---

## RELATED OPUS DOCS

- OPUS-167: MANAS Refactoring (SenseManager fix)
- OPUS-155: Akasha Nervous System
- OPUS-169: MANAS Wiring Scratchpad
- GAD-000: Operator Inversion Principle

---

**आत्मनो मोक्षार्थं जगद्धिताय च**
*"For one's own liberation and for the welfare of the world"*
