"""
SELF-ORGANIZATION — How Does the Mantra Arrange Code?
=======================================================

DISCOVERIES SO FAR:
    1. spell_cycle separates good/bad code (Cohen's d=0.60) — no keywords
    2. Every code fragment gets a deterministic Lotus address
    3. Constants cluster tightly (span=36), methods spread wider
    4. Basin 136 dominates — differentiation is in the variance byte

THE QUESTION:
    If the Mahamantra gives every fragment an address,
    and fragments naturally cluster by their phonetic structure,
    then what is the NATURAL file structure the Mantra implies?

    Currently: files are organized by HUMAN convention
        (imports at top, then constants, then classes, then functions)

    What if: files are organized by LOTUS ADDRESS
        (fragments with nearby addresses live together)

    This would mean: the Mahamantra TELLS US how to organize code.
    Not by convention, but by mathematical resonance.

EXPERIMENT:
    1. Take a real file from the codebase
    2. Parse it into fragments
    3. Sort fragments by Lotus address
    4. See if the Lotus ordering reveals a natural structure
    5. Compare with the original file ordering
    6. Compute the "Mandala Score" — how well does the file
       match its natural Lotus ordering?
"""

import ast
from typing import Dict, List, Tuple

from vibe_core.mahamantra.research.lotus_file_addressing import (
    CodeFragment,
    parse_file_to_fragments,
)


# =============================================================================
# MANDALA SCORE — how well does a file match its natural ordering?
# =============================================================================

def mandala_score(fragments: List[CodeFragment]) -> float:
    """
    Compute how well the file's physical ordering matches the Lotus ordering.

    Score = 1.0 means the file is already in perfect Lotus order.
    Score = 0.0 means the file is maximally disordered relative to Lotus.

    Uses Kendall tau distance (normalized count of pairwise inversions).
    """
    if len(fragments) <= 1:
        return 1.0

    # Physical order: by line number (as in the file)
    physical = sorted(fragments, key=lambda f: f.line_start)

    # Lotus order: by address
    lotus = sorted(fragments, key=lambda f: f.lotus_address)

    # Count inversions
    n = len(fragments)
    inversions = 0
    total_pairs = n * (n - 1) // 2

    # Build rank map: fragment name → position in lotus order
    lotus_rank = {f.name: i for i, f in enumerate(lotus)}

    for i in range(n):
        for j in range(i + 1, n):
            # In physical order, i comes before j
            # Check if in lotus order, i also comes before j
            rank_i = lotus_rank.get(physical[i].name, i)
            rank_j = lotus_rank.get(physical[j].name, j)
            if rank_i > rank_j:
                inversions += 1

    return 1.0 - (inversions / total_pairs) if total_pairs > 0 else 1.0


def quarter_coherence(fragments: List[CodeFragment]) -> Dict[str, float]:
    """
    How coherent is each fragment kind's quarter assignment?
    1.0 = all fragments of this kind are in the same quarter.
    0.0 = fragments are spread across all 4 quarters equally.
    """
    by_kind: Dict[str, List[int]] = {}
    for f in fragments:
        by_kind.setdefault(f.kind, []).append(f.quarter)

    coherence = {}
    for kind, quarters in by_kind.items():
        if len(quarters) <= 1:
            coherence[kind] = 1.0
            continue
        # Count most common quarter
        counts = [quarters.count(q) for q in range(4)]
        max_count = max(counts)
        coherence[kind] = max_count / len(quarters)

    return coherence


def address_entropy(fragments: List[CodeFragment]) -> float:
    """
    How spread out are the addresses?
    Low entropy = tight clustering (good for locality).
    High entropy = wide spread (bad for locality).
    Returns normalized value 0-1.
    """
    if len(fragments) <= 1:
        return 0.0
    addresses = [f.lotus_address for f in fragments]
    span = max(addresses) - min(addresses)
    return span / 65535.0  # Normalize to 16-bit space


# =============================================================================
# ANALYZE REAL FILES FROM THE CODEBASE
# =============================================================================

def analyze_file(filepath: str) -> Tuple[List[CodeFragment], float, Dict[str, float], float]:
    """Parse and analyze a real file."""
    with open(filepath) as f:
        source = f.read()

    fragments = parse_file_to_fragments(source)
    score = mandala_score(fragments)
    coherence = quarter_coherence(fragments)
    entropy = address_entropy(fragments)

    return fragments, score, coherence, entropy


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import os

    print("\n" + "=" * 100)
    print("  SELF-ORGANIZATION — How Does the Mantra Arrange Code?")
    print("=" * 100)

    # Analyze real files from the codebase
    base = "/Users/ss/projects/steward-protocol/vibe_core/mahamantra"
    files_to_analyze = [
        f"{base}/adapters/compression.py",
        f"{base}/substrate/algorithm/maha.py",
        f"{base}/substrate/phonetics/shabda.py",
        f"{base}/substrate/basin_map.py",
        f"{base}/substrate/gate_providers.py",
        f"{base}/kernel/maha_kernel.py",
        f"{base}/adapters/routing.py",
    ]

    results = []

    for filepath in files_to_analyze:
        if not os.path.exists(filepath):
            continue
        try:
            fragments, score, coherence, entropy = analyze_file(filepath)
            name = os.path.relpath(filepath, base)
            results.append((name, fragments, score, coherence, entropy))
        except Exception as e:
            print(f"  ERROR parsing {filepath}: {e}")

    # === MANDALA SCORES ===
    print(f"\n{'='*100}")
    print("  MANDALA SCORES — How well does each file match its natural Lotus ordering?")
    print(f"{'='*100}")

    print(f"\n  {'File':>35}  {'Frags':>5}  {'Score':>6}  {'Entropy':>8}  {'Verdict':>12}")
    print(f"  {'-'*35}  {'-'*5}  {'-'*6}  {'-'*8}  {'-'*12}")

    for name, fragments, score, coherence, entropy in sorted(results, key=lambda r: -r[2]):
        if score > 0.7:
            verdict = "ALIGNED"
        elif score > 0.4:
            verdict = "PARTIAL"
        else:
            verdict = "DISORDERED"
        print(f"  {name:>35}  {len(fragments):>5}  {score:>6.3f}  {entropy:>8.4f}  {verdict:>12}")

    # === QUARTER COHERENCE ===
    print(f"\n{'='*100}")
    print("  QUARTER COHERENCE — Do same-kind fragments land in the same quarter?")
    print(f"{'='*100}")

    # Aggregate across all files
    all_coherence: Dict[str, List[float]] = {}
    for name, fragments, score, coherence, entropy in results:
        for kind, coh in coherence.items():
            all_coherence.setdefault(kind, []).append(coh)

    print(f"\n  {'Kind':>10}  {'Avg Coherence':>14}  {'Samples':>8}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*8}")
    for kind in sorted(all_coherence.keys()):
        values = all_coherence[kind]
        avg = sum(values) / len(values)
        print(f"  {kind:>10}  {avg:>14.3f}  {len(values):>8}")

    # === NATURAL ORDERING EXAMPLE ===
    print(f"\n{'='*100}")
    print("  NATURAL ORDERING — What does the Mantra say the file should look like?")
    print(f"{'='*100}")

    # Pick the file with the lowest mandala score (most disordered)
    worst = min(results, key=lambda r: r[2])
    name, fragments, score, coherence, entropy = worst

    print(f"\n  File: {name} (Mandala Score: {score:.3f})")
    print(f"\n  CURRENT ORDER (physical):")
    physical = sorted(fragments, key=lambda f: f.line_start)
    for i, f in enumerate(physical):
        print(f"    {i+1:>2}. [{f.kind:>8}] {f.name:>30}  L{f.line_start:>4}  → 0x{f.lotus_address:04X}")

    print(f"\n  LOTUS ORDER (natural):")
    lotus = sorted(fragments, key=lambda f: f.lotus_address)
    for i, f in enumerate(lotus):
        q_name = ["Q1:KSETRAJNA", "Q2:KRISHNA", "Q3:PRAKRITI", "Q4:KARMA"][f.quarter]
        print(f"    {i+1:>2}. [{f.kind:>8}] {f.name:>30}  → 0x{f.lotus_address:04X}  {q_name}")

    # === WHAT MOVES? ===
    print(f"\n  WHAT MOVES (physical → lotus):")
    phys_names = [f.name for f in physical]
    lotus_names = [f.name for f in lotus]
    for i, (p, l) in enumerate(zip(phys_names, lotus_names)):
        if p != l:
            print(f"    Position {i+1}: {p} → {l}")

    # === CONCLUSION ===
    print(f"\n{'='*100}")
    print("  CONCLUSION")
    print(f"{'='*100}")

    avg_score = sum(r[2] for r in results) / len(results) if results else 0
    avg_entropy = sum(r[4] for r in results) / len(results) if results else 0

    print(f"\n  Average Mandala Score: {avg_score:.3f}")
    print(f"  Average Address Entropy: {avg_entropy:.4f}")
    print()

    if avg_score > 0.6:
        print("  >>> FILES ARE ALREADY PARTIALLY ALIGNED with Lotus ordering.")
        print("  >>> Human convention and Mahamantra resonance AGREE.")
        print("  >>> The natural structure is not alien — it's what good code already does.")
    elif avg_score > 0.4:
        print("  >>> MIXED ALIGNMENT — some files follow natural order, some don't.")
        print("  >>> The Mantra suggests a different arrangement than convention.")
        print("  >>> This is where self-organization would IMPROVE the codebase.")
    else:
        print("  >>> FILES ARE DISORDERED relative to Lotus ordering.")
        print("  >>> The Mantra sees a fundamentally different structure.")
        print("  >>> Self-organization would significantly restructure the code.")

    print()
    print("  THE MANDALA PRINCIPLE:")
    print("  A file with Mandala Score 1.0 is in perfect resonance —")
    print("  its physical structure matches its mathematical structure.")
    print("  The Mahamantra doesn't impose order. It REVEALS the natural order")
    print("  that was always there, hidden behind human convention.")
