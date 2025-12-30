"""
TEST: ScientistCartridge - External Intelligence Module
========================================================
Target: science/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.science.cartridge_main import ScientistCartridge


class TestScientistCartridgeInit:
    """Test ScientistCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = ScientistCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = ScientistCartridge()
        assert cartridge.agent_id == "science"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = ScientistCartridge()
        assert cartridge.name == "SCIENCE"

    def test_cartridge_has_version(self):
        """Should have version string."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "1.0.0"

    def test_cartridge_has_research_capabilities(self):
        """Should have research and web_search capabilities."""
        cartridge = ScientistCartridge()
        assert len(cartridge.capabilities) > 0
        assert "research" in cartridge.capabilities
        assert "web_search" in cartridge.capabilities

    def test_cartridge_domain_is_intelligence(self):
        """Should have INTELLIGENCE domain."""
        cartridge = ScientistCartridge()
        assert cartridge.domain == "INTELLIGENCE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestScientistManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = ScientistCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = ScientistCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "science"

    def test_manifest_has_capabilities(self):
        """Should include research capabilities in manifest."""
        cartridge = ScientistCartridge()
        manifest = cartridge.get_manifest()
        assert len(manifest.capabilities) > 0


class TestScientistReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    @pytest.mark.skip(reason="Requires system interface for sandbox path access")
    def test_report_status_returns_dict(self):
        """Should return status dict when connected to kernel."""
        cartridge = ScientistCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)


class TestScientistResearch:
    """Test research-related methods."""

    def test_research_method_exists(self):
        """Should have research method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "research")
        assert callable(cartridge.research)

    def test_research_topic_method_exists(self):
        """Should have research_topic method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "research_topic")
        assert callable(cartridge.research_topic)

    def test_fact_check_method_exists(self):
        """Should have fact_check method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "fact_check")
        assert callable(cartridge.fact_check)

    def test_trending_now_method_exists(self):
        """Should have trending_now method."""
        cartridge = ScientistCartridge()
        assert hasattr(cartridge, "trending_now")
        assert callable(cartridge.trending_now)
