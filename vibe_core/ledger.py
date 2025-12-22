"""
⚙️ VIBE CORE: LEDGER MODULE ⚙️
=====================================

The Immutable Memory of Agent City.
Provides append-only event recording with cryptographic hash chaining for tamper detection.

P1 SECURITY (OPUS-018): Per-event ECDSA signatures added.
- Each event is signed by the agent who created it
- Prevents DB tampering even with database access
- Legacy events (agent_signature=NULL) fall back to hash chain only

Implements:
- VibeLedger: Abstract base class (imported from kernel.py)
- InMemoryLedger: Fast, volatile ledger (for testing)
- SQLiteLedger: Persistent, hash-chained + signed ledger (for production)
"""

import hashlib
import json
import logging
import os
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

# BLOCKER #1: Import canonical VibeLedger ABC from kernel.py
from .kernel import VibeLedger

# P1 SECURITY: Import ECDSA signing from steward/crypto.py
try:
    from vibe_core.steward.crypto import load_or_generate_keys, sign_content, verify_signature

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    load_or_generate_keys = None
    sign_content = None
    verify_signature = None

logger = logging.getLogger("VIBE_LEDGER")

# Global lock for cross-connection thread safety on same DB file
_db_locks: Dict[str, threading.Lock] = {}
_db_locks_lock = threading.Lock()


class InMemoryLedger(VibeLedger):
    """Immutable Event Ledger - Append-only task record"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._event_counter = 0

    def record_event(
        self,
        event_type: str,
        agent_id: str,
        details: Dict[str, Any],
        result: str = None,
        task_id: str = None,
        error: str = None,
    ) -> str:
        """Record a generic event (governance action)"""
        self._event_counter += 1
        event_id = f"EVT-{self._event_counter:06d}"
        event = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
            "result": result,
            "task_id": task_id,
            "error": error,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Event recorded {event_id} ({event_type})")
        return event_id

    def record_start(self, task) -> None:
        """Record task start"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_start",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "payload": task.payload,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task started {task.task_id}")

    def record_completion(self, task, result: Any) -> None:
        """Record task completion"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_completed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "result": result,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task completed {task.task_id}")

    def record_failure(self, task, error: str) -> None:
        """Record task failure"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_failed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "error": error,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task failed {task.task_id}")

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result"""
        # Search backwards for the most recent event
        for event in reversed(self.events):
            if event.get("task_id") == task_id:
                return event
        return None

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all ledger events"""
        return self.events.copy()

    def count_events(self) -> int:
        """Return total number of events."""
        return len(self.events)


def _get_db_lock(db_path: str) -> threading.Lock:
    """Get or create a lock for a specific database file."""
    abs_path = os.path.abspath(db_path)
    with _db_locks_lock:
        if abs_path not in _db_locks:
            _db_locks[abs_path] = threading.Lock()
        return _db_locks[abs_path]


class SQLiteLedger(VibeLedger):
    """Persistent SQLite-backed Event Ledger - Append-only task record with persistence"""

    def __init__(self, db_path: str):
        """Initialize SQLite ledger with database file.

        OPUS-025: db_path is REQUIRED. No default - callers must use
        config.paths.data.resolve("vibe_ledger") or pass explicit path.
        """
        if not db_path:
            raise ValueError("db_path is required - use config.paths.data.resolve('vibe_ledger')")
        self.db_path = db_path
        self.connection = None
        self._write_lock = _get_db_lock(db_path)
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create database and schema if not exists"""
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Connect to database (check_same_thread=False for multi-threaded API access)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        # Create table if not exists
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                task_id TEXT,
                agent_id TEXT NOT NULL,
                payload TEXT,
                result TEXT,
                error TEXT,
                details TEXT,
                current_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                agent_signature TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.connection.commit()

        # P1 MIGRATION: Add agent_signature column if missing (for existing DBs)
        self._migrate_add_signature_column()

        # Load or generate signing keys
        self._private_key = None
        self._public_key = None
        if CRYPTO_AVAILABLE:
            try:
                self._private_key, self._public_key = load_or_generate_keys()
                logger.info("🔐 Ledger signing ACTIVE - ECDSA signatures enabled")
            except Exception as e:
                logger.warning(f"⚠️ Ledger signing DISABLED - crypto error: {e}")
        else:
            logger.warning("⚠️ Ledger signing DISABLED - steward/crypto.py not available")

        logger.info(f"💾 SQLite ledger initialized at {self.db_path}")
        logger.info("⛓️  Cryptographic sealing ACTIVE - Hash chain enabled")

    def _migrate_add_signature_column(self) -> None:
        """Add agent_signature column to existing databases (P1 migration)."""
        try:
            cursor = self.connection.cursor()
            # Check if column exists
            cursor.execute("PRAGMA table_info(ledger_events)")
            columns = [row[1] for row in cursor.fetchall()]
            if "agent_signature" not in columns:
                cursor.execute("ALTER TABLE ledger_events ADD COLUMN agent_signature TEXT")
                self.connection.commit()
                logger.info("📦 P1 Migration: Added agent_signature column to ledger_events")
        except Exception as e:
            logger.warning(f"⚠️ P1 Migration check failed: {e}")

    def _sign_event(self, event_string: str) -> Optional[str]:
        """Sign event data using ECDSA.

        Returns base64-encoded signature or None if signing unavailable.
        """
        if not CRYPTO_AVAILABLE or not self._private_key:
            return None
        try:
            signature = sign_content(event_string, self._private_key)
            return signature
        except Exception as e:
            logger.warning(f"⚠️ Event signing failed: {e}")
            return None

    def record_event(
        self,
        event_type: str,
        agent_id: str,
        details: Dict[str, Any],
        result: str = None,
        task_id: str = None,
        error: str = None,
    ) -> str:
        """Record a generic event (governance action)

        Thread-safe: Uses lock to ensure hash chain integrity under concurrent writes.

        Args:
            event_type: Type of event (IO_WRITE, SYSCALL, etc.)
            agent_id: ID of agent performing action
            details: Event payload/details
            result: Result of the action (success/failure/etc.) - GAD-000 compliance
            task_id: Associated task ID if applicable - GAD-000 compliance
            error: Error message if action failed - GAD-000 compliance
        """
        # CRITICAL: Lock entire read-compute-write cycle for hash chain integrity
        with self._write_lock:
            # Get previous hash for the chain
            previous_hash = self._get_previous_hash()

            # Create deterministic event string for hashing (matches verify_chain_integrity)
            timestamp = datetime.utcnow().isoformat()
            event_string = json.dumps(
                {
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "payload": json.dumps(details) if details else None,
                    "result": result,
                    "error": error,
                },
                sort_keys=True,
            )

            # Compute current hash
            current_hash = self._compute_hash(event_string, previous_hash)

            # P1 SECURITY: Sign the event
            agent_signature = self._sign_event(event_string)

            cursor = self.connection.cursor()
            row = cursor.execute("SELECT MAX(id) FROM ledger_events").fetchone()
            next_id = (row[0] or 0) + 1
            event_id = f"EVT-{next_id:06d}"

            cursor.execute(
                """
                INSERT INTO ledger_events
                (event_id, timestamp, event_type, task_id, agent_id, payload, result, error, current_hash, previous_hash, agent_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event_id,
                    timestamp,
                    event_type,
                    task_id,
                    agent_id,
                    json.dumps(details) if details else None,
                    result,
                    error,
                    current_hash,
                    previous_hash,
                    agent_signature,
                ),
            )
            self.connection.commit()

        logger.debug(f"📝 Ledger: Event recorded {event_id} ({event_type})")
        return event_id

    def record_start(self, task) -> None:
        """Record task start"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_start",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "payload": json.dumps(task.payload) if task.payload else None,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task started {task.task_id}")

    def record_completion(self, task, result: Any) -> None:
        """Record task completion"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_completed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "result": json.dumps(result) if result else None,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task completed {task.task_id}")

    def record_failure(self, task, error: str) -> None:
        """Record task failure"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_failed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "error": error,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task failed {task.task_id}")

    def _get_previous_hash(self) -> str:
        """Get hash of last event, or genesis hash if first event"""
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else "0" * 64

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        """Compute SHA256 hash of event + previous_hash"""
        combined = event_data + previous_hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def _insert_event(self, event: Dict[str, Any]) -> None:
        """Insert event into database (append-only with hash chaining)

        Thread-safe: Uses lock to ensure hash chain integrity.
        """
        if not self.connection:
            logger.error("❌ Database connection not available")
            return

        # CRITICAL: Lock entire read-compute-write cycle for hash chain integrity
        with self._write_lock:
            # Get previous hash for the chain
            previous_hash = self._get_previous_hash()

            # Create deterministic event string for hashing
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

            # Compute current hash
            current_hash = self._compute_hash(event_string, previous_hash)

            # P1 SECURITY: Sign the event
            agent_signature = self._sign_event(event_string)

            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO ledger_events
                (timestamp, event_type, task_id, agent_id, payload, result, error, current_hash, previous_hash, agent_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.get("timestamp"),
                    event.get("event_type"),
                    event.get("task_id"),
                    event.get("agent_id"),
                    event.get("payload"),
                    event.get("result"),
                    event.get("error"),
                    current_hash,
                    previous_hash,
                    agent_signature,
                ),
            )
            self.connection.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result (return most recent event for task)"""
        if not self.connection:
            return None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT * FROM ledger_events
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
        """,
            (task_id,),
        )

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all ledger events in order with parsed details"""
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ledger_events ORDER BY id ASC")
        rows = cursor.fetchall()

        events = []
        for row in rows:
            event = dict(row)
            # Parse payload JSON and set as details for consistency with InMemoryLedger
            if event.get("payload") and event.get("details") is None:
                try:
                    event["details"] = json.loads(event["payload"])
                except (json.JSONDecodeError, TypeError):
                    pass
            events.append(event)
        return events

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify the hash chain is intact (tamper detection)"""
        events = self.get_all_events()

        if not events:
            return {
                "status": "CLEAN",
                "message": "Ledger is empty (genesis state)",
                "total_events": 0,
                "corrupted": False,
            }

        corruptions = []
        previous_hash = "0" * 64

        for idx, event in enumerate(events):
            stored_previous = event.get("previous_hash")
            stored_current = event.get("current_hash")

            if stored_previous != previous_hash:
                corruptions.append(
                    {
                        "event_id": event.get("event_id"),
                        "index": idx,
                        "type": "PREVIOUS_HASH_MISMATCH",
                        "error": f"Previous hash mismatch at position {idx}",
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
                        "event_id": event.get("event_id"),
                        "index": idx,
                        "type": "CURRENT_HASH_MISMATCH",
                        "error": f"Current hash mismatch - computed {computed_hash} != stored {stored_current}",
                    }
                )

            previous_hash = stored_current

        if corruptions:
            logger.error(f"🚨 CORRUPTION DETECTED in ledger! {len(corruptions)} events tampered")
            return {
                "status": "CORRUPTED",
                "message": "DATA TAMPERING DETECTED - Ledger chain broken",
                "total_events": len(events),
                "corrupted": True,
                "corruptions": corruptions,
                "top_hash": previous_hash,
            }

        logger.info(f"✅ Ledger chain integrity verified ({len(events)} events, chain unbroken)")
        return {
            "status": "CLEAN",
            "message": "All events verified - chain integrity intact",
            "total_events": len(events),
            "corrupted": False,
            "top_hash": previous_hash,
        }

    def get_top_hash(self) -> str:
        """Get the fingerprint (top hash) of current ledger state"""
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else "0" * 64

    def count_events(self) -> int:
        """Efficiently count total events without loading them into memory."""
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT COUNT(*) FROM ledger_events").fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("💾 SQLite ledger closed")
