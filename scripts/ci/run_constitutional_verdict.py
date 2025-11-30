#!/usr/bin/env python3
"""
Constitutional Verdict - CI/CD Script

Runs the Auditor's constitutional verdict.
Extracted from inline YAML for maintainability.
"""

import sys
import json
from pathlib import Path
from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.auditor.cartridge_main import AuditorCartridge
from vibe_core.agent_interface import AgentSystemInterface
from vibe_core.scheduling.task import Task


def run_verdict():
    print("⚖️  Initializing Auditor for Constitutional Verdict...")
    try:
        kernel = RealVibeKernel()
        auditor = AuditorCartridge()
        auditor.system = AgentSystemInterface(kernel, "auditor")

        task = Task(agent_id="auditor", payload={"action": "constitutional_verdict"})
        verdict = auditor.render_constitutional_verdict(task)

        # Save artifact
        Path("auditor_verdict.json").write_text(json.dumps(verdict, indent=2))

        print(f"📜 Verdict: {verdict['verdict']}")

        if verdict.get("should_fail_build", False):
            print("❌ CONSTITUTIONAL VIOLATION DETECTED")
            return False

        print("✅ Constitution Uphold.")
        return True

    except Exception as e:
        print(f"❌ Fatal error running verdict: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if run_verdict() else 1)
