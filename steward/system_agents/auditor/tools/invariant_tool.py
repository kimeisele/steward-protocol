#!/usr/bin/env python3
"""
THE JUDGE - Invariant Verification Engine

This tool implements the semantic verification layer for STEWARD Protocol.
Unlike unit tests (which check syntax), this verifies MEANING.

Core Concept:
- Invariants are laws that MUST NEVER be broken
- This tool audits the event stream to detect violations
- If any invariant breaks -> VIOLATION event -> System alarm

Example Invariants:
  1. "BROADCAST requires LICENSE_VALID in same task context"
  2. "CREDIT_TRANSFER requires PROPOSAL_PASSED before"
  3. "No orphaned events without proper context"
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("JUDGE_INVARIANT")


class InvariantSeverity(str, Enum):
    """Severity levels for invariant violations"""

    CRITICAL = "CRITICAL"  # System must halt
    HIGH = "HIGH"  # Operations must pause
    MEDIUM = "MEDIUM"  # Warning, but continue
    LOW = "LOW"  # Advisory only


@dataclass
class InvariantRule:
    """Definition of a single invariant rule"""

    name: str
    description: str
    severity: InvariantSeverity
    check_function: callable

    def check(self, events: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
        """
        Execute the invariant check.

        Returns:
            (passed: bool, violation_message: Optional[str])
        """
        try:
            result = self.check_function(events, context or {})
            if isinstance(result, tuple):
                return result
            return (result, None)
        except Exception as e:
            return (False, f"Check execution error: {str(e)}")


@dataclass
class InvariantViolation:
    """Record of a single invariant violation"""

    invariant_name: str
    severity: str
    timestamp: str
    message: str
    violated_events: List[int]  # Indices of events that violated
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VerificationReport:
    """Report from invariant verification"""

    def __init__(self):
        self.passed = True
        self.violations: List[InvariantViolation] = []
        self.checked_events = 0
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def add_violation(self, violation: InvariantViolation):
        """Record a violation"""
        self.violations.append(violation)
        # Any CRITICAL or HIGH violation fails the check
        if violation.severity in [
            InvariantSeverity.CRITICAL.value,
            InvariantSeverity.HIGH.value,
        ]:
            self.passed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "timestamp": self.timestamp,
            "violations_count": len(self.violations),
            "checked_events": self.checked_events,
            "violations": [v.to_dict() for v in self.violations],
        }


class InvariantEngine:
    """
    The JUDGE - Semantic Verification Engine

    Runs checks on the event ledger to ensure system integrity.
    """

    def __init__(self):
        """Initialize the invariant engine with all rules"""
        logger.info("⚖️  JUDGE: Initializing Invariant Engine")

        self.rules: Dict[str, InvariantRule] = {}
        self._register_core_invariants()

    def _register_core_invariants(self):
        """Register the core set of invariant rules"""

        # INVARIANT 1: Broadcast License Requirement
        def check_broadcast_license(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Every BROADCAST event must have a preceding LICENSE_VALID
            in the same task context.
            """
            for i, event in enumerate(events):
                if event.get("event_type") == "BROADCAST":
                    task_id = event.get("task_id")

                    # Look back for LICENSE_VALID in same task
                    license_found = False
                    for j in range(i - 1, -1, -1):
                        prev_event = events[j]
                        if prev_event.get("task_id") != task_id:
                            break
                        if prev_event.get("event_type") == "LICENSE_VALID":
                            license_found = True
                            break

                    if not license_found:
                        return (
                            False,
                            f"BROADCAST event at index {i} missing LICENSE_VALID in task {task_id}",
                        )

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="BROADCAST_LICENSE_REQUIREMENT",
                description="Every BROADCAST must be preceded by LICENSE_VALID in same task",
                severity=InvariantSeverity.CRITICAL,
                check_function=check_broadcast_license,
            )
        )

        # INVARIANT 2: Credit Transfer Proposal Requirement
        def check_credit_transfer_proposal(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Every CREDIT_TRANSFER must have a preceding PROPOSAL_PASSED
            in the same task context.
            """
            for i, event in enumerate(events):
                if event.get("event_type") == "CREDIT_TRANSFER":
                    task_id = event.get("task_id")

                    # Look back for PROPOSAL_PASSED in same task
                    proposal_found = False
                    for j in range(i - 1, -1, -1):
                        prev_event = events[j]
                        if prev_event.get("task_id") != task_id:
                            break
                        if prev_event.get("event_type") == "PROPOSAL_PASSED":
                            proposal_found = True
                            break

                    if not proposal_found:
                        return (
                            False,
                            f"CREDIT_TRANSFER at index {i} missing PROPOSAL_PASSED in task {task_id}",
                        )

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="CREDIT_TRANSFER_PROPOSAL_REQUIREMENT",
                description="Every CREDIT_TRANSFER must be preceded by PROPOSAL_PASSED",
                severity=InvariantSeverity.CRITICAL,
                check_function=check_credit_transfer_proposal,
            )
        )

        # INVARIANT 3: No Orphaned Events
        def check_no_orphaned_events(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Every event must have task_id and agent_id.
            No orphaned/incomplete events allowed.
            """
            for i, event in enumerate(events):
                if not event.get("task_id"):
                    return (False, f"Event at index {i} missing task_id")
                if not event.get("agent_id"):
                    return (False, f"Event at index {i} missing agent_id")
                if not event.get("event_type"):
                    return (False, f"Event at index {i} missing event_type")
                if not event.get("timestamp"):
                    return (False, f"Event at index {i} missing timestamp")

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="NO_ORPHANED_EVENTS",
                description="Every event must have task_id, agent_id, event_type, and timestamp",
                severity=InvariantSeverity.HIGH,
                check_function=check_no_orphaned_events,
            )
        )

        # INVARIANT 4: Event Sequence Integrity
        def check_event_sequence(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Events within a task must be in chronological order.
            """
            task_events: Dict[str, List[Tuple[int, datetime]]] = {}

            for i, event in enumerate(events):
                task_id = event.get("task_id")
                timestamp_str = event.get("timestamp")

                if not task_id or not timestamp_str:
                    continue

                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except:
                    return (False, f"Event at index {i} has invalid timestamp format")

                if task_id not in task_events:
                    task_events[task_id] = []

                task_events[task_id].append((i, timestamp))

            # Check order within each task
            for task_id, events_in_task in task_events.items():
                for k in range(1, len(events_in_task)):
                    prev_idx, prev_ts = events_in_task[k - 1]
                    curr_idx, curr_ts = events_in_task[k]

                    if curr_ts < prev_ts:
                        return (
                            False,
                            f"Events out of order in task {task_id}: "
                            f"event {prev_idx} ({prev_ts}) before event {curr_idx} ({curr_ts})",
                        )

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="EVENT_SEQUENCE_INTEGRITY",
                description="Events within a task must be in chronological order",
                severity=InvariantSeverity.HIGH,
                check_function=check_event_sequence,
            )
        )

        # INVARIANT 5: No Duplicate Events
        def check_no_duplicates(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: No two events should have the same task_id + event_type + timestamp
            (which would indicate a replay or duplicate).
            """
            seen: Dict[Tuple, int] = {}

            for i, event in enumerate(events):
                key = (
                    event.get("task_id"),
                    event.get("event_type"),
                    event.get("timestamp"),
                )

                if key in seen:
                    return (
                        False,
                        f"Duplicate event detected: event {i} matches event {seen[key]} (task={key[0]}, type={key[1]})",
                    )

                seen[key] = i

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="NO_DUPLICATE_EVENTS",
                description="No duplicate events allowed (checked by task_id + event_type + timestamp)",
                severity=InvariantSeverity.CRITICAL,
                check_function=check_no_duplicates,
            )
        )

        # INVARIANT 6: PROPOSAL_VOTED_YES only after PROPOSAL_CREATED
        def check_proposal_workflow(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: PROPOSAL_VOTED_YES events must have a preceding PROPOSAL_CREATED
            for the same proposal_id.
            """
            for i, event in enumerate(events):
                if event.get("event_type") == "PROPOSAL_VOTED_YES":
                    proposal_id = event.get("proposal_id")

                    # Look for PROPOSAL_CREATED with same ID
                    created_found = False
                    for j in range(i - 1, -1, -1):
                        prev_event = events[j]
                        if prev_event.get("event_type") == "PROPOSAL_CREATED":
                            if prev_event.get("proposal_id") == proposal_id:
                                created_found = True
                                break

                    if not created_found:
                        return (
                            False,
                            f"PROPOSAL_VOTED_YES at index {i} has no preceding "
                            f"PROPOSAL_CREATED for proposal_id={proposal_id}",
                        )

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="PROPOSAL_WORKFLOW_INTEGRITY",
                description="PROPOSAL_VOTED_YES must follow PROPOSAL_CREATED for same proposal",
                severity=InvariantSeverity.HIGH,
                check_function=check_proposal_workflow,
            )
        )

        # INVARIANT 7: No Critical Voids (Null/Empty Detection)
        def check_no_critical_voids(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Critical system state fields must never be null/empty.
            Detects "silent failures" where operations complete but state is corrupted.

            Checks:
            - total_credits must not be None/0 (after first action)
            - agents_registered must not be 0 (after boot)
            - ledger_events must not be 0 (after first action)
            - All agents must have valid name and domain (NOT test/dummy agents)
            """
            # Extract system state from context
            total_credits = ctx.get("total_credits")
            agents_registered = ctx.get("agents_registered")
            ledger_events = ctx.get("ledger_events", len(events))
            agents = ctx.get("agents", [])

            # Check agent integrity
            for agent in agents:
                agent_id = agent.get("agent_id", "")
                name = agent.get("name", "")
                domain = agent.get("domain", "")

                # Reject dummy/test agents in production
                if agent_id.startswith("dummy-") or name.startswith("Dummy"):
                    return (
                        False,
                        f"VOID: Dummy/test agent found in production: {agent_id}",
                    )

                # All agents must have name and domain
                if not name or not domain:
                    return (False, f"VOID: Agent {agent_id} missing name or domain")

            # After boot (events exist), these must have values
            if len(events) > 0:
                # Check total_credits
                if total_credits is None or total_credits == 0:
                    return (
                        False,
                        "VOID: total_credits is None or 0 after system action",
                    )

                # Check agents_registered
                if agents_registered is not None and agents_registered == 0:
                    return (
                        False,
                        "VOID: agents_registered is 0 (system appears offline)",
                    )

                # Ledger events should match event count
                if ledger_events == 0 and len(events) > 0:
                    return (
                        False,
                        "VOID: ledger_events is 0 but events exist (state mismatch)",
                    )

            return (True, None)

        self.register_rule(
            InvariantRule(
                name="NO_CRITICAL_VOIDS",
                description="Critical system fields (credits, agents, ledger) must never be null/empty",
                severity=InvariantSeverity.CRITICAL,
                check_function=check_no_critical_voids,
            )
        )

        # INVARIANT 8: Semantic Compliance Requirement (The Curator)
        def check_semantic_compliance(events: List[Dict], ctx: Dict) -> Tuple[bool, Optional[str]]:
            """
            RULE: Policy and governance documents must maintain semantic integrity.
            No marketing hype, existential overreach, or AI slop allowed.

            Phase II Enhancement: Protects the semantic layer from hype and overreach.
            Scans governance documents for red-flag vocabulary.

            Checks:
            - POLICIES.md, MISSION_BRIEFING.md, AGI_MANIFESTO.md
            - All prompts/*.md system prompts
            - Documentation files in docs/

            Severity: HIGH (Warning/HIL Review, non-halting)
            """
            # Load semantic compliance config
            config_path = Path("config/semantic_compliance.yaml")
            if not config_path.exists():
                # Config not present, skip check
                return (True, None)

            try:
                import yaml

                with open(config_path) as f:
                    config = yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load semantic compliance config: {e}")
                return (True, None)

            red_flags = []
            if config and "RED_FLAGS" in config:
                # Flatten all red flags from all categories
                for category, words in config["RED_FLAGS"].items():
                    if isinstance(words, list):
                        red_flags.extend(words)

            if not red_flags:
                return (True, None)

            # Get scope from config
            scope = config.get("SCOPE", {}).get("CRITICAL_DOCUMENTS", [])
            if not scope:
                scope = [
                    "POLICIES.md",
                    "MISSION_BRIEFING.md",
                    "AGI_MANIFESTO.md",
                    "prompts/*.md",
                ]

            # Scan documents
            violations = []
            for pattern in scope:
                files_to_check = list(Path(".").glob(pattern))

                for file_path in files_to_check:
                    if not file_path.is_file():
                        continue

                    try:
                        content = file_path.read_text(encoding="utf-8")

                        # Check for red flags (case-insensitive word boundaries)
                        for red_flag in red_flags:
                            # Use word boundaries to avoid false positives
                            pattern_re = rf"\b{re.escape(red_flag)}\b"
                            matches = re.finditer(pattern_re, content, re.IGNORECASE)

                            for match in matches:
                                # Find line number for context
                                line_num = content[: match.start()].count("\n") + 1
                                violations.append(
                                    {
                                        "file": str(file_path),
                                        "line": line_num,
                                        "word": red_flag,
                                        "context": content[
                                            max(0, match.start() - 30) : min(len(content), match.end() + 30)
                                        ],
                                    }
                                )
                    except Exception as e:
                        logger.debug(f"Could not scan {file_path}: {e}")
                        continue

            # Report violations
            if violations:
                summary = f"Found {len(violations)} red-flag words in governance documents: "
                words_found = ", ".join(sorted(set(v["word"] for v in violations)))
                examples = "; ".join([f"{v['file']}:{v['line']}" for v in violations[:3]])
                detail_msg = f"{summary}{words_found}. Examples: {examples}"

                return (False, detail_msg)

            return (True, None)

        # Register the semantic compliance rule (optional, loads if config exists)
        self.register_rule(
            InvariantRule(
                name="SEMANTIC_COMPLIANCE_REQUIREMENT",
                description="Governance documents must maintain semantic integrity (no hype, no overreach)",
                severity=InvariantSeverity.HIGH,
                check_function=check_semantic_compliance,
            )
        )

        logger.info(f"⚖️  JUDGE: {len(self.rules)} core invariant rules registered (including Curator)")

    def register_rule(self, rule: InvariantRule):
        """Register a new invariant rule"""
        self.rules[rule.name] = rule
        logger.info(f"⚖️  Rule registered: {rule.name} ({rule.severity.value})")

    def verify_ledger(self, events: List[Dict[str, Any]]) -> VerificationReport:
        """
        Verify a list of events against all registered invariants.

        Args:
            events: List of events from the ledger

        Returns:
            VerificationReport with all violations found
        """
        logger.info(f"⚖️  JUDGE: Verifying {len(events)} events against {len(self.rules)} invariants")

        report = VerificationReport()
        report.checked_events = len(events)

        # Run each rule
        for rule_name, rule in self.rules.items():
            logger.debug(f"  Checking: {rule_name}...")

            passed, message = rule.check(events)

            if not passed:
                violation = InvariantViolation(
                    invariant_name=rule_name,
                    severity=rule.severity.value,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    message=message or "Rule check failed",
                    violated_events=[],
                    context={
                        "rule_description": rule.description,
                        "total_events_checked": len(events),
                    },
                )

                logger.warning(f"⚖️  VIOLATION: {rule_name} ({rule.severity.value}) - {message}")

                report.add_violation(violation)
            else:
                logger.debug(f"  ✅ PASS: {rule_name}")

        # Summary
        logger.info(f"⚖️  JUDGE: Verification complete")
        logger.info(f"   Events checked: {report.checked_events}")
        logger.info(f"   Violations found: {len(report.violations)}")
        logger.info(f"   Status: {'✅ PASS' if report.passed else '❌ FAIL'}")

        return report


# Singleton instance
_judge_instance: Optional[InvariantEngine] = None


def get_judge() -> InvariantEngine:
    """Get or create the singleton Judge instance"""
    global _judge_instance
    if _judge_instance is None:
        _judge_instance = InvariantEngine()
    return _judge_instance


__all__ = [
    "InvariantEngine",
    "InvariantRule",
    "InvariantViolation",
    "VerificationReport",
    "InvariantSeverity",
    "get_judge",
]
