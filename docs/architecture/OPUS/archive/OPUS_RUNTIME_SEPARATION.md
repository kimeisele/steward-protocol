# OPUS RUNTIME SEPARATION ARCHITECTURE

## Das Fundamentale Problem

**CODE | CONFIG | RUNTIME sind nicht getrennt.**

<!-- @HARNESS
files:
  - path: vibe_core/cartridges/system/envoy/deterministic_executor.py
    required: true
  - path: vibe_core/envoy_sync.py
    required: true
  - path: vibe_core/runtime/playbook_router.py
    required: true
  - path: vibe_core/cartridges/system/envoy/cartridge_main.py
    required: true
tests:
  - tests/integration/test_kernel_boot.py
wiring:
  - pattern: "DeterministicExecutor"
    in: vibe_core/cartridges/system/envoy/deterministic_executor.py
  - pattern: "EnvoySync"
    in: vibe_core/envoy_sync.py
absent:
  - pattern: "TODO.*runtime"
    in: vibe_core/cartridges/system/envoy/deterministic_executor.py
config:
  - section: runtime_separation
-->

```
AKTUELL (Spaghetti):
┌──────────────────────────────────────────────────────────────────┐
│  EnvoyPlugin  →  EnvoySync  →  PlaybookRouter  →  EnvoyCartridge │
│       ↓              ↓              ↓                   ↓        │
│  DeterministicExecutor  ←→  CircuitExecutor  ←→  MilkOceanRouter │
│       ↓              ↓              ↓                   ↓        │
│  ActionHandlers  ←→  Templates  ←→  Phase Results  ←→  ???       │
└──────────────────────────────────────────────────────────────────┘

Jeder ruft jeden. Keine klare Hierarchie. 8 dokumentierte BREAKS.
```

---

## Die Drei Schichten (SOLL-Zustand)

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAYER 1: CONFIG                          │
│                    (YAML, Static, Boot-time)                    │
├─────────────────────────────────────────────────────────────────┤
│  circuits/*.yaml     - Circuit definitions                      │
│  playbooks/*.yaml    - Playbook definitions                     │
│  _registry.yaml      - Route patterns                           │
│  templates/*.j2      - Jinja2 templates                         │
│                                                                 │
│  RULE: Loaded ONCE at boot. NEVER modified at runtime.          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                         [LOADER]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        LAYER 2: CODE                            │
│                    (Python, Logic, Static)                      │
├─────────────────────────────────────────────────────────────────┤
│  ActionHandlerRegistry   - Handler implementations               │
│  PlaybookLoader          - Config → Python objects               │
│  CircuitLoader           - Config → Python objects               │
│  TemplateEngine          - Jinja2 rendering                      │
│                                                                 │
│  RULE: Pure functions. No state. Deterministic.                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                       [EXECUTION]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       LAYER 3: RUNTIME                          │
│                   (State, Sessions, Dynamic)                    │
├─────────────────────────────────────────────────────────────────┤
│  ExecutionContext        - Current request state                 │
│  PhaseResults            - Inter-phase data flow                 │
│  EphemeralStorage        - Session cache (TTL)                   │
│  RequestLifecycle        - Request → Response tracking           │
│                                                                 │
│  RULE: All state here. Clear lifecycle. Observable.             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Root Cause Analysis: 8 Breaks

### BREAK 1: Dual Routing (PlaybookRouter + MilkOceanRouter)
```
EnvoySync → PlaybookRouter.route() → Task created
EnvoyCartridge → MilkOceanRouter.process_prayer() → Task blocked!

Problem: Zwei Router treffen unabhängige Entscheidungen.
Solution: EIN Router. MilkOcean ist ein GATE, kein Router.
```

### BREAK 2: Circuit vs Playbook Path Uncertainty
```
DeterministicExecutor._execute() {
    if (input compiles to syscall) → CircuitExecutor
    else → Playbook execution
}

Problem: Entscheidung zur EXECUTION time, nicht ROUTING time.
Solution: Router entscheidet Pfad. Executor führt nur aus.
```

### BREAK 3: Template Context nicht aktualisiert
```
template_context = build_context()  # Phase 1
execute_phase(phase_1)              # Speichert in phase_results
execute_phase(phase_2)              # Braucht phase_1 results
                                    # ABER: template_context ist STALE!

Problem: Context wird einmal gebaut, nicht aktualisiert.
Solution: Context vor JEDER Phase neu bauen.
```

### BREAK 4: Kernel Injection Race Condition
```
Request arrives → MilkOceanRouter needs kernel
                  BUT kernel not injected yet!

Problem: Lazy injection creates race conditions.
Solution: Eager initialization at boot time.
```

### BREAK 5: Result Format Mismatch
```
CircuitExecutor returns:  {status, circuit_id, output}
DeterministicExecutor:    {status, playbook_id, phases_executed}
EnvoyCartridge:           {status, response, source}

Problem: Drei verschiedene Result-Formate.
Solution: Unified ExecutionResult type.
```

### BREAK 6: Async/Await Inconsistency
```
ActionHandler.execute() is async
BUT some handlers do sync operations
AND some do await asyncio.sleep()

Problem: Mixed sync/async boundaries.
Solution: All handlers are async. Period.
```

### BREAK 7: Three State Tracking Systems
```
EnvoySync:             pending_tasks, request_history
DeterministicExecutor: .playbook_state/ persistence
EnvoyCartridge:        operation_log

Problem: Kein single source of truth.
Solution: One RequestLifecycle manager.
```

### BREAK 8: MilkOcean Status Codes Undocumented
```
status="routing"  → Execute
status="queued"   → Background
status="blocked"  → Veto
status="critical" → GAJENDRA PROTOCOL (creates new task!)

Problem: Magic strings, no documentation.
Solution: Enum with clear semantics.
```

---

## Die Lösung: Unified Execution Model

### Phase 1: Request Object
```python
@dataclass
class ExecutionRequest:
    """Single source of truth for a request."""
    request_id: str
    user_input: str
    source: str  # "envoy.md", "api", "agent"

    # Routing decision (made ONCE)
    execution_path: Literal["circuit", "playbook", "fast_command"]
    target_id: str  # Circuit ID or Playbook ID

    # Runtime state
    status: Literal["pending", "routing", "executing", "completed", "failed"]
    phase_results: Dict[str, Any]

    # Lifecycle
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
```

### Phase 2: Single Router
```python
class UnifiedRouter:
    """One router to rule them all."""

    def route(self, user_input: str) -> ExecutionRequest:
        """
        Decide execution path AT ROUTING TIME.

        Returns ExecutionRequest with:
        - execution_path: "circuit" | "playbook" | "fast_command"
        - target_id: The circuit/playbook to execute
        """
        # 1. Check fast commands first
        if self._is_fast_command(user_input):
            return ExecutionRequest(
                execution_path="fast_command",
                target_id=self._get_command_name(user_input),
            )

        # 2. Check circuit patterns
        circuit = self._match_circuit(user_input)
        if circuit:
            return ExecutionRequest(
                execution_path="circuit",
                target_id=circuit.id,
            )

        # 3. Fall back to playbook
        playbook = self._match_playbook(user_input)
        return ExecutionRequest(
            execution_path="playbook",
            target_id=playbook.id if playbook else "SIMPLE_QUERY",
        )
```

### Phase 3: Unified Executor
```python
class UnifiedExecutor:
    """Execute based on routing decision."""

    def __init__(self, kernel):
        # Eager initialization - NO lazy loading!
        self.circuit_executor = CircuitExecutor(kernel)
        self.playbook_executor = PlaybookExecutor(kernel)
        self.command_executor = CommandExecutor(kernel)

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute based on pre-determined path."""
        request.status = "executing"
        request.started_at = time.time()

        try:
            if request.execution_path == "fast_command":
                result = await self.command_executor.execute(request)
            elif request.execution_path == "circuit":
                result = await self.circuit_executor.execute(request)
            else:
                result = await self.playbook_executor.execute(request)

            request.status = "completed"
            return result

        except Exception as e:
            request.status = "failed"
            raise

        finally:
            request.completed_at = time.time()
```

### Phase 4: Template Context Flow
```python
class PlaybookExecutor:
    """Execute playbook with proper context flow."""

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        playbook = self.loader.get(request.target_id)

        for phase in playbook.phases:
            # CRITICAL: Rebuild context BEFORE each phase!
            context = self._build_context(request)

            # Execute phase with fresh context
            result = await self._execute_phase(phase, context)

            # Store result for next phase
            if phase.state_var:
                request.phase_results[phase.state_var] = result

        return ExecutionResult(
            status="completed",
            response=request.phase_results.get("rendered", {}).get("rendered", ""),
        )

    def _build_context(self, request: ExecutionRequest) -> Dict[str, Any]:
        """Build fresh context with ALL phase results."""
        context = {
            "user_input": request.user_input,
            "request_id": request.request_id,
        }

        # Flatten phase_results for template access
        for var_name, result in request.phase_results.items():
            context[var_name] = result

        return context
```

---

## Migration Plan

### Step 1: Create ExecutionRequest (Non-Breaking)
- Add `ExecutionRequest` dataclass
- Use it in new code, don't change existing

### Step 2: Unify Router (Breaking)
- Replace PlaybookRouter + MilkOceanRouter
- MilkOcean becomes a GATE (pre-routing check)
- Router returns ExecutionRequest

### Step 3: Fix Template Context (Critical)
- Rebuild context before each phase
- This fixes BREAK 3 immediately

### Step 4: Eager Initialization
- Initialize all executors at plugin boot
- No more lazy loading

### Step 5: Unified Result Format
- All executors return ExecutionResult
- Remove format conversion in EnvoyCartridge

---

## Immediate Fix: Template Context

Das kritischste Problem jetzt ist BREAK 3. Der Fix:

```python
# deterministic_executor.py, line 738-740

# BEFORE (broken):
template_context = self._build_template_context(playbook, execution, intent_vector)
for action in phase.actions:
    # ... uses stale template_context

# AFTER (fixed):
for action in phase.actions:
    # Rebuild context EVERY action to get fresh phase_results
    template_context = self._build_template_context(playbook, execution, intent_vector)
    # ... uses fresh template_context
```

---

## Verification Test

Nach dem Fix sollte dieser Test funktionieren:

```python
def test_circuit_status_renders_output():
    kernel = RealVibeKernel(ledger_path=':memory:')
    kernel.boot()

    result = kernel.envoy.execute_circuit(
        'SYSTEM_STATUS_V2',
        params={'user_input': 'status'}
    )

    assert result['status'] == 'COMPLETED'

    # Check rendered output is NOT empty
    rendered = result['details'].get('rendered', {}).get('rendered', '')
    assert len(rendered) > 0, "Template should produce output"
    assert "Agent City" in rendered, "Template should render city name"
```

---

## Summary

| Problem | Root Cause | Fix |
|---------|------------|-----|
| Dual routing | Two routers | One UnifiedRouter |
| Path uncertainty | Late decision | Route-time decision |
| Template stale | Context built once | Rebuild per phase |
| Race conditions | Lazy init | Eager init at boot |
| Result mismatch | Three formats | One ExecutionResult |
| Async mess | Mixed boundaries | All async |
| State chaos | Three systems | One RequestLifecycle |
| Magic strings | Undocumented | Enum with docs |

**Nächster Schritt:** Fix BREAK 3 (Template Context) - das ist der minimale Fix der sofort funktioniert.

---

## IMMEDIATE ACTION PLAN

### Was wir JETZT tun (Minimal Viable Fix)

**Ziel:** SYSTEM_STATUS_V2 circuit soll funktionieren.

**Problem:** Template Context ist stale - Phase 4 (render_output) kann Phase 1-3 Ergebnisse nicht sehen.

**Fix:** In `_execute_phase_actions()`, Context vor JEDER Action neu bauen.

**File:** `vibe_core/cartridges/system/envoy/deterministic_executor.py`
**Line:** ~739

**Change:**
```python
# Move this line INSIDE the for loop
template_context = self._build_template_context(playbook, execution, intent_vector)
```

**Effort:** 5 Minuten

**Risk:** Gering - nur Timing der Context-Erstellung

---

### Was wir SPÄTER tun (Refactoring)

| Phase | Aufwand | Breaking? | Beschreibung |
|-------|---------|-----------|--------------|
| 1. ExecutionRequest | 2h | Nein | Neuer Datentyp, parallel einführen |
| 2. UnifiedRouter | 4h | JA | Ersetzt PlaybookRouter + MilkOcean |
| 3. Eager Init | 1h | Nein | Executors beim Boot initialisieren |
| 4. ExecutionResult | 2h | JA | Einheitliches Result-Format |
| 5. Cleanup | 2h | Nein | Dead code entfernen |

**Gesamt:** ~11h Arbeit für komplettes Refactoring

---

### Was wir NICHT anfassen

1. **Kernel** - DER KERNEL IST ETERNAL
2. **Ledger** - Immutable by design
3. **Parampara** - Hash-Chain darf nicht brechen
4. **Agent Registry** - Funktioniert bereits

---

## Decision Required

**Frage an User:**

Soll ich jetzt:

**A)** Nur den Minimal Fix machen (5 min) → Template Context in der Loop neu bauen

**B)** Das volle Refactoring starten (11h) → ExecutionRequest + UnifiedRouter + etc.

**C)** Erst den Minimal Fix, dann inkrementell refactoren

Option C ist wahrscheinlich am sinnvollsten - erst zeigen dass es funktioniert, dann aufräumen.
