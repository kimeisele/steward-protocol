#!/usr/bin/env python3
"""
MANIFEST VALIDATOR
==================
Validates all steward.json files against CARTRIDGE_SPEC.md requirements.

Usage:
    python docs/architecture/scripts/validate_manifests.py

Output:
    - All found steward.json files
    - Validation status per file
    - Missing required fields
    - Domain distribution
"""

import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Required fields per CARTRIDGE_SPEC.md
REQUIRED_FIELDS = {
    "identity": ["agent_id", "name"],
    "specs": ["version", "description", "domain"],
    "capabilities": ["operations"],
    "governance": ["compliance_level", "constitution_hash", "issued_at", "issuer"],
}

VALID_DOMAINS = [
    "GOVERNANCE",
    "INFRASTRUCTURE",
    "MEDIA",
    "RESEARCH",
    "ENGINEERING",
    "TESTING",
    "SYSTEM",
    "CORE",
    "INTERFACE",
    "SECURITY",
    "DATA_ETHICS",
    "OBSERVATION",
    "TEMPORAL",
    "META",
    "OUTREACH",
    "COMMUNITY",
    "OFFERINGS",
    "MAINTENANCE",
    "INTROSPECTION",
    "DOCUMENTATION",
    "TRADING",
    "SOCIAL",
    "PROMOTION",
    "JUSTICE",
    "DEMOCRACY",
    "HISTORY",
    "COMPLIANCE",
]


def find_manifests() -> list:
    """Find all steward.json files."""
    manifests = []

    # Search in known locations
    search_paths = [
        PROJECT_ROOT / "steward" / "system_agents",
        PROJECT_ROOT / "agent_city" / "registry",
        PROJECT_ROOT / "starter-packs",
    ]

    for search_path in search_paths:
        if search_path.exists():
            for manifest in search_path.rglob("steward.json"):
                manifests.append(manifest)

    return manifests


def validate_manifest(filepath: Path) -> dict:
    """Validate a single manifest file."""
    result = {
        "path": str(filepath.relative_to(PROJECT_ROOT)),
        "valid": True,
        "errors": [],
        "warnings": [],
        "data": None,
    }

    try:
        content = filepath.read_text()
        data = json.loads(content)
        result["data"] = data

        # Check required sections
        for section, fields in REQUIRED_FIELDS.items():
            if section not in data:
                result["errors"].append(f"Missing section: {section}")
                result["valid"] = False
                continue

            for field in fields:
                if field not in data[section]:
                    result["errors"].append(f"Missing {section}.{field}")
                    result["valid"] = False

        # Check domain validity
        if "specs" in data and "domain" in data["specs"]:
            domain = data["specs"]["domain"]
            if domain not in VALID_DOMAINS:
                result["warnings"].append(f"Unknown domain: {domain}")

        # Check operations
        if "capabilities" in data and "operations" in data["capabilities"]:
            ops = data["capabilities"]["operations"]
            if not ops or len(ops) == 0:
                result["warnings"].append("No operations defined")

        # Check constitution hash
        if "governance" in data:
            gov = data["governance"]
            if gov.get("constitution_hash") in [None, "", "null", "pending"]:
                result["warnings"].append("Constitution hash not set")

    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON: {e}")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error: {e}")

    return result


def main():
    print("=" * 70)
    print("MANIFEST VALIDATOR - steward.json Compliance Check")
    print("=" * 70)
    print()

    manifests = find_manifests()
    print(f"📦 Found {len(manifests)} steward.json files")
    print()

    results = []
    for m in manifests:
        results.append(validate_manifest(m))

    # Sort by validity
    valid = [r for r in results if r["valid"]]
    invalid = [r for r in results if not r["valid"]]

    # Valid manifests
    print(f"✅ VALID MANIFESTS ({len(valid)}):")
    print("-" * 70)
    for r in valid:
        agent_id = r["data"].get("identity", {}).get("agent_id", "unknown")
        domain = r["data"].get("specs", {}).get("domain", "unknown")
        warnings = f" ⚠️ {len(r['warnings'])} warnings" if r["warnings"] else ""
        print(f"   {agent_id:20} | {domain:15} | {r['path']}{warnings}")
    print()

    # Invalid manifests
    if invalid:
        print(f"❌ INVALID MANIFESTS ({len(invalid)}):")
        print("-" * 70)
        for r in invalid:
            print(f"\n   {r['path']}")
            for err in r["errors"]:
                print(f"      ❌ {err}")
        print()

    # Warnings
    warnings_count = sum(len(r["warnings"]) for r in results)
    if warnings_count > 0:
        print(f"⚠️ WARNINGS ({warnings_count}):")
        print("-" * 70)
        for r in results:
            if r["warnings"]:
                print(f"\n   {r['path']}")
                for w in r["warnings"]:
                    print(f"      ⚠️ {w}")
        print()

    # Domain distribution
    print("📊 DOMAIN DISTRIBUTION:")
    print("-" * 70)
    domains = defaultdict(list)
    for r in results:
        if r["data"]:
            domain = r["data"].get("specs", {}).get("domain", "UNKNOWN")
            agent_id = r["data"].get("identity", {}).get("agent_id", "unknown")
            domains[domain].append(agent_id)

    for domain, agents in sorted(domains.items()):
        print(f"   {domain}: {', '.join(agents)}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"   Valid:    {len(valid)}")
    print(f"   Invalid:  {len(invalid)}")
    print(f"   Warnings: {warnings_count}")
    print(f"   Domains:  {len(domains)}")


if __name__ == "__main__":
    main()
