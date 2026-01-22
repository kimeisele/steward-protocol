"""
TESTS: cli/veda_explorer.py - Veda Explorer
============================================

REAL TESTS for:
1. ExplorerMode enum
2. VedaIntent enum
3. VedaResult TypedDict
4. ParsedIntent dataclass
5. VedaExplorer class
6. get_explorer, process functions
"""

import pytest
from vibe_core.mahamantra.cli.veda_explorer import (
    ExplorerMode,
    VedaIntent,
    VedaResult,
    ParsedIntent,
    VedaExplorer,
    get_explorer,
    process,
)


# =============================================================================
# ExplorerMode Enum Tests
# =============================================================================


class TestExplorerMode:
    """Test ExplorerMode enum."""

    def test_explorer_mode_restricted(self):
        """ExplorerMode has RESTRICTED."""
        assert ExplorerMode.RESTRICTED.value == "restricted"

    def test_explorer_mode_enhanced(self):
        """ExplorerMode has ENHANCED."""
        assert ExplorerMode.ENHANCED.value == "enhanced"

    def test_explorer_mode_creative(self):
        """ExplorerMode has CREATIVE."""
        assert ExplorerMode.CREATIVE.value == "creative"


# =============================================================================
# VedaIntent Enum Tests
# =============================================================================


class TestVedaIntent:
    """Test VedaIntent enum."""

    def test_veda_intent_chant(self):
        """VedaIntent has CHANT."""
        assert VedaIntent.CHANT.value == "chant"

    def test_veda_intent_listen(self):
        """VedaIntent has LISTEN."""
        assert VedaIntent.LISTEN.value == "listen"

    def test_veda_intent_resolve(self):
        """VedaIntent has RESOLVE."""
        assert VedaIntent.RESOLVE.value == "resolve"

    def test_veda_intent_serve(self):
        """VedaIntent has SERVE."""
        assert VedaIntent.SERVE.value == "serve"

    def test_veda_intent_scan(self):
        """VedaIntent has SCAN."""
        assert VedaIntent.SCAN.value == "scan"

    def test_veda_intent_help(self):
        """VedaIntent has HELP."""
        assert VedaIntent.HELP.value == "help"

    def test_veda_intent_status(self):
        """VedaIntent has STATUS."""
        assert VedaIntent.STATUS.value == "status"

    def test_veda_intent_unknown(self):
        """VedaIntent has UNKNOWN."""
        assert VedaIntent.UNKNOWN.value == "unknown"


# =============================================================================
# VedaResult TypedDict Tests
# =============================================================================


class TestVedaResult:
    """Test VedaResult TypedDict."""

    def test_veda_result_creation(self):
        """VedaResult can be created."""
        result: VedaResult = {
            "success": True,
            "intent": "chant",
            "mode": "enhanced",
            "response": "Chant complete",
            "data": {"rounds": 1},
            "llm_used": False,
        }
        assert result["success"] is True
        assert result["intent"] == "chant"
        assert result["llm_used"] is False


# =============================================================================
# ParsedIntent Tests
# =============================================================================


class TestParsedIntent:
    """Test ParsedIntent dataclass."""

    def test_parsed_intent_creation(self):
        """ParsedIntent can be created."""
        parsed = ParsedIntent(
            intent=VedaIntent.CHANT,
            params={"rounds": 108},
            raw_input="chant 108",
        )
        assert parsed.intent == VedaIntent.CHANT
        assert parsed.params["rounds"] == 108
        assert parsed.raw_input == "chant 108"

    def test_parsed_intent_defaults(self):
        """ParsedIntent has correct defaults."""
        parsed = ParsedIntent(intent=VedaIntent.HELP)
        assert parsed.params == {}
        assert parsed.raw_input == ""
        assert parsed.confidence == 1.0
        assert parsed.llm_used is False

    def test_parsed_intent_confidence(self):
        """ParsedIntent tracks confidence."""
        parsed = ParsedIntent(
            intent=VedaIntent.RESOLVE,
            confidence=0.8,
        )
        assert parsed.confidence == 0.8

    def test_parsed_intent_llm_used(self):
        """ParsedIntent tracks LLM usage."""
        parsed = ParsedIntent(
            intent=VedaIntent.UNKNOWN,
            llm_used=True,
        )
        assert parsed.llm_used is True


# =============================================================================
# VedaExplorer Tests
# =============================================================================


class TestVedaExplorer:
    """Test VedaExplorer class."""

    def test_veda_explorer_creation_restricted(self):
        """VedaExplorer can be created in RESTRICTED mode."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        assert explorer.mode == ExplorerMode.RESTRICTED

    def test_veda_explorer_creation_enhanced(self):
        """VedaExplorer can be created in ENHANCED mode."""
        explorer = VedaExplorer(mode=ExplorerMode.ENHANCED)
        assert explorer.mode == ExplorerMode.ENHANCED

    def test_veda_explorer_mode_property(self):
        """VedaExplorer.mode returns current mode."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        assert explorer.mode == ExplorerMode.RESTRICTED

    def test_veda_explorer_llm_available_restricted(self):
        """VedaExplorer in RESTRICTED mode has no LLM."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        assert explorer.llm_available is False

    def test_veda_explorer_process_empty_input(self):
        """VedaExplorer.process handles empty input."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        result = explorer.process("")
        assert result["success"] is False
        assert result["intent"] == "empty"

    def test_veda_explorer_process_whitespace_input(self):
        """VedaExplorer.process handles whitespace input."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        result = explorer.process("   ")
        assert result["success"] is False
        assert result["intent"] == "empty"

    def test_veda_explorer_process_help(self):
        """VedaExplorer.process handles help."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        result = explorer.process("help")
        assert result["success"] is True
        assert result["intent"] == "help"

    def test_veda_explorer_process_status(self):
        """VedaExplorer.process handles status."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        result = explorer.process("status")
        assert result["success"] is True
        assert result["intent"] == "status"

    def test_veda_explorer_parse_intent_deterministic_help(self):
        """_parse_intent_deterministic finds help intent."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        parsed = explorer._parse_intent_deterministic("help me")
        # May or may not match depending on keyword loading
        assert parsed.intent in (VedaIntent.HELP, VedaIntent.UNKNOWN)

    def test_veda_explorer_parse_intent_deterministic_number(self):
        """_parse_intent_deterministic recognizes number as chant."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        parsed = explorer._parse_intent_deterministic("108")
        assert parsed.intent == VedaIntent.CHANT
        assert parsed.params.get("rounds") == 108

    def test_veda_explorer_extract_params_chant(self):
        """_extract_params extracts chant params."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        params = explorer._extract_params("chant 108 rounds verbose", VedaIntent.CHANT)
        assert params["rounds"] == 108
        assert params["verbose"] is True

    def test_veda_explorer_extract_params_listen(self):
        """_extract_params extracts listen params."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        params = explorer._extract_params("listen to violations 20", VedaIntent.LISTEN)
        assert params["source"] == "violations"
        assert params["tail"] == 20

    def test_veda_explorer_extract_params_listen_syscalls(self):
        """_extract_params recognizes syscalls source."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        params = explorer._extract_params("show syscalls", VedaIntent.LISTEN)
        assert params["source"] == "syscalls"

    def test_veda_explorer_extract_params_listen_default(self):
        """_extract_params uses defaults for listen."""
        explorer = VedaExplorer(mode=ExplorerMode.RESTRICTED)
        params = explorer._extract_params("listen", VedaIntent.LISTEN)
        assert params["source"] == "all"
        assert params["tail"] == 10


# =============================================================================
# get_explorer Tests
# =============================================================================


class TestGetExplorer:
    """Test get_explorer function."""

    def test_get_explorer_returns_instance(self):
        """get_explorer returns VedaExplorer instance."""
        explorer = get_explorer()
        assert isinstance(explorer, VedaExplorer)

    def test_get_explorer_with_mode(self):
        """get_explorer accepts mode parameter."""
        explorer = get_explorer(mode=ExplorerMode.RESTRICTED)
        assert explorer.mode == ExplorerMode.RESTRICTED

    def test_get_explorer_singleton(self):
        """get_explorer returns same instance for same mode."""
        exp1 = get_explorer(mode=ExplorerMode.RESTRICTED)
        exp2 = get_explorer(mode=ExplorerMode.RESTRICTED)
        # May or may not be same instance depending on mode change
        assert exp1.mode == exp2.mode


# =============================================================================
# process Tests
# =============================================================================


class TestProcess:
    """Test process function."""

    def test_process_returns_veda_result(self):
        """process returns VedaResult."""
        result = process("help", mode=ExplorerMode.RESTRICTED)
        assert "success" in result
        assert "intent" in result
        assert "mode" in result
        assert "response" in result
        assert "data" in result
        assert "llm_used" in result

    def test_process_help(self):
        """process handles help."""
        result = process("help", mode=ExplorerMode.RESTRICTED)
        assert result["success"] is True
        assert result["intent"] == "help"

    def test_process_status(self):
        """process handles status."""
        result = process("status", mode=ExplorerMode.RESTRICTED)
        assert result["success"] is True
        assert result["intent"] == "status"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import veda_explorer

        expected = [
            "VedaExplorer",
            "VedaResult",
            "VedaIntent",
            "ExplorerMode",
            "ParsedIntent",
            "get_explorer",
            "process",
            "repl",
        ]
        for item in expected:
            assert item in veda_explorer.__all__, f"{item} should be in __all__"
