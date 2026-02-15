"""
I/O SENTINEL — Runtime Guard Against Rogue Disk Writers
=========================================================

"na ca mat-sthāni bhūtāni paśya me yogam aiśvaram" — BG 9.5

Problem (from CLAUDE.md):
    30+ Python files write directly to disk (json.dump, write_text, open("w"))
    without going through StateService. These are ROGUE WRITERS — parasitic
    I/O that bypasses the Guna-based IOPolicy enforcement.

Solution:
    Instead of manually fixing 100+ files (entropy feeding), the system
    ITSELF enforces the boundary. This sentinel monkey-patches json.dump
    at runtime to detect and log unauthorized callers.

    It does NOT block writes (that would break things). It OBSERVES and
    REPORTS — like a Naga sentinel watching the perimeter.

    Lives in mahamantra/substrate/ because Mahamantra is the authority.
    The Srivasa Gate (EnforceGateProvider) is the enforcer.
    This sentinel is its eyes.

Usage:
    from vibe_core.mahamantra.substrate.io_sentinel import arm, disarm, report

    arm()      # Start monitoring (call once at boot)
    disarm()   # Stop monitoring (for tests/cleanup)
    report()   # Get violation summary

Architecture:
    - Wraps json.dump and json.dumps with stack inspection
    - Authorized callers (state_service.py, atomic_io.py) pass silently
    - Unauthorized callers get logged with file:line for triage
    - No writes are blocked — observation only (Sattva mode)
    - Thread-safe counters
"""

from __future__ import annotations

__mahajana__ = "prahlada"
__position__ = 7
__genesis__ = "0x90cf95fc"

import json
import inspect
import logging
import threading
from collections import Counter
from pathlib import Path
from typing import Dict, Final, FrozenSet, List, Optional, TypedDict

logger = logging.getLogger("MAHAMANTRA.IO_SENTINEL")


# =============================================================================
# AUTHORIZED CALLERS — These files MAY call json.dump directly
# =============================================================================

_AUTHORIZED_FILES: Final[FrozenSet[str]] = frozenset({
    "state_service.py",
    "atomic_io.py",
    "io_sentinel.py",
    "sync_holon.py",
    "commit_authority.py",
})


# =============================================================================
# TYPES
# =============================================================================

class SentinelViolation(TypedDict):
    caller_file: str
    caller_line: int
    caller_func: str
    call_type: str


class SentinelReport(TypedDict):
    armed: bool
    total_calls: int
    authorized_calls: int
    rogue_calls: int
    rogue_callers: Dict[str, int]
    recent_violations: List[SentinelViolation]


# =============================================================================
# SENTINEL STATE (module-level, thread-safe)
# =============================================================================

_lock = threading.Lock()
_armed: bool = False
_original_dump = json.dump
_total_calls: int = 0
_authorized_calls: int = 0
_rogue_calls: int = 0
_rogue_callers: Counter = Counter()
_recent_violations: List[SentinelViolation] = []
_MAX_RECENT: Final[int] = 100


# =============================================================================
# STACK INSPECTION
# =============================================================================

def _inspect_caller(call_type: str) -> Optional[SentinelViolation]:
    """
    Walk the call stack to find the REAL caller (skip wrappers).

    Returns None if authorized, SentinelViolation if rogue.
    """
    stack = inspect.stack()
    # stack[0] = _inspect_caller
    # stack[1] = _guarded_dump / _guarded_dumps
    # stack[2+] = real caller chain
    for frame_info in stack[2:]:
        filename = Path(frame_info.filename).name
        # Skip internal frames (json module itself, this module)
        if filename in ("__init__.py", "io_sentinel.py", "encoder.py"):
            continue
        if filename in _AUTHORIZED_FILES:
            return None
        return SentinelViolation(
            caller_file=frame_info.filename,
            caller_line=frame_info.lineno,
            caller_func=frame_info.function,
            call_type=call_type,
        )
    return None


# =============================================================================
# GUARDED WRAPPERS
# =============================================================================

def _guarded_dump(*args, **kwargs):
    """Wrapper around json.dump that logs rogue callers."""
    global _total_calls, _authorized_calls, _rogue_calls
    with _lock:
        _total_calls += 1
    violation = _inspect_caller("json.dump")
    if violation is None:
        with _lock:
            _authorized_calls += 1
    else:
        with _lock:
            _rogue_calls += 1
            key = f"{violation['caller_file']}:{violation['caller_line']}"
            _rogue_callers[key] += 1
            if len(_recent_violations) < _MAX_RECENT:
                _recent_violations.append(violation)
        logger.warning(
            "ROGUE WRITER: json.dump called from %s:%d (%s) — not routed through StateService",
            violation["caller_file"], violation["caller_line"], violation["caller_func"],
        )
    return _original_dump(*args, **kwargs)


# =============================================================================
# PUBLIC API
# =============================================================================

def arm() -> None:
    """Arm the sentinel. Monkey-patches json.dump/json.dumps."""
    global _armed
    if _armed:
        return
    json.dump = _guarded_dump
    _armed = True
    logger.info("I/O Sentinel ARMED — monitoring json.dump calls")


def disarm() -> None:
    """Disarm the sentinel. Restores original json.dump/json.dumps."""
    global _armed
    if not _armed:
        return
    json.dump = _original_dump
    _armed = False
    logger.info("I/O Sentinel DISARMED")


def reset() -> None:
    """Reset all counters. For testing."""
    global _total_calls, _authorized_calls, _rogue_calls
    with _lock:
        _total_calls = 0
        _authorized_calls = 0
        _rogue_calls = 0
        _rogue_callers.clear()
        _recent_violations.clear()


def report() -> SentinelReport:
    """Get the sentinel report. Thread-safe snapshot."""
    with _lock:
        return SentinelReport(
            armed=_armed,
            total_calls=_total_calls,
            authorized_calls=_authorized_calls,
            rogue_calls=_rogue_calls,
            rogue_callers=dict(_rogue_callers),
            recent_violations=list(_recent_violations),
        )


def is_armed() -> bool:
    """Return True if the sentinel is currently armed."""
    with _lock:
        return _armed


def drain_violations() -> List[SentinelViolation]:
    """Drain all accumulated violations. Thread-safe.

    Returns the violations and clears the buffer.
    This is the bridge to Ouroboros ingestion:
    Sentinel sees → drain_violations() → OuroborosSubscriber → KG.
    """
    with _lock:
        drained = list(_recent_violations)
        _recent_violations.clear()
    return drained
