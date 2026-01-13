"""UnifiedTrace - GAD-000 Test 2: AI-readable execution traces.

This module provides the central infrastructure for system observability.
It allows the kernel and executors to emit structured events that can be:
1. Parsed by AI (for self-correction)
2. Visualized by UI (for human debug)
3. Persisted to Ledger (for history)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x81f6ae7e"  # GenesisByte: parampara % 37 == 0

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TraceEvent:
    """A single event in the execution trace."""

    trace_id: str
    timestamp: float
    component: str  # e.g., "router", "executor", "agent"
    event_type: str  # e.g., "start", "complete", "error"
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to machine-readable dictionary."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "component": self.component,
            "event_type": self.event_type,
            "data": self.data,
        }


class UnifiedTrace:
    """Central nervous system for AI observability.

    Collects and manages execution traces across the system.
    """

    def __init__(self):
        # In-memory storage for active/recent traces
        # structure: {trace_id: [Event, Event, ...]}
        self._traces: Dict[str, List[TraceEvent]] = {}

    def start(self, component: str, event_type: str = "start", data: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace or execution span.

        Args:
            component: The system component initiating the action
            event_type: Type of start event (default: "start")
            data: Supplemental context data

        Returns:
            trace_id: Unique ID for this execution span
        """
        trace_id = str(uuid.uuid4())[:8]
        event = TraceEvent(
            trace_id=trace_id,
            timestamp=time.time(),
            component=component,
            event_type=event_type,
            data=data or {},
        )
        self._traces[trace_id] = [event]
        return trace_id

    def emit(self, trace_id: str, component: str, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to an existing trace.

        Args:
            trace_id: The active trace ID
            component: The system component emitting the event
            event_type: Type of event (e.g., "step", "retry")
            data: Event data
        """
        if trace_id not in self._traces:
            # Fallback for untracked/orphan events
            self._traces[trace_id] = []

        event = TraceEvent(
            trace_id=trace_id,
            timestamp=time.time(),
            component=component,
            event_type=event_type,
            data=data or {},
        )
        self._traces[trace_id].append(event)

    def complete(self, trace_id: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Mark a trace as completed successfully.

        Args:
            trace_id: The trace to complete
            data: Result data
        """
        self.emit(
            trace_id=trace_id,
            component="system",  # System marks completion
            event_type="complete",
            data=data,
        )

    def error(self, trace_id: str, error: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Mark a trace as failed.

        Args:
            trace_id: The trace that failed
            error: Error message
            data: Additional error context
        """
        payload = data or {}
        payload["error"] = error
        self.emit(
            trace_id=trace_id,
            component="system",
            event_type="error",
            data=payload,
        )

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get the full history of a trace in machine-readable format.

        This is the primary GAD-000 observability API for AI agents.

        Args:
            trace_id: ID of the trace to retrieve

        Returns:
            List of event dictionaries
        """
        events = self._traces.get(trace_id, [])
        return [e.to_dict() for e in events]
