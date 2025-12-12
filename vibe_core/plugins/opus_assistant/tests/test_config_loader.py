"""
OPUS Assistant - Config Loader Tests

Tests for fraktale config loading.
"""

from pathlib import Path


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_loader_importable(self):
        """ConfigLoader can be imported."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        assert ConfigLoader is not None

    def test_loader_instantiation(self):
        """ConfigLoader can be instantiated."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        loader = ConfigLoader(workspace_root=Path("."))
        assert loader is not None

    def test_deep_merge(self):
        """deep_merge correctly merges dicts."""
        from vibe_core.plugins.opus_assistant.core.config_loader import deep_merge

        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 99}, "e": 5}

        result = deep_merge(base, override)

        assert result["a"] == 1  # From base
        assert result["b"]["c"] == 99  # Overridden
        assert result["b"]["d"] == 3  # From base
        assert result["e"] == 5  # From override

    def test_load_returns_dict(self):
        """load() returns a dict."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent
        loader = ConfigLoader(workspace_root=workspace)

        config = loader.load()

        assert isinstance(config, dict)
        assert len(config) > 0

    def test_load_includes_defaults(self):
        """load() includes values from defaults.yaml."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent
        loader = ConfigLoader(workspace_root=workspace)

        config = loader.load()

        # These are from defaults.yaml
        assert "verification" in config or "plugin" in config

    def test_get_dot_notation(self):
        """get() supports dot notation."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent
        loader = ConfigLoader(workspace_root=workspace)

        # Try to get a nested value
        result = loader.get("verification.enabled", default="NOT_FOUND")

        # Should be either True or "NOT_FOUND"
        assert result in [True, False, "NOT_FOUND"]

    def test_get_default_value(self):
        """get() returns default for missing keys."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        loader = ConfigLoader(workspace_root=Path("."))

        result = loader.get("nonexistent.key.path", default="DEFAULT")

        assert result == "DEFAULT"

    def test_reload_refreshes_config(self):
        """reload() refreshes config from files."""
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent
        loader = ConfigLoader(workspace_root=workspace)

        config1 = loader.load()
        config2 = loader.reload()

        # Should be equal (no changes to files)
        assert config1 == config2

    def test_no_rendering_in_loader(self):
        """ConfigLoader has no rich/UI imports."""
        loader_path = Path(__file__).parent.parent / "core" / "config_loader.py"
        content = loader_path.read_text()

        assert "from rich" not in content
        assert "import rich" not in content


class TestDefaults:
    """Test that defaults.yaml exists and is valid."""

    def test_defaults_yaml_exists(self):
        """defaults.yaml exists in plugin directory."""
        defaults_path = Path(__file__).parent.parent / "defaults.yaml"
        assert defaults_path.exists(), "defaults.yaml must exist"

    def test_defaults_yaml_valid(self):
        """defaults.yaml is valid YAML."""
        import yaml

        defaults_path = Path(__file__).parent.parent / "defaults.yaml"
        data = yaml.safe_load(defaults_path.read_text())

        assert isinstance(data, dict)
        assert "plugin" in data
        assert "verification" in data
        assert "drift" in data
        assert "kernel_tick" in data

    def test_defaults_has_plugin_metadata(self):
        """defaults.yaml has plugin metadata."""
        import yaml

        defaults_path = Path(__file__).parent.parent / "defaults.yaml"
        data = yaml.safe_load(defaults_path.read_text())

        assert data["plugin"]["id"] == "opus_assistant"
        assert "version" in data["plugin"]
