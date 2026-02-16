"""
COMPLEXITY HOTSPOTS — Findet die unwartbarsten Funktionen im Projekt.

Nutzt radon (muss installiert sein) um zyklomatische Komplexität zu messen.
Gibt Schulnoten: A(1-5) B(6-10) C(11-20) D(21-30) E(31-40) F(41+)

Fokus: Semantische Analyse, nicht nur Syntax.
- Welche Funktionen sind Zeitbomben?
- Welche Module haben die höchste Durchschnittskomplexität?
- Wo ist die Komplexität in Mahamantra vs. Legacy?

Usage:
    python -m vibe_core.mahamantra.research.audit.complexity_hotspots
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Hotspot:
    filepath: str
    lineno: int
    name: str
    classname: str
    complexity: int
    grade: str
    is_mahamantra: bool


def grade_for_cc(cc: int) -> str:
    if cc <= 5: return "A"
    if cc <= 10: return "B"
    if cc <= 20: return "C"
    if cc <= 30: return "D"
    if cc <= 40: return "E"
    return "F"


def run_radon(target_dir: str) -> List[Hotspot]:
    """Run radon cc and parse JSON output."""
    try:
        result = subprocess.run(
            ["radon", "cc", target_dir, "-j", "-a", "-nc"],
            capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError:
        print("ERROR: radon not installed. Run: pip install radon", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"ERROR: radon failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    hotspots = []

    for filepath, blocks in data.items():
        is_maha = "mahamantra" in filepath
        for b in blocks:
            cc = b["complexity"]
            hotspots.append(Hotspot(
                filepath=filepath,
                lineno=b["lineno"],
                name=b["name"],
                classname=b.get("classname", ""),
                complexity=cc,
                grade=grade_for_cc(cc),
                is_mahamantra=is_maha,
            ))

    return hotspots


def analyze(hotspots: List[Hotspot]) -> Dict:
    """Compute aggregate statistics."""
    # Per-directory aggregation
    dir_stats: Dict[str, List[int]] = {}
    for h in hotspots:
        parts = Path(h.filepath).parts
        # Get top-level dir under vibe_core/
        try:
            vc_idx = list(parts).index("vibe_core")
            top_dir = parts[vc_idx + 1] if vc_idx + 1 < len(parts) else "root"
        except ValueError:
            top_dir = "unknown"
        dir_stats.setdefault(top_dir, []).append(h.complexity)

    dir_averages = {}
    for d, ccs in dir_stats.items():
        avg = sum(ccs) / len(ccs) if ccs else 0
        dir_averages[d] = {
            "count": len(ccs),
            "avg_cc": round(avg, 2),
            "max_cc": max(ccs) if ccs else 0,
            "grade": grade_for_cc(int(avg)),
        }

    # Grade distribution
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for h in hotspots:
        grade_dist[h.grade] += 1

    # Mahamantra vs Legacy
    maha = [h for h in hotspots if h.is_mahamantra]
    legacy = [h for h in hotspots if not h.is_mahamantra]
    maha_avg = sum(h.complexity for h in maha) / len(maha) if maha else 0
    legacy_avg = sum(h.complexity for h in legacy) / len(legacy) if legacy else 0

    return {
        "total_blocks": len(hotspots),
        "grade_distribution": grade_dist,
        "mahamantra": {"blocks": len(maha), "avg_cc": round(maha_avg, 2)},
        "legacy": {"blocks": len(legacy), "avg_cc": round(legacy_avg, 2)},
        "dir_averages": dir_averages,
    }


def print_report(hotspots: List[Hotspot], stats: Dict) -> None:
    """Print human-readable report."""
    print("=" * 90)
    print("COMPLEXITY HOTSPOTS — Cyclomatic Complexity Analysis")
    print("=" * 90)

    # Grade distribution
    gd = stats["grade_distribution"]
    total = stats["total_blocks"]
    print(f"\nGrade Distribution ({total} blocks analyzed):")
    for grade in ["A", "B", "C", "D", "E", "F"]:
        count = gd[grade]
        pct = count / total * 100 if total else 0
        bar = "#" * int(pct / 2)
        print(f"  {grade}: {count:5d} ({pct:5.1f}%) {bar}")

    # Mahamantra vs Legacy
    m = stats["mahamantra"]
    l = stats["legacy"]
    print(f"\nMahamantra: {m['blocks']} blocks, avg CC={m['avg_cc']}")
    print(f"Legacy:     {l['blocks']} blocks, avg CC={l['avg_cc']}")

    # Per-directory averages (sorted by avg CC descending)
    print(f"\nPer-Directory Average Complexity:")
    print(f"  {'Directory':22s} | {'Blocks':>6s} | {'Avg CC':>6s} | {'Max CC':>6s} | Grade")
    print(f"  {'-'*70}")
    for d, s in sorted(stats["dir_averages"].items(), key=lambda x: x[1]["avg_cc"], reverse=True):
        print(f"  {d:22s} | {s['count']:6d} | {s['avg_cc']:6.1f} | {s['max_cc']:6d} | {s['grade']}")

    # Top 25 worst functions
    worst = sorted(hotspots, key=lambda h: h.complexity, reverse=True)[:25]
    print(f"\nTOP 25 WORST FUNCTIONS:")
    print(f"  {'#':>3s} {'Grade':>5s} {'CC':>4s} | {'File':50s} | Function")
    print(f"  {'-'*90}")
    for i, h in enumerate(worst, 1):
        short = h.filepath.replace("vibe_core/", "")
        label = f"{h.classname}.{h.name}" if h.classname else h.name
        loc = f"{short}:{h.lineno}"
        print(f"  {i:3d} [{h.grade}] {h.complexity:4d} | {loc:50s} | {label}")


def main():
    script_path = Path(__file__).resolve()
    project_root = script_path
    while project_root.name != "steward-protocol" and project_root != project_root.parent:
        project_root = project_root.parent

    target = str(project_root / "vibe_core")
    if not Path(target).exists():
        print("ERROR: Cannot find vibe_core/", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {target} ...")
    hotspots = run_radon(target)
    stats = analyze(hotspots)
    print_report(hotspots, stats)

    # Save JSON
    json_path = script_path.parent / "complexity_hotspots_report.json"
    json_path.write_text(json.dumps({
        "stats": stats,
        "top_50": [
            {
                "filepath": h.filepath, "lineno": h.lineno,
                "name": h.name, "classname": h.classname,
                "complexity": h.complexity, "grade": h.grade,
                "is_mahamantra": h.is_mahamantra,
            }
            for h in sorted(hotspots, key=lambda h: h.complexity, reverse=True)[:50]
        ],
    }, indent=2))
    print(f"\nJSON report saved to: {json_path}")


if __name__ == "__main__":
    main()
