"""
TEST: OracleCartridge - System Self-Awareness Agent
====================================================
Target: oracle/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.oracle.cartridge_main import OracleCartridge


class TestOracleCartridgeInit:
    """Test OracleCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = OracleCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = OracleCartridge()
        assert cartridge.agent_id == "oracle"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = OracleCartridge()
        assert cartridge.name == "ORACLE"

    def test_cartridge_has_version(self):
        """Should have version string."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "1.0.0"

    def test_cartridge_has_introspection_capabilities(self):
        """Should have introspection and audit_trail capabilities."""
        cartridge = OracleCartridge()
        assert len(cartridge.capabilities) > 0
        assert "introspection" in cartridge.capabilities
        assert "system_health" in cartridge.capabilities

    def test_cartridge_domain_is_system(self):
        """Should have SYSTEM domain."""
        cartridge = OracleCartridge()
        assert cartridge.domain == "SYSTEM"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestOracleManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = OracleCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = OracleCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "oracle"


class TestOracleReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = OracleCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = OracleCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "oracle"

    def test_report_status_has_running_status(self):
        """Should report RUNNING status."""
        cartridge = OracleCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "RUNNING"


class TestOracleIntrospectionMethods:
    """Test introspection methods (read-only operations)."""

    def test_explain_agent_method_exists(self):
        """Should have explain_agent method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "explain_agent")
        assert callable(cartridge.explain_agent)

    def test_explain_freeze_method_exists(self):
        """Should have explain_freeze method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "explain_freeze")
        assert callable(cartridge.explain_freeze)

    def test_audit_timeline_method_exists(self):
        """Should have audit_timeline method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "audit_timeline")
        assert callable(cartridge.audit_timeline)

    def test_system_health_method_exists(self):
        """Should have system_health method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "system_health")
        assert callable(cartridge.system_health)

    def test_get_raw_transaction_method_exists(self):
        """Should have get_raw_transaction method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "get_raw_transaction")
        assert callable(cartridge.get_raw_transaction)

    def test_get_vault_access_log_method_exists(self):
        """Should have get_vault_access_log method."""
        cartridge = OracleCartridge()
        assert hasattr(cartridge, "get_vault_access_log")
        assert callable(cartridge.get_vault_access_log)
