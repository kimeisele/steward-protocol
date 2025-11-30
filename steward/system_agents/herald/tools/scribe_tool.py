"""
Auto-Scribe: Translates technical events into living documentation (Tool Protocol).

The Scribe projects HERALD's activity into human-readable logbook entries,
ensuring that GitHub visitors see the agent's heartbeat in real-time.

This tool implements the Tool Protocol for kernel-managed execution.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

# Import Event with absolute path
try:
    from steward.system_agents.herald.core.memory import Event
except ImportError:
    # Fallback: define minimal Event dataclass for testing
    from dataclasses import dataclass

    @dataclass
    class Event:
        event_type: str
        timestamp: str
        agent_id: str
        payload: Dict[str, Any]
        signature: Optional[str] = None
        sequence_number: Optional[int] = None


logger = logging.getLogger("HERALD_SCRIBE")


class Scribe(Tool):
    """
    Translates Event objects into human-readable Chronicle entries.

    Purpose:
    - Bridge technical event logs with human-facing documentation
    - Create automatic living documentation from agent activities
    - Demonstrate "liveness" of the system to external observers
    """

    # Event type to emoji mapping
    EVENT_EMOJIS = {
        "content_generated": "✍️",
        "content_published": "🚀",
        "content_rejected": "⚠️",
        "system_error": "🔴",
    }

    # Event type to action verb mapping
    EVENT_ACTIONS = {
        "content_generated": "generated",
        "content_published": "published",
        "content_rejected": "rejected",
        "system_error": "encountered",
    }

    def __init__(self, chronicle_path: Optional[Path] = None):
        """
        Initialize the Scribe.

        Args:
            chronicle_path: Path to docs/chronicles.md
        """
        self.chronicle_path = chronicle_path or Path("docs/chronicles.md")

    @property
    def name(self) -> str:
        return "herald.scribe"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Translate technical events into living documentation - log actions, initialize logbook"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'log_action', 'initialize_logbook'",
            },
            "event_data": {
                "type": "object",
                "required": False,
                "description": "Event data dict (required for log_action): event_type, timestamp, agent_id, payload, signature, sequence_number",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate scribe parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["log_action", "initialize_logbook"]:
            raise ValueError(f"Invalid action: {action}. Must be 'log_action' or 'initialize_logbook'")

        # Validate action-specific parameters
        if action == "log_action":
            if "event_data" not in parameters:
                raise ValueError("log_action requires 'event_data' parameter")
            if not isinstance(parameters["event_data"], dict):
                raise TypeError("event_data must be a dictionary")

            # Validate required event fields
            event_data = parameters["event_data"]
            required_fields = ["event_type", "timestamp", "agent_id", "payload"]
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"event_data missing required field: {field}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute scribe operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with operation results
        """
        try:
            action = parameters["action"]

            if action == "log_action":
                event_data = parameters["event_data"]

                # Create Event object from dict
                event = Event(
                    event_type=event_data["event_type"],
                    timestamp=event_data["timestamp"],
                    agent_id=event_data["agent_id"],
                    payload=event_data["payload"],
                    signature=event_data.get("signature"),
                    sequence_number=event_data.get("sequence_number"),
                )

                success = self._log_action(event)

                if success:
                    return ToolResult(
                        success=True,
                        output={
                            "logged": True,
                            "event_type": event.event_type,
                            "chronicle_path": str(self.chronicle_path),
                        },
                        metadata={
                            "action": "log_action",
                            "event_type": event.event_type,
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Failed to log event to chronicle",
                    )

            elif action == "initialize_logbook":
                self._initialize_logbook_section()

                return ToolResult(
                    success=True,
                    output={
                        "initialized": True,
                        "chronicle_path": str(self.chronicle_path),
                        "exists": self.chronicle_path.exists(),
                    },
                    metadata={
                        "action": "initialize_logbook",
                    },
                )

        except Exception as e:
            error_msg = f"Scribe operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"Scribe: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _log_action(self, event: Event) -> bool:
        """
        Internal method: Log an event as a chronicle entry in the logbook section.

        Args:
            event: The Event to document

        Returns:
            bool: True if successfully logged, False otherwise
        """
        try:
            entry = self._format_logbook_entry(event)
            self._append_to_logbook(entry)
            return True
        except Exception as e:
            logger.error(f"❌ Scribe failed to log event: {e}")
            return False

    def _format_logbook_entry(self, event: Event) -> str:
        """
        Format an Event as a markdown logbook entry.

        Format:
        * **YYYY-MM-DD HH:MM UTC:** 📝 ACTION description. (Ref: 0x12345678)

        Args:
            event: The Event to format

        Returns:
            str: Formatted markdown entry
        """
        # Parse ISO timestamp
        timestamp = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M UTC")

        # Get emoji and action
        emoji = self.EVENT_EMOJIS.get(event.event_type, "📌")
        action = self.EVENT_ACTIONS.get(event.event_type, "recorded").upper()

        # Extract description from payload
        description = self._describe_event(event)

        # Create reference from signature
        reference = self._create_reference(event)

        # Construct the entry
        entry = f"* **{formatted_time}:** {emoji} {action} {description}. (Ref: {reference})"

        return entry

    def _describe_event(self, event: Event) -> str:
        """
        Extract human-readable description from an Event's payload.

        Args:
            event: The Event to describe

        Returns:
            str: Description of the event
        """
        payload = event.payload

        if event.event_type == "content_generated":
            content = payload.get("content", "")[:60]
            platform = payload.get("platform", "unknown").upper()
            return f"content regarding '{content}...'" if len(content) > 0 else f"content on {platform}"

        elif event.event_type == "content_published":
            content = payload.get("content", "")[:60]
            platform = payload.get("platform", "unknown").upper()
            return f"content regarding '{content}...' to {platform}"

        elif event.event_type == "content_rejected":
            reason = payload.get("reason", "unknown reason")
            violations = payload.get("violations", [])
            violation_str = ", ".join(violations[:2]) if violations else reason
            return f"content due to: {violation_str}"

        elif event.event_type == "system_error":
            error_type = payload.get("error_type", "unknown error")
            error_msg = payload.get("error_message", "")[:50]
            return f"error [{error_type}]: {error_msg}"

        return "event of unknown type"

    def _create_reference(self, event: Event) -> str:
        """
        Create a short reference identifier for an event.

        Args:
            event: The Event to reference

        Returns:
            str: Short reference (0x prefix + first 8 chars of signature)
        """
        if event.signature:
            return f"0x{event.signature[:8]}"
        elif event.sequence_number:
            return f"0x{event.sequence_number:08x}"
        else:
            return "0xUNKNOWN"

    def _append_to_logbook(self, entry: str) -> None:
        """
        Append a formatted entry to the logbook section in chronicles.md.

        The logbook section comes after "## Logbook" and before any future sections.
        If no logbook section exists, create one after the main entry.

        Args:
            entry: The formatted markdown entry to append
        """
        if not self.chronicle_path.exists():
            # Initialize the file first
            self.initialize_logbook_section()

        # Read current content
        content = self.chronicle_path.read_text(encoding="utf-8")

        # Check if logbook section exists
        logbook_marker = "## Logbook"

        if logbook_marker not in content:
            # Logbook section doesn't exist, create it via initialize
            self._initialize_logbook_section()
            content = self.chronicle_path.read_text(encoding="utf-8")

        # Now append to existing logbook section
        if logbook_marker in content:
            # Logbook section exists, append to it
            # Find the logbook section and insert before the next ## marker
            lines = content.split("\n")
            logbook_idx = None

            for i, line in enumerate(lines):
                if line.startswith(logbook_marker):
                    logbook_idx = i
                    break

            if logbook_idx is not None:
                # Find the next ## marker after logbook section
                next_marker_idx = None
                for i in range(logbook_idx + 1, len(lines)):
                    if lines[i].startswith("## "):
                        next_marker_idx = i
                        break

                if next_marker_idx is None:
                    # No next marker found, append at end
                    lines.append(entry)
                else:
                    # Insert before next marker with blank line separator
                    lines.insert(next_marker_idx, entry)
                    # Add blank line after entry if next marker doesn't have one
                    if next_marker_idx + 1 < len(lines) and lines[next_marker_idx + 1].strip():
                        lines.insert(next_marker_idx + 1, "")

                updated_content = "\n".join(lines)
            else:
                # This shouldn't happen, but fallback
                updated_content = content + f"\n{entry}\n"
        else:
            # Still no logbook after init - shouldn't happen
            updated_content = content + f"\n{entry}\n"

        # Write back
        self.chronicle_path.write_text(updated_content, encoding="utf-8")

    def _initialize_logbook_section(self) -> None:
        """
        Internal method: Initialize the logbook section in chronicles.md.

        Creates a "## Logbook" section where Auto-Scribe entries are appended.
        If the file doesn't exist, creates it with a basic template.
        """
        if not self.chronicle_path.exists():
            # Create the file with a basic template
            self.chronicle_path.parent.mkdir(parents=True, exist_ok=True)
            template = """# HERALD Chronicles

This is the living documentation of HERALD's autonomous activity.

## Logbook

Autonomous activity log:

---

*The Chronicles are automatically updated by the Auto-Scribe.*
"""
            self.chronicle_path.write_text(template, encoding="utf-8")
            return

        content = self.chronicle_path.read_text(encoding="utf-8")

        if "## Logbook" not in content:
            # Create the logbook section after the first entry
            future_marker = "## Future Entries"
            logbook_section = "\n## Logbook\n\nAutonomous activity log:\n"

            if future_marker in content:
                updated_content = content.replace(f"\n{future_marker}", f"\n{logbook_section}\n{future_marker}")
            else:
                closing_marker = "\n---\n\n*The Chronicles are"
                updated_content = content.replace(closing_marker, f"\n{logbook_section}{closing_marker}")

            self.chronicle_path.write_text(updated_content, encoding="utf-8")

    # Fix the _append_to_logbook method that was left incomplete
    def _append_to_logbook_OLD_DELETED(self, entry: str) -> None:
        """
        DEPRECATED: This method was refactored above.
        Kept for reference only - do not use.
        """
        pass

    def _append_to_logbook(self, entry: str) -> None:
        """
        Append a formatted entry to the logbook section in chronicles.md.

        Args:
            entry: The formatted markdown entry to append
        """
        if not self.chronicle_path.exists():
            # Initialize the file first
            self._initialize_logbook_section()

        # Read current content
        content = self.chronicle_path.read_text(encoding="utf-8")

        # Check if logbook section exists
        logbook_marker = "## Logbook"

        if logbook_marker not in content:
            # Initialize logbook if missing
            self._initialize_logbook_section()
            content = self.chronicle_path.read_text(encoding="utf-8")

        # Find and append to logbook
        lines = content.split("\n")
        logbook_idx = None

        for i, line in enumerate(lines):
            if line.startswith(logbook_marker):
                logbook_idx = i
                break

        if logbook_idx is not None:
            # Find next section or end
            next_marker_idx = None
            for i in range(logbook_idx + 1, len(lines)):
                if lines[i].startswith("## "):
                    next_marker_idx = i
                    break

            if next_marker_idx is None:
                lines.append(entry)
            else:
                lines.insert(next_marker_idx, entry)
                if next_marker_idx + 1 < len(lines) and lines[next_marker_idx + 1].strip():
                    lines.insert(next_marker_idx + 1, "")

            updated_content = "\n".join(lines)
        else:
            updated_content = content + f"\n{entry}\n"

        self.chronicle_path.write_text(updated_content, encoding="utf-8")
