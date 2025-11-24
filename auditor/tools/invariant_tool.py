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

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

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
        if violation.severity in [InvariantSeverity.CRITICAL.value, InvariantSeverity.HIGH.value]:
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
                        return (False, 
                                f"BROADCAST event at index {i} missing LICENSE_VALID in task {task_id}")
            
            return (True, None)
        
        self.register_rule(InvariantRule(
            name="BROADCAST_LICENSE_REQUIREMENT",
            description="Every BROADCAST must be preceded by LICENSE_VALID in same task",
            severity=InvariantSeverity.CRITICAL,
            check_function=check_broadcast_license
        ))

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
                        return (False,
                                f"CREDIT_TRANSFER at index {i} missing PROPOSAL_PASSED in task {task_id}")
            
            return (True, None)
        
        self.register_rule(InvariantRule(
            name="CREDIT_TRANSFER_PROPOSAL_REQUIREMENT",
            description="Every CREDIT_TRANSFER must be preceded by PROPOSAL_PASSED",
            severity=InvariantSeverity.CRITICAL,
            check_function=check_credit_transfer_proposal
        ))

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
        
        self.register_rule(InvariantRule(
            name="NO_ORPHANED_EVENTS",
            description="Every event must have task_id, agent_id, event_type, and timestamp",
            severity=InvariantSeverity.HIGH,
            check_function=check_no_orphaned_events
        ))

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
                        return (False,
                                f"Events out of order in task {task_id}: "
                                f"event {prev_idx} ({prev_ts}) before event {curr_idx} ({curr_ts})")
            
            return (True, None)
        
        self.register_rule(InvariantRule(
            name="EVENT_SEQUENCE_INTEGRITY",
            description="Events within a task must be in chronological order",
            severity=InvariantSeverity.HIGH,
            check_function=check_event_sequence
        ))

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
                    event.get("timestamp")
                )
                
                if key in seen:
                    return (False,
                            f"Duplicate event detected: event {i} matches event {seen[key]} "
                            f"(task={key[0]}, type={key[1]})")
                
                seen[key] = i
            
            return (True, None)
        
        self.register_rule(InvariantRule(
            name="NO_DUPLICATE_EVENTS",
            description="No duplicate events allowed (checked by task_id + event_type + timestamp)",
            severity=InvariantSeverity.CRITICAL,
            check_function=check_no_duplicates
        ))

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
                        return (False,
                                f"PROPOSAL_VOTED_YES at index {i} has no preceding "
                                f"PROPOSAL_CREATED for proposal_id={proposal_id}")
            
            return (True, None)
        
        self.register_rule(InvariantRule(
            name="PROPOSAL_WORKFLOW_INTEGRITY",
            description="PROPOSAL_VOTED_YES must follow PROPOSAL_CREATED for same proposal",
            severity=InvariantSeverity.HIGH,
            check_function=check_proposal_workflow
        ))

        logger.info(f"⚖️  JUDGE: {len(self.rules)} core invariant rules registered")

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
                        "total_events_checked": len(events)
                    }
                )
                
                logger.warning(
                    f"⚖️  VIOLATION: {rule_name} ({rule.severity.value}) - {message}"
                )
                
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
