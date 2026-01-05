"""
Sesha CLI Hook - Audit Ledger

SESHA (ANANTA): The thousand-headed serpent who holds all records.
Here, he maintains the immutable audit trail of CLI operations.

Phases:
- POST_EXECUTE: Record successful execution
- ON_ERROR: Record failed execution

Records:
- Who executed (caller_id)
- What was executed (command, args)
- When (timestamp)
- Outcome (success/failure)
- Context (blocked_by, reason)

GAD-000: "Audit trail - All operations must be traceable"
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from vibe_core.protocols.cli_execution import (
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
)

logger = logging.getLogger("SESHA_CLI")


@dataclass
class CLIAuditEntry:
    """
    Immutable audit entry for CLI execution.

    Once written, cannot be modified (Sesha principle).
    """

    timestamp: str
    caller_id: str
    command: str
    namespace: str
    args: List[str]
    success: bool
    duration_ms: float
    blocked: bool = False
    blocked_by: str = ""
    blocked_reason: str = ""
    error: str = ""

    def to_json(self) -> str:
        """Serialize to JSON for storage."""
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "caller_id": self.caller_id,
                "command": self.command,
                "namespace": self.namespace,
                "args": self.args,
                "success": self.success,
                "duration_ms": self.duration_ms,
                "blocked": self.blocked,
                "blocked_by": self.blocked_by,
                "blocked_reason": self.blocked_reason,
                "error": self.error,
            },
            sort_keys=True,
        )


class SeshaCLIHook(CLIHookProtocol):
    """
    Sesha CLI Hook - Maintains immutable audit trail.

    POST_EXECUTE: Records successful command execution
    ON_ERROR: Records failed command execution

    Optional: Connects to Sesha NAGA service for persistent ledger.
    """

    def __init__(
        self,
        sesha_service: Optional[object] = None,
        log_to_file: Optional[str] = None,
        max_entries: int = 10000,
    ) -> None:
        """
        Initialize Sesha CLI hook.

        Args:
            sesha_service: Optional Sesha NAGA for persistent ledger
            log_to_file: Optional file path for audit log
            max_entries: Max in-memory entries before rotation
        """
        self._sesha = sesha_service
        self._log_file = log_to_file
        self._max_entries = max_entries
        self._entries: List[CLIAuditEntry] = []

    @property
    def hook_id(self) -> str:
        return "sesha"

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        """
        Record audit entries at POST_EXECUTE and ON_ERROR phases.
        """
        if phase == CLIExecutionPhase.POST_EXECUTE:
            self._record(context, success=True)
        elif phase == CLIExecutionPhase.ON_ERROR:
            self._record(context, success=False)

        # Sesha never blocks - only records
        return CLIHookResult(allow=True)

    def _record(self, context: CLIExecutionContext, success: bool) -> None:
        """Record an audit entry."""
        entry = CLIAuditEntry(
            timestamp=datetime.now().isoformat(),
            caller_id=context.caller_id,
            command=context.command_name,
            namespace=context.namespace,
            args=context.args,
            success=success,
            duration_ms=context.duration_ms,
            blocked=context.blocked,
            blocked_by=context.blocked_by,
            blocked_reason=context.blocked_reason,
        )

        # Add to in-memory list
        self._entries.append(entry)

        # Rotate if needed
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries // 2 :]

        # Log
        if success:
            logger.info(
                f"AUDIT: {entry.caller_id} executed {entry.namespace}.{entry.command} in {entry.duration_ms:.2f}ms"
            )
        else:
            logger.warning(
                f"AUDIT: {entry.caller_id} FAILED {entry.namespace}.{entry.command} "
                f"- blocked={entry.blocked}, reason={entry.blocked_reason}"
            )

        # Write to file if configured
        if self._log_file:
            self._write_to_file(entry)

        # Send to LIVING Sesha service - OUROBOROS connection to ledger
        if self._sesha:
            try:
                # SeshaService wraps SQLiteLedger - use _ledger.record_event()
                if hasattr(self._sesha, "_ledger") and self._sesha._ledger:
                    self._sesha._ledger.record_event(
                        event_type="CLI_COMMAND_EXECUTED",
                        agent_id=entry.caller_id,
                        details={
                            "command": f"{entry.namespace}.{entry.command}",
                            "args": entry.args[:5] if entry.args else [],  # Truncate for safety
                            "success": entry.success,
                            "blocked": entry.blocked,
                            "blocked_by": entry.blocked_by,
                            "duration_ms": round(entry.duration_ms, 2),
                        },
                        result="SUCCESS" if entry.success else "FAILED",
                    )
                    logger.debug(f"[SESHA-CLI] Recorded to living ledger: {entry.command}")
            except Exception as e:
                logger.debug(f"Sesha integration: {e}")

    def _write_to_file(self, entry: CLIAuditEntry) -> None:
        """Append entry to audit log file."""
        try:
            with open(self._log_file, "a") as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_entries(
        self,
        caller_id: Optional[str] = None,
        command: Optional[str] = None,
        success_only: bool = False,
        limit: int = 100,
    ) -> List[CLIAuditEntry]:
        """
        Query audit entries.

        Args:
            caller_id: Filter by caller
            command: Filter by command name
            success_only: Only return successful executions
            limit: Max entries to return

        Returns:
            List of matching audit entries (newest first)
        """
        results = []

        for entry in reversed(self._entries):
            if caller_id and entry.caller_id != caller_id:
                continue
            if command and entry.command != command:
                continue
            if success_only and not entry.success:
                continue

            results.append(entry)
            if len(results) >= limit:
                break

        return results

    def get_blocked_entries(self, limit: int = 100) -> List[CLIAuditEntry]:
        """Get entries that were blocked by hooks."""
        return [e for e in self._entries if e.blocked][-limit:]

    def get_stats(self) -> dict:
        """Get audit statistics."""
        total = len(self._entries)
        successful = sum(1 for e in self._entries if e.success)
        blocked = sum(1 for e in self._entries if e.blocked)

        return {
            "total_entries": total,
            "successful": successful,
            "failed": total - successful,
            "blocked": blocked,
            "unique_callers": len(set(e.caller_id for e in self._entries)),
            "unique_commands": len(set(e.command for e in self._entries)),
        }

    def clear(self) -> None:
        """Clear in-memory entries (for testing)."""
        self._entries.clear()
        logger.info("Sesha CLI audit entries cleared")
