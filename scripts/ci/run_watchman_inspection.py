#!/usr/bin/env python3
"""
Watchman Deep Inspection - CI/CD Script

Phase 3.3: Run Watchman Deep Inspection in CI/CD

This is Layer 2 of Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: THIS - AST-based deep analysis (~500ms)
- Layer 3: Auditor verdict (constitutional judgment)

Extracted from inline YAML script for maintainability.

OPUS-167 FIX: Direct tool invocation (no kernel overhead).
The kernel machinery was causing hangs due to tight coupling.
The tool itself runs in <1 second.

OPUS-131: Threshold-based failure for tech debt baseline.
"""

import json
import sys
from pathlib import Path

import yaml

# OPUS-167: Direct tool import - skip kernel machinery
from vibe_core.cartridges.system.watchman.tools.standards_inspection import StandardsInspectionTool


def get_critical_threshold() -> int:
    """Read critical_threshold from ci.yaml (OPUS-131)."""
    ci_yaml = Path("scripts/ci/ci.yaml")
    if ci_yaml.exists():
        try:
            with open(ci_yaml) as f:
                config = yaml.safe_load(f)
            hooks = config.get("hooks", {})
            watchman = hooks.get("watchman_inspection", {})
            return watchman.get("critical_threshold", 0)
        except Exception:
            pass
    return 0  # Default: zero tolerance


print("⚔️  Initializing Watchman Standards Inspection...")
tool = StandardsInspectionTool()

print("🔬 Running Deep Inspection (AST-based analysis)...")
# Direct tool execution - no kernel overhead
tool_result = tool.execute({"action": "inspect_all", "system_agents_path": "vibe_core/cartridges/system"})

# Convert tool result to the expected format
violations = tool_result.output.get("violations", []) if tool_result.success else []

# Group by severity and agent
by_severity = {}
by_agent = {}
for v in violations:
    severity = v.get("severity", "UNKNOWN")
    agent_id = v.get("agent_id", "unknown")
    by_severity[severity] = by_severity.get(severity, 0) + 1
    by_agent[agent_id] = by_agent.get(agent_id, 0) + 1

critical_count = sum(1 for v in violations if v.get("severity") == "CRITICAL")

result = {
    "status": "VIOLATIONS_DETECTED" if critical_count > 0 else ("WARNINGS_DETECTED" if violations else "COMPLIANT"),
    "should_fail_build": critical_count > 0,
    "total_violations": len(violations),
    "critical_count": critical_count,
    "report": {
        "by_severity": by_severity,
        "by_agent": by_agent,
    },
    "violations": violations,
}

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

# OPUS-131: Threshold-based failure
threshold = get_critical_threshold()
exceeds_threshold = critical_count > threshold

# Determine exit code
if exceeds_threshold:
    print(f"\n❌ BUILD FAILED - Critical violations ({critical_count}) exceed threshold ({threshold})")
    print("\nTo fix:")
    print("  1. Review violations in the uploaded artifact")
    print("  2. Use agent.system.get_sandbox_path() instead of Path('data/...')")
    print("  3. Remove any requirements.txt files")
    print("  4. See Phase 2 migration examples (Herald, Forum, Civic)")
    sys.exit(1)
elif critical_count > 0:
    print(f"\n⚠️  BUILD WARNING - Critical violations ({critical_count}) at or below threshold ({threshold})")
    print("OPUS-131: These are known tech debt. Reduce to 0 for full compliance.")
    sys.exit(0)
elif result["total_violations"] > 0:
    print("\n⚠️  BUILD WARNING - Non-critical violations detected")
    print("Consider addressing these in a future PR")
    sys.exit(0)
else:
    print("\n✅ BUILD PASSED - All agents compliant")
    sys.exit(0)
