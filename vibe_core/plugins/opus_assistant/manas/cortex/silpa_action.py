"""
OPUS-101: Silpa Action - VEDA-4 Compliant Code Refactoring.

This wraps SilpaArchitect in a BaseAction interface for auto-discovery.

Karmendriya: PANI (Hands) - The ability to sculpt/modify code.

Handled Intent Types:
- genesis_tests: Generate tests for code
- create_tests: Create test files
- semantic_gap_test: Test based on semantic gaps
- refactor_file: Refactor a specific file
- update_docstring: Update docstrings
- analyze_refactor: Analyze potential refactorings

CRITICAL: This is how MANAS modifies its own code.
If this doesn't work, MANAS cannot self-improve.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
wiring:
  - pattern: "class SilpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
  - pattern: "handled_intent_types.*genesis_tests"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .silpa import (
    RefactorRisk,
    RefactorType,
    SilpaArchitect,
    SilpaAuditor,
    SilpaPlan,
    SilpaRefactoring,
    SilpaResult,
)

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Silpa")


class SilpaAction(BaseAction):
    """
    Silpa Action - Code Modification and Refactoring.

    Wraps SilpaArchitect in BaseAction interface for ActionLoader discovery.

    "PANI (Hands) - The sculptor's hands that shape code."

    CRITICAL: This enables MANAS to modify code.
    Without this working, MANAS cannot self-improve.
    """

    # OPUS-101: VEDA-4 auto-discovery
    name = "silpa_action"

    # Intent types this action handles
    handled_intent_types: Set[str] = {
        # Test generation
        "genesis_tests",
        "create_tests",
        "semantic_gap_test",
        # Refactoring
        "refactor_file",
        "refactor_analyze",
        "analyze_refactor",
        # Docstring operations
        "update_docstring",
        "add_docstring",
        # Code modification
        "rename_variable",
        "rename_function",
        "extract_method",
        "update_imports",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Silpa Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._architect = SilpaArchitect(workspace=self._workspace)
        self._auditor = SilpaAuditor(self._workspace)
        logger.info("[SILPA_ACTION] Initialized - PANI (The Hands)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a code modification intent.

        Routes to appropriate SilpaArchitect method based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.type
        params = intent.params or {}

        try:
            # Test generation intents
            if intent_type in ("genesis_tests", "create_tests", "semantic_gap_test"):
                return self._handle_test_generation(intent, params)

            # Analysis intents
            elif intent_type in ("refactor_analyze", "analyze_refactor"):
                return self._handle_analyze(intent, params)

            # Docstring intents
            elif intent_type in ("update_docstring", "add_docstring"):
                return self._handle_docstring(intent, params)

            # Refactoring intents
            elif intent_type in (
                "refactor_file",
                "rename_variable",
                "rename_function",
                "extract_method",
                "update_imports",
            ):
                return self._handle_refactor(intent, params)

            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent_type,
                    error=f"Unknown intent type for SilpaAction: {intent_type}",
                )

        except Exception as e:
            logger.error(f"[SILPA_ACTION] Error handling {intent_type}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=str(e),
            )

    def _handle_test_generation(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle test generation intents."""
        target_file = params.get("target_file") or params.get("file")
        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter for test generation",
            )

        target_path = Path(target_file)

        # Run existing tests first (if any)
        test_result = self._auditor.run_tests(target_file=target_path)

        # Analyze what tests could be generated
        analysis = {
            "target_file": str(target_file),
            "existing_tests": test_result.passed + test_result.failed,
            "test_coverage_exists": test_result.passed > 0,
            "suggestion": "Use SILPA refactoring to generate missing tests",
        }

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result=analysis,
            metadata={"test_result": test_result.to_dict()},
        )

    def _handle_analyze(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle refactoring analysis intents."""
        target_file = params.get("target_file") or params.get("file")
        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter for analysis",
            )

        target_path = self._workspace / target_file
        if not target_path.exists():
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Target file not found: {target_file}",
            )

        # Read and analyze code
        code = target_path.read_text()
        analysis = {
            "target_file": str(target_file),
            "lines": len(code.splitlines()),
            "size_bytes": len(code),
            "can_refactor": True,
            "suggestions": [],
        }

        # Check for common refactoring opportunities
        if "def " in code:
            func_count = code.count("def ")
            if func_count > 10:
                analysis["suggestions"].append(f"Consider extracting methods - {func_count} functions in file")

        if '"""' not in code and "'''" not in code:
            analysis["suggestions"].append("Missing docstrings - consider adding")

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result=analysis,
        )

    def _handle_docstring(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle docstring update/add intents."""
        target_file = params.get("target_file") or params.get("file")
        target_name = params.get("target_name") or params.get("function") or params.get("class")
        new_docstring = params.get("docstring") or params.get("content")

        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter",
            )

        refactor_type = (
            RefactorType.UPDATE_DOCSTRING if intent.type == "update_docstring" else RefactorType.ADD_DOCSTRING
        )

        refactoring = SilpaRefactoring(
            target_file=Path(target_file),
            refactor_type=refactor_type,
            target_name=target_name,
            new_code=new_docstring,
            description=f"{intent.type} for {target_name or target_file}",
        )

        # Plan the refactoring
        try:
            plan = self._architect.plan(refactoring)

            # For docstrings, classify risk
            risk = self._architect.classify_risk(refactoring)

            if risk == RefactorRisk.FORBIDDEN:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error="Cannot modify protected file",
                )

            # Execute if safe
            if risk == RefactorRisk.SAFE:
                result = self._architect.execute(plan)
                return self._silpa_result_to_action_result(result, intent.type)
            else:
                # Needs approval for non-safe changes
                return ActionResult(
                    success=True,
                    action_name=self.name,
                    intent_type=intent.type,
                    result={
                        "status": "needs_approval",
                        "risk": risk.value,
                        "plan": plan.to_dict(),
                    },
                    metadata={"approval_required": True},
                )

        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=str(e),
            )

    def _handle_refactor(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle general refactoring intents."""
        target_file = params.get("target_file") or params.get("file")

        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter",
            )

        # Map intent type to refactor type
        type_mapping = {
            "refactor_file": RefactorType.CUSTOM,
            "rename_variable": RefactorType.RENAME_VARIABLE,
            "rename_function": RefactorType.RENAME_FUNCTION,
            "extract_method": RefactorType.EXTRACT_METHOD,
            "update_imports": RefactorType.UPDATE_IMPORTS,
        }

        refactor_type = type_mapping.get(intent.type, RefactorType.CUSTOM)

        refactoring = SilpaRefactoring(
            target_file=Path(target_file),
            refactor_type=refactor_type,
            target_name=params.get("target_name"),
            new_code=params.get("new_code"),
            description=params.get("description", f"Refactor: {intent.type}"),
        )

        try:
            # Plan first
            plan = self._architect.plan(refactoring)
            risk = self._architect.classify_risk(refactoring)

            if risk == RefactorRisk.FORBIDDEN:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error="Cannot modify protected/forbidden file",
                )

            # All non-safe refactorings need approval
            if risk != RefactorRisk.SAFE:
                return ActionResult(
                    success=True,
                    action_name=self.name,
                    intent_type=intent.type,
                    result={
                        "status": "needs_approval",
                        "risk": risk.value,
                        "plan": plan.to_dict(),
                    },
                    metadata={"approval_required": True, "risk": risk.value},
                )

            # Execute safe refactorings
            result = self._architect.execute(plan)
            return self._silpa_result_to_action_result(result, intent.type)

        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=str(e),
            )

    def _silpa_result_to_action_result(self, silpa_result: SilpaResult, intent_type: str) -> ActionResult:
        """Convert SilpaResult to ActionResult."""
        return ActionResult(
            success=silpa_result.success,
            action_name=self.name,
            intent_type=intent_type,
            result=silpa_result.to_dict(),
            error=silpa_result.error,
            metadata={
                "risk": silpa_result.risk.value if silpa_result.risk else None,
                "tests_before": silpa_result.tests_before.to_dict() if silpa_result.tests_before else None,
                "tests_after": silpa_result.tests_after.to_dict() if silpa_result.tests_after else None,
            },
        )
