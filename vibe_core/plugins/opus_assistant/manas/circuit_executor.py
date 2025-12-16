"""
OPUS-083: CognitiveCircuitExecutor - The Hand of MANAS.

This is the bridge from thought to action.
MANAS generates intents with `circuit_to_execute`.
This executor runs those circuits WITHOUT requiring full kernel boot.

Architecture:
    CognitiveKernel (Brain)
           │
           ▼
    CognitiveCircuitExecutor (Hand)
           │
           ▼
    Action Handlers (Fingers)

Philosophy:
    An intent without execution is a hallucination.
    A circuit without a runner is dead code.
    This makes both real.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

logger = logging.getLogger("MANAS.CIRCUIT_EXECUTOR")


class CognitiveCircuitExecutor:
    """
    Headless circuit runner for MANAS.

    Executes YAML circuits WITHOUT requiring full kernel boot.
    This is the bridge from thought (Intent) to action (file changes, events).

    Usage:
        executor = CognitiveCircuitExecutor(workspace)
        result = executor.execute_circuit("maintenance_pulse")

    The executor:
    1. Loads circuit YAML definition
    2. Walks the state machine
    3. Dispatches actions to handlers
    4. Returns aggregated results
    """

    def __init__(self, workspace: Path):
        """
        Initialize circuit executor.

        Args:
            workspace: Project root directory
        """
        self._workspace = workspace
        self._circuits_dir = workspace / "vibe_core" / "plugins" / "opus_assistant" / "circuits"
        self._action_handlers = self._build_action_handlers()
        logger.info("⚡ CognitiveCircuitExecutor initialized")

    def execute_circuit(self, circuit_name: str) -> Dict[str, Any]:
        """
        Execute a circuit by name.

        Args:
            circuit_name: Name of circuit (e.g., "maintenance_pulse")

        Returns:
            Execution result with success/failure and details
        """
        logger.info(f"🔄 Executing circuit: {circuit_name}")

        circuit = self._load_circuit(circuit_name)
        if not circuit:
            error = f"Circuit not found: {circuit_name}"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error}

        try:
            result = self._run_state_machine(circuit)
            logger.info(f"✅ Circuit {circuit_name} completed: {result.get('states_executed', 0)} states")
            return result
        except Exception as e:
            error = f"Circuit execution failed: {e}"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error}

    def _load_circuit(self, name: str) -> Optional[Dict]:
        """
        Load circuit YAML definition.

        Args:
            name: Circuit name (without .yaml extension)

        Returns:
            Parsed circuit dict or None if not found
        """
        path = self._circuits_dir / f"{name}.yaml"
        if not path.exists():
            logger.warning(f"Circuit file not found: {path}")
            return None

        try:
            return yaml.safe_load(path.read_text())
        except Exception as e:
            logger.error(f"Failed to parse circuit {name}: {e}")
            return None

    def _run_state_machine(self, circuit: Dict) -> Dict[str, Any]:
        """
        Execute circuit state machine.

        Walks through states, executes actions, follows transitions.

        Args:
            circuit: Parsed circuit definition

        Returns:
            Execution result
        """
        circuit_def = circuit.get("circuit", {})
        entry_state = circuit_def.get("entry_state")
        states = circuit_def.get("states", {})

        if not entry_state or not states:
            return {"success": False, "error": "Invalid circuit: missing entry_state or states"}

        current_state = entry_state
        results: List[Dict[str, Any]] = []
        state_vars: Dict[str, Any] = {}
        states_visited = 0
        max_states = 50  # Prevent infinite loops

        while current_state and current_state in states and states_visited < max_states:
            states_visited += 1
            state_def = states[current_state]
            logger.debug(f"  → State: {current_state}")

            # Execute actions
            for action in state_def.get("actions", []):
                action_result = self._dispatch_action(action, state_vars)
                results.append(action_result)

                # Store result in state_var if specified
                state_var = state_def.get("state_var")
                if state_var:
                    state_vars[state_var] = action_result

            # Check for terminal state
            if state_def.get("terminal"):
                logger.debug(f"  → Terminal state reached: {current_state}")
                break

            # Evaluate transitions
            next_state = self._evaluate_transitions(state_def.get("transitions", []), state_vars)
            current_state = next_state

        return {
            "success": True,
            "states_executed": states_visited,
            "results": results,
            "final_state": current_state,
            "state_vars": state_vars,
        }

    def _evaluate_transitions(self, transitions: List[Dict], state_vars: Dict[str, Any]) -> Optional[str]:
        """
        Evaluate transitions and return next state.

        For now: takes first transition (condition evaluation TBD).
        This is simplified - full condition eval would need expression parser.

        Args:
            transitions: List of transition definitions
            state_vars: Current state variables

        Returns:
            Next state name or None
        """
        if not transitions:
            return None

        # Simplified: take first transition
        # TODO: Implement condition evaluation
        return transitions[0].get("to")

    def _dispatch_action(self, action: Dict, state_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch action to appropriate handler.

        Args:
            action: Action definition
            state_vars: Current state variables (for template substitution)

        Returns:
            Action result
        """
        action_type = action.get("action_type")
        handler = self._action_handlers.get(action_type)

        if handler:
            try:
                return handler(action, state_vars)
            except Exception as e:
                return {"success": False, "error": str(e), "action_type": action_type}

        return {"success": False, "error": f"Unknown action type: {action_type}"}

    def _build_action_handlers(self) -> Dict[str, Callable]:
        """Build action handler map."""
        return {
            "EMIT_EVENT": self._handle_emit_event,
            "EXECUTE_SCRIPT": self._handle_execute_script,
            "LOG": self._handle_log,
        }

    # =========================================================================
    # ACTION HANDLERS
    # =========================================================================

    def _handle_emit_event(self, action: Dict, state_vars: Dict) -> Dict[str, Any]:
        """
        Handle EMIT_EVENT action.

        Logs the event. In future, could publish to EventBus.
        """
        target = action.get("target", "unknown")
        params = action.get("params", {})
        logger.info(f"🔔 CIRCUIT EVENT: {target}")
        return {"success": True, "event": target, "params": params}

    def _handle_execute_script(self, action: Dict, state_vars: Dict) -> Dict[str, Any]:
        """
        Handle EXECUTE_SCRIPT action.

        Dispatches to known script handlers based on target.
        """
        target = action.get("target", "")
        params = action.get("params", {})

        # Dispatch to known script handlers
        script_handlers = {
            "opus.write_opus_md": self._script_write_opus_md,
            "opus.check_opus_freshness": self._script_check_opus_freshness,
            "opus.quick_drift_check": self._script_quick_drift_check,
            "opus.log_observation": self._script_log_observation,
            "opus.detect_drift": self._script_detect_drift,
        }

        handler = script_handlers.get(target)
        if handler:
            return handler(params)

        logger.warning(f"Unknown script target: {target}")
        return {"success": False, "error": f"Unknown script: {target}"}

    def _handle_log(self, action: Dict, state_vars: Dict) -> Dict[str, Any]:
        """Handle LOG action."""
        message = action.get("message", "")
        level = action.get("level", "INFO")
        logger.log(getattr(logging, level, logging.INFO), f"📝 CIRCUIT: {message}")
        return {"success": True}

    # =========================================================================
    # SCRIPT HANDLERS
    # =========================================================================

    def _script_write_opus_md(self, params: Dict) -> Dict[str, Any]:
        """
        Write OPUS.md via OpusDashboardRenderer.

        This is THE critical script - closes the heartbeat→OPUS.md loop.
        """
        try:
            from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
                OpusDashboardRenderer,
            )

            renderer = OpusDashboardRenderer(self._workspace, kernel=None)
            content = renderer.render(quick=params.get("quick", True))

            opus_path = self._workspace / "OPUS.md"
            opus_path.write_text(content)

            logger.info(f"📋 OPUS.md refreshed ({len(content)} bytes)")
            return {"success": True, "file": "OPUS.md", "bytes": len(content)}

        except Exception as e:
            logger.error(f"Failed to write OPUS.md: {e}")
            return {"success": False, "error": str(e)}

    def _script_check_opus_freshness(self, params: Dict) -> Dict[str, Any]:
        """Check if OPUS.md is stale."""
        import time

        opus_path = self._workspace / "OPUS.md"
        if not opus_path.exists():
            return {"success": True, "opus_stale": True, "reason": "OPUS.md does not exist"}

        mtime = opus_path.stat().st_mtime
        age_minutes = (time.time() - mtime) / 60
        threshold = params.get("stale_threshold_minutes", 60)

        is_stale = age_minutes > threshold
        return {
            "success": True,
            "opus_stale": is_stale,
            "age_minutes": int(age_minutes),
            "threshold": threshold,
        }

    def _script_quick_drift_check(self, params: Dict) -> Dict[str, Any]:
        """Run quick drift check."""
        # Simplified drift check - just verify key files exist
        key_files = [
            "OPUS.md",
            "vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py",
            "scripts/heartbeat.py",
        ]

        missing = [f for f in key_files if not (self._workspace / f).exists()]

        return {
            "success": True,
            "drift_detected": len(missing) > 0,
            "missing_files": missing,
        }

    def _script_log_observation(self, params: Dict) -> Dict[str, Any]:
        """Log observation."""
        severity = params.get("severity", "INFO")
        message = params.get("message", "")
        source = params.get("source", "circuit")

        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, f"[{source}] {message}")

        return {"success": True, "logged": True}

    def _script_detect_drift(self, params: Dict) -> Dict[str, Any]:
        """Detect drift between code and docs."""
        # Placeholder - full implementation would analyze code/doc alignment
        return {"success": True, "drift_detected": False, "note": "Full drift detection TBD"}
