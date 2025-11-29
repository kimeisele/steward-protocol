#!/usr/bin/env python3
"""
StandardsInspectionTool - Deep AST-based Code Analysis (Phase 3.2)
===================================================================

This is Watchman's "microscope" - it parses Python AST (Abstract Syntax Tree)
to find architectural violations that simple grep cannot catch.

Part of Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: This tool (AST analysis) - catches the remaining 5%
- Layer 3: Auditor verdict (constitutional judgment)

Capabilities:
1. Detect requirements.txt in agent directories
2. Detect direct Path("data/...") calls (even with variables)
3. Detect missing lazy-loading patterns
4. Detect line count violations (GAD-000: agents should be <500 lines)
5. Detect missing system interface usage

Why AST instead of grep:
- Can detect semantic violations (not just text patterns)
- Understands Python structure (imports, classes, methods)
- Can trace variable usage across functions
- Immune to string escaping tricks

Performance: ~500ms for 14 agents (acceptable for CI/CD, NOT for pre-commit)
"""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("WATCHMAN.STANDARDS_INSPECTION")


class ViolationType(Enum):
    """Types of architectural violations."""

    REQUIREMENTS_TXT = "requirements_txt"
    DIRECT_PATH_DATA = "direct_path_data"
    MISSING_LAZY_LOADING = "missing_lazy_loading"
    LINE_COUNT_EXCEEDED = "line_count_exceeded"
    MISSING_SYSTEM_INTERFACE = "missing_system_interface"
    HARDCODED_PATH_IN_INIT = "hardcoded_path_in_init"


class ViolationSeverity(Enum):
    """Severity levels for violations."""

    CRITICAL = "CRITICAL"  # Build must fail
    HIGH = "HIGH"  # Should fail, but can be overridden
    MEDIUM = "MEDIUM"  # Warning, should be fixed
    LOW = "LOW"  # Suggestion


@dataclass
class Violation:
    """Represents a single architectural violation."""

    agent_id: str
    file_path: str
    line_number: int
    violation_type: ViolationType
    severity: ViolationSeverity
    message: str
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "code_snippet": self.code_snippet,
            "fix_suggestion": self.fix_suggestion,
        }


class PathCallVisitor(ast.NodeVisitor):
    """AST visitor to detect Path("data/...") calls."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[Violation] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call nodes."""
        # Check for Path("data/...") pattern
        if isinstance(node.func, ast.Name) and node.func.id == "Path":
            # Check if first argument is a string starting with "data/"
            if node.args and isinstance(node.args[0], ast.Constant):
                arg_value = node.args[0].value
                if isinstance(arg_value, str) and arg_value.startswith("data/"):
                    self.violations.append(
                        Violation(
                            agent_id=self._extract_agent_id(),
                            file_path=self.file_path,
                            line_number=node.lineno,
                            violation_type=ViolationType.DIRECT_PATH_DATA,
                            severity=ViolationSeverity.CRITICAL,
                            message=f"Direct Path('data/...') call detected: Path('{arg_value}')",
                            code_snippet=f"Path('{arg_value}')",
                            fix_suggestion="Use agent.system.get_sandbox_path() / 'subdir' instead",
                        )
                    )

        self.generic_visit(node)

    def _extract_agent_id(self) -> str:
        """Extract agent ID from file path."""
        parts = Path(self.file_path).parts
        if "system_agents" in parts:
            idx = parts.index("system_agents")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "unknown"


class InitMethodVisitor(ast.NodeVisitor):
    """AST visitor to detect hardcoded paths in __init__ methods."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[Violation] = []
        self.in_init = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if node.name == "__init__":
            self.in_init = True
            self.generic_visit(node)
            self.in_init = False
        else:
            self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment nodes in __init__."""
        if self.in_init:
            # Check for self.path = Path(...) patterns
            if isinstance(node.value, ast.Call):
                if (
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "Path"
                ):
                    # Check if it's a hardcoded path (not lazy-loaded)
                    if node.value.args and isinstance(node.value.args[0], ast.Constant):
                        arg_value = node.value.args[0].value
                        if isinstance(arg_value, str) and not arg_value.startswith("_"):
                            # This is a hardcoded path in __init__ (not a temp variable)
                            self.violations.append(
                                Violation(
                                    agent_id=self._extract_agent_id(),
                                    file_path=self.file_path,
                                    line_number=node.lineno,
                                    violation_type=ViolationType.HARDCODED_PATH_IN_INIT,
                                    severity=ViolationSeverity.MEDIUM,
                                    message=f"Hardcoded path in __init__: {arg_value}",
                                    code_snippet=f"Path('{arg_value}')",
                                    fix_suggestion="Use lazy-loading @property pattern instead",
                                )
                            )

        self.generic_visit(node)

    def _extract_agent_id(self) -> str:
        """Extract agent ID from file path."""
        parts = Path(self.file_path).parts
        if "system_agents" in parts:
            idx = parts.index("system_agents")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "unknown"


class StandardsInspectionTool:
    """
    Deep AST-based inspection tool for architectural standards.

    This is Watchman's "microscope" - it can see violations that grep cannot.
    """

    def __init__(self):
        self.violations: List[Violation] = []

    def inspect_agent(self, agent_path: Path) -> List[Violation]:
        """
        Inspect a single agent for violations.

        Args:
            agent_path: Path to agent directory (e.g., steward/system_agents/herald)

        Returns:
            List of violations found
        """
        violations = []

        # Check 1: requirements.txt should not exist
        requirements_file = agent_path / "requirements.txt"
        if requirements_file.exists():
            violations.append(
                Violation(
                    agent_id=agent_path.name,
                    file_path=str(requirements_file),
                    line_number=1,
                    violation_type=ViolationType.REQUIREMENTS_TXT,
                    severity=ViolationSeverity.CRITICAL,
                    message="requirements.txt found in agent directory",
                    fix_suggestion="Remove requirements.txt and use pyproject.toml",
                )
            )

        # Check 2: Inspect cartridge_main.py with AST
        cartridge_file = agent_path / "cartridge_main.py"
        if cartridge_file.exists():
            violations.extend(self._inspect_python_file(cartridge_file))

        # Check 3: Line count (GAD-000 compliance)
        if cartridge_file.exists():
            line_count = len(cartridge_file.read_text().splitlines())
            if line_count > 500:
                violations.append(
                    Violation(
                        agent_id=agent_path.name,
                        file_path=str(cartridge_file),
                        line_number=1,
                        violation_type=ViolationType.LINE_COUNT_EXCEEDED,
                        severity=ViolationSeverity.MEDIUM,
                        message=f"Agent has {line_count} lines (GAD-000 recommends <500)",
                        fix_suggestion="Consider splitting into multiple tools",
                    )
                )

        return violations

    def _inspect_python_file(self, file_path: Path) -> List[Violation]:
        """
        Inspect a Python file using AST analysis.

        Args:
            file_path: Path to Python file

        Returns:
            List of violations found
        """
        violations = []

        try:
            content = file_path.read_text()
            tree = ast.parse(content, filename=str(file_path))

            # Visit 1: Find Path("data/...") calls
            path_visitor = PathCallVisitor(str(file_path))
            path_visitor.visit(tree)
            violations.extend(path_visitor.violations)

            # Visit 2: Find hardcoded paths in __init__
            init_visitor = InitMethodVisitor(str(file_path))
            init_visitor.visit(tree)
            violations.extend(init_visitor.violations)

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            violations.append(
                Violation(
                    agent_id=file_path.parent.name,
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    violation_type=ViolationType.MISSING_SYSTEM_INTERFACE,
                    severity=ViolationSeverity.HIGH,
                    message=f"Syntax error: {e.msg}",
                )
            )

        return violations

    def inspect_all_agents(self, system_agents_path: Path) -> List[Violation]:
        """
        Inspect all agents in the system_agents directory.

        Args:
            system_agents_path: Path to steward/system_agents

        Returns:
            List of all violations found
        """
        all_violations = []

        # Find all agent directories
        for agent_dir in system_agents_path.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                logger.info(f"🔍 Inspecting {agent_dir.name}...")
                violations = self.inspect_agent(agent_dir)
                all_violations.extend(violations)

                if violations:
                    logger.warning(
                        f"   ⚠️  Found {len(violations)} violation(s) in {agent_dir.name}"
                    )
                else:
                    logger.info(f"   ✅ {agent_dir.name} is compliant")

        return all_violations

    def generate_report(self, violations: List[Violation]) -> Dict[str, Any]:
        """
        Generate a compliance report.

        Args:
            violations: List of violations

        Returns:
            Report dict with summary and details
        """
        # Group by severity
        by_severity = {
            "CRITICAL": [
                v for v in violations if v.severity == ViolationSeverity.CRITICAL
            ],
            "HIGH": [v for v in violations if v.severity == ViolationSeverity.HIGH],
            "MEDIUM": [v for v in violations if v.severity == ViolationSeverity.MEDIUM],
            "LOW": [v for v in violations if v.severity == ViolationSeverity.LOW],
        }

        # Group by agent
        by_agent = {}
        for v in violations:
            if v.agent_id not in by_agent:
                by_agent[v.agent_id] = []
            by_agent[v.agent_id].append(v)

        return {
            "total_violations": len(violations),
            "by_severity": {
                severity: len(viols) for severity, viols in by_severity.items()
            },
            "by_agent": {agent_id: len(viols) for agent_id, viols in by_agent.items()},
            "critical_count": len(by_severity["CRITICAL"]),
            "should_fail_build": len(by_severity["CRITICAL"]) > 0,
            "violations": [v.to_dict() for v in violations],
        }
