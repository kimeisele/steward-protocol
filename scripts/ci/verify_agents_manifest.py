#!/usr/bin/env python3
"""
Agent Manifest Verification - CI/CD Script

Verifies that all system agents have STEWARD.md and steward.json.
Extracted from inline YAML for maintainability.
"""

import json
import sys
from pathlib import Path


def verify_manifests():
    print("📋 Verifying Agent Manifests (STEWARD.md & steward.json)...")
    agents_dir = Path("vibe_core/cartridges/system")
    errors = 0

    if not agents_dir.exists():
        print(f"❌ Directory not found: {agents_dir}")
        return False

    for agent_dir in [d for d in agents_dir.iterdir() if d.is_dir()]:
        agent_name = agent_dir.name

        # Check STEWARD.md
        if not (agent_dir / "STEWARD.md").exists():
            print(f"❌ {agent_name}: Missing STEWARD.md")
            errors += 1

        # Check steward.json
        json_path = agent_dir / "steward.json"
        if not json_path.exists():
            print(f"❌ {agent_name}: Missing steward.json")
            errors += 1
        else:
            # Validate JSON syntax
            try:
                with open(json_path, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ {agent_name}: Invalid JSON in steward.json - {e}")
                errors += 1

    if errors == 0:
        print("✅ All agents valid.")
        return True
    else:
        print(f"❌ Found {errors} manifest violations.")
        return False


if __name__ == "__main__":
    sys.exit(0 if verify_manifests() else 1)
