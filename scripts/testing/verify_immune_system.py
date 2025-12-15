#!/usr/bin/env python3
"""
OPUS-077: IMMUNE SYSTEM VERIFICATION (The Watchman)
We write broken code and expect it to be gone.
"""

import os
import sys
from pathlib import Path

# Add root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from vibe_core.kernel_impl import RealVibeKernel

TEST_FILE = "REFLEX_TEST_BROKEN.py"
TEST_CONTENT = "def broken_code(:\n    print('This calls for a rollback')"


def main():
    print("🧬 INITIALIZING IMMUNE SYSTEM TEST...")

    # 1. Clean up potential residue
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        print("   (Cleaned up old test artifact)")

    # 2. Boot Kernel
    kernel = RealVibeKernel(ledger_path=Path("data/vibe_ledger_test.db"))
    kernel.boot()
    print("✅ Kernel Booted.")

    # 3. Check Envoy
    envoy = getattr(kernel, "envoy", None) or kernel.get_plugin("envoy")
    if not envoy:
        print("❌ CRITICAL: Envoy plugin missing!")
        sys.exit(1)

    print("💉 INJECTING MALFORMED CODE (The Virus)...")

    # 4. Construct Broken Intent
    intent = {
        "id": "virus_001",
        "action": "write_file",
        "params": {"path": TEST_FILE, "content": TEST_CONTENT},
        "confidence": 1.0,
    }

    # 5. Fire via Envoy
    # This should succeed in "writing", but then trigger "on_tool_executed",
    # which calls Pratyaya -> Syntax Check -> Fail -> Rollback.
    print(f"🚀 Firing intent: write broken {TEST_FILE}")
    result = envoy.execute_mission(intent)

    print(f"📊 Execution returned: {result.get('status')}")

    # 6. Verify Reality (Immune Response)
    if os.path.exists(TEST_FILE):
        print("❌ FAILURE: The broken file PERSISTS.")
        print("   The Immune System failed to kill the virus.")
        sys.exit(1)
    else:
        print("🎉 SUCCESS: The broken file IS GONE.")
        print("   Reflex Action confirmed: Syntax Error -> Rollback/Delete.")
        sys.exit(0)


if __name__ == "__main__":
    main()
