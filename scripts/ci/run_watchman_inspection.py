#!/usr/bin/env python3
"""
Watchman Deep Inspection - CI/CD Script

Phase 3.3: Run Watchman Deep Inspection in CI/CD

This is Layer 2 of Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: THIS - AST-based deep analysis (~500ms)
- Layer 3: Auditor verdict (constitutional judgment)

Extracted from inline YAML script for maintainability.
"""

import json
import sys
from pathlib import Path

from steward.system_agents.watchman.cartridge_main import WatchmanCartridge
from vibe_core.agent_interface import AgentSystemInterface
from vibe_core.kernel_impl import RealVibeKernel

print("⚔️  Initializing Watchman...")
kernel = RealVibeKernel()
watchman = WatchmanCartridge()
watchman.system = AgentSystemInterface(kernel, "watchman")

print("🔬 Running Deep Inspection (AST-based analysis)...")
result = watchman.run_deep_inspection()

# Save full report
report_path = Path("watchman_report.json")
report_path.write_text(json.dumps(result, indent=2))
print(f"📊 Full report saved: {report_path}")

# Print summary
print("\n" + "=" * 70)
print("WATCHMAN DEEP INSPECTION SUMMARY")
print("=" * 70)
print(f"Status: {result['status']}")
print(f"Total violations: {result['total_violations']}")
print(f"Critical violations: {result['critical_count']}")

if result["total_violations"] > 0:
    print("\nViolations by agent:")
    for agent_id, count in result["report"]["by_agent"].items():
        print(f"  • {agent_id}: {count}")

    print("\nViolations by severity:")
    for severity, count in result["report"]["by_severity"].items():
        if count > 0:
            print(f"  • {severity}: {count}")

# Determine exit code
if result["should_fail_build"]:
    print("\n❌ BUILD FAILED - Critical violations detected")
    print("\nTo fix:")
    print("  1. Review violations in the uploaded artifact")
    print("  2. Use agent.system.get_sandbox_path() instead of Path('data/...')")
    print("  3. Remove any requirements.txt files")
    print("  4. See Phase 2 migration examples (Herald, Forum, Civic)")
    sys.exit(1)
elif result["total_violations"] > 0:
    print("\n⚠️  BUILD WARNING - Non-critical violations detected")
    print("Consider addressing these in a future PR")
    sys.exit(0)
else:
    print("\n✅ BUILD PASSED - All agents compliant")
    sys.exit(0)
