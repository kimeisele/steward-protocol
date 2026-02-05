"""
LOG ENTRY - The Tattva of Perception
=====================================

Defines the structure of a log event and its transition from 
Dead Text to Alive Data.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import json

@dataclass(frozen=True)
class LogEntry:
    """The unified data atom for all logs."""
    timestamp: datetime
    level: str
    source: str
    message: str
    offset: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Integrity check: A log without a timestamp is void
        if not isinstance(self.timestamp, datetime):
            raise ValueError("LogEntry must have a valid datetime timestamp")

class LogParser:
    """Base class for format-specific parsing logic."""
    def parse(self, line: str, offset: int) -> Optional[LogEntry]:
        raise NotImplementedError

class JsonlParser(LogParser):
    def parse(self, line: str, offset: int) -> Optional[LogEntry]:
        if not line.startswith("{"): return None
        try:
            data = json.loads(line)
            ts = datetime.fromisoformat((data.get("timestamp") or data.get("ts")).replace("Z", "+00:00"))
            return LogEntry(
                timestamp=ts,
                level=data.get("level") or data.get("status") or "INFO",
                source=data.get("source") or data.get("auditor") or "UNKNOWN",
                message=data.get("message") or "structured_log",
                offset=offset,
                metadata=data
            )
        except: return None

class TextParser(LogParser):
    import re
    TS_PATTERN = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})")

    def parse(self, line: str, offset: int) -> Optional[LogEntry]:
        match = self.TS_PATTERN.match(line)
        if not match: return None
        try:
            ts = datetime.strptime(match.group("ts"), "%Y-%m-%d %H:%M:%S,%f")
            parts = line[match.end():].strip().split(" ", 2)
            # Format: [LEVEL] SOURCE: MESSAGE
            level = parts[0].strip("[]") if len(parts) > 0 else "INFO"
            source = parts[1].strip(":") if len(parts) > 1 else "SYSTEM"
            message = parts[2] if len(parts) > 2 else ""
            
            return LogEntry(
                timestamp=ts,
                level=level,
                source=source,
                message=message,
                offset=offset,
                raw=line
            )
        except: return None

class UnifiedParser:
    """Orchestrates multiple parsers without if-else bloat."""
    def __init__(self):
        self.parsers = [JsonlParser(), TextParser()]

    def parse(self, line: str, offset: int) -> Optional[LogEntry]:
        for parser in self.parsers:
            entry = parser.parse(line, offset)
            if entry: return entry
        return None
