"""
Test for the refactored LotusCLI to ensure it uses the Mahamantra adapter.
"""

import io
import sys
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import pytest

# Ensure the project root is in the Python path
sys.path.insert(0, ".")

from vibe_core.cli.lotus_cli import LotusCLI
from vibe_core.mahamantra.adapters.cli import AdapterResult, CellFingerprint


def test_lotus_cli_print_result():
    """Test that _print_result correctly displays routing information."""
    cli_handler = LotusCLI()

    # Create a mock AdapterResult
    mock_result = Mock(spec=AdapterResult)
    mock_result.resonance = {
        "guardian": "yamaraja",
        "position": 15,
    }
    mock_result.cli_command = "audit"
    mock_result.candidates = ["audit", "analyze"]
    mock_result.executed = False

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        cli_handler._print_result(mock_result)
    output = f.getvalue()

    # Verify the output
    assert "[YAMARAJA] Routed to: audit" in output
    assert "Position: 15" in output
    assert "Candidates: audit, analyze" in output


def test_lotus_cli_print_explain():
    """Test that _print_explain correctly calls _render_response."""
    cli_handler = LotusCLI()

    # Create a mock AdapterResult with fingerprint
    mock_fp = Mock(spec=CellFingerprint)
    mock_fp.position = 15
    mock_fp.payload_size = 18
    mock_fp.prana = 100
    mock_fp.cycle = 1
    mock_fp.seed = 12345

    mock_result = Mock(spec=AdapterResult)
    mock_result.resonance = {
        "input": "audit the system",
        "vibration": {"seed": "0x1234", "attractor": "audit"},
        "chapter": "3",
        "position": 15,
        "guardian": "yamaraja",
        "quarter": "dharma",
        "verse": {"guna": "sattva"},
        "parampara": {"verified": True},
        "cell": {"valid": True},
        "holy_name": "Yamaraja",
        "trinity_function": "audit",
    }
    mock_result.cli_command = "audit"
    mock_result.matched_position = 15
    mock_result.executed = False
    mock_result.candidates = ["audit"]
    mock_result.fingerprint = mock_fp

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        cli_handler._print_explain(mock_result)
    output = f.getvalue()

    # Verify the canonical output from _render_response
    assert "MAHAMANTRA - Krishna Routes Everything" in output
    assert "ROUTING" in output
    assert "Position:" in output and "Guardian:" in output
