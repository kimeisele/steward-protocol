# OPUS-150: Unified Interface Audit

## Status: P1 - ARCHITECTURE CLARIFICATION NEEDED

**Created:** 2025-12-20
**Revised:** 2025-12-20 (Holographic paradigm correction)
**Author:** Opus + Human collaborative audit

---

## Executive Summary

### ⚠️ REVISION: Initial Analysis Was Partially Wrong

Initial analysis framed opus_assistant as a "monster that absorbed everything."
This was **INCORRECT**. opus_assistant is a **HOLON** - a self-contained, self-similar,
composable unit with its own internal Prakriti, by design.

The REAL issues are:
1. **Rendering patterns need unification** (3 patterns → should be 1)
2. **Naming confusion** (.opus_state used for both federal and local state)
3. **Some direct writes bypass StateService** (unified_cli.py)
4. **Interface layer "Skin" concept not yet implemented**

---

## The Holographic Paradigm (CORRECT Understanding)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VIBE_OS (Mother State)                      │
│                                                                     │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │ ROOT .opus_state/  (FEDERAL - Brain/Shared State)             │ │
│   │ ├── manas_intents, synapses, viveka_decisions                 │ │
│   │ ├── mantras, sankalpa (Strategic Will)                        │ │
│   │ └── prana_heartbeat, cycle_history                            │ │
│   │                                                               │ │
│   │ WHY FEDERAL? MANAS decisions affect the ENTIRE system.        │ │
│   │ Like: Brain is in your head, but controls whole body.         │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                              ↕ StateService API                     │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │ opus_assistant/ (HOLON - Like a Bundesland)                   │ │
│   │   ├── StateManager (plugin-local)                             │ │
│   │   │   └── .opus_state/ (LOCAL - plugin-specific)              │ │
│   │   │       ├── session.json      (current session)             │ │
│   │   │       ├── syscalls.jsonl    (experience replay 247KB)     │ │
│   │   │       └── observations.jsonl                              │ │
│   │   │                                                           │ │
│   │   └── manas/ (35k LOC - The Brain)                            │ │
│   │       ├── CODE lives here (plugin provides capability)        │ │
│   │       └── STATE is FEDERAL (decisions affect everything)      │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│   This is FRACTAL DESIGN, not spaghetti!                           │
│   "Each plugin owns its state, like Länder have their own budgets" │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Numbers (Context, Not Criticism)

| Component | LOC | Files | Role |
|-----------|-----|-------|------|
| **opus_assistant** | 52,219 | 108 | 🧠 HOLON (Brain) |
| → manas/ alone | 35,897 | 60+ | Cognitive Kernel |
| state/ (Prakriti) | 7,737 | 18 | Federal State |
| interface/ | 6,116 | 25 | Rendering Layer |

opus_assistant is large because it IS the cognitive system.
This is **appropriate** - the brain should be substantial.

---

## Problem 1: Three Rendering Patterns

### Pattern A: generate_content() with hardcoded strings
- Used by: CognitionRenderer, AgentsRenderer, EnvoyRenderer, 10+ others
- Location: `vibe_core/plugins/interface/renderers/*.py`
- Each renderer builds markdown with `lines.append()`

### Pattern B: Jinja2 Templates
- Used by: ONLY OpusDashboardRenderer
- Location: `vibe_core/plugins/opus_assistant/render/` + `templates/`
- Separate from all other renderers

### Pattern C: Config-driven render_sections()
- Defined in: BaseRenderer
- Actually used by: Almost nobody (only _template, architecture)
- interface.yaml has sections: configs that are IGNORED

### The Spaghetti
```
BaseRenderer.render_sections()    ← Defined but unused
       │
       │ Interface Plugin has config/interface.yaml with sections
       │ BUT renderers ignore it!
       │
       └──→ Everyone just does generate_content() with hardcoded strings

OpusDashboardRenderer             ← Completely separate Jinja2 system
       │
       └──→ Lives in opus_assistant, not interface plugin
```

---

## Problem 2: State Naming Confusion (Not Architecture Flaw)

### ✅ CORRECT: Fractal State Architecture

The system has TWO .opus_state directories BY DESIGN:

| Location | Scope | Purpose |
|----------|-------|---------|
| ROOT `.opus_state/` | FEDERAL | MANAS brain state (affects whole system) |
| PLUGIN `.opus_state/` | LOCAL | Plugin-specific state (session, syscalls) |

This is **fractal/holographic** - each holon has its own Prakriti.
Like: Federal government AND state governments both have budgets.

### ⚠️ ISSUE: Naming Confusion

Both directories are named `.opus_state/` which is confusing.
Consider renaming:
- ROOT: `.federal_state/` or `.brain_state/`
- PLUGIN: Keep `.opus_state/` (belongs to opus_assistant)

### ⚠️ ISSUE: Some Direct Writes Bypass StateService

These files write to ROOT `.opus_state/` without using StateService:
```
unified_cli.py     → Path(".opus_state/manas_intents.json")  ← CLI tool
prana.py           → Path(".opus_state/prana_heartbeat")     ← Heartbeat
```

**Question:** Is this intentional (CLI tools are special) or a violation?

### ✅ CORRECT: MANAS Uses StateService

```python
# In opus_assistant/manas/cognitive_kernel.py
state.save("synapses.json", synapses)  # Goes through StateService

# In opus_assistant/manas/cortex/viveka_action.py
state.save("viveka_decisions.json", entries)  # Goes through StateService
```

MANAS properly uses StateService for federal state.

---

## ~~Problem 3: opus_assistant is Not a Plugin~~ (REVISED)

### ✅ CORRECT: opus_assistant IS a Valid Holon

A **holon** is:
- Self-contained AND part of a larger whole
- Has its own internal structure AND connects to parent
- Can be complex internally

opus_assistant is imported by other parts because:
- It PROVIDES cognitive capabilities to the system
- This is like how your brain is "imported" by your body
- The brain is complex, but that's appropriate

**This is NOT a problem - it's the correct holographic architecture.**

---

## ~~Problem 4: MANAS Dislocation~~ (REVISED)

### ✅ CORRECT: MANAS Lives Where It Belongs

MANAS is inside opus_assistant because:
- opus_assistant is the "cognitive holon"
- MANAS is the brain of that holon
- Its STATE is federal (affects whole system)
- Its CODE is in the holon that manages it

This is like:
- The brain is INSIDE your head
- But brain DECISIONS affect your whole body
- The brain doesn't need to be extracted to your chest

**The code location is correct. The state routing is correct.**

---

## The Vision: Holographic Skin

What we WANT (from user vision):

```
┌───────────────────────────────────────────────────────────┐
│                   MARKDOWN LAYER                          │
│              "Holographic Skin"                           │
│                                                           │
│   - Bidirectional (read AND write)                        │
│   - Like Linux: files ARE the OS                          │
│   - Input interface AND output log AND state              │
│   - Unified rendering (one pattern)                       │
│   - Part of Prakriti? Or separate layer?                  │
│                                                           │
│   Human ←→ Markdown Files ←→ System State                 │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## Proposed Solution: Focused Improvements

### ~~Phase 1: Unify State~~ (NOT NEEDED)
The state architecture is CORRECT. Fractal design is intentional.

### ~~Phase 2: Extract MANAS~~ (NOT NEEDED)
MANAS belongs in opus_assistant. Code location is correct.

### Phase 1: Unify Rendering Patterns (REAL ISSUE)
1. Pick ONE pattern (recommend: config-driven with data sources)
2. Migrate all renderers to use same pattern
3. OpusDashboardRenderer can keep Jinja2 internally, but expose same API

### Phase 2: Clarify State Naming
1. Rename ROOT `.opus_state/` to `.brain_state/` or `.federal_state/`
2. Keep PLUGIN `.opus_state/` as-is
3. Document the fractal pattern clearly

### Phase 3: Create Skin Layer (NEW)
1. New concept: vibe_core/skin/ - the "holographic interface"
2. Manages ALL markdown files (OPUS.md, COGNITION.md, etc.)
3. Bidirectional: renders from state, parses input back to state
4. This is the "holographic skin" vision from user

### Phase 4: Fix Direct Writes
1. Audit unified_cli.py direct writes - intentional or violation?
2. If violation, route through StateService
3. If intentional (CLI tools), document why

---

## Architecture Question

**Should the Skin be part of Prakriti or separate?**

Arguments for PART OF Prakriti:
- Markdown files ARE state (bidirectional)
- Git tracking already in Prakriti
- Unified state management

Arguments for SEPARATE layer:
- Clear separation of concerns
- Skin is the boundary, Prakriti is internal
- Different update frequencies

**Proposed answer:** Skin USES Prakriti but is a separate layer
- Like human skin uses the body but is its own organ
- Prakriti = internal state
- Skin = interface to world

---

## Comprehensive Implementation Plan

### Related OPUS Documents (MUST READ)

| Doc | Title | Status | Relevance |
|-----|-------|--------|-----------|
| OPUS-014 | Unified UI Transparency | DRAFT | THE SKIN VISION |
| OPUS-023 | Fractal UI Architecture | IMPLEMENTED | Container/Panel structure |
| OPUS-029 | Plugin Architecture | IMPLEMENTED | Frontend/Backend split |
| OPUS-096 | State Sync Weaver | IMPLEMENTED | Unified state orchestration |
| OPUS-117 | Fractal Integration | IMPLEMENTED | Holographic patterns |

### Phase 1: Unify Rendering Patterns [P1]

**Problem:** 3 patterns exist, should be 1
**Solution:** Standardize on config-driven with data sources

1. [ ] Update `BaseRenderer.render_sections()` to be the standard
2. [ ] Migrate `CognitionRenderer` to use sections config
3. [ ] Migrate `AgentsRenderer` to use sections config
4. [ ] Migrate all other `generate_content()` renderers
5. [ ] OpusDashboardRenderer: Keep Jinja2 internally, expose same API

**Test:** `test_single_rendering_pattern` should PASS when done

### Phase 2: Complete OPUS-014 Vision [P1]

**Problem:** STATE.md, ECONOMY.md, MATRIX.md not implemented
**Solution:** Implement as described in OPUS-014

1. [ ] Create `renderers/state.py` - Prakriti inspector
2. [ ] Create `renderers/economy.py` - Resource meters
3. [ ] Create `renderers/matrix.py` - Routing visualization
4. [ ] Update `config/interface.yaml` with new renderers
5. [ ] Implement SETTINGS.md command parser (bidirectional!)

### Phase 3: Fix Config Section Ignoring [P1]

**Problem:** interface.yaml sections defined but ignored
**Solution:** Make renderers actually USE their section configs

1. [ ] Audit each renderer: does it read its sections?
2. [ ] Update renderers to use `self.get_config().sections`
3. [ ] Remove hardcoded section generation

**Test:** `test_section_configs_are_used` should PASS when done

### Phase 4: Clarify State Naming [P2]

**Problem:** Both called `.opus_state/`
**Solution:** Rename for clarity

1. [ ] Rename ROOT `.opus_state/` → `.manas_state/` or `.brain_state/`
2. [ ] Update all references in code
3. [ ] Document the fractal pattern

### Phase 5: Fix StateService Violations [P2]

**Problem:** Some files write directly without StateService
**Solution:** Route through StateService or document exceptions

1. [ ] Audit `unified_cli.py` direct writes
2. [ ] Audit `prana.py` direct writes
3. [ ] Route through StateService OR document as intentional

**Test:** `test_no_direct_opus_state_writes` should PASS when done

### Phase 6: Create Skin Layer Specification [P3]

**Problem:** No formal specification for "holographic skin"
**Solution:** Write OPUS-151 Skin Layer Specification

1. [ ] Define what "Skin" means (boundary between human and system)
2. [ ] Specify bidirectional parsing (input AND output)
3. [ ] Specify how Skin connects to Prakriti
4. [ ] Specify how plugins register their UI

---

## Success Criteria

When ALL phases complete:
- [ ] All 6 tests should PASS (currently 3 PASS, 3 XFAIL)
- [ ] Single rendering pattern across all renderers
- [ ] STATE.md, ECONOMY.md, MATRIX.md exist and work
- [ ] Config sections actually used by renderers
- [ ] State naming is clear (federal vs local)
- [ ] All state writes documented

---

## Files to Examine

Core files for this refactor:
- `vibe_core/plugins/interface/renderers/base.py` - BaseRenderer
- `vibe_core/state/state_service.py` - StateService
- `vibe_core/plugins/opus_assistant/render/opus_dashboard_renderer.py` - Jinja2 pattern
- `vibe_core/plugins/opus_assistant/manas/` - The brain
- `config/interface.yaml` - Section configs
- `docs/architecture/OPUS/014-UNIFIED-UI-TRANSPARENCY.md` - THE VISION

---

*"The interface is not decoration. It IS the system."*
*"Markdown files are the nervous system's skin - bidirectional, alive, responsive."*
