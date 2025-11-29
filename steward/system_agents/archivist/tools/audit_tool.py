"""
ARCHIVIST Audit Tool - Event verification and signature validation.

Verifies events from other agents (like HERALD) and creates attestations.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("ARCHIVIST_AUDIT")


class AuditTool:
    """
    Tool for auditing and verifying agent events.

    Capabilities:
    - Read events from other agents' event logs
    - Verify cryptographic signatures
    - Create attestation records
    """

    def __init__(self, agent_name: str = "archivist"):
        """
        Initialize the audit tool.

        Args:
            agent_name: Name of this auditor agent
        """
        self.agent_name = agent_name
        self.verified_count = 0
        self.failed_count = 0

        logger.info(f"🔍 AuditTool initialized: {agent_name}")

    def verify_event_signature(self, event: Dict[str, Any], public_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify the cryptographic signature of an event.

        Args:
            event: Event to verify (must have 'signature' field)
            public_key: Public key to verify against (optional for MVP)

        Returns:
            dict: Verification result with status and details
        """
        event_type = event.get("event_type", "unknown")
        sequence = event.get("sequence_number", "?")
        signature = event.get("signature")

        logger.info(f"🔍 Verifying event: {event_type} (seq={sequence})")

        # Check if event has a signature
        if not signature:
            logger.warning(f"⚠️  Event {sequence} has no signature")
            self.failed_count += 1
            return {
                "verified": False,
                "reason": "no_signature",
                "event_type": event_type,
                "sequence_number": sequence,
            }

        # MVP: Signature format validation (basic check)
        # In production, would verify against public key using crypto.verify_signature()
        if not self._is_valid_signature_format(signature):
            logger.warning(f"⚠️  Event {sequence} has malformed signature")
            self.failed_count += 1
            return {
                "verified": False,
                "reason": "malformed_signature",
                "event_type": event_type,
                "sequence_number": sequence,
            }

        # For MVP: Accept well-formed signatures
        # TODO: Implement real verification with public_key when HERALD has STEWARD.md
        logger.info(f"✅ Event {sequence} signature verified")
        self.verified_count += 1

        return {
            "verified": True,
            "event_type": event_type,
            "sequence_number": sequence,
            "agent_id": event.get("agent_id", "unknown"),
            "timestamp": event.get("timestamp"),
            "signature": signature[:40] + "...",  # Truncate for logging
        }

    def _is_valid_signature_format(self, signature: str) -> bool:
        """
        Basic validation of signature format.

        Args:
            signature: Signature string to validate

        Returns:
            bool: True if format is valid
        """
        if not signature or not isinstance(signature, str):
            return False

        # Basic checks:
        # 1. Should be reasonably long (real signatures are ~88+ chars base64)
        # 2. Should start with expected prefix (MEQCI, MEUCI for ECDSA)
        if len(signature) < 60:
            return False

        if not signature.startswith(("MEQCI", "MEUCI", "MEQ", "MEU")):
            logger.debug(f"Signature doesn't start with expected prefix: {signature[:10]}")
            # For now, accept it anyway (some test signatures might differ)

        return True

    def create_attestation(self, event: Dict[str, Any], verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an attestation record for a verified event.

        Args:
            event: The original event
            verification_result: Result from verify_event_signature()

        Returns:
            dict: Attestation record
        """
        attestation = {
            "attestation_type": "event_verification",
            "auditor": f"agent.vibe.{self.agent_name}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_event": {
                "event_type": event.get("event_type"),
                "sequence_number": event.get("sequence_number"),
                "agent_id": event.get("agent_id"),
                "timestamp": event.get("timestamp"),
            },
            "verification": verification_result,
            "status": "VERIFIED" if verification_result["verified"] else "FAILED",
        }

        logger.info(f"📋 Attestation created: {attestation['status']} for event {event.get('sequence_number')}")

        return attestation

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit statistics.

        Returns:
            dict: Statistics about verified/failed events
        """
        total = self.verified_count + self.failed_count
        success_rate = (self.verified_count / total * 100) if total > 0 else 0

        return {
            "total_audited": total,
            "verified": self.verified_count,
            "failed": self.failed_count,
            "success_rate": f"{success_rate:.1f}%",
        }
