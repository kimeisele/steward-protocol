# OPUS-031: OPUS Multiverse Architecture

> **Status**: PLANNING
> **Author**: HIL_ASSISTANT (Gemini) + Claude (Senior Architect)
> **Date**: 2025-12-13
> **Depends On**: OPUS-029 (Plugin Architecture), OPUS-030 (Clean Separation)
> **Scope**: Evolve OPUS from dashboard to Organizational Membrane

<!-- @HARNESS
files:
  # Core Backend (opus_assistant)
  - path: vibe_core/plugins/opus_assistant/render/opus_dashboard_renderer.py
    required: true
    patterns:
      - "def render\\("
      - "def _gather_"

  # Frontend (InterfacePlugin)
  - path: vibe_core/plugins/interface/renderers/opus/renderer.py
    required: true
    patterns:
      - "class OpusRenderer"
      - "generate_content"

  # StateManager (Fractal Holon)
  - path: vibe_core/plugins/opus_assistant/core/state_manager.py
    required: true
    patterns:
      - "class StateManager"
      - "append_observation"

  # Syscall Infrastructure (Layer 2 prerequisite)
  - path: vibe_core/cartridges/system/envoy/blueprint_generator.py
    required: true
    patterns:
      - "SYSCALL_INTENT_PATTERNS"
      - "class BlueprintGenerator"

  # Semantic Executor (Layer 2 prerequisite)
  - path: vibe_core/semantic_syscalls.py
    required: true
    patterns:
      - "class SemanticSyscallExecutor"
      - "_handle_spawn_cognition"

absent:
  # No legacy writers
  - path: vibe_core/plugins/opus_assistant/render/opus_md_writer.py
    reason: "Deleted - no legacy split-brain"
-->

---

## Executive Summary

OPUS is not a dashboard. It's the **embryo of an Organizational Membrane** that:
- Observes itself (Verification)
- Judges itself (Karma)
- Heals itself (AUTO_HEAL circuit)
- Reproduces itself (SPAWN_COGNITION)
- Evolves itself (Circuit composition)

This document defines the evolution from **Layer 1** (current) to **Layer 5** (multiverse).

---

## Current State (Layer 1: Living Dashboard) ✅

| Component | Status | Location |
|-----------|--------|----------|
| Jinja2 Templates | ✅ | `opus_assistant/templates/` |
| Control Plane | ✅ | `view_preferences` in StateManager |
| Karma System | ✅ | `karma_history.jsonl` |
| Dependency Graph | ✅ | `_gather_dependency_graph()` |
| Backend/Frontend Split | ✅ | OPUS-030 completed |

**Architecture (CLEAN):**
```
opus_assistant (BACKEND) → render() → STRING
        ↓
InterfacePlugin (FRONTEND) → kernel.io.write_document()
        ↓
OPUS.md (PROJECTION)
```

---

## Layer 2: Syscall Console (P1)

### Goal
Expose existing syscall infrastructure in OPUS.md as a command interface.

### Prerequisites (Already Exist!)
- `BlueprintGenerator.compile()` - NL → Syscall detection
- `SemanticSyscallExecutor` - Syscall execution
- `DeterministicExecutor` - Playbook execution

### Implementation

**Phase 2.1: Add Syscall Panel to Template**

File: `opus_assistant/templates/panels/syscall_console.md.j2`
```jinja2
## ⚡ Syscall Console

{% if last_syscall %}
| Intent | Result |
|--------|--------|
| `{{ last_syscall.intent }}` | {{ last_syscall.status }} |
{% endif %}

**Available:**
- `spawn <role> agent` → SPAWN_COGNITION
- `dispatch <task> to <agent>` → DISPATCH_TASK

CLI: `python -m vibe_core.cli envoy "<intent>"`
```

**Phase 2.2: Add Gatherer**

File: `opus_dashboard_renderer.py`
```python
def _gather_syscall_history(self) -> Dict[str, Any]:
    """Gather recent syscall executions from StateManager."""
    # Read from .opus_state/syscall_history.jsonl
    pass
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Panel renders in OPUS.md | Visual check |
| Last syscall shown | Execute syscall, verify display |
| CLI link works | Click/copy, execute |

---

## Layer 3: 4D Hypercube State (P2)

### Goal
Visualize the four dimensions of system state:
1. **Time** - Session duration, commit history
2. **Karma** - Trust score, trend, history
3. **City** - Active agents, zones
4. **Circuits** - Waiting, fired, next

### Implementation

**Phase 3.1: Hypercube Panel**

File: `opus_assistant/templates/panels/hypercube.md.j2`
```jinja2
## 🔮 4D Hypercube

| Axis | State |
|------|-------|
| ⏱️ Time | Session: {{ session.duration }} \| Commits: {{ git.commit_count }} |
| 🧬 Karma | {{ karma.current_score }}% ({{ karma.boot_mode }}) {{ karma.trend }} |
| 🏙️ City | {{ city.agent_count }} agents \| Zones: {{ city.zones|join(', ') }} |
| 🔮 Circuits | Waiting: {{ circuits.waiting }} \| Fired: {{ circuits.fired_count }} |
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| All 4 axes render | Visual check |
| Data is live | Change state, verify update |
| Karma trend correct | Check history |

---

## Layer 4: Autonomous Conductor (P3)

### Goal
OPUS runs as GitHub Action, autonomously monitoring and improving.

### Implementation

**Phase 4.1: Conductor Module**

File: `opus_assistant/conductor.py`
```python
"""
OPUS Conductor - Autonomous execution for GitHub Actions.

Usage:
  python -m vibe_core.plugins.opus_assistant.conductor \
    --circuits=OPUS_AUTO_VERIFY,KARMA_CONSEQUENCE \
    --output=OPUS.md
"""
```

**Phase 4.2: GitHub Action Workflow**

File: `.github/workflows/opus_conductor.yml`
```yaml
name: OPUS Conductor
on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8am
  push:
    branches: [main]

jobs:
  conduct:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: OPUS Think Cycle
        run: python -m vibe_core.plugins.opus_assistant.conductor
      - name: Commit Insights
        run: |
          git add OPUS.md
          git diff --cached --quiet || git commit -m "🔮 OPUS: Autonomous insight"
          git push
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Action runs on schedule | Check GitHub Actions |
| OPUS.md updated | Check commit history |
| Insights are meaningful | Human review |

---

## Layer 5: Multiverse (P4 - Far Future)

### Goal
Per-branch OPUS instances with karma merging on PR merge.

### Concept
```
OPUS PRIME (main)
    ├── CHILD OPUS (feature-a) → tracks karma for branch
    ├── CHILD OPUS (feature-b) → tracks karma for branch
    └── On merge: karma flows up (weighted by commits)
```

### Open Questions

1. **Scope**: Per-branch or per-feature-flag?
2. **Karma Merge**: Average? Minimum? Weighted by commits?
3. **State Location**: `.opus_state/` per branch?

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Child OPUS tracks branch | Check `.opus_state/` on branch |
| Karma merges on PR | Check parent karma after merge |
| No split-brain | Verify single source of truth |

---

## Architectural Principles

### 1. Backend/Frontend Separation (OPUS-030)
- `opus_assistant` = BACKEND (data only)
- `InterfacePlugin` = FRONTEND (writes via kernel.io)
- **No exceptions.**

### 2. State Inside State (Fractal Holon)
- Plugin owns `.opus_state/`
- Survives git resets
- Git-tracked for persistence

### 3. No Legacy Rotz
- `opus_md_writer.py` deleted
- No fallback to old patterns
- Single path for all operations

### 4. Circuits Are YAML
- New behavior = new `.yaml` file
- No code changes for simple workflows
- Composable and testable

---

## Priority Matrix

| Layer | Priority | Effort | Impact | Status |
|-------|----------|--------|--------|--------|
| 1. Living Dashboard | - | - | - | ✅ DONE |
| 2. Syscall Console | P1 | Low | High | 📋 PLANNED |
| 3. 4D Hypercube | P2 | Medium | Medium | 📋 PLANNED |
| 4. Autonomous Conductor | P3 | Medium | High | 📋 PLANNED |
| 5. Multiverse | P4 | High | Very High | 💭 VISION |

---

## Next Actions

1. [ ] Implement Layer 2: Syscall Console panel
2. [ ] Test with `python -m vibe_core.cli envoy "spawn test agent"`
3. [ ] Iterate on Layer 3 design
4. [ ] Create conductor.py skeleton for Layer 4

---

*This document is a living plan. The architecture speaks - we listen.*
