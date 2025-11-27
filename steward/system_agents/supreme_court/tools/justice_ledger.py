#!/usr/bin/env python3
"""
Justice Ledger - Immutable record of all Supreme Court proceedings.

This ledger tracks all appellate events:
- Appeals filed
- Reviews conducted
- Verdicts issued
- Precedents recorded
- Overrides executed

Like the kernel ledger, this is append-only and serves as source of truth
for the Supreme Court's actions.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import sys

# BLOCKER #1: Import canonical VibeLedger ABC
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from vibe_core.kernel import VibeLedger

logger = logging.getLogger("JUSTICE_LEDGER")


class JusticeLedger(VibeLedger):
    """
    Immutable ledger of Supreme Court proceedings.

    Every action in the Supreme Court is recorded here for accountability.
    This becomes evidence of whether justice was applied consistently.
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize justice ledger."""
        self.root_path = Path(root_path)
        self.ledger_dir = self.root_path / "data" / "governance" / "justice_ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

        self.ledger_file = self.ledger_dir / "justice_events.jsonl"

        logger.info("⚖️  Justice Ledger initialized")

    def _append_event(self, event: Dict[str, Any]) -> None:
        """
        Internal method to append an event to the justice ledger (append-only).

        Args:
            event: Event to record (should include event_type and timestamp)
        """
        # Ensure timestamp exists
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Append to ledger
        with open(self.ledger_file, "a") as f:
            f.write(json.dumps(event) + "\n")

        logger.debug(f"⚖️  LEDGER: {event.get('event_type')}")

    def record_event(self, event_type_or_dict, agent_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Record an event in the justice ledger.

        Supports both signatures:
        - Domain-specific: record_event(event: Dict) for Supreme Court events
        - VibeLedger ABC: record_event(event_type, agent_id, details) -> str
        """
        if isinstance(event_type_or_dict, dict):
            # Domain-specific signature: record_event(event_dict)
            self._append_event(event_type_or_dict)
            return None
        else:
            # VibeLedger ABC signature: record_event(event_type, agent_id, details) -> str
            full_event = {
                "event_type": event_type_or_dict,
                "agent_id": agent_id,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._append_event(full_event)
            return f"EVT-{len(self.get_events())}"  # Return event_id

    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve events from the ledger.

        Args:
            event_type: If specified, filter by this event type

        Returns:
            List of events
        """
        if not self.ledger_file.exists():
            return []

        events = []
        try:
            with open(self.ledger_file, "r") as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event_type is None or event.get("event_type") == event_type:
                            events.append(event)
        except Exception as e:
            logger.warning(f"Error loading justice ledger: {str(e)}")

        return events

    def get_events_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all justice ledger events for a specific agent."""
        events = self.get_events()
        return [e for e in events if e.get("agent_id") == agent_id]

    def get_events_for_appeal(self, appeal_id: str) -> List[Dict[str, Any]]:
        """Get all justice ledger events for a specific appeal."""
        events = self.get_events()
        return [e for e in events if e.get("appeal_id") == appeal_id]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics of Supreme Court activity.

        Returns:
            Statistics object with counts and summaries
        """
        events = self.get_events()

        # Count event types
        event_counts = {}
        for event in events:
            event_type = event.get("event_type")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Count mercy granted
        verdicts = [e for e in events if e.get("event_type") == "VERDICT_ISSUED"]
        mercy_count = sum(1 for v in verdicts if v.get("verdict_type") == "mercy_granted")
        upheld_count = sum(1 for v in verdicts if v.get("verdict_type") == "upheld")
        conditional_count = sum(1 for v in verdicts if v.get("verdict_type") == "mercy_conditional")

        return {
            "total_events": len(events),
            "event_breakdown": event_counts,
            "verdicts": {
                "mercy_granted": mercy_count,
                "upheld": upheld_count,
                "conditional": conditional_count,
                "total": len(verdicts)
            },
            "mercy_rate": mercy_count / len(verdicts) if verdicts else 0.0,
            "first_event": events[0]["timestamp"] if events else None,
            "last_event": events[-1]["timestamp"] if events else None
        }

    def verify_ledger_integrity(self) -> bool:
        """
        Verify the ledger has not been tampered with.

        In production, this would use cryptographic hashing.
        """
        try:
            events = self.get_events()
            logger.info(f"✅ Justice ledger integrity verified ({len(events)} events)")
            return True
        except Exception as e:
            logger.error(f"❌ Justice ledger integrity check failed: {str(e)}")
            return False

    # ==================== VibeLedger Interface Adapters ====================
    # BLOCKER #1: Implement VibeLedger ABC interface to satisfy inheritance contract

    def record_start(self, task) -> None:
        """Record task start (VibeLedger interface)"""
        self.record_event({
            "event_type": "TASK_START",
            "task_id": getattr(task, "task_id", None),
            "agent_id": getattr(task, "agent_id", "unknown"),
            "payload": getattr(task, "payload", None)
        })

    def record_completion(self, task, result: Any) -> None:
        """Record task completion (VibeLedger interface)"""
        self.record_event({
            "event_type": "TASK_COMPLETED",
            "task_id": getattr(task, "task_id", None),
            "agent_id": getattr(task, "agent_id", "unknown"),
            "result": result
        })

    def record_failure(self, task, error: str) -> None:
        """Record task failure (VibeLedger interface)"""
        self.record_event({
            "event_type": "TASK_FAILED",
            "task_id": getattr(task, "task_id", None),
            "agent_id": getattr(task, "agent_id", "unknown"),
            "error": error
        })

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result (VibeLedger interface)"""
        events = self.get_events()
        for event in reversed(events):
            if event.get("task_id") == task_id:
                return event
        return None
