# OPUS-087: PRANA - Plugin Pulse Architecture

**Scope:** Refactor Heartbeat to be "dumb" like the Kernel
**Philosophy:** Heartbeat receives, Plugins execute. No business logic in scheduler.
**Status:** 🔴 HIGH RISK / CRITICAL PATH (Pending Implementation)

---

## Terminology

| Term | Scope | Timing | Context |
|------|-------|--------|---------|
| **Tick** | Micro-Cycle | Milliseconds | In-process kernel loop. `on_tick_pre`/`on_tick_post`. Memory/CPU operations. |
| **Pulse** | Macro-Cycle | Minutes | Out-of-process (GitHub Actions). `on_pulse`. Git ops, reporting, state sync. |

**Key Insight:** Ticks are synchronous (kernel is running). Pulses are asynchronous (headless mode, cron-triggered).

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


class PulseTransaction:
    """Collects mutations from all plugins for atomic batch commit."""

    def __init__(self):
        self.mutations: List[StateMutation] = []
        self.validation_errors: List[str] = []
        self.committed: bool = False

    def register(self, mutation: StateMutation) -> bool:
        """Register a mutation. Returns False if validation fails."""
        if not mutation.validate():
            self.validation_errors.append(
                f"{mutation.plugin_id}: Invalid mutation {mutation.action}"
            )
            return False
        self.mutations.append(mutation)
        return True

    def abort(self, reason: str) -> None:
        """Abort transaction before commit. Clears all mutations."""
        logger.warning(f"PulseTransaction ABORT: {reason}")
        self.mutations.clear()
        self.validation_errors.append(reason)

    def commit(self) -> Tuple[int, int]:
        """
        Execute all mutations. Returns (success_count, failure_count).

        FAIL-FORWARD STRATEGY:
        - If validation fails BEFORE write -> Abort entire transaction
        - If error occurs DURING write -> Log, continue, don't rollback
        - Git state is too complex for safe rollback
        """
        if self.validation_errors:
            logger.error(f"Cannot commit: {len(self.validation_errors)} validation errors")
            return (0, len(self.mutations))

        success, failure = 0, 0
        sorted_mutations = sorted(self.mutations, key=lambda m: m.priority)

        for mutation in sorted_mutations:
            try:
                self._apply_mutation(mutation)
                success += 1
            except Exception as e:
                logger.error(f"Mutation failed: {mutation.plugin_id}/{mutation.action}: {e}")
                failure += 1
                # FAIL-FORWARD: Continue with next mutation

        self.committed = True
        return (success, failure)
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

## Plugin Protocol Extension

```python
# In vibe_core/plugin_protocol.py - ADD to KernelPlugin class

def on_pulse(
    self,
    kernel: "RealVibeKernel",
    transaction: "PulseTransaction",
) -> HookResult:
    """
    Called during heartbeat pulse (macro-cycle).

    IMPORTANT: This runs OUT-OF-PROCESS (GitHub Actions headless mode).
    Do NOT assume kernel is fully initialized.

    Args:
        kernel: The kernel instance (may be minimal in headless mode)
        transaction: Register mutations here, don't commit directly

    Returns:
        HookResult with optional data for reporting

    Example:
        def on_pulse(self, kernel, transaction) -> HookResult:
            # Collect data
            karma = self.calculate_karma_decay()

            # Register mutation (don't apply directly!)
            transaction.register(StateMutation(
                plugin_id=self.plugin_id,
                action="decay_karma",
                target="karma.json",
                payload={"agent_id": "envoy", "delta": karma}
            ))

            return HookResult.ok(data={"decayed": karma})
    """
    return HookResult.ok()

@property
def pulse_phase(self) -> "PulsePhase":
    """
    Declare execution phase for on_pulse ordering.

    Phases execute in order: SENSORS -> COGNITION -> ACTUATORS -> CLEANUP

    Override to change default (ACTUATORS).
    """
    return PulsePhase.ACTUATORS
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

wiring:
  # === PLUGIN PROTOCOL ===
  - pattern: "def on_pulse"
    in: vibe_core/plugin_protocol.py
  - pattern: "def pulse_phase"
    in: vibe_core/plugin_protocol.py

  # === PULSE PHASE ENUM ===
  - pattern: "class PulsePhase"
    in: vibe_core/plugin_protocol.py

  # === ORCHESTRATOR ===
  - pattern: "class PranaOrchestrator"
    in: vibe_core/prana_orchestrator.py
  - pattern: "class PulseTransaction"
    in: vibe_core/prana_orchestrator.py
  - pattern: "class StateMutation"
    in: vibe_core/prana_orchestrator.py

  # === RATE LIMITING ===
  - pattern: "min_pulse_interval_seconds"
    in: vibe_core/prana_orchestrator.py

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
-->

---

## Migration Plan (Incremental)

| Phase | Task | Risk | Safety | Reversible |
|-------|------|------|--------|------------|
| 1 | Add `PulsePhase` enum to plugin_protocol.py | LOW | N/A | YES |
| 2 | Add `on_pulse` + `pulse_phase` to KernelPlugin | LOW | N/A | YES |
| 3 | Create `vibe_core/prana_orchestrator.py` with safety wrappers | LOW | Isolated | YES |
| 4 | Create `tests/integration/test_prana_orchestrator.py` | LOW | TDD | YES |
| 5 | Implement `on_pulse` in opus_assistant (OPUS.md refresh) | MEDIUM | Tested | YES |
| 6 | Implement `on_pulse` in vedic_governance (karma decay) | MEDIUM | Tested | YES |
| 7 | Wire heartbeat.py to use PranaOrchestrator | **HIGH** | Full test | PARTIAL |

### Phase 5 Spec: opus_assistant.on_pulse

```python
def on_pulse(self, kernel, transaction) -> HookResult:
    """Refresh OPUS.md during heartbeat."""
    # 1. Collect current state
    state = self._collect_prakriti_state(kernel)

    # 2. Render OPUS.md content
    content = self._render_opus_md(state)

    # 3. Register mutation
    transaction.register(StateMutation(
        plugin_id=self.plugin_id,
        action="update_doc",
        target="OPUS.md",
        payload={"content": content}
    ))

    return HookResult.ok(data={"sections_updated": len(state)})
```

### Phase 6 Spec: vedic_governance.on_pulse

```python
def on_pulse(self, kernel, transaction) -> HookResult:
    """Apply karma decay and ashrama transitions."""
    mutations = []

    # 1. Calculate karma decay for all agents
    for agent_id in self._get_active_agents():
        decay = self._calculate_decay(agent_id)
        if decay != 0:
            transaction.register(StateMutation(
                plugin_id=self.plugin_id,
                action="decay_karma",
                target="karma.json",
                payload={"agent_id": agent_id, "delta": decay}
            ))
            mutations.append(agent_id)

    return HookResult.ok(data={"agents_processed": len(mutations)})
```

---

## Semantic Checks (Pre-Implementation)

All checks are automated via `@HARNESS` block above. Manual verification:

- [ ] `PulsePhase` enum has exactly 4 values in correct order
- [ ] `on_pulse` signature includes `transaction: PulseTransaction` parameter
- [ ] `StateMutation.validate()` checks all required fields
- [ ] `PulseTransaction.commit()` implements fail-forward (no rollback)
- [ ] `min_pulse_interval_seconds >= 60` enforced
- [ ] No `git commit` or `git push` inside plugin `on_pulse` methods
- [ ] Tests cover: isolation failure, phase ordering, rate limiting, mutation validation

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

---

## Dependencies

This spec depends on:
- `vibe_core/plugin_protocol.py` (KernelPlugin base class)
- `vibe_core/prana.py` (config loading - DO NOT MODIFY)
- `scripts/heartbeat.py` (orchestration target)

This spec is required by:
- OPUS-088 (if exists): Advanced pulse scheduling
- Any future plugin implementing `on_pulse`

---

*"प्राण - The vital life force must be protected from chaos."*
