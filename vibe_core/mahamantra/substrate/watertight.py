"""
WATERTIGHT - Type Integrity Verification
========================================

"na tv evāhaṁ jātu nāsaṁ na tvaṁ neme janādhipāḥ
na caiva na bhaviṣyāmaḥ sarve vayam ataḥ param"

"Never was there a time when I did not exist, nor you,
nor all these kings; nor in the future shall any of us cease to be."
— Bhagavad Gita 2.12

WATERTIGHT = NO MAYA = NO `Any` TYPES

This module verifies that the Mahamantra kernel maintains
type integrity. Like Krishna's existence, types are ETERNAL -
they don't change arbitrarily.

ANTI-MAYAVAD: Types have IDENTITY. `Any` is impersonalism.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Set, Tuple

from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# WATERTIGHT CONSTANTS
# =============================================================================

# Forbidden type patterns (Mayavad types)
FORBIDDEN_TYPES: Final[Set[str]] = {
    "Any",
    "object",  # When used as a type hint without Generic
}

# Allowed generic usages of object
ALLOWED_OBJECT_CONTEXTS: Final[Set[str]] = {
    "Protocol",
    "Generic",
    "__eq__",
    "__ne__",
    "__hash__",
}


# =============================================================================
# VERIFICATION RESULTS
# =============================================================================

@dataclass
class TypeViolation:
    """A single type violation found."""
    file: str
    line: int
    column: int
    violation_type: str  # "Any" or "object"
    context: str         # The code context


@dataclass
class WatertightReport:
    """
    Report of watertight verification.

    remainder = len(violations) % 37
    If remainder == 0, the system is connected to Parampara.
    If not, there's ego (violations) remaining.
    """
    total_files: int
    files_checked: int
    violations: List[TypeViolation]
    passed: bool

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def remainder(self) -> int:
        """
        The 'ego' remainder.

        0 = Pure (no violations OR violations % 37 == 0)
        >0 = Ego remains (impure types)
        """
        if self.violation_count == 0:
            return 0
        return self.violation_count % PARAMPARA

    @property
    def is_connected(self) -> bool:
        """Is the codebase connected to Parampara?"""
        return self.violation_count == 0


# =============================================================================
# AST VISITOR FOR TYPE CHECKING
# =============================================================================

class AnyTypeVisitor(ast.NodeVisitor):
    """
    AST visitor that finds `Any` type annotations.

    ANTI-MAYAVAD: We hunt impersonalist types.
    """

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: List[TypeViolation] = []
        self._in_allowed_context = False

    def visit_Name(self, node: ast.Name) -> None:
        """Check for bare `Any` usage."""
        if node.id == "Any":
            self.violations.append(TypeViolation(
                file=self.filename,
                line=node.lineno,
                column=node.col_offset,
                violation_type="Any",
                context=f"Bare 'Any' type at line {node.lineno}"
            ))
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Check for `Any` in subscripted types like Dict[str, Any]."""
        self._check_subscript_for_any(node)
        self.generic_visit(node)

    def _check_subscript_for_any(self, node: ast.Subscript) -> None:
        """Recursively check subscript for Any."""
        if isinstance(node.slice, ast.Name) and node.slice.id == "Any":
            self.violations.append(TypeViolation(
                file=self.filename,
                line=node.lineno,
                column=node.col_offset,
                violation_type="Any",
                context=f"'Any' in generic type at line {node.lineno}"
            ))
        elif isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                if isinstance(elt, ast.Name) and elt.id == "Any":
                    self.violations.append(TypeViolation(
                        file=self.filename,
                        line=node.lineno,
                        column=node.col_offset,
                        violation_type="Any",
                        context=f"'Any' in generic type at line {node.lineno}"
                    ))


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

def check_file(filepath: Path) -> List[TypeViolation]:
    """
    Check a single Python file for type violations.

    Returns list of violations found.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        return [TypeViolation(
            file=str(filepath),
            line=0,
            column=0,
            violation_type="ParseError",
            context=str(e)
        )]

    visitor = AnyTypeVisitor(str(filepath))
    visitor.visit(tree)
    return visitor.violations


def check_directory(dirpath: Path, exclude_patterns: Optional[List[str]] = None) -> WatertightReport:
    """
    Check all Python files in a directory for type violations.

    Args:
        dirpath: Directory to check
        exclude_patterns: Patterns to exclude (e.g., ["__pycache__", "test_"])

    Returns:
        WatertightReport with all findings
    """
    exclude = exclude_patterns or ["__pycache__", ".git", "venv", "node_modules"]

    all_files: List[Path] = []
    for pyfile in dirpath.rglob("*.py"):
        # Skip excluded patterns
        skip = False
        for pattern in exclude:
            if pattern in str(pyfile):
                skip = True
                break
        if not skip:
            all_files.append(pyfile)

    all_violations: List[TypeViolation] = []
    files_checked = 0

    for filepath in all_files:
        violations = check_file(filepath)
        all_violations.extend(violations)
        files_checked += 1

    return WatertightReport(
        total_files=len(all_files),
        files_checked=files_checked,
        violations=all_violations,
        passed=len(all_violations) == 0
    )


def verify_watertight(path: Optional[Path] = None) -> WatertightReport:
    """
    Verify that the mahamantra kernel is watertight.

    Default: checks vibe_core/mahamantra/
    """
    if path is None:
        # Default to mahamantra directory
        path = Path(__file__).parent

    return check_directory(path)


def print_report(report: WatertightReport) -> None:
    """Print a human-readable watertight report."""
    print("=" * 60)
    print("WATERTIGHT VERIFICATION REPORT")
    print("=" * 60)
    print(f"Files checked: {report.files_checked}/{report.total_files}")
    print(f"Violations: {report.violation_count}")
    print(f"Remainder (ego): {report.remainder}")
    print(f"Connected to Parampara: {report.is_connected}")
    print()

    if report.violations:
        print("VIOLATIONS:")
        for v in report.violations[:10]:  # Show first 10
            print(f"  {v.file}:{v.line}:{v.column} - {v.violation_type}")
            print(f"    {v.context}")
        if len(report.violations) > 10:
            print(f"  ... and {len(report.violations) - 10} more")
    else:
        print("NO VIOLATIONS - WATERTIGHT!")

    print("=" * 60)


# =============================================================================
# QUICK VERIFICATION
# =============================================================================

def is_watertight() -> bool:
    """Quick check: Is the mahamantra kernel watertight?"""
    report = verify_watertight()
    return report.passed


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "TypeViolation",
    "WatertightReport",
    # Functions
    "check_file",
    "check_directory",
    "verify_watertight",
    "print_report",
    "is_watertight",
    # Constants
    "FORBIDDEN_TYPES",
]
