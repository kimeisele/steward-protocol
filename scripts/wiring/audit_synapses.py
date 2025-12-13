#!/usr/bin/env python3
"""
🧠 SYNAPSE AUDIT - Dead Wire Detector

Finds all events that are EMITTED but never LISTENED to.
These are "dead wires" - signals that scream into the void.

Usage:
    python scripts/wiring/audit_synapses.py

Architecture:
    1. Scan all .py files for emit_event/emit/broadcast calls
    2. Scan all .py files for subscribe/listen/on_* handlers
    3. Cross-reference to find orphans
    4. Generate Wiring Report

This is the diagnostic tool for the "Brain Awakening" phase.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


def find_emitted_events(workspace: Path) -> Dict[str, List[Tuple[str, int, str]]]:
    """
    Find all events that are emitted.

    Returns:
        Dict mapping event_name -> [(file, line, context), ...]
    """
    events: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)

    # Patterns for event emission
    patterns = [
        # emit_event("EVENT_NAME", ...) or emit("EVENT_NAME", ...)
        r'emit_event\s*\(\s*["\']([A-Z_]+)["\']',
        r'emit\s*\(\s*["\']([a-zA-Z_.]+)["\']',
        r'await\s+bus\.emit\s*\(\s*["\']([a-zA-Z_.]+)["\']',
        # EventType.NAME
        r"EventType\.([A-Z_]+)",
        # event_type="EVENT_NAME"
        r'event_type\s*=\s*["\']([A-Z_]+)["\']',
        # EMIT_EVENT action in circuits
        r'action_type:\s*EMIT_EVENT[\s\S]*?target:\s*["\']?([a-zA-Z_.]+)["\']?',
    ]

    for py_file in workspace.rglob("*.py"):
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                for pattern in patterns:
                    for match in re.finditer(pattern, line):
                        event_name = match.group(1)
                        rel_path = str(py_file.relative_to(workspace))
                        events[event_name].append((rel_path, i, line.strip()[:80]))
        except Exception:
            pass

    # Also scan YAML circuit files
    for yaml_file in workspace.rglob("*.yaml"):
        if "__pycache__" in str(yaml_file):
            continue

        try:
            content = yaml_file.read_text()

            # Find EMIT_EVENT targets
            for match in re.finditer(r'action_type:\s*EMIT_EVENT[\s\S]*?target:\s*["\']?([a-zA-Z_.]+)', content):
                event_name = match.group(1)
                rel_path = str(yaml_file.relative_to(workspace))
                events[event_name].append((rel_path, 0, "EMIT_EVENT in circuit"))
        except Exception:
            pass

    return dict(events)


def find_listened_events(workspace: Path) -> Dict[str, List[Tuple[str, int, str]]]:
    """
    Find all events that are listened to.

    Returns:
        Dict mapping event_name -> [(file, line, context), ...]
    """
    listeners: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)

    # Patterns for event listening
    patterns = [
        # subscribe("EVENT_NAME", handler)
        r'subscribe\s*\(\s*["\']([A-Z_]+)["\']',
        # on_event("EVENT_NAME") decorator
        r'on_event\s*\(\s*["\']([A-Z_]+)["\']',
        # listen("EVENT_NAME")
        r'listen\s*\(\s*["\']([a-zA-Z_.]+)["\']',
        # triggers: - event: EVENT_NAME (in circuits)
        r"event:\s*([A-Z_]+)",
        # if event_type == "EVENT_NAME"
        r'event_type\s*==\s*["\']([A-Z_]+)["\']',
        # case "EVENT_NAME":
        r'case\s+["\']([A-Z_]+)["\']',
    ]

    for py_file in workspace.rglob("*.py"):
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                for pattern in patterns:
                    for match in re.finditer(pattern, line):
                        event_name = match.group(1)
                        rel_path = str(py_file.relative_to(workspace))
                        listeners[event_name].append((rel_path, i, line.strip()[:80]))
        except Exception:
            pass

    # Also scan YAML circuit files for triggers
    for yaml_file in workspace.rglob("*.yaml"):
        if "__pycache__" in str(yaml_file):
            continue

        try:
            content = yaml_file.read_text()

            # Find trigger events
            for match in re.finditer(r"-\s*event:\s*([A-Z_]+)", content):
                event_name = match.group(1)
                rel_path = str(yaml_file.relative_to(workspace))
                listeners[event_name].append((rel_path, 0, "trigger in circuit"))
        except Exception:
            pass

    return dict(listeners)


def find_orphan_events(emitted: Dict[str, List], listened: Dict[str, List]) -> Set[str]:
    """Find events that are emitted but never listened to."""
    emitted_set = set(emitted.keys())
    listened_set = set(listened.keys())

    orphans = emitted_set - listened_set
    return orphans


def find_unhandled_listeners(emitted: Dict[str, List], listened: Dict[str, List]) -> Set[str]:
    """Find listeners that wait for events that are never emitted."""
    emitted_set = set(emitted.keys())
    listened_set = set(listened.keys())

    unhandled = listened_set - emitted_set
    return unhandled


def generate_report(workspace: Path) -> str:
    """Generate full wiring audit report."""
    emitted = find_emitted_events(workspace)
    listened = find_listened_events(workspace)

    orphans = find_orphan_events(emitted, listened)
    unhandled = find_unhandled_listeners(emitted, listened)

    # Connected events (both emitted and listened)
    connected = set(emitted.keys()) & set(listened.keys())

    lines = [
        "=" * 70,
        "🧠 SYNAPSE AUDIT - Brain Wiring Report",
        "=" * 70,
        "",
        "📊 Summary:",
        f"   Events emitted:    {len(emitted)}",
        f"   Events listened:   {len(listened)}",
        f"   Connected (wired): {len(connected)}",
        f"   ORPHANS (dead):    {len(orphans)}",
        f"   Unhandled:         {len(unhandled)}",
        "",
    ]

    # Orphan events (emitted but no listener)
    if orphans:
        lines.extend(
            [
                "─" * 70,
                "🔴 ORPHAN EVENTS (emitted but NO listener)",
                "   These signals scream into the void!",
                "─" * 70,
            ]
        )
        for event in sorted(orphans):
            sources = emitted.get(event, [])
            lines.append(f"\n   {event}")
            for src, line_num, ctx in sources[:3]:
                lines.append(f"      └── {src}:{line_num}")

    # Unhandled listeners (waiting for events that never fire)
    if unhandled:
        lines.extend(
            [
                "",
                "─" * 70,
                "🟡 UNHANDLED LISTENERS (waiting for events never emitted)",
                "   These handlers wait forever!",
                "─" * 70,
            ]
        )
        for event in sorted(unhandled):
            handlers = listened.get(event, [])
            lines.append(f"\n   {event}")
            for src, line_num, ctx in handlers[:3]:
                lines.append(f"      └── {src}:{line_num}")

    # Connected events (healthy synapses)
    if connected:
        lines.extend(
            [
                "",
                "─" * 70,
                "🟢 CONNECTED EVENTS (healthy synapses)",
                "─" * 70,
            ]
        )
        for event in sorted(connected):
            emit_count = len(emitted.get(event, []))
            listen_count = len(listened.get(event, []))
            lines.append(f"   ✓ {event} ({emit_count} emitters → {listen_count} listeners)")

    # Wiring suggestions
    lines.extend(
        [
            "",
            "=" * 70,
            "💡 WIRING SUGGESTIONS",
            "=" * 70,
        ]
    )

    if orphans:
        lines.append("\nOrphan events that SHOULD have listeners:")
        suggestions = {
            "DRIFT_DETECTED": "→ vedic_governance should demote responsible agent",
            "TEST_FAILED": "→ karma circuit should record failure",
            "DOCUMENT_UPDATED": "→ opus_assistant should invalidate cache",
            "SECURITY_ALERT": "→ vedic_governance should pause agent",
            "VERIFICATION": "→ karma circuit should track trust score",
        }
        for event in sorted(orphans):
            suggestion = suggestions.get(event, "→ Consider adding a handler")
            lines.append(f"   • {event} {suggestion}")

    lines.extend(
        [
            "",
            "=" * 70,
            "Run this after connecting wires to verify brain health.",
            "=" * 70,
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    workspace = Path.cwd()
    if len(sys.argv) > 1:
        workspace = Path(sys.argv[1])

    report = generate_report(workspace)
    print(report)
