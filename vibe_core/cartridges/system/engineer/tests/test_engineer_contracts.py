"""
TEST: EngineerCartridge - The Meta-Agent & Builder
==================================================
Target: engineer/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.engineer.cartridge_main import EngineerCartridge


class TestEngineerCartridgeInit:
    """Test EngineerCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = EngineerCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = EngineerCartridge()
        assert cartridge.agent_id == "engineer"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = EngineerCartridge()
        assert cartridge.name == "ENGINEER"

    def test_cartridge_has_version(self):
        """Should have version string (Tool Protocol v3.0)."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "3.0.0"

    def test_cartridge_has_builder_capabilities(self):
        """Should have manifest_reality and code_generation capabilities."""
        cartridge = EngineerCartridge()
        assert len(cartridge.capabilities) > 0
        assert "manifest_reality" in cartridge.capabilities
        assert "code_generation" in cartridge.capabilities

    def test_cartridge_domain_is_infrastructure(self):
        """Should have INFRASTRUCTURE domain."""
        cartridge = EngineerCartridge()
        assert cartridge.domain == "INFRASTRUCTURE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestEngineerManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = EngineerCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = EngineerCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "engineer"

    def test_manifest_has_no_dependencies(self):
        """Should have empty dependencies list."""
        cartridge = EngineerCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.dependencies == []


class TestEngineerReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = EngineerCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = EngineerCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "engineer"

    def test_report_status_has_running_status(self):
        """Should report RUNNING status."""
        cartridge = EngineerCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "RUNNING"


class TestEngineerBuilderMethods:
    """Test builder-related methods."""

    def test_manifest_reality_method_exists(self):
        """Should have manifest_reality method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "manifest_reality")
        assert callable(cartridge.manifest_reality)

    def test_create_agent_legacy_method_exists(self):
        """Should have create_agent_legacy method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "create_agent_legacy")
        assert callable(cartridge.create_agent_legacy)

    def test_spawn_agent_method_exists(self):
        """Should have spawn_agent method (OPUS-012 protocol)."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "spawn_agent")
        assert callable(cartridge.spawn_agent)


class TestEngineerCodeGeneration:
    """Test code generation helpers."""

    def test_generate_cartridge_code_method_exists(self):
        """Should have _generate_cartridge_code private method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "_generate_cartridge_code")
        assert callable(cartridge._generate_cartridge_code)

    def test_request_audit_method_exists(self):
        """Should have _request_audit private method."""
        cartridge = EngineerCartridge()
        assert hasattr(cartridge, "_request_audit")
        assert callable(cartridge._request_audit)
