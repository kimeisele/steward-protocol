#!/usr/bin/env python3
"""
GAD INDEX GENERATOR - Data-Driven Architecture Index
=====================================================
Generates GAD_INDEX.yaml from CODE REALITY, not theory.

This is THE source of truth. Run it, commit the output.
The index tells us what ACTUALLY exists.

Usage:
    python docs/architecture/scripts/generate_gad_index.py

Output:
    docs/architecture/GAD_INDEX.yaml
"""

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml


def scan_codebase():
    """Scan all code for GAD references."""
    gad_pattern = re.compile(r"GAD-(\d+)", re.IGNORECASE)
    gads = defaultdict(lambda: {"refs": 0, "files": [], "contexts": [], "documented": False, "doc_path": None})

    # Find existing GAD docs
    for md in Path(".").rglob("GAD*.md"):
        if ".git" in str(md):
            continue
        match = re.search(r"GAD-?(\d+)", md.name)
        if match:
            gad_id = f"GAD-{match.group(1)}"
            gads[gad_id]["documented"] = True
            gads[gad_id]["doc_path"] = str(md)

    # Scan code for references
    for ext in ["py", "yaml", "json"]:
        for f in Path(".").rglob(f"*.{ext}"):
            if ".git" in str(f) or "node_modules" in str(f) or "drafts" in str(f):
                continue
            try:
                content = f.read_text()
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    for match in gad_pattern.finditer(line):
                        gad_id = f"GAD-{match.group(1)}"
                        gads[gad_id]["refs"] += 1
                        if str(f) not in gads[gad_id]["files"]:
                            gads[gad_id]["files"].append(str(f))
                        # Capture context (first 3 only)
                        if len(gads[gad_id]["contexts"]) < 3:
                            ctx = line.strip()[:100]
                            if ctx not in gads[gad_id]["contexts"]:
                                gads[gad_id]["contexts"].append(ctx)
            except Exception:
                pass

    return dict(gads)


def determine_pillar(gad_num):
    """Determine which pillar a GAD belongs to based on number."""
    if gad_num == 0:
        return "FOUNDATION"
    elif gad_num < 10:
        return "LEGACY"  # Old vibe-agency single digits
    elif gad_num < 100:
        return "0XX"
    elif gad_num < 1000:
        return f"{gad_num // 100}XX"
    elif gad_num < 10000:
        return f"{gad_num // 100}XX"  # 5000 -> 50XX, 5500 -> 55XX
    return "UNKNOWN"


def build_index(gads):
    """Build structured index from GAD data."""
    index = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "method": "data-driven (scanned from code)",
            "total_gads": len(gads),
            "documented": sum(1 for g in gads.values() if g["documented"]),
            "undocumented": sum(1 for g in gads.values() if not g["documented"] and g["refs"] > 0),
        },
        "pillars": defaultdict(list),
        "gads": {},
    }

    for gad_id, data in sorted(gads.items(), key=lambda x: -x[1]["refs"]):
        if data["refs"] == 0 and not data["documented"]:
            continue

        gad_num = int(re.search(r"\d+", gad_id).group())
        pillar = determine_pillar(gad_num)

        entry = {
            "refs": data["refs"],
            "files": len(data["files"]),
            "documented": data["documented"],
            "pillar": pillar,
        }
        if data["doc_path"]:
            entry["doc"] = data["doc_path"]
        if data["contexts"]:
            entry["sample"] = data["contexts"][0]

        index["gads"][gad_id] = entry
        index["pillars"][pillar].append(gad_id)

    # Convert defaultdict to regular dict for YAML
    index["pillars"] = dict(index["pillars"])

    return index


def main():
    print("Scanning codebase for GAD references...")
    gads = scan_codebase()

    print(f"Found {len(gads)} unique GAD identifiers")

    index = build_index(gads)

    # Write YAML
    output_path = Path("docs/architecture/GAD_INDEX.yaml")
    with open(output_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✅ Generated: {output_path}")
    print(f"   Total GADs: {index['meta']['total_gads']}")
    print(f"   Documented: {index['meta']['documented']}")
    print(f"   Undocumented: {index['meta']['undocumented']}")

    print("\nPillars by reference count:")
    pillar_counts = defaultdict(int)
    for gad_id, data in index["gads"].items():
        pillar_counts[data["pillar"]] += data["refs"]

    for pillar, count in sorted(pillar_counts.items(), key=lambda x: -x[1]):
        gad_list = index["pillars"].get(pillar, [])
        print(f"   {pillar}: {count} refs ({len(gad_list)} GADs)")


if __name__ == "__main__":
    main()
