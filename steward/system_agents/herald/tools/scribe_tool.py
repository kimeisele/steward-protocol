"""
Auto-Scribe: Translates technical events into living documentation.

The Scribe projects HERALD's activity into human-readable logbook entries,
ensuring that GitHub visitors see the agent's heartbeat in real-time.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import json

from ..core.memory import Event


class Scribe:
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

    def log_action(self, event: Event) -> bool:
        """
        Log an event as a chronicle entry in the logbook section.

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
            print(f"❌ Scribe failed to log event: {e}")
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
            return (
                f"content regarding '{content}...'"
                if len(content) > 0
                else f"content on {platform}"
            )

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
        future_marker = "## Future Entries"

        if logbook_marker not in content:
            # Logbook section doesn't exist, create it
            # Insert after the main entry section and before "## Future Entries"
            if future_marker in content:
                # Insert before "## Future Entries"
                updated_content = content.replace(
                    f"\n{future_marker}",
                    f"\n{logbook_marker}\n\n{entry}\n\n{future_marker}",
                )
            else:
                # Append before final section
                closing_marker = "\n---\n\n*The Chronicles are"
                if closing_marker in content:
                    updated_content = content.replace(
                        closing_marker,
                        f"\n{logbook_marker}\n\n{entry}\n{closing_marker}",
                    )
                else:
                    # Just append before the last line
                    lines = content.rstrip().split("\n")
                    lines.insert(-2, f"\n{logbook_marker}\n\n{entry}\n")
                    updated_content = "\n".join(lines)
        else:
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
                    if (
                        next_marker_idx + 1 < len(lines)
                        and lines[next_marker_idx + 1].strip()
                    ):
                        lines.insert(next_marker_idx + 1, "")

                updated_content = "\n".join(lines)
            else:
                # This shouldn't happen, but fallback
                updated_content = content + f"\n{entry}\n"

        # Write back
        self.chronicle_path.write_text(updated_content, encoding="utf-8")

    def initialize_logbook_section(self) -> None:
        """
        Initialize the logbook section in chronicles.md if it doesn't exist.

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
                updated_content = content.replace(
                    f"\n{future_marker}", f"\n{logbook_section}\n{future_marker}"
                )
            else:
                closing_marker = "\n---\n\n*The Chronicles are"
                updated_content = content.replace(
                    closing_marker, f"\n{logbook_section}{closing_marker}"
                )

            self.chronicle_path.write_text(updated_content, encoding="utf-8")
