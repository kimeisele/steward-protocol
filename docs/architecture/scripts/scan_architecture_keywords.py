#!/usr/bin/env python3
"""
ARCHITECTURE KEYWORD SCANNER
============================
Scans codebase for architecture-relevant keywords beyond just GAD.

Keywords:
- GAD-XXX: Governance Architecture Documents
- ARCH-XXX: Architecture decisions
- ADR-XXX: Architecture Decision Records
- Vedic concepts: parampara, karma, dharma, prana, veda, sankhya, etc.

Usage:
    python docs/architecture/scripts/scan_architecture_keywords.py

Output:
    docs/architecture/KEYWORD_INDEX.yaml
"""

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

# Keywords to scan for
KEYWORD_PATTERNS = {
    "GAD": re.compile(r"GAD-(\d+)", re.IGNORECASE),
    "ARCH": re.compile(r"ARCH-(\d+)", re.IGNORECASE),
    "ADR": re.compile(r"ADR-(\d+)", re.IGNORECASE),
}

# Vedic/domain concepts (case-insensitive exact match)
VEDIC_CONCEPTS = [
    "parampara",
    "karma",
    "dharma",
    "prana",
    "veda",
    "sankhya",
    "bhagavat",
    "kanto",
    "sarga",
    "narasimha",
    "bhu-mandala",
    "civic",
    "steward",
]


def scan_numbered_refs(pattern_name, pattern, extensions=("py", "yaml", "json", "md")):
    """Scan for numbered references like GAD-000, ARCH-021."""
    refs = defaultdict(lambda: {"count": 0, "files": [], "contexts": []})

    for ext in extensions:
        for f in Path(".").rglob(f"*.{ext}"):
            if ".git" in str(f) or "node_modules" in str(f):
                continue
            try:
                content = f.read_text()
                for match in pattern.finditer(content):
                    ref_id = f"{pattern_name}-{match.group(1)}"
                    refs[ref_id]["count"] += 1
                    if str(f) not in refs[ref_id]["files"]:
                        refs[ref_id]["files"].append(str(f))
                    # Get line context
                    if len(refs[ref_id]["contexts"]) < 2:
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        ctx = content[start:end].replace("\n", " ").strip()[:100]
                        if ctx not in refs[ref_id]["contexts"]:
                            refs[ref_id]["contexts"].append(ctx)
            except Exception:
                pass

    return dict(refs)


def scan_concepts(concepts, extensions=("py",)):
    """Scan for domain concepts (vedic terms etc)."""
    refs = defaultdict(lambda: {"count": 0, "files": [], "usage": []})

    for ext in extensions:
        for f in Path(".").rglob(f"*.{ext}"):
            if ".git" in str(f) or "node_modules" in str(f):
                continue
            try:
                content = f.read_text().lower()
                for concept in concepts:
                    pattern = re.compile(rf"\b{concept}\b", re.IGNORECASE)
                    matches = pattern.findall(content)
                    if matches:
                        refs[concept]["count"] += len(matches)
                        if str(f) not in refs[concept]["files"]:
                            refs[concept]["files"].append(str(f))
            except Exception:
                pass

    return dict(refs)


def main():
    print("=" * 60)
    print("ARCHITECTURE KEYWORD SCANNER")
    print("=" * 60)
    print()

    index = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "method": "data-driven scan",
        },
        "numbered_refs": {},
        "concepts": {},
    }

    # Scan numbered references
    for name, pattern in KEYWORD_PATTERNS.items():
        print(f"Scanning {name} references...")
        refs = scan_numbered_refs(name, pattern)
        if refs:
            index["numbered_refs"][name] = {
                "total": len(refs),
                "total_refs": sum(r["count"] for r in refs.values()),
                "items": {
                    k: {"count": v["count"], "files": len(v["files"])}
                    for k, v in sorted(refs.items(), key=lambda x: -x[1]["count"])
                },
            }
            print(f"   Found {len(refs)} unique {name} identifiers")

    # Scan vedic concepts
    print("Scanning vedic/domain concepts...")
    concepts = scan_concepts(VEDIC_CONCEPTS)
    index["concepts"] = {
        "total": len([c for c in concepts.values() if c["count"] > 0]),
        "items": {
            k: {"count": v["count"], "files": len(v["files"])}
            for k, v in sorted(concepts.items(), key=lambda x: -x[1]["count"])
            if v["count"] > 0
        },
    }
    print(f"   Found {index['concepts']['total']} active concepts")

    # Write output
    output_path = Path("docs/architecture/KEYWORD_INDEX.yaml")
    with open(output_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print()
    print(f"✅ Generated: {output_path}")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, data in index["numbered_refs"].items():
        print(f"{name}: {data['total']} unique, {data['total_refs']} total refs")
    print(f"Concepts: {index['concepts']['total']} active")
    print()

    # Top items
    print("TOP ITEMS:")
    for name, data in index["numbered_refs"].items():
        top = list(data["items"].items())[:3]
        for item, info in top:
            print(f"   {item}: {info['count']} refs in {info['files']} files")

    print()
    for concept, info in list(index["concepts"]["items"].items())[:5]:
        print(f"   {concept}: {info['count']} refs in {info['files']} files")


if __name__ == "__main__":
    main()
