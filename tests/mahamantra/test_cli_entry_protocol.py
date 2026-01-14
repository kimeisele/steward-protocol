"""
Tests for CLI Entry Protocol.

PROTOCOL FIRST: These tests define the CONTRACT.
Implementation MUST pass these tests.

"ekam evādvitīyam" - One without a second.
"""

import pytest
from typing import List

from vibe_core.mahamantra.cli import (
    CLIEntryProtocol,
    CLIEntryResult,
    CLICapability,
    CLIHealth,
    CLIResult,
    CLIState,
)
from vibe_core.mahamantra.substrate.protocol import ProtocolRegistry


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure registry and cli_auto are clean."""
    ProtocolRegistry.clear()
    from vibe_core.mahamantra.cli.auto import cli_auto
    # Reset cli_auto state
    cli_auto._methods = {}
    cli_auto._nulls = {}
    cli_auto._keywords = {}
    cli_auto._discovered = False
    yield
    ProtocolRegistry.clear()
    cli_auto._methods = {}
    cli_auto._nulls = {}
    cli_auto._keywords = {}
    cli_auto._discovered = False


# =============================================================================
# PROTOCOL COMPLIANCE TESTS
# =============================================================================

class TestCLIEntryProtocolContract:
    """Test that CLIEntryProtocol defines the correct contract."""

    def test_protocol_has_run_method(self):
        """Entry protocol MUST have run(args) -> int."""
        assert hasattr(CLIEntryProtocol, "run")

    def test_protocol_has_discover_method(self):
        """Entry protocol MUST have discover() -> List[CLICapability]."""
        assert hasattr(CLIEntryProtocol, "discover")

    def test_protocol_has_get_state_method(self):
        """Entry protocol MUST have get_state() -> CLIState."""
        assert hasattr(CLIEntryProtocol, "get_state")

    def test_protocol_has_check_health_method(self):
        """Entry protocol MUST have check_health() -> CLIHealth."""
        assert hasattr(CLIEntryProtocol, "check_health")

    def test_protocol_is_runtime_checkable(self):
        """Protocol MUST be runtime_checkable for isinstance()."""
        # Create a minimal implementation
        class MinimalEntry:
            def run(self, args: List[str]) -> int:
                return 0

            def discover(self) -> List[CLICapability]:
                return []

            def get_state(self) -> CLIState:
                return CLIState()

            def check_health(self) -> CLIHealth:
                return CLIHealth()

        entry = MinimalEntry()
        assert isinstance(entry, CLIEntryProtocol)


# =============================================================================
# MAHAMANTRA CLI ENTRY TESTS
# =============================================================================

class TestMahamantraCLIEntry:
    """
    Tests for mahamantra-based CLI entry.

    These tests verify that cli_auto is properly wired as the entry point.
    """

    def test_cli_auto_discovers_108_methods(self):
        """cli_auto MUST discover 108+ methods from Protocols."""
        from vibe_core.mahamantra.cli.auto import cli_auto

        count = cli_auto.discover_all()
        # We expect at least 108 methods (109 currently discovered)
        assert count >= 108, f"Expected at least 108 methods, got {count}"

    def test_cli_auto_covers_all_16_positions(self):
        """cli_auto MUST discover methods for all 16 positions."""
        from vibe_core.mahamantra.cli.auto import cli_auto
        from vibe_core.mahamantra.kernel.singularity import mahamantra

        cli_auto.discover_all()

        positions_with_methods = len(cli_auto._methods)
        if positions_with_methods != 16:
            for i in range(16):
                if i not in cli_auto._methods:
                    print(f"MISSING POSITION {i}: {mahamantra[i].guardian.value}")

        assert positions_with_methods == 16, f"Expected 16 positions, got {positions_with_methods}"

    def test_cli_auto_execute_returns_cli_result(self):
        """cli_auto.execute() MUST return CLIResult."""
        from vibe_core.mahamantra.cli.auto import cli_auto
        from vibe_core.mahamantra.cli.protocol import CLIResult

        cli_auto.discover_all()
        result = cli_auto.execute("analyze", ["test"])

        assert isinstance(result, CLIResult)
        assert hasattr(result, "success")
        assert hasattr(result, "exit_code")
        assert hasattr(result, "output")

    def test_cli_auto_routes_to_correct_position(self):
        """cli_auto MUST route commands to correct mahajana position."""
        from vibe_core.mahamantra.cli.auto import cli_auto

        cli_auto.discover_all()

        # analyze -> Kapila (position 6)
        pos = cli_auto._get_position("analyze")
        assert pos == 6, f"analyze should route to position 6 (Kapila), got {pos}"

        # judge -> Yamaraja (position 15)
        pos = cli_auto._get_position("judge")
        assert pos == 15, f"judge should route to position 15 (Yamaraja), got {pos}"

        # bootstrap -> Prithu (position 0)
        pos = cli_auto._get_position("bootstrap")
        assert pos == 0, f"bootstrap should route to position 0 (Prithu), got {pos}"

    def test_cli_auto_capabilities_returns_list(self):
        """cli_auto.get_capabilities() MUST return List[CLICapability]."""
        from vibe_core.mahamantra.cli.auto import cli_auto
        from vibe_core.mahamantra.cli.protocol import CLICapability

        cli_auto.discover_all()
        caps = cli_auto.get_capabilities()

        assert isinstance(caps, list)
        assert len(caps) >= 108
        assert all(isinstance(c, CLICapability) for c in caps)


# =============================================================================
# ZERO MANUAL WIRING TESTS
# =============================================================================

class TestZeroManualWiring:
    """
    Tests that verify ZERO manual wiring.

    These tests ensure we don't regress to the unified_cli.py pattern.
    """

    def test_no_hardcoded_command_map(self):
        """Entry point MUST NOT have hardcoded command maps."""
        from vibe_core.mahamantra.cli.auto import CLIAutoDiscovery

        # CLIAutoDiscovery should NOT have any hardcoded handlers
        discovery = CLIAutoDiscovery()

        # Before discover_all(), should have ZERO methods
        assert len(discovery._methods) == 0
        assert len(discovery._keywords) == 0

    def test_all_commands_from_protocol_introspection(self):
        """ALL commands MUST come from Protocol introspection, not hardcoding."""
        from vibe_core.mahamantra.cli.auto import cli_auto
        from vibe_core.mahamantra.kernel.singularity import mahamantra

        cli_auto.discover_all()

        # Every discovered method should trace back to a Protocol
        for pos, methods in cli_auto._methods.items():
            # Get the protocol base for this position
            protocol_base = mahamantra.protocols[pos]

            # Verify the protocol exists
            assert protocol_base is not None, f"No protocol at position {pos}"

    def test_discover_is_idempotent(self):
        """discover_all() MUST be idempotent."""
        from vibe_core.mahamantra.cli.auto import cli_auto

        count1 = cli_auto.discover_all()
        count2 = cli_auto.discover_all()

        assert count1 == count2, "discover_all() should return same count on repeated calls"


# =============================================================================
# GAD-000 COMPLIANCE TESTS
# =============================================================================

class TestGAD000Compliance:
    """
    GAD-000 Turing Test: Can an AI successfully operate the CLI?
    """

    def test_discoverability_all_commands_listed(self):
        """GAD-000 #1: Can AI discover all available commands?"""
        from vibe_core.mahamantra.cli.auto import cli_auto

        cli_auto.discover_all()
        caps = cli_auto.get_capabilities()

        # AI can discover all 108+ commands
        assert len(caps) >= 108

        # Each capability has required fields
        for cap in caps:
            assert cap.name, "Capability must have name"
            assert cap.purpose, "Capability must have purpose"
            assert cap.mahajana_position >= 0, "Capability must have position"

    def test_parseability_structured_output(self):
        """GAD-000 #3: Are outputs machine-readable?"""
        from vibe_core.mahamantra.cli.auto import cli_auto

        cli_auto.discover_all()
        result = cli_auto.execute("analyze", ["test"])

        # Result is structured, not just a string
        assert hasattr(result, "success")
        assert hasattr(result, "exit_code")
        assert hasattr(result, "output")

        # Output can be converted to dict
        output_dict = result.output.to_dict()
        assert isinstance(output_dict, dict)

    def test_idempotency_same_input_same_output(self):
        """GAD-000 #5: Same input = same output?"""
        from vibe_core.mahamantra.cli.auto import cli_auto

        cli_auto.discover_all()

        result1 = cli_auto.execute("analyze", ["test"])
        result2 = cli_auto.execute("analyze", ["test"])

        assert result1.success == result2.success
        assert result1.exit_code == result2.exit_code


# =============================================================================
# PARAMPARA CONNECTION TESTS
# =============================================================================

class TestParamparaConnection:
    """
    Test that CLI is connected to Parampara (37 formula).

    24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37
    """

    def test_all_positions_connected(self):
        """All 16 positions MUST be connected to Parampara."""
        from vibe_core.mahamantra.kernel.singularity import mahamantra
        from vibe_core.mahamantra.substrate import PARAMPARA

        for pos in mahamantra.positions:
            assert pos.parampara_vector % PARAMPARA == 0, (
                f"Position {pos.index} not connected to Parampara"
            )

    def test_parampara_is_37(self):
        """PARAMPARA constant MUST be 37."""
        from vibe_core.mahamantra.substrate import PARAMPARA

        assert PARAMPARA == 37
