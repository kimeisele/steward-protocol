# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x995c7463"  # GenesisByte: parampara % 37 == 0
import json
import os
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vibe_core.ledger import SQLiteLedger

DB_PATH = "data/test_ledger.db"


def verify_persistence():
    print("\n💾 Verifying Persistence & Auditability...")

    # Clean up previous test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # 1. Create and Write
    print("   Creating ledger and recording events...")
    ledger = SQLiteLedger(DB_PATH)

    event_id_1 = ledger.record_event("TEST_EVENT", "tester", {"data": "value1"})
    event_id_2 = ledger.record_event("TEST_EVENT", "tester", {"data": "value2"})

    ledger.close()

    # 2. Re-open and Verify
    print("   Re-opening ledger to verify persistence...")
    ledger = SQLiteLedger(DB_PATH)
    events = ledger.get_all_events()

    if len(events) == 2:
        print(f"   ✅ Data persisted (Found {len(events)} events)")
    else:
        print(f"   ❌ Data lost! Found {len(events)} events")

    # 3. Verify Integrity
    print("   Verifying chain integrity...")
    integrity = ledger.verify_chain_integrity()
    if not integrity["corrupted"]:
        print("   ✅ Chain integrity verified")
    else:
        print("   ❌ Chain integrity check failed on clean data")

    ledger.close()

    # 4. Tamper Test
    print("   Attempting tampering (modifying historical event)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Modify the first event's payload without updating hash
    cursor.execute(
        "UPDATE ledger_events SET payload = ? WHERE event_id = ?", (json.dumps({"data": "TAMPERED"}), event_id_1)
    )
    conn.commit()
    conn.close()

    # 5. Verify Detection
    print("   Verifying tampering detection...")
    ledger = SQLiteLedger(DB_PATH)
    integrity = ledger.verify_chain_integrity()

    if integrity["corrupted"]:
        print(f"   ✅ Tampering detected! ({len(integrity['corruptions'])} corruptions found)")
        # print(integrity["corruptions"])
    else:
        print("   ❌ Tampering NOT detected!")

    # Clean up
    ledger.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


if __name__ == "__main__":
    try:
        verify_persistence()
        print("\n✨ Phase 3 Verification Complete")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback

        traceback.print_exc()
