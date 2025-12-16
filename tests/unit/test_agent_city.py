"""
Agent City Plugin Tests - Phase 0 (TDD)
========================================

Tests written BEFORE implementation.
Using existing fixtures from conftest.py and test_orchestration.
"""


class TestAgentCityPluginLoading:
    """Tests for Agent City plugin loading."""

    def test_plugin_exists(self):
        """Agent City plugin module can be imported."""
        # This will fail until we create the plugin
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        assert AgentCityPlugin is not None

    def test_plugin_has_manifest(self, project_root):
        """Agent City has valid manifest.json."""
        import json

        manifest_path = project_root / "vibe_core/plugins/agent_city/manifest.json"
        assert manifest_path.exists(), "manifest.json not found"

        manifest = json.loads(manifest_path.read_text())
        assert manifest.get("id") == "agent_city"
        assert manifest.get("type") == "plugin"

    def test_plugin_gad000_capabilities(self):
        """Plugin provides get_capabilities (GAD-000 Test 1)."""
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        plugin = AgentCityPlugin()
        caps = plugin.get_capabilities()

        assert "operations" in caps
        assert "spawn_citizen" in caps["operations"]


class TestAgentCityCitizenLifecycle:
    """Tests for citizen spawn/move/dissolve."""

    def test_spawn_citizen(self, permissive_kernel):
        """Engineer can spawn a citizen in the city."""
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        plugin = AgentCityPlugin()
        plugin.on_boot(permissive_kernel)

        result = plugin.spawn_citizen(
            citizen_id="test-analyst",
            zone="research",
        )

        assert result["status"] == "spawned"
        assert result["citizen_id"] == "test-analyst"

    def test_list_citizens(self, permissive_kernel):
        """List all citizens in the city."""
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        plugin = AgentCityPlugin()
        plugin.on_boot(permissive_kernel)

        # Spawn one first
        plugin.spawn_citizen(citizen_id="test-citizen", zone="general")

        citizens = plugin.list_citizens()
        assert "test-citizen" in citizens

    def test_dissolve_citizen(self, permissive_kernel):
        """Citizen can be dissolved."""
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        plugin = AgentCityPlugin()
        plugin.on_boot(permissive_kernel)

        # First spawn
        spawn_result = plugin.spawn_citizen(citizen_id="ephemeral", zone="general")
        assert spawn_result["status"] == "spawned"

        # Then dissolve
        result = plugin.dissolve_citizen(citizen_id="ephemeral")

        assert result["status"] == "dissolved"
        assert "ephemeral" not in plugin.list_citizens()


class TestAgentCityConfig:
    """Tests for city configuration."""

    def test_zones_config_exists(self, project_root):
        """Zones config file exists."""

        config_path = project_root / "config/cities/agent_city/zones.yaml"
        assert config_path.exists(), "zones.yaml not found"

    def test_load_zones(self):
        """Zones can be loaded from config."""
        from vibe_core.plugins.agent_city.plugin_main import AgentCityPlugin

        plugin = AgentCityPlugin()
        zones = plugin.get_zones()

        assert isinstance(zones, dict)
        assert len(zones) > 0
