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

### Implementation (Singularity-Ready)

> 🧠 **DESIGN DECISION 1**: SyscallEntry is NOT a log - it's an **Experience Replay Buffer**
>
> In a Neuro-Symbolic architecture, this is your training dataset.
> The system must know: "I tried X, and it caused Y."

**Phase 2.1: Add Experience Replay to StateManager**

File: `opus_assistant/core/state_manager.py`
```python
@dataclass
class SyscallEntry:
    """
    Experience Replay: Links neural intent to symbolic action and outcome.

    This enables future in-context learning without fine-tuning:
    Feed the last 50 successful entries as few-shot examples.
    """
    timestamp: str

    # 1. Neural Input (The trigger)
    intent_raw: str          # e.g. "Create a monitoring agent"

    # 2. Symbolic Action (The translation)
    syscall: str             # e.g. "SPAWN_COGNITION"
    params_hash: str         # Hash of params (for deduplication)

    # 3. Reality Feedback (The outcome)
    result: str              # "SUCCESS", "FAILURE", "REJECTED_BY_GATE"
    error: Optional[str]     # If failed, why?

    # 4. Learning Signal (For future in-context learning)
    karma_impact: int        # Did this action improve the system? (0 = neutral)

# Add to OpusStateManager:
SYSCALL_HISTORY_FILE = "syscall_history.jsonl"

def record_syscall(self, entry: SyscallEntry) -> bool:
    """Record a syscall execution to history (Experience Replay)."""
    # Similar pattern to append_observation()

def get_successful_syscalls(self, limit: int = 50) -> List[SyscallEntry]:
    """Get recent successful syscalls for few-shot learning."""
    all_entries = self.get_syscall_history()
    return [e for e in all_entries if e.result == "SUCCESS"][:limit]
```

**Why this matters:**
- When `BlueprintGenerator` needs to be smarter, feed it successful `SyscallEntry`s as few-shot examples
- **Self-learning without fine-tuning**
- The `karma_impact` field tracks whether actions helped or hurt

**Phase 2.2: Add Syscall Panel to Template**

File: `opus_assistant/templates/panels/syscall_console.md.j2`
```jinja2
## ⚡ Syscall Console

{% if syscall_history %}
| Time | Intent | Syscall | Result | Karma |
|------|--------|---------|--------|-------|
{% for s in syscall_history[:5] %}
| {{ s.timestamp }} | `{{ s.intent_raw[:30] }}` | {{ s.syscall }} | {{ s.result }} | {{ s.karma_impact }} |
{% endfor %}
{% else %}
_No syscalls recorded yet_
{% endif %}

**CLI:** `python -m vibe_core.cli envoy "<intent>"`

**Limitations:**
- Uses regex patterns, not LLM
- Unmatched intents → confidence=0.5 playbook mode
- Future: Feed successful syscalls as few-shot examples
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

> 🧠 **DESIGN DECISION 2**: The Conductor is NOT a script - it's a **Circuit**
>
> Don't build a specialized runner. Use the existing `CircuitEngine`.
> The system must control itself through standard tools.

### Goal
OPUS runs as GitHub Action using **existing infrastructure** (Circuits + CLI).

### Architecture Decision: No conductor.py!

**❌ WRONG (Spaghetti):**
```bash
python -m vibe_core.plugins.opus_assistant.conductor  # Specialized script
```

**✅ RIGHT (Reusable):**
```bash
python -m vibe_core.cli execute \
    --circuit knowledge/circuits/maintenance/opus_autonomy.yaml \
    --headless \
    --non-interactive
```

**Why:**
1. **Reusability**: Tomorrow's "Security Scan Conductor" = just another YAML, not Python
2. **Testing**: Test autonomy loop locally like any other circuit
3. **Singularity**: System can invent new maintenance tasks by writing YAML (safe), not Python (dangerous)

### Prerequisites

| Requirement | Status | Action |
|-------------|--------|--------|
| Python 3.11+ | ✅ | Already in pyproject.toml |
| `execute --circuit` CLI | ❌ | Add to unified_cli.py |
| Headless Boot Mode | ❌ | Add to boot_sequence.py |
| `opus_autonomy.yaml` | ❌ | Create circuit definition |

> 🧠 **DESIGN DECISION 3**: Headless Boot must be MINIMAL
>
> GitHub Action can't wait 5 minutes for Docker + API servers.
> Headless = Core logic + FileSystem + StateManager + LLM client. No Docker, no FastAPI.

### Implementation

**Phase 4.1: Add Headless Boot Mode**

File: `vibe_core/runtime/boot_sequence.py`
```python
class BootMode(Enum):
    FULL = "full"        # API Server, Agent Container, Event Bus, DB
    HEADLESS = "headless"  # Core logic, FileSystem, StateManager, LLM client only

def boot_kernel(mode: BootMode = BootMode.FULL) -> RealVibeKernel:
    """Boot kernel with specified mode."""
    kernel = RealVibeKernel()

    if mode == BootMode.HEADLESS:
        # Skip heavy subsystems
        kernel.skip_docker = True
        kernel.skip_api_server = True
        kernel.skip_agent_containers = True
        # Keep: FileSystem, StateManager, LLM clients, CircuitEngine
    else:
        # Full boot
        kernel.start_api_server()
        kernel.start_agent_containers()
        # ...

    return kernel
```

**Phase 4.2: Add `execute --circuit` to CLI**

File: `vibe_core/cli/unified_cli.py`
```python
@cli.command()
@click.option("--circuit", required=True, help="Path to circuit YAML")
@click.option("--headless", is_flag=True, help="Boot in headless mode")
@click.option("--non-interactive", is_flag=True, help="No prompts")
def execute(circuit: str, headless: bool, non_interactive: bool):
    """Execute a circuit in headless mode."""
    from vibe_core.runtime.boot_sequence import boot_kernel, BootMode

    mode = BootMode.HEADLESS if headless else BootMode.FULL
    kernel = boot_kernel(mode)

    # Load and execute circuit
    circuit_engine = kernel.get_engine("circuit")
    result = circuit_engine.execute_circuit(circuit)

    sys.exit(0 if result.success else 1)
```

**Phase 4.3: Create OPUS Autonomy Circuit**

File: `knowledge/circuits/maintenance/opus_autonomy.yaml`
```yaml
circuit:
  id: OPUS_AUTONOMY
  name: "OPUS Autonomous Maintenance"
  description: "Self-improvement cycle for GitHub Actions"

  triggers:
    - event: MANUAL  # Triggered by CLI

  entry_state: verify_health

  states:
    verify_health:
      actions:
        - action_type: EXECUTE_SCRIPT
          target: "opus.verify"
      transitions:
        - condition: "result.score >= 80"
          next_state: update_opus
        - condition: "result.score < 80"
          next_state: log_degradation

    log_degradation:
      actions:
        - action_type: EXECUTE_SCRIPT
          target: "opus.log_observation"
          params:
            severity: WARN
            message: "Trust score degraded: {{ result.score }}%"
      transitions:
        - next_state: update_opus

    update_opus:
      actions:
        - action_type: EXECUTE_SCRIPT
          target: "opus.write_opus_md"  # Triggers InterfacePlugin
      transitions:
        - next_state: complete

    complete:
      terminal: true
```

### GitHub Action (Final)

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
        run: pip install -e .

      - name: OPUS Autonomy Cycle
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python -m vibe_core.cli execute \
            --circuit knowledge/circuits/maintenance/opus_autonomy.yaml \
            --headless \
            --non-interactive

      - name: Commit Changes
        run: |
          git config user.name "OPUS Conductor"
          git config user.email "opus@steward.ai"
          git add OPUS.md .opus_state/
          git diff --cached --quiet || git commit -m "🔮 OPUS: Autonomous insight"
          git push
```

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| `BootMode.HEADLESS` implemented | Unit test: boots in <5s, no Docker |
| `execute --circuit` works | `python -m vibe_core.cli execute --help` |
| `opus_autonomy.yaml` executes | Local test with --dry-run |
| GitHub Action succeeds | Check Actions tab |

### Why This Is Singularity-Ready

1. **Self-Modifying**: System can write new YAML circuits (safe) to add behaviors
2. **No Specialized Code**: Same CLI, same engine, different YAML
3. **Testable**: Run autonomy loop locally before deploying to GitHub
4. **Extensible**: Add `security_scan.yaml`, `dependency_update.yaml` with zero Python

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

### 6. Experience Replay, Not Logs (NEW - Design Decision 1)
- `SyscallEntry` = Training data, not just logs
- Links: Intent → Action → Outcome → Karma Impact
- Enables in-context learning without fine-tuning

### 7. No Specialized Scripts (NEW - Design Decision 2)
- Conductor = Circuit + CLI, not Python script
- System controls itself through standard tools
- New automation = new YAML, not new Python

### 8. Headless Boot Mode (NEW - Design Decision 3)
- GitHub Actions need fast boot (<5s)
- Headless = Core + FileSystem + StateManager + LLM
- No Docker, no FastAPI, no Agent Containers

---

## Priority Matrix

| Layer | Priority | Effort | Impact | Status |
|-------|----------|--------|--------|--------|
| 1. Living Dashboard | - | - | - | ✅ DONE |
| 2. Syscall Console | P1 | Medium | High | 📋 READY (spec complete) |
| 3. 4D Hypercube | P2 | Medium | Medium | 📋 PLANNED |
| 4. Autonomous Conductor | P3 | Medium | High | 📋 READY (spec complete) |
| 5. Multiverse | P4 | Very High | Very High | 🔴 NEEDS RFC |

---

## Summary of Design Decisions

| # | Decision | Why |
|---|----------|-----|
| 1 | SyscallEntry = Experience Replay | Self-learning without fine-tuning |
| 2 | No conductor.py | Reusable circuits, system self-controls |
| 3 | Headless Boot Mode | Fast GitHub Actions (<5s boot) |

---

## Next Actions

### Layer 2: Syscall Console
1. [ ] Add `SyscallEntry` dataclass to `state_manager.py`
2. [ ] Add `record_syscall()` method to `OpusStateManager`
3. [ ] Add `get_successful_syscalls()` for few-shot learning
4. [ ] Create `syscall_console.md.j2` panel
5. [ ] Wire envoy to record syscalls

### Layer 3: 4D Hypercube
1. [ ] Add `_gather_city()` to renderer
2. [ ] Add karma trend calculation
3. [ ] Create `hypercube.md.j2` panel

### Layer 4: Autonomous Conductor
1. [ ] Implement `BootMode.HEADLESS` in boot_sequence.py
2. [ ] Add `execute --circuit` to unified_cli.py
3. [ ] Create `opus_autonomy.yaml` circuit
4. [ ] Test locally before GitHub Action

### Layer 5: Multiverse
1. [ ] Write RFC for multiverse architecture
2. [ ] Define karma merge algorithm
3. [ ] POC on single feature branch

---

*This document is honest about what exists vs what's aspirational. No spaghetti.*
