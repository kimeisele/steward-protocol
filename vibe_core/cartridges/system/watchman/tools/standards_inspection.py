#!/usr/bin/env python3
"""
StandardsInspectionTool - Core Code Governance Engine.
======================================================

Declarative AST analysis for architectural compliance.
Part of the VibeOS Core (System Agent: Watchman).
"""

import ast
import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("WATCHMAN.STANDARDS")


class ViolationSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Violation:
    agent_id: str
    file_path: str
    line_number: int
    rule_id: str
    severity: ViolationSeverity
    message: str
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "code_snippet": self.code_snippet,
            "fix_suggestion": self.fix_suggestion,
        }


class UniversalRuleVisitor(ast.NodeVisitor):
    """Interpret rules from standards.yaml against an AST."""

    def __init__(self, file_path: str, rules: List[Dict[str, Any]]):
        self.file_path = file_path
        self.rules = rules
        self.violations: List[Violation] = []

    def visit_Call(self, node: ast.Call) -> None:
        self._check_node(node, "Call")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self._check_node(node, "Attribute")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._check_node(node, "ExceptHandler")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_node(node, "Assign")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self._check_node(node, "Name")
        self.generic_visit(node)

    def _check_node(self, node: ast.AST, target_type: str) -> None:
        for rule in self.rules:
            if rule.get("target") != target_type:
                continue

            if self._matches_rule(node, rule):
                try:
                    snippet = ast.unparse(node)[:100]
                except Exception:
                    snippet = "N/A"

                self.violations.append(
                    Violation(
                        agent_id=self._extract_agent_id(),
                        file_path=self.file_path,
                        line_number=node.lineno,
                        rule_id=rule.get("id", "unknown"),
                        severity=ViolationSeverity(rule.get("severity", "MEDIUM")),
                        message=rule.get("message", "Violation"),
                        code_snippet=snippet,
                        fix_suggestion=rule.get("fix_suggestion"),
                    )
                )

    def _matches_rule(self, node: ast.AST, rule: Dict[str, Any]) -> bool:
        match = rule.get("match", {})

        # 1. Match Function Name
        if "func" in match:
            if not isinstance(node, ast.Call):
                return False
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name != match["func"]:
                return False

        # 1b. Match Function Name in List (func_in)
        if "func_in" in match:
            if not isinstance(node, ast.Call):
                return False
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name not in match["func_in"]:
                return False

        # 1c. Match Attribute Name (e.g., .get_instance(), .iterdir())
        if "attr" in match:
            if not isinstance(node, ast.Call):
                return False
            if not isinstance(node.func, ast.Attribute):
                return False
            if node.func.attr != match["attr"]:
                return False

        # 2. Match Object Name
        if "object" in match:
            obj = ""
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                obj = node.value.id
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
            ):
                obj = node.func.value.id
            if obj != match["object"]:
                return False

        # 3. Match Arguments
        if "args_contain" in match:
            forbidden = match["args_contain"]
            found = False
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and any(f in str(sub.value) for f in forbidden):
                    found = True
                    break
            if not found:
                return False

        # 3a. Match Arguments starting with prefix (args_starts_with)
        if "args_starts_with" in match:
            prefix = match["args_starts_with"]
            if not isinstance(node, ast.Call):
                return False
            found = False
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if arg.value.startswith(prefix):
                        found = True
                        break
            if not found:
                return False

        # 3b. Match Assignment name pattern (for global_singleton_dict)
        if "name_pattern" in match:
            if not isinstance(node, ast.Assign):
                return False
            # Check if any target matches the pattern
            pattern = match["name_pattern"]
            pattern_matched = False
            for target in node.targets:
                if isinstance(target, ast.Name) and pattern in target.id:
                    pattern_matched = True
                    break
            if not pattern_matched:
                return False

        # 3c. Match Name node directly (e.g., Any, Optional without subscript)
        if "name" in match:
            if not isinstance(node, ast.Name):
                return False
            if node.id != match["name"]:
                return False

        # 3d. Match keyword argument absence (e.g., subprocess.run without timeout)
        if "keyword_absent" in match:
            if not isinstance(node, ast.Call):
                return False
            keyword_name = match["keyword_absent"]
            # If keyword IS present, rule doesn't match
            for kw in node.keywords:
                if kw.arg == keyword_name:
                    return False  # Keyword found, so NOT a violation

        # 4. Custom Conditions
        if rule.get("condition") == "is_pass_only":
            if isinstance(node, ast.ExceptHandler):
                return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)

        # 5. Check allowed_files exclusion
        allowed = rule.get("allowed_files", [])
        if allowed and any(af in self.file_path for af in allowed):
            return False  # Skip violations in allowed files

        return True

    def _extract_agent_id(self) -> str:
        p = Path(self.file_path)
        for i, part in enumerate(p.parts):
            if part in ["system", "agent_city"] and i + 1 < len(p.parts):
                return p.parts[i + 1]
        return "core"


class StandardsInspectionTool(Tool):
    def __init__(self):
        self._rules = self._load_standards()

    def _load_standards(self) -> List[Dict[str, Any]]:
        p = Path("config/standards.yaml")
        if p.exists():
            try:
                with open(p) as f:
                    return yaml.safe_load(f).get("rules", [])
            except Exception as e:
                logger.error(f"Failed to load standards: {e}")
        return []

    @property
    def name(self) -> str:
        return "watchman.standards"

    @property
    def description(self) -> str:
        return "Core Standards Engine"

    @property
    def parameters_schema(self) -> dict:
        return {"action": {"type": "string", "required": True}, "path": {"type": "string"}}

    def validate(self, params: dict):
        if "action" not in params:
            raise ValueError("Missing action")

    def execute(self, params: dict) -> ToolResult:
        try:
            path = Path(params.get("path", "vibe_core"))
            violations = []
            if params["action"] == "inspect_file":
                violations = self.inspect_file(path)
            else:
                for py in path.glob("**/*.py"):
                    if "__pycache__" not in str(py):
                        violations.extend(self.inspect_file(py))

            return ToolResult(success=True, output={"violations": [v.to_dict() for v in violations]})
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def inspect_file(self, file_path: Path) -> List[Violation]:
        try:
            tree = ast.parse(file_path.read_text())
            visitor = UniversalRuleVisitor(str(file_path), self._rules)
            visitor.visit(tree)
            return visitor.violations
        except Exception:
            return []


if __name__ == "__main__":
    import sys

    tool = StandardsInspectionTool()
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vibe_core")
    res = tool.execute({"action": "inspect_all", "path": str(target)})
    print(json.dumps(res.output, indent=2))
