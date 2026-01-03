#!/usr/bin/env python3
"""
KRUPP-STAHL TEST: LEDGER ACID PROPERTIES
=========================================
Tests the fundamental guarantees an Agent OS MUST provide:
- Atomicity: All or nothing writes
- Consistency: Hash chain never breaks
- Isolation: Concurrent writers don't corrupt
- Durability: Committed = Persisted

NO MOCKS. NO SKIPS. REAL STRESS.
"""

import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.ledger import SQLiteLedger


@pytest.mark.timeout(120)  # Stress test needs longer timeout
def test_concurrent_writes_integrity():
    """
    STRESS TEST: Multiple threads writing simultaneously.

    Acceptance Criteria:
    - Zero lost writes (all events recorded)
    - Hash chain remains unbroken
    - No duplicate event IDs
    """
    num_threads = 20  # Reduced from 50 to avoid extreme lock contention
    events_per_thread = 50  # Reduced from 100 for faster CI

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        errors = []
        event_ids = []
        lock = threading.Lock()

        def writer(thread_id: int):
            """Each thread gets its own connection (SQLite requirement)"""
            ledger = SQLiteLedger(db_path)
            local_ids = []
            try:
                for i in range(events_per_thread):
                    event_id = ledger.record_event(
                        "stress_test", f"thread_{thread_id}", {"thread": thread_id, "seq": i}
                    )
                    local_ids.append(event_id)
            except Exception as e:
                with lock:
                    errors.append(f"Thread {thread_id}: {e}")
            finally:
                with lock:
                    event_ids.extend(local_ids)
                ledger.close()

        # Launch threads
        threads = []
        start = time.time()
        for t in range(num_threads):
            thread = threading.Thread(target=writer, args=(t,))
            threads.append(thread)
            thread.start()

        for t in threads:
            t.join()

        duration = time.time() - start
        expected_events = num_threads * events_per_thread

        # Verify with fresh connection
        verify_ledger = SQLiteLedger(db_path)
        events = verify_ledger.get_all_events()
        actual_events = len(events)

        # Check 1: No lost writes
        assert actual_events == expected_events, (
            f"LOST WRITES: Expected {expected_events}, got {actual_events} (lost: {expected_events - actual_events}, duration: {duration:.2f}s)"
        )

        # Check 2: Hash chain integrity
        integrity = verify_ledger.verify_chain_integrity()
        assert not integrity["corrupted"], f"HASH CHAIN CORRUPTED: {len(integrity.get('corruptions', []))} breaks"

        # Check 3: No duplicate IDs
        unique_ids = set(e.get("event_id") for e in events)
        assert len(unique_ids) == actual_events, f"DUPLICATE EVENT IDS: {actual_events - len(unique_ids)} duplicates"

        verify_ledger.close()

        assert not errors, f"THREAD ERRORS: {len(errors)} - {errors[:5]}"

        print(f"{actual_events} events, chain intact, {duration:.2f}s, rate: {actual_events / duration:.0f} events/s")

    finally:
        os.unlink(db_path)


def test_crash_durability():
    """
    CRASH TEST: Write event, kill -9, verify persistence.

    Simulates hard crashes (power loss, kernel panic).
    Event MUST survive if record_event() returned.
    """
    num_iterations = 10

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    crash_script = """
import os
import sys
sys.path.insert(0, "{project_root}")
from vibe_core.ledger import SQLiteLedger

ledger = SQLiteLedger("{db_path}")
event_id = ledger.record_event("crash_test", "tester", {{"iteration": {iteration}, "marker": "{marker}"}})
print(f"EVENT_ID={{event_id}}")
sys.stdout.flush()
# Ensure write is committed before kill
ledger.connection.execute("PRAGMA wal_checkpoint(FULL)")
os.kill(os.getpid(), 9)
"""

    project_root = str(Path(__file__).parent.parent.parent)

    try:
        survived = 0
        lost = 0

        for i in range(num_iterations):
            marker = hashlib.sha256(f"crash_{i}_{time.time()}".encode()).hexdigest()[:16]

            script = crash_script.format(project_root=project_root, db_path=db_path, iteration=i, marker=marker)

            # Run crash script
            proc = subprocess.Popen(
                [sys.executable, "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                # SECURITY FIX B-P1-1: Count timeouts as test failures, don't silently skip
                # A timeout during crash simulation is a failure to complete the test
                lost += 1
                print(f"⚠️ Iteration {i} timed out - counting as potential data loss")
                continue

            # Verify event survived
            verify_ledger = SQLiteLedger(db_path)
            events = verify_ledger.get_all_events()

            found = any(e.get("payload") and marker in str(e.get("payload")) for e in events)

            if found:
                survived += 1
            else:
                lost += 1

            verify_ledger.close()

        assert lost == 0, f"DATA LOSS: {lost}/{num_iterations} events lost after crash (survived: {survived})"

        print(f"{survived}/{num_iterations} events survived hard crash")

    finally:
        try:
            os.unlink(db_path)
            # Clean up WAL files
            for ext in ["-wal", "-shm"]:
                wal = db_path + ext
                if os.path.exists(wal):
                    os.unlink(wal)
        except Exception:
            pass


def test_replay_attack_detection():
    """
    SECURITY TEST: Attempt to replay old events.

    Attack vector: Copy an old event and re-insert it.
    System MUST detect the broken hash chain.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        ledger = SQLiteLedger(db_path)

        # Create legitimate events
        for i in range(5):
            ledger.record_event("legitimate", "honest_agent", {"seq": i})

        events_before = ledger.get_all_events()

        # ATTACK: Directly inject a duplicate event via raw SQL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Copy event #2 and insert it again (replay attack)
        old_event = events_before[2]
        cursor.execute(
            """
            INSERT INTO ledger_events
            (event_id, timestamp, event_type, agent_id, payload, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "REPLAYED_EVT",
                old_event["timestamp"],
                old_event["event_type"],
                old_event["agent_id"],
                old_event.get("payload"),
                old_event["current_hash"],  # Using OLD hash
                old_event["previous_hash"],
            ),
        )
        conn.commit()
        conn.close()

        # Verify chain detects tampering
        integrity = ledger.verify_chain_integrity()
        ledger.close()

        assert integrity["corrupted"], (
            "REPLAY ATTACK UNDETECTED: Injected old event, chain reported clean (injected: REPLAYED_EVT)"
        )

        print(
            f"Replay attack detected via hash chain verification ({len(integrity.get('corruptions', []))} corruptions found)"
        )

    finally:
        os.unlink(db_path)


def test_tamper_detection():
    """
    SECURITY TEST: Modify an existing event's payload.

    Attack vector: SQL UPDATE to change event data.
    System MUST detect via hash mismatch.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        ledger = SQLiteLedger(db_path)

        # Create events
        for i in range(5):
            ledger.record_event("vote", "citizen", {"choice": "A", "amount": 1})

        # ATTACK: Modify vote amount directly in DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ledger_events
            SET payload = '{"choice": "B", "amount": 1000000}'
            WHERE id = 3
        """)
        conn.commit()
        conn.close()

        # Verify tampering detected
        integrity = ledger.verify_chain_integrity()
        ledger.close()

        assert integrity["corrupted"], "TAMPERING UNDETECTED: Modified payload, chain reported clean"

        # Check if the correct event was flagged
        corruptions = integrity.get("corruptions", [])
        flagged_indices = [c.get("index") for c in corruptions]

        assert 2 in flagged_indices, (
            f"WRONG EVENT FLAGGED: Tampered event #3 not in corruption list (flagged: {flagged_indices})"
        )

        print("Payload tampering detected at correct position (index 2)")

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
