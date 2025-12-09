"""
GAD-000 Verification Script.

Verifies:
1. UnifiedCLI uses Inspector Pattern (get_capabilities).
2. 'steward capabilities' command outputs valid JSON.
3. Integration with SystemInspector is correct.
"""

import io
import json
import os
import sys
from contextlib import redirect_stdout

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.cli.unified_cli import UnifiedCLI


def verify_gad000():
    print("🔍 VERIFYING GAD-000 COMPLIANCE...")

    cli = UnifiedCLI()

    # 1. Test Inspector Integration
    print("\n[TEST 1] Inspector Pattern Integration")
    caps = cli.get_capabilities()

    if not caps.get("inspector_pattern"):
        print("❌ FAILED: 'inspector_pattern' flag missing from capabilities.")
        sys.exit(1)

    print("✅ Inspector Pattern active.")
    print(f"   Version: {caps['version']}")

    # 2. Test Command Output (JSON)
    print("\n[TEST 2] 'capabilities' Command (JSON)")

    # Capture stdout
    f = io.StringIO()
    with redirect_stdout(f):
        exit_code = cli.run(["capabilities"])

    output = f.getvalue()

    if exit_code != 0:
        print(f"❌ FAILED: Exit code {exit_code}")
        sys.exit(1)

    try:
        json_out = json.loads(output)
        if json_out.get("inspector_pattern") is not True:
            print("❌ FAILED: JSON output incorrect.")
            sys.exit(1)
        print("✅ JSON Output Valid.")
    except json.JSONDecodeError:
        print("❌ FAILED: Output is not valid JSON.")
        print(f"Output: {output}")
        sys.exit(1)

    print("\n✅ Verification Complete: GAD-000 Phase 1 PASS.")


if __name__ == "__main__":
    verify_gad000()
