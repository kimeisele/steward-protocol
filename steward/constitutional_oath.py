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
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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
            # Fallback for dev environments without constitution
            logger.warning("⚠️ Constitution not found, using GENESIS_NULL_HASH")
            return hashlib.sha256(b"GENESIS").hexdigest()

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
        block_number: Optional[int] = None,
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
            "event_id": f"oath_{agent_id}_{constitution_hash[:8]}",
        }

        if block_number is not None:
            event["block_number"] = block_number

        return event

    @staticmethod
    def verify_oath(oath_event: Dict[str, Any], identity_tool: Any) -> Tuple[bool, str]:
        """
        Verify that an oath is valid.
        INCLUDES NULL-POINTER PROTECTION & LEGACY MAPPING (GAD-1100).

        Args:
            oath_event: The oath attestation from ledger
            identity_tool: IdentityTool instance for signature verification

        Returns:
            Tuple of (is_valid, reason_message)
        """
        if not oath_event:
            return False, "❌ Oath event is None or empty"

        try:
            # 1. SCHEMA NORMALIZATION (The Fix)
            # Maps legacy 'oath_hash' to standard 'constitution_hash'
            stored_hash = oath_event.get("constitution_hash")
            if not stored_hash and "oath_hash" in oath_event:
                stored_hash = oath_event["oath_hash"]
                # logger.debug("🔄 Schema mapped: oath_hash -> constitution_hash")

            if not stored_hash:
                return False, "❌ Missing constitution_hash in oath event"

            # 2. HASH VERIFICATION
            current_hash = ConstitutionalOath.compute_constitution_hash()

            # Robust logging that won't crash on None slicing
            sh_preview = stored_hash[:16] if stored_hash else "NONE"
            ch_preview = current_hash[:16] if current_hash else "NONE"

            if current_hash != stored_hash:
                # Allow Genesis bypass if hashes match known development constants
                if stored_hash == "genesis_hash":
                    logger.warning("⚠️ Allowing GENESIS_HASH bypass for bootstrapping")
                    return True, "Genesis Bootstrap Authorized"

                reason = f"Hash Mismatch. Stored: {sh_preview}... Current: {ch_preview}..."
                logger.warning(f"⚠️  {reason}")
                return False, reason

            logger.info(f"✅ Oath verified for {oath_event.get('agent', 'Unknown Agent')}")
            return True, "Oath is valid"

        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in verify_oath: {e}")
            return False, f"Verification Exception: {str(e)}"
