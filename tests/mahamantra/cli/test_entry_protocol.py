"""
TESTS: cli/entry_protocol.py - CLI Entry Protocol
==================================================

REAL TESTS for:
1. CLIEntryProtocol protocol
2. CLIEntryResult dataclass
"""

import pytest
from typing import List
from vibe_core.mahamantra.cli.entry_protocol import (
    CLIEntryProtocol,
    CLIEntryResult,
)
from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIHealth,
    CLIResult,
    CLIState,
)


# =============================================================================
# CLIEntryProtocol Tests
# =============================================================================


class TestCLIEntryProtocol:
    """Test CLIEntryProtocol."""

    def test_cli_entry_protocol_is_protocol(self):
        """CLIEntryProtocol is a runtime checkable protocol."""
        assert hasattr(CLIEntryProtocol, "__protocol_attrs__") or hasattr(CLIEntryProtocol, "_is_runtime_protocol")

    def test_cli_entry_protocol_implementation(self):
        """CLIEntryProtocol can be implemented."""

        class TestEntry:
            def run(self, args: List[str]) -> int:
                return 0

            def discover(self) -> List[CLICapability]:
                return []

            def get_state(self) -> CLIState:
                return CLIState()

            def check_health(self) -> CLIHealth:
                return CLIHealth()

        entry = TestEntry()
        assert entry.run([]) == 0
        assert isinstance(entry.discover(), list)
        assert isinstance(entry.get_state(), CLIState)
        assert isinstance(entry.check_health(), CLIHealth)

    def test_cli_entry_protocol_isinstance_check(self):
        """CLIEntryProtocol can be checked with isinstance."""

        class TestEntry:
            def run(self, args: List[str]) -> int:
                return 0

            def discover(self) -> List[CLICapability]:
                return []

            def get_state(self) -> CLIState:
                return CLIState()

            def check_health(self) -> CLIHealth:
                return CLIHealth()

        entry = TestEntry()
        # Runtime checkable protocol should work with isinstance
        assert isinstance(entry, CLIEntryProtocol)


# =============================================================================
# CLIEntryResult Tests
# =============================================================================


class TestCLIEntryResult:
    """Test CLIEntryResult dataclass."""

    def test_cli_entry_result_creation(self):
        """CLIEntryResult can be created."""
        result = CLIEntryResult(
            result=CLIResult.ok(),
            command="test",
            args=["--verbose"],
        )
        assert result.command == "test"
        assert result.args == ["--verbose"]
        assert result.result.success is True

    def test_cli_entry_result_with_routing(self):
        """CLIEntryResult tracks routing info."""
        result = CLIEntryResult(
            result=CLIResult.ok(data="result"),
            command="analyze",
            args=["system"],
            routed_to="mahamantra[6].analyze",
        )
        assert result.routed_to == "mahamantra[6].analyze"

    def test_cli_entry_result_fallback_flag(self):
        """CLIEntryResult tracks fallback usage."""
        result = CLIEntryResult(
            result=CLIResult.ok(),
            command="legacy",
            args=[],
            fallback_used=True,
        )
        assert result.fallback_used is True

    def test_cli_entry_result_defaults(self):
        """CLIEntryResult has correct defaults."""
        result = CLIEntryResult(
            result=CLIResult.ok(),
            command="cmd",
            args=[],
        )
        assert result.routed_to is None
        assert result.fallback_used is False


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import entry_protocol

        expected = [
            "CLIEntryProtocol",
            "CLIEntryResult",
        ]
        for item in expected:
            assert item in entry_protocol.__all__, f"{item} should be in __all__"
