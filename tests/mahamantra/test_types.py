"""
TESTS: _types.py - Watertight TypedDicts
========================================

"nānyaṁ guṇebhyaḥ kartāraṁ yadā draṣṭānupaśyati"

REAL TESTS for:
1. TickState TypedDict
2. RouteResult TypedDict
3. ExecuteResult TypedDict
4. LilaState TypedDict
"""

import pytest
from typing import get_type_hints
from vibe_core.mahamantra._types import (
    TickState,
    RouteResult,
    ExecuteResult,
    LilaState,
)


class TestTickState:
    """Test TickState TypedDict."""

    def test_tick_state_keys(self):
        """TickState has correct keys."""
        hints = get_type_hints(TickState)
        expected_keys = {"tick", "position", "quarter", "guardian", "word", "opcode"}
        assert set(hints.keys()) == expected_keys

    def test_tick_state_can_be_created(self):
        """TickState can be instantiated."""
        state: TickState = {
            "tick": 0,
            "position": 0,
            "quarter": "GENESIS",
            "guardian": "vyasa",
            "word": "Hare",
            "opcode": 0,
        }
        assert state["tick"] == 0
        assert state["position"] == 0
        assert state["quarter"] == "GENESIS"

    def test_tick_state_opcode_optional(self):
        """TickState opcode can be None."""
        state: TickState = {
            "tick": 5,
            "position": 5,
            "quarter": "DHARMA",
            "guardian": "kumaras",
            "word": "Krishna",
            "opcode": None,
        }
        assert state["opcode"] is None


class TestRouteResult:
    """Test RouteResult TypedDict."""

    def test_route_result_keys(self):
        """RouteResult has correct keys."""
        hints = get_type_hints(RouteResult)
        expected_keys = {"position", "guardian", "quarter"}
        assert set(hints.keys()) == expected_keys

    def test_route_result_can_be_created(self):
        """RouteResult can be instantiated."""
        result: RouteResult = {
            "position": 6,
            "guardian": "kapila",
            "quarter": "DHARMA",
        }
        assert result["position"] == 6
        assert result["guardian"] == "kapila"


class TestExecuteResult:
    """Test ExecuteResult TypedDict."""

    def test_execute_result_keys(self):
        """ExecuteResult has correct keys."""
        hints = get_type_hints(ExecuteResult)
        expected_keys = {
            "success", "exit_code", "position", "guardian",
            "quarter", "guna", "requires_confirmation", "output", "error"
        }
        assert set(hints.keys()) == expected_keys

    def test_execute_result_can_be_created(self):
        """ExecuteResult can be instantiated."""
        result: ExecuteResult = {
            "success": True,
            "exit_code": 0,
            "position": 8,
            "guardian": "parashurama",
            "quarter": "KARMA",
            "guna": "rajas",
            "requires_confirmation": False,
            "output": "executed",
            "error": None,
        }
        assert result["success"] is True
        assert result["guna"] == "rajas"

    def test_execute_result_tamas_requires_confirmation(self):
        """TAMAS operations require confirmation."""
        result: ExecuteResult = {
            "success": False,
            "exit_code": 1,
            "position": 3,
            "guardian": "shambhu",
            "quarter": "GENESIS",
            "guna": "tamas",
            "requires_confirmation": True,
            "output": "",
            "error": "Requires user confirmation",
        }
        assert result["guna"] == "tamas"
        assert result["requires_confirmation"] is True


class TestLilaState:
    """Test LilaState TypedDict."""

    def test_lila_state_keys(self):
        """LilaState has correct keys."""
        hints = get_type_hints(LilaState)
        expected_keys = {
            "lila_position", "position", "phase", "cycle",
            "quarter", "guardian", "word", "opcode",
            "is_navadvipa", "is_puri"
        }
        assert set(hints.keys()) == expected_keys

    def test_lila_state_navadvipa_phase(self):
        """LilaState in Navadvipa phase (0-23)."""
        state: LilaState = {
            "lila_position": 10,
            "position": 10,
            "phase": "navadvipa",
            "cycle": 1,
            "quarter": "KARMA",
            "guardian": "janaka",
            "word": "Rama",
            "opcode": 10,
            "is_navadvipa": True,
            "is_puri": False,
        }
        assert state["phase"] == "navadvipa"
        assert state["is_navadvipa"] is True
        assert state["is_puri"] is False

    def test_lila_state_puri_phase(self):
        """LilaState in Puri phase (24-47)."""
        state: LilaState = {
            "lila_position": 30,
            "position": 14,  # 30 % 16 = 14
            "phase": "puri",
            "cycle": 2,
            "quarter": "MOKSHA",
            "guardian": "shuka",
            "word": "Hare",
            "opcode": 14,
            "is_navadvipa": False,
            "is_puri": True,
        }
        assert state["phase"] == "puri"
        assert state["is_navadvipa"] is False
        assert state["is_puri"] is True

    def test_lila_48_positions(self):
        """Lila has 48 positions (24 + 24)."""
        # Navadvipa: 0-23
        # Puri: 24-47
        navadvipa_end = 23
        puri_start = 24
        puri_end = 47

        state_nav: LilaState = {
            "lila_position": navadvipa_end,
            "position": navadvipa_end % 16,
            "phase": "navadvipa",
            "cycle": 2,
            "quarter": "DHARMA",
            "guardian": "manu",
            "word": "Hare",
            "opcode": None,
            "is_navadvipa": True,
            "is_puri": False,
        }
        assert state_nav["lila_position"] == 23

        state_puri: LilaState = {
            "lila_position": puri_end,
            "position": puri_end % 16,
            "phase": "puri",
            "cycle": 3,
            "quarter": "MOKSHA",
            "guardian": "yamaraja",
            "word": "Hare",
            "opcode": None,
            "is_navadvipa": False,
            "is_puri": True,
        }
        assert state_puri["lila_position"] == 47


class TestTypeExports:
    """Test module exports."""

    def test_all_types_exported(self):
        """All types are in __all__."""
        from vibe_core.mahamantra import _types
        assert "TickState" in _types.__all__
        assert "RouteResult" in _types.__all__
        assert "ExecuteResult" in _types.__all__
        assert "LilaState" in _types.__all__
