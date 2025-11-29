"""
HERALD Memory Module - Event Sourcing and State Reconstruction.

Event Sourcing Pattern:
- Every action (content_generated, published, rejected, etc.) creates an immutable Event
- Events are cryptographically signed and stored in data/events/herald.jsonl
- Agent memory is reconstructed by replaying events from line 0 to N
- If HERALD crashes, it can rebuild its complete state from the ledger

This makes HERALD's behavior auditable and deterministic.
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


logger = logging.getLogger("HERALD_MEMORY")


@dataclass
class Event:
    """
    Immutable event representing an action taken by HERALD.

    Attributes:
        event_type: Type of event (content_generated, published, rejected, etc.)
        timestamp: ISO 8601 timestamp when event occurred
        agent_id: HERALD agent identifier
        payload: Event-specific data (content, platform, etc.)
        signature: Cryptographic signature of event (NIST P-256)
        sequence_number: Monotonic counter for ordering
    """

    event_type: str
    timestamp: str
    agent_id: str
    payload: Dict[str, Any]
    signature: Optional[str] = None
    sequence_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(self.to_dict(), default=str)


class EventLog:
    """
    Immutable event ledger for HERALD.

    Implements the Event Sourcing pattern:
    - All actions are recorded as signed events
    - Events are stored in append-only JSONL file
    - State is reconstructed by replaying events
    - No mutable database needed
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        """
        Initialize the event log.

        Args:
            ledger_path: Path to the JSONL event ledger file.
                        Defaults to data/events/herald.jsonl
        """
        if ledger_path is None:
            ledger_path = Path("data/events/herald.jsonl")

        self.ledger_path = Path(ledger_path)
        self.agent_id = "agent.steward.herald"
        self.sequence_counter = 0

        # Validation feedback for retry loops (in-memory, consumed on retrieval)
        self.pending_validation_feedback: Optional[Dict[str, Any]] = None

        # Create ledger directory if it doesn't exist
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing ledger and count events
        self._reload_sequence_counter()

        logger.info(f"📖 EventLog initialized at {self.ledger_path}")
        logger.info(f"   Events in ledger: {self.sequence_counter}")

    def _reload_sequence_counter(self):
        """Reload sequence counter from existing ledger."""
        if self.ledger_path.exists():
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()
                self.sequence_counter = len(lines)
                logger.debug(f"   Loaded {self.sequence_counter} events from ledger")

    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Event:
        """
        Create a new event (not yet committed to ledger).

        Args:
            event_type: Type of event (e.g., "content_generated", "published", "rejected")
            payload: Event-specific data

        Returns:
            Event object (not yet signed or stored)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        event = Event(
            event_type=event_type,
            timestamp=timestamp,
            agent_id=self.agent_id,
            payload=payload,
            sequence_number=self.sequence_counter + 1,
        )

        return event

    def sign_event(self, event: Event) -> Event:
        """
        Sign an event with HERALD's cryptographic identity.

        Args:
            event: Event to sign

        Returns:
            Event with signature added
        """
        if sign_content is None:
            logger.warning("⚠️  Steward crypto not available - event will be unsigned")
            return event

        try:
            # Create signature data from event (excluding signature field)
            event_data = {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "agent_id": event.agent_id,
                "payload": event.payload,
                "sequence_number": event.sequence_number,
            }
            event_json = json.dumps(event_data, sort_keys=True, default=str)

            # Sign the event
            signature = sign_content(event_json)
            event.signature = signature

            logger.debug(
                f"✅ Event signed: {event.event_type} (#{event.sequence_number})"
            )
            return event

        except Exception as e:
            logger.warning(f"⚠️  Failed to sign event: {e}")
            return event

    def commit(self, event: Event) -> bool:
        """
        Commit an event to the ledger (append-only).

        This is the atomic operation - once committed, events cannot be modified.

        Args:
            event: Event to commit

        Returns:
            True if successfully committed, False otherwise
        """
        try:
            # Ensure event is signed
            if event.signature is None:
                event = self.sign_event(event)

            # Increment sequence counter
            self.sequence_counter += 1
            event.sequence_number = self.sequence_counter

            # Append to ledger
            with open(self.ledger_path, "a") as f:
                f.write(event.to_json() + "\n")

            logger.info(
                f"📝 Event committed #{event.sequence_number}: {event.event_type}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to commit event: {e}")
            return False

    def get_event_by_sequence(self, sequence_number: int) -> Optional[Event]:
        """
        Retrieve a specific event by sequence number.

        Args:
            sequence_number: Sequence number of the event (1-indexed)

        Returns:
            Event object or None if not found
        """
        if not self.ledger_path.exists():
            return None

        try:
            with open(self.ledger_path, "r") as f:
                for idx, line in enumerate(f, start=1):
                    if idx == sequence_number:
                        data = json.loads(line.strip())
                        return Event(**data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve event {sequence_number}: {e}")
            return None

    def get_all_events(self) -> List[Event]:
        """
        Retrieve all events from the ledger.

        Returns:
            List of all Event objects in order
        """
        events = []
        if not self.ledger_path.exists():
            return events

        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        events.append(Event(**data))
            return events
        except Exception as e:
            logger.error(f"❌ Failed to retrieve all events: {e}")
            return events

    def get_events_by_type(self, event_type: str) -> List[Event]:
        """
        Retrieve all events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of Event objects matching the type
        """
        all_events = self.get_all_events()
        return [e for e in all_events if e.event_type == event_type]

    def get_recent_events(self, limit: int = 10) -> List[Event]:
        """
        Retrieve the most recent events.

        Args:
            limit: Number of recent events to retrieve

        Returns:
            List of recent Event objects
        """
        all_events = self.get_all_events()
        return all_events[-limit:] if len(all_events) > limit else all_events

    def rebuild_state(self) -> Dict[str, Any]:
        """
        Rebuild HERALD's state by replaying all events from the ledger.

        This is called on startup to restore agent state after a crash.

        Returns:
            Dict with reconstructed state
        """
        state = {
            "agent_id": self.agent_id,
            "content_generated": 0,
            "content_published": 0,
            "content_rejected": 0,
            "last_activity": None,
            "last_failure": None,
            "safe_mode": False,
        }

        events = self.get_all_events()
        logger.info(f"🔄 Rebuilding state from {len(events)} events...")

        for event in events:
            if event.event_type == "content_generated":
                state["content_generated"] += 1
                state["last_activity"] = event.timestamp

            elif event.event_type == "content_published":
                state["content_published"] += 1
                state["last_activity"] = event.timestamp

            elif event.event_type == "content_rejected":
                state["content_rejected"] += 1
                state["last_activity"] = event.timestamp
                state["last_failure"] = event.timestamp

            elif event.event_type == "system_error":
                state["last_failure"] = event.timestamp
                state["safe_mode"] = True
                logger.warning(f"⚠️  System error recorded at {event.timestamp}")

        logger.info(
            f"✅ State rebuilt: {state['content_generated']} generated, "
            f"{state['content_published']} published, "
            f"{state['content_rejected']} rejected"
        )

        if state["safe_mode"]:
            logger.warning("⚠️  Safe Mode enabled due to recent failures")

        return state

    def record_content_generated(
        self,
        content: str,
        platform: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Event]:
        """
        Record that HERALD generated content.

        Args:
            content: The generated content
            platform: Target platform (twitter, reddit, etc.)
            context: Optional metadata

        Returns:
            Event object if successfully recorded, None otherwise
        """
        event = self.create_event(
            event_type="content_generated",
            payload={
                "content": content[:100] + "..." if len(content) > 100 else content,
                "platform": platform,
                "content_length": len(content),
                "context": context or {},
            },
        )
        if self.commit(event):
            return event
        return None

    def record_content_published(
        self,
        content: str,
        platform: str,
        post_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Event]:
        """
        Record that HERALD published content.

        Args:
            content: The published content
            platform: Platform it was published to
            post_id: Identifier of the post on the platform
            metadata: Optional metadata

        Returns:
            Event object if successfully recorded, None otherwise
        """
        event = self.create_event(
            event_type="content_published",
            payload={
                "content": content[:100] + "..." if len(content) > 100 else content,
                "platform": platform,
                "post_id": post_id,
                "metadata": metadata or {},
            },
        )
        if self.commit(event):
            return event
        return None

    def record_content_rejected(
        self,
        content: str,
        reason: str,
        violations: Optional[List[str]] = None,
    ) -> Optional[Event]:
        """
        Record that HERALD rejected content due to governance violations.

        Args:
            content: The rejected content
            reason: Reason for rejection
            violations: List of specific governance violations

        Returns:
            Event object if successfully recorded, None otherwise
        """
        event = self.create_event(
            event_type="content_rejected",
            payload={
                "content": content[:100] + "..." if len(content) > 100 else content,
                "reason": reason,
                "violations": violations or [],
            },
        )
        if self.commit(event):
            return event
        return None

    def record_system_error(
        self,
        error_type: str,
        error_message: str,
        traceback: Optional[str] = None,
    ) -> Optional[Event]:
        """
        Record a system error.

        Args:
            error_type: Type of error (e.g., "api_error", "governance_failure")
            error_message: Error message
            traceback: Optional traceback information

        Returns:
            Event object if successfully recorded, None otherwise
        """
        event = self.create_event(
            event_type="system_error",
            payload={
                "error_type": error_type,
                "error_message": error_message,
                "traceback": traceback,
            },
        )
        if self.commit(event):
            return event
        return None

    def store_validation_feedback(
        self, violations: List[str], draft: Optional[str] = None
    ) -> None:
        """
        Store validation feedback from a failed governance check.

        This feedback will be retrieved by the next PROCESS cycle to generate better content.
        Feedback is consumed (cleared) when retrieved, preventing stale feedback.

        Args:
            violations: List of governance violations from HeraldConstitution.validate()
            draft: Optional draft content that failed validation
        """
        self.pending_validation_feedback = {
            "violations": violations,
            "draft": draft,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(
            f"📋 Validation feedback stored: {len(violations)} violations to fix in next cycle"
        )

    def get_last_validation_feedback(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve and consume the last validation feedback.

        This is called by the PROCESS phase to understand what went wrong in the previous
        failed validation. After retrieval, the feedback is cleared to prevent reusing stale data.

        Returns:
            Dict with "violations" and "draft" if feedback exists, None otherwise
        """
        if self.pending_validation_feedback is None:
            return None

        feedback = self.pending_validation_feedback
        self.pending_validation_feedback = None  # Consume the feedback

        logger.info(
            f"⚠️  Retrieved validation feedback: {len(feedback['violations'])} violations to address"
        )
        return feedback


def get_event_log(ledger_path: Optional[Path] = None) -> EventLog:
    """Get the HERALD EventLog instance (singleton pattern)."""
    return EventLog(ledger_path)
