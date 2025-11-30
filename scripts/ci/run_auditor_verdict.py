#!/usr/bin/env python3
"""
Auditor Constitutional Verdict - CI/CD Script

Phase 3.4: Auditor Constitutional Verdict (Layer 3)

This is the final authority on code quality - constitutional judgment.
Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: Watchman (AST analysis) - catches architectural violations
- Layer 3: THIS - constitutional judgment (supreme authority)

Extracted from inline YAML script for maintainability.
"""
import sys
import json
from pathlib import Path

# Initialize kernel and load Auditor
from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.auditor.cartridge_main import AuditorCartridge

print("⚖️  Initializing Auditor...")
kernel = RealVibeKernel()
auditor = AuditorCartridge()

# Inject system interface (required for compliance checks)
from vibe_core.agent_interface import AgentSystemInterface
auditor.system = AgentSystemInterface(kernel, "auditor")

print("⚖️  Rendering Constitutional Verdict (Layer 3)...")

# Create task for constitutional verdict
from vibe_core.scheduling.task import Task
task = Task(
    agent_id="auditor",
    payload={"action": "constitutional_verdict"}
)

verdict = auditor.render_constitutional_verdict(task)

# Save full verdict
verdict_path = Path("auditor_verdict.json")
verdict_path.write_text(json.dumps(verdict, indent=2))
print(f"⚖️  Full verdict saved: {verdict_path}")

# Print summary
print("\n" + "="*70)
print("AUDITOR CONSTITUTIONAL VERDICT")
print("="*70)
print(f"Verdict: {verdict['verdict']}")
print(f"Total violations: {verdict['total_violations']}")

if verdict['total_violations'] > 0:
    print("\nViolations by severity:")
    for severity, count in verdict['by_severity'].items():
        if count > 0:
            print(f"  • {severity}: {count}")

    if verdict.get('by_article'):
        print("\nViolations by article:")
        for article, count in verdict['by_article'].items():
            print(f"  • {article}: {count}")

print(f"\nConstitution Hash: {verdict.get('constitutional_hash', 'N/A')}")

# Determine exit code
if verdict['should_fail_build']:
    print("\n❌ BUILD FAILED - Constitutional violations detected")
    print("\nThe Constitution is the supreme law. These violations cannot be ignored.")
    print("\nTo fix:")
    print("  1. Review violations in the uploaded artifact")
    print("  2. Ensure agents have steward.json and STEWARD.md")
    print("  3. Add logging/audit trails for accountability")
    print("  4. Implement VibeAgent protocol for interoperability")
    print("  5. See CONSTITUTION.md for full requirements")
    sys.exit(1)
elif verdict['total_violations'] > 0:
    print("\n⚠️  BUILD WARNING - Non-critical violations detected")
    print("Consider addressing these to improve constitutional alignment")
    sys.exit(0)
else:
    print("\n✅ BUILD PASSED - All agents uphold the Constitution")
    sys.exit(0)
