# BLOCKER #2: Circular Imports Analysis

**Date:** 2025-11-27
**Status:** ANALYZED
**Total Workarounds Found:** 92 try/except ImportError patterns

---

## The Real Problem vs False Problems

### **REAL Circular Import Problems: 3 Categories**

#### **Category 1: OathMixin Optional (23 workarounds)**
```python
# Almost every agent does this:
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

class SomeAgent(VibeAgent, OathMixin if OathMixin else object):
    ...
```

**Problem:** Agents want optional Oath capability but can't guarantee it loads.
**Root Cause:** OathMixin imports ConstitutionalOath which might have dependencies.
**Solution:** Move to Layer 1 as Protocol, make it always available.

---

#### **Category 2: External Dependencies (7 workarounds)**
```python
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None
```

**Problem:** Code tries to import optional external packages.
**Root Cause:** NOT circular imports! It's "graceful degradation" for optional features.
**Solution:** These should STAY as try/except OR move to requirements file.

---

#### **Category 3: Internal Circular Dependencies (62 workarounds)**
```python
try:
    from some.module import SomeClass
except ImportError:
    # "Import here to avoid circular dependency"
    pass
```

**Problem:** Two modules want to import each other.
**Root Cause:** Bad architecture - should inject dependencies instead.
**Solution:** 3-Layer architecture fixes this by design.

---

## What Needs to Happen

### **Don't Fix (#2, #7):**
- OpenAI, PIL, Tavily imports - these are EXTERNAL
- They should stay try/except (feature detection)
- OR go in requirements.txt with optional extras

### **DO Fix (#1, #3):**

**#1: OathMixin (23 workarounds)**
- Move OathMixin to Layer 1 (Protocols)
- Make it core part of system (not optional)
- Becomes `OathProtocol` in protocols layer
- All agents can safely import without try/except

**#3: Internal Circular (62 workarounds)**
- Layer 1: All Protocols (no imports except typing)
- Layer 2: Implementations (only Layer 1 imports)
- Layer 3: Integration (dynamic via PhoenixConfigEngine)
- Circular imports become IMPOSSIBLE

---

## Action Items for BLOCKER #2

### **Phase 1: Restructure (No Code Changes Yet)**
1. Create `vibe_core/protocols/` directory
2. Plan which files go to Layer 1, 2, 3
3. Understand OathMixin → OathProtocol migration

### **Phase 2: Layer 1 - Protocols**
- Move all ABCs to `protocols/`
- Create `oath_protocol.py`
- NO implementations, only interfaces
- Minimal imports (only typing, abc)

### **Phase 3: Layer 2 - Implementations**
- Reorganize agents/, store/, ledger/
- Update imports: only from protocols
- Make OathMixin implementation of OathProtocol
- All external optional stuff stays try/except

### **Phase 4: Layer 3 - Integration**
- Create PhoenixConfigEngine
- Dynamic instantiation from config
- All wiring happens here

### **Phase 5: Remove Workarounds**
- Delete most try/except ImportError (except external deps)
- Clean imports
- Zero circular dependencies

---

## Effort Estimate

| Phase | Files | Risk | Time |
|-------|-------|------|------|
| Restructure | - | LOW | 30min |
| Layer 1 | 5-7 | LOW | 1h |
| Layer 2 | 20+ | MEDIUM | 2h |
| Layer 3 | 1 | LOW | 1h |
| Cleanup | 62 | MEDIUM | 1.5h |
| **TOTAL** | | | **5.5h** |

---

## Next Step

**Start Phase 1: Restructure & Plan**

We identify exactly:
- Which files → Layer 1
- Which files → Layer 2
- Which files → Layer 3
- What gets deleted (workarounds)

NO code changes yet. Just planning.
