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

  # StateManager (Fractal Holon) - NOTE: Class is OpusStateManager!
  - path: vibe_core/plugins/opus_assistant/core/state_manager.py
    required: true
    patterns:
      - "class OpusStateManager"
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
| Control Plane | ✅ | `view_preferences` in OpusStateManager |
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

### What EXISTS (Verified)
| Component | Location | Status |
|-----------|----------|--------|
| `BlueprintGenerator.compile()` | `envoy/blueprint_generator.py:169` | ✅ Works |
| `SemanticSyscallExecutor` | `semantic_syscalls.py` | ✅ Works |
| `SYSCALL_INTENT_PATTERNS` | `blueprint_generator.py` | ✅ Regex patterns |

### What DOESN'T Exist (Must Build)

> ⚠️ **HONEST ASSESSMENT**: Layer 2 requires NEW infrastructure

| Component | Status | Action Required |
|-----------|--------|-----------------|
| `syscall_history.jsonl` | ❌ NOT EXISTS | Create storage format |
| `SyscallEntry` dataclass | ❌ NOT EXISTS | Add to state_manager.py |
| `record_syscall()` method | ❌ NOT EXISTS | Add to OpusStateManager |
| Syscall Console panel | ❌ NOT EXISTS | Create template |

### Implementation (Honest)

**Phase 2.1: Add Syscall Storage to StateManager**

File: `opus_assistant/core/state_manager.py`
```python
@dataclass
class SyscallEntry:
    """A single syscall execution record."""
    timestamp: str
    intent: str
    syscall_type: str
    result: str  # "success" | "failed" | "no_match"
    confidence: float

# Add to OpusStateManager:
SYSCALL_HISTORY_FILE = "syscall_history.jsonl"

def record_syscall(self, entry: SyscallEntry) -> bool:
    """Record a syscall execution to history."""
    # Similar pattern to append_observation()
```

**Phase 2.2: Add Syscall Panel to Template**

File: `opus_assistant/templates/panels/syscall_console.md.j2`
```jinja2
## ⚡ Syscall Console

{% if syscall_history %}
| Time | Intent | Result |
|------|--------|--------|
{% for s in syscall_history[:5] %}
| {{ s.timestamp }} | `{{ s.intent[:40] }}` | {{ s.result }} |
{% endfor %}
{% else %}
_No syscalls recorded yet_
{% endif %}

**CLI:** `python -m vibe_core.cli envoy "<intent>"`

**Limitations:**
- Uses regex patterns, not LLM
- Unmatched intents → confidence=0.5 playbook mode
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| `SyscallEntry` dataclass exists | `grep "class SyscallEntry" state_manager.py` |
| `syscall_history.jsonl` created on first syscall | Check `.opus_state/` |
| Panel renders in OPUS.md | Visual check |

---

## Layer 3: 4D Hypercube State (P2)

### Goal
Visualize the four dimensions of system state.

### What EXISTS (Verified)
| Axis | Data Source | Status |
|------|-------------|--------|
| ⏱️ Time | `session.json` | ✅ Has `started_at` |
| 🧬 Karma | `karma_history.jsonl` | ✅ Has scores |
| 🏙️ City | `kernel.city` | ⚠️ Requires kernel access |
| 🔮 Circuits | `_gather_circuits()` | ✅ Already gathered |

### What DOESN'T Exist (Must Build)
| Component | Status | Action Required |
|-----------|--------|-----------------|
| Hypercube panel | ❌ NOT EXISTS | Create template |
| City data gatherer | ⚠️ PARTIAL | Need `_gather_city()` method |
| Trend calculation | ❌ NOT EXISTS | Add to karma gatherer |

### Implementation

**Phase 3.1: Add `_gather_city()` to Renderer**

```python
def _gather_city(self) -> Dict[str, Any]:
    """Gather city/agent data from kernel."""
    if not self._kernel:
        return {"agent_count": 0, "zones": []}

    city = getattr(self._kernel, "city", None)
    if not city:
        return {"agent_count": 0, "zones": []}

    # Extract agent info from city
    # ...
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| All 4 axes render | Visual check |
| Karma trend shows direction | Check ↗/↘/→ indicator |
| City shows agent count | Compare with kernel state |

---

## Layer 4: Autonomous Conductor (P3)

> ⚠️ **STATUS: REQUIRES DESIGN PHASE**
> This layer needs detailed specification before implementation.

### Goal
OPUS runs as GitHub Action, autonomously monitoring and improving.

### Prerequisites (NOT YET SPECIFIED)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Python version | ❓ | 3.11+ assumed |
| Dependencies | ❓ | `requirements.txt` needed |
| Headless kernel boot | ❓ | How to init without full boot? |
| Conductor CLI contract | ❓ | What args? What output format? |
| API keys handling | ❓ | Secrets injection |

### Proposed CLI Contract (DRAFT)

```bash
# Minimal conductor interface
python -m vibe_core.plugins.opus_assistant.conductor \
    --mode=autonomous \
    --circuits=OPUS_AUTO_VERIFY \
    --output=OPUS.md \
    --dry-run  # Don't write, just print

# Exit codes:
# 0 = success, OPUS.md updated
# 1 = error
# 2 = no changes needed
```

### GitHub Action (DRAFT)

```yaml
name: OPUS Conductor
on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8am UTC
  push:
    branches: [main]

jobs:
  conduct:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          # Or: pip install -e .

      - name: OPUS Think Cycle
        env:
          # Optional: For future LLM enhancement
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python -m vibe_core.plugins.opus_assistant.conductor \
            --mode=autonomous \
            --output=OPUS.md

      - name: Commit Insights
        run: |
          git config user.name "OPUS Conductor"
          git config user.email "opus@steward.ai"
          git add OPUS.md .opus_state/
          git diff --cached --quiet || git commit -m "🔮 OPUS: Autonomous insight"
          git push
```

### Open Design Questions

1. **Headless Boot**: Can kernel boot without full runtime? What's minimal init?
2. **Circuit Selection**: Which circuits are safe for autonomous execution?
3. **Error Handling**: What if conductor fails mid-execution?
4. **Rate Limiting**: How often is too often?

---

## Layer 5: Multiverse (P4)

> 🔴 **STATUS: REQUIRES DESIGN PHASE**
> This is vision/inspiration only. No technical spec exists.

### Concept (Aspirational)

```
OPUS PRIME (main)
    ├── CHILD OPUS (feature-a) → tracks karma for branch
    ├── CHILD OPUS (feature-b) → tracks karma for branch
    └── On merge: karma flows up (weighted by commits)
```

### Open Design Questions (Unanswered)

| Question | Options | Decision |
|----------|---------|----------|
| Scope | Per-branch vs per-feature-flag | ❓ TBD |
| State location | `.opus_state/` per branch? | ❓ TBD |
| Karma merge rule | Average? Min? Weighted? | ❓ TBD |
| Conflict resolution | Parent wins? Child wins? | ❓ TBD |
| Git workflow | Merge commit? Squash? | ❓ TBD |

### Required Before Implementation

- [ ] RFC document for multiverse architecture
- [ ] Proof-of-concept on single branch
- [ ] Karma merge algorithm specification
- [ ] Git hook integration design

---

## Architectural Principles

### 1. Backend/Frontend Separation (OPUS-030) ✅
- `opus_assistant` = BACKEND (data only)
- `InterfacePlugin` = FRONTEND (writes via kernel.io)
- **No exceptions.**

### 2. State Inside State (Fractal Holon) ✅
- Plugin owns `.opus_state/`
- Survives git resets
- Git-tracked for persistence

### 3. No Legacy Rotz ✅
- `opus_md_writer.py` deleted
- No fallback to old patterns
- Single path for all operations

### 4. Circuits Are YAML (With Constraints)
- New behavior = new `.yaml` file
- **BUT**: Circuits need registered `action_type` handlers
- Non-existent `action_type` will silently fail
- Document all available `action_type` values

### 5. BlueprintGenerator Limitations
- Uses **regex patterns**, not LLM
- Unmatched input → `confidence=0.5` playbook mode
- Not magic NL understanding

---

## Priority Matrix

| Layer | Priority | Effort | Impact | Status |
|-------|----------|--------|--------|--------|
| 1. Living Dashboard | - | - | - | ✅ DONE |
| 2. Syscall Console | P1 | Medium | High | 📋 NEEDS INFRA |
| 3. 4D Hypercube | P2 | Medium | Medium | 📋 PLANNED |
| 4. Autonomous Conductor | P3 | High | High | 🔴 NEEDS DESIGN |
| 5. Multiverse | P4 | Very High | Very High | 🔴 NEEDS DESIGN |

---

## Next Actions

1. [ ] **Layer 2**: Add `SyscallEntry` + `record_syscall()` to OpusStateManager
2. [ ] **Layer 2**: Create `syscall_console.md.j2` panel
3. [ ] **Layer 3**: Add `_gather_city()` to renderer
4. [ ] **Layer 4**: Write RFC for conductor design
5. [ ] **Layer 5**: Write RFC for multiverse architecture

---

*This document is honest about what exists vs what's aspirational. No spaghetti.*
