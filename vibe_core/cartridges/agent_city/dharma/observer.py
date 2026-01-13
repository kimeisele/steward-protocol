"""
DHARMA Observer - The Watchful Eye

Subscribes to system events and detects violations of Dharmic principles.
When violations are detected, creates repair tasks for the engineer agent.

ARCHITECTURE (GAD-000 Compliant):
    ┌─────────────────────────────────────────────────────────────────┐
    │                    CORE (Event Bus)                              │
    │       SYSCALL_EXECUTED, VIOLATION, ERROR events                  │
    └─────────────────────────────────────────────────────────────────┘
                              │ Events flow down
                              ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    DHARMA Observer                               │
    │  ┌─────────────────────────────────────────────────────────────┐│
    │  │       _on_event() → _detect_violation()                     ││
    │  │                     │                                       ││
    │  │                     ▼                                       ││
    │  │       If violation: _create_repair_task()                   ││
    │  │                     │                                       ││
    │  │                     ▼                                       ││
    │  │       Task → engineer agent OR task_ledger                  ││
    │  └─────────────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────────────┘

The Self-Correction Loop: Observe → Detect → Repair
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x91d0ddbe"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.cartridges.agent_city.dharma.cartridge_main import DharmaCartridge

logger = logging.getLogger("DHARMA.OBSERVER")


class DharmaObserver:
    """
    The Watchful Eye - Proactive violation detection.

    Subscribes to EventBus and monitors for Dharmic violations:
    - force_push, bypass, skip_tests, --no-verify
    - Constitution violations
    - Error patterns that indicate systemic issues

    When violations are detected, creates repair tasks.
    """

    # Violation patterns to detect
    VIOLATION_PATTERNS = {
        "himsa": ["force", "bypass", "override", "delete_kernel"],
        "asteya": ["skip_tests", "skip_checks", "no_test"],
        "aparigraha": ["--no-verify", "no-verify", "--force"],
        "asatya": ["fake", "mock_production", "lie"],
    }

    def __init__(self, cartridge: Optional["DharmaCartridge"] = None):
        """
        Initialize the observer.

        Args:
            cartridge: Reference to parent DharmaCartridge for task creation.
        """
        self._cartridge = cartridge
        self._subscribed = False
        self._violations_detected = 0
        self._repairs_created = 0
        self._event_count = 0

    def subscribe(self) -> bool:
        """
        Subscribe to relevant events from the EventBus.

        Returns:
            True if subscription successful, False otherwise.
        """
        try:
            from vibe_core.event_bus import EventType, get_event_bus

            bus = get_event_bus()

            # Subscribe to syscall events (main observation point)
            bus.subscribe(self._on_syscall_event, EventType.SYSCALL_EXECUTED)

            # Subscribe to violation events (already flagged)
            bus.subscribe(self._on_violation_event, EventType.VIOLATION)

            # Subscribe to error events (might indicate issues)
            bus.subscribe(self._on_error_event, EventType.ERROR)

            self._subscribed = True
            logger.info("👁️ DharmaObserver subscribed to EventBus (SYSCALL, VIOLATION, ERROR)")
            return True

        except ImportError:
            logger.debug("EventBus not available - observer disabled")
            return False
        except Exception as e:
            logger.debug(f"Could not subscribe to events: {e}")
            return False

    def unsubscribe(self) -> None:
        """Unsubscribe from all events."""
        if not self._subscribed:
            return

        try:
            from vibe_core.event_bus import EventType, get_event_bus

            bus = get_event_bus()
            bus.unsubscribe(self._on_syscall_event, EventType.SYSCALL_EXECUTED)
            bus.unsubscribe(self._on_violation_event, EventType.VIOLATION)
            bus.unsubscribe(self._on_error_event, EventType.ERROR)

            self._subscribed = False
            logger.info("👁️ DharmaObserver unsubscribed from EventBus")

        except Exception as e:
            logger.debug(f"Could not unsubscribe: {e}")

    def _on_syscall_event(self, event: Any) -> None:
        """
        Handle SYSCALL_EXECUTED events.

        This is the main observation point - every syscall passes through here.
        We check if the syscall parameters contain violation patterns.
        """
        self._event_count += 1

        try:
            # Extract syscall details
            details = getattr(event, "details", {}) or {}
            syscall_type = details.get("syscall_type", "")
            params = details.get("params", {})
            agent_id = getattr(event, "agent_id", "unknown")

            # Check for violations in the syscall
            violations = self._detect_violations(syscall_type, params, agent_id)

            if violations:
                self._violations_detected += len(violations)
                for violation in violations:
                    logger.warning(f"⚠️ DHARMA detected violation: {violation}")
                    self._create_repair_task(violation, event)

        except Exception as e:
            logger.debug(f"Error processing syscall event: {e}")

    def _on_violation_event(self, event: Any) -> None:
        """
        Handle VIOLATION events (already flagged by other systems).

        These are serious - someone else already detected a constitutional breach.
        """
        self._event_count += 1
        self._violations_detected += 1

        try:
            details = getattr(event, "details", {}) or {}
            agent_id = getattr(event, "agent_id", "unknown")
            message = getattr(event, "message", "Unknown violation")

            violation = {
                "type": "constitutional",
                "principle": "VIOLATION",
                "agent": agent_id,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "HIGH",
            }

            logger.warning(f"🚨 DHARMA received VIOLATION event from {agent_id}: {message}")
            self._create_repair_task(violation, event)

        except Exception as e:
            logger.debug(f"Error processing violation event: {e}")

    def _on_error_event(self, event: Any) -> None:
        """
        Handle ERROR events.

        Not all errors are violations, but repeated errors might indicate issues.
        """
        self._event_count += 1

        # For now, just count errors. Could implement pattern detection.
        try:
            agent_id = getattr(event, "agent_id", "unknown")

            # Log but don't create repair task for every error
            logger.debug(f"📝 DHARMA observed ERROR from {agent_id}")

        except Exception as e:
            logger.debug(f"Error processing error event: {e}")

    def _detect_violations(self, syscall_type: str, params: Dict[str, Any], agent_id: str) -> List[Dict[str, Any]]:
        """
        Detect Dharmic violations in syscall parameters.

        Returns list of violation dicts.
        """
        violations = []
        params_str = str(params).lower()
        syscall_lower = syscall_type.lower()

        for principle, patterns in self.VIOLATION_PATTERNS.items():
            for pattern in patterns:
                if pattern in params_str or pattern in syscall_lower:
                    violations.append(
                        {
                            "type": "dharmic",
                            "principle": principle,
                            "pattern": pattern,
                            "agent": agent_id,
                            "syscall": syscall_type,
                            "timestamp": datetime.utcnow().isoformat(),
                            "severity": "MEDIUM" if principle != "himsa" else "HIGH",
                        }
                    )

        return violations

    def _create_repair_task(self, violation: Dict[str, Any], event: Any) -> None:
        """
        Create a repair task for the engineer agent.

        This is the "Self-Correction Loop" - DHARMA observes violations
        and creates tasks to fix them.
        """
        self._repairs_created += 1

        try:
            # Build repair task description
            principle = violation.get("principle", "unknown")
            agent = violation.get("agent", "unknown")
            pattern = violation.get("pattern", "unknown")
            severity = violation.get("severity", "MEDIUM")

            task_description = (
                f"DHARMA Repair Request [{severity}]\n"
                f"Violation: {principle.upper()}\n"
                f"Pattern: {pattern}\n"
                f"Agent: {agent}\n"
                f"Action: Review and remediate the violation. "
                f"Consider adding pre-commit hooks or governance rules."
            )

            # Try to create task via kernel's task system
            if self._cartridge and hasattr(self._cartridge, "system"):
                system = self._cartridge.system
                if system and hasattr(system, "create_task"):
                    system.create_task(
                        agent_id="engineer",
                        payload={
                            "action": "repair",
                            "violation": violation,
                            "description": task_description,
                            "priority": 1 if severity == "HIGH" else 2,
                        },
                    )
                    logger.info(f"🔧 Repair task created for engineer: {principle}")
                    return

            # Fallback: Log the repair request
            logger.info(f"🔧 Repair needed (no task system): {task_description}")

            # Try to write to task ledger file as fallback
            self._write_to_task_ledger(violation, task_description)

        except Exception as e:
            logger.debug(f"Could not create repair task: {e}")

    def _write_to_task_ledger(self, violation: Dict[str, Any], description: str) -> None:
        """
        Fallback: Log repair task when task system unavailable.

        Note: We log repairs instead of writing to files to maintain
        VFS isolation (GAD-000 compliance). The cartridge can retrieve
        repair stats via get_stats() for periodic processing.
        """
        import json

        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "violation": violation,
                "description": description,
                "status": "pending",
            }

            # Log the repair request (visible in logs)
            logger.info(f"📝 REPAIR REQUEST: {json.dumps(entry)}")

        except Exception as e:
            logger.debug(f"Could not write to ledger: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get observer statistics."""
        return {
            "subscribed": self._subscribed,
            "events_observed": self._event_count,
            "violations_detected": self._violations_detected,
            "repairs_created": self._repairs_created,
        }
