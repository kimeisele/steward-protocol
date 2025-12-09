"""
Verify Doctor Plugin.
Tests if 'system:doctor' is discovered and runnable.
"""

import io
import os
import sys
from contextlib import redirect_stdout

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.cli.unified_cli import UnifiedCLI


def verify_doctor():
    print("🔍 VERIFYING DOCTOR PLUGIN...")

    cli = UnifiedCLI()

    # 1. Verification: Discovery
    print("\n[TEST 1] Command Discovery")
    caps = cli.get_capabilities()

    doctor_cmd = None
    for cmd in caps["plugin_commands"]:
        if cmd["name"] == "doctor" and cmd["namespace"] == "system":
            doctor_cmd = cmd
            break

    if not doctor_cmd:
        print("❌ FAILED: 'system:doctor' not found in capabilities.")
        # Print available for debugging
        print("Available:", [f"{c['namespace']}:{c['name']}" for c in caps["plugin_commands"]])
        sys.exit(1)

    print("✅ Found 'system:doctor' command.")

    # 2. Verification: Execution
    print("\n[TEST 2] Execution (OFFLINE)")

    # Capture stdout
    f = io.StringIO()
    # We might need to map 'system:doctor' to the actual command name used by CLI
    # Use the name found in discovery usually 'namespace:name' but depends on protocol.py

    # Let's try to infer the key text from protocol logic or just guess 'system:doctor'
    cmd_key = "system:doctor"

    with redirect_stdout(f):
        # Pass the full command key as argument 0
        exit_code = cli.run([cmd_key])

    output = f.getvalue()

    # Note: Plugin handler returns dict, UnifiedCLI renders it.
    # We should see dict output or rendered text.

    print(f"Output preview: {output[:100]}...")

    if exit_code != 0:
        print(f"❌ FAILED: Exit code {exit_code}")
        sys.exit(1)

    print("✅ Doctor executed successfully.")


if __name__ == "__main__":
    verify_doctor()
