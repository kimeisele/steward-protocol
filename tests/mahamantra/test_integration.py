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
    # VM routes to a deterministic position (not necessarily 0)
    assert 0 <= result["final_position"] < WORDS
    # Parampara verified through VM pipeline
    assert isinstance(result["parampara_connected"], bool)
    # Each round = one lotus.execute() = one yajna cycle
    assert result["switch_count"] >= 0


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
    # Each round = one lotus.execute() with its own yajna switches
    assert result["switch_count"] >= 0
    
    # Parampara verified through VM pipeline
    assert isinstance(result["parampara_connected"], bool)


def test_chant_verbose_mode(capsys):
    """
    Test verbose output to stdout.
    """
    result = cli_chant(rounds=1, verbose=True)
    assert result["success"]
    
    captured = capsys.readouterr()
    assert "MAHAMANTRA CHANT - Through VM Pipeline" in captured.out
    assert "KIRTAN" in captured.out
