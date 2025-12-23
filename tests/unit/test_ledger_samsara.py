"""
OPUS-208: Ledger Samsara & Unified Query Tests
==============================================

Verifies:
1. Crash-safe rotation (Samsara)
2. Cryptographic linkage across archives
3. Unified querying across hot DB and archives
"""

import os
import time
from pathlib import Path

import pytest

from vibe_core.ledger import SQLiteLedger


@pytest.mark.unit
@pytest.mark.fast
class TestLedgerSamsara:
    @pytest.fixture
    def test_db(self, temp_dir: Path) -> str:
        """Fixture providing a temporary database path."""
        db_path = temp_dir / "test_ledger.db"
        return str(db_path)

    def test_ledger_rotation_and_genesis_linkage(self, test_db: str):
        """Verify that rotation creates a new DB linked to the previous one."""
        ledger = SQLiteLedger(test_db)

        # 1. Add data to old chain
        ledger.record_event("OLD_CHAIN_EVENT", "AGENT_A", {"seq": 1})
        top_hash_old = ledger.get_top_hash()

        # 2. Rotate
        archive_path = ledger.rotate()
        assert archive_path is not None
        assert os.path.exists(archive_path)
        assert os.path.exists(test_db)  # New DB should exist

        # 3. Verify Genesis in new DB
        hot_events = ledger.get_events(include_archives=False)
        assert len(hot_events) == 1
        genesis_event = hot_events[0]
        assert genesis_event["event_type"] == "LEDGER_GENESIS"
        assert genesis_event["details"]["previous_ledger_hash"] == top_hash_old

        ledger.close()

    def test_unified_query_logic(self, test_db: str):
        """Verify that get_events searches across hot DB and archives."""
        ledger = SQLiteLedger(test_db)

        # Batch 1 (Archive)
        for i in range(5):
            ledger.record_event("ARCHIVE_EVENT", "ALPHA", {"idx": i})
            time.sleep(0.01)

        ledger.rotate()

        # Batch 2 (Hot)
        for i in range(3):
            ledger.record_event("HOT_EVENT", "BETA", {"idx": i})
            time.sleep(0.01)

        # Query Hot Only
        hot_events = ledger.get_events(include_archives=False)
        # 3 events + 1 genesis
        assert len(hot_events) == 4

        # Query Unified (Sorted newest first)
        all_events = ledger.get_events(include_archives=True)
        # (3 hot + 1 genesis) + 5 archived = 9
        assert len(all_events) == 9

        # Verify Sorting
        assert all_events[0]["event_type"] == "HOT_EVENT"
        assert all_events[-1]["event_type"] == "ARCHIVE_EVENT"

        # Verify Filtering
        beta_events = ledger.get_events(agent_id="BETA", include_archives=True)
        assert len(beta_events) == 3
        for e in beta_events:
            assert e["agent_id"] == "BETA"

        ledger.close()

    def test_incremental_fetch_and_anchor_persistence(self, test_db: str):
        """Verify the health anchor logic from OPUS-208 Phase 1."""
        ledger = SQLiteLedger(test_db)

        # Batch 1
        for _ in range(10):
            ledger.record_event("T1", "A", {})

        # Simulate Health Check 1
        anchor = ledger.get_meta("health_anchor") or (0, "0" * 64)
        new_events = ledger.get_events_since(anchor[0])
        assert len(new_events) == 10

        # Save anchor
        last = new_events[-1]
        ledger.set_meta("health_anchor", (last["id"], last["current_hash"]))

        # Batch 2
        for _ in range(5):
            ledger.record_event("T2", "A", {})

        # Simulate Health Check 2 (Incremental)
        anchor2 = ledger.get_meta("health_anchor")
        new_events2 = ledger.get_events_since(anchor2[0])
        assert len(new_events2) == 5

        ledger.close()
