"""
OPUS Observation Logger - The System's "Journal".

Phase 2.5: Not just reports - a living diary.

This module provides the "soft interaction" that makes OPUS.md feel alive.
Instead of just static verification tables, the system can now LOG
observations, warnings, and insights directly into OPUS.md.

The "🧠 System Observations" section is:
- Append-only (new entries added, old preserved)
- Timestamped (when did the system notice this?)
- Severity-tagged (INFO, WARN, ALERT, INSIGHT)

This is the "watcher" that notices patterns and anomalies.

Architecture (Spaghetti Prevention):
    ┌─────────────────────────────────┐
    │      OpusContextService         │  ← Aggregates state (DUMB)
    │      (No analysis logic!)       │
    └──────────────┬──────────────────┘
                   │ feeds
                   ▼
    ┌─────────────────────────────────┐
    │      ObservationLogger          │  ← Writes journal (FOCUSED)
    │      (Only logging, no analysis)│
    └──────────────┬──────────────────┘
                   │ appends to
                   ▼
    ┌─────────────────────────────────┐
    │         OPUS.md                 │
    │  ## 🧠 System Observations      │  ← Human/AI readable journal
    │  (Append-only, timestamped)     │
    └─────────────────────────────────┘

If you need analysis logic, put it in a SEPARATE AnomalyDetector!
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

logger = logging.getLogger("OPUS_JOURNAL")

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.core.state_manager import OpusStateManager


class ObservationSeverity(Enum):
    """Severity levels for observations."""

    INFO = "ℹ️"  # Normal operational info
    WARN = "⚠️"  # Something to watch
    ALERT = "🚨"  # Needs attention
    INSIGHT = "💡"  # AI-generated insight


@dataclass
class Observation:
    """A single observation entry."""

    timestamp: str
    severity: ObservationSeverity
    message: str
    source: str = "opus_assistant"  # Which component logged this
    context_hash: Optional[str] = None  # Link to context snapshot

    def to_markdown(self) -> str:
        """Format as markdown line for OPUS.md."""
        ts_short = self.timestamp[:19]  # Trim to YYYY-MM-DDTHH:MM:SS
        return f"- `{ts_short}` {self.severity.value} **[{self.source}]** {self.message}"


@dataclass
class ObservationJournal:
    """Collection of observations for a session."""

    observations: List[Observation] = field(default_factory=list)
    max_entries: int = 50  # Keep journal manageable

    def add(self, observation: Observation) -> None:
        """Add observation, maintaining max size (FIFO)."""
        self.observations.append(observation)
        if len(self.observations) > self.max_entries:
            self.observations = self.observations[-self.max_entries :]

    def to_markdown(self) -> str:
        """Format journal as markdown section."""
        if not self.observations:
            return "_No observations yet._"

        lines = []
        for obs in reversed(self.observations):  # Most recent first
            lines.append(obs.to_markdown())

        return "\n".join(lines)


class ObservationLogger:
    """
    Logs observations to OPUS.md's journal section.

    This is the "soft interaction" - the system talking to humans.
    NOT a God Class - only handles logging, nothing else.

    Usage:
        logger = ObservationLogger(workspace_root=Path("."))
        logger.log_observation(
            severity=ObservationSeverity.WARN,
            message="Drift detected between docs/X.md and src/X.py",
            source="drift_detector"
        )
        logger.flush_to_opus()  # Write to OPUS.md
    """

    # Section markers for OPUS.md
    JOURNAL_START = "<!-- @JOURNAL START -->"
    JOURNAL_END = "<!-- @JOURNAL END -->"
    SECTION_HEADER = "## 🧠 System Observations"

    def __init__(
        self,
        workspace_root: Path,
        max_entries: int = 50,
        state_manager: Optional["OpusStateManager"] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize observation logger.

        Args:
            workspace_root: Workspace path
            max_entries: Max observations to keep (FIFO)
            state_manager: Optional StateManager for persistence (Fractal Holon pattern)
        """
        self._workspace = workspace_root
        self._opus_path = workspace_root / "OPUS.md"
        self._config = config or {}
        self._journal = ObservationJournal(max_entries=max_entries)
        self._pending_flush = False
        self._state_manager = state_manager

    def log_observation(
        self,
        severity: ObservationSeverity,
        message: str,
        source: str = "opus_assistant",
        context_hash: Optional[str] = None,
    ) -> None:
        """
        Log an observation to the journal.

        Args:
            severity: Observation severity level
            message: Human-readable message
            source: Component that logged this
            context_hash: Optional link to context snapshot
        """
        observation = Observation(
            timestamp=datetime.now().isoformat(),
            severity=severity,
            message=message,
            source=source,
            context_hash=context_hash,
        )
        self._journal.add(observation)
        self._pending_flush = True

        # Also log to Python logger
        level = {
            ObservationSeverity.INFO: logging.INFO,
            ObservationSeverity.WARN: logging.WARNING,
            ObservationSeverity.ALERT: logging.ERROR,
            ObservationSeverity.INSIGHT: logging.INFO,
        }.get(severity, logging.INFO)

        logger.log(level, f"[{source}] {message}")

        # 🔌 WIRING: ALL observations → plugin-local state (Fractal Holon)
        # This makes the system "untötbar" - survives git resets
        # NOTE: We persist ALL severities so OPUS.md can read from StateManager
        # (opus_assistant is BACKEND only - no direct file writes)
        self._persist_to_state(observation)

    def log_info(self, message: str, source: str = "opus_assistant") -> None:
        """Convenience: Log INFO observation."""
        self.log_observation(ObservationSeverity.INFO, message, source)

    def log_warn(self, message: str, source: str = "opus_assistant") -> None:
        """Convenience: Log WARN observation."""
        self.log_observation(ObservationSeverity.WARN, message, source)

    def log_alert(self, message: str, source: str = "opus_assistant") -> None:
        """Convenience: Log ALERT observation."""
        self.log_observation(ObservationSeverity.ALERT, message, source)

    def log_insight(self, message: str, source: str = "opus_assistant") -> None:
        """Convenience: Log INSIGHT observation."""
        self.log_observation(ObservationSeverity.INSIGHT, message, source)

    def _persist_to_state(self, observation: Observation) -> None:
        """
        🔌 WIRING: Persist critical observations to plugin-local state.

        This is the "untötbar" persistence layer (Fractal Holon pattern):
        - Plugin owns its own state in .opus_state/
        - Git-tracked, survives resets
        - Clean isolation from system-wide resources

        Only ALERT and WARN observations are persisted (to keep file small).
        """
        if self._state_manager is None:
            # Lazy-load state manager if not provided
            try:
                from vibe_core.plugins.opus_assistant.core.state_manager import (
                    ObservationEntry,
                    get_state_manager,
                )

                self._state_manager = get_state_manager()
            except ImportError:
                logger.debug("StateManager not available - observation not persisted")
                return

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import ObservationEntry

            entry = ObservationEntry(
                timestamp=observation.timestamp,
                severity=observation.severity.name,
                message=observation.message,
                source=observation.source,
                context_hash=observation.context_hash,
            )
            self._state_manager.append_observation(entry)
            logger.debug(f"📝 Observation persisted to plugin state: {observation.severity.name}")

        except Exception as e:
            # Don't fail if state write fails - it's a secondary persistence
            logger.warning(f"Failed to persist observation to plugin state: {e}")

    def flush_to_opus(self) -> bool:
        """
        DEPRECATED: Direct file writes violate the architecture.

        ⚠️ ARCHITECTURE:
        - opus_assistant is BACKEND only (data provider)
        - Observations are now persisted to StateManager automatically
        - OPUS.md reads from StateManager when InterfacePlugin renders
        - InterfacePlugin writes via kernel.io

        This method now does nothing and returns True for backwards compatibility.
        """
        import warnings

        warnings.warn(
            "ObservationLogger.flush_to_opus() is deprecated. "
            "Observations are now persisted to StateManager automatically.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._pending_flush = False
        return True

    def _update_journal_section(self, content: str) -> str:
        """Update or create journal section in OPUS.md content."""
        journal_markdown = self._journal.to_markdown()
        section_content = f"""{self.SECTION_HEADER}

{self.JOURNAL_START}
{journal_markdown}
{self.JOURNAL_END}
"""

        # Check if journal section exists
        pattern = re.compile(
            rf"{re.escape(self.JOURNAL_START)}.*?{re.escape(self.JOURNAL_END)}",
            re.DOTALL,
        )

        if pattern.search(content):
            # Replace existing section
            new_content = pattern.sub(
                f"{self.JOURNAL_START}\n{journal_markdown}\n{self.JOURNAL_END}",
                content,
            )
        elif self.SECTION_HEADER in content:
            # Header exists but no markers - add markers after header
            new_content = content.replace(
                self.SECTION_HEADER,
                section_content,
            )
        else:
            # No section - append at end (before any closing markers)
            # Try to insert before @AI or @HUMAN sections if they exist at end
            if "<!-- @AI" in content or "<!-- @HUMAN" in content:
                # Find last auto-generated end
                insert_pos = content.rfind("<!-- @AUTO-GENERATED END -->")
                if insert_pos > 0:
                    new_content = (
                        content[: insert_pos + len("<!-- @AUTO-GENERATED END -->")]
                        + "\n\n"
                        + section_content
                        + content[insert_pos + len("<!-- @AUTO-GENERATED END -->") :]
                    )
                else:
                    new_content = content + "\n\n" + section_content
            else:
                new_content = content + "\n\n" + section_content

        return new_content

    def _create_opus_template(self) -> str:
        """Create basic OPUS.md template if none exists."""
        return f"""# OPUS.md

> Operational Protocol for Unified Stewardship

<!-- @AUTO-GENERATED START -->
_Generated by OPUS Assistant_
<!-- @AUTO-GENERATED END -->

{self.SECTION_HEADER}

{self.JOURNAL_START}
_No observations yet._
{self.JOURNAL_END}

<!-- @HUMAN START -->
_Human notes go here. This section is NEVER overwritten._
<!-- @HUMAN END -->

<!-- @AI START -->
_AI observations go here. This section is NEVER overwritten._
<!-- @AI END -->
"""

    def get_journal(self) -> ObservationJournal:
        """Get current journal (for inspection/testing)."""
        return self._journal

    def get_pending_count(self) -> int:
        """Get number of observations pending flush."""
        return len(self._journal.observations) if self._pending_flush else 0

    def clear(self) -> None:
        """Clear journal (for testing)."""
        self._journal = ObservationJournal(max_entries=self._journal.max_entries)
        self._pending_flush = False
