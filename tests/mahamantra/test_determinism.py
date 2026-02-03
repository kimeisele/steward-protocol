"""
Test Mahamantra Determinism - NO PUSSY TESTS
==============================================

The system MUST be deterministic:
- Same input → Same seed → Same attractor → Same position → Same phoneme

This is a REGRESSION test. Values are EXACT, not "is not None" bullshit.
"""

import pytest

from vibe_core.mahamantra import mahamantra


def test_determinism_same_input_same_output():
    """
    Run the same input 10 times.
    Every single value must be IDENTICAL.
    """
    results = [mahamantra("test determinism") for _ in range(10)]

    # All must be identical
    first = results[0]
    for i, result in enumerate(results[1:], start=2):
        assert result["vibration"]["seed"] == first["vibration"]["seed"], f"Run {i} seed differs"
        assert result["vibration"]["attractor"] == first["vibration"]["attractor"], f"Run {i} attractor differs"
        assert result["position"] == first["position"], f"Run {i} position differs"
        assert result["vibration"]["phoneme"] == first["vibration"]["phoneme"], f"Run {i} phoneme differs"


def test_regression_test_determinism():
    """
    REGRESSION TEST: Exact values for known input.
    If this fails, the algorithm changed (breaking change!).
    """
    result = mahamantra("test determinism")

    # EXACT expected values (captured 2026-02-03)
    assert result["vibration"]["seed"] == 100786206
    assert result["vibration"]["attractor"] == 11
    assert result["position"] == 11
    assert result["vibration"]["phoneme"] == "ma"
    assert result["guardian"] == "bhishma"
    assert result["vibration"]["signature"]["frequency"] == 48


def test_different_inputs_different_outputs():
    """
    Different inputs MUST produce different results.
    """
    r1 = mahamantra("input one")
    r2 = mahamantra("input two")

    # At least ONE value must differ
    assert (
        r1["vibration"]["seed"] != r2["vibration"]["seed"]
        or r1["vibration"]["attractor"] != r2["vibration"]["attractor"]
        or r1["position"] != r2["position"]
    )


def test_full_flow_integrity():
    """
    COMPLETE END-TO-END TEST.
    Input → Compression → Algorithm → Cell → Chamber → Shabda → Output

    Every component must execute successfully.
    """
    result = mahamantra("analyze this codebase")

    # 1. Compression worked
    assert result["vibration"]["seed"] > 0
    assert result["vibration"]["attractor"] >= 0

    # 2. Position routing worked
    assert 0 <= result["position"] <= 15
    assert result["guardian"] in [
        "vyasa",
        "brahma",
        "narada",
        "shambhu",
        "prithu",
        "kumaras",
        "kapila",
        "manu",
        "parashurama",
        "prahlada",
        "janaka",
        "bhishma",
        "nrisimha",
        "bali",
        "shuka",
        "yamaraja",
    ]

    # 3. Gita resonance worked
    assert result["chapter"] >= 1
    assert result["chapter"] <= 18
    if result["verse"]:
        assert "id" in result["verse"]
        assert result["verse"]["guna"] in ["suddha", "rajas", "tamas"]

    # 4. Cell transformation worked
    assert result["cell"]["is_alive"] is True
    assert result["cell"]["prana"] > 0
    assert 0 <= result["cell"]["integrity"] <= 1
    assert result["cell"]["cycle"] >= 0

    # 5. Shabda extraction worked
    assert result["vibration"]["phoneme"] is not None
    assert len(result["vibration"]["phoneme"]) > 0
    assert 0 <= result["vibration"]["rama_index"] <= 48
    assert result["vibration"]["signature"]["frequency"] > 0

    # 6. Execution succeeded
    assert result["execution"]["success"] is True

    # 7. Akash state updated
    assert result["akash"]["total_beats"] > 0


def test_known_seeds():
    """
    Test specific seed values produce expected results.
    Ensures algorithm stability across versions.
    """
    test_cases = [
        ("hello", 252159080, 18),  # seed, expected_attractor
        ("world", 127534056, 15),
        ("test", 218349628, 28),
    ]

    for input_text, expected_seed, expected_attractor in test_cases:
        result = mahamantra(input_text)
        assert result["vibration"]["seed"] == expected_seed, f"Seed changed for '{input_text}'"
        assert result["vibration"]["attractor"] == expected_attractor, f"Attractor changed for '{input_text}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
