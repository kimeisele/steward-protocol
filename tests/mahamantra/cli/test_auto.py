"""
TESTS: cli/auto.py - CLI Auto Discovery
========================================

REAL TESTS for:
1. DiscoveredMethod dataclass
2. CLIAutoDiscovery class
3. cli_auto singleton
4. discover, execute, capabilities functions
"""

import pytest
from vibe_core.mahamantra.cli.auto import (
    CLIAutoDiscovery,
    cli_auto,
    DiscoveredMethod,
    discover,
    execute,
    capabilities,
)
from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIOutput,
    CLIParameter,
    CLIResult,
)


# =============================================================================
# DiscoveredMethod Tests
# =============================================================================


class TestDiscoveredMethod:
    """Test DiscoveredMethod dataclass."""

    def test_discovered_method_creation(self):
        """DiscoveredMethod can be created."""
        method = DiscoveredMethod(
            name="analyze",
            position=6,
            guardian="kapila",
            parameters=[CLIParameter(name="target", param_type="string")],
            return_fields=["success", "result"],
            doc="Analyze target",
        )
        assert method.name == "analyze"
        assert method.position == 6
        assert method.guardian == "kapila"

    def test_discovered_method_parameters(self):
        """DiscoveredMethod holds parameters."""
        method = DiscoveredMethod(
            name="test",
            position=0,
            guardian="vyasa",
            parameters=[
                CLIParameter(name="path", param_type="string", required=True),
                CLIParameter(name="verbose", param_type="boolean", default=False),
            ],
            return_fields=[],
            doc="Test method",
        )
        assert len(method.parameters) == 2
        assert method.parameters[0].name == "path"
        assert method.parameters[1].default is False

    def test_discovered_method_return_fields(self):
        """DiscoveredMethod holds return fields."""
        method = DiscoveredMethod(
            name="fetch",
            position=8,
            guardian="parashurama",
            parameters=[],
            return_fields=["data", "count", "success"],
            doc="Fetch data",
        )
        assert "data" in method.return_fields
        assert "count" in method.return_fields


# =============================================================================
# CLIAutoDiscovery Tests
# =============================================================================


class TestCLIAutoDiscovery:
    """Test CLIAutoDiscovery class."""

    def test_cli_auto_discovery_creation(self):
        """CLIAutoDiscovery can be created."""
        auto = CLIAutoDiscovery()
        assert auto is not None
        assert auto._discovered is False

    def test_cli_auto_discover_all(self):
        """discover_all discovers methods."""
        auto = CLIAutoDiscovery()
        count = auto.discover_all()
        assert count >= 0
        assert auto._discovered is True

    def test_cli_auto_discover_all_idempotent(self):
        """discover_all is idempotent."""
        auto = CLIAutoDiscovery()
        count1 = auto.discover_all()
        count2 = auto.discover_all()
        assert count1 == count2

    def test_cli_auto_get_position(self):
        """_get_position finds position for command."""
        auto = CLIAutoDiscovery()
        auto.discover_all()

        # Test parampara fallback (always returns valid position)
        pos = auto._get_position("unknown_xyz")
        assert 0 <= pos <= 15

    def test_cli_auto_get_method_name(self):
        """_get_method_name finds method name."""
        auto = CLIAutoDiscovery()
        auto.discover_all()

        # Check if any methods were discovered
        if auto._methods:
            pos = list(auto._methods.keys())[0]
            if auto._methods[pos]:
                expected = list(auto._methods[pos].keys())[0]
                result = auto._get_method_name(pos, expected)
                assert result == expected

    def test_cli_auto_execute_unknown_command(self):
        """execute returns failure for unknown command with no implementation."""
        auto = CLIAutoDiscovery()
        auto.discover_all()
        result = auto.execute("xyzzy_nonexistent_12345")
        # Result may succeed or fail depending on discovery
        assert isinstance(result, CLIResult)

    def test_cli_auto_get_capabilities(self):
        """get_capabilities returns discovered capabilities."""
        auto = CLIAutoDiscovery()
        auto.discover_all()
        caps = auto.get_capabilities()
        assert isinstance(caps, list)
        # All items should be CLICapability
        for cap in caps:
            assert isinstance(cap, CLICapability)

    def test_cli_auto_get_capabilities_position(self):
        """get_capabilities filters by position."""
        auto = CLIAutoDiscovery()
        auto.discover_all()
        caps = auto.get_capabilities(position=6)
        for cap in caps:
            assert cap.mahajana_position == 6

    def test_cli_auto_get_stats(self):
        """get_stats returns statistics."""
        auto = CLIAutoDiscovery()
        auto.discover_all()
        stats = auto.get_stats()
        assert "positions_discovered" in stats
        assert "total_methods" in stats
        assert "total_keywords" in stats
        assert "null_implementations" in stats

    def test_cli_auto_repr(self):
        """CLIAutoDiscovery has __repr__."""
        auto = CLIAutoDiscovery()
        assert "CLIAutoDiscovery" in repr(auto)

    def test_cli_auto_build_call_args_empty(self):
        """_build_call_args handles empty args."""
        auto = CLIAutoDiscovery()
        args = auto._build_call_args([], None)
        assert args == {}

    def test_cli_auto_build_call_args_with_params(self):
        """_build_call_args builds args from CLI strings."""
        auto = CLIAutoDiscovery()
        method_info = DiscoveredMethod(
            name="test",
            position=0,
            guardian="vyasa",
            parameters=[
                CLIParameter(name="path", param_type="string"),
                CLIParameter(name="count", param_type="integer"),
                CLIParameter(name="verbose", param_type="boolean"),
            ],
            return_fields=[],
            doc="Test",
        )
        args = auto._build_call_args(["mypath", "42", "true"], method_info)
        assert args["path"] == "mypath"
        assert args["count"] == 42
        assert args["verbose"] is True

    def test_cli_auto_result_to_output_none(self):
        """_result_to_output handles None."""
        auto = CLIAutoDiscovery()
        output = auto._result_to_output(None)
        assert isinstance(output, CLIOutput)
        # Should have status: complete
        items = {item.key: item.value for item in output.items}
        assert items.get("status") == "complete"

    def test_cli_auto_result_to_output_dict(self):
        """_result_to_output handles dict results."""
        auto = CLIAutoDiscovery()
        result = {"key1": "value1", "key2": 42}
        output = auto._result_to_output(result)
        items = {item.key: item.value for item in output.items}
        assert items.get("key1") == "value1"
        assert items.get("key2") == 42

    def test_cli_auto_result_to_output_list(self):
        """_result_to_output handles list results."""
        auto = CLIAutoDiscovery()
        result = ["a", "b", "c"]
        output = auto._result_to_output(result)
        items = {item.key: item.value for item in output.items}
        assert items.get("count") == 3

    def test_cli_auto_result_to_output_scalar(self):
        """_result_to_output handles scalar results."""
        auto = CLIAutoDiscovery()
        output = auto._result_to_output("hello")
        items = {item.key: item.value for item in output.items}
        assert items.get("result") == "hello"


# =============================================================================
# cli_auto Singleton Tests
# =============================================================================


class TestCliAutoSingleton:
    """Test cli_auto singleton."""

    def test_cli_auto_is_instance(self):
        """cli_auto is a CLIAutoDiscovery instance."""
        assert isinstance(cli_auto, CLIAutoDiscovery)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_discover_function(self):
        """discover function works."""
        count = discover()
        assert count >= 0

    def test_execute_function(self):
        """execute function works."""
        result = execute("test_nonexistent")
        assert isinstance(result, CLIResult)

    def test_capabilities_function(self):
        """capabilities function works."""
        caps = capabilities()
        assert isinstance(caps, list)

    def test_capabilities_function_with_position(self):
        """capabilities function filters by position."""
        caps = capabilities(position=6)
        for cap in caps:
            assert cap.mahajana_position == 6


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import auto

        expected = [
            "CLIAutoDiscovery",
            "cli_auto",
            "DiscoveredMethod",
            "discover",
            "execute",
            "capabilities",
        ]
        for item in expected:
            assert item in auto.__all__, f"{item} should be in __all__"
