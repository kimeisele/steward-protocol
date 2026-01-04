#!/usr/bin/env python3
"""
Comprehensive verification script for BLOCKER #0: Phoenix Config Integration
Checks all 13 system agents for proper config parameter and assignment.
"""

import ast
import os
import sys
from pathlib import Path

# Discover project root dynamically
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent.parent  # scripts/verification -> project root

# List of all 13 system agents
AGENTS = [
    "herald",
    "civic",
    "science",
    "forum",
    "engineer",
    "watchman",
    "envoy",
    "archivist",
    "auditor",
    "chronicle",
    "supreme_court",
    "scribe",
    "oracle",
]


def verify_agent(agent_name: str) -> dict:
    """Verify a single agent has proper config integration."""
    agent_path = _project_root / "vibe_core" / "cartridges" / "system" / agent_name / "cartridge_main.py"

    result = {
        "agent": agent_name,
        "path": str(agent_path),
        "exists": agent_path.exists(),
        "syntax_valid": False,
        "has_config_param": False,
        "has_self_config": False,
        "has_config_import": False,
        "errors": [],
    }

    if not agent_path.exists():
        result["errors"].append(f"File not found: {agent_path}")
        return result

    try:
        with open(agent_path, "r") as f:
            content = f.read()

        # Check for syntax errors
        try:
            tree = ast.parse(content)
            result["syntax_valid"] = True
        except SyntaxError as e:
            result["errors"].append(f"Syntax error: {e}")
            return result

        # Check for config import
        result["has_config_import"] = "from vibe_core.config import" in content
        if not result["has_config_import"]:
            result["errors"].append("Missing: from vibe_core.config import ...")

        # Check for config parameter in __init__
        result["has_config_param"] = "config: Optional[" in content or "config=" in content
        if not result["has_config_param"]:
            result["errors"].append("Missing: config parameter in __init__")

        # Check for self.config assignment
        result["has_self_config"] = "self.config = config" in content
        if not result["has_self_config"]:
            result["errors"].append("Missing: self.config = config or ...")

    except Exception as e:
        result["errors"].append(f"Error reading file: {e}")

    return result


def main():
    """Verify all agents and report results."""
    print("=" * 80)
    print("BLOCKER #0 VERIFICATION - Phoenix Config Integration")
    print("=" * 80)
    print()

    results = []
    for agent_name in AGENTS:
        result = verify_agent(agent_name)
        results.append(result)

    # Print detailed results
    for result in results:
        status = (
            "✅ PASS"
            if (
                result["syntax_valid"]
                and result["has_config_param"]
                and result["has_self_config"]
                and result["has_config_import"]
            )
            else "❌ FAIL"
        )
        print(f"{status}  {result['agent']:20} ({result['path']})")

        if result["errors"]:
            for error in result["errors"]:
                print(f"      → {error}")
        print()

    # Summary
    passed = sum(
        1
        for r in results
        if (r["syntax_valid"] and r["has_config_param"] and r["has_self_config"] and r["has_config_import"])
    )
    total = len(results)

    print("=" * 80)
    print(f"SUMMARY: {passed}/{total} agents passed verification")
    print("=" * 80)

    # Details
    print(f"✅ Syntax Valid:      {sum(1 for r in results if r['syntax_valid'])}/{total}")
    print(f"✅ Config Import:     {sum(1 for r in results if r['has_config_import'])}/{total}")
    print(f"✅ Config Parameter:  {sum(1 for r in results if r['has_config_param'])}/{total}")
    print(f"✅ Self Config Assign: {sum(1 for r in results if r['has_self_config'])}/{total}")
    print()

    if passed == total:
        print("🎉 All agents passed BLOCKER #0 verification!")
        return 0
    else:
        print(f"⚠️  {total - passed} agent(s) failed verification")
        return 1


if __name__ == "__main__":
    sys.exit(main())
