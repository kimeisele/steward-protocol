"""
OPUS-053: SILPA (The Self-Architect) - Safe Code Refactoring Tests.

TDD: These tests define the expected behavior for the SILPA module.

SILPA = Art, Craft, Architecture - the ability to reshape code safely.
The surgeon that operates on the living system with precision.

"No surgery without anesthesia. No refactoring without tests."
"""

from pathlib import Path

import pytest

# =============================================================================
# SECTION 1: DATA MODEL TESTS
# =============================================================================


class TestSilpaDataModels:
    """Test SILPA data models."""

    def test_refactor_risk_enum_values(self):
        """Mutation killer: RefactorRisk must have all levels."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import RefactorRisk

        assert RefactorRisk.SAFE.value == "safe"
        assert RefactorRisk.MODERATE.value == "moderate"
        assert RefactorRisk.HIGH.value == "high"
        assert RefactorRisk.FORBIDDEN.value == "forbidden"

    def test_refactor_type_enum_values(self):
        """Mutation killer: RefactorType must have all types."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import RefactorType

        assert RefactorType.UPDATE_DOCSTRING.value == "update_docstring"
        assert RefactorType.ADD_DOCSTRING.value == "add_docstring"
        assert RefactorType.RENAME_VARIABLE.value == "rename_variable"
        assert RefactorType.EXTRACT_METHOD.value == "extract_method"

    def test_silpa_refactoring_to_dict(self, tmp_path):
        """Mutation killer: SilpaRefactoring.to_dict works."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=tmp_path / "test.py",
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Test refactoring",
            instructions="Update the docstring",
        )

        d = ref.to_dict()
        assert "target_file" in d
        assert "refactor_type" in d
        assert d["refactor_type"] == "update_docstring"

    def test_silpa_test_result_to_dict(self):
        """Mutation killer: SilpaTestResult.to_dict works."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaTestResult

        result = SilpaTestResult(
            success=True,
            exit_code=0,
            tests_run=10,
            tests_passed=10,
            tests_failed=0,
            stdout="All tests passed",
            stderr="",
            duration_ms=1234.5,
        )

        d = result.to_dict()
        assert d["success"] is True
        assert d["tests_run"] == 10
        assert d["duration_ms"] == 1234.5

    def test_silpa_result_to_chat_response_success(self, tmp_path):
        """Mutation killer: Success response formats correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorRisk,
            RefactorType,
            SilpaPlan,
            SilpaRefactoring,
            SilpaResult,
            SilpaTestResult,
        )

        ref = SilpaRefactoring(
            target_file=tmp_path / "test.py",
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Test",
            instructions="Test",
        )

        plan = SilpaPlan(
            refactoring=ref,
            original_code="",
            original_hash="abc123",
            planned_code="",
            risk_level=RefactorRisk.SAFE,
            affected_functions=[],
            affected_classes=[],
            estimated_impact="",
            approval_required=False,
        )

        pre_test = SilpaTestResult(True, 0, 5, 5, 0, "", "", 100)
        post_test = SilpaTestResult(True, 0, 5, 5, 0, "", "", 100)

        result = SilpaResult(
            success=True,
            plan=plan,
            pre_test=pre_test,
            post_test=post_test,
        )

        response = result.to_chat_response()
        assert "✅" in response
        assert "SUCCESS" in response
        assert "Pre-Test" in response
        assert "Post-Test" in response

    def test_silpa_result_to_chat_response_failure(self, tmp_path):
        """Mutation killer: Failure response formats correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorRisk,
            RefactorType,
            SilpaPlan,
            SilpaRefactoring,
            SilpaResult,
        )

        ref = SilpaRefactoring(
            target_file=tmp_path / "test.py",
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Test",
            instructions="Test",
        )

        plan = SilpaPlan(
            refactoring=ref,
            original_code="",
            original_hash="abc123",
            planned_code="",
            risk_level=RefactorRisk.SAFE,
            affected_functions=[],
            affected_classes=[],
            estimated_impact="",
            approval_required=False,
        )

        result = SilpaResult(
            success=False,
            plan=plan,
            error="Something went wrong",
            rollback_performed=True,
        )

        response = result.to_chat_response()
        assert "❌" in response
        assert "FAILED" in response
        assert "Rollback" in response


# =============================================================================
# SECTION 2: SILPA AUDITOR TESTS
# =============================================================================


class TestSilpaAuditor:
    """Test SilpaAuditor - Platinum Protocol test verification."""

    def test_auditor_initialization(self, tmp_path):
        """Mutation killer: Auditor initializes correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaAuditor

        auditor = SilpaAuditor(workspace=tmp_path)
        assert auditor._workspace == tmp_path
        assert auditor._timeout == SilpaAuditor.DEFAULT_TIMEOUT

    def test_auditor_parse_pytest_output_success(self, tmp_path):
        """Mutation killer: Pytest output parsing works for success."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaAuditor

        auditor = SilpaAuditor(workspace=tmp_path)

        output = "===== 10 passed, 2 warnings in 1.23s ====="
        tests_run, tests_passed, tests_failed = auditor._parse_pytest_output(output)

        assert tests_passed == 10
        assert tests_failed == 0
        assert tests_run == 10

    def test_auditor_parse_pytest_output_failure(self, tmp_path):
        """Mutation killer: Pytest output parsing works for failures."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaAuditor

        auditor = SilpaAuditor(workspace=tmp_path)

        output = "===== 8 passed, 2 failed in 2.34s ====="
        tests_run, tests_passed, tests_failed = auditor._parse_pytest_output(output)

        assert tests_passed == 8
        assert tests_failed == 2
        assert tests_run == 10

    def test_auditor_discover_tests_for_file(self, tmp_path):
        """Mutation killer: Test discovery works."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaAuditor

        # Create test file structure
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_boot_mode.py").write_text("# test file")

        auditor = SilpaAuditor(workspace=tmp_path)
        target_file = tmp_path / "boot_mode.py"

        discovered = auditor._discover_tests_for_file(target_file)
        assert len(discovered) > 0
        assert "tests/test_boot_mode.py" in discovered


# =============================================================================
# SECTION 3: SILPA TRANSFORMER TESTS
# =============================================================================


class TestSilpaTransformer:
    """Test SilpaTransformer - AST-based code modification."""

    def test_transformer_initialization(self):
        """Mutation killer: Transformer initializes correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaTransformer

        transformer = SilpaTransformer()
        assert transformer._transformers is not None

    def test_transformer_can_transform_docstring(self):
        """Mutation killer: UPDATE_DOCSTRING is supported."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaTransformer,
        )

        transformer = SilpaTransformer()
        assert transformer.can_transform(RefactorType.UPDATE_DOCSTRING)
        assert transformer.can_transform(RefactorType.ADD_DOCSTRING)

    def test_transformer_rejects_invalid_code(self):
        """Mutation killer: Invalid code raises ValueError."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaTransformer,
        )

        transformer = SilpaTransformer()

        invalid_code = "def broken("  # Syntax error

        with pytest.raises(ValueError, match="Cannot parse"):
            transformer.transform(
                invalid_code,
                RefactorType.UPDATE_DOCSTRING,
                {"target_name": "test", "new_docstring": "new"},
            )


# =============================================================================
# SECTION 4: SILPA ARCHITECT TESTS
# =============================================================================


class TestSilpaArchitect:
    """Test SilpaArchitect - main orchestrator."""

    @pytest.fixture
    def architect(self, tmp_path):
        """Create architect with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaArchitect

        return SilpaArchitect(workspace=tmp_path)

    @pytest.fixture
    def test_file(self, tmp_path):
        """Create a test Python file."""
        test_py = tmp_path / "test_module.py"
        test_py.write_text('''"""Original docstring."""

def hello():
    """Say hello."""
    return "hello"

class MyClass:
    """A class."""
    pass
''')
        return test_py

    def test_architect_initialization(self, architect, tmp_path):
        """Mutation killer: Architect initializes correctly."""
        assert architect._workspace == tmp_path
        assert architect._auditor is not None
        assert architect._transformer is not None

    def test_architect_classify_risk_safe(self, architect, tmp_path):
        """Mutation killer: Docstring updates are SAFE."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorRisk,
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=tmp_path / "test.py",
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        risk = architect.classify_risk(ref)
        assert risk == RefactorRisk.SAFE

    def test_architect_classify_risk_forbidden(self, architect, tmp_path):
        """Mutation killer: Protected files are FORBIDDEN."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorRisk,
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=Path("vibe_core/cognitive_kernel.py"),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        risk = architect.classify_risk(ref)
        assert risk == RefactorRisk.FORBIDDEN

    def test_architect_classify_risk_narasimha_forbidden(self, architect):
        """Mutation killer: Narasimha files are FORBIDDEN."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorRisk,
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=Path("vibe_core/plugins/opus_assistant/narasimha/guardian.py"),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        risk = architect.classify_risk(ref)
        assert risk == RefactorRisk.FORBIDDEN

    def test_architect_plan_creates_plan(self, architect, test_file, tmp_path):
        """Mutation killer: plan() creates a valid SilpaPlan."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaPlan,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=test_file.relative_to(tmp_path),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        plan = architect.plan(ref)

        assert isinstance(plan, SilpaPlan)
        assert plan.original_code is not None
        assert plan.original_hash is not None
        assert len(plan.affected_functions) > 0  # Should find 'hello'
        assert len(plan.affected_classes) > 0  # Should find 'MyClass'

    def test_architect_plan_fails_for_missing_file(self, architect, tmp_path):
        """Mutation killer: plan() fails for non-existent file."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=Path("nonexistent.py"),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        with pytest.raises(FileNotFoundError):
            architect.plan(ref)

    def test_architect_plan_fails_for_forbidden(self, architect, tmp_path):
        """Mutation killer: plan() fails for forbidden files."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaRefactoring,
        )

        # Create a file that looks like it's in a protected path
        # But we need to actually create it for the test
        protected = tmp_path / "vibe_core" / "cognitive_kernel.py"
        protected.parent.mkdir(parents=True)
        protected.write_text("# kernel")

        ref = SilpaRefactoring(
            target_file=Path("vibe_core/cognitive_kernel.py"),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
        )

        with pytest.raises(PermissionError, match="protected"):
            architect.plan(ref)

    def test_architect_execute_requires_approval_for_moderate(self, architect, test_file, tmp_path):
        """Mutation killer: Moderate risk requires approval token."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaRefactoring,
        )

        ref = SilpaRefactoring(
            target_file=test_file.relative_to(tmp_path),
            refactor_type=RefactorType.RENAME_FUNCTION,  # MODERATE risk
            description="Rename function",
            instructions="Rename hello to greet",
        )

        plan = architect.plan(ref)
        plan.approval_required = True  # Force approval

        result = architect.execute(plan)  # No approval token

        assert result.success is False
        assert "Approval token required" in result.error

    def test_architect_analyze_code(self, architect):
        """Mutation killer: _analyze_code finds functions and classes."""
        code = """
def func1():
    pass

def func2():
    pass

class MyClass:
    def method(self):
        pass
"""
        functions, classes = architect._analyze_code(code)

        assert "func1" in functions
        assert "func2" in functions
        assert "method" in functions
        assert "MyClass" in classes


# =============================================================================
# SECTION 5: PLATINUM PROTOCOL INTEGRATION TESTS
# =============================================================================


class TestPlatinumProtocol:
    """Test the Platinum Protocol workflow."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a workspace with test files."""
        # Create source file
        src = tmp_path / "my_module.py"
        src.write_text('''"""My module docstring."""

def add(a, b):
    """Add two numbers."""
    return a + b
''')

        # Create test file
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_my_module.py"
        test_file.write_text('''"""Tests for my_module."""
import sys
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])

from my_module import add

def test_add():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, 1) == 0
''')

        return tmp_path

    def test_platinum_protocol_dry_run(self, workspace):
        """Mutation killer: Dry run doesn't modify files."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
            RefactorType,
            SilpaArchitect,
            SilpaRefactoring,
        )

        architect = SilpaArchitect(workspace=workspace)

        ref = SilpaRefactoring(
            target_file=Path("my_module.py"),
            refactor_type=RefactorType.UPDATE_DOCSTRING,
            description="Update docstring",
            instructions="Make it better",
            test_pattern="tests/test_my_module.py",
        )

        plan = architect.plan(ref)
        original_content = (workspace / "my_module.py").read_text()

        # Execute in dry run mode
        result = architect.execute(plan, dry_run=True)

        # File should be unchanged
        assert (workspace / "my_module.py").read_text() == original_content
        assert "DRY RUN" in result.audit_trail[-1] or any("DRY RUN" in entry for entry in result.audit_trail)


# =============================================================================
# SECTION 6: JNANA INTEGRATION TESTS
# =============================================================================


class TestSilpaJnanaIntegration:
    """Test SILPA integration with JNANA chat."""

    def test_handle_silpa_query_status(self, tmp_path):
        """Mutation killer: Status query returns info."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import handle_silpa_query

        result = handle_silpa_query("silpa status", workspace=tmp_path)

        assert isinstance(result, str)
        assert "SILPA" in result

    def test_handle_silpa_query_info(self, tmp_path):
        """Mutation killer: Info query returns help."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import handle_silpa_query

        result = handle_silpa_query("what is silpa", workspace=tmp_path)

        assert isinstance(result, str)
        # Check for "Platinum" anywhere in output
        assert "Platinum" in result

    def test_get_silpa_for_chat(self, tmp_path):
        """Mutation killer: Chat status shows all info."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import get_silpa_for_chat

        result = get_silpa_for_chat(workspace=tmp_path)

        assert "SILPA" in result
        assert "Self-Architect" in result
        assert "Platinum" in result
        assert "Protected Files" in result
        assert "Narasimha" in result


# =============================================================================
# SECTION 7: PROTECTED PATHS TESTS
# =============================================================================


class TestProtectedPaths:
    """Test that protected paths cannot be modified."""

    def test_kernel_is_protected(self):
        """Mutation killer: cognitive_kernel.py is protected."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import PROTECTED_PATHS

        assert any("cognitive_kernel.py" in p for p in PROTECTED_PATHS)

    def test_governance_is_protected(self):
        """Mutation killer: governance/ is protected."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import PROTECTED_PATHS

        assert any("governance" in p for p in PROTECTED_PATHS)

    def test_narasimha_is_protected(self):
        """Mutation killer: narasimha/ is protected."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import PROTECTED_PATHS

        assert any("narasimha" in p for p in PROTECTED_PATHS)

    def test_silpa_cannot_modify_itself(self):
        """Mutation killer: SILPA cannot modify silpa.py."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import PROTECTED_PATHS

        assert any("silpa.py" in p for p in PROTECTED_PATHS)
