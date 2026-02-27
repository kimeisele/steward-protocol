"""
EVENT BRIDGE - Der Priester (The Priest)
========================================

"arcayam eva haraye pujam yah sraddhayehate"
"One who worships the Deity in the temple with faith..."
— Srimad Bhagavatam 11.3.48

The Temple (commands.py) receives only clean offerings.
The Priest (this module) goes to the basement and fetches them.

ARCHITECTURE:
    cli_listen (Temple) → EventBridge (Priest) → Files/StateService (Basement)

This is the ONLY place where file paths and I/O belong.
commands.py stays pure - presentation only.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x8aeeac66"  # GenesisByte: parampara % 37 == 0

import json
from pathlib import Path
from typing import Dict, Final, List, Optional, TypedDict

# =============================================================================
# EVENT ENTRY (The Clean Offering)
# =============================================================================


class EventEntry(TypedDict, total=False):
    """Single event entry - the clean offering to the Temple."""

    timestamp: str
    source: str
    severity: str
    message: str
    file_path: str
    rule_id: str
    syscall_type: str
    result: str


# =============================================================================
# EVENT SOURCES (The Basement Map)
# =============================================================================
# TODO: Migrate to StateService for Naga 2060 unified event hub


class EventSourceConfig(TypedDict):
    """Configuration for an event source."""

    path: str
    parser: str  # "violations" or "syscalls"


# The dirty work - path configuration lives HERE, not in commands.py
EVENT_SOURCES: Final[Dict[str, EventSourceConfig]] = {
    "violations": {
        "path": "data/ledger/violations.jsonl",
        "parser": "violations",
    },
    "syscalls": {
        "path": ".vibe/state/plugins/opus_assistant/syscalls.jsonl",
        "parser": "syscalls",
    },
}


# =============================================================================
# PARSERS (Transform Raw to Clean)
# =============================================================================


def _parse_violation(data: Dict) -> EventEntry:
    """Parse a violation JSONL line into EventEntry."""
    return EventEntry(
        source="violations",
        timestamp=data.get("timestamp", ""),
        severity=data.get("severity", ""),
        message=data.get("message", ""),
        file_path=data.get("file_path", ""),
        rule_id=data.get("violated_invariant") or data.get("rule_id", ""),
    )


def _parse_syscall(data: Dict) -> EventEntry:
    """Parse a syscall JSONL line into EventEntry."""
    return EventEntry(
        source="syscalls",
        timestamp=data.get("timestamp", ""),
        syscall_type=data.get("syscall_type", ""),
        result=data.get("result", ""),
        message=data.get("intent", ""),
    )


PARSERS = {
    "violations": _parse_violation,
    "syscalls": _parse_syscall,
}


# =============================================================================
# THE BRIDGE (The Priest's Work)
# =============================================================================


def get_available_sources() -> List[str]:
    """Get list of available event sources."""
    return list(EVENT_SOURCES.keys())


def get_events(
    source: str = "all",
    limit: int = 10,
    severity_filter: Optional[str] = None,
) -> tuple[List[EventEntry], int]:
    """
    Fetch events from configured sources.

    The Priest goes to the basement and returns clean offerings.

    Args:
        source: "violations", "syscalls", or "all"
        limit: Maximum entries to return
        severity_filter: Filter by severity (for violations)

    Returns:
        Tuple of (filtered_entries, total_count)
    """
    entries: List[EventEntry] = []

    # Determine which sources to read
    if source == "all" or source == "":
        sources_to_read = list(EVENT_SOURCES.keys())
    elif source in EVENT_SOURCES:
        sources_to_read = [source]
    else:
        sources_to_read = list(EVENT_SOURCES.keys())

    # Read from each source
    for src_name in sources_to_read:
        config = EVENT_SOURCES[src_name]
        src_path = Path(config["path"])
        parser = PARSERS.get(config["parser"])

        if not src_path.exists() or not parser:
            continue

        try:
            with open(src_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entry = parser(data)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue

    total_count = len(entries)

    # Filter by severity if specified
    if severity_filter:
        severity_upper = severity_filter.upper()
        entries = [e for e in entries if e.get("severity", "").upper() == severity_upper]

    # Sort by timestamp (newest first) and limit
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    entries = entries[:limit]

    return entries, total_count


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "EventEntry",
    "EventSourceConfig",
    "EVENT_SOURCES",
    "get_available_sources",
    "get_events",
]
