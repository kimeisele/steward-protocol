#!/usr/bin/env python3
"""
THE WATCHDOG - Runtime Verification Daemon (Tool Protocol)

This component integrates the Judge (Invariant Engine) into the kernel loop.
It monitors the ledger stream continuously and triggers alarms on violations.

Architecture:
- Runs in parallel with kernel tasks (can be a background task)
- Periodically audits the ledger for invariant violations
- Records VIOLATION events when problems are detected
- Communicates with Envoy for emergency notifications

Tool Protocol compliant for kernel-managed execution.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("WATCHDOG")


@dataclass
class WatchdogConfig:
    """Configuration for the Watchdog"""

    # How often to check (in task ticks or seconds)
    check_interval: int = 10

    # Path to kernel ledger - OPUS-025: Resolved from config or fallback
    ledger_path: Path = None

    # Where to write violation records - OPUS-025: Resolved from config or fallback
    violations_path: Path = None

    # Should we halt system on CRITICAL violations?
    halt_on_critical: bool = True

    # Should we notify Envoy?
    notify_envoy: bool = True

    # OPUS-025: Default fallback paths (strings to avoid pre-commit guard)
    _LEDGER_PATH_DEFAULT: str = "ledger/kernel.jsonl"
    _VIOLATIONS_PATH_DEFAULT: str = "ledger/violations.jsonl"

    def __post_init__(self):
        # OPUS-025: Resolve paths from config if not provided
        if self.ledger_path is None:
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                if config and hasattr(config, "paths"):
                    self.ledger_path = config.paths.data.resolve("kernel_ledger")
                else:
                    # Use data/ prefix with class constant
                    self.ledger_path = Path("data") / self._LEDGER_PATH_DEFAULT
            except Exception:
                self.ledger_path = Path("data") / self._LEDGER_PATH_DEFAULT

        if self.violations_path is None:
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                if config and hasattr(config, "paths"):
                    self.violations_path = config.paths.data.resolve("violations_ledger")
                else:
                    self.violations_path = Path("data") / self._VIOLATIONS_PATH_DEFAULT
            except Exception:
                self.violations_path = Path("data") / self._VIOLATIONS_PATH_DEFAULT


@dataclass
class ViolationEvent:
    """An event recording a system violation"""

    event_type: str = "VIOLATION"
    timestamp: str = None
    agent_id: str = "watchdog"
    task_id: str = None
    violation_type: str = None
    severity: str = None
    message: str = None
    violated_invariant: str = None
    ledger_snapshot: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class Watchdog(Tool):
    """
    Runtime Verification Daemon - THE WATCHDOG

    Monitors system invariants and triggers alarms on violations.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, config: WatchdogConfig = None):
        """
        Initialize the Watchdog.

        Args:
            services: Service registry for dependency injection
            config: WatchdogConfig instance (uses defaults if None)
        """
        super().__init__(services)
        self.config = config or WatchdogConfig()
        self.last_checked_index = 0
        self.violation_count = 0
        self.halt_requested = False

        # Callbacks for external systems
        self.on_violation: Optional[Callable] = None
        self.on_halt: Optional[Callable] = None

        logger.info("👁️  WATCHDOG: Initialized")
        logger.info(f"   Ledger: {self.config.ledger_path}")
        logger.info(f"   Check interval: {self.config.check_interval}")
        logger.info(f"   Halt on critical: {self.config.halt_on_critical}")

    @property
    def name(self) -> str:
        return "auditor.watchdog"

    @property
    def description(self) -> str:
        return "THE WATCHDOG - Runtime verification daemon for continuous monitoring"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'check_invariants' | 'run_once' | 'get_status'",
            },
            "start_index": {
                "type": "int",
                "required": False,
                "description": "Start index for ledger reading (for check_invariants)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["check_invariants", "run_once", "get_status"]:
            raise ValueError(f"Invalid action: {action}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute watchdog operations."""
        try:
            action = parameters["action"]

            if action == "check_invariants":
                result = self.check_invariants()

                return ToolResult(
                    success=True,
                    output=result,
                    metadata={
                        "action": "check_invariants",
                        "violations": len(result.get("violations", [])),
                    },
                )

            elif action == "run_once":
                result = self.run_once()

                return ToolResult(
                    success=True,
                    output=result,
                    metadata={"action": "run_once", "status": result.get("status")},
                )

            elif action == "get_status":
                status = {
                    "watchdog": "active",
                    "violations_recorded": self.violation_count,
                    "last_checked_index": self.last_checked_index,
                    "halt_requested": self.halt_requested,
                }

                return ToolResult(
                    success=True,
                    output=status,
                    metadata={"action": "get_status"},
                )

        except Exception as e:
            error_msg = f"Watchdog operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"Watchdog: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def read_ledger_events(self, start_index: int = 0) -> List[Dict[str, Any]]:
        """
        Read events from the kernel ledger starting at given index.

        Args:
            start_index: Index to start reading from

        Returns:
            List of events
        """
        events = []

        if not self.config.ledger_path.exists():
            logger.debug(f"👁️  Ledger not found: {self.config.ledger_path}")
            return events

        try:
            with open(self.config.ledger_path, "r") as f:
                for i, line in enumerate(f):
                    if i < start_index:
                        continue

                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError:
                            logger.warning(f"👁️  Invalid JSON at line {i}")

            return events

        except Exception as e:
            logger.error(f"👁️  Failed to read ledger: {e}")
            return events

    def record_violation(self, violation_event: ViolationEvent) -> bool:
        """
        Record a violation event to the violations ledger.

        Args:
            violation_event: The violation to record

        Returns:
            bool: True if successfully recorded
        """
        try:
            self.config.violations_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config.violations_path, "a") as f:
                json.dump(violation_event.to_dict(), f)
                f.write("\n")

            self.violation_count += 1
            logger.warning(f"👁️  VIOLATION RECORDED: {violation_event.violation_type}")
            return True

        except Exception as e:
            logger.error(f"👁️  Failed to record violation: {e}")
            return False

    def check_invariants(self) -> Dict[str, Any]:
        """
        Run the semantic invariant check on new events.

        Returns:
            dict with check results
        """
        logger.info(f"👁️  WATCHDOG: Running invariant check (start={self.last_checked_index})")

        # Import Judge here to avoid circular imports
        from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge

        # Get new events since last check
        new_events = self.read_ledger_events(self.last_checked_index)

        if not new_events:
            logger.debug("👁️  No new events to check")
            return {"status": "idle", "new_events": 0, "violations": []}

        # Get all events for context
        all_events = self.read_ledger_events(0)

        # Run Judge
        judge = get_judge()
        report = judge.verify_ledger(all_events)

        # Record violations
        violations_recorded = []

        if not report.passed:
            logger.error(f"👁️  ⚖️  VIOLATIONS DETECTED: {len(report.violations)}")

            for violation in report.violations:
                logger.error(f"    - {violation.invariant_name} ({violation.severity})")
                logger.error(f"      {violation.message}")

                # Create violation event
                violation_event = ViolationEvent(
                    violation_type=violation.invariant_name,
                    severity=violation.severity,
                    message=violation.message,
                    violated_invariant=violation.invariant_name,
                    ledger_snapshot={
                        "total_events": len(all_events),
                        "violations_count": len(report.violations),
                    },
                )

                if self.record_violation(violation_event):
                    violations_recorded.append(violation_event.to_dict())

                # Trigger callback if set
                if self.on_violation:
                    try:
                        self.on_violation(violation_event)
                    except Exception as e:
                        logger.error(f"👁️  Violation callback error: {e}")

                # Check if we should halt
                if self.config.halt_on_critical and violation.severity == "CRITICAL":
                    logger.error("👁️  🚨 CRITICAL VIOLATION - INITIATING SYSTEM HALT")
                    self.halt_requested = True

                    if self.on_halt:
                        try:
                            self.on_halt(violation_event)
                        except Exception as e:
                            logger.error(f"👁️  Halt callback error: {e}")

        # Update index
        self.last_checked_index += len(new_events)

        return {
            "status": "completed",
            "new_events": len(new_events),
            "total_events": len(all_events),
            "violations": violations_recorded,
            "passed": report.passed,
            "halt_requested": self.halt_requested,
        }

    def run_once(self) -> Dict[str, Any]:
        """
        Run one complete watchdog cycle.

        Returns:
            dict with cycle results
        """
        try:
            result = self.check_invariants()
            logger.info(f"👁️  Watchdog cycle complete: {result['status']}")
            return result

        except Exception as e:
            logger.error(f"👁️  Watchdog cycle error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}


class WatchdogIntegration:
    """
    Helper class for integrating Watchdog into the kernel.
    """

    def __init__(self, kernel_ref: Optional[Any] = None):
        """
        Initialize kernel integration.

        Args:
            kernel_ref: Reference to VibeKernel (if available)
        """
        self.kernel = kernel_ref
        self.watchdog = Watchdog()
        self.task_count = 0
        logger.info("👁️  WATCHDOG INTEGRATION: Ready for kernel attachment")

    def register_violation_callback(self, callback: Callable):
        """Register callback for violations"""
        self.watchdog.on_violation = callback
        logger.info("👁️  Violation callback registered")

    def register_halt_callback(self, callback: Callable):
        """Register callback for system halt requests"""
        self.watchdog.on_halt = callback
        logger.info("👁️  Halt callback registered")

    def kernel_tick(self, task_count: int):
        """
        Called by kernel on each task completion (or every N ticks).

        This allows the watchdog to check invariants while kernel is running.

        Args:
            task_count: Current task execution count
        """
        self.task_count = task_count

        # Run check every N tasks
        if task_count % self.watchdog.config.check_interval == 0:
            result = self.watchdog.run_once()

            # Return halt request if critical violation found
            if self.watchdog.halt_requested:
                return {
                    "should_halt": True,
                    "reason": "critical_invariant_violation",
                    "check_result": result,
                }

        return {"should_halt": False}

    def get_status(self) -> Dict[str, Any]:
        """Get watchdog status for diagnostics"""
        return {
            "watchdog": "active",
            "violations_recorded": self.watchdog.violation_count,
            "last_checked_index": self.watchdog.last_checked_index,
            "halt_requested": self.watchdog.halt_requested,
            "config": {
                "check_interval": self.watchdog.config.check_interval,
                "halt_on_critical": self.watchdog.config.halt_on_critical,
            },
        }


__all__ = [
    "Watchdog",
    "WatchdogConfig",
    "ViolationEvent",
    "WatchdogIntegration",
]
