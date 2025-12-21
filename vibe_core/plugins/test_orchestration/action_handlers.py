"""
TEST VALIDATION ACTION HANDLERS - PANOPTICON+ Nano Agents
=========================================================

Deterministic action handlers for test validation circuit.
Each handler is a "Nano Agent" - a micro-worker that executes
ONE specific action type WITHOUT LLM.

These handlers make the test_validation.yaml circuit EXECUTABLE:
- ast_parse: Parse Python file into AST
- pattern_match: Check patterns against source code
- assertion_analysis: Analyze test assertions
- semantic_analysis: Check test coverage intent
- compile_report: Generate validation report
- enforce: Apply verdict (block/warn/approve)

ARCHITECTURE:
    Circuit YAML → CircuitLoader → DeterministicExecutor → ActionHandlers
                                                              ↓
                                        ast_parse → pattern_match → assertion_analysis
                                                              ↓
                                        compile_report → enforce → VERDICT

NO LLM REQUIRED - Pure AST + Regex + State Machine!
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("TEST_VALIDATION_HANDLERS")


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class ValidationContext:
    """Context for test validation execution."""

    file_path: str
    source: Optional[str] = None
    ast_tree: Optional[ast.AST] = None
    violations: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    state_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandlerResult:
    """Result from a handler execution."""

    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    next_state: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, output: Dict[str, Any], next_state: str) -> "HandlerResult":
        return cls(success=True, output=output, next_state=next_state)

    @classmethod
    def fail(cls, error: str, next_state: str) -> "HandlerResult":
        return cls(success=False, error=error, next_state=next_state)


# =============================================================================
# BASE HANDLER
# =============================================================================


class TestValidationHandler:
    """Base class for test validation action handlers."""

    action_type: str = ""

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        """Execute the handler. Override in subclasses."""
        raise NotImplementedError


# =============================================================================
# AST PARSE HANDLER
# =============================================================================


class AstParseHandler(TestValidationHandler):
    """
    Handler for 'ast_parse' action.
    Parses Python source file into AST.
    """

    action_type = "ast_parse"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        file_path = Path(context.file_path)

        if not file_path.exists():
            return HandlerResult.fail(
                error=f"File not found: {file_path}",
                next_state="report_parse_error",
            )

        try:
            source = file_path.read_text()
            context.source = source
        except Exception as e:
            return HandlerResult.fail(
                error=f"Cannot read file: {e}",
                next_state="report_parse_error",
            )

        try:
            tree = ast.parse(source)
            context.ast_tree = tree
            return HandlerResult.ok(
                output={"ast_tree": "parsed", "line_count": len(source.splitlines())},
                next_state="check_fixtures",
            )
        except SyntaxError as e:
            return HandlerResult.fail(
                error=f"Syntax error at line {e.lineno}: {e.msg}",
                next_state="report_parse_error",
            )


# =============================================================================
# PATTERN MATCH HANDLER
# =============================================================================


class PatternMatchHandler(TestValidationHandler):
    """
    Handler for 'pattern_match' action.
    Checks source code against forbidden/required patterns.
    """

    action_type = "pattern_match"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        if context.source is None:
            return HandlerResult.fail(
                error="No source code available",
                next_state="report_parse_error",
            )

        rules = params.get("rules", [])
        violations = []

        for rule in rules:
            pattern = rule.get("pattern", "")
            required = rule.get("required", False)
            required_when = rule.get("required_when")  # Conditional requirement
            exclude_paths = rule.get("exclude_paths", [])  # Paths to exclude from this rule
            severity = rule.get("severity", "warning")
            message = rule.get("message", "Pattern violation")

            # Check if current file should be excluded from this rule
            if exclude_paths:
                skip_rule = any(excl in context.file_path for excl in exclude_paths)
                if skip_rule:
                    continue

            try:
                # Check if this is a conditional requirement
                if required_when:
                    # Only require pattern if required_when matches
                    if re.search(required_when, context.source):
                        if not re.search(pattern, context.source):
                            violations.append(
                                {
                                    "rule": pattern,
                                    "severity": severity,
                                    "message": message,
                                    "type": "missing_required_conditional",
                                }
                            )
                elif required:
                    # Pattern MUST be present (unconditional)
                    if not re.search(pattern, context.source):
                        violations.append(
                            {
                                "rule": pattern,
                                "severity": severity,
                                "message": message,
                                "type": "missing_required",
                            }
                        )
                else:
                    # Pattern is FORBIDDEN (unless 'without' condition is met)
                    without_pattern = rule.get("without")

                    # If 'without' is specified, only flag if 'without' pattern is NOT present
                    if without_pattern and re.search(without_pattern, context.source):
                        # The 'without' pattern IS present, so this is OK
                        continue

                    matches = list(re.finditer(pattern, context.source))
                    for match in matches:
                        line_num = context.source[: match.start()].count("\n") + 1
                        violations.append(
                            {
                                "rule": pattern,
                                "severity": severity,
                                "message": message,
                                "line": line_num,
                                "type": "forbidden",
                            }
                        )
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")

        context.violations.extend(violations)
        context.state_data["fixture_violations"] = violations

        has_violations = len(violations) > 0
        next_state = "report_violations" if has_violations else "check_assertions"

        return HandlerResult.ok(
            output={"fixture_violations": violations, "count": len(violations)},
            next_state=next_state,
        )


# =============================================================================
# ASSERTION ANALYSIS HANDLER
# =============================================================================


class AssertionAnalysisHandler(TestValidationHandler):
    """
    Handler for 'assertion_analysis' action.
    Analyzes test functions for meaningful assertions.
    """

    action_type = "assertion_analysis"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        if context.ast_tree is None:
            return HandlerResult.fail(
                error="No AST available",
                next_state="report_parse_error",
            )

        # params.get("rules", []) available for future extensibility
        violations = []

        # Find all test functions
        for node in ast.walk(context.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Check: At least one assertion per test
                has_assertion = self._has_assertion(node)
                if not has_assertion:
                    violations.append(
                        {
                            "rule": "assertion_count",
                            "severity": "warning",
                            "message": f"Test '{node.name}' has no assertions",
                            "line": node.lineno,
                            "type": "missing_assertion",
                        }
                    )

                # Check: No assert True
                for child in ast.walk(node):
                    if isinstance(child, ast.Assert):
                        if isinstance(child.test, ast.Constant) and child.test.value is True:
                            violations.append(
                                {
                                    "rule": "assert_true",
                                    "severity": "warning",
                                    "message": "'assert True' is meaningless",
                                    "line": child.lineno,
                                    "type": "meaningless_assertion",
                                }
                            )

        # Check: No bare except: pass
        for node in ast.walk(context.ast_tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None and len(node.body) == 1:
                    if isinstance(node.body[0], ast.Pass):
                        violations.append(
                            {
                                "rule": "except_pass",
                                "severity": "critical",
                                "message": "'except: pass' swallows all errors",
                                "line": node.lineno,
                                "type": "error_swallowing",
                            }
                        )

        context.violations.extend(violations)
        context.state_data["assertion_violations"] = violations

        has_violations = len(violations) > 0
        next_state = "report_violations" if has_violations else "check_coverage_intent"

        return HandlerResult.ok(
            output={"assertion_violations": violations, "count": len(violations)},
            next_state=next_state,
        )

    def _has_assertion(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has any assertion."""
        for child in ast.walk(func_node):
            if isinstance(child, ast.Assert):
                return True
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute):
                    if func.attr in ["raises", "warns", "fail", "assertEqual", "assertTrue"]:
                        return True
                if isinstance(func, ast.Name):
                    if func.id in ["assert_that", "assertEqual", "assertTrue"]:
                        return True
        return False


# =============================================================================
# SEMANTIC ANALYSIS HANDLER
# =============================================================================


class SemanticAnalysisHandler(TestValidationHandler):
    """
    Handler for 'semantic_analysis' action.
    Checks test coverage intent and naming conventions.
    """

    action_type = "semantic_analysis"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        if context.ast_tree is None:
            return HandlerResult.fail(
                error="No AST available",
                next_state="report_parse_error",
            )

        issues = []

        for node in ast.walk(context.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Check: Docstring present
                docstring = ast.get_docstring(node)
                if not docstring:
                    issues.append(
                        {
                            "rule": "docstring_present",
                            "severity": "info",
                            "message": f"Test '{node.name}' missing docstring",
                            "line": node.lineno,
                        }
                    )

                # Check: Descriptive name pattern
                if not re.match(r"test_[a-z]+_[a-z]+", node.name):
                    issues.append(
                        {
                            "rule": "test_name_descriptive",
                            "severity": "info",
                            "message": f"Test name '{node.name}' should describe scenario",
                            "line": node.lineno,
                        }
                    )

        context.state_data["coverage_issues"] = issues

        next_state = "suggest_improvements" if issues else "generate_report"

        return HandlerResult.ok(
            output={"coverage_issues": issues, "count": len(issues)},
            next_state=next_state,
        )


# =============================================================================
# COMPILE REPORT HANDLER
# =============================================================================


class CompileReportHandler(TestValidationHandler):
    """
    Handler for 'compile_report' action.
    Generates the final validation report.
    """

    action_type = "compile_report"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        fixture_violations = context.state_data.get("fixture_violations", [])
        assertion_violations = context.state_data.get("assertion_violations", [])
        coverage_issues = context.state_data.get("coverage_issues", [])

        all_violations = fixture_violations + assertion_violations + coverage_issues
        has_critical = any(v.get("severity") == "critical" for v in all_violations)
        has_warnings = any(v.get("severity") == "warning" for v in all_violations)

        # Build report
        lines = [
            f"# Test Validation Report: {context.file_path}",
            "",
            "## Fixture Compliance",
        ]

        if fixture_violations:
            lines.append("VIOLATIONS FOUND:")
            for v in fixture_violations:
                lines.append(f"- [{v['severity']}] {v['message']} (line {v.get('line', '?')})")
        else:
            lines.append("All fixtures correctly used.")

        lines.extend(["", "## Assertion Quality"])

        if assertion_violations:
            lines.append("ISSUES FOUND:")
            for v in assertion_violations:
                lines.append(f"- [{v['severity']}] {v['message']} (line {v.get('line', '?')})")
        else:
            lines.append("Assertions look good.")

        lines.extend(["", "## Coverage Intent"])

        if coverage_issues:
            lines.append("ISSUES FOUND:")
            for v in coverage_issues:
                lines.append(f"- [{v['severity']}] {v['message']} (line {v.get('line', '?')})")
        else:
            lines.append("Coverage intent verified.")

        if context.suggestions:
            lines.extend(["", "## Suggestions"])
            for s in context.suggestions:
                lines.append(f"- {s}")

        lines.extend(["", "## Verdict"])
        if has_critical:
            lines.append("BLOCKED: Fix critical issues before merge")
            verdict = "blocked"
        elif has_warnings:
            lines.append("WARN: Consider fixing warnings")
            verdict = "warn"
        else:
            lines.append("PASSED: Test meets PANOPTICON+ standards")
            verdict = "passed"

        report = "\n".join(lines)
        context.state_data["validation_report"] = report
        context.state_data["verdict"] = verdict
        context.state_data["has_critical"] = has_critical
        context.state_data["has_warnings"] = has_warnings

        return HandlerResult.ok(
            output={
                "validation_report": report,
                "verdict": verdict,
                "has_critical": has_critical,
                "has_warnings": has_warnings,
            },
            next_state="apply_verdict",
        )


# =============================================================================
# ENFORCE HANDLER
# =============================================================================


class EnforceHandler(TestValidationHandler):
    """
    Handler for 'enforce' action.
    Applies the verdict (block/warn/approve).
    """

    action_type = "enforce"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        has_critical = context.state_data.get("has_critical", False)
        has_warnings = context.state_data.get("has_warnings", False)
        verdict = context.state_data.get("verdict", "passed")

        if has_critical:
            action = "block_commit"
            message = "PANOPTICON+: Test blocked - fix critical issues"
        elif has_warnings:
            action = "warn_only"
            message = "PANOPTICON+: Test passed with warnings"
        else:
            action = "approve"
            message = "PANOPTICON+: Test approved"

        return HandlerResult.ok(
            output={
                "action": action,
                "message": message,
                "verdict": verdict,
                "blocked": has_critical,
            },
            next_state="done",
        )


# =============================================================================
# SUGGESTION GENERATOR HANDLER
# =============================================================================


class LogViolationsHandler(TestValidationHandler):
    """
    Handler for 'log_violations' action.
    Logs violations and continues to appropriate next state.
    """

    action_type = "log_violations"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        # Log the violations
        for v in context.violations:
            logger.info(f"[{v.get('severity', 'unknown')}] {v.get('message', 'No message')}")

        # Determine next state based on what violations we have
        fixture_violations = context.state_data.get("fixture_violations", [])
        assertion_violations = context.state_data.get("assertion_violations", [])

        # If we have fixture violations but haven't checked assertions yet
        if fixture_violations and not assertion_violations:
            return HandlerResult.ok(
                output={"logged": len(context.violations)},
                next_state="check_assertions",
            )

        # If we have assertion violations but haven't generated report
        if assertion_violations:
            return HandlerResult.ok(
                output={"logged": len(context.violations)},
                next_state="generate_report",
            )

        # Default: go to report
        return HandlerResult.ok(
            output={"logged": len(context.violations)},
            next_state="generate_report",
        )


class GenerateSuggestionsHandler(TestValidationHandler):
    """
    Handler for 'generate_suggestions' action.
    Generates improvement suggestions based on violations.
    """

    action_type = "generate_suggestions"

    def execute(
        self,
        context: ValidationContext,
        params: Dict[str, Any],
    ) -> HandlerResult:
        suggestions = []

        fixture_violations = context.state_data.get("fixture_violations", [])
        assertion_violations = context.state_data.get("assertion_violations", [])

        # Fixture suggestions
        for v in fixture_violations:
            if "Custom Agent" in v.get("message", ""):
                suggestions.append("Use TestAgents.compliant() or TestAgents.without_oath() from fixtures")
            if "oath_sworn" in v.get("rule", ""):
                suggestions.append("Use TestAgents.with_false_oath() instead of manual oath assignment")
            if "Import TestAgents" in v.get("message", ""):
                suggestions.append("Add: from vibe_core.plugins.test_orchestration import TestAgents")

        # Assertion suggestions
        for v in assertion_violations:
            if "no assertions" in v.get("message", ""):
                suggestions.append("Add assertions to test function to verify behavior")
            if "assert True" in v.get("message", ""):
                suggestions.append("Replace 'assert True' with meaningful assertion")
            if "except: pass" in v.get("message", ""):
                suggestions.append("Use pytest.raises() for expected exceptions, or remove bare except")

        # Deduplicate
        suggestions = list(dict.fromkeys(suggestions))
        context.suggestions = suggestions

        return HandlerResult.ok(
            output={"suggestions": suggestions},
            next_state="generate_report",
        )


# =============================================================================
# HANDLER REGISTRY
# =============================================================================


class TestValidationHandlerRegistry:
    """
    Registry for test validation action handlers.

    Usage:
        registry = TestValidationHandlerRegistry()
        handler = registry.get("ast_parse")
        result = handler.execute(context, params)
    """

    def __init__(self):
        self._handlers: Dict[str, TestValidationHandler] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register all default handlers."""
        handlers = [
            AstParseHandler(),
            PatternMatchHandler(),
            AssertionAnalysisHandler(),
            SemanticAnalysisHandler(),
            CompileReportHandler(),
            EnforceHandler(),
            GenerateSuggestionsHandler(),
            LogViolationsHandler(),
        ]
        for handler in handlers:
            self.register(handler)

    def register(self, handler: TestValidationHandler) -> None:
        """Register a handler."""
        self._handlers[handler.action_type] = handler
        logger.debug(f"Registered test validation handler: {handler.action_type}")

    def get(self, action_type: str) -> Optional[TestValidationHandler]:
        """Get handler by action type."""
        return self._handlers.get(action_type)

    def has(self, action_type: str) -> bool:
        """Check if handler exists."""
        return action_type in self._handlers

    @property
    def registered_types(self) -> List[str]:
        """List all registered action types."""
        return list(self._handlers.keys())


# =============================================================================
# CIRCUIT EXECUTOR - Nano Agent City
# =============================================================================


class TestValidationCircuitExecutor:
    """
    Executes the test_validation circuit using registered handlers.

    This is the "Nano Agent City" - each state transition invokes
    a deterministic handler (Nano Agent) to process the file.

    NO LLM REQUIRED - Pure state machine execution!
    """

    def __init__(self, circuit: Optional[Dict[str, Any]] = None):
        """
        Initialize executor.

        Args:
            circuit: Circuit definition (loaded from YAML).
                     If None, uses default test_validation circuit.
        """
        self.registry = TestValidationHandlerRegistry()
        self.circuit = circuit
        self._load_circuit_if_needed()

    def _load_circuit_if_needed(self):
        """Load circuit from YAML if not provided."""
        if self.circuit is not None:
            return

        from vibe_core.loaders import CircuitLoader

        circuits, _ = CircuitLoader.discover_and_load()
        self.circuit = circuits.get("test_validation")

        if self.circuit is None:
            logger.warning("test_validation circuit not found, using inline definition")

    def execute(self, file_path: str) -> Dict[str, Any]:
        """
        Execute the test validation circuit on a file.

        This walks through the state machine, invoking handlers
        for each state until reaching 'done'.

        Args:
            file_path: Path to test file to validate

        Returns:
            Final execution result with verdict and report
        """
        context = ValidationContext(file_path=file_path)

        # State machine execution
        current_state = "parse_test"  # Initial state
        max_iterations = 20  # Safety limit
        iteration = 0

        state_history = []

        while current_state != "done" and iteration < max_iterations:
            iteration += 1
            state_history.append(current_state)

            logger.debug(f"[{iteration}] State: {current_state}")

            # Get state definition
            state_def = self._get_state_def(current_state)
            if state_def is None:
                logger.error(f"Unknown state: {current_state}")
                break

            # Get handler for action
            action = state_def.get("action", current_state)
            handler = self.registry.get(action)

            if handler is None:
                logger.warning(f"No handler for action: {action}")
                # Try to continue with default transition
                current_state = state_def.get("on_success", state_def.get("transition", "done"))
                continue

            # Execute handler
            params = state_def.get("rules", state_def.get("input", {}))
            if isinstance(params, list):
                params = {"rules": params}
            result = handler.execute(context, params)

            logger.debug(f"  -> {action}: success={result.success}, next={result.next_state}")

            # Transition to next state
            if result.next_state:
                current_state = result.next_state
            elif result.success:
                current_state = state_def.get("on_success", state_def.get("transition", "done"))
            else:
                current_state = state_def.get("on_failure", "done")

        return {
            "file_path": file_path,
            "verdict": context.state_data.get("verdict", "unknown"),
            "blocked": context.state_data.get("has_critical", False),
            "report": context.state_data.get("validation_report", ""),
            "violations": context.violations,
            "suggestions": context.suggestions,
            "state_history": state_history,
            "iterations": iteration,
        }

    def _get_state_def(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Get state definition from circuit."""
        if self.circuit is None:
            return self._get_inline_state_def(state_id)

        states = self.circuit.get("states", [])
        for state in states:
            if state.get("id") == state_id:
                return state
        return None

    def _get_inline_state_def(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Fallback inline state definitions."""
        states = {
            "parse_test": {
                "action": "ast_parse",
                "on_success": "check_fixtures",
                "on_failure": "done",
            },
            "check_fixtures": {
                "action": "pattern_match",
                "rules": [
                    {
                        "pattern": r"class.*Agent.*VibeAgent",
                        "severity": "critical",
                        "message": "Custom Agent class forbidden",
                        "exclude_paths": [
                            "tests/hardening/",
                            "test_governance",
                            "test_red_team",
                            "test_capability",
                            "test_event_bus",
                            "test_kernel_markdown",
                            "tests/archive/",
                            "test_node_pulse_e2e",
                            "tests/perf/",
                        ],
                    },
                    {
                        "pattern": r"from vibe_core.plugins.test_orchestration import",
                        "required": True,
                        "severity": "warning",
                        "message": "Should import from fixtures",
                    },
                    {
                        "pattern": r"oath_sworn\s*=\s*(True|False)",
                        "severity": "critical",
                        "message": "Manual oath assignment forbidden",
                    },
                ],
            },
            "check_assertions": {
                "action": "assertion_analysis",
            },
            "check_coverage_intent": {
                "action": "semantic_analysis",
            },
            "suggest_improvements": {
                "action": "generate_suggestions",
            },
            "generate_report": {
                "action": "compile_report",
            },
            "apply_verdict": {
                "action": "enforce",
            },
            "report_violations": {
                "action": "log_violations",  # Log and route to next state
            },
        }
        return states.get(state_id)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def validate_test_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a test file using the circuit executor.

    This is the main entry point for test validation.

    Args:
        file_path: Path to test file

    Returns:
        Validation result dict
    """
    executor = TestValidationCircuitExecutor()
    return executor.execute(file_path)


def validate_test_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Validate multiple test files.

    Can be parallelized for "Agent Flood" style execution!

    Args:
        file_paths: List of test file paths

    Returns:
        List of validation results
    """
    executor = TestValidationCircuitExecutor()
    return [executor.execute(fp) for fp in file_paths]
