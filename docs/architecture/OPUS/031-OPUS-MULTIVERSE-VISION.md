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
      - "def set_preference"
      - "def get_preference"

  # Layer 1.5: Control Cables (Bidirectional OPUS.md)
  - path: vibe_core/plugins/opus_assistant/core/control_cables.py
    required: true
    patterns:
      - "class ControlCablesParser"
      - "parse_control_plane"
      - "apply_to_state"
      - "SCHEMA"

  # Layer 1.5: Treasury (Resource Tracking with Kill-Switch)
  - path: vibe_core/plugins/opus_assistant/core/treasury.py
    required: true
    patterns:
      - "class Treasury"
      - "check_budget"
      - "record_usage"
      - "class DailySpend"

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

future:
  # Layer 1.5: Intent Buffer Panel (still to be created)
  - path: vibe_core/plugins/opus_assistant/templates/panels/intent_buffer.md.j2
    patterns:
      - "pending_intent"
      - "AWAITING_APPROVAL"

  # Layer 2: Syscall Console Panel (to be created)
  - path: vibe_core/plugins/opus_assistant/templates/panels/syscall_console.md.j2
    patterns:
      - "syscall_history"

  # Layer 2: SyscallEntry in StateManager (to be added)
  - path: vibe_core/plugins/opus_assistant/core/state_manager.py
    patterns:
      - "class SyscallEntry"
      - "record_syscall"
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

## Layer 1.5: Interactive Dashboard (P0 - Critical Upgrade)

> 🧠 **DESIGN DECISION 4**: OPUS.md is NOT just output - it's a **Bidirectional Control Surface**
>
> The document becomes the API. Edit the markdown → System changes behavior.
> No CLI needed. No REST calls. Just text.

### The Missing Link

Currently OPUS.md is **write-only** (system outputs). We need **read-write** (human inputs back).

```
CURRENT (One-Way):
StateManager → render() → OPUS.md → Human reads

REQUIRED (Bidirectional):
StateManager → render() → OPUS.md ←→ Human edits → Parser → StateManager
                                      ↑
                              FEEDBACK LOOP
```

### Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Control Cables Parser | ✅ DONE | `core/control_cables.py` |
| Treasury | ✅ DONE | `core/treasury.py` |
| set_preference() | ✅ DONE | `core/state_manager.py` |
| Intent Buffer | ❌ NOT EXISTS | `templates/panels/intent_buffer.md.j2` |
| Heartbeat Counter | ❌ NOT EXISTS | Needs integration into render cycle |
| Schema Validation | ✅ DONE | Built into `ControlCablesParser.SCHEMA` |

### Implementation

**Phase 1.5.1: Control Cables Parser**

> 🧠 **DESIGN DECISION 5**: Human edits are **Configuration**, not **Commands**
>
> When you edit `Auto-Heal Mode: ON` in OPUS.md, it persists until changed.
> It's not a one-shot command - it's a setting.

File: `opus_assistant/core/control_cables.py`
```python
class ControlCablesParser:
    """
    Parse Control Plane section from OPUS.md back into StateManager.

    This closes the feedback loop:
    OPUS.md (human edit) → Parser → StateManager → Next Render
    """

    VALID_SETTINGS = {
        "auto_heal_mode": {"type": bool, "default": False},
        "aggressive_refactoring": {"type": bool, "default": False},
        "budget_limit_usd": {"type": float, "default": 5.0},
        "simulation_mode": {"type": bool, "default": True},
    }

    def parse_control_plane(self, opus_content: str) -> Dict[str, Any]:
        """Extract settings from ## 🎛️ Control Plane section."""
        settings = {}

        # Find Control Plane section
        # Parse checkboxes: - [x] Setting: VALUE
        # Validate against VALID_SETTINGS schema
        # Return validated settings (invalid → fallback to default)

        return settings

    def apply_to_state(self, state_manager: OpusStateManager,
                       settings: Dict[str, Any]) -> None:
        """Apply parsed settings to StateManager."""
        for key, value in settings.items():
            state_manager.set_preference(key, value)
```

**Phase 1.5.2: Treasury Panel (Resource Awareness)**

> 🧠 **DESIGN DECISION 6**: Autonomous systems MUST track their resource consumption
>
> An infinite loop burning $100/hour is a bug. The system must know its budget.

File: `opus_assistant/core/treasury.py`
```python
@dataclass
class TreasuryState:
    """Track API costs and enforce budget limits."""

    tokens_used_today: int = 0
    estimated_cost_usd: float = 0.0
    budget_limit_usd: float = 5.0
    budget_exhausted: bool = False

    # Cost estimates (OpenRouter)
    COST_PER_1K_INPUT: float = 0.001
    COST_PER_1K_OUTPUT: float = 0.002

class Treasury:
    """
    Resource tracking with kill-switch.

    If budget_exhausted=True, the Autonomous Conductor MUST stop.
    """

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Record token usage and update cost estimate."""

    def check_budget(self) -> bool:
        """Return False if budget exhausted (kill-switch)."""
        return not self.state.budget_exhausted
```

**Phase 1.5.3: Intent Buffer (Explainable AI)**

> Before acting, declare intent. This makes the system transparent.

Template: `opus_assistant/templates/panels/intent_buffer.md.j2`
```jinja2
## 🎯 Pending Intent

{% if pending_intent %}
> **I intend to:** {{ pending_intent.action }}
> **Because:** {{ pending_intent.reason }}
> **Files affected:** {{ pending_intent.files | length }}
> **Risk level:** {{ pending_intent.risk }}
> **Status:** {{ pending_intent.status }}  {# AWAITING_APPROVAL | APPROVED | REJECTED #}
{% else %}
_No pending actions_
{% endif %}
```

**Phase 1.5.4: Heartbeat (Liveness Signal)**

```jinja2
**Cycle:** #{{ cycle_count }} | **Last Beat:** {{ heartbeat_utc }} | **Health:** {{ health_emoji }}
```

### Merge Strategy for Concurrent Edits

| Section Type | On Conflict |
|--------------|-------------|
| `@HUMAN:*` | NEVER overwrite - merge human content |
| `@AI:*` | System overwrites (AI's workspace) |
| `## 🎛️ Control Plane` | Parse and apply, then regenerate |
| Other sections | System overwrites |

### Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Control Cables Parser works | Edit checkbox → Next cycle reflects change |
| Treasury tracks costs | Check `.opus_state/treasury.json` |
| Intent Buffer renders | Visual check in OPUS.md |
| Heartbeat updates | Timestamp changes each cycle |
| Invalid settings fallback | Bad value → default, no crash |

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

### GitHub Action

```yaml
# .github/workflows/opus_conductor.yml
name: OPUS Conductor
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  push:
    branches: [main]
  workflow_dispatch:

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

### 6. Experience Replay, Not Logs (Design Decision 1)
- `SyscallEntry` = Training data, not just logs
- Links: Intent → Action → Outcome → Karma Impact
- Enables in-context learning without fine-tuning

### 7. No Specialized Scripts (Design Decision 2)
- Conductor = Circuit + CLI, not Python script
- System controls itself through standard tools
- New automation = new YAML, not new Python

### 8. Headless Boot Mode (Design Decision 3)
- GitHub Actions need fast boot (<5s)
- Headless = Core + FileSystem + StateManager + LLM
- No Docker, no FastAPI, no Agent Containers

### 9. Bidirectional Control Surface (Design Decision 4)
- OPUS.md is INPUT, not just OUTPUT
- Human edits → Parser → StateManager → Next Cycle
- The document IS the API

### 10. Configuration, Not Commands (Design Decision 5)
- Settings persist until changed
- Not one-shot commands
- Schema validation prevents invalid states

### 11. Resource Awareness (Design Decision 6)
- Track token usage and costs
- Budget limits with kill-switch
- Prevents runaway autonomous loops

---

## Priority Matrix

| Layer | Priority | Effort | Impact | Status |
|-------|----------|--------|--------|--------|
| 1. Living Dashboard | - | - | - | ✅ DONE |
| **1.5. Interactive Dashboard** | **P0** | **Medium** | **Critical** | **🟡 IN PROGRESS (3/5 components)** |
| 2. Syscall Console | P1 | Medium | High | 📋 READY (spec complete) |
| 3. 4D Hypercube | P2 | Medium | Medium | 📋 PLANNED |
| 4. Autonomous Conductor | P3 | Medium | High | 📋 READY (spec complete) |
| 5. Multiverse | P4 | Very High | Very High | 🔴 NEEDS RFC |

**Layer 1.5 Progress:**
- ✅ `control_cables.py` - Parse OPUS.md Control Plane back to state
- ✅ `treasury.py` - Track API costs with kill-switch
- ✅ `set_preference()` - Added to StateManager
- ❌ `intent_buffer.md.j2` - Still needed
- ❌ Heartbeat counter - Still needed

---

## Summary of Design Decisions

| # | Decision | Why |
|---|----------|-----|
| 1 | SyscallEntry = Experience Replay | Self-learning without fine-tuning |
| 2 | No conductor.py | Reusable circuits, system self-controls |
| 3 | Headless Boot Mode | Fast GitHub Actions (<5s boot) |
| 4 | Bidirectional Control Surface | OPUS.md as API, not just report |
| 5 | Configuration, Not Commands | Settings persist, schema-validated |
| 6 | Resource Awareness | Budget limits prevent runaway costs |

---

## Next Actions

### Layer 1.5: Interactive Dashboard (P0 - IN PROGRESS)
1. [x] Create `control_cables.py` with `ControlCablesParser`
2. [x] Add `parse_control_plane()` method
3. [ ] Integrate parser into render cycle (read before write)
4. [x] Create `treasury.py` with `Treasury` class
5. [ ] Add `intent_buffer.md.j2` panel template
6. [ ] Add heartbeat counter to session state
7. [ ] Test: Edit OPUS.md checkbox → Verify next cycle reflects change

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

## Appendix: Existing Wiring (Proof It's Possible)

### BlueprintGenerator (Already Works)
```python
# vibe_core/cartridges/system/envoy/blueprint_generator.py
SYSCALL_INTENT_PATTERNS = {
    SyscallType.SPAWN_COGNITION: [
        r"create\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|bot|worker|cartridge)",
        r"spawn\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|cognition|worker|bot)",
        ...
    ],
}
```

### SemanticSyscallExecutor (Already Works)
```python
# vibe_core/semantic_syscalls.py
def _handle_spawn_cognition(self, request: SyscallRequest) -> SyscallResult:
    """SPAWN_COGNITION: Birth a new agent."""
    # ... creates DynamicAgent, registers with kernel
```

### KernelTickHandler (Already Works)
```python
# vibe_core/plugins/opus_assistant/events/kernel_tick.py
async def _execute_cognitive_task(self, intent: str) -> Dict[str, Any]:
    """Execute a cognitive task via the Envoy pattern."""
    result = await executor.execute(
        playbook_id="cognitive_task",
        user_input=intent,
        intent_vector=None,
        kernel=kernel,
    )
```

---

*This document is honest about what exists vs what's aspirational. No spaghetti.
The Organizational Membrane now has feedback loops - it can be controlled through text.*
