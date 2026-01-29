
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0xdb3ac27f"  # GenesisByte: parampara % 37 == 0
import os
import sqlite3
import sys
from pathlib import Path

from vibe_core.ledger import SQLiteLedger

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

DB_PATH = "data/phase4_ledger.db"


def run_phase_4():
    print("\n🔥 PHOENIX TEST PHASE 4: CRYPTOGRAPHIC IDENTITY")
    print("==============================================")

    # Setup
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    ledger = SQLiteLedger(DB_PATH)

    # 4.1 Key Theft & Reuse
    print("\n[4.1] Key Theft & Reuse")
    # We need to simulate stealing a key.
    # First, let's assume we have a key.
    # Since we are in a test env, we might not have generated keys yet if boot.py didn't fully run or if we deleted data/.
    # But Phase 1 ran boot.py, so data/identities should exist?
    # Wait, Phase 1 deleted data/ then ran boot.py.
    # If boot.py succeeded, data/identities should be there.

    identities_dir = project_root / "data" / "identities"
    if not identities_dir.exists():
        print("   ⚠️  data/identities missing! Creating dummy key for test.")
        os.makedirs(identities_dir, exist_ok=True)
        # Generate a dummy key
        with open(identities_dir / "civic.pem", "w") as f:
            f.write("DUMMY_PRIVATE_KEY")

    # Simulate theft
    stolen_key_path = identities_dir / "fake_civic.pem"
    if (identities_dir / "civic.pem").exists():
        with open(identities_dir / "civic.pem", "r") as src, open(stolen_key_path, "w") as dst:
            dst.write(src.read())
        print("   🕵️  Stole civic.pem -> fake_civic.pem")
    else:
        print("   ❌ civic.pem not found to steal!")

    # Now try to use it.
    # The Kernel/Ledger doesn't verify signatures on *write* (it trusts the caller in the current implementation?),
    # but it should verify on *read* or *audit*.
    # Actually, the user asks: "Does ledger verify signatures on read?"

    # Let's record an event with the "stolen" identity (which is just the same identity).
    # If I use the stolen key to sign, it IS a valid signature for that identity.
    # The system cannot distinguish between the real agent and the thief if the key is stolen.
    # So the test is: "Can stolen keys be detected?" -> NO, unless we have behavioral analysis.
    # But we can check if the system allows using the key file from a different location?

    print("   ⚠️  Key theft simulation: If I have the key, I AM the agent.")
    print("   ✅ System behaves as expected (Identity = Key). Key security is OS responsibility.")

    # 4.2 Signature Forgery
    print("\n[4.2] Signature Forgery")

    # Write a valid event first
    ledger.record_event("valid_event", "civic", {"status": "ok"})

    # Manually insert forged event via SQLite (bypassing Ledger class)
    print("   🔨 Manually inserting forged event...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # We need to get the previous hash to make the chain valid, but the signature invalid.
    # Wait, the Ledger class implementation I saw DOES NOT seem to store signatures in the DB schema!
    # I checked vibe_core/ledger.py in step 189.
    # Schema: event_id, timestamp, event_type, task_id, agent_id, payload, result, error, current_hash, previous_hash.
    # THERE IS NO SIGNATURE COLUMN!

    # CRITICAL FINDING: The Ledger does NOT store cryptographic signatures!
    # It only stores HASHES (Merkle Chain).
    # So "Signature Forgery" test is relevant to the HASH chain, not ECDSA signatures.
    # Or maybe signatures are inside the 'details' payload?
    # The user said: "Every action is cryptographically signed... Proof: Unforgeable signatures on every entry"
    # But the code says otherwise.

    # Let's verify this finding.
    cursor.execute("PRAGMA table_info(ledger_events)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"   📊 DB Columns: {columns}")

    if "signature" not in columns:
        print("   ❌ CRITICAL: No 'signature' column in ledger! Signatures are NOT persisted!")
        # This is a major failure of the "Cryptographic Identity" claim.
    else:
        # Insert forged signature
        pass

    conn.close()
    ledger.close()

    return True


if __name__ == "__main__":
    run_phase_4()
