"""
TEST VALIDATION TOOL - PANOPTICON+ for Agents
==============================================

Tool wrapper that allows any Agent (especially Watchman) to execute
the test validation circuit.

This closes the loop:
    Agent → Tool → CircuitExecutor → Nano Agents → Verdict

Usage by Watchman Agent:
    result = tool.execute({
        "action": "validate",
        "path": "tests/test_foo.py"
    })

Usage for batch validation (Agent Flood):
    result = tool.execute({
        "action": "validate_batch",
        "paths": ["tests/test_a.py", "tests/test_b.py", ...]
    })
"""

import logging
from pathlib import Path
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult

from .action_handlers import (
    TestValidationCircuitExecutor,
    validate_test_file,
    validate_test_files,
)

logger = logging.getLogger("TEST_VALIDATION_TOOL")


class TestValidationTool(Tool):
    """
    Tool for executing PANOPTICON+ test validation.

    This tool wraps the TestValidationCircuitExecutor, allowing
    any agent to validate test files using the deterministic
    circuit-based validation system.

    Actions:
        - validate: Validate a single test file
        - validate_batch: Validate multiple test files
        - validate_directory: Validate all tests in a directory
        - get_circuit_info: Return info about the validation circuit
    """

    name = "test_validation"
    description = "Validates test files against PANOPTICON+ standards using circuit-based execution"

    def __init__(self):
        self.executor = TestValidationCircuitExecutor()

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters."""
        return {
            "action": {
                "type": "string",
                "required": True,
                "enum": ["validate", "validate_batch", "validate_directory", "get_circuit_info"],
                "description": "The action to perform",
            },
            "path": {
                "type": "string",
                "required": False,
                "description": "Path to test file (for 'validate' action)",
            },
            "paths": {
                "type": "array",
                "required": False,
                "description": "List of test file paths (for 'validate_batch' action)",
            },
            "directory": {
                "type": "string",
                "required": False,
                "description": "Directory path (for 'validate_directory' action)",
            },
            "pattern": {
                "type": "string",
                "required": False,
                "default": "test_*.py",
                "description": "Glob pattern for test files",
            },
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate that parameters meet requirements."""
        action = parameters.get("action")
        if not action:
            raise ValueError("Missing required parameter: action")

        if action == "validate" and not parameters.get("path"):
            raise ValueError("'validate' action requires 'path' parameter")

        if action == "validate_batch" and not parameters.get("paths"):
            raise ValueError("'validate_batch' action requires 'paths' parameter")

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute test validation.

        Parameters:
            action: str - The action to perform
            path: str - Path to file (for 'validate')
            paths: List[str] - Paths to files (for 'validate_batch')
            directory: str - Directory path (for 'validate_directory')

        Returns:
            ToolResult with validation results
        """
        action = parameters.get("action", "validate")

        try:
            if action == "validate":
                return self._validate_single(parameters)
            elif action == "validate_batch":
                return self._validate_batch(parameters)
            elif action == "validate_directory":
                return self._validate_directory(parameters)
            elif action == "get_circuit_info":
                return self._get_circuit_info()
            else:
                return ToolResult(
                    success=False,
                    output={"error": f"Unknown action: {action}"},
                )
        except Exception as e:
            logger.error(f"Test validation failed: {e}")
            return ToolResult(
                success=False,
                output={"error": str(e)},
            )

    def _validate_single(self, parameters: Dict[str, Any]) -> ToolResult:
        """Validate a single test file."""
        path = parameters.get("path")
        if not path:
            return ToolResult(
                success=False,
                output={"error": "Missing 'path' parameter"},
            )

        result = validate_test_file(path)

        return ToolResult(
            success=not result["blocked"],
            output={
                "file": result["file_path"],
                "verdict": result["verdict"],
                "blocked": result["blocked"],
                "violations": result["violations"],
                "report": result["report"],
                "state_count": result["iterations"],
            },
        )

    def _validate_batch(self, parameters: Dict[str, Any]) -> ToolResult:
        """Validate multiple test files (Agent Flood style)."""
        paths = parameters.get("paths", [])
        if not paths:
            return ToolResult(
                success=False,
                output={"error": "Missing 'paths' parameter"},
            )

        results = validate_test_files(paths)

        # Aggregate results
        total = len(results)
        passed = sum(1 for r in results if not r["blocked"])
        blocked = total - passed

        all_violations = []
        for r in results:
            for v in r["violations"]:
                all_violations.append(
                    {
                        "file": r["file_path"],
                        **v,
                    }
                )

        return ToolResult(
            success=blocked == 0,
            output={
                "total": total,
                "passed": passed,
                "blocked": blocked,
                "violations": all_violations,
                "files": [
                    {
                        "file": r["file_path"],
                        "verdict": r["verdict"],
                        "blocked": r["blocked"],
                    }
                    for r in results
                ],
            },
        )

    def _validate_directory(self, parameters: Dict[str, Any]) -> ToolResult:
        """Validate all test files in a directory."""
        directory = parameters.get("directory", "tests")
        pattern = parameters.get("pattern", "test_*.py")

        dir_path = Path(directory)
        if not dir_path.exists():
            return ToolResult(
                success=False,
                output={"error": f"Directory not found: {directory}"},
            )

        # Find all test files
        test_files = list(dir_path.glob(f"**/{pattern}"))
        paths = [str(f) for f in test_files]

        if not paths:
            return ToolResult(
                success=True,
                output={
                    "message": f"No test files matching '{pattern}' in {directory}",
                    "total": 0,
                },
            )

        # Delegate to batch validation
        return self._validate_batch({"paths": paths})

    def _get_circuit_info(self) -> ToolResult:
        """Return information about the validation circuit."""
        return ToolResult(
            success=True,
            output={
                "circuit_id": "test_validation",
                "type": "state_machine",
                "description": "PANOPTICON+ test validation circuit",
                "handlers": self.executor.registry.registered_types,
                "states": [
                    "parse_test",
                    "check_fixtures",
                    "check_assertions",
                    "check_coverage_intent",
                    "suggest_improvements",
                    "generate_report",
                    "apply_verdict",
                    "report_violations",
                ],
                "rules": {
                    "PANOPTICON_001": "No custom Agent classes in tests",
                    "PANOPTICON_002": "Must import from fixtures",
                    "PANOPTICON_003": "No manual oath_sworn assignment",
                    "PANOPTICON_004": "At least one assertion per test",
                    "PANOPTICON_005": "No 'assert True' (meaningless)",
                    "PANOPTICON_006": "No 'except: pass' (error swallowing)",
                },
            },
        )


# =============================================================================
# TOOL FACTORY
# =============================================================================


def create_test_validation_tool() -> TestValidationTool:
    """Factory function to create the tool."""
    return TestValidationTool()
