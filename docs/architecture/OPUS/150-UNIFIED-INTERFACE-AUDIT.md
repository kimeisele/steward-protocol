# OPUS-150: Unified Interface Audit

## Status: P0 - CRITICAL ARCHITECTURE DEBT

**Created:** 2025-12-20
**Author:** Opus + Human collaborative audit

---

## Executive Summary

This audit reveals **severe architectural fragmentation** in the rendering and state systems.
What should be a unified "holographic skin" layer is instead scattered across:

- 3 different rendering patterns
- 2 separate state storage systems
- 1 monster plugin (opus_assistant) that absorbed everything

---

## The Numbers

| Component | LOC | Files | Status |
|-----------|-----|-------|--------|
| **opus_assistant** | 52,219 | 108 | 🔴 MONSTER |
| → manas/ alone | 35,897 | 60+ | 🔴 5x bigger than state/ |
| state/ (Prakriti) | 7,737 | 18 | 🟡 Should be bigger |
| interface/ | 6,116 | 25 | 🟡 Thin shell |

**opus_assistant is 4x BIGGER than state + interface combined!**

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

## Problem 2: Two State Systems

### System A: vibe_core/state/ (Prakriti)
- prakriti.py, git_state.py, ledger_state.py, etc.
- StateService claims to be "ONLY authorized interface"
- Contains: samskara.py, sanskrit_matrix.py (new compression system)

### System B: .opus_state/ (opus_assistant's shadow state)
- 14+ JSON files stored flat
- Written to DIRECTLY by multiple files (violating StateService)
- Contains: manas_intents, synapses, viveka_decisions, mantras, etc.

### Direct .opus_state/ violations found:
```
unified_cli.py     → Path(".opus_state/manas_intents.json")
unified_cli.py     → Path(".opus_state/manas_memory.json")
unified_cli.py     → Path(".opus_state/synapses.json")
treasury.py        → Path(".opus_state/...")
prana.py           → Path(".opus_state/prana_heartbeat")
sync_holon.py      → Path(".opus_state/")
```

---

## Problem 3: opus_assistant is Not a Plugin

A plugin should be:
- Optional, removable
- Self-contained
- Not a dependency for core functionality

But opus_assistant is imported by:
- interface/renderers/opus/ (rendering)
- envoy/ plugin
- task_manager/ plugin
- unified_cli.py (CLI)
- vajra/ (testing)
- steward/ (rituals)
- cartridges/manas/

**It's the de-facto brain of the system, hiding as a "plugin".**

---

## Problem 4: MANAS Dislocation

manas/ should be:
- A top-level cognitive module
- Integrated with StateService
- Using unified rendering

Instead:
- Buried inside opus_assistant/manas/ (35k LOC)
- Has its own state in .opus_state/
- Has its own rendering in templates/

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

## Proposed Solution: Radical Restructure

### Phase 1: Unify State
1. Move all .opus_state/ into StateService management
2. Single state directory with clear ownership
3. No more direct Path() writes

### Phase 2: Extract MANAS
1. Move opus_assistant/manas/ to vibe_core/manas/
2. Make it a first-class citizen, not a plugin sub-module
3. Integrate with StateService

### Phase 3: Unify Rendering
1. Pick ONE pattern (recommend: config-driven with data sources)
2. Kill the Jinja2 special case for OPUS.md
3. All renderers use same base architecture

### Phase 4: Create Skin Layer
1. New module: vibe_core/skin/ or vibe_core/interface/
2. Manages ALL markdown files
3. Bidirectional: renders from state, parses back to state
4. Single source of truth for UI

### Phase 5: Downsize opus_assistant
1. What remains: circuits, vidya, narasimha (specialized features)
2. Everything else extracted
3. Becomes a true optional plugin

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

## Next Steps

1. [ ] Write tests that expose the fragmentation
2. [ ] Create migration plan for .opus_state/ → StateService
3. [ ] Extract manas/ to top-level
4. [ ] Implement unified renderer pattern
5. [ ] Create Skin layer specification

---

## Files to Examine

Core files for this refactor:
- `vibe_core/plugins/interface/renderers/base.py` - BaseRenderer
- `vibe_core/state/state_service.py` - StateService
- `vibe_core/plugins/opus_assistant/render/opus_dashboard_renderer.py` - Jinja2 pattern
- `vibe_core/plugins/opus_assistant/manas/` - The brain
- `config/interface.yaml` - Unused section configs

---

*"The interface is not decoration. It IS the system."*
