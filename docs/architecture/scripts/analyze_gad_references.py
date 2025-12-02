#!/usr/bin/env python3
"""
GAD REFERENCE ANALYZER
======================
Finds all GAD-XXXX references in the codebase and checks which have formal docs.

This is REVERSE ENGINEERING - from code to spec.

Usage:
    python docs/architecture/scripts/analyze_gad_references.py

Output:
    - All GAD references found in code
    - Which have corresponding .md docs
    - Which are UNDOCUMENTED (need specs written)
"""

import re
from collections import defaultdict
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Patterns to find GAD references
GAD_PATTERN = re.compile(r"GAD-(\d+)", re.IGNORECASE)

# Known GAD doc locations
GAD_DOC_LOCATIONS = [
    PROJECT_ROOT,  # Root level
    PROJECT_ROOT / "docs" / "architecture" / "core",
    PROJECT_ROOT / "docs" / "architecture",
    PROJECT_ROOT / "docs",
]


def find_gad_docs() -> dict:
    """Find all existing GAD-*.md documents."""
    gad_docs = {}

    for location in GAD_DOC_LOCATIONS:
        if not location.exists():
            continue
        for f in location.glob("GAD*.md"):
            # Extract GAD number
            match = GAD_PATTERN.search(f.name)
            if match:
                gad_num = match.group(1)
                gad_docs[gad_num] = f

    return gad_docs


def find_gad_references_in_file(filepath: Path) -> list:
    """Find all GAD-XXXX references in a single file."""
    references = []

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.split("\n"), 1):
            for match in GAD_PATTERN.finditer(line):
                references.append(
                    {
                        "gad_number": match.group(1),
                        "file": str(filepath.relative_to(PROJECT_ROOT)),
                        "line": line_num,
                        "context": line.strip()[:100],
                    }
                )
    except Exception:
        pass

    return references


def scan_codebase() -> dict:
    """Scan entire codebase for GAD references."""
    gad_refs = defaultdict(list)

    # Directories to scan
    scan_dirs = [
        PROJECT_ROOT / "vibe_core",
        PROJECT_ROOT / "steward",
        PROJECT_ROOT / "agent_city",
        PROJECT_ROOT / "provider",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "tests",
    ]

    # File extensions to scan
    extensions = {".py", ".yaml", ".yml", ".json", ".md"}

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for filepath in scan_dir.rglob("*"):
            if filepath.is_file() and filepath.suffix in extensions:
                refs = find_gad_references_in_file(filepath)
                for ref in refs:
                    gad_refs[ref["gad_number"]].append(ref)

    return dict(gad_refs)


def main():
    print("=" * 70)
    print("GAD REFERENCE ANALYZER - Reverse Engineering Specs from Code")
    print("=" * 70)
    print()

    # Find existing docs
    gad_docs = find_gad_docs()
    print(f"📚 Found {len(gad_docs)} existing GAD documents:")
    for num, path in sorted(gad_docs.items(), key=lambda x: int(x[0])):
        print(f"   GAD-{num}: {path.relative_to(PROJECT_ROOT)}")
    print()

    # Scan codebase
    print("🔍 Scanning codebase for GAD references...")
    gad_refs = scan_codebase()
    print(f"   Found references to {len(gad_refs)} unique GAD specifications")
    print()

    # Analyze
    documented = []
    undocumented = []

    for gad_num, refs in sorted(gad_refs.items(), key=lambda x: int(x[0])):
        if gad_num in gad_docs:
            documented.append((gad_num, refs, gad_docs[gad_num]))
        else:
            undocumented.append((gad_num, refs))

    # Report documented
    print("✅ DOCUMENTED GAD SPECS (have .md files):")
    print("-" * 70)
    for gad_num, refs, doc_path in documented:
        files = set(r["file"] for r in refs)
        print(f"   GAD-{gad_num}: {len(refs)} references in {len(files)} files")
        print(f"            Doc: {doc_path.relative_to(PROJECT_ROOT)}")
    print()

    # Report undocumented - THIS IS THE GOLD
    print("❌ UNDOCUMENTED GAD SPECS (code exists, no spec doc!):")
    print("-" * 70)
    for gad_num, refs in undocumented:
        files = set(r["file"] for r in refs)
        print(f"\n   GAD-{gad_num}: {len(refs)} references in {len(files)} files")
        print("   Files:")
        for f in sorted(files)[:5]:
            print(f"      - {f}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
        print("   Sample contexts:")
        for ref in refs[:3]:
            print(f"      {ref['file']}:{ref['line']}: {ref['context'][:60]}...")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"   Documented:   {len(documented)} GAD specs")
    print(f"   Undocumented: {len(undocumented)} GAD specs  ← NEED SPECS WRITTEN!")
    print()

    if undocumented:
        print("🔥 PRIORITY: Write specs for these undocumented GADs:")
        for gad_num, refs in sorted(undocumented, key=lambda x: -len(x[1])):
            print(f"   GAD-{gad_num} ({len(refs)} code references)")


if __name__ == "__main__":
    main()
