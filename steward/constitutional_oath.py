#!/usr/bin/env python3
"""
CONSTITUTIONAL OATH - Cryptographic Attestation of Governance Binding.

When an agent boots, it must:
1. Read the Constitution
2. Hash it (SHA-256)
3. Sign the hash with its identity
4. Record the oath in the immutable ledger

This is the "Genesis Ceremony" – the moment an agent binds itself to Truth.
"""

import hashlib
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("CONSTITUTIONAL_OATH")


class ConstitutionalOath:
    """
    Implements cryptographic binding of agents to the Constitution.
    
    This is NOT policy enforcement. This is metaphysical commitment.
    The agent says: "I bind myself to this Truth, and I sign this binding."
    """

    CONSTITUTION_PATH = Path("CONSTITUTION.md")
    OATH_EVENT_TYPE = "CONSTITUTIONAL_OATH"

    @staticmethod
    def compute_constitution_hash() -> str:
        """
        Compute SHA-256 hash of current Constitution.
        
        Returns:
            Hex string of the constitution hash
            
        Raises:
            FileNotFoundError: If CONSTITUTION.md not found
        """
        if not ConstitutionalOath.CONSTITUTION_PATH.exists():
            raise FileNotFoundError(
                f"Constitution not found at {ConstitutionalOath.CONSTITUTION_PATH}"
            )

        with open(ConstitutionalOath.CONSTITUTION_PATH, "rb") as f:
            constitution_bytes = f.read()
            constitution_hash = hashlib.sha256(constitution_bytes).hexdigest()

        logger.info(f"📜 Constitution hash computed: {constitution_hash[:16]}...")
        return constitution_hash

    @staticmethod
    def create_oath_event(
        agent_id: str,
        constitution_hash: str,
        signature: str,
        block_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a Constitutional Oath attestation event.
        
        Args:
            agent_id: The agent swearing the oath
            constitution_hash: SHA-256 of the Constitution
            signature: Cryptographic signature from agent's private key
            block_number: Ledger block number (optional)
            
        Returns:
            Oath event dictionary ready for ledger
        """
        event = {
            "type": ConstitutionalOath.OATH_EVENT_TYPE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_id,
            "constitution_hash": constitution_hash,
            "constitution_hash_short": constitution_hash[:16],
            "signature": signature[:32] + "..." if len(signature) > 32 else signature,
            "signature_full": signature,
            "status": "SWORN",
            "event_id": f"oath_{agent_id}_{constitution_hash[:8]}"
        }

        if block_number is not None:
            event["block_number"] = block_number

        return event

    @staticmethod
    def verify_oath(
        oath_event: Dict[str, Any],
        identity_tool: Any
    ) -> Tuple[bool, str]:
        """
        Verify that an oath is still valid (Constitution hash hasn't changed).
        
        Args:
            oath_event: The oath attestation from ledger
            identity_tool: IdentityTool instance for signature verification
            
        Returns:
            Tuple of (is_valid, reason_message)
        """
        try:
            current_hash = ConstitutionalOath.compute_constitution_hash()
            stored_hash = oath_event.get("constitution_hash")

            if current_hash != stored_hash:
                reason = (
                    f"Constitution has changed. "
                    f"Oath hash: {stored_hash[:16]}... "
                    f"Current hash: {current_hash[:16]}..."
                )
                logger.warning(f"⚠️  Oath verification failed: {reason}")
                return False, reason

            # Signature verification would happen here if we had identity_tool
            logger.info(f"✅ Oath verified for {oath_event.get('agent')}")
            return True, "Oath is valid and Constitution intact"

        except Exception as e:
            logger.error(f"❌ Error verifying oath: {e}")
            return False, f"Verification error: {str(e)}"
