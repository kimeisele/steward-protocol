#!/usr/bin/env python3
"""
THE WATCHDOG - Runtime Verification Daemon

This component integrates the Judge (Invariant Engine) into the kernel loop.
It monitors the ledger stream continuously and triggers alarms on violations.

Architecture:
- Runs in parallel with kernel tasks (can be a background task)
- Periodically audits the ledger for invariant violations
- Records VIOLATION events when problems are detected
- Communicates with Envoy for emergency notifications
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

logger = logging.getLogger("WATCHDOG")


@dataclass
class WatchdogConfig:
    """Configuration for the Watchdog"""
    # How often to check (in task ticks or seconds)
    check_interval: int = 10
    
    # Path to kernel ledger
    ledger_path: Path = Path("data/ledger/kernel.jsonl")
    
    # Where to write violation records
    violations_path: Path = Path("data/ledger/violations.jsonl")
    
    # Should we halt system on CRITICAL violations?
    halt_on_critical: bool = True
    
    # Should we notify Envoy?
    notify_envoy: bool = True


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


class Watchdog:
    """
    Runtime Verification Daemon - THE WATCHDOG
    
    Monitors system invariants and triggers alarms on violations.
    """

    def __init__(self, config: WatchdogConfig = None):
        """
        Initialize the Watchdog.
        
        Args:
            config: WatchdogConfig instance (uses defaults if None)
        """
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
        from auditor.tools.invariant_tool import get_judge
        
        # Get new events since last check
        new_events = self.read_ledger_events(self.last_checked_index)
        
        if not new_events:
            logger.debug("👁️  No new events to check")
            return {
                "status": "idle",
                "new_events": 0,
                "violations": []
            }
        
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
                        "violations_count": len(report.violations)
                    }
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
                    logger.error(f"👁️  🚨 CRITICAL VIOLATION - INITIATING SYSTEM HALT")
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
            "halt_requested": self.halt_requested
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
            return {
                "status": "error",
                "error": str(e)
            }


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
                    "check_result": result
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
            }
        }


__all__ = [
    "Watchdog",
    "WatchdogConfig",
    "ViolationEvent",
    "WatchdogIntegration",
]
