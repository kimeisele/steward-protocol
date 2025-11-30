#!/usr/bin/env python3
"""
Verification Script - HIL Assistant (VAD Layer)
Tests the 'next_action' command on the EnvoyCartridge.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from envoy.cartridge_main import EnvoyCartridge

from vibe_core import Task

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("VERIFICATION")


def main():
    print("\n" + "=" * 60)
    print("🧠 VERIFICATION: HIL Assistant (VAD Layer)")
    print("=" * 60 + "\n")

    # 1. Initialize Envoy
    envoy = EnvoyCartridge()

    print("✅ System Initialized.\n")

    # 2. Test 'next_action' Command
    print("-" * 40)
    print("🤖 TESTING: 'next_action' Command")
    print("-" * 40)

    task = Task(
        agent_id="envoy",
        payload={
            "command": "next_action",
            "args": {},  # Should auto-load the latest G.A.P. report
        },
    )

    result = envoy.process(task)

    print("\n📝 Result:\n")
    if result.get("status") == "success":
        print(result.get("summary"))
        print("\n✅ VERIFICATION PASSED: Strategic summary generated.")
    else:
        print(f"❌ VERIFICATION FAILED: {result.get('error')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
