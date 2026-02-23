"""
Moltbook Event Sourcing — Immutable JSONL Ledger.

Pattern: Herald core/memory.py (EventLog + LedgerEvent)

Every action creates an immutable event:
    content_generated, content_published, content_rejected,
    engagement_completed, system_error

State is reconstructed by replaying events from line 0 to N.
Replaces plugin_main.py _log_activity() with proper event sourcing.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_MEMORY")


@dataclass
class LedgerEvent:
    """Immutable event in the Moltbook ledger."""

    event_type: str
    timestamp: str
    agent_id: str
    payload: Dict[str, Any]
    sequence_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class EventLog:
    """
    Immutable event ledger for Moltbook.

    Append-only JSONL file. State reconstructed by replaying events.
    Simpler than Herald's version — no crypto signing (MoltbookService
    already enforces guna gates on all writes).
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        if ledger_path is None:
            try:
                from vibe_core.phoenix.config import get_config

                data_root = Path(get_config().paths.data.resolve("plugins/moltbook"))
            except Exception:
                data_root = Path(".vibe/state/plugins/moltbook")
            ledger_path = data_root / "events.jsonl"

        self.ledger_path = Path(ledger_path)
        self.agent_id = "agent.moltbook"
        self.sequence_counter = 0
        self.pending_validation_feedback: Optional[Dict[str, Any]] = None

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._reload_sequence_counter()

    def _reload_sequence_counter(self) -> None:
        """Count existing events in ledger."""
        if self.ledger_path.exists():
            try:
                with open(self.ledger_path, "r") as f:
                    self.sequence_counter = sum(1 for line in f if line.strip())
            except Exception:
                self.sequence_counter = 0

    def commit(self, event_type: str, payload: Dict[str, Any]) -> Optional[LedgerEvent]:
        """Create and commit an event atomically."""
        self.sequence_counter += 1
        event = LedgerEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=self.agent_id,
            payload=payload,
            sequence_number=self.sequence_counter,
        )
        try:
            with open(self.ledger_path, "a") as f:
                f.write(event.to_json() + "\n")
            return event
        except Exception as e:
            logger.warning(f"Event commit failed: {e}")
            self.sequence_counter -= 1
            return None

    def record_content_generated(self, content_type: str, content: str, **extra: Any) -> Optional[LedgerEvent]:
        """Record content generation."""
        return self.commit("content_generated", {
            "content_type": content_type,
            "content_preview": content[:100],
            "content_length": len(content),
            **extra,
        })

    def record_content_published(self, content_type: str, content: str, **extra: Any) -> Optional[LedgerEvent]:
        """Record content publication."""
        return self.commit("content_published", {
            "content_type": content_type,
            "content_preview": content[:100],
            **extra,
        })

    def record_content_rejected(
        self, content: str, reason: str, violations: Optional[List[str]] = None
    ) -> Optional[LedgerEvent]:
        """Record content rejection by governance."""
        return self.commit("content_rejected", {
            "content_preview": content[:100],
            "reason": reason,
            "violations": violations or [],
        })

    def record_engagement(self, action: str, target: str, **extra: Any) -> Optional[LedgerEvent]:
        """Record social engagement (follow, vote, subscribe)."""
        return self.commit("engagement_completed", {
            "action": action,
            "target": target,
            **extra,
        })

    def record_error(self, error_type: str, message: str) -> Optional[LedgerEvent]:
        """Record system error."""
        return self.commit("system_error", {
            "error_type": error_type,
            "message": message[:200],
        })

    def store_validation_feedback(self, violations: List[str], draft: Optional[str] = None) -> None:
        """Store feedback from failed governance check for next retry."""
        self.pending_validation_feedback = {
            "violations": violations,
            "draft": draft,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_last_validation_feedback(self) -> Optional[Dict[str, Any]]:
        """Retrieve and consume last validation feedback."""
        feedback = self.pending_validation_feedback
        self.pending_validation_feedback = None
        return feedback

    def get_recent_events(self, limit: int = 20) -> List[LedgerEvent]:
        """Get the most recent events from the ledger."""
        events: List[LedgerEvent] = []
        if not self.ledger_path.exists():
            return events
        try:
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()
            for line in lines[-limit:]:
                if line.strip():
                    data = json.loads(line.strip())
                    events.append(LedgerEvent(**data))
        except Exception as e:
            logger.warning(f"Event read failed: {e}")
        return events

    def rebuild_state(self) -> Dict[str, Any]:
        """Reconstruct state by replaying all events."""
        state: Dict[str, Any] = {
            "content_generated": 0,
            "content_published": 0,
            "content_rejected": 0,
            "engagements": 0,
            "errors": 0,
            "last_activity": None,
        }
        for event in self.get_recent_events(limit=10000):
            et = event.event_type
            if et == "content_generated":
                state["content_generated"] += 1
            elif et == "content_published":
                state["content_published"] += 1
            elif et == "content_rejected":
                state["content_rejected"] += 1
            elif et == "engagement_completed":
                state["engagements"] += 1
            elif et == "system_error":
                state["errors"] += 1
            state["last_activity"] = event.timestamp
        return state


_event_log: Optional[EventLog] = None


def get_event_log(ledger_path: Optional[Path] = None) -> EventLog:
    """Get Moltbook EventLog singleton."""
    global _event_log
    if _event_log is None:
        _event_log = EventLog(ledger_path)
    return _event_log
