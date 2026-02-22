"""
TEST BALARAMA SEAL (Body/Soul Separation)
=========================================

Verifies:
1.  StateService.save() writes FILE (Body) and updates MAHASTATE (Soul).
2.  MahaState.seal() is ASYNC (marks dirty, doesn't flush immediately).
3.  MahaState.validate() detects MATCH vs DRIFT.
"""

import json
import logging
import shutil
import sys
import time
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path.cwd()))

# Configure logging to see StateService/MahaState errors
logging.basicConfig(level=logging.DEBUG)

from vibe_core.mahamantra.substrate.maha_state import get_maha_state
from vibe_core.state.state_service import get_state_service


@pytest.mark.xfail(
    reason="Standalone script using sys.exit() — needs rewrite as proper pytest test; config section 'balarama_test' missing",
    strict=False,
)
def test_balarama_seal():
    print("🧪 Starting Balarama Seal Test...")

    workspace = Path.cwd()

    # 1. Setup
    service = get_state_service(workspace)
    maha = get_maha_state(workspace)

    # Reset MahaState to clean slate
    maha._entries.clear()
    maha._dirty = False

    # 2. Save a Test File (Body Creation)
    filename = "balarama_test.json"
    data = {"mission": "protect_krishna", "weapon": "plough"}

    print(f"📝 Saving {filename} via StateService...")
    service.save(filename, data)

    # 3. Verify Body (File)
    file_path = service.state_root / filename
    if not file_path.exists():
        print("❌ FAIL: File not written to disk!")
        sys.exit(1)
    print("✅ Body: File exists on disk.")

    # DEBUG: Check contents
    print(f"DEBUG: MahaState Instance ID in Test: {id(maha)}")
    print(f"DEBUG: MahaState Entries keys: {list(maha._entries.keys())}")

    # 4. Verify Soul (MahaState Memory)
    seed = maha.get(filename)
    if seed is None:
        print(f"❌ FAIL: Seed not in MahaState memory! Entry missing for {filename}")
        # Try to force seal manually to see if it works
        print("DEBUG: Attempting manual seal from test...")
        maha.seal(filename, data)
        if maha.get(filename):
            print("DEBUG: Manual seal worked! Issue is in StateService call path.")
        else:
            print("DEBUG: Manual seal FAILED! Issue is in MahaState.seal itself.")

        sys.exit(1)
    print(f"✅ Soul: Seed is present in memory: {seed}")

    if not maha._dirty:
        print("❌ FAIL: MahaState should be dirty!")
        sys.exit(1)
    print("✅ Async: MahaState is marked dirty.")

    # 5. Flush Soul (Persistence)
    print("💾 Persisting MahaState...")
    maha.save()

    if maha._dirty:
        print("❌ FAIL: MahaState still dirty after save!")
        sys.exit(1)

    maha_state_path = workspace / ".vibe/state/mahamantra/maha_state.json"
    if not maha_state_path.exists():
        print("❌ FAIL: maha_state.json not created!")
        sys.exit(1)
    print("✅ Persistence: maha_state.json created.")

    # 6. Verify Validation (Match)
    print("🔍 Validating Match...")
    result = maha.validate(filename, data)
    if result != "MATCH":
        print(f"❌ FAIL: Expected MATCH, got {result}")
        sys.exit(1)
    print("✅ Validation: MATCH confirmed.")

    # 7. Simulate Drift (Atomicity Gap)
    print("⚡ Simulating Drift (Modifying Body only)...")
    drift_data = {"mission": "protect_krishna", "weapon": "club"}  # Changed weapon causing seed change

    # We cheat and write directly to disk to bypass StateService (simulating external edit or race condition)
    # Actually validate takes content, so we just pass new content to validate against old seed
    drift_result = maha.validate(filename, drift_data)

    if drift_result != "DRIFT":
        print(f"❌ FAIL: Expected DRIFT, got {drift_result}")
        sys.exit(1)
    print("✅ Validation: DRIFT detected correctly.")

    # 8. Reconciliation (The Healing)
    print("🚑 Simulating Reconciliation (Healing the Drift)...")
    # In a real scenario, this would happen on boot or via manual admin tool
    # We simply re-seal the authentic file (Body wins)
    maha.seal(filename, drift_data)

    # Verify Healing
    healed_result = maha.validate(filename, drift_data)
    if healed_result != "MATCH":
        print(f"❌ FAIL: Expected MATCH after healing, got {healed_result}")
        sys.exit(1)

    # Verify Persistence of Healed State
    maha.save()
    print("✅ Reconciliation: Drift healed and state persisted.")

    print("\n🎉 BALARAMA RESTORATION VERIFIED: Body/Soul separation + Drift Recovery confirmed.")


if __name__ == "__main__":
    try:
        test_balarama_seal()
    except Exception as e:
        print(f"\n💥 CRASH: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
