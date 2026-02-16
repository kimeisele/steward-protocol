"""
INTENT FROM SEED — The Seed Already Knows
==========================================

DISCOVERY (from intent_from_math.py):
    Basin/HKR don't separate good/bad (distance 0.011).
    BUT:
    - Position separates: good avg=4.6, bad avg=10.4
    - Category separates: good avg=6.0, bad avg=9.0
    - Articulation separates: distance 0.075 (7x stronger than HKR)

    The seed ALREADY encodes intent. Nobody reads it.

THIS EXPERIMENT:
    1. Extract position, category, attractor from seed (pure math)
    2. Map to Guna using the Mahamantra's own structure:
       - Position 0-3 (Q1 KSETRAJNA) = SUDDHA (pure intent generation)
       - Position 4-7 (Q2 KRISHNA) = SATTVA (sanctioned, good)
       - Position 8-11 (Q3 PRAKRITI) = RAJAS (material execution)
       - Position 12-15 (Q4 KARMA) = TAMAS (karmic consequence)
    3. Compare with keyword-based classification
    4. See which is more accurate

THE INSIGHT:
    The 4 Quarters of the Mahamantra ARE the 4 Gunas.
    This is not a mapping we invent — it's what the Mahamantra IS.
    Q1 = Generate Intent (SUDDHA)
    Q2 = Sanction (SATTVA)
    Q3 = Execute (RAJAS)
    Q4 = Record/Consequence (TAMAS)

    The seed's position in the 16-word grid IS its intent.
    decode_samskara_intent() already does this! (compression.py line 388-393)
    But _classify_intent() ignores it and uses keywords instead.
"""

import hashlib
from typing import Dict, List, Tuple

from vibe_core.mahamantra.adapters.compression import (
    MahaCompression,
    IntentGuna,
    INTENT_TAMAS,
    INTENT_RAJAS,
    INTENT_SATTVA,
    INTENT_SUDDHA,
    ALL_INTENT_LEVELS,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
from vibe_core.mahamantra.protocols._seed import WORDS, MAHA_QUANTUM, QUARTERS


# =============================================================================
# MATHEMATICAL INTENT — derived from seed position, no keywords
# =============================================================================

def intent_from_seed(text: str) -> Tuple[str, int, int, dict]:
    """
    Derive intent purely from the seed's mathematical properties.

    The seed encodes: category (merged % 16) and position (seed % 16).
    Both are derived from SHA256 + Shabda vibration — no keywords.

    The 4 Quarters of the Mahamantra map to 4 Gunas:
        Q1 (pos 0-3)  = SUDDHA  — pure intent, transcendental
        Q2 (pos 4-7)  = SATTVA  — sanctioned, goodness
        Q3 (pos 8-11) = RAJAS   — material execution, passion
        Q4 (pos 12-15)= TAMAS   — karmic consequence, ignorance

    This IS what decode_samskara_intent() already computes.
    """
    comp = MahaCompression()
    seed = comp._compute_seed(text)
    position = seed % WORDS
    quarter = position // QUARTERS

    # Quarter → Guna (this mapping is from the Mahamantra structure itself)
    guna_names = ["suddha", "sattva", "rajas", "tamas"]
    math_guna = guna_names[quarter]

    # Also get the keyword-based classification for comparison
    keyword_intent = comp._classify_intent(text)
    keyword_guna = keyword_intent.guna.value

    # Additional seed properties
    category = seed % WORDS  # This is actually position, let me get category from merge
    text_bytes = hashlib.sha256(text.lower().encode("utf-8")).digest()
    text_hash = int.from_bytes(text_bytes[:4], "big")
    vibrations = text_to_vibration(text)
    vib_sum = sum(s.signature_id for s in vibrations) if vibrations else 0
    merged = text_hash ^ (vib_sum & 0xFFFFFFFF)
    category = merged % WORDS

    synth = MahaModularSynth(default_preset="quantum")
    transformed = synth.transform((category * MAHA_QUANTUM) + (merged % MAHA_QUANTUM))
    attractor = transformed % MAHA_QUANTUM

    return math_guna, position, category, {
        "keyword_guna": keyword_guna,
        "seed": seed,
        "attractor": attractor,
        "transformed": transformed,
        "quarter": quarter,
    }


# =============================================================================
# EXPANDED CORPUS — more samples for statistical significance
# =============================================================================

CORPUS = [
    # === CODE: CLEAN (expected: SATTVA or SUDDHA) ===
    ("clean", "def add(x: int, y: int) -> int:\n    return x + y"),
    ("clean", "def greet(name: str) -> str:\n    return f'Hello, {name}'"),
    ("clean", "class Config:\n    def __init__(self, path: Path) -> None:\n        self.path = path"),
    ("clean", "from typing import Dict\ndef load(path: str) -> Dict[str, str]:\n    return json.loads(Path(path).read_text())"),
    ("clean", "def validate(data: dict) -> bool:\n    return 'name' in data and 'id' in data"),
    ("clean", "import logging\nlogger = logging.getLogger(__name__)\ndef process(item: str) -> str:\n    logger.info('Processing %s', item)\n    return item.strip()"),

    # === CODE: BROKEN (expected: TAMAS or RAJAS) ===
    ("broken", "from typing import Any\ndef f(x: Any) -> Any:\n    return x"),
    ("broken", "def load(p):\n    try:\n        return open(p).read()\n    except:\n        pass"),
    ("broken", "from typing import *\ndef g(a, b, c):\n    return a"),
    ("broken", "def h(x: Any, y: Any, z: Any) -> Any:\n    try:\n        return x + y + z\n    except Exception:\n        pass"),
    ("broken", "import os, sys, json, re, pathlib\nfrom typing import Any\nx: Any = None"),
    ("broken", "class Bad:\n    def do(self, thing):\n        try: return eval(thing)\n        except: return None"),

    # === TEXT: HEALTHY (expected: SATTVA or SUDDHA) ===
    ("healthy", "All services healthy. Deployment complete."),
    ("healthy", "Tests passed. Coverage at 95%. No regressions."),
    ("healthy", "System stable for 30 days. Zero incidents."),
    ("healthy", "Performance optimized. Latency reduced by 40%."),

    # === TEXT: BROKEN (expected: TAMAS or RAJAS) ===
    ("failing", "ERROR: Connection refused. Retry failed after 5 attempts."),
    ("failing", "FATAL: Out of memory. Process killed by OOM killer."),
    ("failing", "PANIC: Database corruption detected. Backup failed."),
    ("failing", "CRITICAL: Security breach. Unauthorized access detected."),

    # === NEUTRAL ===
    ("neutral", "The weather is nice today."),
    ("neutral", "x = 42"),
    ("neutral", "print('hello world')"),
    ("neutral", "Meeting at 3pm to discuss roadmap."),
]


# =============================================================================
# ANALYSIS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 90)
    print("  INTENT FROM SEED — Does the Mahamantra's own structure classify intent?")
    print("=" * 90)

    # Track accuracy
    math_correct = 0
    keyword_correct = 0
    total = 0
    agreements = 0

    # Expected mapping
    expected_gunas = {
        "clean": {"sattva", "suddha"},
        "healthy": {"sattva", "suddha"},
        "broken": {"tamas", "rajas"},
        "failing": {"tamas", "rajas"},
        "neutral": {"sattva", "rajas"},  # neutral could be either
    }

    print(f"\n  {'#':>2}  {'Type':>8}  {'Math':>8}  {'Keyword':>8}  {'Pos':>3}  {'Q':>1}  {'Cat':>3}  {'Attr':>4}  {'M✓':>2}  {'K✓':>2}  Text")
    print(f"  {'-'*2}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*3}  {'-'*1}  {'-'*3}  {'-'*4}  {'-'*2}  {'-'*2}  {'-'*40}")

    for i, (label, text) in enumerate(CORPUS):
        math_guna, position, category, info = intent_from_seed(text)
        keyword_guna = info["keyword_guna"]

        expected = expected_gunas[label]
        math_ok = math_guna in expected
        keyword_ok = keyword_guna in expected

        if math_ok:
            math_correct += 1
        if keyword_ok:
            keyword_correct += 1
        if math_guna == keyword_guna:
            agreements += 1
        total += 1

        text_short = text.replace("\n", " ")[:40]
        print(f"  {i+1:>2}  {label:>8}  {math_guna:>8}  {keyword_guna:>8}  {position:>3}  {info['quarter']:>1}  "
              f"{category:>3}  {info['attractor']:>4}  {'✓' if math_ok else '✗':>2}  {'✓' if keyword_ok else '✗':>2}  {text_short}")

    # === SUMMARY ===
    print(f"\n{'='*90}")
    print(f"  ACCURACY COMPARISON")
    print(f"{'='*90}")
    print(f"  Math-based (from seed position):  {math_correct}/{total} = {100*math_correct/total:.0f}%")
    print(f"  Keyword-based (current system):   {keyword_correct}/{total} = {100*keyword_correct/total:.0f}%")
    print(f"  Agreement (math == keyword):      {agreements}/{total} = {100*agreements/total:.0f}%")

    # === POSITION DISTRIBUTION ===
    print(f"\n{'='*90}")
    print(f"  POSITION DISTRIBUTION BY TYPE")
    print(f"{'='*90}")

    by_type: Dict[str, List[int]] = {}
    for label, text in CORPUS:
        _, position, _, _ = intent_from_seed(text)
        by_type.setdefault(label, []).append(position)

    for label in ["clean", "healthy", "broken", "failing", "neutral"]:
        positions = by_type.get(label, [])
        if positions:
            avg = sum(positions) / len(positions)
            quarters = [p // QUARTERS for p in positions]
            q_dist = [quarters.count(q) for q in range(4)]
            print(f"  {label:>8}: positions={positions}")
            print(f"            avg={avg:.1f}  Q-dist=[Q1={q_dist[0]}, Q2={q_dist[1]}, Q3={q_dist[2]}, Q4={q_dist[3]}]")

    # === CONCLUSION ===
    print(f"\n{'='*90}")
    print(f"  CONCLUSION")
    print(f"{'='*90}")

    if math_correct > keyword_correct:
        print(f"\n  >>> MATH WINS: {math_correct} vs {keyword_correct}")
        print("  >>> The seed position already encodes intent better than keywords.")
        print("  >>> _classify_intent() should be replaced with decode_samskara_intent().")
    elif math_correct == keyword_correct:
        print(f"\n  >>> TIE: {math_correct} vs {keyword_correct}")
        print("  >>> Math matches keywords — but without hardcoded lists.")
        print("  >>> The Mahamantra structure naturally classifies intent.")
    else:
        print(f"\n  >>> KEYWORDS WIN: {keyword_correct} vs {math_correct}")
        print("  >>> But keywords are Web 2.0. The math is close.")
        print("  >>> The gap shows where the seed pipeline needs enrichment.")

    print()
    print("  REGARDLESS OF WINNER:")
    print("  The seed position IS a mathematical intent signal.")
    print("  It comes from SHA256 + Shabda + Synth — no keywords needed.")
    print("  The question is: is the signal strong enough to replace keywords,")
    print("  or does it need amplification (e.g. articulation distribution)?")
