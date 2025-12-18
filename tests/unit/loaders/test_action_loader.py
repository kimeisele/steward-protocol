"""
Tests for ActionLoader - OPUS-100.

Verifies VEDA-4 auto-discovery pattern for MANAS action modules.
"""

from pathlib import Path

import pytest

from vibe_core.loaders import ActionLoader, ActionLoadError


class TestActionLoaderDiscovery:
    """Test auto-discovery of actions."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_discover_shell_action(self):
        """Verify ShellAction is discovered."""
        actions, metadata = ActionLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=True,
        )

        # Must have at least 1 action (ShellAction)
        assert len(actions) >= 1, f"Expected at least 1 action, got {len(actions)}"
        assert "shell_action" in actions, "ShellAction not discovered"

    def test_metadata_populated(self):
        """Verify metadata includes class name, file, and handled_intent_types."""
        actions, metadata = ActionLoader.discover_and_load(workspace=Path.cwd())

        for name, meta in metadata.items():
            assert "class" in meta, f"Missing 'class' in metadata for {name}"
            assert "file" in meta, f"Missing 'file' in metadata for {name}"
            assert "enabled" in meta, f"Missing 'enabled' in metadata for {name}"
            assert "handled_intent_types" in meta, f"Missing 'handled_intent_types' in metadata for {name}"

    def test_actions_have_name_property(self):
        """Verify all discovered actions have a name property."""
        actions, _ = ActionLoader.discover_and_load(workspace=Path.cwd())

        for name, action in actions.items():
            assert hasattr(action, "name"), f"Action {name} missing 'name' property"
            assert action.name == name, f"Action name mismatch: {action.name} != {name}"

    def test_actions_have_act_method(self):
        """Verify all discovered actions have an act method."""
        actions, _ = ActionLoader.discover_and_load(workspace=Path.cwd())

        for name, action in actions.items():
            assert hasattr(action, "act"), f"Action {name} missing 'act' method"
            assert callable(action.act), f"Action {name}.act is not callable"

    def test_actions_have_handled_intent_types(self):
        """Verify all actions declare their handled intent types."""
        actions, _ = ActionLoader.discover_and_load(workspace=Path.cwd())

        for name, action in actions.items():
            assert hasattr(action, "handled_intent_types"), f"Action {name} missing 'handled_intent_types'"
            assert isinstance(action.handled_intent_types, set), f"Action {name}.handled_intent_types not a set"


class TestActionLoaderIntentMapping:
    """Test intent_type -> action mapping."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_intent_handler_map_built(self):
        """Verify intent handler map is built during discovery."""
        ActionLoader.discover_and_load(workspace=Path.cwd())
        intent_map = ActionLoader.get_intent_handler_map()

        assert isinstance(intent_map, dict)
        # ShellAction handles at least these
        assert "git_status" in intent_map
        assert "git_commit" in intent_map
        assert "shell_execute" in intent_map

    def test_get_handler_for_intent(self):
        """Test get_handler_for_intent utility."""
        ActionLoader.discover_and_load(workspace=Path.cwd())

        handler = ActionLoader.get_handler_for_intent("git_status")
        assert handler == "shell_action"

    def test_get_handler_for_unknown_intent(self):
        """Test get_handler_for_intent returns None for unknown."""
        ActionLoader.discover_and_load(workspace=Path.cwd())

        handler = ActionLoader.get_handler_for_intent("unknown_intent_xyz")
        assert handler is None

    def test_get_action_for_intent(self):
        """Test get_action_for_intent utility."""
        action = ActionLoader.get_action_for_intent("git_status", workspace=Path.cwd())
        assert action is not None
        assert action.name == "shell_action"

    def test_get_action_for_unknown_intent(self):
        """Test get_action_for_intent returns None for unknown."""
        action = ActionLoader.get_action_for_intent("unknown_intent_xyz", workspace=Path.cwd())
        assert action is None


class TestActionLoaderCaching:
    """Test caching behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_caching_enabled(self):
        """Verify second call returns cached results."""
        actions1, _ = ActionLoader.discover_and_load(workspace=Path.cwd())
        actions2, _ = ActionLoader.discover_and_load(workspace=Path.cwd())
        assert actions1 is actions2

    def test_force_refresh_bypasses_cache(self):
        """Verify force_refresh creates new instances."""
        actions1, _ = ActionLoader.discover_and_load(workspace=Path.cwd())
        actions2, _ = ActionLoader.discover_and_load(workspace=Path.cwd(), force_refresh=True)
        assert actions1 is not actions2

    def test_clear_cache_works(self):
        """Verify clear_cache resets the cache."""
        actions1, _ = ActionLoader.discover_and_load(workspace=Path.cwd())
        ActionLoader.clear_cache()
        actions2, _ = ActionLoader.discover_and_load(workspace=Path.cwd())
        assert actions1 is not actions2


class TestActionLoaderStrictMode:
    """Test STRICT MODE behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_strict_mode_enabled_by_default(self):
        """Verify strict_mode is True by default."""
        assert ActionLoader.strict_mode is True

    def test_strict_mode_can_be_disabled(self):
        """Verify strict mode can be disabled per-call."""
        actions, _ = ActionLoader.discover_and_load(
            workspace=Path.cwd(),
            strict=False,
        )
        assert len(actions) >= 1


class TestActionLoaderUtilities:
    """Test utility methods."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_list_actions(self):
        """Test list_actions utility method."""
        names = ActionLoader.list_actions(workspace=Path.cwd())
        assert isinstance(names, list)
        assert "shell_action" in names

    def test_get_action(self):
        """Test get_action utility method."""
        action = ActionLoader.get_action("shell_action", workspace=Path.cwd())
        assert action is not None
        assert action.name == "shell_action"

    def test_get_action_nonexistent(self):
        """Test get_action returns None for unknown action."""
        action = ActionLoader.get_action("nonexistent", workspace=Path.cwd())
        assert action is None


class TestShellAction:
    """Test ShellAction specifically."""

    def setup_method(self):
        """Clear cache before each test."""
        ActionLoader.clear_cache()

    def test_shell_action_can_handle(self):
        """Test can_handle method."""
        action = ActionLoader.get_action("shell_action", workspace=Path.cwd())
        assert action.can_handle("git_status")
        assert action.can_handle("git_commit")
        assert not action.can_handle("unknown_intent")

    def test_shell_action_handled_types(self):
        """Test handled_intent_types contains expected types."""
        action = ActionLoader.get_action("shell_action", workspace=Path.cwd())
        expected = {"git_status", "git_commit", "git_push", "shell_execute"}
        for intent_type in expected:
            assert intent_type in action.handled_intent_types
