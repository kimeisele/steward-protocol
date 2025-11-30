#!/usr/bin/env python3
"""
Agent Manifest Verification - CI/CD Script

Verifies that all system agents have:
1. STEWARD.md identity file
2. steward.json manifest
3. Valid JSON in manifest

Extracted from inline YAML script for maintainability.
"""
import sys
import json
from pathlib import Path


def check_steward_md_files():
    """Check all system agents have STEWARD.md"""
    print("Checking all system agents have STEWARD.md...")
    agent_dirs = Path("steward/system_agents").glob("*/")
    missing = 0

    for agent_dir in agent_dirs:
        if not agent_dir.is_dir():
            continue
        agent = agent_dir.name
        steward_md = agent_dir / "STEWARD.md"

        if not steward_md.exists():
            print(f"❌ Missing: {agent}/STEWARD.md")
            missing += 1
        else:
            print(f"✅ Found: {agent}/STEWARD.md")

    if missing > 0:
        print(f"\n❌ FAIL: {missing} agents missing STEWARD.md")
        return False
    else:
        print("\n✅ PASS: All agents have STEWARD.md")
        return True


def check_steward_json_files():
    """Check all system agents have steward.json"""
    print("\nChecking all system agents have steward.json...")
    agent_dirs = Path("steward/system_agents").glob("*/")
    missing = 0

    for agent_dir in agent_dirs:
        if not agent_dir.is_dir():
            continue
        agent = agent_dir.name
        steward_json = agent_dir / "steward.json"

        if not steward_json.exists():
            print(f"❌ Missing: {agent}/steward.json")
            missing += 1
        else:
            print(f"✅ Found: {agent}/steward.json")

    if missing > 0:
        print(f"\n❌ FAIL: {missing} agents missing steward.json")
        return False
    else:
        print("\n✅ PASS: All agents have steward.json")
        return True


def validate_manifest_json():
    """Validate steward.json syntax"""
    print("\nValidating steward.json syntax...")
    manifests = Path("steward/system_agents").glob("*/steward.json")
    invalid = 0

    for manifest in manifests:
        agent = manifest.parent.name
        try:
            with open(manifest) as f:
                json.load(f)
            print(f"✅ Valid JSON: {agent}/steward.json")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {agent}/steward.json - {e}")
            invalid += 1

    if invalid > 0:
        print(f"\n❌ FAIL: {invalid} manifests have invalid JSON")
        return False
    else:
        print("\n✅ PASS: All manifests are valid JSON")
        return True


if __name__ == "__main__":
    results = []
    results.append(check_steward_md_files())
    results.append(check_steward_json_files())
    results.append(validate_manifest_json())

    if all(results):
        print("\n✅ All agent manifest checks passed")
        sys.exit(0)
    else:
        print("\n❌ Some agent manifest checks failed")
        sys.exit(1)
