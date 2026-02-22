"""
LEGACY ABSORPTION MAP — Kartografiert was außerhalb Mahamantra lebt.

Für jedes Top-Level-Verzeichnis in vibe_core/ (außer mahamantra/) wird geprüft:
- Wie viele .py Dateien existieren (ohne __init__, tests, __pycache__)
- Wie viele davon Re-Export-Shims sind (importieren aus mahamantra)
- Wie viele davon echte Legacy-Logik enthalten (müssen migriert werden)
- Wie viele davon tot/leer sind (< 5 Code-Zeilen)

Ergebnis: Eine Tabelle + JSON-Report die zeigt wo die Leichen liegen.

Usage:
    python -m vibe_core.mahamantra.research.audit.legacy_absorption_map
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict


@dataclass
class FileClassification:
    path: str
    code_lines: int
    category: str  # "shim", "real", "dead"
    imports_mahamantra: bool
    has_reexport_marker: bool


@dataclass
class DirectoryReport:
    name: str
    total_files: int = 0
    real_files: int = 0
    shim_files: int = 0
    dead_files: int = 0
    total_sloc: int = 0
    status: str = ""
    files: List[FileClassification] = field(default_factory=list)


def classify_file(filepath: Path) -> FileClassification:
    """Classify a single Python file as shim, real, or dead."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return FileClassification(
            path=str(filepath),
            code_lines=0,
            category="dead",
            imports_mahamantra=False,
            has_reexport_marker=False,
        )

    # Count non-empty, non-comment, non-docstring lines (rough SLOC)
    lines = content.split("\n")
    code_lines = 0
    in_docstring = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                continue  # single-line docstring
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        code_lines += 1

    imports_mahamantra = "from vibe_core.mahamantra" in content
    has_reexport_marker = any(
        marker in content for marker in ["Re-export", "re-export", "CANONICAL", "backwards compat"]
    )

    if code_lines < 5:
        category = "dead"
    elif has_reexport_marker and code_lines < 30:
        category = "shim"
    elif imports_mahamantra and code_lines < 20:
        category = "shim"
    else:
        category = "real"

    return FileClassification(
        path=str(filepath),
        code_lines=code_lines,
        category=category,
        imports_mahamantra=imports_mahamantra,
        has_reexport_marker=has_reexport_marker,
    )


def scan_directory(base: Path, dirname: str) -> DirectoryReport:
    """Scan a single top-level directory."""
    dirpath = base / dirname
    if not dirpath.exists():
        return DirectoryReport(name=dirname)

    py_files = [
        f
        for f in dirpath.rglob("*.py")
        if f.name != "__init__.py"
        and "test" not in f.name.lower()
        and "__pycache__" not in str(f)
        and ".benchmarks" not in str(f)
    ]

    report = DirectoryReport(name=dirname, total_files=len(py_files))

    for f in sorted(py_files):
        cls = classify_file(f)
        report.files.append(cls)
        report.total_sloc += cls.code_lines

        if cls.category == "shim":
            report.shim_files += 1
        elif cls.category == "dead":
            report.dead_files += 1
        else:
            report.real_files += 1

    if report.real_files == 0 and report.total_files > 0:
        report.status = "ABSORBED"  # All migrated or dead
    elif report.shim_files > 0 or report.dead_files > 0:
        report.status = "MIXED"  # Partially migrated
    elif report.total_files > 0:
        report.status = "LEGACY"  # Nothing migrated yet
    else:
        report.status = "EMPTY"

    return report


def run_full_scan(project_root: Path) -> Dict:
    """Run the full legacy absorption scan."""
    base = project_root / "vibe_core"

    # All top-level dirs except mahamantra
    all_dirs = sorted(
        [
            d.name
            for d in base.iterdir()
            if d.is_dir() and d.name != "mahamantra" and d.name != "__pycache__" and d.name != ".benchmarks"
        ]
    )

    reports = []
    totals = {"total": 0, "real": 0, "shim": 0, "dead": 0, "sloc": 0}

    for dirname in all_dirs:
        report = scan_directory(base, dirname)
        if report.total_files == 0:
            continue
        reports.append(report)
        totals["total"] += report.total_files
        totals["real"] += report.real_files
        totals["shim"] += report.shim_files
        totals["dead"] += report.dead_files
        totals["sloc"] += report.total_sloc

    return {"reports": reports, "totals": totals}


def print_table(result: Dict) -> None:
    """Print a human-readable table."""
    reports = result["reports"]
    totals = result["totals"]

    print("=" * 90)
    print("LEGACY ABSORPTION MAP — What lives outside Mahamantra")
    print("=" * 90)
    print(f"{'Directory':22s} | {'Files':>5s} | {'Real':>4s} | {'Shim':>4s} | {'Dead':>4s} | {'SLOC':>6s} | Status")
    print("-" * 90)

    for r in sorted(reports, key=lambda x: x.real_files, reverse=True):
        print(
            f"{r.name:22s} | {r.total_files:5d} | {r.real_files:4d} | "
            f"{r.shim_files:4d} | {r.dead_files:4d} | {r.total_sloc:6d} | {r.status}"
        )

    print("-" * 90)
    print(
        f"{'TOTAL':22s} | {totals['total']:5d} | {totals['real']:4d} | "
        f"{totals['shim']:4d} | {totals['dead']:4d} | {totals['sloc']:6d} |"
    )
    print("=" * 90)

    # Summary
    pct_real = (totals["real"] / totals["total"] * 100) if totals["total"] else 0
    pct_absorbed = ((totals["shim"] + totals["dead"]) / totals["total"] * 100) if totals["total"] else 0
    print(f"\nReal legacy (must migrate): {totals['real']} files ({pct_real:.1f}%)")
    print(f"Already absorbed/dead:     {totals['shim'] + totals['dead']} files ({pct_absorbed:.1f}%)")

    # Top offenders
    print("\nTOP LEGACY OFFENDERS (most real files to absorb):")
    for r in sorted(reports, key=lambda x: x.real_files, reverse=True)[:10]:
        if r.real_files == 0:
            break
        print(f"  {r.name:22s} — {r.real_files} real files, {r.total_sloc} SLOC")


def save_json(result: Dict, output_path: Path) -> None:
    """Save full report as JSON."""
    serializable = {
        "totals": result["totals"],
        "directories": [asdict(r) for r in result["reports"]],
    }
    output_path.write_text(json.dumps(serializable, indent=2))
    print(f"\nJSON report saved to: {output_path}")


def main():
    # Find project root
    script_path = Path(__file__).resolve()
    # Walk up to find vibe_core
    project_root = script_path
    while project_root.name != "steward-protocol" and project_root != project_root.parent:
        project_root = project_root.parent

    if not (project_root / "vibe_core").exists():
        print("ERROR: Cannot find vibe_core/ from script location", file=sys.stderr)
        sys.exit(1)

    result = run_full_scan(project_root)
    print_table(result)

    # Save JSON next to this script
    json_path = script_path.parent / "legacy_absorption_report.json"
    save_json(result, json_path)


if __name__ == "__main__":
    main()
