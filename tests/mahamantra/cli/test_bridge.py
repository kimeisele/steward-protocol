"""
TESTS: cli/bridge.py - CLI Bridge (Resonance-Based)
====================================================

REAL TESTS for:
1. BridgeResult dataclass
2. MahamantraCLIBridge class (resonance-based routing)
3. cli_bridge singleton
4. route and get_position functions

KREBS ENTFERNT: No keyword matching tests - resonance only.
"""

import pytest
from vibe_core.mahamantra.cli.bridge import (
    BridgeResult,
    MahamantraCLIBridge,
    cli_bridge,
    route,
    get_position,
)
from vibe_core.mahamantra.substrate.seed import WORDS


# =============================================================================
# BridgeResult Tests
# =============================================================================


class TestBridgeResult:
    """Test BridgeResult dataclass."""

    def test_bridge_result_creation(self):
        """BridgeResult can be created."""
        result = BridgeResult(success=True, exit_code=0)
        assert result.success is True
        assert result.exit_code == 0

    def test_bridge_result_with_position(self):
        """BridgeResult tracks position."""
        result = BridgeResult(success=True, exit_code=0, position=6)
        assert result.position == 6

    def test_bridge_result_with_handler(self):
        """BridgeResult tracks handler name."""
        result = BridgeResult(
            success=True,
            exit_code=0,
            handler="mahamantra[6]",
        )
        assert result.handler == "mahamantra[6]"

    def test_bridge_result_with_error(self):
        """BridgeResult tracks error message."""
        result = BridgeResult(
            success=False,
            exit_code=1,
            error="Command not found",
        )
        assert result.success is False
        assert result.error == "Command not found"


# =============================================================================
# MahamantraCLIBridge Tests (Resonance-Based)
# =============================================================================


class TestMahamantraCLIBridge:
    """Test MahamantraCLIBridge class with resonance-based routing."""

    def test_cli_bridge_creation(self):
        """MahamantraCLIBridge can be created."""
        bridge = MahamantraCLIBridge()
        assert bridge is not None

    def test_cli_bridge_get_position_returns_valid(self):
        """get_position returns valid position (0 to WORDS-1)."""
        bridge = MahamantraCLIBridge()
        # Resonance-based - any command gets a position
        pos = bridge.get_position("status")
        assert pos is not None
        assert 0 <= pos < WORDS

    def test_cli_bridge_get_position_case_insensitive(self):
        """get_position is case insensitive."""
        bridge = MahamantraCLIBridge()
        pos1 = bridge.get_position("status")
        pos2 = bridge.get_position("STATUS")
        assert pos1 == pos2

    def test_cli_bridge_get_position_deterministic(self):
        """Resonance routing is deterministic."""
        bridge = MahamantraCLIBridge()
        pos1 = bridge.get_position("test_command")
        pos2 = bridge.get_position("test_command")
        assert pos1 == pos2

    def test_cli_bridge_can_route(self):
        """can_route returns True for all commands (resonance always routes)."""
        bridge = MahamantraCLIBridge()
        # Resonance-based routing always works
        assert bridge.can_route("boot") is True
        assert bridge.can_route("unknown_xyz_123") is True

    def test_cli_bridge_register_handler(self):
        """register_handler registers custom handler."""
        bridge = MahamantraCLIBridge()

        def custom_handler(cmd, args):
            return 0

        bridge.register_handler(6, custom_handler)
        assert 6 in bridge._handlers

    def test_cli_bridge_get_domain_info(self):
        """get_domain_info returns domain info."""
        bridge = MahamantraCLIBridge()
        info = bridge.get_domain_info(6)
        assert "guardian" in info
        assert "opcode" in info
        assert "is_head" in info

    def test_cli_bridge_list_routes(self):
        """list_routes returns WORDS routes (all positions)."""
        bridge = MahamantraCLIBridge()
        routes = bridge.list_routes()
        assert len(routes) == WORDS  # SSOT: WORDS positions
        # Each route is (guardian, position, guardian)
        assert all(len(r) == 3 for r in routes)

    def test_cli_bridge_repr(self):
        """MahamantraCLIBridge has __repr__ with WORDS."""
        bridge = MahamantraCLIBridge()
        repr_str = repr(bridge)
        assert "MahamantraCLIBridge" in repr_str
        assert f"positions={WORDS}" in repr_str

    def test_cli_bridge_route_returns_result(self):
        """route returns BridgeResult."""
        bridge = MahamantraCLIBridge()
        result = bridge.route("status", [])
        assert isinstance(result, BridgeResult)
        assert result.position is not None


# =============================================================================
# cli_bridge Singleton Tests
# =============================================================================


class TestCliBridgeSingleton:
    """Test cli_bridge singleton."""

    def test_cli_bridge_is_instance(self):
        """cli_bridge is a MahamantraCLIBridge instance."""
        assert isinstance(cli_bridge, MahamantraCLIBridge)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_route_function(self):
        """route function works."""
        result = route("status", [])
        assert isinstance(result, BridgeResult)

    def test_route_function_default_args(self):
        """route function has default args."""
        result = route("analyze")
        assert isinstance(result, BridgeResult)

    def test_get_position_function(self):
        """get_position function returns valid position."""
        pos = get_position("analyze")
        assert pos is not None
        assert 0 <= pos < WORDS


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import bridge

        # KREBS ENTFERNT: DOMAIN_KEYWORDS removed from exports
        expected = [
            "MahamantraCLIBridge",
            "cli_bridge",
            "BridgeResult",
            "route",
            "get_position",
        ]
        for item in expected:
            assert item in bridge.__all__, f"{item} should be in __all__"
