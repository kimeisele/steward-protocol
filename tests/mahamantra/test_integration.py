"""
MAHAMANTRA INTEGRATION TESTS
============================

"yathā taror mūla-niṣecanena"
"As pouring water on the root nourishes the entire tree..."
(SB 4.31.14)

Verifies the integration of:
- SankirtanChamber (Root)
- SiksastakamRegistry (Memory)
- CLI Commands (Branches/Fruits)
"""

import pytest
from vibe_core.mahamantra.commands import cli_chant
from vibe_core.mahamantra.substrate.seed import WORDS, PARAMPARA

def test_chant_integration_basic():
    """
    Test standard chant cycle (1 round).
    Verifies that the CLI command spins up the Chamber and produces valid output.
    """
    result = cli_chant(rounds=1, verbose=False)
    
    assert result["success"]
    assert result["rounds"] == 1
    assert result["ticks"] == WORDS  # 16
    assert result["final_position"] == 0 # 16 % 16 = 0
    # Parampara connected if cells exist (presence)
    assert result["parampara_connected"] is True
    # Initial run might not have resonance (depends on pattern)
    # But total transformations must be 16
    assert result["switch_count"] == 16


def test_chant_resonance_accumulation():
    """
    Test multiple rounds leading to resonance.
    
    4 rounds = 64 ticks.
    The Chamber uses a single Seed Cell, which transforms and jumps around.
    It leaves a trail in the Registry.
    Eventually, it should hit its own tail or filled slots.
    """
    ROUNDS = 4
    result = cli_chant(rounds=ROUNDS, verbose=False)
    
    assert result["success"]
    assert result["rounds"] == ROUNDS
    assert result["ticks"] == ROUNDS * WORDS
    assert result["switch_count"] == ROUNDS * WORDS
    
    # We expect the registry to be populated
    # parampara_connected indicates Active Cells > 0
    assert result["parampara_connected"] is True


def test_chant_verbose_mode(capsys):
    """
    Test verbose output to stdout.
    """
    result = cli_chant(rounds=1, verbose=True)
    assert result["success"]
    
    captured = capsys.readouterr()
    assert "MAHAMANTRA CHANT - Sankirtan Chamber Active" in captured.out
    assert "KIRTAN" in captured.out
    assert "res=" in captured.out
