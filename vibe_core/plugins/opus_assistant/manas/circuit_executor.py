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

        Supports basic condition patterns:
        - "variable == true" / "variable == false"
        - "variable == 'string_value'"
        - "variable.attribute == value"
        - "true" (always matches)
        - No condition (always matches)

        Args:
            transitions: List of transition definitions
            state_vars: Current state variables

        Returns:
            Next state name or None
        """
        if not transitions:
            return None

        for transition in transitions:
            condition = transition.get("condition")

            # No condition = always take this transition
            if not condition:
                return transition.get("to")

            # Evaluate the condition
            if self._evaluate_condition(condition, state_vars):
                return transition.get("to")

        # No matching transition - take first as fallback (legacy behavior)
        logger.warning("No condition matched, falling back to first transition")
        return transitions[0].get("to")

    def _evaluate_condition(self, condition: str, state_vars: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string against state variables.

        Supports:
        - "true" → always True
        - "false" → always False
        - "var == true" / "var == false"
        - "var == 'string'"
        - "var.attr == value"
        - "not var.attr"

        Args:
            condition: Condition string to evaluate
            state_vars: Current state variables

        Returns:
            Boolean result of condition evaluation
        """
        import re

        condition = condition.strip()

        # Handle "true" / "false" literals
        if condition.lower() == "true":
            return True
        if condition.lower() == "false":
            return False

        # Handle Jinja-style {{ variable }} - extract inner part
        jinja_match = re.match(r"\{\{\s*(.+?)\s*\}\}", condition)
        if jinja_match:
            condition = jinja_match.group(1)

        # Handle "not variable.attribute"
        if condition.startswith("not "):
            inner = condition[4:].strip()
            return not self._evaluate_condition(inner, state_vars)

        # Handle equality: "var == value" or "var.attr == value"
        eq_match = re.match(r"(.+?)\s*==\s*(.+)", condition)
        if eq_match:
            left = eq_match.group(1).strip()
            right = eq_match.group(2).strip()

            # Resolve both sides (handles variables, numbers, strings, booleans)
            left_val = self._resolve_value(left, state_vars)
            right_val = self._resolve_value(right, state_vars)

            return left_val == right_val

        # Handle inequality: "var < value" or "var >= value"
        # Order matters: check >= and <= before > and < to avoid partial matches
        ineq_patterns = [
            (r"(.+?)\s*<=\s*(.+)", lambda a, b: a <= b),
            (r"(.+?)\s*>=\s*(.+)", lambda a, b: a >= b),
            (r"(.+?)\s*<\s*(.+)", lambda a, b: a < b),
            (r"(.+?)\s*>\s*(.+)", lambda a, b: a > b),
        ]
        for pattern, op in ineq_patterns:
            match = re.match(pattern, condition)
            if match:
                left = self._resolve_value(match.group(1).strip(), state_vars)
                right = self._resolve_value(match.group(2).strip(), state_vars)
                try:
                    return op(left, right)
                except (TypeError, ValueError):
                    return False

        # Fallback: treat as truthy check on variable
        val = self._resolve_var(condition, state_vars)
        return bool(val)

    def _resolve_value(self, value_str: str, state_vars: Dict[str, Any]) -> Any:
        """
        Resolve a value - either a literal (number, string, boolean) or a variable path.

        Args:
            value_str: Value string (e.g., "42", "true", "result.count", "'string'")
            state_vars: State variables dict

        Returns:
            Resolved value
        """
        value_str = value_str.strip()

        # Check for boolean literals first
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Try to parse as integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Check for quoted string
        if (value_str.startswith("'") and value_str.endswith("'")) or (
            value_str.startswith('"') and value_str.endswith('"')
        ):
            return value_str[1:-1]

        # Try to resolve as variable path
        return self._resolve_var(value_str, state_vars)

    def _resolve_var(self, var_path: str, state_vars: Dict[str, Any]) -> Any:
        """
        Resolve a variable path like "result.success" from state_vars.

        Args:
            var_path: Dot-separated path like "result.success"
            state_vars: State variables dict

        Returns:
            Resolved value or None if not found
        """
        parts = var_path.split(".")
        current = state_vars

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None

            if current is None:
                return None

        return current

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
            "opus.generate_harness": self._script_generate_harness,
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

    def _script_generate_harness(self, params: Dict) -> Dict[str, Any]:
        """
        Auto-generate @HARNESS for OPUS documentation files.

        This is the SELF-HEALING capability of MANAS.
        Given an OPUS file and module name, generates a proper harness
        based on the actual code structure.

        Args:
            params:
                opus_file: Path to the OPUS markdown file
                module_name: Name of the cortex module (e.g., "veda")

        Returns:
            Result dict with success status and details
        """
        opus_file = params.get("opus_file")
        module_name = params.get("module_name")

        if not opus_file or not module_name:
            return {"success": False, "error": "Missing opus_file or module_name"}

        opus_path = Path(opus_file) if not isinstance(opus_file, Path) else opus_file
        if not opus_path.is_absolute():
            opus_path = self._workspace / opus_file

        if not opus_path.exists():
            return {"success": False, "error": f"OPUS file not found: {opus_path}"}

        try:
            # Find the module file - search multiple locations (OPUS-054 DNA Folding)
            search_paths = [
                self._workspace / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "cortex" / f"{module_name}.py",
                self._workspace / "vibe_core" / "plugins" / "opus_assistant" / "manas" / f"{module_name}.py",
                self._workspace / "vibe_core" / f"{module_name}.py",
                self._workspace / "vibe_core" / f"{module_name}_orchestrator.py",
                self._workspace / "vibe_core" / "plugins" / f"{module_name}" / "plugin_main.py",
                self._workspace / "vibe_core" / "state" / f"{module_name}.py",
                self._workspace / "vibe_core" / "steward" / f"{module_name}.py",
            ]

            module_path = None
            for path in search_paths:
                if path.exists():
                    module_path = path
                    break

            if not module_path:
                # Try glob search as last resort
                for pattern in [f"**/{module_name}.py", f"**/{module_name}_*.py"]:
                    matches = list(self._workspace.glob(pattern))
                    matches = [m for m in matches if "__pycache__" not in str(m) and "test" not in str(m)]
                    if matches:
                        module_path = matches[0]
                        break

            if not module_path:
                return {"success": False, "error": f"Module not found for: {module_name}"}

            # Find test file if exists - search multiple locations
            test_search_paths = [
                self._workspace / "tests" / "manas" / f"test_{module_name}.py",
                self._workspace / "tests" / "unit" / f"test_{module_name}.py",
                self._workspace / "tests" / "integration" / f"test_{module_name}.py",
                self._workspace / "tests" / f"test_{module_name}.py",
            ]
            test_path = None
            for tp in test_search_paths:
                if tp.exists():
                    test_path = tp
                    break
            has_test = test_path is not None

            # Analyze module for key patterns
            module_content = module_path.read_text()
            classes = self._extract_classes(module_content)
            key_methods = self._extract_key_methods(module_content)

            # Generate harness content
            harness = self._build_harness(
                module_name=module_name,
                module_rel_path=str(module_path.relative_to(self._workspace)),
                test_rel_path=str(test_path.relative_to(self._workspace)) if has_test else None,
                classes=classes,
                methods=key_methods,
            )

            # Read existing content and inject harness
            existing_content = opus_path.read_text()

            # Check if already has harness
            if "<!-- @HARNESS" in existing_content:
                return {"success": False, "error": "File already has @HARNESS", "skipped": True}

            # Find insertion point (after first header or at end)
            lines = existing_content.split("\n")
            insert_idx = len(lines)

            for i, line in enumerate(lines):
                if line.startswith("# ") and i > 0:
                    # Insert before second header
                    insert_idx = i
                    break
                elif line.startswith("---") and i > 2:
                    # Insert before first horizontal rule (after intro)
                    insert_idx = i
                    break

            # Insert harness
            lines.insert(insert_idx, "\n" + harness + "\n")
            new_content = "\n".join(lines)

            # Write back
            opus_path.write_text(new_content)

            logger.info(f"✅ Generated harness for {opus_path.name}")
            return {
                "success": True,
                "file": str(opus_path),
                "module": module_name,
                "classes_found": len(classes),
                "methods_found": len(key_methods),
                "has_test": has_test,
            }

        except Exception as e:
            logger.error(f"Failed to generate harness: {e}")
            return {"success": False, "error": str(e)}

    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python module."""
        import re

        matches = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        return matches

    def _extract_key_methods(self, content: str) -> List[str]:
        """Extract key public method names (not private/dunder)."""
        import re

        matches = re.findall(r"^\s+def\s+([a-z][a-z0-9_]*)\s*\(", content, re.MULTILINE)
        # Filter out private methods
        return [m for m in matches if not m.startswith("_")][:10]  # Limit to 10

    def _build_harness(
        self,
        module_name: str,
        module_rel_path: str,
        test_rel_path: Optional[str],
        classes: List[str],
        methods: List[str],
    ) -> str:
        """Build the @HARNESS block content."""
        harness_lines = [
            "<!-- @HARNESS",
            "files:",
            f"  - path: {module_rel_path}",
            "    required: true",
        ]

        if test_rel_path:
            harness_lines.extend(
                [
                    "",
                    "tests:",
                    f"  - {test_rel_path}",
                ]
            )

        if classes:
            harness_lines.extend(
                [
                    "",
                    "semantic:",
                ]
            )
            for cls in classes[:3]:  # Max 3 classes
                harness_lines.extend(
                    [
                        "  - type: class_exists",
                        f"    name: {module_name}_{cls.lower()}",
                        f"    in: {module_rel_path}",
                        f"    class: {cls}",
                    ]
                )

        if methods:
            if not classes:
                harness_lines.extend(
                    [
                        "",
                        "wiring:",
                    ]
                )
            else:
                harness_lines.append("")
                harness_lines.append("wiring:")

            for method in methods[:5]:  # Max 5 methods
                harness_lines.extend(
                    [
                        f'  - pattern: "def {method}"',
                        f"    in: {module_rel_path}",
                    ]
                )

        harness_lines.append("-->")

        return "\n".join(harness_lines)
