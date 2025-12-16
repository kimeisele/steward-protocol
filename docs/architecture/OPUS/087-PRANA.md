# OPUS-087: PRANA - Plugin Pulse Architecture

**Scope:** Refactor Heartbeat to be "dumb" like the Kernel
**Philosophy:** Heartbeat receives, Plugins execute. No business logic in scheduler.
**Status:** 🟡 IN PROGRESS (Phase 4 Complete, Phase 5-7 Pending)

---

## Implementation Progress

| Phase | Task | Status | Commit |
|-------|------|--------|--------|
| 1 | Add `PulsePhase` enum to plugin_protocol.py | ✅ DONE | `f9be506` |
| 2 | Add `on_pulse` + `pulse_phase` to KernelPlugin | ✅ DONE | `f9be506` |
| 3 | Create `vibe_core/prana_orchestrator.py` | ✅ DONE | `4948536` |
| 4 | Create `tests/integration/test_prana_orchestrator.py` | ✅ DONE | `4948536` |
| 5 | Implement `on_pulse` in opus_assistant | ⏳ PENDING | - |
| 6 | Implement `on_pulse` in vedic_governance | ⏳ PENDING | - |
| 7 | Wire heartbeat.py to use PranaOrchestrator | ⏳ PENDING | - |

**Current Test Status:** 26/26 tests passing (`test_prana_orchestrator.py`)

---

## Terminology

| Term | Scope | Timing | Context |
|------|-------|--------|---------|
| **Tick** | Micro-Cycle | Milliseconds | In-process kernel loop. `on_tick_pre`/`on_tick_post`. Memory/CPU operations. |
| **Pulse** | Macro-Cycle | Minutes | Out-of-process (GitHub Actions). `on_pulse`. Git ops, reporting, state sync. |

**Key Insight:** Ticks are synchronous (kernel is running). Pulses are asynchronous (headless mode, cron-triggered).

---

## VISNU Compliance (Layer 0 Protection)

**CRITICAL:** We MUST NOT modify `.github/workflows/*.yml` files.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 0: VISNU PROTECTED                      │
│  .github/workflows/heartbeat.yml  ← IMMUTABLE (cron: */15 * * *)│
│  .github/workflows/steward-ci.yml ← IMMUTABLE                    │
│  .github/workflows/system-cycle.yml ← IMMUTABLE                  │
├─────────────────────────────────────────────────────────────────┤
│                    LAYER 1: CONFIG-DRIVEN                        │
│  config/prana.yaml  ← EDITABLE (behavior changes here)          │
│  scripts/heartbeat.py ← CALLS PranaOrchestrator                 │
├─────────────────────────────────────────────────────────────────┤
│                    LAYER 2: PLUGIN CODE                          │
│  vibe_core/prana_orchestrator.py ← Orchestration logic          │
│  vibe_core/plugins/*/plugin_main.py ← on_pulse implementations  │
└─────────────────────────────────────────────────────────────────┘
```

**Why this matters:**
- Workflow files require manual approval for changes
- Config changes can be committed automatically
- Plugin code is covered by standard CI/CD

---

## System Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  GitHub Actions (Layer 0)                        │
│  heartbeat.yml: cron: '*/15 * * * *'                            │
│       ↓                                                          │
│  python scripts/heartbeat.py                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  scripts/heartbeat.py                            │
│  1. Load config/prana.yaml (via vibe_core/prana.py)             │
│  2. Check min_interval (skip if too soon)                        │
│  3. Boot kernel if configured                                    │
│  4. Create PranaOrchestrator                     ← NEW!         │
│  5. Call orchestrator.run_pulse_cycle()          ← NEW!         │
│  6. Single git commit at end                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PranaOrchestrator                               │
│  1. Create PulseTransaction                                      │
│  2. Get plugins sorted by PulsePhase                             │
│  3. Execute each phase:                                          │
│     SENSORS (1) → COGNITION (2) → ACTUATORS (3) → CLEANUP (4)   │
│  4. For each plugin:                                             │
│     try:                                                         │
│       result = plugin.on_pulse(kernel, transaction)              │
│     except:                                                      │
│       quarantine_plugin(plugin_id)                               │
│  5. Commit all mutations atomically                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Plugin on_pulse() Implementations               │
├─────────────────────────────────────────────────────────────────┤
│  opus_assistant (Phase: SENSORS)                                 │
│  → Collect Prakriti state                                        │
│  → Render OPUS.md                                                │
│  → Register: StateMutation(action="update_doc", target="OPUS.md")│
├─────────────────────────────────────────────────────────────────┤
│  vedic_governance (Phase: ACTUATORS)                             │
│  → Calculate karma decay                                         │
│  → Check ashrama transitions                                     │
│  → Register: StateMutation(action="decay_karma", target=...)     │
├─────────────────────────────────────────────────────────────────┤
│  interface (Phase: CLEANUP)                                      │
│  → Write rendered files                                          │
│  → Cleanup temp state                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Vision

```
CURRENT: heartbeat.py = 605 LOC of business logic
TARGET:  heartbeat.py = ~100 LOC (orchestration + safety wrappers)
         prana_orchestrator.py = Plugin pulse coordination
```

**Architecture Decision:** The existing `vibe_core/prana.py` (config loader) remains UNTOUCHED. New orchestration logic goes into `vibe_core/prana_orchestrator.py` to avoid naming collision and boot process disruption.

---

## Units Convention

**CRITICAL:** All time values in core code use **SECONDS (int)**. Conversion to minutes happens ONLY at UI/config boundaries.

```python
# CORRECT - Internal
min_pulse_interval: int = 60  # 60 seconds

# CORRECT - Config file (user-facing)
# config/prana.yaml
heartbeat:
  min_interval_minutes: 1  # Converted to 60 seconds on load
```

---

## Safety Requirements

### 1. Isolation Wrappers (Bad Apple Problem)

```python
# WRONG (Naive)
for plugin in plugins:
    plugin.on_pulse(kernel)  # One crash = ALL dead

# CORRECT (Senior)
for plugin in plugins:
    try:
        result = plugin.on_pulse(kernel)
        self.log_pulse_success(plugin.name, result)
    except Exception as e:
        self.log_pulse_failure(plugin.name, e)
        self.quarantine_plugin(plugin.name)
        # Loop continues! Heart keeps beating.
```

### 2. Deterministic Sequence (Varna System)

Plugins MUST declare execution phase. Random order = race conditions.

```python
class PulsePhase(Enum):
    """Execution phases for pulse cycle - ordered by dependency."""
    SENSORS = 1    # Drishti - Collect data first
    COGNITION = 2  # Manas - Then think
    ACTUATORS = 3  # Karma - Then act
    CLEANUP = 4    # Shuddhi - Finally cleanup

class KernelPlugin(ABC):
    @property
    def pulse_phase(self) -> PulsePhase:
        """Override to declare execution phase. Default: ACTUATORS."""
        return PulsePhase.ACTUATORS
```

### 3. Adrenaline Governor (Rate Limiting)

Plugins can REQUEST faster pulses. PRANA decides.

```python
@dataclass
class PranaOrchestratorConfig:
    min_pulse_interval_seconds: int = 60  # NEVER faster than 60s
    default_interval_seconds: int = 900   # 15 min

def resolve_frequency(self, votes: List[int]) -> int:
    """Conservative voting: use max(votes, min_limit)"""
    requested = min(votes) if votes else self.default_interval_seconds
    return max(requested, self.min_pulse_interval_seconds)
```

### 4. Best Effort Batching (Fail-Forward Strategy)

Plugins MUST NOT commit to Git during `on_pulse`. They register mutations with PulseTransaction.

```python
@dataclass
class StateMutation:
    """Single state change request from a plugin."""
    plugin_id: str
    action: str  # e.g., "update_doc", "decay_karma", "refresh_opus"
    target: str  # e.g., "OPUS.md", "karma.json", "agent:envoy"
    payload: Dict[str, Any]
    priority: int = 1  # Lower = execute first within phase

    def validate(self) -> bool:
        """Pre-flight validation before commit."""
        return bool(self.plugin_id and self.action and self.target)
```

---

## Mutation Schema

### Allowed Actions

| Action | Target Pattern | Payload | Description |
|--------|----------------|---------|-------------|
| `update_doc` | `*.md` | `{"content": str}` | Update markdown file |
| `decay_karma` | `karma.json` | `{"agent_id": str, "delta": int}` | Adjust karma score |
| `refresh_state` | `prakriti/*` | `{"layer": int}` | Refresh Prakriti layer |
| `log_observation` | `journal/*` | `{"severity": str, "message": str}` | Add to system journal |
| `quarantine_plugin` | `plugin:{id}` | `{"reason": str}` | Disable misbehaving plugin |

### Validation Rules

1. `plugin_id` MUST match registered plugin
2. `action` MUST be in allowed actions list
3. `target` MUST match expected pattern for action
4. `payload` MUST contain required fields for action

---

## Phase 5: opus_assistant.on_pulse (DETAILED)

**File:** `vibe_core/plugins/opus_assistant/plugin_main.py`
**PulsePhase:** `SENSORS` (runs first - collects state)

### Implementation

```python
from vibe_core.plugin_protocol import HookResult, PulsePhase
from vibe_core.prana_orchestrator import StateMutation

class OpusAssistantPlugin(KernelPlugin):

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS  # Collect data first

    def on_pulse(self, kernel, transaction) -> HookResult:
        """
        Refresh OPUS.md during heartbeat.

        This runs every 15 minutes via GitHub Actions.
        Collects system state and renders the dashboard.
        """
        try:
            # 1. Collect current state (headless-safe)
            state = self._collect_pulse_state(kernel)

            # 2. Render OPUS.md content
            content = self._render_opus_for_pulse(state)

            # 3. Register mutation (don't write directly!)
            transaction.register(StateMutation(
                plugin_id=self.plugin_id,
                action="update_doc",
                target="OPUS.md",
                payload={"content": content}
            ))

            return HookResult.ok(data={
                "sections_updated": len(state),
                "content_length": len(content)
            })

        except Exception as e:
            # Don't crash - return error result
            return HookResult.error(f"OPUS refresh failed: {e}")

    def _collect_pulse_state(self, kernel) -> Dict[str, Any]:
        """
        Collect state in headless mode.

        IMPORTANT: kernel may be None or minimal in GitHub Actions.
        Must work without full kernel initialization.
        """
        state = {}

        # Layer 1: Git state (always available)
        state["git"] = self._get_git_state()

        # Layer 2: Runtime state (if kernel available)
        if kernel:
            state["kernel"] = {
                "running": True,
                "agents": len(kernel.get_agents() if hasattr(kernel, 'get_agents') else [])
            }
        else:
            state["kernel"] = {"running": False, "agents": 0}

        # Layer 3: File-based state
        state["verification"] = self._read_verification_cache()

        return state

    def _render_opus_for_pulse(self, state: Dict[str, Any]) -> str:
        """Render OPUS.md from collected state."""
        # Use existing renderer but in headless mode
        return self._opus_renderer.render(state, headless=True)
```

### Test Cases Required

```python
# tests/integration/test_opus_pulse.py

def test_opus_on_pulse_returns_ok():
    """on_pulse should return HookResult.ok() on success."""

def test_opus_on_pulse_registers_mutation():
    """on_pulse should register exactly one update_doc mutation."""

def test_opus_on_pulse_works_headless():
    """on_pulse should work when kernel is None."""

def test_opus_pulse_phase_is_sensors():
    """opus_assistant should declare SENSORS phase."""

def test_opus_on_pulse_handles_errors():
    """on_pulse should return HookResult.error() not raise."""
```

---

## Phase 6: vedic_governance.on_pulse (DETAILED)

**File:** `vibe_core/plugins/vedic_governance/plugin_main.py`
**PulsePhase:** `ACTUATORS` (runs after data collection)

### Implementation

```python
from vibe_core.plugin_protocol import HookResult, PulsePhase
from vibe_core.prana_orchestrator import StateMutation

class VedicGovernancePlugin(KernelPlugin):

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.ACTUATORS  # Act on collected data

    def on_pulse(self, kernel, transaction) -> HookResult:
        """
        Apply karma decay and check ashrama transitions.

        Runs every 15 minutes to:
        1. Decay karma for inactive agents
        2. Check if any agent should transition ashrama
        3. Update governance state
        """
        try:
            processed = 0

            # 1. Load current karma state
            karma_state = self._load_karma_state()

            # 2. Calculate decay for each agent
            for agent_id, karma in karma_state.items():
                decay = self._calculate_pulse_decay(agent_id, karma)

                if decay != 0:
                    transaction.register(StateMutation(
                        plugin_id=self.plugin_id,
                        action="decay_karma",
                        target="karma.json",
                        payload={"agent_id": agent_id, "delta": decay}
                    ))
                    processed += 1

            # 3. Check ashrama transitions
            transitions = self._check_ashrama_transitions()
            for agent_id, new_ashrama in transitions:
                transaction.register(StateMutation(
                    plugin_id=self.plugin_id,
                    action="log_observation",
                    target="journal/governance.log",
                    payload={
                        "severity": "INFO",
                        "message": f"Agent {agent_id} transitioned to {new_ashrama}"
                    }
                ))

            return HookResult.ok(data={
                "agents_processed": processed,
                "transitions": len(transitions)
            })

        except Exception as e:
            return HookResult.error(f"Governance pulse failed: {e}")

    def _calculate_pulse_decay(self, agent_id: str, current_karma: int) -> int:
        """
        Calculate karma decay for one pulse cycle.

        Decay rules:
        - No activity in 15 min: -1 karma
        - Error in last pulse: -5 karma
        - Success in last pulse: +1 karma (recovery)
        """
        # Implementation based on activity tracking
        pass
```

### Test Cases Required

```python
# tests/integration/test_governance_pulse.py

def test_governance_on_pulse_returns_ok():
    """on_pulse should return HookResult.ok() on success."""

def test_governance_on_pulse_registers_decay():
    """on_pulse should register decay_karma mutations."""

def test_governance_pulse_phase_is_actuators():
    """vedic_governance should declare ACTUATORS phase."""

def test_governance_decay_calculation():
    """Karma decay should follow specified rules."""

def test_governance_on_pulse_handles_errors():
    """on_pulse should return HookResult.error() not raise."""
```

---

## Phase 7: Wire heartbeat.py (DETAILED)

**File:** `scripts/heartbeat.py`
**Risk Level:** HIGH (production code change)

### Current Structure (605 LOC)

```python
class HeartbeatEngine:
    def pulse(self):
        # Phase 1: Ingest from inbox
        self._ingest_inbox()

        # Phase 2: Sync TASKS.md → TaskManager
        self._read_tasks_md()

        # Phase 3: Execute pending tasks
        self._execute_tasks()

        # Phase 4: MANAS thinks (OPUS-073)
        self._manas_think()

        # Phase 5: Sync TaskManager → TASKS.md
        self._write_tasks_md()

        # Phase 6: Commit progress
        self._commit_progress()
```

### Target Structure (~100 LOC)

```python
class HeartbeatEngine:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.orchestrator = PranaOrchestrator(kernel=None)

    def pulse(self):
        """Execute one heartbeat cycle using PranaOrchestrator."""
        logger.info("💓 HEARTBEAT PULSE STARTED")

        try:
            # Single entry point: Let plugins do the work
            result = self.orchestrator.run_pulse_cycle()

            # Log results
            logger.info(f"  Plugins executed: {result['plugins_executed']}")
            logger.info(f"  Mutations committed: {result['mutations_committed']}")

            # Git commit (single atomic commit)
            if result['mutations_committed'] > 0:
                self._commit_progress(result)

            logger.info("✅ HEARTBEAT PULSE COMPLETED")

        except Exception as e:
            logger.error(f"❌ HEARTBEAT FAILED: {e}")
            raise
```

### Migration Strategy

```
Step 1: Add PranaOrchestrator import (safe)
Step 2: Create orchestrator in __init__ (safe)
Step 3: Add run_pulse_cycle() call BEFORE existing logic (parallel run)
Step 4: Compare results for 1 week
Step 5: Remove old business logic one method at a time
Step 6: Final cleanup
```

---

## The Harness

<!-- @HARNESS
files:
  - path: scripts/heartbeat.py
    required: true
  - path: vibe_core/plugin_protocol.py
    required: true
  - path: vibe_core/prana_orchestrator.py
    required: true
  - path: vibe_core/plugins/opus_assistant/plugin_main.py
    required: true
  - path: vibe_core/plugins/vedic_governance/plugin_main.py
    required: true

wiring:
  # === PLUGIN PROTOCOL (Phase 1-2) ===
  - pattern: "def on_pulse"
    in: vibe_core/plugin_protocol.py
  - pattern: "def pulse_phase"
    in: vibe_core/plugin_protocol.py
  - pattern: "class PulsePhase"
    in: vibe_core/plugin_protocol.py

  # === ORCHESTRATOR (Phase 3) ===
  - pattern: "class PranaOrchestrator"
    in: vibe_core/prana_orchestrator.py
  - pattern: "class PulseTransaction"
    in: vibe_core/prana_orchestrator.py
  - pattern: "class StateMutation"
    in: vibe_core/prana_orchestrator.py
  - pattern: "min_pulse_interval_seconds"
    in: vibe_core/prana_orchestrator.py

  # === OPUS ASSISTANT (Phase 5) ===
  - pattern: "def on_pulse"
    in: vibe_core/plugins/opus_assistant/plugin_main.py
  - pattern: "pulse_phase.*SENSORS"
    in: vibe_core/plugins/opus_assistant/plugin_main.py

  # === VEDIC GOVERNANCE (Phase 6) ===
  - pattern: "def on_pulse"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "pulse_phase.*ACTUATORS"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

  # === HEARTBEAT WIRING (Phase 7) ===
  - pattern: "PranaOrchestrator"
    in: scripts/heartbeat.py
  - pattern: "run_pulse_cycle"
    in: scripts/heartbeat.py

semantic:
  - type: method_exists
    name: plugin_on_pulse
    in: vibe_core/plugin_protocol.py
    class: KernelPlugin
    method: on_pulse
    rationale: "Plugins must have on_pulse hook for heartbeat integration"

  - type: property_exists
    name: plugin_pulse_phase
    in: vibe_core/plugin_protocol.py
    class: KernelPlugin
    property: pulse_phase
    rationale: "Plugins must declare execution phase for deterministic ordering"

  - type: enum_exists
    name: pulse_phase_enum
    in: vibe_core/plugin_protocol.py
    enum: PulsePhase
    values: [SENSORS, COGNITION, ACTUATORS, CLEANUP]
    rationale: "Execution phases must be explicitly defined"

  - type: class_exists
    name: pulse_transaction
    in: vibe_core/prana_orchestrator.py
    class: PulseTransaction
    rationale: "Transaction wrapper for atomic mutation batching"

  - type: class_exists
    name: state_mutation
    in: vibe_core/prana_orchestrator.py
    class: StateMutation
    rationale: "Typed mutation schema for plugin state changes"

  - type: config_exists
    name: prana_min_interval
    in: vibe_core/prana_orchestrator.py
    field: min_pulse_interval_seconds
    rationale: "Rate limiting MUST be enforced in seconds"

tests:
  - tests/integration/test_prana_orchestrator.py
  - tests/integration/test_opus_pulse.py
  - tests/integration/test_governance_pulse.py
-->

---

## Semantic Checks (Implementation Status)

### Phase 1-4 (DONE ✅)

- [x] `PulsePhase` enum has exactly 4 values in correct order
- [x] `on_pulse` signature includes `transaction: PulseTransaction` parameter
- [x] `StateMutation.validate()` checks all required fields
- [x] `PulseTransaction.commit()` implements fail-forward (no rollback)
- [x] `min_pulse_interval_seconds >= 60` enforced
- [x] Tests cover: isolation failure, phase ordering, rate limiting, mutation validation

### Phase 5 (PENDING ⏳)

- [ ] `opus_assistant.on_pulse` implemented
- [ ] `opus_assistant.pulse_phase` returns `PulsePhase.SENSORS`
- [ ] Works in headless mode (kernel=None)
- [ ] Registers `update_doc` mutation for OPUS.md
- [ ] Tests pass: `test_opus_pulse.py`

### Phase 6 (PENDING ⏳)

- [ ] `vedic_governance.on_pulse` implemented
- [ ] `vedic_governance.pulse_phase` returns `PulsePhase.ACTUATORS`
- [ ] Registers `decay_karma` mutations
- [ ] Tests pass: `test_governance_pulse.py`

### Phase 7 (PENDING ⏳)

- [ ] `heartbeat.py` imports `PranaOrchestrator`
- [ ] `heartbeat.py` calls `run_pulse_cycle()`
- [ ] No `git commit` inside plugin `on_pulse` methods
- [ ] Single atomic commit at end of pulse

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plugin crash during pulse | Other plugins blocked | Isolation wrappers (try/except per plugin) |
| Race condition in mutations | Corrupted state | PulsePhase ordering + single commit |
| Rate limit bypass | System overload | Adrenaline Governor enforces min interval |
| Mutation validation bypass | Invalid state | StateMutation.validate() + abort on failure |
| Git conflict during commit | Merge hell | Single atomic commit at end of cycle |
| Rollback complexity | Data loss | Fail-forward strategy (no rollback) |
| Headless mode failures | Silent breakage | Explicit kernel=None handling in all plugins |
| VISNU violation | Blocked PR | Config-driven changes only (no workflow edits) |

---

## Dependencies

This spec depends on:
- `vibe_core/plugin_protocol.py` (KernelPlugin base class)
- `vibe_core/prana.py` (config loading - DO NOT MODIFY)
- `scripts/heartbeat.py` (orchestration target)
- `.github/workflows/heartbeat.yml` (VISNU PROTECTED - DO NOT MODIFY)

This spec is required by:
- Any future plugin implementing `on_pulse`
- OPUS dashboard refresh reliability
- Karma/governance automation

---

## Next Actions

1. **Implement Phase 5** - `opus_assistant.on_pulse()`
   - Add `pulse_phase` property returning `SENSORS`
   - Implement headless-safe state collection
   - Register `update_doc` mutation
   - Write tests

2. **Implement Phase 6** - `vedic_governance.on_pulse()`
   - Add `pulse_phase` property returning `ACTUATORS`
   - Implement karma decay logic
   - Register `decay_karma` mutations
   - Write tests

3. **Implement Phase 7** - Wire `heartbeat.py`
   - Add PranaOrchestrator import
   - Replace business logic with `run_pulse_cycle()`
   - Test in parallel with existing logic first
   - Final migration

---

*"प्राण - The vital life force must be protected from chaos."*
