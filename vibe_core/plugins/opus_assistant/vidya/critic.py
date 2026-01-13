"""
VIDYA Critic - Static Analysis and Code Validation.

OPUS-033: THE CORE LOGIC of VIDYA

"No code without validation. No deployment without proof."

The Critic is the ONLY real logic in VIDYA. Everything else is orchestration.
This module performs static analysis on generated code to ensure safety
before it enters the system.

Checks:
1. Syntax Validation (compile())
2. AST Analysis (dangerous pattern detection)
3. Import Whitelist (prevent dangerous module imports)
4. Code Quality (basic linting)

The Critic is the Narasimha of VIDYA - the protector that ensures
only safe code enters the kingdom.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa006b9e9"  # GenesisByte: parampara % 37 == 0

import ast
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("VIDYA.Critic")


class Severity(Enum):
    """Severity levels for critic findings."""

    INFO = "info"  # Style/quality suggestion
    WARNING = "warning"  # Potential issue, review recommended
    ERROR = "error"  # Security risk, must fix
    CRITICAL = "critical"  # Immediate threat, BLOCK


@dataclass
class Finding:
    """A single finding from code analysis."""

    severity: Severity
    code: str  # e.g., "DANGEROUS_EXEC"
    message: str  # Human-readable description
    line: Optional[int] = None
    column: Optional[int] = None
    node_type: Optional[str] = None


@dataclass
class CriticResult:
    """Result of code critique."""

    passed: bool  # True if code is safe to deploy
    syntax_valid: bool  # True if code compiles
    findings: List[Finding] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "syntax_valid": self.syntax_valid,
            "findings": [
                {
                    "severity": f.severity.value,
                    "code": f.code,
                    "message": f.message,
                    "line": f.line,
                    "column": f.column,
                }
                for f in self.findings
            ],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "critical_count": self.critical_count,
            "summary": self.summary,
        }


class DangerousPatternVisitor(ast.NodeVisitor):
    """AST visitor that detects dangerous code patterns."""

    # Dangerous built-in functions
    DANGEROUS_CALLS: Set[str] = {
        "exec",
        "eval",
        "compile",
        "__import__",
        "open",  # Only dangerous with write mode
        "input",  # Can hang in automated contexts
    }

    # Dangerous modules
    DANGEROUS_MODULES: Set[str] = {
        "os",  # System calls
        "subprocess",  # Command execution
        "sys",  # System manipulation
        "shutil",  # File operations
        "socket",  # Network operations
        "requests",  # HTTP (external calls)
        "urllib",  # HTTP
        "pickle",  # Deserialization attacks
        "marshal",  # Deserialization
        "ctypes",  # C interface
        "multiprocessing",  # Process spawning
    }

    # Whitelisted os functions (safe subset)
    OS_WHITELIST: Set[str] = {
        "path",
        "getcwd",
        "path.join",
        "path.exists",
        "path.isfile",
        "path.isdir",
        "path.dirname",
        "path.basename",
        "environ.get",
    }

    def __init__(self):
        self.findings: List[Finding] = []
        self._imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements."""
        for alias in node.names:
            module_name = alias.name.split(".")[0]
            self._imported_modules.add(module_name)

            if module_name in self.DANGEROUS_MODULES:
                self.findings.append(
                    Finding(
                        severity=Severity.ERROR,
                        code="DANGEROUS_IMPORT",
                        message=f"Import of dangerous module '{module_name}' detected",
                        line=node.lineno,
                        column=node.col_offset,
                        node_type="Import",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from X import Y statements."""
        if node.module:
            module_name = node.module.split(".")[0]
            self._imported_modules.add(module_name)

            if module_name in self.DANGEROUS_MODULES:
                # Check if it's a whitelisted submodule
                full_import = node.module
                is_whitelisted = any(
                    full_import.startswith(f"os.{w}")
                    or full_import == "os"
                    and any(alias.name in self.OS_WHITELIST for alias in node.names)
                    for w in self.OS_WHITELIST
                )

                if not is_whitelisted:
                    self.findings.append(
                        Finding(
                            severity=Severity.ERROR,
                            code="DANGEROUS_IMPORT",
                            message=f"Import from dangerous module '{module_name}' detected",
                            line=node.lineno,
                            column=node.col_offset,
                            node_type="ImportFrom",
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for dangerous patterns."""
        # Get the function name
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Check for dangerous built-ins
        if func_name in self.DANGEROUS_CALLS:
            severity = Severity.CRITICAL if func_name in {"exec", "eval"} else Severity.ERROR
            self.findings.append(
                Finding(
                    severity=severity,
                    code=f"DANGEROUS_{func_name.upper()}",
                    message=f"Call to dangerous function '{func_name}()' detected",
                    line=node.lineno,
                    column=node.col_offset,
                    node_type="Call",
                )
            )

        # Check for subprocess with shell=True
        if func_name in {"run", "call", "Popen", "check_output", "check_call"}:
            for keyword in node.keywords:
                if keyword.arg == "shell":
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        self.findings.append(
                            Finding(
                                severity=Severity.CRITICAL,
                                code="SHELL_INJECTION",
                                message="subprocess with shell=True is a security risk",
                                line=node.lineno,
                                column=node.col_offset,
                                node_type="Call",
                            )
                        )

        # Check for os.system
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "os" and node.func.attr == "system":
                    self.findings.append(
                        Finding(
                            severity=Severity.CRITICAL,
                            code="OS_SYSTEM",
                            message="os.system() is dangerous - use subprocess with shell=False",
                            line=node.lineno,
                            column=node.col_offset,
                            node_type="Call",
                        )
                    )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for dangerous attribute access."""
        # Detect __builtins__ access
        if node.attr == "__builtins__":
            self.findings.append(
                Finding(
                    severity=Severity.CRITICAL,
                    code="BUILTINS_ACCESS",
                    message="Direct access to __builtins__ is not allowed",
                    line=node.lineno,
                    column=node.col_offset,
                    node_type="Attribute",
                )
            )

        # Detect __globals__ access
        if node.attr == "__globals__":
            self.findings.append(
                Finding(
                    severity=Severity.CRITICAL,
                    code="GLOBALS_ACCESS",
                    message="Direct access to __globals__ is not allowed",
                    line=node.lineno,
                    column=node.col_offset,
                    node_type="Attribute",
                )
            )

        self.generic_visit(node)


class Critic:
    """
    Code Critic - Validates generated code before deployment.

    The Critic is the guardian that ensures only safe code enters the system.
    It performs multiple levels of analysis:
    1. Syntax validation
    2. AST-based dangerous pattern detection
    3. Import analysis
    4. Code quality checks
    """

    def __init__(self):
        """Initialize the Critic."""
        self._pattern_checks = self._register_pattern_checks()

    def _register_pattern_checks(self) -> List[callable]:
        """Register regex-based pattern checks."""
        return [
            self._check_string_exec,
            self._check_hardcoded_secrets,
            self._check_infinite_loops,
        ]

    def validate(self, code: str, filename: str = "<generated>") -> CriticResult:
        """
        Validate code for safety and correctness.

        Args:
            code: Python source code to validate
            filename: Optional filename for error messages

        Returns:
            CriticResult with pass/fail status and findings
        """
        findings: List[Finding] = []
        syntax_valid = True

        # Step 1: Syntax validation
        try:
            compile(code, filename, "exec")
            logger.debug("✅ Syntax validation passed")
        except SyntaxError as e:
            syntax_valid = False
            findings.append(
                Finding(
                    severity=Severity.CRITICAL,
                    code="SYNTAX_ERROR",
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno,
                    column=e.offset,
                )
            )
            # Can't continue with AST analysis if syntax is invalid
            return self._build_result(findings, syntax_valid)

        # Step 2: AST analysis
        try:
            tree = ast.parse(code)
            visitor = DangerousPatternVisitor()
            visitor.visit(tree)
            findings.extend(visitor.findings)
            logger.debug(f"✅ AST analysis complete: {len(visitor.findings)} findings")
        except Exception as e:
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="AST_PARSE_ERROR",
                    message=f"AST parsing failed: {e}",
                )
            )

        # Step 3: Regex-based pattern checks
        for check in self._pattern_checks:
            check_findings = check(code)
            findings.extend(check_findings)

        return self._build_result(findings, syntax_valid)

    def _build_result(self, findings: List[Finding], syntax_valid: bool) -> CriticResult:
        """Build the final CriticResult from findings."""
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        error_count = sum(1 for f in findings if f.severity == Severity.ERROR)
        warning_count = sum(1 for f in findings if f.severity == Severity.WARNING)

        # Pass only if no critical or error findings
        passed = critical_count == 0 and error_count == 0 and syntax_valid

        # Generate summary
        if passed:
            summary = "✅ Code validation passed - safe to deploy"
        else:
            issues = []
            if critical_count > 0:
                issues.append(f"{critical_count} critical")
            if error_count > 0:
                issues.append(f"{error_count} errors")
            if not syntax_valid:
                issues.append("syntax invalid")
            summary = f"❌ Code validation failed: {', '.join(issues)}"

        return CriticResult(
            passed=passed,
            syntax_valid=syntax_valid,
            findings=findings,
            error_count=error_count,
            warning_count=warning_count,
            critical_count=critical_count,
            summary=summary,
        )

    def _check_string_exec(self, code: str) -> List[Finding]:
        """Check for exec/eval hidden in strings."""
        findings = []
        patterns = [
            (r'["\']exec\s*\(["\']', "HIDDEN_EXEC"),
            (r'["\']eval\s*\(["\']', "HIDDEN_EVAL"),
            (r'getattr\s*\([^,]+,\s*["\']__', "GETATTR_DUNDER"),
        ]

        for pattern, code_name in patterns:
            for match in re.finditer(pattern, code):
                # Find line number
                line_num = code[: match.start()].count("\n") + 1
                findings.append(
                    Finding(
                        severity=Severity.WARNING,
                        code=code_name,
                        message=f"Suspicious pattern detected: {pattern}",
                        line=line_num,
                    )
                )

        return findings

    def _check_hardcoded_secrets(self, code: str) -> List[Finding]:
        """Check for hardcoded secrets/API keys."""
        findings = []
        patterns = [
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "HARDCODED_API_KEY"),
            (r'password\s*=\s*["\'][^"\']+["\']', "HARDCODED_PASSWORD"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "HARDCODED_SECRET"),
            (r'token\s*=\s*["\'][^"\']+["\']', "HARDCODED_TOKEN"),
        ]

        for pattern, code_name in patterns:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                line_num = code[: match.start()].count("\n") + 1
                findings.append(
                    Finding(
                        severity=Severity.WARNING,
                        code=code_name,
                        message="Potential hardcoded credential detected",
                        line=line_num,
                    )
                )

        return findings

    def _check_infinite_loops(self, code: str) -> List[Finding]:
        """Check for potential infinite loops."""
        findings = []

        # Simple pattern: while True without break
        if "while True:" in code or "while 1:" in code:
            # Check if there's a break in the same scope
            # This is a simplistic check - AST would be better
            if "break" not in code:
                findings.append(
                    Finding(
                        severity=Severity.WARNING,
                        code="POTENTIAL_INFINITE_LOOP",
                        message="while True loop without visible break statement",
                    )
                )

        return findings

    def quick_check(self, code: str) -> bool:
        """
        Quick pass/fail check without detailed findings.

        Args:
            code: Python source code

        Returns:
            True if code passes basic safety checks
        """
        result = self.validate(code)
        return result.passed


# Convenience function
def validate_code(code: str, filename: str = "<generated>") -> CriticResult:
    """Convenience function for code validation."""
    critic = Critic()
    return critic.validate(code, filename)
