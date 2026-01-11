# PROTOCOL MIGRATION MAP

## THE LOTUS + CHANDELIER PATTERN

```
                    ┌─────────────────┐
                    │  Level -2       │ ← KRISHNA/MAHAMANTRA (Source)
                    │  SUBSTRATE      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ HARE     │  │ KRISHNA  │  │ RAMA     │ ← 3 Branches (Essence)
        │ Energy   │  │ Source   │  │ Strength │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
        ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
        │ 4 Phases│   │ 4 Phases│   │ 4 Phases│ ← Structure
        │ W-P-S-S │   │ W-P-S-S │   │ W-P-S-S │
        └─────────┘   └─────────┘   └─────────┘
                             │
                    ┌────────┴────────┐
                    │  Level +N       │
                    │  APPLICATION    │ ← User Layer (CLIs)
                    └─────────────────┘

LOTUS: Unfolds 1 → N (from source outward)
CHANDELIER: Everything traces N → 1 (back to source)
```

## CURRENT PROTOCOL COVERAGE

### protocols/ Folder Structure
```
protocols/
├── ROOT (59 files)      ← Mixed: some canonical, some legacy
├── avataras/ (5)        ← 4 HEADs + vyuha
├── governance/ (4)      ← This folder!
├── lila/ (1)            ← Divine play
├── mahajanas/ (20)      ← 12 Mahajanas × ~1.7 files
├── naga/ (27)           ← Security federation
├── science/ (2)         ← Research
├── substrate/ (21)      ← Deepest layer (mantra, resonance)
└── universal/ (32)      ← Transcendental (Krishna, Gita, router)
                         ─────
                         ~170 files in protocols/
```

### Wild Systems (50+) NOT in protocols/

| Directory | Files | Purpose | Suggested Mahajana |
|-----------|-------|---------|-------------------|
| **runtime/** | ~25 | Execution layer | JANAKA (Duty) |
| **cortex/** | ~15 | Cognitive engines | SHUKA (Vision) |
| **naga/** (outside protocols) | 73 | Security impl | YAMARAJA |
| **plugins/** | 295 | Extensions | PRAHLADA |
| **cli/** | 64 | User interfaces | NARADA |
| **services/** | ~20 | Service layer | JANAKA |
| **state/** | 21 | State management | BHISHMA |
| **loaders/** | 16 | VEDA-4 loading | BRAHMA |
| **reactor/** | ~10 | Resonance computation | KAPILA |
| **knowledge/** | ~10 | Knowledge graph | KUMARAS |

## LAYER ARCHITECTURE

### Level -2 to -1: SUBSTRATE (Foundation)
Already in protocols:
- `substrate/byte.py` - DNA/bits
- `substrate/resonance.py` - Phonetic resonance
- `substrate/mantra/` - Mahamantra computation
- `substrate/tattva.py` - 24+12+1=37

### Level -1 to 0: UNIVERSAL (Transcendental)
Already in protocols:
- `universal/semantic_router.py` - Full routing stack
- `universal/intent_bridge.py` - Intent → OpCode
- `universal/krishna.py`, `rama.py` - Holy Names
- `universal/gita.py` - Gita principles

### Level 0: KERNEL (Foundation)
**WILD - Needs migration:**
- `di.py` (600 lines) - ServiceRegistry → **PRIORITY 1**
- `event_bus.py` (600 lines) - Event system → **PRIORITY 1**
- `orchestration_cycle.py` (700 lines) - Cycle foundation → **PRIORITY 1**
- `lineage.py` (600 lines) - Execution context → **PRIORITY 2**
- `semantic_syscalls.py` (800 lines) - Syscall abstraction → **PRIORITY 2**

### Level 1: RUNTIME (Execution)
**WILD - Needs migration:**
- `runtime/layered_router.py` (432 lines) - 4-layer routing → **PRIORITY 1**
- `runtime/unified_execution.py` - Lazy execution → **PRIORITY 1**
- `runtime/circuit_breaker.py` - Fault tolerance → **PRIORITY 2**
- `runtime/llm_engine.py` - LLM orchestration → **PRIORITY 2**

### Level 2: CORTEX (Cognition)
**WILD - Needs migration:**
- `cortex/engines/semantic_engine.py` - Vector routing → **PRIORITY 2**
- `cortex/engines/circuit_engine.py` - Circuit execution → **PRIORITY 2**

### Level 3: SERVICES (Application)
**WILD - Needs migration:**
- `prana_orchestrator.py` - Plugin lifecycle → **PRIORITY 3**
- `task_kernel.py` - Task execution → **PRIORITY 3**
- `knowledge/graph.py` - Knowledge graph → **PRIORITY 3**

## MIGRATION PRIORITY

### Phase 1: KERNEL PROTOCOLS (Most critical)
These are the foundation everything else depends on:
1. `di.py` → `protocols/kernel/di.py`
2. `event_bus.py` → `protocols/kernel/events.py`
3. `orchestration_cycle.py` → `protocols/kernel/cycle.py`
4. `runtime/layered_router.py` → Already has protocol? Check

### Phase 2: RUNTIME PROTOCOLS
1. `unified_execution.py` → `protocols/runtime/execution.py`
2. `circuit_breaker.py` → `protocols/runtime/circuit.py`
3. `llm_engine.py` → `protocols/runtime/llm.py`

### Phase 3: COGNITIVE PROTOCOLS
1. `semantic_engine.py` → `protocols/cortex/semantic.py`
2. `circuit_engine.py` → `protocols/cortex/circuit.py`

### Phase 4: SERVICE PROTOCOLS
1. `knowledge/graph.py` → `protocols/knowledge/graph.py`
2. `prana_orchestrator.py` → `protocols/services/prana.py`

## SEMANTIC MISMATCHES TO FIX

| Current Name | Issue | Suggested Fix |
|--------------|-------|---------------|
| `reactor/quantum.py` | Duplicate of resonance? | Merge with `substrate/resonance.py` |
| `cortex/engines/semantic_engine.py` | Runtime, not protocol | Extract protocol |
| `runtime/layered_router.py` | Complex logic, not protocol | Extract protocol |

## FOLDER NAMING CONVENTION

### Existing (Keep)
- `substrate/` - Level -2 to -1 (deepest)
- `universal/` - Level -2 (transcendental)
- `mahajanas/` - The 12 guardians
- `naga/` - Security federation
- `avataras/` - The 4 HEADs

### Proposed (New)
- `kernel/` - Level 0 (DI, events, cycle)
- `runtime/` - Level 1 (execution, routing)
- `cortex/` - Level 2 (cognitive engines)
- `services/` - Level 3+ (application layer)

## NOTES

1. **NO QUARANTINE** - Don't create "legacy" or "deprecated" folders
2. **PROTOCOL FIRST** - Extract protocol interface, keep impl separate
3. **LAYER BY LAYER** - Migrate bottom-up (kernel first)
4. **TEST COVERAGE** - Each migrated protocol needs tests
5. **NO MANUAL LABOR** - Use decorators and registries
