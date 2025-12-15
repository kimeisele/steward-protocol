#!/usr/bin/env python3
"""
OPUS-076: LIVE FIRE VERIFICATION
We don't trust return values. We verify side effects.
"""

import os
import sys
from pathlib import Path

# Add root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from vibe_core.kernel_impl import RealVibeKernel

TEST_FILE = "LIVE_FIRE_TEST.txt"
TEST_CONTENT = "OPUS-076: NO PUSSY MODE ACTIVE. REALITY ALTERED."


def main():
    print("🔥 INITIALIZING LIVE FIRE TEST...")

    # 1. Clean up potential residue
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        print("   (Cleaned up old test artifact)")

    # 2. Boot Kernel (Minimal)
    # We use RealVibeKernel as typically used in CLI
    kernel = RealVibeKernel(ledger_path=Path("data/vibe_ledger_test.db"))
    kernel.boot()
    print("✅ Kernel Booted.")

    # 3. Check Envoy
    envoy = getattr(kernel, "envoy", None)
    if not envoy:
        # Try getting plugin by ID
        envoy = kernel.get_plugin("envoy")

    if not envoy:
        print("❌ CRITICAL: Envoy plugin missing!")
        sys.exit(1)

    print(f"   Envoy found: {envoy}")

    # 4. Construct Intent (The "Bomb")
    intent = {
        "id": "live_fire_001",
        "action": "write_file",  # Must match a registered FileTool action
        "params": {"path": TEST_FILE, "content": TEST_CONTENT},
        "confidence": 1.0,  # Bypass Manas hesitation
    }

    # 5. Fire via Envoy (The Hand)
    # We deliberately call execute_mission directly to verify the Hand's capability
    # independent of Manas routing logic, though Manas calls this same method.
    print(f"🚀 Firing intent: {intent['action']} -> {TEST_FILE}")

    # Verify execute_mission signature compliance
    result = envoy.execute_mission(intent)

    # 6. Verify Reality
    print(f"📊 Execution Result: {result.get('status')}")
    print(f"   Details: {result}")

    if os.path.exists(TEST_FILE):
        with open(TEST_FILE, "r") as f:
            content = f.read()

        if content == TEST_CONTENT:
            print("\n🎉 SUCCESS: REALITY ALTERED.")
            print(f"   File created: {TEST_FILE}")
            print(f"   Content verified: '{content}'")

            # Cleanup
            os.remove(TEST_FILE)
            sys.exit(0)
        else:
            print("\n❌ FAILURE: File created but content wrong.")
            print(f"   Expected: {TEST_CONTENT}")
            print(f"   Got: {content}")
            sys.exit(1)
    else:
        print("\n❌ FAILURE: File was NOT created on disk.")
        print("   Envoy claimed execution, but reality disagrees.")
        sys.exit(1)


if __name__ == "__main__":
    main()
