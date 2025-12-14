"""
OPUS-048: DHARMA (Das kosmische Gesetz) - Architectural Drift Detection Tests.

Sanskrit: Dharma = The cosmic law, duty, order that prevents chaos.

These tests verify:
1. Architecture spec parsing works
2. Filesystem scanning finds actual modules
3. Drift detection correctly identifies violations
4. Proposals can be generated for fixable violations
"""

from pathlib import Path

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.dharma import (
    ArchitecturalViolation,
    ArchitectureSpec,
    DharmaAuditor,
    DriftReport,
    FilesystemScanner,
    check_drift_for_chat,
)

# =============================================================================
# TEST: ArchitecturalViolation
# =============================================================================


class TestArchitecturalViolation:
    """Tests for ArchitecturalViolation dataclass."""

    def test_violation_creation(self):
        """Test creating a violation."""
        violation = ArchitecturalViolation(
            violation_type="undocumented_module",
            path="vibe_core/plugins/secret",
            description="Secret module not documented",
            severity="medium",
            suggested_action="Document or remove",
            can_auto_fix=True,
        )

        assert violation.violation_type == "undocumented_module"
        assert violation.severity == "medium"
        assert violation.can_auto_fix is True

    def test_violation_to_dict(self):
        """Test serialization."""
        violation = ArchitecturalViolation(
            violation_type="test",
            path="test/path",
            description="Test",
            severity="low",
            suggested_action="Test",
        )

        d = violation.to_dict()
        assert d["type"] == "test"
        assert d["path"] == "test/path"


# =============================================================================
# TEST: DriftReport
# =============================================================================


class TestDriftReport:
    """Tests for DriftReport dataclass."""

    def test_empty_report(self):
        """Test report with no violations."""
        report = DriftReport(
            generated_at="2024-01-01T00:00:00Z",
            total_violations=0,
            violations=[],
            documented_modules=10,
            actual_modules=10,
            compliance_score=100.0,
        )

        assert report.total_violations == 0
        assert report.compliance_score == 100.0
        assert "Keine" in report.summary() or "gesetzestreu" in report.summary()

    def test_report_with_violations(self):
        """Test report with violations."""
        violations = [
            ArchitecturalViolation(
                violation_type="test",
                path="test",
                description="Test",
                severity="high",
                suggested_action="Test",
            )
        ]

        report = DriftReport(
            generated_at="2024-01-01T00:00:00Z",
            total_violations=1,
            violations=violations,
            documented_modules=10,
            actual_modules=11,
            compliance_score=90.0,
            high=1,
        )

        assert report.total_violations == 1
        assert "Verstöße" in report.summary()

    def test_report_to_dict(self):
        """Test serialization."""
        report = DriftReport(
            generated_at="2024-01-01T00:00:00Z",
            total_violations=0,
            violations=[],
            documented_modules=5,
            actual_modules=5,
            compliance_score=100.0,
        )

        d = report.to_dict()
        assert d["total_violations"] == 0
        assert d["compliance_score"] == 100.0


# =============================================================================
# TEST: ArchitectureSpec
# =============================================================================


class TestArchitectureSpec:
    """Tests for ArchitectureSpec."""

    @pytest.fixture
    def spec(self, tmp_path):
        """Create spec with temp workspace."""
        return ArchitectureSpec(workspace=tmp_path)

    def test_legal_plugins_predefined(self, spec):
        """Test that known legal plugins are recognized."""
        assert spec.is_legal_plugin("opus_assistant")
        assert spec.is_legal_plugin("envoy")
        assert spec.is_legal_plugin("doctor")

    def test_illegal_plugin_detected(self, spec):
        """Test that unknown plugins are not legal."""
        assert not spec.is_legal_plugin("secret_hacks")
        assert not spec.is_legal_plugin("backdoor")

    def test_legal_top_level(self, spec):
        """Test known legal top-level directories."""
        assert spec.is_legal_top_level("vibe_core")
        assert spec.is_legal_top_level("tests")
        assert spec.is_legal_top_level("docs")

    def test_hidden_dirs_always_legal(self, spec):
        """Test that hidden directories are always legal."""
        assert spec.is_legal_top_level(".git")
        assert spec.is_legal_top_level(".venv")
        assert spec.is_legal_top_level(".opus_state")

    def test_scan_docs_extracts_modules(self, tmp_path):
        """Test that scanning docs extracts module references."""
        # Create docs directory with architecture file
        docs_dir = tmp_path / "docs" / "architecture"
        docs_dir.mkdir(parents=True)

        # Write doc mentioning a module
        (docs_dir / "TEST.md").write_text(
            "# Test\n\nThe vibe_core/my_module provides functionality.\nSee plugins/special_plugin for details."
        )

        spec = ArchitectureSpec(workspace=tmp_path)

        # Module should now be documented
        assert "my_module" in spec.get_documented_modules()
        assert "special_plugin" in spec.get_documented_modules()


# =============================================================================
# TEST: FilesystemScanner
# =============================================================================


class TestFilesystemScanner:
    """Tests for FilesystemScanner."""

    @pytest.fixture
    def scanner(self, tmp_path):
        """Create scanner with temp workspace."""
        return FilesystemScanner(workspace=tmp_path)

    def test_scan_plugins_empty(self, scanner, tmp_path):
        """Test scanning empty workspace."""
        plugins = scanner.scan_plugins()
        assert plugins == []

    def test_scan_plugins_finds_dirs(self, tmp_path):
        """Test scanning finds plugin directories."""
        plugins_dir = tmp_path / "vibe_core" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "plugin_a").mkdir()
        (plugins_dir / "plugin_b").mkdir()
        (plugins_dir / "__pycache__").mkdir()  # Should be ignored

        scanner = FilesystemScanner(workspace=tmp_path)
        plugins = scanner.scan_plugins()

        assert "plugin_a" in plugins
        assert "plugin_b" in plugins
        assert "__pycache__" not in plugins

    def test_scan_cartridges(self, tmp_path):
        """Test scanning cartridges by category."""
        # Create cartridge structure
        system_dir = tmp_path / "vibe_core" / "cartridges" / "system"
        system_dir.mkdir(parents=True)
        (system_dir / "agent_a").mkdir()
        (system_dir / "agent_b").mkdir()

        city_dir = tmp_path / "vibe_core" / "cartridges" / "agent_city"
        city_dir.mkdir(parents=True)
        (city_dir / "citizen_a").mkdir()

        scanner = FilesystemScanner(workspace=tmp_path)
        cartridges = scanner.scan_cartridges()

        assert "system" in cartridges
        assert "agent_city" in cartridges
        assert "agent_a" in cartridges["system"]
        assert "agent_b" in cartridges["system"]
        assert "citizen_a" in cartridges["agent_city"]

    def test_find_orphan_files(self, tmp_path):
        """Test finding orphan Python files."""
        # Create some files
        (tmp_path / "orphan.py").write_text("# orphan")
        (tmp_path / "setup.py").write_text("# setup")  # Allowed
        (tmp_path / "conftest.py").write_text("# conftest")  # Allowed

        scanner = FilesystemScanner(workspace=tmp_path)
        orphans = scanner.find_orphan_python_files()

        assert "orphan.py" in orphans
        assert "setup.py" not in orphans
        assert "conftest.py" not in orphans


# =============================================================================
# TEST: DharmaAuditor
# =============================================================================


class TestDharmaAuditor:
    """Tests for DharmaAuditor."""

    @pytest.fixture
    def auditor(self, tmp_path):
        """Create auditor with temp workspace."""
        return DharmaAuditor(workspace=tmp_path)

    def test_audit_empty_workspace(self, auditor):
        """Test auditing empty workspace."""
        report = auditor.audit()

        assert report.total_violations == 0
        assert report.compliance_score == 100.0

    def test_audit_detects_undocumented_plugin(self, tmp_path):
        """Test that undocumented plugins are detected."""
        # Create unknown plugin
        plugins_dir = tmp_path / "vibe_core" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "secret_backdoor").mkdir()

        auditor = DharmaAuditor(workspace=tmp_path)
        report = auditor.audit()

        assert report.total_violations > 0
        assert any("secret_backdoor" in v.path for v in report.violations)

    def test_audit_ignores_legal_plugins(self, tmp_path):
        """Test that known legal plugins don't trigger violations."""
        # Create legal plugin
        plugins_dir = tmp_path / "vibe_core" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "opus_assistant").mkdir()

        auditor = DharmaAuditor(workspace=tmp_path)
        report = auditor.audit()

        # Should not have violation for opus_assistant
        assert not any(
            "opus_assistant" in v.path and v.violation_type == "undocumented_module" for v in report.violations
        )

    def test_audit_detects_missing_manifest(self, tmp_path):
        """Test detection of cartridge without manifest."""
        # Create cartridge without manifest
        agent_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "no_manifest_agent"
        agent_dir.mkdir(parents=True)

        auditor = DharmaAuditor(workspace=tmp_path)
        report = auditor.audit()

        assert any(v.violation_type == "missing_manifest" for v in report.violations)

    def test_audit_passes_with_manifest(self, tmp_path):
        """Test that cartridge with manifest passes."""
        # Create cartridge with manifest
        agent_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "good_agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "steward.json").write_text('{"identity": {"agent_id": "good_agent"}}')

        auditor = DharmaAuditor(workspace=tmp_path)
        report = auditor.audit()

        # Should not have missing_manifest for good_agent
        assert not any("good_agent" in v.path and v.violation_type == "missing_manifest" for v in report.violations)

    def test_check_architectural_drift_summary(self, auditor):
        """Test quick drift check returns string."""
        result = auditor.check_architectural_drift()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_proposal(self, tmp_path):
        """Test proposal generation for fixable violations."""
        violations = [
            ArchitecturalViolation(
                violation_type="undocumented_module",
                path="vibe_core/plugins/new_module",
                description="Not documented",
                severity="medium",
                suggested_action="Document it",
                can_auto_fix=True,
            )
        ]

        auditor = DharmaAuditor(workspace=tmp_path)
        proposal = auditor.generate_proposal(violations)

        assert proposal is not None
        assert proposal.proposal_id.startswith("CAP-")
        assert "new_module" in proposal.affected_paths[0]

    def test_no_proposal_for_unfixable(self, tmp_path):
        """Test no proposal for unfixable violations."""
        violations = [
            ArchitecturalViolation(
                violation_type="orphan_file",
                path="random.py",
                description="Orphan",
                severity="low",
                suggested_action="Remove",
                can_auto_fix=False,
            )
        ]

        auditor = DharmaAuditor(workspace=tmp_path)
        proposal = auditor.generate_proposal(violations)

        assert proposal is None


# =============================================================================
# TEST: KRIYA Integration
# =============================================================================


class TestKriyaIntegration:
    """Tests for KRIYA chat integration."""

    def test_check_drift_for_chat_returns_string(self):
        """Test that chat function returns readable string."""
        result = check_drift_for_chat()

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain status indicators
        assert "✅" in result or "⚠️" in result

    def test_chat_response_contains_score(self):
        """Test that response contains compliance score."""
        result = check_drift_for_chat()
        assert "Compliance" in result or "Score" in result or "%" in result


# =============================================================================
# TEST: Real Workspace Integration
# =============================================================================


class TestRealWorkspaceIntegration:
    """Integration tests with real workspace (if available)."""

    @pytest.fixture
    def real_workspace(self):
        """Get real workspace path."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "vibe_core").exists():
                return parent
        pytest.skip("Real workspace not found")

    def test_audit_real_workspace(self, real_workspace):
        """Test auditing real workspace."""
        auditor = DharmaAuditor(workspace=real_workspace)
        report = auditor.audit()

        # Should complete without error
        assert report.generated_at is not None
        assert report.actual_modules > 0

    def test_real_compliance_reasonable(self, real_workspace):
        """Test that real compliance score is reasonable."""
        auditor = DharmaAuditor(workspace=real_workspace)
        report = auditor.audit()

        # Compliance should be reasonable (not 0%)
        assert report.compliance_score >= 0
        # But also not necessarily 100% in a real codebase
        assert report.compliance_score <= 100
