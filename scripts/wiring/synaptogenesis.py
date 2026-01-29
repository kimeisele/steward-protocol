#!/usr/bin/env python3
"""
🧬 SYNAPTOGENESIS - Auto-Wiring Suggestion Engine

Instead of manually wiring 42 orphan events, this tool:
1. Groups orphan events by semantic meaning
2. Suggests which plugin/handler SHOULD listen
3. Generates circuit YAML stubs for each wiring

This is NEURO-EVOLUTION - the system suggests its own wiring.

Usage:
    python scripts/wiring/synaptogenesis.py
    python scripts/wiring/synaptogenesis.py --generate-circuits
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x34cf5718"  # GenesisByte: parampara % 37 == 0

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

# Semantic groupings and suggested listeners
SEMANTIC_GROUPS = {
    "lifecycle": {
        "events": [
            "AGENT_REGISTERED",
            "AGENT_DESTROYED",
            "AGENT_SPAWNED",
            "KERNEL_BOOT",
            "KERNEL_SHUTDOWN",
        ],
        "suggested_listener": "vedic_governance",
        "reason": "Agent lifecycle events should update governance registry",
        "circuit_action": "Update varna/ashrama registry, clean up on destruction",
    },
    "errors": {
        "events": ["ERROR", "FAILURE", "EXCEPTION", "CRASH", "FATAL"],
        "suggested_listener": "karma_consequence",
        "reason": "Errors should affect karma and potentially trigger demotion",
        "circuit_action": "Record error, update trust score, check demotion threshold",
    },
    "task_completion": {
        "events": ["TASK_COMPLETED", "COMPLETED", "SUCCESS"],
        "suggested_listener": "vedic_governance",
        "reason": "Task completions should count toward graduation",
        "circuit_action": "Increment task counter, check for ashrama promotion",
    },
    "constitutional": {
        "events": [
            "VIOLATION",
            "INVARIANT_VIOLATION",
            "CONSTITUTIONAL_OATH",
            "OATH_SWORN",
        ],
        "suggested_listener": "steward_protocol",
        "reason": "Constitutional events need verification and enforcement",
        "circuit_action": "Verify oath, enforce violations, update compliance status",
    },
    "communication": {
        "events": [
            "BROADCAST",
            "PRAYER_RECEIVED",
            "MERCY",
            "THOUGHT",
            "ACTION",
        ],
        "suggested_listener": "opus_assistant",
        "reason": "Communication events should be logged to journal",
        "circuit_action": "Log to observation journal, update state of mind",
    },
    "economy": {
        "events": ["CREDIT_TRANSFER", "CREDIT_USED", "KARMA_RECORDED"],
        "suggested_listener": "ledger",
        "reason": "Economic events need persistent recording",
        "circuit_action": "Record transaction, update balances, emit confirmation",
    },
    "security": {
        "events": [
            "CRITICAL_INTERRUPT",
            "SECURITY_ALERT",
            "NARASIMHA_DESTRUCTION",
        ],
        "suggested_listener": "vedic_governance",
        "reason": "Security events should pause/restrict affected agents",
        "circuit_action": "Pause agent, restrict permissions, alert administrator",
    },
    "testing": {
        "events": [
            "TEST_RESULT",
            "TEST_FAILED",
            "TEST_SUITE_RUN",
            "TEST_CONTRACT_CREATED",
            "TEST_CONTRACT_UPDATED",
            "TEST_MUTATION_DETECTED",
            "TEST_UPDATE_PERMITTED",
        ],
        "suggested_listener": "test_orchestration",
        "reason": "Test events should update test state and trigger reruns",
        "circuit_action": "Update test status, trigger healing if failed",
    },
    "audit": {
        "events": ["AUDIT_CHECK", "audit.complete", "audit.warning"],
        "suggested_listener": "opus_assistant",
        "reason": "Audit events should be logged and trigger verification",
        "circuit_action": "Log audit result, update trust score if degraded",
    },
    "genesis": {
        "events": ["GENESIS", "EPHEMERAL_CITY_MERGE"],
        "suggested_listener": "sarga_cycle",
        "reason": "Genesis events should initialize system state",
        "circuit_action": "Record boot event, initialize karma tracking",
    },
    "opus_internal": {
        "events": [
            "opus.circuit_started",
            "opus.context_updated",
            "opus.heal_started",
            "opus.refreshed",
            "circuit_started",
            "circuit_completed",
            "karma.demotion_triggered",
        ],
        "suggested_listener": "opus_assistant",
        "reason": "OPUS internal events for self-monitoring",
        "circuit_action": "Log to journal, update circuit status dashboard",
    },
}


def load_orphan_events(workspace: Path) -> Set[str]:
    """Load orphan events from audit_synapses.py output."""
    # Import and run the audit
    import sys

    sys.path.insert(0, str(workspace / "scripts/wiring"))

    try:
        from audit_synapses import find_emitted_events, find_listened_events, find_orphan_events

        emitted = find_emitted_events(workspace)
        listened = find_listened_events(workspace)
        return find_orphan_events(emitted, listened)
    except ImportError:
        # Fallback: hardcoded from last audit
        return {
            "ACTION",
            "AGENT_DESTROYED",
            "AGENT_REGISTERED",
            "AUDIT_CHECK",
            "BROADCAST",
            "COMPLETED",
            "CONSTITUTIONAL_OATH",
            "CREDIT_TRANSFER",
            "CREDIT_USED",
            "CRITICAL_INTERRUPT",
            "EPHEMERAL_CITY_MERGE",
            "ERROR",
            "INVARIANT_VIOLATION",
            "KARMA_RECORDED",
            "KERNEL_SHUTDOWN",
            "MERCY",
            "NARASIMHA_DESTRUCTION",
            "OATH_SWORN",
            "PRAYER_RECEIVED",
            "TASK_COMPLETED",
            "THOUGHT",
            "audit.complete",
            "audit.warning",
            "circuit_completed",
            "circuit_started",
            "karma.demotion_triggered",
            "opus.circuit_started",
            "opus.context_updated",
            "opus.heal_started",
            "opus.refreshed",
        }


def group_orphans(orphans: Set[str]) -> Dict[str, List[str]]:
    """Group orphan events by semantic category."""
    grouped: Dict[str, List[str]] = defaultdict(list)
    ungrouped = []

    for event in orphans:
        found = False
        for group_name, group_info in SEMANTIC_GROUPS.items():
            if event in group_info["events"]:
                grouped[group_name].append(event)
                found = True
                break

        if not found:
            # Try pattern matching
            event_lower = event.lower()
            if "error" in event_lower or "fail" in event_lower:
                grouped["errors"].append(event)
            elif "test" in event_lower:
                grouped["testing"].append(event)
            elif "agent" in event_lower:
                grouped["lifecycle"].append(event)
            elif "opus" in event_lower or "circuit" in event_lower:
                grouped["opus_internal"].append(event)
            elif "audit" in event_lower:
                grouped["audit"].append(event)
            else:
                ungrouped.append(event)

    if ungrouped:
        grouped["uncategorized"] = ungrouped

    return dict(grouped)


def generate_circuit_stub(group_name: str, events: List[str], group_info: Dict) -> str:
    """Generate a circuit YAML stub for a group of events."""
    listener = group_info.get("suggested_listener", "opus_assistant")
    action = group_info.get("circuit_action", "Log and process")

    events_yaml = "\n".join(f"    - event: {e}" for e in events)

    return f"""# AUTO-GENERATED: {group_name.upper()}_WIRING
# Suggested listener: {listener}
# Reason: {group_info.get("reason", "N/A")}
#
circuit:
  id: {group_name.upper()}_WIRING
  name: "{group_name.replace("_", " ").title()} Event Wiring"
  description: "Auto-wire {len(events)} orphan events to {listener}"
  domain: SYNAPTOGENESIS
  version: "1.0.0"
  entry_state: "handle_event"

  triggers:
{events_yaml}

  states:
    handle_event:
      name: "Handle {group_name.title()} Event"
      description: "{action}"
      state_var: "result"
      actions:
        - action_type: EXECUTE_SCRIPT
          target: "opus.log_observation"
          params:
            severity: "INFO"
            message: "Received {{{{ trigger_event.event_type }}}}"
            source: "{group_name}_wiring"
        # TODO: Add specific handling for {listener}
      on_success: COMPLETE
      on_failure: COMPLETE

    COMPLETE:
      name: "Wiring Complete"
      terminal: true
      result:
        status: "success"
        group: "{group_name}"
"""


def generate_report(workspace: Path, generate_circuits: bool = False) -> str:
    """Generate synaptogenesis report."""
    orphans = load_orphan_events(workspace)
    grouped = group_orphans(orphans)

    lines = [
        "=" * 70,
        "🧬 SYNAPTOGENESIS - Auto-Wiring Suggestion Engine",
        "=" * 70,
        "",
        f"📊 Total Orphan Events: {len(orphans)}",
        f"📁 Semantic Groups: {len(grouped)}",
        "",
    ]

    # Show groups with suggestions
    for group_name, events in sorted(grouped.items()):
        group_info = SEMANTIC_GROUPS.get(group_name, {})
        listener = group_info.get("suggested_listener", "unknown")
        reason = group_info.get("reason", "No specific reason")

        lines.extend(
            [
                "─" * 70,
                f"📦 {group_name.upper()} ({len(events)} events)",
                f"   🎯 Suggested Listener: {listener}",
                f"   📝 Reason: {reason}",
                "",
            ]
        )

        for event in sorted(events):
            lines.append(f"      • {event}")

        lines.append("")

    # Wiring priority
    lines.extend(
        [
            "=" * 70,
            "⚡ WIRING PRIORITY (suggested order)",
            "=" * 70,
            "",
        ]
    )

    priority_order = [
        ("errors", "🔴 CRITICAL - Errors must have consequences"),
        ("lifecycle", "🟠 HIGH - Agent lifecycle must be tracked"),
        ("task_completion", "🟡 MEDIUM - Graduation tracking"),
        ("security", "🔴 CRITICAL - Security events need response"),
        ("constitutional", "🟠 HIGH - Constitutional enforcement"),
        ("testing", "🟡 MEDIUM - Test result tracking"),
        ("audit", "🟢 LOW - Audit logging"),
        ("communication", "🟢 LOW - Communication logging"),
        ("economy", "🟡 MEDIUM - Economic tracking"),
        ("opus_internal", "🟢 LOW - Self-monitoring"),
    ]

    for group_name, priority_desc in priority_order:
        if group_name in grouped:
            count = len(grouped[group_name])
            lines.append(f"   {priority_desc}")
            lines.append(
                f"      → Wire {count} events to {SEMANTIC_GROUPS.get(group_name, {}).get('suggested_listener', '?')}"
            )
            lines.append("")

    # Generate circuit stubs if requested
    if generate_circuits:
        lines.extend(
            [
                "",
                "=" * 70,
                "📄 GENERATED CIRCUIT STUBS",
                "=" * 70,
            ]
        )

        circuits_dir = workspace / "vibe_core/plugins/opus_assistant/circuits/generated"
        circuits_dir.mkdir(exist_ok=True)

        for group_name, events in grouped.items():
            if group_name == "uncategorized":
                continue

            group_info = SEMANTIC_GROUPS.get(group_name, {})
            circuit_yaml = generate_circuit_stub(group_name, events, group_info)

            circuit_file = circuits_dir / f"{group_name}_wiring.yaml"
            circuit_file.write_text(circuit_yaml)
            lines.append(f"\n   ✅ Generated: {circuit_file.relative_to(workspace)}")

    lines.extend(
        [
            "",
            "=" * 70,
            "🧠 Run with --generate-circuits to create circuit stubs",
            "=" * 70,
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synaptogenesis - Auto-Wiring Suggestion Engine")
    parser.add_argument("--generate-circuits", action="store_true", help="Generate circuit YAML stubs")
    parser.add_argument("workspace", nargs="?", default=".", help="Workspace path")

    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()

    report = generate_report(workspace, generate_circuits=args.generate_circuits)
    print(report)
