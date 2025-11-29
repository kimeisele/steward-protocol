#!/usr/bin/env python3
"""
FIX STEWARD.JSON SCHEMA - Convert to Discoverer-compatible format

Problem: Passport Office created steward.json files with schema:
  { "identity": { "agent_id": "...", ... }, ... }

But Discoverer expects:
  { "agent": { "id": "...", ... }, ... }

This script converts ALL steward.json files to the working schema.
"""

import json
import sys
from pathlib import Path


def convert_manifest(manifest_path: Path) -> bool:
    """
    Convert steward.json from new schema to old (working) schema.

    Returns True if converted, False if already correct or error.
    """
    try:
        with open(manifest_path, "r") as f:
            data = json.load(f)

        # Check if already in old schema
        if "agent" in data and "id" in data["agent"]:
            print(f"   ✅ Already correct: {manifest_path.parent.name}")
            return False

        # Check if in new schema
        if "identity" not in data or "agent_id" not in data["identity"]:
            print(f"   ⚠️  Unknown schema: {manifest_path.parent.name}")
            return False

        # Convert from new schema to old schema
        identity = data.get("identity", {})
        specs = data.get("specs", {})
        capabilities = data.get("capabilities", {})
        governance = data.get("governance", {})

        # Build old schema
        old_schema = {
            "steward_version": "1.0.0",
            "agent": {
                "id": identity.get("agent_id", "unknown"),
                "name": identity.get("name", "Unknown"),
                "version": specs.get("version", "1.0.0"),
                "class": "system_service",  # or extract from domain
                "specialization": specs.get("domain", "GENERAL"),
                "status": "active",
            },
            "credentials": {
                "mandate": specs.get("description", "System agent"),
                "constraints": [],
                "prime_directive": "Serve the system",
            },
            "capabilities": {
                "interfaces": ["kernel"],
                "operations": capabilities.get("operations", []),
            },
        }

        # Add governance if present
        if governance:
            old_schema["governance"] = governance

        # Write back
        with open(manifest_path, "w") as f:
            json.dump(old_schema, f, indent=2)

        print(f"   ✅ Converted: {manifest_path.parent.name}")
        return True

    except Exception as e:
        print(f"   ❌ Error converting {manifest_path}: {e}")
        return False


def main():
    """Convert all steward.json files in system_agents/"""

    base_path = Path("steward/system_agents")

    if not base_path.exists():
        print(f"❌ Path not found: {base_path}")
        return 1

    print("🔧 Converting steward.json files to Discoverer-compatible schema...")
    print()

    converted_count = 0
    already_correct = 0
    error_count = 0

    for manifest_path in base_path.rglob("steward.json"):
        result = convert_manifest(manifest_path)
        if result is True:
            converted_count += 1
        elif result is False:
            already_correct += 1
        else:
            error_count += 1

    print()
    print("=" * 60)
    print(f"✅ Converted: {converted_count}")
    print(f"✅ Already correct: {already_correct}")
    print(f"❌ Errors: {error_count}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
