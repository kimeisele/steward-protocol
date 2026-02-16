"""
SPELL INTENT — Words as Programs, Intent as Attractor
=======================================================

DISCOVERY CHAIN:
    1. Keywords = Web 2.0 (hardcoded lists) → must go
    2. SHA256 dominates Shabda in the seed → position is pseudo-random
    3. Pure Shabda separation ratio = 1.03 (too weak alone)
    4. BUT: spell_cycle() already exists — each phoneme IS a modulation step
    5. spell_cycle treats text as a PROGRAM: VARGA→op, ELEMENT→ADSR, SUB→pos, HARMONIC→feedback

THE EXPERIMENT:
    Instead of: text → SHA256 + vib_sum → Synth → seed
    Do:         text → phoneme coords → spell_cycle → attractor

    This means: the TEXT ITSELF is the program.
    The attractor it converges to IS its intent.
    No keywords. No hashing. Pure computation from vibration.

    If "def add(x: int)" and "def f(x: Any)" produce different attractors,
    then the Mahamantra can distinguish code quality through COMPUTATION,
    not classification.

THIS IS WHAT THE USER MEANS:
    "Das Mantra BERECHNET den Intent"
    "Keine hardcoded Keywords"
    "Reverse Engineering — wie gibt das Mantra vor"
"""

from typing import Dict, List, Tuple

from vibe_core.mahamantra.adapters.synth import MahaSynth
from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
from vibe_core.mahamantra.substrate.varnamala_codec import encode as iast_encode
from vibe_core.mahamantra.substrate.basin_map import (
    COORD_BASIN,
    COORD_HKR,
    BASIN_LIST,
    BASIN_INDEX,
    BASIN_COUNT,
)
from vibe_core.mahamantra.protocols._seed import WORDS, MAHA_QUANTUM


# =============================================================================
# TEXT → RAMA COORDS (the bridge from Latin text to Mahamantra space)
# =============================================================================

def text_to_rama_coords(text: str) -> Tuple[int, ...]:
    """
    Convert arbitrary text to RAMA coordinates (0-48).

    Each character's Shabda signature_id maps to a RAMA coord.
    This is the same mapping used in the 7D resonance ranker.
    """
    vibrations = text_to_vibration(text)
    if not vibrations:
        return (0,)
    return tuple(s.signature_id % 49 for s in vibrations)


# =============================================================================
# SPELL-BASED INTENT — text as program through the synth
# =============================================================================

def spell_intent(text: str, seed: int = 0) -> dict:
    """
    Compute intent by running text through spell_cycle.

    The text becomes a PROGRAM:
    - Each phoneme = one modulation step
    - VARGA determines operation (H/K/R)
    - ELEMENT determines ADSR envelope
    - The final attractor IS the intent

    No keywords. No hashing. Pure phonetic computation.
    """
    synth = MahaSynth(preset="quantum")
    coords = text_to_rama_coords(text)

    # Run the text as a spell through the synth
    result = synth.spell_cycle(coords, seed=seed)

    # The final value IS the computed intent
    final = result.final_value
    position = final % WORDS
    quarter = position // (WORDS // 4)

    # Basin: where does this converge?
    from vibe_core.mahamantra.substrate.algorithm.maha import MahaAlgorithm16
    algo = MahaAlgorithm16()
    basin_val = final % MAHA_QUANTUM
    for _ in range(100):
        prev = basin_val
        basin_val = algo.transform(basin_val)
        if basin_val == prev:
            break

    # HKR color of the coordinate sequence
    h, k, r = 0.0, 0.0, 0.0
    for c in coords:
        ch, ck, cr = COORD_HKR[c]
        h += ch; k += ck; r += cr
    n = len(coords)
    hkr = (h / n, k / n, r / n)

    # Operation distribution from the spell
    op_counts = {"H": 0, "K": 0, "R": 0}
    for step in result.steps:
        op_counts[step.name] += 1
    total_ops = sum(op_counts.values())
    op_dist = {k: v / total_ops for k, v in op_counts.items()} if total_ops > 0 else {"H": 0.33, "K": 0.33, "R": 0.34}

    return {
        "final_value": final,
        "position": position,
        "quarter": quarter,
        "quarter_name": ["KSETRAJNA", "KRISHNA", "PRAKRITI", "KARMA"][quarter],
        "basin": basin_val,
        "hkr": tuple(round(x, 3) for x in hkr),
        "op_dist": op_dist,
        "coord_count": len(coords),
        "steps": len(result.steps),
    }


# =============================================================================
# CORPUS
# =============================================================================

CORPUS = [
    # CLEAN CODE
    ("clean", "def add(x: int, y: int) -> int:\n    return x + y"),
    ("clean", "def greet(name: str) -> str:\n    return f'Hello, {name}'"),
    ("clean", "class Config:\n    def __init__(self, path: Path) -> None:\n        self.path = path"),
    ("clean", "from typing import Dict\ndef load(path: str) -> Dict[str, str]:\n    return json.loads(Path(path).read_text())"),
    ("clean", "def validate(data: dict) -> bool:\n    return 'name' in data and 'id' in data"),
    ("clean", "import logging\nlogger = logging.getLogger(__name__)"),

    # BROKEN CODE
    ("broken", "from typing import Any\ndef f(x: Any) -> Any:\n    return x"),
    ("broken", "def load(p):\n    try:\n        return open(p).read()\n    except:\n        pass"),
    ("broken", "from typing import *\ndef g(a, b, c):\n    return a"),
    ("broken", "def h(x: Any, y: Any, z: Any) -> Any:\n    try:\n        return x + y + z\n    except Exception:\n        pass"),
    ("broken", "import os, sys, json, re, pathlib\nfrom typing import Any\nx: Any = None"),
    ("broken", "class Bad:\n    def do(self, thing):\n        try: return eval(thing)\n        except: return None"),

    # HEALTHY TEXT
    ("healthy", "All services healthy. Deployment complete."),
    ("healthy", "Tests passed. Coverage at 95 percent. No regressions."),
    ("healthy", "System stable for 30 days. Zero incidents."),
    ("healthy", "Performance optimized. Latency reduced by 40 percent."),

    # FAILING TEXT
    ("failing", "Connection refused. Retry failed after 5 attempts."),
    ("failing", "Out of memory. Process killed."),
    ("failing", "Database corruption detected. Backup failed."),
    ("failing", "Security breach. Unauthorized access detected."),
]


# =============================================================================
# ANALYSIS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("  SPELL INTENT — Text as Program, Attractor as Intent")
    print("  Each phoneme = one modulation step through the Synth")
    print("=" * 100)

    results_by_type: Dict[str, List[dict]] = {}

    print(f"\n  {'#':>2}  {'Type':>8}  {'Final':>6}  {'Pos':>3}  {'Q':>8}  {'Basin':>5}  "
          f"{'H%':>5}  {'K%':>5}  {'R%':>5}  {'OpH':>4}  {'OpK':>4}  {'OpR':>4}  Text")
    print(f"  {'-'*2}  {'-'*8}  {'-'*6}  {'-'*3}  {'-'*8}  {'-'*5}  "
          f"{'-'*5}  {'-'*5}  {'-'*5}  {'-'*4}  {'-'*4}  {'-'*4}  {'-'*30}")

    for i, (label, text) in enumerate(CORPUS):
        r = spell_intent(text)
        results_by_type.setdefault(label, []).append(r)

        text_short = text.replace("\n", " ")[:30]
        print(f"  {i+1:>2}  {label:>8}  {r['final_value']:>6}  {r['position']:>3}  {r['quarter_name']:>8}  {r['basin']:>5}  "
              f"{r['hkr'][0]:>5.2f}  {r['hkr'][1]:>5.2f}  {r['hkr'][2]:>5.2f}  "
              f"{r['op_dist']['H']:>4.2f}  {r['op_dist']['K']:>4.2f}  {r['op_dist']['R']:>4.2f}  {text_short}")

    # === CLUSTER ANALYSIS ===
    print(f"\n{'='*100}")
    print("  CLUSTER ANALYSIS — spell_cycle attractors by type")
    print(f"{'='*100}")

    for label in ["clean", "broken", "healthy", "failing"]:
        rs = results_by_type.get(label, [])
        if not rs:
            continue

        finals = [r["final_value"] for r in rs]
        positions = [r["position"] for r in rs]
        basins = [r["basin"] for r in rs]
        quarters = [r["quarter"] for r in rs]

        avg_final = sum(finals) / len(finals)
        avg_pos = sum(positions) / len(positions)
        avg_basin = sum(basins) / len(basins)

        q_dist = [quarters.count(q) for q in range(4)]

        avg_h = sum(r["op_dist"]["H"] for r in rs) / len(rs)
        avg_k = sum(r["op_dist"]["K"] for r in rs) / len(rs)
        avg_r = sum(r["op_dist"]["R"] for r in rs) / len(rs)

        print(f"\n  [{label:>8}] n={len(rs)}")
        print(f"    Final values: {finals}")
        print(f"    Positions:    {positions}  avg={avg_pos:.1f}")
        print(f"    Basins:       {sorted(set(basins))}  avg={avg_basin:.1f}")
        print(f"    Quarters:     Q1={q_dist[0]} Q2={q_dist[1]} Q3={q_dist[2]} Q4={q_dist[3]}")
        print(f"    Op dist:      H={avg_h:.3f}  K={avg_k:.3f}  R={avg_r:.3f}")

    # === GOOD vs BAD separation ===
    print(f"\n{'='*100}")
    print("  GOOD vs BAD — Does spell_cycle separate?")
    print(f"{'='*100}")

    good = results_by_type.get("clean", []) + results_by_type.get("healthy", [])
    bad = results_by_type.get("broken", []) + results_by_type.get("failing", [])

    good_finals = [r["final_value"] for r in good]
    bad_finals = [r["final_value"] for r in bad]
    good_positions = [r["position"] for r in good]
    bad_positions = [r["position"] for r in bad]
    good_basins = set(r["basin"] for r in good)
    bad_basins = set(r["basin"] for r in bad)

    print(f"\n  Good finals:    avg={sum(good_finals)/len(good_finals):.1f}  range=[{min(good_finals)}, {max(good_finals)}]")
    print(f"  Bad finals:     avg={sum(bad_finals)/len(bad_finals):.1f}  range=[{min(bad_finals)}, {max(bad_finals)}]")
    print(f"  Good positions: avg={sum(good_positions)/len(good_positions):.1f}  {good_positions}")
    print(f"  Bad positions:  avg={sum(bad_positions)/len(bad_positions):.1f}  {bad_positions}")
    print(f"  Good basins:    {sorted(good_basins)}")
    print(f"  Bad basins:     {sorted(bad_basins)}")
    print(f"  Basin overlap:  {good_basins & bad_basins}")

    # Op distribution comparison
    good_h = sum(r["op_dist"]["H"] for r in good) / len(good)
    good_k = sum(r["op_dist"]["K"] for r in good) / len(good)
    good_r = sum(r["op_dist"]["R"] for r in good) / len(good)
    bad_h = sum(r["op_dist"]["H"] for r in bad) / len(bad)
    bad_k = sum(r["op_dist"]["K"] for r in bad) / len(bad)
    bad_r = sum(r["op_dist"]["R"] for r in bad) / len(bad)

    print(f"\n  Good op dist:   H={good_h:.4f}  K={good_k:.4f}  R={good_r:.4f}")
    print(f"  Bad op dist:    H={bad_h:.4f}  K={bad_k:.4f}  R={bad_r:.4f}")
    print(f"  Delta:          H={good_h-bad_h:+.4f}  K={good_k-bad_k:+.4f}  R={good_r-bad_r:+.4f}")

    op_dist_distance = ((good_h-bad_h)**2 + (good_k-bad_k)**2 + (good_r-bad_r)**2) ** 0.5
    print(f"  Op dist distance: {op_dist_distance:.4f}")

    # === FINAL VERDICT ===
    print(f"\n{'='*100}")
    print("  VERDICT")
    print(f"{'='*100}")

    # Check if finals separate
    good_mean = sum(good_finals) / len(good_finals)
    bad_mean = sum(bad_finals) / len(bad_finals)
    good_var = sum((f - good_mean)**2 for f in good_finals) / len(good_finals)
    bad_var = sum((f - bad_mean)**2 for f in bad_finals) / len(bad_finals)
    pooled_std = ((good_var + bad_var) / 2) ** 0.5

    if pooled_std > 0:
        cohens_d = abs(good_mean - bad_mean) / pooled_std
    else:
        cohens_d = 0

    print(f"\n  Cohen's d (final values): {cohens_d:.3f}")
    print(f"  (0.2=small, 0.5=medium, 0.8=large effect)")

    if cohens_d >= 0.5:
        print(f"\n  >>> SPELL_CYCLE SEPARATES: d={cohens_d:.2f}")
        print("  >>> Text-as-program produces different attractors for good vs bad.")
        print("  >>> The Mahamantra CAN compute intent without keywords.")
    elif cohens_d >= 0.2:
        print(f"\n  >>> WEAK SEPARATION: d={cohens_d:.2f}")
        print("  >>> spell_cycle provides a signal but needs amplification.")
    else:
        print(f"\n  >>> NO SEPARATION: d={cohens_d:.2f}")
        print("  >>> spell_cycle alone doesn't separate good from bad.")

    print()
    print("  KEY INSIGHT:")
    print("  The spell_cycle treats each phoneme as a modulation instruction.")
    print("  The SEQUENCE matters — not just the sum.")
    print("  'def' followed by 'int' produces a different attractor than")
    print("  'def' followed by 'Any' — because the modulation path differs.")
    print("  This is computation, not classification.")
