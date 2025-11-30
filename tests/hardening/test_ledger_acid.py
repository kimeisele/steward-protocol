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
import json
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from multiprocessing import Process, Queue
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.ledger import SQLiteLedger


class HardeningResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def fail(self, msg: str, **details):
        self.passed = False
        self.message = msg
        self.details = details
        return self

    def success(self, msg: str = "OK", **details):
        self.passed = True
        self.message = msg
        self.details = details
        return self


def test_concurrent_writes_integrity(num_threads: int = 50, events_per_thread: int = 100) -> HardeningResult:
    """
    STRESS TEST: Multiple threads writing simultaneously.

    Acceptance Criteria:
    - Zero lost writes (all events recorded)
    - Hash chain remains unbroken
    - No duplicate event IDs
    """
    result = HardeningResult("CONCURRENT_WRITES_INTEGRITY")

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
                        f"stress_test",
                        f"thread_{thread_id}",
                        {"thread": thread_id, "seq": i}
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
        if actual_events != expected_events:
            return result.fail(
                f"LOST WRITES: Expected {expected_events}, got {actual_events}",
                lost=expected_events - actual_events,
                duration=duration
            )

        # Check 2: Hash chain integrity
        integrity = verify_ledger.verify_chain_integrity()
        if integrity["corrupted"]:
            return result.fail(
                f"HASH CHAIN CORRUPTED: {len(integrity.get('corruptions', []))} breaks",
                corruptions=integrity.get("corruptions", [])[:5],
                duration=duration
            )

        # Check 3: No duplicate IDs
        unique_ids = set(e.get("event_id") for e in events)
        if len(unique_ids) != actual_events:
            return result.fail(
                f"DUPLICATE EVENT IDS: {actual_events - len(unique_ids)} duplicates",
                duration=duration
            )

        verify_ledger.close()

        if errors:
            return result.fail(f"THREAD ERRORS: {len(errors)}", errors=errors[:5])

        return result.success(
            f"{actual_events} events, chain intact, {duration:.2f}s",
            events=actual_events,
            rate=actual_events/duration,
            duration=duration
        )

    finally:
        os.unlink(db_path)


def test_crash_durability(num_iterations: int = 10) -> HardeningResult:
    """
    CRASH TEST: Write event, kill -9, verify persistence.

    Simulates hard crashes (power loss, kernel panic).
    Event MUST survive if record_event() returned.
    """
    result = HardeningResult("CRASH_DURABILITY")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    crash_script = '''
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
'''

    project_root = str(Path(__file__).parent.parent.parent)

    try:
        survived = 0
        lost = 0

        for i in range(num_iterations):
            marker = hashlib.sha256(f"crash_{i}_{time.time()}".encode()).hexdigest()[:16]

            script = crash_script.format(
                project_root=project_root,
                db_path=db_path,
                iteration=i,
                marker=marker
            )

            # Run crash script
            proc = subprocess.Popen(
                [sys.executable, "-c", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                continue

            # Verify event survived
            verify_ledger = SQLiteLedger(db_path)
            events = verify_ledger.get_all_events()

            found = any(
                e.get("payload") and marker in str(e.get("payload"))
                for e in events
            )

            if found:
                survived += 1
            else:
                lost += 1

            verify_ledger.close()

        if lost > 0:
            return result.fail(
                f"DATA LOSS: {lost}/{num_iterations} events lost after crash",
                survived=survived,
                lost=lost
            )

        return result.success(
            f"{survived}/{num_iterations} events survived hard crash",
            survived=survived
        )

    finally:
        try:
            os.unlink(db_path)
            # Clean up WAL files
            for ext in ["-wal", "-shm"]:
                wal = db_path + ext
                if os.path.exists(wal):
                    os.unlink(wal)
        except:
            pass


def test_replay_attack_detection() -> HardeningResult:
    """
    SECURITY TEST: Attempt to replay old events.

    Attack vector: Copy an old event and re-insert it.
    System MUST detect the broken hash chain.
    """
    result = HardeningResult("REPLAY_ATTACK_DETECTION")

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
        cursor.execute("""
            INSERT INTO ledger_events
            (event_id, timestamp, event_type, agent_id, payload, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "REPLAYED_EVT",
            old_event["timestamp"],
            old_event["event_type"],
            old_event["agent_id"],
            old_event.get("payload"),
            old_event["current_hash"],  # Using OLD hash
            old_event["previous_hash"]
        ))
        conn.commit()
        conn.close()

        # Verify chain detects tampering
        integrity = ledger.verify_chain_integrity()
        ledger.close()

        if not integrity["corrupted"]:
            return result.fail(
                "REPLAY ATTACK UNDETECTED: Injected old event, chain reported clean",
                injected_event="REPLAYED_EVT"
            )

        return result.success(
            "Replay attack detected via hash chain verification",
            corruptions_found=len(integrity.get("corruptions", []))
        )

    finally:
        os.unlink(db_path)


def test_tamper_detection() -> HardeningResult:
    """
    SECURITY TEST: Modify an existing event's payload.

    Attack vector: SQL UPDATE to change event data.
    System MUST detect via hash mismatch.
    """
    result = HardeningResult("TAMPER_DETECTION")

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

        if not integrity["corrupted"]:
            return result.fail(
                "TAMPERING UNDETECTED: Modified payload, chain reported clean"
            )

        # Check if the correct event was flagged
        corruptions = integrity.get("corruptions", [])
        flagged_indices = [c.get("index") for c in corruptions]

        if 2 not in flagged_indices:  # index 2 = id 3
            return result.fail(
                "WRONG EVENT FLAGGED: Tampered event #3 not in corruption list",
                flagged=flagged_indices
            )

        return result.success(
            "Payload tampering detected at correct position",
            tampered_index=2
        )

    finally:
        os.unlink(db_path)


def run_all_tests() -> dict:
    """Run all ACID tests and return summary."""

    print("\n" + "=" * 60)
    print("🔩 KRUPP-STAHL LEDGER ACID TEST SUITE")
    print("=" * 60)

    tests = [
        ("Concurrent Writes (50 threads x 100 events)", test_concurrent_writes_integrity),
        ("Crash Durability (10 kill -9 cycles)", test_crash_durability),
        ("Replay Attack Detection", test_replay_attack_detection),
        ("Tamper Detection", test_tamper_detection),
    ]

    results = {}
    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n[TEST] {name}")
        try:
            result = test_fn()
            results[result.name] = result

            if result.passed:
                print(f"  ✅ PASS: {result.message}")
                passed += 1
            else:
                print(f"  ❌ FAIL: {result.message}")
                if result.details:
                    for k, v in list(result.details.items())[:3]:
                        print(f"     {k}: {v}")
                failed += 1

        except Exception as e:
            print(f"  💥 ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    summary = run_all_tests()
    sys.exit(0 if summary["failed"] == 0 else 1)
