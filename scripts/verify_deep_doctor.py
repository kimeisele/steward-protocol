"""
Verify Doctor Deep Diagnostics.
Directly calls DoctorPlugin.cmd_doctor(deep=True) to test logic speed and correctness.
"""

import os
import sys

sys.path.append(os.getcwd())

from vibe_core.plugins.doctor.plugin_main import DoctorPlugin


def test_deep_scan():
    print("Running Doctor Deep Scan...")
    plugin = DoctorPlugin()
    report = plugin.cmd_doctor(deep=True)

    print(f"Status: {report['status']}")

    legacy_check = next((c for c in report["checks"] if c["check"] == "legacy_rot"), None)
    if not legacy_check:
        print("❌ FAILED: legacy_rot check missing")
        sys.exit(1)

    print(f"Scanned files: {legacy_check['scanned']}")
    print(f"Deprecated files: {legacy_check['deprecated_files']}")

    # We expect some deprecated files (at least cli/legacy.py)
    if legacy_check["deprecated_files"] > 0:
        print("✅ Deep Scan correctly identified deprecated code.")
    else:
        print("⚠️  WARNING: No deprecated code found (unexpected?)")

    if report["status"] == "ADVISORY":
        print("✅ Status correctly set to ADVISORY")
    else:
        print(f"❌ Status mismatch: {report['status']}")


if __name__ == "__main__":
    test_deep_scan()
