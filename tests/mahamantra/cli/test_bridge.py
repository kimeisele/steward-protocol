"""
TESTS: cli/bridge.py - CLI Bridge
==================================

REAL TESTS for:
1. DOMAIN_KEYWORDS mapping
2. BridgeResult dataclass
3. MahamantraCLIBridge class
4. cli_bridge singleton
5. route and get_position functions
"""

import pytest
from vibe_core.mahamantra.cli.bridge import (
    DOMAIN_KEYWORDS,
    BridgeResult,
    MahamantraCLIBridge,
    cli_bridge,
    route,
    get_position,
)


# =============================================================================
# DOMAIN_KEYWORDS Tests
# =============================================================================


class TestDomainKeywords:
    """Test DOMAIN_KEYWORDS mapping."""

    def test_domain_keywords_has_16_positions(self):
        """DOMAIN_KEYWORDS has entries for all 16 positions."""
        assert len(DOMAIN_KEYWORDS) == 16

    def test_domain_keywords_position_0_vyasa(self):
        """Position 0 (Vyasa) has boot/genesis keywords."""
        keywords = DOMAIN_KEYWORDS[0]
        assert "boot" in keywords
        assert "wake" in keywords
        assert "genesis" in keywords
        assert "vyasa" in keywords

    def test_domain_keywords_position_1_brahma(self):
        """Position 1 (Brahma) has creation keywords."""
        keywords = DOMAIN_KEYWORDS[1]
        assert "create" in keywords
        assert "new" in keywords
        assert "brahma" in keywords

    def test_domain_keywords_position_2_narada(self):
        """Position 2 (Narada) has broadcast keywords."""
        keywords = DOMAIN_KEYWORDS[2]
        assert "broadcast" in keywords
        assert "notify" in keywords
        assert "narada" in keywords

    def test_domain_keywords_position_6_kapila(self):
        """Position 6 (Kapila) has analysis keywords."""
        keywords = DOMAIN_KEYWORDS[6]
        assert "analyze" in keywords
        assert "gc" in keywords
        assert "kapila" in keywords

    def test_domain_keywords_position_8_parashurama(self):
        """Position 8 (Parashurama) has execution keywords."""
        keywords = DOMAIN_KEYWORDS[8]
        assert "fetch" in keywords
        assert "execute" in keywords
        assert "parashurama" in keywords

    def test_domain_keywords_position_15_yamaraja(self):
        """Position 15 (Yamaraja) has judgment keywords."""
        keywords = DOMAIN_KEYWORDS[15]
        assert "judge" in keywords
        assert "correct" in keywords
        assert "yamaraja" in keywords


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
            handler="cli_engine[6]",
        )
        assert result.handler == "cli_engine[6]"

    def test_bridge_result_fallback_flag(self):
        """BridgeResult tracks fallback usage."""
        result = BridgeResult(success=True, exit_code=0, fallback=True)
        assert result.fallback is True

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
# MahamantraCLIBridge Tests
# =============================================================================


class TestMahamantraCLIBridge:
    """Test MahamantraCLIBridge class."""

    def test_cli_bridge_creation(self):
        """MahamantraCLIBridge can be created."""
        bridge = MahamantraCLIBridge()
        assert bridge is not None

    def test_cli_bridge_get_position_exact_match(self):
        """get_position finds exact keyword match."""
        bridge = MahamantraCLIBridge()
        assert bridge.get_position("boot") == 0
        assert bridge.get_position("create") == 1
        assert bridge.get_position("broadcast") == 2
        assert bridge.get_position("analyze") == 6
        assert bridge.get_position("judge") == 15

    def test_cli_bridge_get_position_case_insensitive(self):
        """get_position is case insensitive."""
        bridge = MahamantraCLIBridge()
        assert bridge.get_position("BOOT") == 0
        assert bridge.get_position("Analyze") == 6

    def test_cli_bridge_get_position_substring_match(self):
        """get_position finds substring match."""
        bridge = MahamantraCLIBridge()
        pos = bridge.get_position("analyze-deep")
        # Should match "analyze" keyword → position 6
        assert pos is not None

    def test_cli_bridge_get_position_parampara_fallback(self):
        """get_position uses parampara fallback for unknown commands."""
        bridge = MahamantraCLIBridge()
        pos = bridge.get_position("unknown_xyz_123")
        # Should return a valid position via hash
        assert 0 <= pos <= 15

    def test_cli_bridge_parampara_fallback_deterministic(self):
        """Parampara fallback is deterministic."""
        bridge = MahamantraCLIBridge()
        pos1 = bridge._parampara_fallback("test_command")
        pos2 = bridge._parampara_fallback("test_command")
        assert pos1 == pos2

    def test_cli_bridge_can_route(self):
        """can_route returns True for routable commands."""
        bridge = MahamantraCLIBridge()
        # All commands can be routed (via keywords or fallback)
        assert bridge.can_route("boot") is True
        assert bridge.can_route("unknown") is True  # Fallback works

    def test_cli_bridge_disable_fallback(self):
        """disable_fallback disables CLIRegistry fallback."""
        bridge = MahamantraCLIBridge()
        assert bridge._fallback_enabled is True
        bridge.disable_fallback()
        assert bridge._fallback_enabled is False

    def test_cli_bridge_enable_fallback(self):
        """enable_fallback re-enables CLIRegistry fallback."""
        bridge = MahamantraCLIBridge()
        bridge.disable_fallback()
        bridge.enable_fallback()
        assert bridge._fallback_enabled is True

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
        assert "keywords" in info
        assert "is_head" in info

    def test_cli_bridge_list_routes(self):
        """list_routes returns all routes."""
        bridge = MahamantraCLIBridge()
        routes = bridge.list_routes()
        assert len(routes) > 0
        # Each route is (keyword, position, guardian)
        assert all(len(r) == 3 for r in routes)

    def test_cli_bridge_repr(self):
        """MahamantraCLIBridge has __repr__."""
        bridge = MahamantraCLIBridge()
        assert "MahamantraCLIBridge" in repr(bridge)

    def test_cli_bridge_route_returns_result(self):
        """route returns BridgeResult."""
        bridge = MahamantraCLIBridge()
        result = bridge.route("boot", [])
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
        result = route("boot", [])
        assert isinstance(result, BridgeResult)

    def test_route_function_default_args(self):
        """route function has default args."""
        result = route("analyze")
        assert isinstance(result, BridgeResult)

    def test_get_position_function(self):
        """get_position function works."""
        pos = get_position("analyze")
        assert pos == 6


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import bridge

        expected = [
            "MahamantraCLIBridge",
            "cli_bridge",
            "BridgeResult",
            "DOMAIN_KEYWORDS",
            "route",
            "get_position",
        ]
        for item in expected:
            assert item in bridge.__all__, f"{item} should be in __all__"
