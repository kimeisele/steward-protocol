"""
ARCHIVIST Audit Ledger - Wrapper over Kernel Ledger (OPUS-070 VAJRA)

REFACTORED: No longer maintains separate JSONL file.
Delegates ALL operations to kernel.ledger (SRUTI - Single Source of Truth).

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    KERNEL (The Soul)                        │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │  kernel.ledger = SRUTI (SQLiteLedger)                 │  │
    │  │  - Hash-chained, ECDSA signed                         │  │
    │  │  - Single Source of Truth for ALL events              │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
                                │
                        READS/WRITES (via kernel)
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    AuditLedger (VIEW)                       │
    │                                                             │
    │  - Filters kernel.ledger for attestation events             │
    │  - Provides ARCHIVIST-specific query methods                │
    │  - NO separate storage (delegated to kernel)                │
    └─────────────────────────────────────────────────────────────┘
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xdf4e2e5c"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("ARCHIVIST_LEDGER")

# Event type prefix for ARCHIVIST attestations
ARCHIVIST_EVENT_PREFIX = "archivist_"


class AuditLedger:
    """
    ARCHIVIST Audit Ledger - VIEW over kernel.ledger.

    OPUS-070 VAJRA: Delegates to kernel.ledger instead of maintaining
    separate storage. This ensures Single Source of Truth.

    Usage:
        ledger = AuditLedger()
        ledger.inject_kernel(kernel)  # ⚡ VAJRA binding

        # Write attestation (goes to kernel.ledger)
        event_id = ledger.record_attestation(...)

        # Read attestations (filters kernel.ledger)
        attestations = ledger.get_attestations()
    """

    def __init__(self):
        """Initialize AuditLedger (kernel injected later via VAJRA)."""
        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel: Optional["RealVibeKernel"] = None
        self._attestation_count = 0
        logger.info("📖 AuditLedger initialized (waiting for kernel injection)")

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        OPUS-070: AuditLedger MUST delegate to kernel.ledger.
        Without kernel injection, it operates in "shadow mode" (no persistence).

        Args:
            kernel: The RealVibeKernel instance with ledger access
        """
        self._vibe_kernel = kernel
        logger.info("⚡ ARCHIVIST: Kernel injected - ledger binding ACTIVE")

    def _get_ledger(self):
        """Get kernel.ledger via VAJRA binding."""
        if self._vibe_kernel is None:
            logger.debug("⚠️ ARCHIVIST: No kernel - shadow mode")
            return None

        if not hasattr(self._vibe_kernel, "ledger"):
            logger.warning("⚠️ ARCHIVIST: Kernel has no ledger attribute")
            return None

        return self._vibe_kernel.ledger

    # ==================== ATTESTATION OPERATIONS ====================

    def record_attestation(
        self,
        target_event: Dict[str, Any],
        verification_result: Dict[str, Any],
        status: str = "VERIFIED",
    ) -> Optional[str]:
        """
        Record an attestation to kernel.ledger.

        Args:
            target_event: The event being attested (from another agent)
            verification_result: Verification proof details
            status: "VERIFIED" or "FAILED"

        Returns:
            Event ID if recorded, None if shadow mode
        """
        ledger = self._get_ledger()
        if ledger is None:
            logger.warning("⚠️ ARCHIVIST: Cannot record attestation - shadow mode")
            return None

        details = {
            "target_event": target_event,
            "verification_result": verification_result,
            "attestation_status": status,
        }

        event_id = ledger.record_event(
            event_type=f"{ARCHIVIST_EVENT_PREFIX}attestation",
            agent_id="archivist",
            details=details,
        )

        self._attestation_count += 1
        logger.info(f"✅ ARCHIVIST: Attestation recorded → {event_id}")
        return event_id

    def get_attestations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all attestation events from kernel.ledger.

        Args:
            limit: Maximum number of attestations to return

        Returns:
            List of attestation events (filtered from kernel.ledger)
        """
        ledger = self._get_ledger()
        if ledger is None:
            return []

        all_events = ledger.get_all_events()
        attestations = [e for e in all_events if e.get("event_type", "").startswith(ARCHIVIST_EVENT_PREFIX)]

        return attestations[-limit:] if len(attestations) > limit else attestations

    def get_attestations_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all attestations targeting a specific agent.

        Args:
            agent_id: Agent identifier to filter by

        Returns:
            List of attestations for that agent
        """
        attestations = self.get_attestations(limit=1000)
        return [a for a in attestations if a.get("details", {}).get("target_event", {}).get("agent_id") == agent_id]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get attestation statistics.

        Returns:
            Statistics dict with counts and status
        """
        attestations = self.get_attestations(limit=10000)
        verified_count = sum(1 for a in attestations if a.get("details", {}).get("attestation_status") == "VERIFIED")
        failed_count = sum(1 for a in attestations if a.get("details", {}).get("attestation_status") == "FAILED")

        return {
            "total_attestations": len(attestations),
            "verified": verified_count,
            "failed": failed_count,
            "session_count": self._attestation_count,
            "source": "kernel.ledger (SRUTI)",
            "wired": self._vibe_kernel is not None,
        }

    # ==================== LEGACY COMPATIBILITY ====================
    # These methods maintain backward compatibility with old code

    def append(self, attestation: Dict[str, Any]) -> bool:
        """
        Legacy method: Append attestation.

        DEPRECATED: Use record_attestation() instead.
        """
        logger.warning("⚠️ AuditLedger.append() is deprecated - use record_attestation()")
        event_id = self.record_attestation(
            target_event=attestation.get("target_event", {}),
            verification_result=attestation,
            status=attestation.get("status", "RECORDED"),
        )
        return event_id is not None

    def read_all(self) -> List[Dict[str, Any]]:
        """
        Legacy method: Read all attestations.

        DEPRECATED: Use get_attestations() instead.
        """
        return self.get_attestations(limit=10000)

    def read_latest(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Legacy method: Read latest N attestations.
        """
        return self.get_attestations(limit=count)


# Factory function
def get_audit_ledger() -> AuditLedger:
    """Get an AuditLedger instance (requires kernel injection)."""
    return AuditLedger()
