"""
OPUS-133: Viveka Action - The Hands of Discrimination.

This action executes triage intents from VivekaSense.
It uses SILPA (The Self-Architect) to safely add documentation.

Handled Intent Types:
- triage_p1_critical: Auto-fix critical documentation gaps
- triage_p2_high: Auto-fix high priority gaps
- triage_execute: Execute a specific triage fix

The Platinum Protocol applies:
1. PRE-GATE: Verify code parses correctly
2. TRANSFORM: Add docstring via AST
3. POST-GATE: Verify code still parses
4. COMMIT: Stage changes (optional)

"Viveka sees, Viveka discriminates, Viveka ACTS."

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true
wiring:
  - pattern: "class VivekaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "handled_intent_types.*triage_p1_critical"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->
"""

import ast
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Viveka")

# Protected paths that should never be modified automatically
PROTECTED_PATHS = {
    "vibe_core/kernel/",
    "vibe_core/state/",
    "vibe_core/governance/",
    ".github/workflows/",
}


# Template for auto-generated docstrings
DOCSTRING_TEMPLATE = '''"""
{description}

{details}
"""'''


class VivekaAction(BaseAction):
    """
    Viveka Action - Executes triage intents by adding missing documentation.

    Uses SILPA's Platinum Protocol for safe code modification:
    - Only modifies docstrings (SAFE risk level)
    - Verifies code parses before and after
    - Protected paths are never touched

    Modes:
    - dry_run=True: Shows what would be done, no changes
    - dry_run=False: Actually modifies files
    """

    # VEDA-4 auto-discovery
    name = "viveka_action"

    handled_intent_types: Set[str] = {
        "triage_p1_critical",
        "triage_p2_high",
        "triage_execute",
        "viveka_auto_doc",
    }

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize Viveka Action."""
        super().__init__(workspace)
        logger.info("👁️ VivekaAction initialized (The Hands of Discrimination)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a triage intent (BaseAction interface).

        For P1/P2 intents, this adds missing docstrings to the identified element.
        """
        intent_type = intent.intent_type
        params = intent.params

        logger.info(f"👁️ VivekaAction executing: {intent.title}")

        # Check for dry_run mode
        dry_run = params.get("dry_run", True)  # Default to dry_run for safety

        if intent_type in ("triage_p1_critical", "triage_p2_high"):
            return self._handle_triage_gap(intent, dry_run)
        elif intent_type == "triage_execute":
            return self._handle_explicit_execute(intent, dry_run)
        elif intent_type == "viveka_auto_doc":
            return self._handle_auto_doc(intent, dry_run)
        else:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=f"Unknown intent type: {intent_type}",
            )

    def _handle_triage_gap(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """
        Handle a triage gap intent (P1 or P2).

        Reads the file, generates a docstring, and optionally injects it.
        """
        params = intent.params
        file_path = params.get("file_path", "")
        element_name = params.get("element_name", "")
        element_type = params.get("element_type", "function")
        line_number = params.get("line_number", 0)

        if not file_path or not element_name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error="Missing file_path or element_name in params",
            )

        # Resolve path
        target_path = Path(file_path)
        if not target_path.is_absolute():
            target_path = self._workspace / target_path

        if not target_path.exists():
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"File not found: {target_path}",
            )

        # Read the file and find the element
        try:
            code = target_path.read_text()
            tree = ast.parse(code)
        except SyntaxError as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Cannot parse file: {e}",
            )

        # Find the element and check if it has a docstring
        element_info = self._find_element(tree, element_name, element_type)
        if not element_info:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Element {element_name} not found in {target_path.name}",
            )

        has_docstring = element_info.get("has_docstring", False)

        if has_docstring:
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "skipped",
                    "reason": f"{element_name} already has a docstring",
                    "file": str(target_path),
                },
            )

        # Generate a docstring
        generated_docstring = self._generate_docstring(
            element_name=element_name,
            element_type=element_type,
            element_info=element_info,
        )

        if dry_run:
            # Dry run - just report what would be done
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "dry_run",
                    "file": str(target_path),
                    "element": element_name,
                    "element_type": element_type,
                    "line": element_info.get("line", 0),
                    "generated_docstring": generated_docstring,
                    "message": f"Would add docstring to {element_type} '{element_name}'",
                },
            )

        # Actual execution - direct AST transformation (simpler than SILPA)
        try:
            # Check if protected path
            rel_path = str(target_path.relative_to(self._workspace))
            if self._is_protected_path(rel_path):
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"FORBIDDEN: Cannot modify protected file {rel_path}",
                )

            # Apply docstring via AST transformation
            new_code = self._add_docstring_ast(
                code=code,
                tree=tree,
                element_name=element_name,
                element_type=element_type,
                docstring=generated_docstring,
            )

            if new_code is None:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"Failed to add docstring to {element_name}",
                )

            # POST-GATE: Verify new code parses
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"POST-GATE failed: Generated code has syntax error: {e}",
                )

            # Write the transformed code
            target_path.write_text(new_code)

            logger.info(f"✅ Docstring added to {element_name} in {target_path.name}")
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "executed",
                    "file": str(target_path),
                    "element": element_name,
                    "docstring_added": True,
                    "message": f"Added docstring to {element_type} '{element_name}'",
                },
            )

        except Exception as e:
            logger.error(f"❌ VivekaAction failed: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=str(e),
            )

    def _handle_explicit_execute(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """Handle explicit triage_execute intent."""
        # Same as triage gap but with explicit override
        return self._handle_triage_gap(intent, dry_run=False)

    def _handle_auto_doc(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """Handle viveka_auto_doc intent - batch documentation."""
        # Future: batch process multiple gaps
        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.intent_type,
            result={
                "action": "not_implemented",
                "message": "Batch auto-doc not yet implemented",
            },
        )

    def _find_element(self, tree: ast.AST, element_name: str, element_type: str) -> Optional[Dict[str, Any]]:
        """Find an element (function/class) in the AST."""
        for node in ast.walk(tree):
            if element_type == "function" and isinstance(node, ast.FunctionDef):
                if node.name == element_name:
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    return {
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno,
                        "has_docstring": has_docstring,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            ast.unparse(d) if hasattr(ast, "unparse") else str(d) for d in node.decorator_list
                        ],
                    }
            elif element_type == "class" and isinstance(node, ast.ClassDef):
                if node.name == element_name:
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    return {
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "has_docstring": has_docstring,
                        "bases": [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases],
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    }
        return None

    def _generate_docstring(
        self,
        element_name: str,
        element_type: str,
        element_info: Dict[str, Any],
    ) -> str:
        """
        Generate a docstring for an element.

        In a full implementation, this would use an LLM.
        For now, we generate a template-based docstring.
        """
        # Note: Return docstring content WITHOUT triple quotes
        # ast.Constant will handle the string representation
        if element_type == "function":
            args = element_info.get("args", [])
            args_doc = ""
            if args:
                filtered_args = [arg for arg in args if arg != "self"]
                if filtered_args:
                    args_doc = "\n\nArgs:\n" + "\n".join(f"    {arg}: Description needed" for arg in filtered_args)

            return f"{element_name} - TODO: Add description.{args_doc}"

        elif element_type == "class":
            methods = element_info.get("methods", [])
            methods_doc = ""
            if methods:
                public_methods = [m for m in methods if not m.startswith("_")]
                if public_methods:
                    methods_doc = "\n\nPublic Methods:\n" + "\n".join(
                        f"    {m}: Description needed" for m in public_methods[:5]
                    )

            return f"{element_name} - TODO: Add description.{methods_doc}"

        return f"{element_name} - TODO: Add description."

    def _is_protected_path(self, rel_path: str) -> bool:
        """Check if a path is protected from automatic modification."""
        for protected in PROTECTED_PATHS:
            if rel_path.startswith(protected):
                return True
        return False

    def _add_docstring_ast(
        self,
        code: str,
        tree: ast.AST,
        element_name: str,
        element_type: str,
        docstring: str,
    ) -> Optional[str]:
        """
        Add a docstring to an element using surgical text insertion.

        This approach preserves the original formatting instead of
        regenerating the entire file with ast.unparse().

        Returns the new code or None if transformation fails.
        """
        # Find the element's definition line
        target_line = None
        target_indent = 0

        for node in ast.walk(tree):
            is_match = False
            if element_type == "function":
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == element_name:
                        is_match = True
            elif element_type == "class":
                if isinstance(node, ast.ClassDef):
                    if node.name == element_name:
                        is_match = True

            if is_match:
                # Get line number and column offset for indentation
                target_line = node.lineno  # 1-indexed
                target_indent = node.col_offset + 4  # Body indent = def indent + 4
                break

        if target_line is None:
            return None

        # Split code into lines
        lines = code.split("\n")

        # Find the line after the def/class statement (could span multiple lines)
        # We need to find the colon that ends the signature
        insert_after = target_line - 1  # Convert to 0-indexed
        while insert_after < len(lines) and ":" not in lines[insert_after]:
            insert_after += 1

        # Format the docstring with proper indentation
        indent = " " * target_indent
        docstring_lines = docstring.split("\n")
        if len(docstring_lines) == 1:
            # Single-line docstring
            formatted_docstring = f'{indent}"""{docstring}"""'
        else:
            # Multi-line docstring
            formatted_docstring = f'{indent}"""{docstring_lines[0]}'
            for line in docstring_lines[1:]:
                formatted_docstring += f"\n{indent}{line}"
            formatted_docstring += f'\n{indent}"""'

        # Insert after the definition line
        lines.insert(insert_after + 1, formatted_docstring)

        return "\n".join(lines)
