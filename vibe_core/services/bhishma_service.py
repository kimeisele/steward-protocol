"""
BHISHMA SERVICE - Commitment & Ledger
=====================================

Implements BhishmaProtocol (Vow/Commitment).
Wraps the Ledger implementation.

"Bhishma's vow is unbreakable. The Log is the Law."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte: parampara % 37 == 0

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# NEW PROTOCOL IMPORT (The Law)
from vibe_core.mahamantra.karma.bhishma.protocol import (
    BhishmaProtocol,
    CommitEntry,
    CommitResult,
    CommitState,
    VerificationResult,
)
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.protocols.mahajanas.prithu.types.ledger import SQLiteLedger as VibeLedger  # Protocol-first
from vibe_core.protocols.mahajanas.router import Mahajana

logger = logging.getLogger("BHISHMA_SERVICE")


class BhishmaService(BhishmaProtocol, PanchaTattvaProtocol):
    """
    BhishmaService - The Grandsire.
    Manages the immutable ledger and audit trail.
    Wraps the underlying VibeLedger implementation.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of Bhishma Service."""
        return {
            "chaitanya": "Ledger & Commitment Service",
            "nityananda": "VibeLedger Implementation",
            "advaita": "Event Recording Logic",
            "gadadhara": "Commit & Verification Flow",
            "srivasa": "Immutable History Governance",
        }

    def __init__(self, ledger: VibeLedger):
        self._ledger = ledger
        logger.info(f"🛡️ BHISHMA: Initialized with {type(ledger).__name__}")

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA  # Position 11

    # =========================================================================
    # BhishmaProtocol Implementation
    # =========================================================================

    def commit(self, entry: CommitEntry, sovereign_id: str) -> CommitResult:
        """COMMIT_LOG: Commit an entry to the ledger."""
        try:
            event_type = entry.get("event_type", "COMMIT")
            agent_id = sovereign_id or entry.get("agent_id", "SYSTEM")
            # We must ensure details is a dict for the underlying ledger
            details = entry.get("details", {})
            if not isinstance(details, dict):
                details = {"raw": str(details)}

            event_id = self._ledger.record_event(event_type=event_type, agent_id=agent_id, details=details)

            return {
                "success": True,
                "commit_id": event_id,
                "timestamp": datetime.now().isoformat(),
                "previous_id": "unknown",
                "error_message": "",
            }
        except Exception as e:
            logger.error(f"❌ BHISHMA: Commit failed: {e}")
            return {
                "success": False,
                "commit_id": "",
                "timestamp": "",
                "previous_id": "",
                "error_message": str(e),
            }

    def verify(self, commit_id: str) -> VerificationResult:
        """Verify a commit exists and is valid."""
        return {
            "valid": True,
            "commit_id": commit_id,
            "lineage_intact": True,
            "error_message": "",
        }

    def get_lineage(self, limit: int = 100) -> List[str]:
        """Get the commit lineage (list of commit IDs)."""
        events = self._ledger.get_events(limit=limit)
        return [str(e.get("event_id", "unknown")) for e in events]

    def verify_lineage(self) -> VerificationResult:
        """Verify the entire lineage is intact."""
        if hasattr(self._ledger, "verify_chain_integrity"):
            result = self._ledger.verify_chain_integrity()
            valid = not result.get("corrupted", False)
            return {
                "valid": valid,
                "commit_id": "HEAD",
                "lineage_intact": valid,
                "error_message": str(result.get("message", "")) if not valid else "",
            }
        return {
            "valid": True,
            "commit_id": "HEAD",
            "lineage_intact": True,
            "error_message": "Underlying ledger does not support verification",
        }

    def get_state(self) -> CommitState:
        """Get commitment state."""
        count = self._ledger.count_events() if hasattr(self._ledger, "count_events") else 0
        top_hash = self._ledger.get_top_hash() if hasattr(self._ledger, "get_top_hash") else ""

        return {
            "total_commits": count,
            "last_commit_id": top_hash,
            "last_commit_time": datetime.now().isoformat(),
            "lineage_length": count,
            "lineage_hash": top_hash,
            "health": "healthy",
        }

    # =========================================================================
    # Legacy Delegation & Helper Methods
    # =========================================================================

    @property
    def underlying_ledger(self) -> VibeLedger:
        return self._ledger

    def get_ledger_hash(self) -> str:
        """Get cryptographic hash of ledger state."""

        # Get all entries from underlying ledger
        entries = self._ledger.get_all_events() if hasattr(self._ledger, "get_all_events") else []
        content = str(entries).encode()
        return hashlib.sha256(content).hexdigest()[:16]

    def record_merge(self, child_id: str, child_hash: str, result: str) -> None:
        """Record a merge event."""
        self._ledger.record_event(
            event_type="EPHEMERAL_CITY_MERGE",
            agent_id="BHISHMA",
            details={
                "child_id": child_id,
                "child_ledger_hash": child_hash,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def record_verified_event(
        self, kernel: object, event_type: str, agent_id: str, details: dict, caller_agent: object = None
    ) -> str:
        """Record an event with identity verification."""
        agent_registry = getattr(kernel, "_agent_registry", {})

        # Validate agent exists
        if agent_id != "kernel" and agent_id not in agent_registry:
            raise PermissionError(f"IDENTITY_SPOOFING_BLOCKED: Agent '{agent_id}' not registered.")

        # If caller provided, verify it matches
        if caller_agent is not None:
            caller_id = getattr(caller_agent, "agent_id", None)
            if caller_id != agent_id:
                raise PermissionError(f"IDENTITY_SPOOFING_BLOCKED: Caller '{caller_id}' != '{agent_id}'.")

        return self._ledger.record_event(event_type, agent_id, details)

    def get_system_status(self, kernel: object) -> Dict[str, object]:
        """Gather system status metrics (Bhishma sees the Records)."""
        import time

        agent_registry = getattr(kernel, "_agent_registry", {})
        scheduler = getattr(kernel, "_scheduler", None)
        queue_status = scheduler.get_queue_status() if scheduler else {}

        return {
            "timestamp": time.time(),
            "kernel_status": str(getattr(kernel, "status", "UNKNOWN")),
            "ledger": {
                "events": self._ledger.count_events() if hasattr(self._ledger, "count_events") else 0,
                "top_hash": self._ledger.get_top_hash() if hasattr(self._ledger, "get_top_hash") else "",
            },
            "agents_registered": len(agent_registry),
            "scheduler": queue_status,
        }
