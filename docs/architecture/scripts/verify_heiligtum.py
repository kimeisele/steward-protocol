#!/usr/bin/env python3
"""
HEILIGTUM VERIFIER - Check Code Against Sacred Registry
========================================================
Compares GAD_INDEX.yaml (code reality) against HEILIGTUM.yaml (sacred truth).

This script is meant to run as a background service or CI check.
It reports DIFFS that require HIL attention.

Usage:
    python docs/architecture/scripts/verify_heiligtum.py

Exit codes:
    0 = All good, code matches HEILIGTUM
    1 = ERRORS found (orphan GADs, missing EPICs)
    2 = WARNINGS found (undocumented specs)
"""

import hashlib
import sys
from pathlib import Path

import yaml


def load_yaml(path):
    """Load YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def compute_seal_hash(heiligtum):
    """Compute hash of pillars + extended_ranges + rules (excluding meta)."""
    content = {
        "pillars": heiligtum.get("pillars", {}),
        "extended_ranges": heiligtum.get("extended_ranges", {}),
        "rules": heiligtum.get("rules", []),
    }
    yaml_str = yaml.dump(content, sort_keys=True)
    return hashlib.sha256(yaml_str.encode()).hexdigest()[:16]


def find_pillar_for_gad(gad_num, heiligtum):
    """Find which pillar a GAD number belongs to."""
    # Check extended ranges first (more specific)
    for name, config in heiligtum.get("extended_ranges", {}).items():
        r = config["range"]
        if r[0] <= gad_num <= r[1]:
            return name, "extended"

    # Check main pillars
    for name, config in heiligtum.get("pillars", {}).items():
        r = config["range"]
        if r[0] <= gad_num <= r[1]:
            return name, "pillar"

    return None, None


def verify(heiligtum_path, index_path):
    """Verify GAD_INDEX against HEILIGTUM."""
    heiligtum = load_yaml(heiligtum_path)
    index = load_yaml(index_path)

    errors = []
    warnings = []
    info = []

    # Check seal (if not UNSIGNED)
    stored_hash = heiligtum.get("meta", {}).get("seal_hash", "")
    if stored_hash != "UNSIGNED":
        computed = compute_seal_hash(heiligtum)
        if stored_hash != computed:
            errors.append(f"SEAL BROKEN! Expected {stored_hash}, got {computed}")

    # Check each GAD in index
    orphans = []
    undocumented = []
    legacy_refs = 0

    for gad_id, data in index.get("gads", {}).items():
        # Extract number
        import re

        match = re.search(r"\d+", gad_id)
        if not match:
            continue
        gad_num = int(match.group())

        # Find pillar
        pillar, pillar_type = find_pillar_for_gad(gad_num, heiligtum)

        if pillar is None:
            orphans.append(f"{gad_id} ({data['refs']} refs)")
        elif pillar == "LEGACY":
            legacy_refs += data["refs"]
        elif not data.get("documented", False):
            undocumented.append(f"{gad_id} → {pillar} ({data['refs']} refs)")

    # Report orphans (ERROR)
    if orphans:
        errors.append("ORPHAN GADs (not in any pillar):")
        for o in orphans[:10]:
            errors.append(f"  - {o}")
        if len(orphans) > 10:
            errors.append(f"  ... and {len(orphans) - 10} more")

    # Report undocumented (WARNING)
    if undocumented:
        warnings.append("UNDOCUMENTED GADs (in pillar but no .md):")
        for u in undocumented[:10]:
            warnings.append(f"  - {u}")
        if len(undocumented) > 10:
            warnings.append(f"  ... and {len(undocumented) - 10} more")

    # Report legacy (INFO)
    if legacy_refs > 0:
        info.append(f"LEGACY refs: {legacy_refs} (should decrease over time)")

    # Check EPICs
    for pillar_name, config in heiligtum.get("pillars", {}).items():
        epic = config.get("epic")
        if epic and epic in index.get("gads", {}):
            if not index["gads"][epic].get("documented", False):
                warnings.append(f"EPIC {epic} ({pillar_name}) not documented!")

    return errors, warnings, info


def main():
    base = Path("docs/architecture")
    heiligtum_path = base / "HEILIGTUM.yaml"
    index_path = base / "GAD_INDEX.yaml"

    if not heiligtum_path.exists():
        print("ERROR: HEILIGTUM.yaml not found!")
        sys.exit(1)

    if not index_path.exists():
        print("ERROR: GAD_INDEX.yaml not found!")
        print("Run: python docs/architecture/scripts/generate_gad_index.py")
        sys.exit(1)

    print("=" * 60)
    print("HEILIGTUM VERIFICATION")
    print("=" * 60)
    print()

    errors, warnings, info = verify(heiligtum_path, index_path)

    if errors:
        print("❌ ERRORS (require HIL attention):")
        for e in errors:
            print(f"   {e}")
        print()

    if warnings:
        print("⚠️  WARNINGS:")
        for w in warnings:
            print(f"   {w}")
        print()

    if info:
        print("ℹ️  INFO:")
        for i in info:
            print(f"   {i}")
        print()

    if not errors and not warnings:
        print("✅ All GADs verified against HEILIGTUM")
        print()

    # Summary
    print("=" * 60)
    if errors:
        print("RESULT: FAILED - HIL action required")
        sys.exit(1)
    elif warnings:
        print("RESULT: PASSED with warnings")
        sys.exit(0)
    else:
        print("RESULT: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
