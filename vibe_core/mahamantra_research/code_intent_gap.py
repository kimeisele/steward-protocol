"""
CODE INTENT GAP ANALYSIS
=========================

FRAGE: Was versteht die MahaCompression von Code?
       Was fehlt damit der Intent von Code klar wird?

EXPERIMENT:
1. Gleichen Code mit/ohne Any durch Compression schicken
2. Gleichen Code mit/ohne silent except durch Compression schicken
3. Schauen ob Seed, Intent-Level, Position sich unterscheiden
4. Schauen was Shabda (Phonetik) aus Code-Tokens macht

ERGEBNIS: Identifiziert die GAPs in der Seed-Pipeline für Code-Awareness.
"""

from vibe_core.mahamantra.adapters.compression import (
    MahaCompression,
    IntentGuna,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    text_to_vibration,
    VibrationSignature,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth


def compare_seeds(label_a: str, code_a: str, label_b: str, code_b: str) -> dict:
    """Compare two code snippets through the full compression pipeline."""
    comp = MahaCompression()

    result_a = comp.compress(code_a)
    result_b = comp.compress(code_b)

    vib_a = text_to_vibration(code_a)
    vib_b = text_to_vibration(code_b)

    vib_sum_a = sum(s.signature_id for s in vib_a) if vib_a else 0
    vib_sum_b = sum(s.signature_id for s in vib_b) if vib_b else 0

    return {
        "label_a": label_a,
        "label_b": label_b,
        "seed_a": result_a.seed,
        "seed_b": result_b.seed,
        "seeds_differ": result_a.seed != result_b.seed,
        "intent_a": result_a.intent_level.guna.value,
        "intent_b": result_b.intent_level.guna.value,
        "intents_differ": result_a.intent_level.guna != result_b.intent_level.guna,
        "position_a": result_a.position,
        "position_b": result_b.position,
        "positions_differ": result_a.position != result_b.position,
        "vibration_sum_a": vib_sum_a,
        "vibration_sum_b": vib_sum_b,
        "vibration_delta": abs(vib_sum_a - vib_sum_b),
        "phoneme_count_a": len(vib_a),
        "phoneme_count_b": len(vib_b),
    }


def print_comparison(result: dict) -> None:
    """Pretty-print a comparison result."""
    print(f"\n{'=' * 60}")
    print(f"  {result['label_a']}  vs  {result['label_b']}")
    print(f"{'=' * 60}")
    print(
        f"  Seed:      {result['seed_a']:>12}  |  {result['seed_b']:>12}  {'DIFFER' if result['seeds_differ'] else 'SAME'}"
    )
    print(
        f"  Intent:    {result['intent_a']:>12}  |  {result['intent_b']:>12}  {'DIFFER' if result['intents_differ'] else 'SAME'}"
    )
    print(
        f"  Position:  {result['position_a']:>12}  |  {result['position_b']:>12}  {'DIFFER' if result['positions_differ'] else 'SAME'}"
    )
    print(
        f"  Vibration: {result['vibration_sum_a']:>12}  |  {result['vibration_sum_b']:>12}  delta={result['vibration_delta']}"
    )
    print(f"  Phonemes:  {result['phoneme_count_a']:>12}  |  {result['phoneme_count_b']:>12}")


# =============================================================================
# EXPERIMENT 1: Any vs typed
# =============================================================================

CODE_WITH_ANY = """
from typing import Any, Dict

def process(data: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["value"] = data
    return result
"""

CODE_TYPED = """
from typing import Dict

def process(data: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    result["value"] = data
    return result
"""

# =============================================================================
# EXPERIMENT 2: Silent except vs proper handling
# =============================================================================

CODE_SILENT_EXCEPT = """
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.loads(f.read())
    except Exception:
        pass
    return {}
"""

CODE_PROPER_EXCEPT = """
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.loads(f.read())
    except FileNotFoundError as exc:
        logger.warning("Config not found: %s", exc)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", path, exc)
    return {}
"""

# =============================================================================
# EXPERIMENT 3: Broken import vs clean import
# =============================================================================

CODE_BROKEN_IMPORT = """
import os, sys, json
from pathlib import *
from typing import Any
x = Any
"""

CODE_CLEAN_IMPORT = """
import json
from pathlib import Path
from typing import Optional
config_path: Optional[Path] = None
"""

# =============================================================================
# EXPERIMENT 4: Intent keywords IN code
# =============================================================================

CODE_WITH_ERROR_WORDS = """
def handle_error(error_msg: str) -> None:
    if "fatal" in error_msg or "crash" in error_msg:
        raise RuntimeError(f"Fatal crash: {error_msg}")
"""

CODE_WITH_SUCCESS_WORDS = """
def handle_success(result: str) -> None:
    if "complete" in result and "verified" in result:
        logger.info(f"Success: {result}")
"""

# =============================================================================
# EXPERIMENT 5: Phonetic signature of code tokens
# =============================================================================


def analyze_code_phonetics():
    """What does Shabda hear when it listens to code tokens?"""
    tokens = [
        "Any",
        "str",
        "int",
        "Dict",
        "List",
        "Optional",
        "def",
        "class",
        "import",
        "return",
        "raise",
        "except",
        "pass",
        "try",
        "finally",
        "Exception",
        "TypeError",
        "ValueError",
        "self",
        "None",
        "True",
        "False",
    ]

    print(f"\n{'=' * 60}")
    print("  SHABDA PHONETIC ANALYSIS OF CODE TOKENS")
    print(f"{'=' * 60}")

    for token in tokens:
        vibs = text_to_vibration(token)
        vib_sum = sum(s.signature_id for s in vibs) if vibs else 0
        phoneme_count = len(vibs)

        # What articulation points does this token use?
        articulations = set()
        for v in vibs:
            articulations.add(v.articulation.name)

        print(
            f"  {token:>15}  vib_sum={vib_sum:>6}  phonemes={phoneme_count:>2}  articulation={','.join(sorted(articulations))}"
        )


# =============================================================================
# EXPERIMENT 6: Can compression distinguish code quality?
# =============================================================================


def code_quality_spectrum():
    """Run a spectrum of code quality through compression."""
    comp = MahaCompression()
    synth = MahaModularSynth(default_preset="quantum")

    samples = [
        ("garbage", "x = 1\ny = 2\nz = x + y"),
        ("any_soup", "def f(x: Any, y: Any) -> Any: return Any"),
        ("silent_fail", "try:\n    x()\nexcept:\n    pass"),
        ("typed_clean", "def add(x: int, y: int) -> int:\n    return x + y"),
        ("documented", 'def add(x: int, y: int) -> int:\n    """Add two integers."""\n    return x + y'),
        (
            "robust",
            "def add(x: int, y: int) -> int:\n    if not isinstance(x, int):\n        raise TypeError(f'Expected int, got {type(x)}')\n    return x + y",
        ),
        ("text_prose", "The system is healthy and all tests pass successfully."),
        ("text_error", "FATAL: Connection timeout. Database crash. Memory leak detected."),
    ]

    print(f"\n{'=' * 60}")
    print("  CODE QUALITY SPECTRUM THROUGH COMPRESSION")
    print(f"{'=' * 60}")
    print(f"  {'Label':>15}  {'Seed':>12}  {'Attractor':>10}  {'Pos':>4}  {'Intent':>8}")
    print(f"  {'-' * 15}  {'-' * 12}  {'-' * 10}  {'-' * 4}  {'-' * 8}")

    for label, code in samples:
        result = comp.compress(code)
        attractor = synth.transform(result.seed)
        print(
            f"  {label:>15}  {result.seed:>12}  {attractor:>10}  {result.position:>4}  {result.intent_level.guna.value:>8}"
        )


# =============================================================================
# RUN ALL
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CODE INTENT GAP ANALYSIS")
    print("  What does MahaCompression understand about code?")
    print("=" * 60)

    # Experiment 1-4: Pairwise comparisons
    comparisons = [
        ("Any-typed", CODE_WITH_ANY, "Properly-typed", CODE_TYPED),
        ("Silent-except", CODE_SILENT_EXCEPT, "Proper-except", CODE_PROPER_EXCEPT),
        ("Broken-import", CODE_BROKEN_IMPORT, "Clean-import", CODE_CLEAN_IMPORT),
        ("Error-words", CODE_WITH_ERROR_WORDS, "Success-words", CODE_WITH_SUCCESS_WORDS),
    ]

    gap_count = 0
    for label_a, code_a, label_b, code_b in comparisons:
        result = compare_seeds(label_a, code_a, label_b, code_b)
        print_comparison(result)

        if not result["intents_differ"]:
            gap_count += 1
            print(f"  >>> GAP: Compression cannot distinguish {label_a} from {label_b} by intent!")

    # Experiment 5: Phonetic analysis
    analyze_code_phonetics()

    # Experiment 6: Quality spectrum
    code_quality_spectrum()

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Intent-blind comparisons: {gap_count}/{len(comparisons)}")
    print(f"  (Higher = more gaps in code-awareness)")
    print()
    if gap_count > 0:
        print("  CONCLUSION: The compression pipeline treats code as prose.")
        print("  It cannot distinguish good code from bad code by INTENT.")
        print("  The keyword-based classifier only catches words like 'error'/'success',")
        print("  not structural code quality (Any, silent except, broken imports).")
        print()
        print("  NEXT: Add code-structural intent signals to the seed pipeline.")
    else:
        print("  CONCLUSION: Compression already distinguishes code quality!")
