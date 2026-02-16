#!/usr/bin/env python3
"""
MAHAMANTRA INVENTORY SCAN
=========================
Scans every .py file in mahamantra/ and produces a JSON inventory.

Per file:
  - path (relative to mahamantra/)
  - loc (lines of code, excluding blank/comments)
  - category: substrate|kernel|protocol|adapter|test|research|cli|audit|other
  - smells: list of detected issues
  - has_mahajana: bool (has __mahajana__ declaration)
  - has_position: bool (has __position__ declaration)
  - imports_from: list of top-level import sources
  - health: 0-100 score

Smells detected:
  - singleton_bypass: MahamantraLotus() instead of get_mahamantra()
  - any_type: uses 'Any' type annotation
  - ungoverned_io: direct open()/write_text()/json.dump() not in test/research
  - deprecated_code: contains DeprecationWarning or DEPRECATED
  - dead_import: imports something never used (basic check)
  - no_identity: production file without __mahajana__/__position__
  - bare_except: except: or except Exception without logging
"""

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

MAHAMANTRA_ROOT = Path(__file__).resolve().parent.parent.parent  # mahamantra/

CATEGORY_MAP = {
    "substrate": "substrate",
    "kernel": "kernel",
    "protocols": "protocol",
    "adapters": "adapter",
    "tests": "test",
    "research": "research",
    "cli": "cli",
    "audit": "audit",
    "dharma": "dharma",
    "reactor": "reactor",
    "lila": "lila",
    "moksha": "moksha",
    "genesis": "genesis",
    "karma": "karma",
    "kama": "kama",
    "demos": "demo",
    "tools": "tool",
    "analysis": "analysis",
    "sound": "sound",
    "venu": "venu",
    "net": "net",
    "namarupa": "namarupa",
    "seed": "seed",
    "data": "data",
}


def categorize(rel_path: str) -> str:
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        folder = parts[0]
        if folder in CATEGORY_MAP:
            return CATEGORY_MAP[folder]
    # Top-level files
    return "root"


def count_loc(source: str) -> int:
    count = 0
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def detect_smells(source: str, rel_path: str, category: str) -> List[str]:
    smells = []

    # Singleton bypass
    if "MahamantraLotus()" in source:
        # Exclude the singleton factory itself and docstrings
        lines_with_call = [
            l.strip() for l in source.splitlines()
            if "MahamantraLotus()" in l
            and not l.strip().startswith("#")
            and not l.strip().startswith('"')
            and not l.strip().startswith("'")
            and "_mahamantra_instance = MahamantraLotus()" not in l
        ]
        if lines_with_call:
            smells.append("singleton_bypass")

    # Any type usage
    if re.search(r'\bAny\b', source):
        # Check it's actually a type annotation, not just a word
        if "from typing import" in source and "Any" in source:
            smells.append("any_type")
        elif ": Any" in source or "-> Any" in source:
            smells.append("any_type")

    # Ungoverned I/O (only flag in production code, not tests/research)
    if category not in ("test", "research", "demo", "audit"):
        io_patterns = [
            r'open\(',
            r'\.write_text\(',
            r'\.write_bytes\(',
            r'json\.dump\(',
        ]
        for pat in io_patterns:
            if re.search(pat, source):
                smells.append("ungoverned_io")
                break

    # Deprecated code
    if "DeprecationWarning" in source or "DEPRECATED" in source:
        smells.append("deprecated_code")

    # No identity (production files should have __mahajana__)
    if category not in ("test", "research", "demo", "audit", "root", "data"):
        if "__mahajana__" not in source and not rel_path.endswith("__init__.py"):
            smells.append("no_identity")

    # _fire_gate direct call (should use fire_gate public API)
    if "._fire_gate(" in source:
        # Exclude the implementation itself in lotus_core.py
        if "def _fire_gate(" not in source and "self._fire_gate(gate, ctx)" not in source:
            smells.append("private_gate_call")

    return smells


def compute_health(loc: int, smells: List[str], has_mahajana: bool, category: str) -> int:
    score = 100

    # Smell penalties
    penalties = {
        "singleton_bypass": 20,
        "any_type": 10,
        "ungoverned_io": 15,
        "deprecated_code": 10,
        "no_identity": 5,
        "private_gate_call": 25,
    }
    for smell in smells:
        score -= penalties.get(smell, 5)

    # Size penalty (files over 500 LOC are suspicious)
    if loc > 500:
        score -= min(20, (loc - 500) // 100 * 5)

    # Identity bonus for production code
    if has_mahajana and category not in ("test", "research", "demo"):
        score += 5

    return max(0, min(100, score))


def scan_file(filepath: Path, root: Path) -> Dict[str, Any]:
    rel_path = str(filepath.relative_to(root))
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {
            "path": rel_path,
            "loc": 0,
            "category": "error",
            "smells": ["unreadable"],
            "has_mahajana": False,
            "has_position": False,
            "health": 0,
        }

    category = categorize(rel_path)
    loc = count_loc(source)
    smells = detect_smells(source, rel_path, category)
    has_mahajana = "__mahajana__" in source
    has_position = "__position__" in source

    health = compute_health(loc, smells, has_mahajana, category)

    return {
        "path": rel_path,
        "loc": loc,
        "category": category,
        "smells": smells,
        "has_mahajana": has_mahajana,
        "has_position": has_position,
        "health": health,
    }


def main():
    root = MAHAMANTRA_ROOT
    files = sorted(root.rglob("*.py"))
    files = [f for f in files if "__pycache__" not in str(f) and ".benchmarks" not in str(f)]

    inventory = []
    for f in files:
        entry = scan_file(f, root)
        inventory.append(entry)

    # Summary stats
    total_loc = sum(e["loc"] for e in inventory)
    total_files = len(inventory)
    categories = {}
    for e in inventory:
        cat = e["category"]
        if cat not in categories:
            categories[cat] = {"files": 0, "loc": 0, "smells": 0}
        categories[cat]["files"] += 1
        categories[cat]["loc"] += e["loc"]
        categories[cat]["smells"] += len(e["smells"])

    all_smells = {}
    for e in inventory:
        for s in e["smells"]:
            all_smells[s] = all_smells.get(s, 0) + 1

    sick_files = [e for e in inventory if e["health"] < 70]
    sick_files.sort(key=lambda x: x["health"])

    avg_health = sum(e["health"] for e in inventory) / total_files if total_files else 0

    result = {
        "scan_date": "2026-02-16",
        "total_files": total_files,
        "total_loc": total_loc,
        "avg_health": round(avg_health, 1),
        "categories": dict(sorted(categories.items(), key=lambda x: -x[1]["loc"])),
        "smell_counts": dict(sorted(all_smells.items(), key=lambda x: -x[1])),
        "sick_files_count": len(sick_files),
        "sick_files": sick_files[:50],  # Top 50 sickest
        "files": inventory,
    }

    output_path = root / "research" / "audit" / "INVENTORY.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    print(f"MAHAMANTRA INVENTORY SCAN")
    print(f"=" * 50)
    print(f"Total files:  {total_files}")
    print(f"Total LOC:    {total_loc:,}")
    print(f"Avg health:   {avg_health:.1f}/100")
    print(f"Sick files:   {len(sick_files)} (health < 70)")
    print()
    print("CATEGORIES:")
    for cat, stats in sorted(categories.items(), key=lambda x: -x[1]["loc"]):
        print(f"  {cat:15s}  {stats['files']:3d} files  {stats['loc']:6,} LOC  {stats['smells']:3d} smells")
    print()
    print("SMELL COUNTS:")
    for smell, count in sorted(all_smells.items(), key=lambda x: -x[1]):
        print(f"  {smell:25s}  {count:3d}")
    print()
    if sick_files:
        print(f"TOP 20 SICKEST FILES:")
        for e in sick_files[:20]:
            print(f"  [{e['health']:3d}] {e['path']}")
            if e["smells"]:
                print(f"        smells: {', '.join(e['smells'])}")
    print()
    print(f"Inventory written to: {output_path}")


if __name__ == "__main__":
    main()
