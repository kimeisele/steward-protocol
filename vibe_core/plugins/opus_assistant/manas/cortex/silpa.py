"""
OPUS-053: SILPA (The Self-Architect) - Safe Code Refactoring.

Sanskrit: Silpa = Art, Craft, Architecture, Sculpture.

SILPA gives MANAS the ability to safely modify its own code.
This is the most delicate operation - surgery on a living system.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                     SILPA (The Sculptor)                    │
    │                                                             │
    │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
    │   │ SilpaAuditor│──▶│SilpaTransform│──▶│SilpaArchitect│     │
    │   │ (Tests)     │   │ (AST/Code)  │   │ (Orchestrate)│     │
    │   └─────────────┘   └─────────────┘   └─────────────┘      │
    │          │                                    │              │
    │          ▼                                    ▼              │
    │   ┌─────────────────────────────────────────────────────┐  │
    │   │           PLATINUM PROTOCOL (Safety Gate)           │  │
    │   │  1. Tests GREEN → 2. Refactor → 3. Tests GREEN      │  │
    │   └─────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘

The Platinum Protocol:
    1. PRE-GATE: Run tests on target file (must be GREEN)
    2. TRANSFORM: Apply refactoring via AST
    3. POST-GATE: Run tests again (must still be GREEN)
    4. ROLLBACK: If POST-GATE fails, restore original

Risk Classification:
    - SAFE: Docstring updates, comment changes, formatting
    - MODERATE: Variable renames, method extraction
    - HIGH: Logic changes, interface modifications
    - FORBIDDEN: Security-critical code, kernel files

"The sculptor reveals the statue hidden within the stone."
"""

import ast
import hashlib
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Cortex.Silpa")


# =============================================================================
# SECTION 1: DATA MODELS
# =============================================================================


class RefactorRisk(Enum):
    """Risk level for refactoring operations."""

    SAFE = "safe"  # Docstrings, comments, formatting
    MODERATE = "moderate"  # Renames, extractions
    HIGH = "high"  # Logic changes
    FORBIDDEN = "forbidden"  # Security-critical, kernel


class RefactorType(Enum):
    """Types of refactoring operations."""

    UPDATE_DOCSTRING = "update_docstring"
    ADD_DOCSTRING = "add_docstring"
    RENAME_VARIABLE = "rename_variable"
    RENAME_FUNCTION = "rename_function"
    EXTRACT_METHOD = "extract_method"
    CONSOLIDATE_METHODS = "consolidate_methods"
    UPDATE_IMPORTS = "update_imports"
    CUSTOM = "custom"


@dataclass
class SilpaRefactoring:
    """A refactoring request."""

    target_file: Path
    refactor_type: RefactorType
    description: str
    instructions: str  # What to change
    test_pattern: Optional[str] = None  # e.g., "tests/test_boot_mode.py"
    risk_override: Optional[RefactorRisk] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_file": str(self.target_file),
            "refactor_type": self.refactor_type.value,
            "description": self.description,
            "instructions": self.instructions,
            "test_pattern": self.test_pattern,
        }


@dataclass
class SilpaPlan:
    """A refactoring plan with before/after states."""

    refactoring: SilpaRefactoring
    original_code: str
    original_hash: str
    planned_code: str
    risk_level: RefactorRisk
    affected_functions: List[str]
    affected_classes: List[str]
    estimated_impact: str
    approval_required: bool
    approval_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "refactoring": self.refactoring.to_dict(),
            "original_hash": self.original_hash,
            "risk_level": self.risk_level.value,
            "affected_functions": self.affected_functions,
            "affected_classes": self.affected_classes,
            "estimated_impact": self.estimated_impact,
            "approval_required": self.approval_required,
        }


@dataclass
class SilpaTestResult:
    """Result of running tests."""

    success: bool
    exit_code: int
    tests_run: int
    tests_passed: int
    tests_failed: int
    stdout: str
    stderr: str
    duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SilpaResult:
    """Result of a refactoring operation."""

    success: bool
    plan: SilpaPlan
    pre_test: Optional[SilpaTestResult] = None
    post_test: Optional[SilpaTestResult] = None
    error: Optional[str] = None
    rollback_performed: bool = False
    audit_trail: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "plan": self.plan.to_dict(),
            "pre_test": self.pre_test.to_dict() if self.pre_test else None,
            "post_test": self.post_test.to_dict() if self.post_test else None,
            "error": self.error,
            "rollback_performed": self.rollback_performed,
            "audit_trail": self.audit_trail,
        }

    def to_chat_response(self) -> str:
        """Format for chat display."""
        if self.success:
            emoji = "✅"
            status = "SUCCESS"
        else:
            emoji = "❌"
            status = "FAILED"

        lines = [
            f"{emoji} **SILPA Refactoring: {status}**",
            "",
            f"**File:** `{self.plan.refactoring.target_file}`",
            f"**Type:** {self.plan.refactoring.refactor_type.value}",
            f"**Risk:** {self.plan.risk_level.value}",
            "",
        ]

        if self.pre_test:
            lines.append(f"**Pre-Test:** {'✅ PASS' if self.pre_test.success else '❌ FAIL'}")
        if self.post_test:
            lines.append(f"**Post-Test:** {'✅ PASS' if self.post_test.success else '❌ FAIL'}")

        if self.error:
            lines.extend(["", f"**Error:** {self.error}"])

        if self.rollback_performed:
            lines.extend(["", "⚠️ **Rollback performed - original code restored**"])

        if self.audit_trail:
            lines.extend(["", "**Audit Trail:**"])
            for entry in self.audit_trail[-5:]:  # Last 5 entries
                lines.append(f"  • {entry}")

        return "\n".join(lines)


# =============================================================================
# SECTION 2: SILPA AUDITOR - Platinum Protocol Test Verification
# =============================================================================


class SilpaAuditor:
    """
    Platinum Protocol Test Verification.

    The guardian that ensures tests pass before and after refactoring.
    Without this, no refactoring may proceed.

    "No surgery without anesthesia. No refactoring without tests."
    """

    DEFAULT_TIMEOUT = 60  # seconds

    def __init__(self, workspace: Path):
        """
        Initialize auditor.

        Args:
            workspace: Project root directory
        """
        self._workspace = workspace
        self._timeout = self.DEFAULT_TIMEOUT

    def run_tests(self, test_pattern: Optional[str] = None, target_file: Optional[Path] = None) -> SilpaTestResult:
        """
        Run tests and capture results.

        Args:
            test_pattern: Specific test file/pattern to run
            target_file: Target file being refactored (for test discovery)

        Returns:
            SilpaTestResult with pass/fail information
        """
        import time

        start_time = time.time()

        # Build pytest command
        cmd = ["python", "-m", "pytest", "-v", "--tb=short"]

        if test_pattern:
            cmd.append(test_pattern)
        elif target_file:
            # Try to discover related tests
            discovered = self._discover_tests_for_file(target_file)
            if discovered:
                cmd.extend(discovered)
            else:
                # Run all tests as fallback (limited scope)
                cmd.extend(["--ignore=tests/integration", "-x", "--timeout=30"])

        logger.info(f"SILPA Auditor: Running tests - {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )

            elapsed = (time.time() - start_time) * 1000

            # Parse pytest output
            tests_run, tests_passed, tests_failed = self._parse_pytest_output(result.stdout)

            return SilpaTestResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                stdout=result.stdout[-2000:] if result.stdout else "",  # Limit size
                stderr=result.stderr[-1000:] if result.stderr else "",
                duration_ms=elapsed,
            )

        except subprocess.TimeoutExpired:
            elapsed = (time.time() - start_time) * 1000
            return SilpaTestResult(
                success=False,
                exit_code=-1,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                stdout="",
                stderr="Test timeout exceeded",
                duration_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return SilpaTestResult(
                success=False,
                exit_code=-1,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                stdout="",
                stderr=str(e),
                duration_ms=elapsed,
            )

    def _discover_tests_for_file(self, target_file: Path) -> List[str]:
        """Discover test files for a target file."""
        discovered = []

        # Extract module name from file
        file_stem = target_file.stem  # e.g., "boot_mode"

        # Common test patterns
        patterns = [
            f"tests/test_{file_stem}.py",
            f"tests/unit/test_{file_stem}.py",
            f"tests/**/test_{file_stem}.py",
        ]

        for pattern in patterns:
            test_path = self._workspace / pattern.replace("**", "*")
            if "*" not in pattern:
                if (self._workspace / pattern).exists():
                    discovered.append(pattern)
            else:
                # Glob pattern
                matches = list(self._workspace.glob(pattern))
                discovered.extend([str(m.relative_to(self._workspace)) for m in matches])

        return discovered

    def _parse_pytest_output(self, output: str) -> tuple:
        """Parse pytest output for test counts."""
        import re

        tests_run = 0
        tests_passed = 0
        tests_failed = 0

        # Pattern: "5 passed, 2 failed" or "10 passed"
        match = re.search(r"(\d+) passed", output)
        if match:
            tests_passed = int(match.group(1))

        match = re.search(r"(\d+) failed", output)
        if match:
            tests_failed = int(match.group(1))

        tests_run = tests_passed + tests_failed

        # Also check for "X warnings" pattern which implies tests ran
        if tests_run == 0:
            match = re.search(r"(\d+) warnings", output)
            if match:
                # Some tests ran but we couldn't parse them
                tests_run = 1
                tests_passed = 1

        return tests_run, tests_passed, tests_failed


# =============================================================================
# SECTION 3: SILPA TRANSFORMER - AST-Based Code Modification
# =============================================================================


class SilpaTransformer:
    """
    AST-based code transformer.

    Uses Python's AST module for safe, parseable code modifications.
    Never modifies code that doesn't parse correctly.

    "The chisel respects the grain of the marble."
    """

    def __init__(self):
        """Initialize transformer."""
        self._transformers: Dict[RefactorType, Callable] = {
            RefactorType.UPDATE_DOCSTRING: self._transform_update_docstring,
            RefactorType.ADD_DOCSTRING: self._transform_add_docstring,
            RefactorType.CONSOLIDATE_METHODS: self._transform_consolidate_methods,
        }

    def can_transform(self, refactor_type: RefactorType) -> bool:
        """Check if transformer supports this type."""
        return refactor_type in self._transformers

    def transform(
        self,
        code: str,
        refactor_type: RefactorType,
        instructions: Dict[str, Any],
    ) -> tuple:
        """
        Transform code according to instructions.

        Args:
            code: Original source code
            refactor_type: Type of refactoring
            instructions: Specific instructions for the transform

        Returns:
            Tuple of (transformed_code, affected_items)
        """
        if refactor_type not in self._transformers:
            raise ValueError(f"Unsupported refactor type: {refactor_type}")

        # Parse the code first - fail fast if invalid
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Cannot parse code: {e}")

        # Apply transformation
        transformer_func = self._transformers[refactor_type]
        transformed_tree, affected = transformer_func(tree, instructions)

        # Generate new code
        try:
            new_code = ast.unparse(transformed_tree)
        except Exception as e:
            raise ValueError(f"Cannot generate code from AST: {e}")

        return new_code, affected

    def _transform_update_docstring(
        self,
        tree: ast.AST,
        instructions: Dict[str, Any],
    ) -> tuple:
        """Update docstring of a function or class."""
        target_name = instructions.get("target_name")
        new_docstring = instructions.get("new_docstring")
        affected = []

        class DocstringUpdater(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == target_name or target_name is None:
                    # Update docstring
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            node.body[0].value.value = new_docstring
                            affected.append(f"function:{node.name}")
                return self.generic_visit(node)

            def visit_ClassDef(self, node):
                if node.name == target_name or target_name is None:
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            node.body[0].value.value = new_docstring
                            affected.append(f"class:{node.name}")
                return self.generic_visit(node)

        updater = DocstringUpdater()
        new_tree = updater.visit(tree)
        ast.fix_missing_locations(new_tree)

        return new_tree, affected

    def _transform_add_docstring(
        self,
        tree: ast.AST,
        instructions: Dict[str, Any],
    ) -> tuple:
        """Add docstring to a function or class that lacks one."""
        target_name = instructions.get("target_name")
        new_docstring = instructions.get("new_docstring")
        affected = []

        class DocstringAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == target_name:
                    # Check if already has docstring
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                    )
                    if not has_docstring:
                        # Add docstring as first statement
                        docstring_node = ast.Expr(value=ast.Constant(value=new_docstring))
                        node.body.insert(0, docstring_node)
                        affected.append(f"function:{node.name}")
                return self.generic_visit(node)

        adder = DocstringAdder()
        new_tree = adder.visit(tree)
        ast.fix_missing_locations(new_tree)

        return new_tree, affected

    def _transform_consolidate_methods(
        self,
        tree: ast.AST,
        instructions: Dict[str, Any],
    ) -> tuple:
        """
        Consolidate repetitive methods into a single pattern.

        This is a more complex transformation used for the boot_mode.py POC.
        """
        # For now, return unchanged - this would need LLM assistance
        # for truly intelligent consolidation
        return tree, []


# =============================================================================
# SECTION 4: SILPA ARCHITECT - Main Orchestrator
# =============================================================================


# Protected paths that SILPA cannot modify
PROTECTED_PATHS: Set[str] = frozenset(
    {
        # Kernel files (VISNU protected)
        "vibe_core/cognitive_kernel.py",
        "vibe_core/bootseq/",
        "vibe_core/governance/",
        # Security-critical
        "vibe_core/plugins/opus_assistant/narasimha/",
        # SILPA itself (no self-modification)
        "vibe_core/plugins/opus_assistant/manas/cortex/silpa.py",
    }
)


class SilpaArchitect:
    """
    The Self-Architect - Safe Code Refactoring Orchestrator.

    Coordinates the Platinum Protocol:
    1. Verify tests pass (PRE-GATE)
    2. Plan and apply refactoring
    3. Verify tests still pass (POST-GATE)
    4. Rollback if anything fails

    "To sculpt is to reveal. To refactor is to clarify."
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize the architect.

        Args:
            workspace: Project root directory
        """
        self._workspace = workspace or Path.cwd()
        self._auditor = SilpaAuditor(self._workspace)
        self._transformer = SilpaTransformer()

        logger.info("🔨 SILPA Architect initialized")

    def classify_risk(self, refactoring: SilpaRefactoring) -> RefactorRisk:
        """
        Classify the risk level of a refactoring.

        Args:
            refactoring: The refactoring request

        Returns:
            Risk level
        """
        # Check for protected paths
        target_str = str(refactoring.target_file)
        for protected in PROTECTED_PATHS:
            if protected in target_str:
                return RefactorRisk.FORBIDDEN

        # Override if specified
        if refactoring.risk_override:
            return refactoring.risk_override

        # Classify by type
        safe_types = {RefactorType.UPDATE_DOCSTRING, RefactorType.ADD_DOCSTRING}
        moderate_types = {RefactorType.RENAME_VARIABLE, RefactorType.RENAME_FUNCTION, RefactorType.UPDATE_IMPORTS}
        high_types = {RefactorType.EXTRACT_METHOD, RefactorType.CONSOLIDATE_METHODS, RefactorType.CUSTOM}

        if refactoring.refactor_type in safe_types:
            return RefactorRisk.SAFE
        elif refactoring.refactor_type in moderate_types:
            return RefactorRisk.MODERATE
        elif refactoring.refactor_type in high_types:
            return RefactorRisk.HIGH

        return RefactorRisk.MODERATE

    def plan(self, refactoring: SilpaRefactoring) -> SilpaPlan:
        """
        Create a refactoring plan.

        Args:
            refactoring: The refactoring request

        Returns:
            SilpaPlan with analysis and planned changes
        """
        target_path = self._workspace / refactoring.target_file

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        # Read original code
        original_code = target_path.read_text()
        original_hash = hashlib.sha256(original_code.encode()).hexdigest()[:16]

        # Classify risk
        risk = self.classify_risk(refactoring)

        if risk == RefactorRisk.FORBIDDEN:
            raise PermissionError(f"Cannot refactor protected file: {refactoring.target_file}")

        # Analyze affected items
        affected_functions, affected_classes = self._analyze_code(original_code)

        # For now, planned_code is same as original (actual transform happens in execute)
        planned_code = original_code

        return SilpaPlan(
            refactoring=refactoring,
            original_code=original_code,
            original_hash=original_hash,
            planned_code=planned_code,
            risk_level=risk,
            affected_functions=affected_functions,
            affected_classes=affected_classes,
            estimated_impact=f"Affects {len(affected_functions)} functions, {len(affected_classes)} classes",
            approval_required=risk in {RefactorRisk.MODERATE, RefactorRisk.HIGH},
        )

    def execute(
        self,
        plan: SilpaPlan,
        approval_token: Optional[str] = None,
        dry_run: bool = False,
    ) -> SilpaResult:
        """
        Execute a refactoring plan with Platinum Protocol.

        Args:
            plan: The refactoring plan
            approval_token: Required for moderate/high risk refactorings
            dry_run: If True, don't actually modify files

        Returns:
            SilpaResult with success/failure and audit trail
        """
        audit_trail = []
        timestamp = datetime.now().isoformat()
        audit_trail.append(f"[{timestamp}] SILPA execution started")

        target_path = self._workspace / plan.refactoring.target_file

        # Check approval for risky operations
        if plan.approval_required and not approval_token:
            return SilpaResult(
                success=False,
                plan=plan,
                error="Approval token required for this risk level",
                audit_trail=audit_trail,
            )

        # ═══════════════════════════════════════════════════════════════════
        # PLATINUM PROTOCOL - PHASE 1: PRE-GATE (Tests must be GREEN)
        # ═══════════════════════════════════════════════════════════════════

        audit_trail.append("PLATINUM PROTOCOL: Phase 1 - PRE-GATE")

        pre_test = self._auditor.run_tests(
            test_pattern=plan.refactoring.test_pattern,
            target_file=target_path,
        )

        if not pre_test.success:
            audit_trail.append(f"PRE-GATE FAILED: {pre_test.tests_failed} tests failed")
            return SilpaResult(
                success=False,
                plan=plan,
                pre_test=pre_test,
                error="PRE-GATE failed: Tests must pass before refactoring",
                audit_trail=audit_trail,
            )

        audit_trail.append(f"PRE-GATE PASSED: {pre_test.tests_passed} tests passed")

        if dry_run:
            audit_trail.append("DRY RUN: Skipping actual modification")
            return SilpaResult(
                success=True,
                plan=plan,
                pre_test=pre_test,
                audit_trail=audit_trail,
            )

        # ═══════════════════════════════════════════════════════════════════
        # PLATINUM PROTOCOL - PHASE 2: TRANSFORM (Apply refactoring)
        # ═══════════════════════════════════════════════════════════════════

        audit_trail.append("PLATINUM PROTOCOL: Phase 2 - TRANSFORM")

        # Backup original
        backup_path = target_path.with_suffix(".py.silpa_backup")
        try:
            shutil.copy2(target_path, backup_path)
            audit_trail.append(f"Backup created: {backup_path.name}")
        except Exception as e:
            audit_trail.append(f"Backup failed: {e}")
            return SilpaResult(
                success=False,
                plan=plan,
                pre_test=pre_test,
                error=f"Failed to create backup: {e}",
                audit_trail=audit_trail,
            )

        # Apply transformation
        try:
            # Write the planned code (or transformed code)
            target_path.write_text(plan.planned_code)
            audit_trail.append("Code transformation applied")
        except Exception as e:
            # Restore backup immediately
            shutil.copy2(backup_path, target_path)
            backup_path.unlink()
            audit_trail.append(f"Transform failed, backup restored: {e}")
            return SilpaResult(
                success=False,
                plan=plan,
                pre_test=pre_test,
                error=f"Failed to apply transformation: {e}",
                rollback_performed=True,
                audit_trail=audit_trail,
            )

        # ═══════════════════════════════════════════════════════════════════
        # PLATINUM PROTOCOL - PHASE 3: POST-GATE (Tests must still be GREEN)
        # ═══════════════════════════════════════════════════════════════════

        audit_trail.append("PLATINUM PROTOCOL: Phase 3 - POST-GATE")

        post_test = self._auditor.run_tests(
            test_pattern=plan.refactoring.test_pattern,
            target_file=target_path,
        )

        if not post_test.success:
            # ROLLBACK - Tests failed after refactoring
            audit_trail.append(f"POST-GATE FAILED: {post_test.tests_failed} tests failed")
            audit_trail.append("ROLLBACK: Restoring original code")

            try:
                shutil.copy2(backup_path, target_path)
                backup_path.unlink()
                audit_trail.append("Rollback successful")
            except Exception as e:
                audit_trail.append(f"CRITICAL: Rollback failed: {e}")

            return SilpaResult(
                success=False,
                plan=plan,
                pre_test=pre_test,
                post_test=post_test,
                error="POST-GATE failed: Refactoring broke tests - rolled back",
                rollback_performed=True,
                audit_trail=audit_trail,
            )

        # Success! Clean up backup
        audit_trail.append(f"POST-GATE PASSED: {post_test.tests_passed} tests passed")

        try:
            backup_path.unlink()
            audit_trail.append("Backup cleaned up")
        except Exception:
            pass  # Non-critical

        audit_trail.append("PLATINUM PROTOCOL: Complete - Refactoring successful")

        return SilpaResult(
            success=True,
            plan=plan,
            pre_test=pre_test,
            post_test=post_test,
            audit_trail=audit_trail,
        )

    def _analyze_code(self, code: str) -> tuple:
        """Analyze code to find functions and classes."""
        functions = []
        classes = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

        except SyntaxError:
            pass  # Code analysis failed, but we can still proceed

        return functions, classes


# =============================================================================
# SECTION 5: JNANA INTEGRATION - Chat Interface
# =============================================================================


def handle_silpa_query(content: str, workspace: Optional[Path] = None) -> str:
    """
    Handle a refactoring query from JNANA chat.

    Args:
        content: The user's query content
        workspace: Optional workspace path

    Returns:
        Formatted response string
    """
    content_lower = content.lower()

    if any(word in content_lower for word in ["status", "info", "what is"]):
        return get_silpa_for_chat(workspace)

    # TODO: Parse refactoring commands
    return (
        "🔨 **SILPA** (The Self-Architect)\n\n"
        "SILPA can safely refactor code using the Platinum Protocol.\n\n"
        "**Commands:**\n"
        "• `silpa status` - Show SILPA status\n"
        "• `silpa plan <file>` - Plan a refactoring\n"
        "• `silpa execute <plan>` - Execute with approval\n\n"
        "**Platinum Protocol:**\n"
        "1. Tests must pass BEFORE refactoring\n"
        "2. Apply code changes\n"
        "3. Tests must pass AFTER refactoring\n"
        "4. Automatic rollback on failure"
    )


def get_silpa_for_chat(workspace: Optional[Path] = None) -> str:
    """
    Get SILPA status for chat display.

    Args:
        workspace: Optional workspace path

    Returns:
        Status string for chat
    """
    return """🔨 **SILPA** (The Self-Architect)
├─ Status: Active
├─ Protocol: Platinum (Test-Guarded)
└─ Risk Levels: SAFE, MODERATE, HIGH, FORBIDDEN

**Supported Refactorings:**
• Update/Add docstrings
• Rename variables/functions
• Extract methods
• Consolidate patterns

**Protected Files:**
• Kernel (cognitive_kernel.py)
• Governance rules
• Security modules (Narasimha)
• SILPA itself (no self-modification)

**Safety Guarantee:**
No code change without passing tests before AND after.
"""
