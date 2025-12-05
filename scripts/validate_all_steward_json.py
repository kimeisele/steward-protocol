#!/usr/bin/env python3
"""
Validate ALL steward.json files in the repo.
Check if they have required fields and proper structure.
"""

import json
import sys
from pathlib import Path


def validate_manifest(path):
    """Validate a single steward.json file."""
    try:
        with open(path, "r") as f:
            data = json.load(f)

        agent_name = path.parent.name

        # Check for required fields
        if "agent" not in data:
            return (agent_name, "❌ INVALID", "Missing 'agent' section")

        agent = data["agent"]

        if "id" not in agent:
            return (agent_name, "❌ INVALID", "Missing agent.id")

        if "name" not in agent:
            return (agent_name, "⚠️ PARTIAL", "Missing agent.name")

        if "capabilities" not in data:
            return (agent_name, "⚠️ PARTIAL", "Missing capabilities section")

        capabilities = data["capabilities"]

        if "operations" not in capabilities:
            return (agent_name, "⚠️ PARTIAL", f"Missing operations (id={agent['id']})")

        ops = capabilities["operations"]
        if not isinstance(ops, list) or len(ops) == 0:
            return (agent_name, "⚠️ PARTIAL", f"Empty operations (id={agent['id']})")

        # Check operations structure
        for op in ops:
            if not isinstance(op, dict):
                return (
                    agent_name,
                    "⚠️ PARTIAL",
                    f"Invalid operation structure (id={agent['id']})",
                )
            if "name" not in op:
                return (
                    agent_name,
                    "⚠️ PARTIAL",
                    f"Operation missing 'name' (id={agent['id']})",
                )

        return (agent_name, "✅ VALID", f"id={agent['id']}, ops={len(ops)}")

    except json.JSONDecodeError:
        return (agent_name, "❌ INVALID", "JSON parse error")
    except Exception as e:
        return (agent_name, "❌ INVALID", f"Error: {e}")


def main():
    # Find all steward.json files
    paths = list(Path("vibe_core/cartridges/system").rglob("steward.json"))
    paths.extend(Path("vibe_core/cartridges/agent_city").rglob("steward.json"))

    # Validate each
    results = []
    for path in sorted(paths):
        result = validate_manifest(path)
        results.append(result)

    # Print results
    valid_count = 0
    partial_count = 0
    invalid_count = 0

    print("=" * 70)
    print("STEWARD.JSON VALIDATION REPORT")
    print("=" * 70)
    print()

    for name, status, msg in results:
        print(f"{status:12} {name:20} {msg}")
        if "✅" in status:
            valid_count += 1
        elif "⚠️" in status:
            partial_count += 1
        else:
            invalid_count += 1

    print()
    print("=" * 70)
    print(f"✅ VALID:   {valid_count}")
    print(f"⚠️ PARTIAL: {partial_count}")
    print(f"❌ INVALID: {invalid_count}")
    print(f"📊 TOTAL:   {len(results)}")
    print("=" * 70)

    return 0 if invalid_count == 0 and partial_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
