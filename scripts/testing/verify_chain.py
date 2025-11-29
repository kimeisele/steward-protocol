#!/usr/bin/env python3
"""
⛓️  LEDGER CHAIN VERIFIER
========================

Validates cryptographic integrity of the audit ledger.
Detects data tampering through hash chain verification.

Usage:
    python scripts/verify_chain.py [--db-path DATA_PATH] [--repair]
"""

import hashlib
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("CHAIN_VERIFIER")


class ChainVerifier:
    """Cryptographic chain verifier for tamper-evident logging"""

    def __init__(self, db_path: str = "data/vibe_ledger.db"):
        self.db_path = db_path
        self.connection = None
        self.events = []

        if not Path(db_path).exists():
            logger.error(f"❌ Database not found: {db_path}")
            sys.exit(1)

        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        logger.info(f"📖 Connected to ledger: {db_path}")

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        """Compute SHA256 hash of event + previous_hash"""
        combined = event_data + previous_hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def load_events(self) -> List[Dict[str, Any]]:
        """Load all events from database"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ledger_events ORDER BY id ASC")
        rows = cursor.fetchall()
        self.events = [dict(row) for row in rows]
        logger.info(f"📚 Loaded {len(self.events)} events")
        return self.events

    def verify_chain(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify entire chain integrity"""
        if not self.events:
            return True, {
                "status": "CLEAN",
                "message": "Ledger is empty (genesis state)",
                "total_events": 0,
                "corrupted": False,
            }

        corruptions = []
        previous_hash = "0" * 64

        for idx, event in enumerate(self.events):
            stored_previous = event.get("previous_hash")
            stored_current = event.get("current_hash")

            # Check previous hash link
            if stored_previous != previous_hash:
                corruptions.append(
                    {
                        "index": idx,
                        "event_id": event.get("event_id"),
                        "type": "PREVIOUS_HASH_MISMATCH",
                        "expected": previous_hash,
                        "stored": stored_previous,
                    }
                )

            # Recompute current hash
            event_string = json.dumps(
                {
                    "timestamp": event.get("timestamp"),
                    "event_type": event.get("event_type"),
                    "task_id": event.get("task_id"),
                    "agent_id": event.get("agent_id"),
                    "payload": event.get("payload"),
                    "result": event.get("result"),
                    "error": event.get("error"),
                },
                sort_keys=True,
            )

            computed_hash = self._compute_hash(event_string, previous_hash)

            if computed_hash != stored_current:
                corruptions.append(
                    {
                        "index": idx,
                        "event_id": event.get("event_id"),
                        "type": "CURRENT_HASH_MISMATCH",
                        "computed": computed_hash,
                        "stored": stored_current,
                    }
                )

            previous_hash = stored_current

        if corruptions:
            logger.error(f"🚨 CORRUPTION DETECTED: {len(corruptions)} anomalies found")
            return False, {
                "status": "CORRUPTED",
                "message": "DATA TAMPERING DETECTED - Chain integrity broken",
                "total_events": len(self.events),
                "corrupted": True,
                "corruption_count": len(corruptions),
                "corruptions": corruptions,
                "top_hash": previous_hash,
            }

        logger.info(f"✅ CHAIN CLEAN: All {len(self.events)} events verified")
        return True, {
            "status": "CLEAN",
            "message": "Ledger chain integrity verified",
            "total_events": len(self.events),
            "corrupted": False,
            "top_hash": previous_hash,
        }

    def print_report(self, clean: bool, result: Dict[str, Any]) -> None:
        """Print verification report"""
        print("\n" + "=" * 70)
        print("⛓️  LEDGER CHAIN INTEGRITY REPORT")
        print("=" * 70)

        print(f"\n📊 Status: {result.get('status')}")
        print(f"📋 Message: {result.get('message')}")
        print(f"📈 Total Events: {result.get('total_events')}")
        print(f"🔍 Integrity: {'🟢 INTACT' if clean else '🔴 BROKEN'}")

        if result.get("top_hash"):
            print(f"🔐 Top Hash (Fingerprint): {result.get('top_hash')}")

        if result.get("corruptions"):
            print(f"\n⚠️  CORRUPTIONS FOUND ({len(result['corruptions'])})")
            for corruption in result["corruptions"]:
                print(f"\n  📍 Event #{corruption['index']} ({corruption['event_id']})")
                print(f"     Type: {corruption['type']}")
                if "expected" in corruption:
                    print(f"     Expected: {corruption['expected'][:16]}...")
                    print(f"     Stored:   {corruption['stored'][:16]}...")
                if "computed" in corruption:
                    print(f"     Computed: {corruption['computed'][:16]}...")
                    print(f"     Stored:   {corruption['stored'][:16]}...")

        print("\n" + "=" * 70 + "\n")

    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Verify ledger chain integrity")
    parser.add_argument("--db-path", default="data/vibe_ledger.db", help="Path to ledger database")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    verifier = ChainVerifier(args.db_path)
    verifier.load_events()
    clean, result = verifier.verify_chain()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        verifier.print_report(clean, result)

    verifier.close()

    sys.exit(0 if clean else 1)


if __name__ == "__main__":
    main()
