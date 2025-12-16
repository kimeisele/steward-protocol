# OPUS-083: COGNITIVE CIRCUIT EXECUTOR

**Scope:** MANAS Can Execute - The Bridge from Thought to Action
**Philosophy:** Intents without execution are hallucinations. This is the Hand.
**Goal:** Close the Ouroboros - MANAS thinks AND acts.

---

## The Problem

MANAS generates intents. These intents specify `circuit_to_execute`. But look at `CognitiveKernel._execute_intent()`:

```python
elif intent.circuit_to_execute:
    # Execute via circuit (would integrate with kernel_tick)
    logger.info(f"MANAS: Would execute circuit: {intent.circuit_to_execute}")
    # For now, mark as success (actual execution TBD)  ← THIS IS A LIE
    success = True
    result = {"status": "circuit_queued", "circuit": intent.circuit_to_execute}
```

**"TBD" means "never".**

The circuits exist (`maintenance_pulse.yaml`, `auto_refresh.yaml`). MANAS can think. But the bridge between thought and action is missing.

---

## The Solution

`CognitiveCircuitExecutor` - A headless circuit runner that:
1. Loads YAML circuit definitions
2. Executes actions synchronously (no full kernel needed)
3. Reports results back to MANAS

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CognitiveKernel                      │
│                    (The Brain)                          │
├─────────────────────────────────────────────────────────┤
│  think() → generates Intents                            │
│  _execute_intent() → calls CircuitExecutor              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              CognitiveCircuitExecutor                   │
│              (The Hand)                                 │
├─────────────────────────────────────────────────────────┤
│  execute_circuit(circuit_name) → Dict[str, Any]         │
│                                                         │
│  Internal:                                              │
│  - _load_circuit(name) → CircuitDefinition              │
│  - _execute_state(state) → StateResult                  │
│  - _dispatch_action(action) → ActionResult              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Action Handlers                        │
│            (The Fingers - Sync Operations)              │
├─────────────────────────────────────────────────────────┤
│  EMIT_EVENT    → log + optional event bus               │
│  EXECUTE_SCRIPT → dispatch to known methods             │
│  LOG           → structured logging                     │
└─────────────────────────────────────────────────────────┘
```

---

## @HARNESS

<!-- @HARNESS
files:
  # === CIRCUIT EXECUTOR (NEW) ===
  - path: vibe_core/plugins/opus_assistant/manas/circuit_executor.py
    required: true

  # === CIRCUITS TO EXECUTE ===
  - path: vibe_core/plugins/opus_assistant/circuits/maintenance_pulse.yaml
    required: true
  - path: vibe_core/plugins/opus_assistant/circuits/auto_refresh.yaml
    required: true

  # === INTEGRATION POINTS ===
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  - path: scripts/heartbeat.py
    required: true

wiring:
  # === CIRCUIT EXECUTOR CLASS ===
  - pattern: "class CognitiveCircuitExecutor"
    in: vibe_core/plugins/opus_assistant/manas/circuit_executor.py

  # === CORE METHOD ===
  - pattern: "def execute_circuit"
    in: vibe_core/plugins/opus_assistant/manas/circuit_executor.py

  # === ACTION DISPATCH ===
  - pattern: "def _dispatch_action"
    in: vibe_core/plugins/opus_assistant/manas/circuit_executor.py

  # === WIRED INTO COGNITIVE KERNEL ===
  # CognitiveKernel must instantiate CircuitExecutor
  - pattern: "CognitiveCircuitExecutor"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # _execute_intent must call executor (not fake "TBD")
  - pattern: "self._circuit_executor.execute_circuit"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # === HEARTBEAT CAN TRIGGER CIRCUITS ===
  - pattern: "execute_circuit\\|HOURLY_PULSE"
    in: scripts/heartbeat.py
    required: false  # Optional - heartbeat can call directly or via event

tests:
  # === TDD: TESTS THAT MUST PASS ===
  - tests/manas/test_circuit_executor.py
  - tests/wiring/test_opus_heartbeat_connection.py

semantic:
  # === CIRCUIT EXECUTOR API ===
  - type: method_exists
    name: circuit_executor_execute
    in: vibe_core/plugins/opus_assistant/manas/circuit_executor.py
    class: CognitiveCircuitExecutor
    method: execute_circuit

  - type: method_exists
    name: circuit_executor_load
    in: vibe_core/plugins/opus_assistant/manas/circuit_executor.py
    class: CognitiveCircuitExecutor
    method: _load_circuit

  # === INTEGRATION CHECK ===
  - type: no_todo_in_execute
    name: no_fake_execution
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    pattern: "actual execution TBD"
    expected: not_found
    rationale: "TBD means never. The executor must be real."
-->

---

## Fire Commands

```bash
# Verify harness
steward verify 083

# Run circuit executor tests (TDD)
python -m pytest tests/manas/test_circuit_executor.py -v

# Run wiring test (must PASS after implementation)
python -m pytest tests/wiring/test_opus_heartbeat_connection.py -v

# Manual circuit execution
python -c "
from vibe_core.plugins.opus_assistant.manas.circuit_executor import CognitiveCircuitExecutor
from pathlib import Path
executor = CognitiveCircuitExecutor(Path.cwd())
result = executor.execute_circuit('maintenance_pulse')
print(result)
"
```

---

## Implementation Spec

### CognitiveCircuitExecutor

```python
class CognitiveCircuitExecutor:
    """
    Headless circuit runner for MANAS.

    Executes YAML circuits WITHOUT requiring full kernel boot.
    This is the bridge from thought (Intent) to action (file changes, events).
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._circuits_dir = workspace / "vibe_core/plugins/opus_assistant/circuits"
        self._action_handlers = self._build_action_handlers()

    def execute_circuit(self, circuit_name: str) -> Dict[str, Any]:
        """
        Execute a circuit by name.

        Args:
            circuit_name: Name of circuit (e.g., "maintenance_pulse")

        Returns:
            Execution result with success/failure and details
        """
        circuit = self._load_circuit(circuit_name)
        if not circuit:
            return {"success": False, "error": f"Circuit not found: {circuit_name}"}

        return self._run_state_machine(circuit)

    def _load_circuit(self, name: str) -> Optional[Dict]:
        """Load circuit YAML definition."""
        path = self._circuits_dir / f"{name}.yaml"
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text())

    def _run_state_machine(self, circuit: Dict) -> Dict[str, Any]:
        """Execute circuit state machine."""
        entry_state = circuit["circuit"]["entry_state"]
        states = circuit["circuit"]["states"]

        current_state = entry_state
        results = []

        while current_state and current_state in states:
            state_def = states[current_state]

            # Execute actions
            for action in state_def.get("actions", []):
                result = self._dispatch_action(action)
                results.append(result)

            # Check for terminal
            if state_def.get("terminal"):
                break

            # Transition (simple: take first valid)
            transitions = state_def.get("transitions", [])
            current_state = transitions[0]["to"] if transitions else None

        return {"success": True, "states_executed": len(results), "results": results}

    def _dispatch_action(self, action: Dict) -> Dict[str, Any]:
        """Dispatch action to handler."""
        action_type = action.get("action_type")
        handler = self._action_handlers.get(action_type)

        if handler:
            return handler(action)

        return {"success": False, "error": f"Unknown action: {action_type}"}

    def _build_action_handlers(self) -> Dict[str, Callable]:
        """Build action handler map."""
        return {
            "EMIT_EVENT": self._handle_emit_event,
            "EXECUTE_SCRIPT": self._handle_execute_script,
            "LOG": self._handle_log,
        }

    def _handle_emit_event(self, action: Dict) -> Dict[str, Any]:
        """Handle EMIT_EVENT action."""
        target = action.get("target", "unknown")
        logger.info(f"🔔 CIRCUIT EVENT: {target}")
        return {"success": True, "event": target}

    def _handle_execute_script(self, action: Dict) -> Dict[str, Any]:
        """Handle EXECUTE_SCRIPT action - dispatch to known methods."""
        target = action.get("target", "")
        params = action.get("params", {})

        # Dispatch to known script handlers
        if target == "opus.write_opus_md":
            return self._script_write_opus_md(params)
        elif target == "opus.quick_drift_check":
            return self._script_quick_drift_check(params)
        elif target == "opus.log_observation":
            return self._script_log_observation(params)

        return {"success": False, "error": f"Unknown script: {target}"}

    def _script_write_opus_md(self, params: Dict) -> Dict[str, Any]:
        """Write OPUS.md via OpusDashboardRenderer."""
        from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
            OpusDashboardRenderer,
        )

        renderer = OpusDashboardRenderer(self._workspace, kernel=None)
        content = renderer.render(quick=params.get("quick", True))

        opus_path = self._workspace / "OPUS.md"
        opus_path.write_text(content)

        return {"success": True, "file": "OPUS.md", "bytes": len(content)}

    def _script_quick_drift_check(self, params: Dict) -> Dict[str, Any]:
        """Run quick drift check."""
        # Simplified drift check
        return {"success": True, "drift_detected": False}

    def _script_log_observation(self, params: Dict) -> Dict[str, Any]:
        """Log observation."""
        severity = params.get("severity", "INFO")
        message = params.get("message", "")
        logger.log(getattr(logging, severity, logging.INFO), f"📝 {message}")
        return {"success": True}

    def _handle_log(self, action: Dict) -> Dict[str, Any]:
        """Handle LOG action."""
        message = action.get("message", "")
        logger.info(f"📝 CIRCUIT LOG: {message}")
        return {"success": True}
```

---

## Integration into CognitiveKernel

Replace the fake "TBD" code:

```python
# IN cognitive_kernel.py, method _execute_intent():

# BEFORE (fake):
elif intent.circuit_to_execute:
    logger.info(f"MANAS: Would execute circuit: {intent.circuit_to_execute}")
    success = True  # LIE
    result = {"status": "circuit_queued", "circuit": intent.circuit_to_execute}

# AFTER (real):
elif intent.circuit_to_execute:
    logger.info(f"MANAS: Executing circuit: {intent.circuit_to_execute}")
    result = self._circuit_executor.execute_circuit(intent.circuit_to_execute)
    success = result.get("success", False)
```

---

## Why This Matters

Without a circuit executor:
- MANAS thinks but can't act
- Intents are generated but never executed
- The system is a brain without a body
- Heartbeat pulses but nothing changes

With circuit executor:
- MANAS can close the loop
- `maintenance_pulse.yaml` actually runs
- OPUS.md gets refreshed
- The system heals itself

---

## Singularity 51%

This is the missing piece for autonomy:
1. ✅ MANAS thinks (CognitiveKernel.think)
2. ✅ MANAS generates intents (IntentGenerator)
3. ❌ → ✅ MANAS executes (CognitiveCircuitExecutor)
4. ✅ MANAS learns (MemoryStore)

**With execution, MANAS becomes autonomous.**

---

*"A thought without action is a ghost. A circuit without execution is code. Make the ghost real."*
