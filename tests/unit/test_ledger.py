"""
TEST: Vibe Ledger (The Memory)
==============================
Verifies the immutable memory of the Agent City.
Target: vibe_core/ledger.py
Standard: GAD-5000
"""

import json
import os
import sqlite3

from vibe_core.ledger import InMemoryLedger, SQLiteLedger


class TestInMemoryLedger:
    def test_append_event(self):
        """Should append events to memory."""
        ledger = InMemoryLedger()
        event_id = ledger.record_event("test_event", "me", {"foo": "bar"})

        events = ledger.get_all_events()
        assert len(events) == 1
        assert events[0]["event_id"] == event_id
        assert events[0]["details"]["foo"] == "bar"


class TestSQLiteLedger:
    def setup_method(self):
        self.db_path = "test_ledger.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def teardown_method(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_hash_chaining(self):
        """Should chain hashes correctly."""
        ledger = SQLiteLedger(self.db_path)

        # Record Event 1 (Genesis)
        id1 = ledger.record_event("genesis", "system", {"n": 1})

        # Record Event 2
        id2 = ledger.record_event("update", "system", {"n": 2})

        events = ledger.get_all_events()
        assert len(events) == 2

        # Note: get_all_events() returns DESC order (newest first)
        # Reverse for chronological order
        events = list(reversed(events))
        evt1 = events[0]
        evt2 = events[1]

        # Verify genesis previous hash is all zeros
        assert evt1["previous_hash"] == "0" * 64

        # Verify chain: E2.previous == E1.current
        assert evt2["previous_hash"] == evt1["current_hash"]

        # Verify integrity check passes
        report = ledger.verify_chain_integrity()
        assert report["status"] == "CLEAN"
        assert report["corrupted"] is False

        ledger.close()

    def test_tamper_detection(self):
        """Should detect bit-flipping attacks."""
        ledger = SQLiteLedger(self.db_path)
        ledger.record_event("evt1", "agent1", {"data": "A"})
        ledger.record_event("evt2", "agent1", {"data": "B"})
        ledger.close()

        # ATTACK: Manually modify SQLite DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Modify the payload of the first event
        # This should break the hash chain for the SECOND event (previous_hash mismatch check won't catch it,
        # but recomputing hash of E1 will show it doesn't match E1.current_hash)
        # Wait, actually:
        # If I change E1 payload, E1.current_hash remains "valid" (stored) but "computed" will differ.
        cursor.execute("UPDATE ledger_events SET payload = ? WHERE id = 1", (json.dumps({"data": "TAMPERED"}),))
        conn.commit()
        conn.close()

        # VERIFY
        ledger_reopen = SQLiteLedger(self.db_path)
        report = ledger_reopen.verify_chain_integrity()

        assert report["status"] == "CORRUPTED"
        assert report["corrupted"] is True
        assert len(report["corruptions"]) > 0

        ledger_reopen.close()
