"""
MachineState - The SQLite Persistence Layer for Vibe OS.

Provides durable state storage for the Prakriti engine.
"""

import asyncio
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("MACHINE_STATE")


class MachineState:
    """
    Persistent State (SQLite backed).

    Represents the 'Memory' of the machine.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Simple KV store for now
            conn.execute("""
                CREATE TABLE IF NOT EXISTS machine_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            conn.commit()

    async def set(self, key: str, value: Any):
        """Set a persistent value."""
        # SQLite is blocking, but fast. For high throughput, use run_in_executor.
        # For Vibe v1.0, simple blocking call is acceptable (or minimal wrapper).

        json_val = json.dumps(value)

        def _write():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO machine_memory (key, value, updated_at)
                    VALUES (?, ?, strftime('%s', 'now'))
                """,
                    (key, json_val),
                )
                conn.commit()

        # Run in thread explicitly to avoid blocking event loop
        await asyncio.to_thread(_write)

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a persistent value."""

        def _read():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value FROM machine_memory WHERE key = ?", (key,))
                row = cursor.fetchone()
                return json.loads(row[0]) if row else default

        return await asyncio.to_thread(_read)

    async def get_all(self) -> Dict[str, Any]:
        """Get entire state dump."""

        def _read_all():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, value FROM machine_memory")
                return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

        return await asyncio.to_thread(_read_all)

    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics."""
        size_bytes = 0
        if self.db_path.exists():
            size_bytes = self.db_path.stat().st_size

        count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM machine_memory")
                count = cursor.fetchone()[0]
        except Exception:
            pass

        return {"size_bytes": size_bytes, "key_count": count}

    def delete(self, key: str):
        """Delete a key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM machine_memory WHERE key = ?", (key,))
            conn.commit()
