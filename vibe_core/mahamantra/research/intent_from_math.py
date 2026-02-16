"""
INTENT FROM MATH — Can the Attractor Replace Keywords?
========================================================

CORE QUESTION:
    _classify_intent() uses hardcoded keyword lists (Web 2.0).
    But the seed pipeline already computes:
        - SHA256 hash (content identity)
        - Shabda vibration sum (phonetic identity)
        - MahaModularSynth attractor (convergence point in mod-137)
        - Position (seed % 16)
        - Category (merged % 16)
        - Basin (which of 7 attractors the seed converges to)
        - HKR color (divine operation proportion)

    HYPOTHESIS: The attractor, basin, position, and HKR color
    already encode the intent — we just need to READ it instead
    of keyword-matching.

EXPERIMENT:
    1. Run diverse inputs through the full seed pipeline
    2. Extract attractor, basin, position, HKR from the seed
    3. See if "bad" inputs naturally cluster differently from "good" inputs
    4. If yes → keywords are redundant, math already knows
    5. If no → we need to understand what the math is missing

THIS IS REVERSE ENGINEERING:
    We don't define what the intent should be.
    We observe what the Mahamantra naturally computes.
"""

import hashlib
from typing import Dict, List, Tuple

from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaAlgorithm16,
    MahaModularSynth,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import text_to_vibration
from vibe_core.mahamantra.substrate.basin_map import (
    COORD_BASIN,
    COORD_HKR,
    COORD_PHONEME_ATTRACTOR,
    BASIN_LIST,
    PHONEME_ATTRACTOR_LIST,
)
from vibe_core.mahamantra.protocols._seed import WORDS, MAHA_QUANTUM


# =============================================================================
# FULL MATHEMATICAL FINGERPRINT — everything the seed pipeline computes
# =============================================================================

def mathematical_fingerprint(text: str) -> dict:
    """
    Extract the COMPLETE mathematical fingerprint of a text input.
    No keywords. Only what the Mahamantra naturally computes.
    """
    # Layer 1: SHA256
    text_bytes = hashlib.sha256(text.lower().encode("utf-8")).digest()
    text_hash = int.from_bytes(text_bytes[:4], "big")

    # Layer 2: Shabda vibration
    vibrations = text_to_vibration(text)
    vib_sum = sum(s.signature_id for s in vibrations) if vibrations else 0
    vib_count = len(vibrations)

    # Articulation distribution (5 points)
    artic_dist = [0] * 5
    for v in vibrations:
        artic_dist[v.articulation.value] += 1

    # Voicing distribution (4 types)
    voice_dist = [0] * 4
    for v in vibrations:
        voice_dist[v.voicing.value] += 1

    # Merge
    merged = text_hash ^ (vib_sum & 0xFFFFFFFF)
    category = merged % WORDS
    base_seed = (category * MAHA_QUANTUM) + (merged % MAHA_QUANTUM)

    # Layer 3: Synth transform
    synth = MahaModularSynth(default_preset="quantum")
    transformed = synth.transform(base_seed)
    attractor_mod = transformed % MAHA_QUANTUM
    position = ((category << 24) | (transformed << 12) | attractor_mod) & 0xFFFFFFFF
    position_16 = position % WORDS

    # Basin: where does the transformed value converge?
    algo = MahaAlgorithm16()
    basin_value = transformed % MAHA_QUANTUM
    for _ in range(100):
        prev = basin_value
        basin_value = algo.transform(basin_value)
        if basin_value == prev:
            break

    # Attractor type (fixed point vs cycle)
    attractor_val, iterations, attr_type = algo.find_attractor(transformed % MAHA_QUANTUM)

    # Shabda-derived RAMA coords for HKR analysis
    # Each phoneme maps to a signature_id, we can use signature_id % 49 as coord
    rama_coords = [s.signature_id % 49 for s in vibrations] if vibrations else [0]
    avg_hkr = [0.0, 0.0, 0.0]
    for c in rama_coords:
        h, k, r = COORD_HKR[c]
        avg_hkr[0] += h
        avg_hkr[1] += k
        avg_hkr[2] += r
    n = len(rama_coords)
    avg_hkr = [x / n for x in avg_hkr]

    # Phoneme attractor distribution
    pa_dist = {}
    for c in rama_coords:
        pa = COORD_PHONEME_ATTRACTOR[c]
        pa_dist[pa] = pa_dist.get(pa, 0) + 1

    # Dominant phoneme attractor
    dominant_pa = max(pa_dist, key=pa_dist.get) if pa_dist else 0

    return {
        "text_hash": text_hash,
        "vib_sum": vib_sum,
        "vib_count": vib_count,
        "merged": merged,
        "category": category,
        "transformed": transformed,
        "attractor_mod137": attractor_mod,
        "position_16": position_16,
        "basin": basin_value,
        "attractor_value": attractor_val,
        "attractor_type": attr_type.name,
        "iterations_to_converge": iterations,
        "artic_dist": artic_dist,
        "voice_dist": voice_dist,
        "hkr": tuple(round(x, 3) for x in avg_hkr),
        "dominant_hkr": "H" if avg_hkr[0] > avg_hkr[1] and avg_hkr[0] > avg_hkr[2]
                        else "K" if avg_hkr[1] > avg_hkr[2] else "R",
        "phoneme_attractor_dist": pa_dist,
        "dominant_phoneme_attractor": dominant_pa,
    }


# =============================================================================
# TEST CORPUS — diverse inputs, labeled by expected quality
# =============================================================================

CORPUS = {
    # === CODE: GOOD ===
    "typed_func": ("good", """
def add(x: int, y: int) -> int:
    return x + y
"""),
    "typed_class": ("good", """
class Config:
    def __init__(self, path: Path) -> None:
        self.path = path
    def load(self) -> Dict[str, str]:
        return json.loads(self.path.read_text())
"""),
    "proper_error": ("good", """
def parse(data: str) -> dict:
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        logger.error("Parse failed: %s", exc)
        raise ValueError(f"Invalid JSON: {exc}") from exc
"""),

    # === CODE: BAD ===
    "any_soup": ("bad", """
from typing import Any, Dict
def process(data: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["value"] = data
    return result
"""),
    "silent_except": ("bad", """
def load(path):
    try:
        return open(path).read()
    except:
        pass
"""),
    "star_import": ("bad", """
from typing import *
from pathlib import *
def f(x, y, z):
    return x
"""),

    # === TEXT: HEALTHY ===
    "healthy_log": ("good", "All services healthy. Tests passed. Deployment verified."),
    "clean_report": ("good", "System stable. Memory usage optimal. Zero errors in 24h."),

    # === TEXT: BROKEN ===
    "error_log": ("bad", "FATAL: Connection timeout. Database crash. Memory leak detected."),
    "panic_log": ("bad", "PANIC: Unrecoverable error. System halting. Data corruption."),

    # === NEUTRAL ===
    "neutral_text": ("neutral", "The quick brown fox jumps over the lazy dog."),
    "neutral_code": ("neutral", """
x = 42
y = x * 2
print(y)
"""),
}


# =============================================================================
# ANALYSIS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 90)
    print("  INTENT FROM MATH — Can the Mahamantra compute intent without keywords?")
    print("=" * 90)

    results_by_quality = {"good": [], "bad": [], "neutral": []}

    print(f"\n  {'Label':>16}  {'Exp':>4}  {'Cat':>3}  {'Pos':>3}  {'Basin':>5}  {'Attr':>5}  {'Type':>6}  "
          f"{'HKR':>15}  {'Dom':>3}  {'DomPA':>5}")
    print(f"  {'-'*16}  {'-'*4}  {'-'*3}  {'-'*3}  {'-'*5}  {'-'*5}  {'-'*6}  {'-'*15}  {'-'*3}  {'-'*5}")

    for label, (expected, text) in CORPUS.items():
        fp = mathematical_fingerprint(text)
        results_by_quality[expected].append(fp)

        hkr_str = f"({fp['hkr'][0]:.2f},{fp['hkr'][1]:.2f},{fp['hkr'][2]:.2f})"
        print(f"  {label:>16}  {expected:>4}  {fp['category']:>3}  {fp['position_16']:>3}  "
              f"{fp['basin']:>5}  {fp['attractor_value']:>5}  {fp['attractor_type']:>6}  "
              f"{hkr_str:>15}  {fp['dominant_hkr']:>3}  {fp['dominant_phoneme_attractor']:>5}")

    # === CLUSTER ANALYSIS ===
    print(f"\n{'='*90}")
    print("  CLUSTER ANALYSIS — Do good/bad inputs naturally separate?")
    print(f"{'='*90}")

    for quality in ["good", "bad", "neutral"]:
        fps = results_by_quality[quality]
        if not fps:
            continue

        # Average values
        avg_cat = sum(f["category"] for f in fps) / len(fps)
        avg_pos = sum(f["position_16"] for f in fps) / len(fps)
        avg_basin = sum(f["basin"] for f in fps) / len(fps)
        avg_attr = sum(f["attractor_value"] for f in fps) / len(fps)
        avg_h = sum(f["hkr"][0] for f in fps) / len(fps)
        avg_k = sum(f["hkr"][1] for f in fps) / len(fps)
        avg_r = sum(f["hkr"][2] for f in fps) / len(fps)

        basins = set(f["basin"] for f in fps)
        attractors = set(f["attractor_value"] for f in fps)
        categories = set(f["category"] for f in fps)
        positions = set(f["position_16"] for f in fps)

        print(f"\n  [{quality.upper():>7}] n={len(fps)}")
        print(f"    Category:  avg={avg_cat:.1f}  unique={sorted(categories)}")
        print(f"    Position:  avg={avg_pos:.1f}  unique={sorted(positions)}")
        print(f"    Basin:     avg={avg_basin:.1f}  unique={sorted(basins)}")
        print(f"    Attractor: avg={avg_attr:.1f}  unique={sorted(attractors)}")
        print(f"    HKR:       H={avg_h:.3f}  K={avg_k:.3f}  R={avg_r:.3f}")

    # === ARTICULATION ANALYSIS ===
    print(f"\n{'='*90}")
    print("  ARTICULATION ANALYSIS — Does phonetic structure differ by quality?")
    print(f"{'='*90}")

    artic_names = ["KANTHA", "TALU", "MURDHA", "DANTA", "OSHTHA"]
    voice_names = ["UNVOICED", "UNVOICED_ASP", "VOICED", "VOICED_ASP"]

    for quality in ["good", "bad", "neutral"]:
        fps = results_by_quality[quality]
        if not fps:
            continue

        # Sum articulation distributions
        total_artic = [0] * 5
        total_voice = [0] * 4
        total_phonemes = 0
        for f in fps:
            for i in range(5):
                total_artic[i] += f["artic_dist"][i]
            for i in range(4):
                total_voice[i] += f["voice_dist"][i]
            total_phonemes += f["vib_count"]

        if total_phonemes > 0:
            artic_pct = [round(100 * a / total_phonemes, 1) for a in total_artic]
            voice_pct = [round(100 * v / total_phonemes, 1) for v in total_voice]
        else:
            artic_pct = [0] * 5
            voice_pct = [0] * 4

        print(f"\n  [{quality.upper():>7}] {total_phonemes} phonemes")
        print(f"    Articulation: {' | '.join(f'{n}={p}%' for n, p in zip(artic_names, artic_pct))}")
        print(f"    Voicing:      {' | '.join(f'{n}={p}%' for n, p in zip(voice_names, voice_pct))}")

    # === VERDICT ===
    print(f"\n{'='*90}")
    print("  VERDICT")
    print(f"{'='*90}")

    good_basins = set(f["basin"] for f in results_by_quality["good"])
    bad_basins = set(f["basin"] for f in results_by_quality["bad"])
    overlap = good_basins & bad_basins

    good_hkr = tuple(sum(f["hkr"][i] for f in results_by_quality["good"]) / len(results_by_quality["good"]) for i in range(3))
    bad_hkr = tuple(sum(f["hkr"][i] for f in results_by_quality["bad"]) / len(results_by_quality["bad"]) for i in range(3))
    hkr_dist = sum((good_hkr[i] - bad_hkr[i])**2 for i in range(3)) ** 0.5

    print(f"\n  Basin overlap (good ∩ bad):  {overlap}  ({len(overlap)} shared)")
    print(f"  HKR distance (good vs bad): {hkr_dist:.4f}")

    if len(overlap) == 0:
        print("\n  >>> BASINS SEPARATE PERFECTLY — keywords are redundant!")
        print("  >>> Intent can be computed from basin alone.")
    elif hkr_dist > 0.05:
        print(f"\n  >>> Basins overlap but HKR SEPARATES (distance={hkr_dist:.4f})")
        print("  >>> Intent can be computed from HKR color.")
    else:
        print("\n  >>> Neither basin nor HKR separate good from bad.")
        print("  >>> The math needs enrichment — but NOT keywords.")
        print("  >>> The Shabda layer already has articulation/voicing distributions.")
        print("  >>> These distributions ARE the intent signal.")

    # === ARTICULATION AS INTENT ===
    good_artic = [0] * 5
    bad_artic = [0] * 5
    good_total = 0
    bad_total = 0
    for f in results_by_quality["good"]:
        for i in range(5):
            good_artic[i] += f["artic_dist"][i]
        good_total += f["vib_count"]
    for f in results_by_quality["bad"]:
        for i in range(5):
            bad_artic[i] += f["artic_dist"][i]
        bad_total += f["vib_count"]

    if good_total > 0 and bad_total > 0:
        good_pct = [a / good_total for a in good_artic]
        bad_pct = [a / bad_total for a in bad_artic]
        artic_dist = sum((good_pct[i] - bad_pct[i])**2 for i in range(5)) ** 0.5

        print(f"\n  Articulation distance (good vs bad): {artic_dist:.4f}")
        if artic_dist > 0.02:
            print("  >>> Articulation distributions DIFFER — phonetic structure encodes quality!")
            for i, name in enumerate(artic_names):
                delta = good_pct[i] - bad_pct[i]
                if abs(delta) > 0.01:
                    direction = "more" if delta > 0 else "less"
                    print(f"      {name}: good has {direction} ({delta:+.3f})")
