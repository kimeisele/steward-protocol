"""
⚙️ VIBE CORE: LEDGER MODULE ⚙️
=====================================

The Immutable Memory of Agent City.
Provides append-only event recording with cryptographic hash chaining for tamper detection.

Implements:
- VibeLedger: Abstract base class
- InMemoryLedger: Fast, volatile ledger (for testing)
- SQLiteLedger: Persistent, hash-chained ledger (for production)
"""

import logging
import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger("VIBE_LEDGER")


class VibeLedger:
    """Abstract Base Class for the Ledger"""

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        raise NotImplementedError

    def record_start(self, task) -> None:
        raise NotImplementedError

    def record_completion(self, task, result: Any) -> None:
        raise NotImplementedError

    def record_failure(self, task, error: str) -> None:
        raise NotImplementedError

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def get_all_events(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


class InMemoryLedger(VibeLedger):
    """Immutable Event Ledger - Append-only task record"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._event_counter = 0

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Record a generic event (governance action)"""
        self._event_counter += 1
        event_id = f"EVT-{self._event_counter:06d}"
        event = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
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


class SQLiteLedger(VibeLedger):
    """Persistent SQLite-backed Event Ledger - Append-only task record with persistence"""

    def __init__(self, db_path: str = "data/vibe_ledger.db"):
        """Initialize SQLite ledger with database file"""
        self.db_path = db_path
        self.connection = None
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
        cursor.execute("""
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        logger.info(f"💾 SQLite ledger initialized at {self.db_path}")
        logger.info(f"⛓️  Cryptographic sealing ACTIVE - Hash chain enabled")

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Record a generic event (governance action)"""
        # Get previous hash for the chain
        previous_hash = self._get_previous_hash()

        # Create deterministic event string for hashing (matches verify_chain_integrity)
        timestamp = datetime.utcnow().isoformat()
        event_string = json.dumps({
            "timestamp": timestamp,
            "event_type": event_type,
            "task_id": None,
            "agent_id": agent_id,
            "payload": json.dumps(details) if details else None,
            "result": None,
            "error": None,
        }, sort_keys=True)

        # Compute current hash
        current_hash = self._compute_hash(event_string, previous_hash)

        cursor = self.connection.cursor()
        row = cursor.execute("SELECT MAX(id) FROM ledger_events").fetchone()
        next_id = (row[0] or 0) + 1
        event_id = f"EVT-{next_id:06d}"

        cursor.execute("""
            INSERT INTO ledger_events
            (event_id, timestamp, event_type, agent_id, payload, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp,
            event_type,
            agent_id,
            json.dumps(details) if details else None,
            current_hash,
            previous_hash,
        ))
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
        row = cursor.execute(
            "SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "0" * 64

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        """Compute SHA256 hash of event + previous_hash"""
        combined = event_data + previous_hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def _insert_event(self, event: Dict[str, Any]) -> None:
        """Insert event into database (append-only with hash chaining)"""
        if not self.connection:
            logger.error("❌ Database connection not available")
            return

        # Get previous hash for the chain
        previous_hash = self._get_previous_hash()

        # Create deterministic event string for hashing
        event_string = json.dumps({
            "timestamp": event.get("timestamp"),
            "event_type": event.get("event_type"),
            "task_id": event.get("task_id"),
            "agent_id": event.get("agent_id"),
            "payload": event.get("payload"),
            "result": event.get("result"),
            "error": event.get("error"),
        }, sort_keys=True)

        # Compute current hash
        current_hash = self._compute_hash(event_string, previous_hash)

        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO ledger_events
            (timestamp, event_type, task_id, agent_id, payload, result, error, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("timestamp"),
            event.get("event_type"),
            event.get("task_id"),
            event.get("agent_id"),
            event.get("payload"),
            event.get("result"),
            event.get("error"),
            current_hash,
            previous_hash,
        ))
        self.connection.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result (return most recent event for task)"""
        if not self.connection:
            return None

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM ledger_events
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (task_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all ledger events in order"""
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ledger_events ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify the hash chain is intact (tamper detection)"""
        events = self.get_all_events()

        if not events:
            return {
                "status": "CLEAN",
                "message": "Ledger is empty (genesis state)",
                "total_events": 0,
                "corrupted": False
            }

        corruptions = []
        previous_hash = "0" * 64

        for idx, event in enumerate(events):
            stored_previous = event.get("previous_hash")
            stored_current = event.get("current_hash")

            if stored_previous != previous_hash:
                corruptions.append({
                    "event_id": event.get("event_id"),
                    "index": idx,
                    "type": "PREVIOUS_HASH_MISMATCH",
                    "error": f"Previous hash mismatch at position {idx}"
                })

            # Recompute current hash
            event_string = json.dumps({
                "timestamp": event.get("timestamp"),
                "event_type": event.get("event_type"),
                "task_id": event.get("task_id"),
                "agent_id": event.get("agent_id"),
                "payload": event.get("payload"),
                "result": event.get("result"),
                "error": event.get("error"),
            }, sort_keys=True)

            computed_hash = self._compute_hash(event_string, previous_hash)

            if computed_hash != stored_current:
                corruptions.append({
                    "event_id": event.get("event_id"),
                    "index": idx,
                    "type": "CURRENT_HASH_MISMATCH",
                    "error": f"Current hash mismatch - computed {computed_hash} != stored {stored_current}"
                })

            previous_hash = stored_current

        if corruptions:
            logger.error(f"🚨 CORRUPTION DETECTED in ledger! {len(corruptions)} events tampered")
            return {
                "status": "CORRUPTED",
                "message": "DATA TAMPERING DETECTED - Ledger chain broken",
                "total_events": len(events),
                "corrupted": True,
                "corruptions": corruptions,
                "top_hash": previous_hash
            }

        logger.info(f"✅ Ledger chain integrity verified ({len(events)} events, chain unbroken)")
        return {
            "status": "CLEAN",
            "message": "All events verified - chain integrity intact",
            "total_events": len(events),
            "corrupted": False,
            "top_hash": previous_hash
        }

    def get_top_hash(self) -> str:
        """Get the fingerprint (top hash) of current ledger state"""
        cursor = self.connection.cursor()
        row = cursor.execute(
            "SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "0" * 64

    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("💾 SQLite ledger closed")
