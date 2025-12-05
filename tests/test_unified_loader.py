"""
Tests for the Unified Loader System.

Tests cover:
    1. Schema validation (manifest_schema.json)
    2. UnifiedLoader base class
    3. ItemMeta creation
    4. Config hierarchy (manifest defaults → local → global)
"""

import json

from vibe_core.loaders.base_loader import ItemMeta, LoaderRegistry, UnifiedLoader
from vibe_core.loaders.schema import validate_manifest, validate_manifest_file

# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


class TestManifestValidation:
    """Tests for manifest schema validation."""

    def test_valid_plugin_manifest(self):
        """Valid plugin manifest should pass."""
        manifest = {
            "type": "plugin",
            "id": "my_plugin",
            "name": "My Plugin",
            "version": "1.0.0",
        }
        errors = validate_manifest(manifest)
        assert errors == []

    def test_valid_agent_manifest(self):
        """Valid agent manifest should pass."""
        manifest = {
            "type": "agent",
            "id": "herald",
            "name": "Herald Agent",
            "version": "1.0.0",
            "compliance_level": 2,
        }
        errors = validate_manifest(manifest)
        assert errors == []

    def test_missing_type(self):
        """Missing type should fail."""
        manifest = {
            "id": "my_plugin",
            "name": "My Plugin",
        }
        errors = validate_manifest(manifest)
        assert any("type" in e.lower() for e in errors)

    def test_missing_id_and_name(self):
        """Missing both id and name should fail."""
        manifest = {
            "type": "plugin",
        }
        errors = validate_manifest(manifest)
        assert any("id" in e.lower() or "name" in e.lower() for e in errors)

    def test_invalid_id_format(self):
        """Invalid ID format should fail."""
        manifest = {
            "type": "plugin",
            "id": "MyPlugin",  # Should be snake_case
            "name": "My Plugin",
        }
        errors = validate_manifest(manifest)
        assert any("id" in e.lower() and "format" in e.lower() for e in errors)

    def test_invalid_id_starting_with_number(self):
        """ID starting with number should fail."""
        manifest = {
            "type": "plugin",
            "id": "123plugin",
            "name": "Plugin 123",
        }
        errors = validate_manifest(manifest)
        assert any("id" in e.lower() for e in errors)

    def test_invalid_version_format(self):
        """Invalid version format should fail."""
        manifest = {
            "type": "plugin",
            "id": "my_plugin",
            "name": "My Plugin",
            "version": "1.0",  # Should be X.Y.Z
        }
        errors = validate_manifest(manifest)
        assert any("version" in e.lower() for e in errors)

    def test_invalid_type(self):
        """Invalid type should fail."""
        manifest = {
            "type": "invalid_type",
            "id": "my_thing",
            "name": "My Thing",
        }
        errors = validate_manifest(manifest)
        assert any("type" in e.lower() for e in errors)

    def test_invalid_priority_negative(self):
        """Negative priority should fail."""
        manifest = {
            "type": "plugin",
            "id": "my_plugin",
            "name": "My Plugin",
            "priority": -1,
        }
        errors = validate_manifest(manifest)
        assert any("priority" in e.lower() for e in errors)

    def test_invalid_priority_too_high(self):
        """Priority over 1000 should fail."""
        manifest = {
            "type": "plugin",
            "id": "my_plugin",
            "name": "My Plugin",
            "priority": 1001,
        }
        errors = validate_manifest(manifest)
        assert any("priority" in e.lower() for e in errors)

    def test_valid_priority(self):
        """Valid priority should pass."""
        manifest = {
            "type": "plugin",
            "id": "my_plugin",
            "name": "My Plugin",
            "priority": 50,
        }
        errors = validate_manifest(manifest)
        assert errors == []


class TestManifestFileValidation:
    """Tests for manifest file validation."""

    def test_valid_file(self, tmp_path):
        """Valid manifest file should pass."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "test_plugin",
                    "name": "Test Plugin",
                }
            )
        )
        errors = validate_manifest_file(manifest_path)
        assert errors == []

    def test_nonexistent_file(self, tmp_path):
        """Non-existent file should fail."""
        manifest_path = tmp_path / "nonexistent.json"
        errors = validate_manifest_file(manifest_path)
        assert any("not found" in e.lower() for e in errors)

    def test_invalid_json(self, tmp_path):
        """Invalid JSON should fail."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text("{ invalid json }")
        errors = validate_manifest_file(manifest_path)
        assert any("json" in e.lower() for e in errors)


# =============================================================================
# ITEM META TESTS
# =============================================================================


class TestItemMeta:
    """Tests for ItemMeta dataclass."""

    def test_successful_meta(self, tmp_path):
        """Test successful item metadata."""
        meta = ItemMeta(
            item_id="test_plugin",
            item_type="plugin",
            manifest={"type": "plugin", "id": "test_plugin", "name": "Test"},
            manifest_path=tmp_path / "manifest.json",
            entry_path=tmp_path / "plugin_main.py",
            entry_class=None,
            loaded_successfully=True,
        )
        assert meta.item_id == "test_plugin"
        assert meta.loaded_successfully
        assert "OK" in repr(meta)

    def test_failed_meta(self, tmp_path):
        """Test failed item metadata."""
        meta = ItemMeta(
            item_id="broken_plugin",
            item_type="plugin",
            manifest={},
            manifest_path=tmp_path / "manifest.json",
            entry_path=None,
            entry_class=None,
            loaded_successfully=False,
            error="Manifest validation failed",
        )
        assert not meta.loaded_successfully
        assert "FAILED" in repr(meta)
        assert meta.error == "Manifest validation failed"


# =============================================================================
# UNIFIED LOADER TESTS
# =============================================================================


class TestUnifiedLoader:
    """Tests for UnifiedLoader base class."""

    def test_find_manifest_json(self, tmp_path):
        """Should find manifest.json."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text("{}")

        class TestLoader(UnifiedLoader):
            item_type = "test"
            scan_paths = [tmp_path]

        found = TestLoader._find_manifest(tmp_path)
        assert found == manifest_path

    def test_find_no_manifest(self, tmp_path):
        """Should return None when no manifest."""

        class TestLoader(UnifiedLoader):
            item_type = "test"
            scan_paths = [tmp_path]

        found = TestLoader._find_manifest(tmp_path)
        assert found is None

    def test_load_manifest(self, tmp_path):
        """Should load manifest dict."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "test",
                    "name": "Test",
                }
            )
        )

        class TestLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = [tmp_path]

        manifest = TestLoader._load_manifest(manifest_path)
        assert manifest["type"] == "plugin"
        assert manifest["id"] == "test"

    def test_validate_manifest_type_mismatch(self):
        """Should detect type mismatch."""

        class PluginLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = []

        errors = PluginLoader._validate_manifest(
            {
                "type": "agent",  # Wrong type
                "id": "test",
                "name": "Test",
            }
        )
        assert any("type mismatch" in e.lower() for e in errors)


class TestLoaderRegistry:
    """Tests for LoaderRegistry."""

    def test_register_and_get(self):
        """Should register and retrieve loaders."""

        class MyLoader(UnifiedLoader):
            item_type = "my_type"
            scan_paths = []

        LoaderRegistry.register("my_type", MyLoader)
        retrieved = LoaderRegistry.get("my_type")
        assert retrieved is MyLoader

    def test_get_nonexistent(self):
        """Should return None for unregistered type."""
        retrieved = LoaderRegistry.get("nonexistent_type_12345")
        assert retrieved is None

    def test_all_types(self):
        """Should list all registered types."""

        class AnotherLoader(UnifiedLoader):
            item_type = "another_type"
            scan_paths = []

        LoaderRegistry.register("another_type", AnotherLoader)
        types = LoaderRegistry.all_types()
        assert "another_type" in types


# =============================================================================
# CONFIG HIERARCHY TESTS
# =============================================================================


class TestConfigHierarchy:
    """Tests for config loading and merging."""

    def test_manifest_defaults(self, tmp_path):
        """Should use manifest defaults."""
        manifest = {
            "type": "plugin",
            "id": "test",
            "name": "Test",
            "defaults": {
                "setting1": "default_value",
                "setting2": 42,
            },
        }

        class TestLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = []

        config = TestLoader._load_config(tmp_path, manifest, None)
        assert config["setting1"] == "default_value"
        assert config["setting2"] == 42

    def test_local_config_overrides_defaults(self, tmp_path):
        """Local config.yaml should override manifest defaults."""
        manifest = {
            "type": "plugin",
            "id": "test",
            "name": "Test",
            "defaults": {
                "setting1": "default_value",
                "setting2": 42,
            },
        }

        # Create local config
        config_path = tmp_path / "config.yaml"
        config_path.write_text("setting1: local_value\nsetting3: new_setting")

        class TestLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = []

        config = TestLoader._load_config(tmp_path, manifest, None)
        assert config["setting1"] == "local_value"  # Overridden
        assert config["setting2"] == 42  # From defaults
        assert config["setting3"] == "new_setting"  # Added

    def test_global_config_overrides_all(self, tmp_path):
        """Global config should override local and defaults."""
        manifest = {
            "type": "plugin",
            "id": "test",
            "name": "Test",
            "defaults": {
                "setting1": "default_value",
            },
        }

        # Create local config
        config_path = tmp_path / "config.yaml"
        config_path.write_text("setting1: local_value")

        # Global config
        global_config = {
            "plugins": {
                "test": {
                    "setting1": "global_value",
                }
            }
        }

        class TestLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = []

        config = TestLoader._load_config(tmp_path, manifest, global_config)
        assert config["setting1"] == "global_value"  # Global wins


# =============================================================================
# FULL DISCOVERY TESTS
# =============================================================================


class TestFullDiscovery:
    """Integration tests for full discovery flow."""

    def test_discover_manifests_only(self, tmp_path):
        """Should discover manifests without loading."""
        # Create plugin structure
        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "my_plugin",
                    "name": "My Plugin",
                }
            )
        )

        class PluginLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = [tmp_path]

        manifests, metadata = PluginLoader.discover_manifests()
        assert "my_plugin" in manifests
        assert "my_plugin" in metadata
        assert metadata["my_plugin"].loaded_successfully

    def test_skip_hidden_directories(self, tmp_path):
        """Should skip directories starting with . or _."""
        # Create hidden plugin
        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "hidden",
                    "name": "Hidden",
                }
            )
        )

        # Create __pycache__
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "cache",
                    "name": "Cache",
                }
            )
        )

        # Create valid plugin
        valid_dir = tmp_path / "valid_plugin"
        valid_dir.mkdir()
        (valid_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "valid_plugin",
                    "name": "Valid",
                }
            )
        )

        class PluginLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = [tmp_path]

        manifests, metadata = PluginLoader.discover_manifests()
        assert "valid_plugin" in manifests
        assert "hidden" not in manifests
        assert "cache" not in manifests

    def test_disabled_plugin_not_loaded(self, tmp_path):
        """Disabled plugins should be discovered but not loaded."""
        plugin_dir = tmp_path / "disabled_plugin"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "type": "plugin",
                    "id": "disabled_plugin",
                    "name": "Disabled",
                    "enabled": False,
                }
            )
        )

        class PluginLoader(UnifiedLoader):
            item_type = "plugin"
            scan_paths = [tmp_path]

        instances, metadata = PluginLoader.discover_and_load()
        assert "disabled_plugin" not in instances
        assert "disabled_plugin" in metadata
        assert not metadata["disabled_plugin"].loaded_successfully
        assert "disabled" in metadata["disabled_plugin"].error.lower()
