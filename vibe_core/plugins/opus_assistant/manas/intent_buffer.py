"""
OPUS-167: Intent Buffer - Lifecycle Management for MANAS Intents

Extracted from CognitiveKernel to reduce kernel size and improve separation
of concerns. The IntentBuffer manages:

1. Intent storage (in-memory list)
2. Persistence (to .opus_state/manas_intents.json)
3. Deduplication
4. Expiry cleanup
5. Buffer size limits

The kernel orchestrates approval/rejection/execution, but the buffer
handles the data operations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .intent_generator import Intent, IntentPriority, IntentRisk

logger = logging.getLogger("MANAS.IntentBuffer")


@dataclass
class IntentBufferEntry:
    """An entry in the intent buffer."""

    intent: Intent
    status: str = "pending"  # pending, approved, rejected, executed, expired, blocked
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    executed_at: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "intent": self.intent.to_dict(),
            "status": self.status,
            "added_at": self.added_at,
            "executed_at": self.executed_at,
            "execution_result": self.execution_result,
        }


class IntentBuffer:
    """
    OPUS-167: Intent lifecycle management for MANAS.

    This class manages the intent buffer that was previously embedded
    in the CognitiveKernel. Extracting it reduces kernel complexity
    and improves testability.

    Usage:
        buffer = IntentBuffer(workspace=Path.cwd(), max_size=10)

        # Add intents
        buffer.add(entry)

        # Check for duplicates
        if not buffer.is_duplicate(intent):
            buffer.add(IntentBufferEntry(intent=intent))

        # Get pending intents
        pending = buffer.get_pending()

        # Find specific intent
        entry = buffer.find("intent_123")

        # Cleanup expired
        buffer.cleanup_expired(hours=24)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        max_size: int = 10,
        expiry_hours: int = 24,
    ):
        """
        Initialize IntentBuffer.

        Args:
            workspace: Workspace root path
            max_size: Maximum buffer size (oldest removed when exceeded)
            expiry_hours: Hours after which intents expire
        """
        self._workspace = workspace or Path.cwd()
        self._max_size = max_size
        self._expiry_hours = expiry_hours
        self._entries: List[IntentBufferEntry] = []

        # Load from disk on init
        self._load()

        logger.debug(
            f"📋 IntentBuffer initialized (max={max_size}, expiry={expiry_hours}h, loaded={len(self._entries)})"
        )

    @property
    def buffer_file(self) -> Path:
        """Get path to buffer file."""
        return self._workspace / ".opus_state" / "manas_intents.json"

    def add(self, entry: IntentBufferEntry) -> bool:
        """
        Add an entry to the buffer.

        If buffer exceeds max_size, oldest non-pending entries are removed.

        Args:
            entry: The entry to add

        Returns:
            True if added successfully
        """
        self._entries.append(entry)

        # Enforce max size
        self._enforce_size_limit()

        # Auto-save
        self._save()

        logger.debug(f"📋 Added intent to buffer: {entry.intent.id}")
        return True

    def find(self, intent_id: str) -> Optional[IntentBufferEntry]:
        """
        Find an entry by intent ID.

        Args:
            intent_id: The intent ID to find

        Returns:
            The entry if found, None otherwise
        """
        for entry in self._entries:
            if entry.intent.id == intent_id:
                return entry
        return None

    def get_pending(self) -> List[Intent]:
        """Get all pending intents."""
        return [entry.intent for entry in self._entries if entry.status == "pending"]

    def get_all(self) -> List[IntentBufferEntry]:
        """Get all entries."""
        return list(self._entries)

    def is_duplicate(self, intent: Intent) -> bool:
        """
        Check if intent is a duplicate of one already in buffer.

        Considers:
        - Same intent_type
        - Same title (approximate)
        - Still pending

        Args:
            intent: Intent to check

        Returns:
            True if duplicate
        """
        for entry in self._entries:
            if entry.status != "pending":
                continue

            if entry.intent.intent_type == intent.intent_type:
                # Same type - check title similarity
                if entry.intent.title == intent.title:
                    return True

                # Check if titles are similar enough
                if self._titles_similar(entry.intent.title, intent.title):
                    return True

        return False

    def _titles_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be duplicates."""
        # Simple check: if one contains the other
        t1_lower = title1.lower()
        t2_lower = title2.lower()
        return t1_lower in t2_lower or t2_lower in t1_lower

    def update_status(
        self,
        intent_id: str,
        status: str,
        executed_at: Optional[str] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update an entry's status.

        Args:
            intent_id: The intent ID
            status: New status
            executed_at: Optional execution timestamp
            execution_result: Optional execution result

        Returns:
            True if updated
        """
        entry = self.find(intent_id)
        if not entry:
            return False

        entry.status = status
        if executed_at:
            entry.executed_at = executed_at
        if execution_result is not None:
            entry.execution_result = execution_result

        self._save()
        return True

    def cleanup_expired(self, hours: Optional[int] = None) -> int:
        """
        Remove expired intents.

        Args:
            hours: Override expiry hours (default uses init value)

        Returns:
            Number of entries removed
        """
        expiry_hours = hours or self._expiry_hours
        cutoff = datetime.utcnow() - timedelta(hours=expiry_hours)
        cutoff_str = cutoff.isoformat()

        original_count = len(self._entries)

        # Keep: pending entries OR entries newer than cutoff
        self._entries = [entry for entry in self._entries if entry.status == "pending" or entry.added_at >= cutoff_str]

        removed = original_count - len(self._entries)

        if removed > 0:
            self._save()
            logger.debug(f"📋 Cleaned up {removed} expired intents")

        return removed

    def _enforce_size_limit(self) -> None:
        """Remove oldest non-pending entries if buffer exceeds max size."""
        while len(self._entries) > self._max_size:
            # Find oldest non-pending to remove
            removed = False
            for i, entry in enumerate(self._entries):
                if entry.status != "pending":
                    self._entries.pop(i)
                    removed = True
                    break

            if not removed:
                # All pending - remove oldest anyway
                self._entries.pop(0)

    def _load(self) -> None:
        """Load buffer from disk."""
        try:
            if not self.buffer_file.exists():
                return

            data = json.loads(self.buffer_file.read_text())
            self._entries = []

            for entry_data in data.get("intents", []):
                intent_data = entry_data.get("intent", {})

                # Reconstruct Intent
                intent = Intent(
                    id=intent_data.get("id", "unknown"),
                    intent_type=intent_data.get("intent_type", "unknown"),
                    title=intent_data.get("title", "Unknown"),
                    description=intent_data.get("description", ""),
                    reasoning=intent_data.get("reasoning", ""),
                    priority=IntentPriority(intent_data.get("priority", "medium")),
                    risk=IntentRisk(intent_data.get("risk", "medium")),
                    created_at=intent_data.get("created_at", datetime.utcnow().isoformat()),
                    circuit_to_execute=intent_data.get("circuit_to_execute"),
                    params=intent_data.get("params", {}),
                    auto_executable=intent_data.get("auto_executable", False),
                    expires_at=intent_data.get("expires_at"),
                )

                entry = IntentBufferEntry(
                    intent=intent,
                    status=entry_data.get("status", "pending"),
                    added_at=entry_data.get("added_at", datetime.utcnow().isoformat()),
                    executed_at=entry_data.get("executed_at"),
                    execution_result=entry_data.get("execution_result"),
                )
                self._entries.append(entry)

            logger.debug(f"📋 Loaded {len(self._entries)} intents from disk")

        except Exception as e:
            logger.warning(f"📋 Could not load intent buffer: {e}")
            self._entries = []

    def _save(self) -> None:
        """Save buffer to disk."""
        try:
            data = {
                "intents": [entry.to_dict() for entry in self._entries],
                "updated_at": datetime.utcnow().isoformat(),
            }

            self.buffer_file.parent.mkdir(parents=True, exist_ok=True)
            self.buffer_file.write_text(json.dumps(data, indent=2))

        except Exception as e:
            logger.warning(f"📋 Could not save intent buffer: {e}")

    def save(self) -> None:
        """Public save method for explicit saves."""
        self._save()

    def __len__(self) -> int:
        """Return buffer size."""
        return len(self._entries)

    def __iter__(self):
        """Iterate over entries."""
        return iter(self._entries)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "IntentBuffer",
    "IntentBufferEntry",
]
