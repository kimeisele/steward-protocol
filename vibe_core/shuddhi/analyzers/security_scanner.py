"""
OPUS-212: WatchmanASTScanner - AST-Based Security Analysis for Watchman.

This module provides AST-based security scanning to upgrade Watchman's
regex-based FORBIDDEN_PATTERNS to proper semantic analysis.

NOTE: This is a WATCHMAN tool, not Narasimha!
- WATCHMAN: Scans and detects violations (this module helps with that)
- NARASIMHA: The Kill Switch that destroys rogue agents (vibe_core/narasimha.py)

Threat Model (High Priority):
1. Insecure Deserialization (Pickle RCE)
2. Resource Exhaustion (Subprocess without timeout)
3. XML External Entities (XXE)
4. Silent Failures (except: pass)
5. Unsafe File Operations
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class Severity(str, Enum):
    """Security violation severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SecurityViolation:
    """A detected security violation."""

    code: str
    severity: Severity
    message: str
    line: int
    col: int
    node_type: str
    fix_available: bool = False

    def __repr__(self) -> str:
        return f"[{self.severity.value}] {self.code} Line {self.line}: {self.message}"


class WatchmanASTScanner(ast.NodeVisitor):
    """
    AST-based Security Scanner for Watchman.

    Upgrades Watchman's regex patterns to semantic AST analysis:
    - Handles multi-line code correctly
    - Understands argument positions and names
    - Tracks import aliases
    - Provides precise line/column for CST bridge (Shuddhi)
    """

    # Policy: Banned Modules
    BANNED_IMPORTS: Dict[str, tuple] = {
        "pickle": ("SEC001", Severity.CRITICAL, "Pickle allows RCE. Use JSON."),
        "cPickle": ("SEC001", Severity.CRITICAL, "Pickle allows RCE. Use JSON."),
        "dill": ("SEC001", Severity.CRITICAL, "Dill allows RCE. Use JSON."),
        "shelve": (
            "SEC001",
            Severity.CRITICAL,
            "Shelve uses pickle internally. Use JSON.",
        ),
        "xml.etree.ElementTree": (
            "SEC002",
            Severity.HIGH,
            "XML parser vulnerable to XXE. Use defusedxml.",
        ),
        "xml.sax": (
            "SEC002",
            Severity.HIGH,
            "XML parser vulnerable to XXE. Use defusedxml.",
        ),
        "xml.dom.minidom": (
            "SEC002",
            Severity.HIGH,
            "XML parser vulnerable to XXE. Use defusedxml.",
        ),
        "telnetlib": ("SEC003", Severity.MEDIUM, "Telnet is insecure. Use SSH."),
        "ftplib": ("SEC004", Severity.MEDIUM, "FTP is insecure. Use SFTP."),
    }

    # Subprocess functions that need timeout
    SUBPROCESS_FUNCS: Set[str] = {"run", "call", "check_call", "check_output"}

    def __init__(self):
        self.violations: List[SecurityViolation] = []
        self.module_aliases: Dict[str, str] = {}
        self._in_try_block = False
        self._current_except_handler: Optional[ast.ExceptHandler] = None

    def visit_Import(self, node: ast.Import):
        """Check for banned imports."""
        for alias in node.names:
            name = alias.name
            asname = alias.asname or alias.name
            self.module_aliases[asname] = name

            if name in self.BANNED_IMPORTS:
                code, severity, msg = self.BANNED_IMPORTS[name]
                self.violations.append(
                    SecurityViolation(
                        code=code,
                        severity=severity,
                        message=msg,
                        line=node.lineno,
                        col=node.col_offset,
                        node_type="Import",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check for banned from-imports."""
        module = node.module or ""

        # Check full module path
        if module in self.BANNED_IMPORTS:
            code, severity, msg = self.BANNED_IMPORTS[module]
            self.violations.append(
                SecurityViolation(
                    code=code,
                    severity=severity,
                    message=msg,
                    line=node.lineno,
                    col=node.col_offset,
                    node_type="ImportFrom",
                )
            )

        # Track aliases
        for alias in node.names:
            asname = alias.asname or alias.name
            self.module_aliases[asname] = f"{module}.{alias.name}"

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check for dangerous function calls."""
        # Check subprocess calls without timeout
        self._check_subprocess_timeout(node)

        # Check pickle.load/loads
        self._check_pickle_usage(node)

        # Check eval/exec
        self._check_code_execution(node)

        # Check open() without context manager (when not in 'with')
        self._check_unsafe_open(node)

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        """Track try blocks for silent failure detection."""
        self._in_try_block = True
        for handler in node.handlers:
            self._current_except_handler = handler
            self._check_silent_except(handler)
        self._in_try_block = False
        self._current_except_handler = None
        self.generic_visit(node)

    def _check_subprocess_timeout(self, node: ast.Call):
        """Check if subprocess calls have timeout argument."""
        func_name = self._get_call_name(node)

        # Check for subprocess.run, subprocess.call, etc.
        is_subprocess = False
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module = self.module_aliases.get(node.func.value.id, node.func.value.id)
                if module == "subprocess" and node.func.attr in self.SUBPROCESS_FUNCS:
                    is_subprocess = True

        if not is_subprocess:
            return

        # Check for timeout keyword
        has_timeout = any(kw.arg == "timeout" for kw in node.keywords if kw.arg is not None)

        if not has_timeout:
            self.violations.append(
                SecurityViolation(
                    code="SEC005",
                    severity=Severity.HIGH,
                    message=f"subprocess.{node.func.attr}() called without timeout. Risk: DoS via hung process.",
                    line=node.lineno,
                    col=node.col_offset,
                    node_type="Call",
                    fix_available=True,
                )
            )

    def _check_pickle_usage(self, node: ast.Call):
        """Check for pickle.load/loads usage."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module = self.module_aliases.get(node.func.value.id, node.func.value.id)
                if module in ("pickle", "cPickle", "dill"):
                    if node.func.attr in ("load", "loads"):
                        self.violations.append(
                            SecurityViolation(
                                code="SEC001",
                                severity=Severity.CRITICAL,
                                message=f"{module}.{node.func.attr}() allows arbitrary code execution. Use JSON.",
                                line=node.lineno,
                                col=node.col_offset,
                                node_type="Call",
                            )
                        )

    def _check_code_execution(self, node: ast.Call):
        """Check for eval/exec usage."""
        func_name = self._get_call_name(node)

        if func_name in ("eval", "exec"):
            self.violations.append(
                SecurityViolation(
                    code="SEC006",
                    severity=Severity.CRITICAL,
                    message=f"{func_name}() allows arbitrary code execution.",
                    line=node.lineno,
                    col=node.col_offset,
                    node_type="Call",
                )
            )

    def _check_unsafe_open(self, node: ast.Call):
        """Check for open() in write mode without self.system."""
        func_name = self._get_call_name(node)

        if func_name == "open":
            # Check for write mode
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if "w" in arg.value or "a" in arg.value:
                        self.violations.append(
                            SecurityViolation(
                                code="SEC007",
                                severity=Severity.MEDIUM,
                                message="open() for writing detected. Use self.system.write_file() for audit trail.",
                                line=node.lineno,
                                col=node.col_offset,
                                node_type="Call",
                                fix_available=True,
                            )
                        )
                        return

            # Check keyword mode argument
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    if isinstance(kw.value.value, str):
                        if "w" in kw.value.value or "a" in kw.value.value:
                            self.violations.append(
                                SecurityViolation(
                                    code="SEC007",
                                    severity=Severity.MEDIUM,
                                    message="open() for writing detected. Use self.system.write_file().",
                                    line=node.lineno,
                                    col=node.col_offset,
                                    node_type="Call",
                                    fix_available=True,
                                )
                            )
                            return

    def _check_silent_except(self, handler: ast.ExceptHandler):
        """Check for silent exception handlers (except: pass)."""
        # Check if handler body is just 'pass' or '...'
        if len(handler.body) == 1:
            stmt = handler.body[0]
            is_silent = False

            if isinstance(stmt, ast.Pass):
                is_silent = True
            elif isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Constant) and stmt.value.value is ...:
                    is_silent = True

            if is_silent:
                exception_type = "Exception"
                if handler.type:
                    if isinstance(handler.type, ast.Name):
                        exception_type = handler.type.id
                    elif isinstance(handler.type, ast.Tuple):
                        exception_type = "multiple"

                # Bare except is worse
                severity = Severity.HIGH if handler.type is None else Severity.MEDIUM

                self.violations.append(
                    SecurityViolation(
                        code="SEC008",
                        severity=severity,
                        message=f"Silent exception handler (except {exception_type}: pass). Violations go undetected.",
                        line=handler.lineno,
                        col=handler.col_offset,
                        node_type="ExceptHandler",
                        fix_available=True,
                    )
                )

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract the function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None


def analyze_source(source_code: str) -> List[SecurityViolation]:
    """
    Analyze source code for security violations.

    Args:
        source_code: Python source code

    Returns:
        List of SecurityViolation objects
    """
    tree = ast.parse(source_code)
    guardrail = WatchmanASTScanner()
    guardrail.visit(tree)
    return guardrail.violations


def analyze_file(file_path: Path) -> List[SecurityViolation]:
    """
    Analyze a Python file for security violations.

    Args:
        file_path: Path to Python file

    Returns:
        List of SecurityViolation objects
    """
    source_code = file_path.read_text()
    return analyze_source(source_code)


def get_critical_violations(violations: List[SecurityViolation]) -> List[SecurityViolation]:
    """Filter for critical severity violations only."""
    return [v for v in violations if v.severity == Severity.CRITICAL]


def get_fixable_violations(violations: List[SecurityViolation]) -> List[SecurityViolation]:
    """Filter for violations that have automated fixes available."""
    return [v for v in violations if v.fix_available]
