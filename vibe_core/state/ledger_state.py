"""
LedgerState - Layer 1 (STHULA) Ledger Integration for Prakriti

OPUS-027: The missing piece for Split-Brain prevention.

This wraps the SQLite ledger to provide:
- Git sync tracking (which commit was last recorded)
- Hash chain integrity verification
- Cryptographic Zipper (bidirectional Git<->Ledger linking)

GAD-000 Compliant:
- All methods return dict/dataclass
- get_capabilities() for discoverability
"""

import hashlib
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("LEDGER_STATE")


@dataclass
class SyncEvent:
    """A Git-Ledger synchronization event."""

    event_id: str
    git_sha: str
    files_committed: List[str]
    timestamp: float
    ledger_hash: str  # Hash at time of sync (for chain verification)


@dataclass
class LedgerHead:
    """Current head of the ledger hash chain."""

    hash: str
    event_count: int
    last_sync_sha: Optional[str]
    last_sync_time: Optional[float]


class LedgerState:
    """Ledger state wrapper for Prakriti.

    Provides the "Memory" layer that must stay in sync with Git (Code).
    Without this, Split-Brain between Git and Ledger cannot be detected.

    The Cryptographic Zipper:
    - Every Git commit contains Ledger-Head hash
    - Every Ledger sync event contains Git SHA
    - Result: Code and Memory are cryptographically inseparable
    """

    # Table for sync events
    SYNC_TABLE = "prakriti_sync_events"

    def __init__(self, db_path: Path):
        """Initialize LedgerState.

        Args:
            db_path: Path to SQLite database
        """
        self._db_path = db_path
        self._ensure_schema()
        logger.info(f"[LEDGER_STATE] Initialized at {db_path}")

    # =========================================================================
    # Schema Management
    # =========================================================================

    def _ensure_schema(self) -> None:
        """Ensure sync tracking table exists."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self._db_path) as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.SYNC_TABLE} (
                    event_id TEXT PRIMARY KEY,
                    git_sha TEXT NOT NULL,
                    files_json TEXT,
                    timestamp REAL NOT NULL,
                    ledger_hash TEXT NOT NULL,
                    prev_hash TEXT
                )
            """)
            # Index for fast SHA lookups
            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_sync_git_sha
                ON {self.SYNC_TABLE}(git_sha)
            """)
            conn.commit()

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "get_last_sync_commit",
                "record_sync",
                "get_current_head_hash",
                "verify_chain",
                "get_sync_history",
            ],
            "db_path": str(self._db_path),
            "sync_table": self.SYNC_TABLE,
        }

    # =========================================================================
    # Core Sync Operations (OPUS-027)
    # =========================================================================

    def get_last_sync_commit(self) -> Optional[str]:
        """Get the last Git commit SHA recorded in Ledger.

        Returns:
            Git SHA string or None if no syncs recorded
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(f"""
                SELECT git_sha FROM {self.SYNC_TABLE}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return row[0] if row else None

    def record_sync(
        self,
        git_sha: str,
        files_committed: Optional[List[str]] = None,
    ) -> str:
        """Record a state sync event in Ledger.

        This creates the Git->Ledger link of the Cryptographic Zipper.

        Args:
            git_sha: The Git commit SHA being synced
            files_committed: List of files in the commit

        Returns:
            Event ID of the recorded sync
        """
        import json
        import uuid

        event_id = f"sync_{uuid.uuid4().hex[:12]}"
        timestamp = time.time()
        files_json = json.dumps(files_committed or [])

        # Get previous hash for chain
        prev_hash = self.get_current_head_hash()

        # Compute new hash (chain link)
        ledger_hash = self._compute_hash(
            event_id=event_id,
            git_sha=git_sha,
            timestamp=timestamp,
            prev_hash=prev_hash,
        )

        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                f"""
                INSERT INTO {self.SYNC_TABLE}
                (event_id, git_sha, files_json, timestamp, ledger_hash, prev_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (event_id, git_sha, files_json, timestamp, ledger_hash, prev_hash),
            )
            conn.commit()

        logger.info(f"[LEDGER_STATE] Sync recorded: {git_sha[:7]} -> {ledger_hash[:8]}")
        return event_id

    def get_current_head_hash(self) -> str:
        """Get hash of the current ledger head.

        This is the Ledger->Git link of the Cryptographic Zipper.
        This hash goes INTO Git commits to bind them to Ledger state.

        Returns:
            Hash string (empty string if no entries)
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(f"""
                SELECT ledger_hash FROM {self.SYNC_TABLE}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return row[0] if row else ""

    def get_head(self) -> LedgerHead:
        """Get complete head information.

        Returns:
            LedgerHead with hash, count, and last sync info
        """
        with sqlite3.connect(self._db_path) as conn:
            # Get count
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self.SYNC_TABLE}")
            count = cursor.fetchone()[0]

            # Get latest
            cursor = conn.execute(f"""
                SELECT ledger_hash, git_sha, timestamp
                FROM {self.SYNC_TABLE}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row:
                return LedgerHead(
                    hash=row[0],
                    event_count=count,
                    last_sync_sha=row[1],
                    last_sync_time=row[2],
                )
            else:
                return LedgerHead(
                    hash="",
                    event_count=0,
                    last_sync_sha=None,
                    last_sync_time=None,
                )

    # =========================================================================
    # Chain Verification
    # =========================================================================

    def verify_chain(self) -> Dict[str, Any]:
        """Verify Ledger hash chain integrity.

        Walks the chain and verifies each link.

        Returns:
            Dict with verification results
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(f"""
                SELECT event_id, git_sha, timestamp, ledger_hash, prev_hash
                FROM {self.SYNC_TABLE}
                ORDER BY timestamp ASC
            """)
            rows = cursor.fetchall()

        if not rows:
            return {"valid": True, "chain_length": 0, "errors": []}

        errors = []
        expected_prev = ""

        for i, (event_id, git_sha, timestamp, ledger_hash, prev_hash) in enumerate(rows):
            # Check prev_hash link
            if prev_hash != expected_prev:
                errors.append(
                    {
                        "index": i,
                        "event_id": event_id,
                        "error": f"Chain broken: expected prev_hash={expected_prev}, got {prev_hash}",
                    }
                )

            # Verify hash computation
            computed = self._compute_hash(event_id, git_sha, timestamp, prev_hash)
            if computed != ledger_hash:
                errors.append(
                    {
                        "index": i,
                        "event_id": event_id,
                        "error": f"Hash mismatch: computed={computed}, stored={ledger_hash}",
                    }
                )

            expected_prev = ledger_hash

        return {
            "valid": len(errors) == 0,
            "chain_length": len(rows),
            "errors": errors,
        }

    # =========================================================================
    # History & Status
    # =========================================================================

    def get_sync_history(self, limit: int = 10) -> List[SyncEvent]:
        """Get recent sync events.

        Args:
            limit: Max events to return

        Returns:
            List of SyncEvent objects (newest first)
        """
        import json

        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                f"""
                SELECT event_id, git_sha, files_json, timestamp, ledger_hash
                FROM {self.SYNC_TABLE}
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()

        return [
            SyncEvent(
                event_id=row[0],
                git_sha=row[1],
                files_committed=json.loads(row[2]) if row[2] else [],
                timestamp=row[3],
                ledger_hash=row[4],
            )
            for row in rows
        ]

    def status(self) -> Dict[str, Any]:
        """Get ledger status summary."""
        head = self.get_head()
        return {
            "db_path": str(self._db_path),
            "chain_length": head.event_count,
            "current_hash": head.hash[:16] + "..." if head.hash else None,
            "last_sync_sha": head.last_sync_sha,
            "last_sync_time": head.last_sync_time,
        }

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _compute_hash(
        self,
        event_id: str,
        git_sha: str,
        timestamp: float,
        prev_hash: str,
    ) -> str:
        """Compute hash for a sync event (chain link).

        Args:
            event_id: Unique event identifier
            git_sha: Git commit SHA
            timestamp: Unix timestamp
            prev_hash: Previous chain hash

        Returns:
            SHA-256 hash string
        """
        data = f"{event_id}|{git_sha}|{timestamp}|{prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
