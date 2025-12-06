"""
TEST VALIDATOR - Layer 2 of PANOPTICON+ (Deterministic)
========================================================

Validates test files against PANOPTICON+ standards.
NO LLM REQUIRED - pure AST + regex pattern matching.

Rules enforced:
1. FORBIDDEN: Custom Agent mock classes in test files
2. REQUIRED: Import from fixtures (TestAgents, TestKernel, etc.)
3. FORBIDDEN: Manual oath_sworn assignment outside fixtures
4. REQUIRED: At least one assertion per test function
5. FORBIDDEN: assert True (meaningless)
6. FORBIDDEN: except: pass (swallowing errors)

Usage:
    validator = TestValidator()
    report = validator.validate_file("tests/test_foo.py")
    if report.has_critical:
        print("BLOCKED:", report.critical_violations)

Integration:
    - Pre-commit hook
    - CI pipeline
    - TestOrchestrationPlugin.validate_tests()
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("TEST_VALIDATOR")


# =============================================================================
# VIOLATION DEFINITIONS
# =============================================================================


@dataclass
class Violation:
    """A single rule violation."""

    rule: str
    severity: str  # "critical", "warning", "info"
    message: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report for a file or set of files."""

    file_path: str
    violations: List[Violation] = field(default_factory=list)
    passed: bool = True

    @property
    def has_critical(self) -> bool:
        return any(v.severity == "critical" for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(v.severity == "warning" for v in self.violations)

    @property
    def critical_violations(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == "critical"]

    @property
    def warning_violations(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == "warning"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "passed": self.passed,
            "has_critical": self.has_critical,
            "has_warnings": self.has_warnings,
            "violation_count": len(self.violations),
            "violations": [
                {
                    "rule": v.rule,
                    "severity": v.severity,
                    "message": v.message,
                    "line": v.line_number,
                }
                for v in self.violations
            ],
        }


# =============================================================================
# VALIDATION RULES
# =============================================================================


class Rule:
    """Base class for validation rules."""

    rule_id: str
    severity: str
    description: str

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        """Check the rule and return violations."""
        raise NotImplementedError


class ForbiddenCustomAgentClass(Rule):
    """FORBIDDEN: Custom Agent mock classes in test files."""

    rule_id = "PANOPTICON_001"
    severity = "critical"
    description = "Custom Agent class in test. Use TestAgents.xxx() instead."

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from VibeAgent or has Agent in name
                is_agent_subclass = False

                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr

                    if "Agent" in base_name or base_name == "VibeAgent":
                        is_agent_subclass = True
                        break

                # Also check class name patterns
                if "Agent" in node.name and not node.name.startswith("_"):
                    is_agent_subclass = True

                if is_agent_subclass:
                    violations.append(
                        Violation(
                            rule=self.rule_id,
                            severity=self.severity,
                            message=f"FORBIDDEN: Custom Agent class '{node.name}'. "
                            f"Use TestAgents.without_oath(), TestAgents.compliant(), etc.",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=f"class {node.name}(...)",
                        )
                    )

        return violations


class RequireFixtureImport(Rule):
    """REQUIRED: Import from fixtures for test files."""

    rule_id = "PANOPTICON_002"
    severity = "warning"
    description = "Test should import from PANOPTICON+ fixtures."

    # Patterns that indicate fixture usage
    FIXTURE_PATTERNS = [
        "from vibe_core.plugins.test_orchestration import",
        "from vibe_core.plugins.test_orchestration.fixtures import",
        "TestAgents",
        "TestKernel",
        "TestPlugins",
        "TestContext",
    ]

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        # Only check test files
        if not Path(file_path).name.startswith("test_"):
            return violations

        has_fixture_import = False
        for pattern in self.FIXTURE_PATTERNS:
            if pattern in source:
                has_fixture_import = True
                break

        # Check if file creates agents or kernels
        creates_agents = "Agent(" in source or "VibeAgent" in source
        creates_kernels = "Kernel(" in source or "RealVibeKernel" in source

        if (creates_agents or creates_kernels) and not has_fixture_import:
            violations.append(
                Violation(
                    rule=self.rule_id,
                    severity=self.severity,
                    message="Test creates agents/kernels but doesn't import from fixtures. "
                    "Consider using TestAgents and TestKernel from test_orchestration.",
                    file_path=file_path,
                    line_number=1,
                )
            )

        return violations


class ForbiddenManualOathAssignment(Rule):
    """FORBIDDEN: Manual oath_sworn assignment outside fixtures."""

    rule_id = "PANOPTICON_003"
    severity = "critical"
    description = "Manual oath_sworn assignment. Use TestAgents.with_false_oath()."

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        # Skip if this IS the fixtures file
        if "fixtures.py" in file_path:
            return violations

        # Pattern: oath_sworn = True/False (with various spacing)
        pattern = r"oath_sworn\s*=\s*(True|False)"

        for i, line in enumerate(source.split("\n"), 1):
            if re.search(pattern, line):
                violations.append(
                    Violation(
                        rule=self.rule_id,
                        severity=self.severity,
                        message="FORBIDDEN: Manual oath_sworn assignment. "
                        "Use TestAgents.without_oath() or TestAgents.with_false_oath().",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                    )
                )

        return violations


class RequireAssertions(Rule):
    """REQUIRED: At least one assertion per test function."""

    rule_id = "PANOPTICON_004"
    severity = "warning"
    description = "Test function should have at least one assertion."

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                has_assertion = False

                for child in ast.walk(node):
                    # Check for assert statements
                    if isinstance(child, ast.Assert):
                        has_assertion = True
                        break
                    # Check for pytest.raises, pytest.warns, etc.
                    if isinstance(child, ast.Call):
                        func = child.func
                        if isinstance(func, ast.Attribute):
                            if func.attr in ["raises", "warns", "fail"]:
                                has_assertion = True
                                break
                        if isinstance(func, ast.Name):
                            if func.id in ["assert_that", "assertEqual", "assertTrue"]:
                                has_assertion = True
                                break

                if not has_assertion:
                    violations.append(
                        Violation(
                            rule=self.rule_id,
                            severity=self.severity,
                            message=f"Test function '{node.name}' has no assertions.",
                            file_path=file_path,
                            line_number=node.lineno,
                        )
                    )

        return violations


class ForbiddenAssertTrue(Rule):
    """FORBIDDEN: assert True (meaningless test)."""

    rule_id = "PANOPTICON_005"
    severity = "warning"
    description = "assert True is meaningless."

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                # Check if asserting True or False directly
                test = node.test
                if isinstance(test, ast.Constant):
                    if test.value is True:
                        violations.append(
                            Violation(
                                rule=self.rule_id,
                                severity=self.severity,
                                message="'assert True' is meaningless - test always passes.",
                                file_path=file_path,
                                line_number=node.lineno,
                            )
                        )

        return violations


class ForbiddenBareExcept(Rule):
    """FORBIDDEN: except: pass (swallowing errors)."""

    rule_id = "PANOPTICON_006"
    severity = "critical"
    description = "Bare except swallows errors and hides failures."

    def check(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Bare except (no exception type)
                if node.type is None:
                    # Check if body is just 'pass'
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        violations.append(
                            Violation(
                                rule=self.rule_id,
                                severity=self.severity,
                                message="FORBIDDEN: 'except: pass' swallows all errors. This hides test failures.",
                                file_path=file_path,
                                line_number=node.lineno,
                            )
                        )

        return violations


# =============================================================================
# VALIDATOR
# =============================================================================


class TestValidator:
    """
    Validates test files against PANOPTICON+ rules.

    All validation is deterministic (AST + regex) - no LLM needed.
    """

    # Default rules to apply
    DEFAULT_RULES = [
        ForbiddenCustomAgentClass(),
        RequireFixtureImport(),
        ForbiddenManualOathAssignment(),
        RequireAssertions(),
        ForbiddenAssertTrue(),
        ForbiddenBareExcept(),
    ]

    def __init__(self, rules: Optional[List[Rule]] = None):
        """
        Initialize validator with rules.

        Args:
            rules: List of Rule instances (default: DEFAULT_RULES)
        """
        self.rules = rules or self.DEFAULT_RULES
        logger.info(f"TestValidator initialized with {len(self.rules)} rules")

    def validate_file(self, file_path: str | Path) -> ValidationReport:
        """
        Validate a single test file.

        Args:
            file_path: Path to test file

        Returns:
            ValidationReport with violations
        """
        file_path = Path(file_path)
        report = ValidationReport(file_path=str(file_path))

        if not file_path.exists():
            report.passed = False
            report.violations.append(
                Violation(
                    rule="FILE_NOT_FOUND",
                    severity="critical",
                    message=f"File not found: {file_path}",
                    file_path=str(file_path),
                )
            )
            return report

        try:
            source = file_path.read_text()
        except Exception as e:
            report.passed = False
            report.violations.append(
                Violation(
                    rule="FILE_READ_ERROR",
                    severity="critical",
                    message=f"Cannot read file: {e}",
                    file_path=str(file_path),
                )
            )
            return report

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            report.passed = False
            report.violations.append(
                Violation(
                    rule="SYNTAX_ERROR",
                    severity="critical",
                    message=f"Syntax error: {e}",
                    file_path=str(file_path),
                    line_number=e.lineno,
                )
            )
            return report

        # Apply all rules
        for rule in self.rules:
            try:
                violations = rule.check(str(file_path), source, tree)
                report.violations.extend(violations)
            except Exception as e:
                logger.warning(f"Rule {rule.rule_id} failed on {file_path}: {e}")

        # Determine pass/fail based on critical violations
        report.passed = not report.has_critical

        return report

    def validate_directory(
        self,
        directory: str | Path,
        pattern: str = "test_*.py",
    ) -> List[ValidationReport]:
        """
        Validate all test files in a directory.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for test files

        Returns:
            List of ValidationReports
        """
        directory = Path(directory)
        reports = []

        for test_file in directory.glob(f"**/{pattern}"):
            report = self.validate_file(test_file)
            reports.append(report)

            if report.has_critical:
                logger.warning(f"❌ {test_file}: {len(report.critical_violations)} critical violations")
            elif report.has_warnings:
                logger.info(f"⚠️  {test_file}: {len(report.warning_violations)} warnings")
            else:
                logger.debug(f"✅ {test_file}: passed")

        return reports

    def validate_and_report(
        self,
        path: str | Path,
        output_format: str = "text",
    ) -> tuple[bool, str]:
        """
        Validate and generate human-readable report.

        Args:
            path: File or directory to validate
            output_format: "text" or "json"

        Returns:
            (all_passed, report_string)
        """
        path = Path(path)

        if path.is_file():
            reports = [self.validate_file(path)]
        else:
            reports = self.validate_directory(path)

        all_passed = all(r.passed for r in reports)

        if output_format == "json":
            import json

            return all_passed, json.dumps([r.to_dict() for r in reports], indent=2)

        # Text format
        lines = ["=" * 60, "PANOPTICON+ Test Validation Report", "=" * 60, ""]

        for report in reports:
            status = "✅ PASS" if report.passed else "❌ FAIL"
            lines.append(f"{status} {report.file_path}")

            for v in report.violations:
                icon = "🚫" if v.severity == "critical" else "⚠️ " if v.severity == "warning" else "ℹ️ "
                line_info = f" (line {v.line_number})" if v.line_number else ""
                lines.append(f"  {icon} [{v.rule}]{line_info}: {v.message}")

            if report.violations:
                lines.append("")

        lines.append("=" * 60)
        total = len(reports)
        passed = sum(1 for r in reports if r.passed)
        failed = total - passed

        lines.append(f"Total: {total} files, {passed} passed, {failed} failed")

        if all_passed:
            lines.append("✅ All tests meet PANOPTICON+ standards")
        else:
            lines.append("❌ BLOCKED: Fix critical violations before commit")

        return all_passed, "\n".join(lines)


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """CLI entry point for test validation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_validator.py <path>")
        print("  path: Test file or directory to validate")
        sys.exit(1)

    path = sys.argv[1]

    validator = TestValidator()
    all_passed, report = validator.validate_and_report(path)

    print(report)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
