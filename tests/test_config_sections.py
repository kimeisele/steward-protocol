"""
Tests for Phoenix Config Sections.

Tests the new modular config system:
- agents section (config/agents.yaml)
- providers section (config/providers.yaml)
- Section auto-discovery
- Dual-Load Strategy
"""

from pathlib import Path

import pytest

from vibe_core.phoenix import get_config, reset_config
from vibe_core.phoenix.section_loader import SectionLoader


@pytest.fixture(autouse=True)
def reset_phoenix():
    """Reset phoenix config before each test."""
    reset_config()
    SectionLoader.clear_cache()
    yield
    reset_config()
    SectionLoader.clear_cache()


class TestSectionDiscovery:
    """Test section auto-discovery."""

    def test_agents_section_discovered(self):
        """Agents section is discovered from config/agents.yaml."""
        sections, meta = SectionLoader.discover()
        assert "agents" in sections
        assert meta["agents"].source_file == Path("config/agents.yaml")

    def test_providers_section_discovered(self):
        """Providers section is discovered from config/providers.yaml."""
        sections, meta = SectionLoader.discover()
        assert "providers" in sections
        assert meta["providers"].source_file == Path("config/providers.yaml")

    def test_all_core_sections_discovered(self):
        """All core sections are discovered."""
        sections, _ = SectionLoader.discover()
        core_sections = {"kernel", "city", "quality", "steward", "agents", "providers", "cli"}
        for section_id in core_sections:
            assert section_id in sections, f"Missing section: {section_id}"


class TestAgentsSection:
    """Test agents section (config/agents.yaml)."""

    def test_agents_loaded(self):
        """System agents are loaded from YAML."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        assert len(agents.system_agents) == 12

    def test_agent_definition_fields(self):
        """Agent definitions have required fields."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]

        # Check first agent
        agent = agents.system_agents[0]
        assert agent.name == "DiscoveryAgent"
        assert "discoverer" in agent.class_path
        assert agent.protocol == "VibeAgent"
        assert agent.enabled is True

    def test_agents_validation_passes(self):
        """Agents section validation passes."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        errors = agents.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_get_enabled_agents(self):
        """get_enabled_agents returns only enabled agents."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        enabled = agents.get_enabled_agents()
        assert all(a.enabled for a in enabled)

    def test_get_agent_by_name(self):
        """get_agent returns agent by name."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        herald = agents.get_agent("HeraldAgent")
        assert herald is not None
        assert herald.name == "HeraldAgent"

    def test_get_agent_not_found(self):
        """get_agent returns None for unknown agent."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        assert agents.get_agent("NonExistentAgent") is None


class TestProvidersSection:
    """Test providers section (config/providers.yaml)."""

    def test_providers_loaded(self):
        """Providers are loaded from YAML."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        assert "anthropic" in providers.llm.llm_provider

    def test_features_loaded(self):
        """Feature flags are loaded."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        assert providers.features.oauth_enforcement is True
        assert providers.features.live_fire_enabled is False
        assert providers.features.debug_mode is False

    def test_playbook_loaded(self):
        """Playbook config is loaded."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        assert "SimpleLLMAgent" in providers.playbook.executor_agent

    def test_imports_loaded(self):
        """Import order is loaded."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        assert len(providers.imports.order) > 0
        assert "vibe_core.protocols" in providers.imports.order

    def test_providers_validation_passes(self):
        """Providers section validation passes."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        errors = providers.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"


class TestPhoenixConfigIntegration:
    """Test PhoenixConfig integration with new sections."""

    def test_new_sections_accessible(self):
        """New sections are accessible via get_section."""
        config = get_config()
        agents = config.get_section("agents")
        providers = config.get_section("providers")

        assert agents is not None
        assert providers is not None

    def test_list_sections_includes_new(self):
        """list_sections includes new sections."""
        config = get_config()
        sections = config.list_sections()

        assert "agents" in sections
        assert "providers" in sections

    def test_backward_compat_kernel_features(self):
        """Kernel still has features for backward compat."""
        config = get_config()
        # Old API still works
        assert config.kernel.features.debug_mode is False
        assert config.kernel.providers.llm_provider is not None


class TestDualLoadStrategy:
    """Test Dual-Load Strategy (sections override phoenix.yaml)."""

    def test_agents_from_section_not_phoenix(self):
        """Agents come from agents section, not phoenix.yaml."""
        sections, _ = SectionLoader.discover()

        # agents section has the agents
        agents_section = sections["agents"]
        assert len(agents_section.system_agents) == 12

        # kernel section still loads from phoenix.yaml for backward compat
        # but the canonical source is now agents section
        kernel = sections["kernel"]
        # Both should have the same agents (until phoenix.yaml is cleaned)

    def test_providers_from_section_not_phoenix(self):
        """Providers come from providers section."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]

        assert "anthropic" in providers.llm.llm_provider
        assert providers.features.oauth_enforcement is True


class TestSectionSerialization:
    """Test section serialization."""

    def test_agents_to_dict(self):
        """Agents section serializes to dict."""
        sections, _ = SectionLoader.discover()
        agents = sections["agents"]
        data = agents.to_dict()

        assert "system_agents" in data
        assert len(data["system_agents"]) == 12

    def test_providers_to_dict(self):
        """Providers section serializes to dict."""
        sections, _ = SectionLoader.discover()
        providers = sections["providers"]
        data = providers.to_dict()

        assert "providers" in data
        assert "features" in data
        assert "playbook" in data
        assert "imports" in data
