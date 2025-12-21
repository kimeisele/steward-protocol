# OPUS-171: The ONE TRUE Architecture - FINAL Unification Plan

> **Status**: ARCHITECTURE PLAN
> **Created**: 2025-12-21
> **Auditor**: Claude (Senior Architect Mode)
> **Mandate**: "German Engineering - Build roads, not paths. Do it ONCE but RIGHT."

---

## THE DISCOVERY: System-Level Already Exists!

After deep investigation of `kernel_impl.py` (the REAL blueprint), I discovered:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM LEVEL EXISTS!                         │
│                    vibe_core/state/                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  prakriti.py        → Unified State Engine (KERNEL USES THIS)  │
│  unified_akshara.py → Routing + PRANA (Exploration)            │
│  sanskrit_matrix.py → Phonemic Memory Compression              │
│  samskara.py        → Memory Impressions                       │
│  cognitive_weaver.py → State ↔ Knowledge Bridge                │
│  state_service.py   → StateService (MANAS partially uses)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ SHOULD USE
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    MANAS (DUPLICATES!)                          │
│                    manas/                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  akshara.py (1061 lines)  → DUPLICATES unified_akshara logic!  │
│  triggers.py              → Own SynapticMemory + _load_synapses │
│  viveka_action.py         → Own _load_synapses (DIFFERENT v1)   │
│  synaptic_seeder.py       → Own _load_synapses (v2)            │
│  mirror.py                → Own _load_synapses (mixed)         │
│                                                                 │
│  SCHEMA INCONSISTENCY:                                          │
│  - v1: {"triggers": [...], "version": "1.0"}                   │
│  - v2: {"weights": {...}, "schema": "v2"}                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## THE ROOT CAUSE

1. **MANAS was built separately** from the Kernel infrastructure
2. **Nobody connected** MANAS to use system-level components
3. **Duplication crept in** over time
4. **Manual cables everywhere** instead of loaders

---

## THE SOLUTION: "As Above, So Below"

The Kernel pattern (`kernel_impl.py`) shows us how to do it RIGHT:

```python
# KERNEL PATTERNS (from kernel_impl.py):

# 1. BLUEPRINT PROTOCOL - Factories, not instances
self._ledger_blueprint = lambda: InMemoryLedger()
self.protect_attribute("_ledger_blueprint")

# 2. PLUGIN SYSTEM - Auto-discovery
self._plugins_map, self._plugin_metadata = PluginLoader.discover_and_load(...)

# 3. PRAKRITI - Unified State
from vibe_core.state import Prakriti
self.prakriti = Prakriti(db_path=prakriti_db_path)

# 4. CAPABILITY REGISTRY - Centralized
self.__capability_registry = CapabilityRegistry(ledger=self.ledger)

# 5. VAJRA ARMOR - Self-healing
self.vajra_seal()
```

**MANAS must follow the SAME patterns!**

---

## THE UNIFIED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                         KERNEL LEVEL                            │
│                     (vibe_core/kernel_impl.py)                  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Prakriti  │  │ PluginLoader│  │ CapRegistry │             │
│  │ (Unified    │  │ (Auto-disc) │  │ (Central)   │             │
│  │   State)    │  │             │  │             │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          │                │                │
┌─────────┼────────────────┼────────────────┼─────────────────────┐
│         │     SYSTEM STATE LAYER          │                     │
│         │     (vibe_core/state/)          │                     │
│         ▼                │                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ StateService│  │  Unified    │  │  Sanskrit   │             │
│  │ (Facade)    │  │  Akshara    │  │   Matrix    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│  ┌──────┴──────────────────────────────────┴──────┐             │
│  │              SynapseStore (NEW)                │             │
│  │         Unified synapse persistence            │             │
│  │    Single schema: {"weights": {...}, "v3"}    │             │
│  └────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ USE (not duplicate!)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MANAS COGNITIVE KERNEL                   │
│                     (opus_assistant/manas/)                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    LOADERS (VEDA-4)                         ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ││
│  │  │  Sense   │ │ Analyzer │ │  Action  │ │  Bridge  │       ││
│  │  │  Loader  │ │  Loader  │ │  Loader  │ │  Loader  │       ││
│  │  │    ✅    │ │    ✅    │ │    ✅    │ │   NEW    │       ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MANAGERS                                 ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                    ││
│  │  │  Sense   │ │  Action  │ │  Bridge  │                    ││
│  │  │ Manager  │ │ Manager  │ │ Manager  │                    ││
│  │  │  ✅ USES │ │ NEEDS FIX│ │   NEW    │                    ││
│  │  │  LOADER  │ │          │ │          │                    ││
│  │  └──────────┘ └──────────┘ └──────────┘                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ❌ REMOVE: akshara.py (duplicate)                             │
│  ❌ REMOVE: 4x _load_synapses() methods                        │
│  ✅ USE: vibe_core/state/unified_akshara.py                    │
│  ✅ USE: vibe_core/state/sanskrit_matrix.py                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## THE UNIFIED SYNAPSE SCHEMA (v3)

**Current Mess:**
```python
# v1 (viveka_action.py):
{"triggers": [...], "version": "1.0"}

# v2 (triggers.py, synaptic_seeder.py):
{"weights": {...}, "schema": "v2"}
```

**Unified v3:**
```python
{
    "schema": "v3",
    "version": "2025-12-21",

    # Weights: trigger → action → weight
    "weights": {
        "trigger:test_failure": {
            "action:run_test": 0.8,
            "action:debug": 0.5
        }
    },

    # Triggers: List for ordered access
    "triggers": [
        {
            "trigger": "trigger:test_failure",
            "varga": "MURDHANYA",
            "connections": [...]
        }
    ],

    # Metadata
    "meta": {
        "created": "2025-12-21T00:00:00Z",
        "last_updated": "2025-12-21T12:00:00Z",
        "updates_count": 42
    }
}
```

---

## THE FINAL FIX LIST (In Order)

### Phase 1: State Unification (Foundation)

| # | Task | Status |
|---|------|--------|
| 1.1 | Create `SynapseStore` in `vibe_core/state/` | ✅ DONE |
| 1.2 | Implement v1 → v3 migration | ✅ DONE |
| 1.3 | Implement v2 → v3 migration | ✅ DONE |
| 1.4 | ~~Create `SynapseLoader`~~ Not needed - SynapseStore IS the loader | ✅ N/A |

**NOTE**: VEDA-4 loaders (SenseLoader, ActionLoader) are for Python module discovery.
SynapseStore handles JSON data persistence - different pattern. Direct use via `get_synapse_store()`.

### Phase 2: MANAS Loader Cleanup

| # | Task | Status |
|---|------|--------|
| 2.1 | SenseManager uses SenseLoader | ✅ DONE |
| 2.2 | Create BridgeLoader | TODO |
| 2.3 | Create BridgeManager (uses BridgeLoader) | TODO |
| 2.4 | ActionManager uses ActionLoader | TODO |
| 2.5 | Remove analyzers/__init__.py manual imports | TODO |

### Phase 3: Remove Duplicates (Synapse Loading Only!) ✅ COMPLETE

**NOTE**: OPUS-172 analysis confirmed manas/akshara.py is the CORE phonemic library.
unified_akshara.py USES it via triggers.py. They are COMPLEMENTARY, not duplicate!

| # | Task | Status |
|---|------|--------|
| 3.1 | ~~Remove manas/akshara.py~~ KEEP IT! (see OPUS-172) | ✅ N/A |
| 3.2 | triggers.py _load_synapses() → SynapseStore | ✅ DONE |
| 3.3 | viveka_action.py _load_synapses() → SynapseStore | ✅ DONE |
| 3.4 | synaptic_seeder.py _load_synapses() → SynapseStore | ✅ DONE |
| 3.5 | mirror.py _load_synapses() → SynapseStore | ✅ DONE |

**Verification**: `grep -r "json.loads.*synapses" manas/` returns NO MATCHES.
All 4 files now use `get_synapse_store(workspace).load()` with unified v3 schema.

### Phase 4: Wire Sanskrit Matrix to Main Loop

| # | Task | Status |
|---|------|--------|
| 4.1 | Prakriti → Sanskrit Matrix connection | TODO |
| 4.2 | Add compression call after synapse update | TODO |
| 4.3 | Wire Akasha into decision path | TODO |

### Phase 5: Decompose God Objects

| # | Task | Status |
|---|------|--------|
| 5.1 | Split intent_router.py (2376 lines) | TODO |
| 5.2 | Delegate from cognitive_kernel.py | TODO |

---

## VERIFICATION COMMANDS

```bash
# After Phase 1 complete:
python -c "from vibe_core.state.synapse_store import SynapseStore; print(SynapseStore.get_schema_version())"

# After Phase 2 complete:
python -c "from vibe_core.loaders import BridgeLoader; print(BridgeLoader.list_bridges())"

# After Phase 3 complete:
grep -r "_load_synapses" vibe_core/plugins/opus_assistant/manas/  # Should be EMPTY

# After Phase 4 complete:
python -c "from vibe_core.state import Prakriti; p = Prakriti(); print(p.snapshot())"
```

---

## PRINCIPLES (German Engineering)

1. **ONE source of truth** - No duplicates
2. **Loaders for everything** - VEDA-4 pattern
3. **As above, so below** - Kernel patterns apply to MANAS
4. **Unified schemas** - v3 for all state
5. **Do it ONCE but RIGHT** - No more band-aid fixes

---

**आत्मनो मोक्षार्थं जगद्धिताय च**
*"For one's own liberation and for the welfare of the world"*
