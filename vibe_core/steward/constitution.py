#!/usr/bin/env python3
"""
CONSTITUTIONAL OATH - Cryptographic Attestation of Governance Binding.

When an agent boots, it must:
1. Read the Constitution
2. Hash it (SHA-256)
3. Sign the hash with its identity
4. Record the oath in the immutable ledger

This is the "Genesis Ceremony" - the moment an agent binds itself to Truth.

LOCATION: vibe_core/steward/constitution.py
ORIGINAL: steward/constitutional_oath.py (kept for backwards compatibility)
"""

import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("STEWARD.CONSTITUTION")


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
            FileNotFoundError: If CONSTITUTION.md not found (uses fallback)
        """
        if not ConstitutionalOath.CONSTITUTION_PATH.exists():
            # Fallback for dev environments without constitution
            logger.warning("Constitution not found, using GENESIS_NULL_HASH")
            return hashlib.sha256(b"GENESIS").hexdigest()

        with open(ConstitutionalOath.CONSTITUTION_PATH, "rb") as f:
            constitution_bytes = f.read()
            constitution_hash = hashlib.sha256(constitution_bytes).hexdigest()

        logger.debug(f"Constitution hash computed: {constitution_hash[:16]}...")
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
    def verify_oath(oath_event: Dict[str, Any], identity_tool: Any = None) -> Tuple[bool, str]:
        """
        Verify that an oath is valid.
        INCLUDES NULL-POINTER PROTECTION & LEGACY MAPPING.

        Args:
            oath_event: The oath attestation from ledger
            identity_tool: IdentityTool instance for signature verification (optional)

        Returns:
            Tuple of (is_valid, reason_message)
        """
        if not oath_event:
            return False, "Oath event is None or empty"

        try:
            # 1. SCHEMA NORMALIZATION
            # Maps legacy 'oath_hash' to standard 'constitution_hash'
            stored_hash = oath_event.get("constitution_hash")
            if not stored_hash and "oath_hash" in oath_event:
                stored_hash = oath_event["oath_hash"]

            if not stored_hash:
                return False, "Missing constitution_hash in oath event"

            # 2. HASH VERIFICATION
            current_hash = ConstitutionalOath.compute_constitution_hash()

            # Robust logging that won't crash on None slicing
            sh_preview = stored_hash[:16] if stored_hash else "NONE"
            ch_preview = current_hash[:16] if current_hash else "NONE"

            if current_hash != stored_hash:
                # [VAJRA FIX]
                # Truth is absolute. No Dev Mode exceptions for the Constitution.
                reason = f"Hash Mismatch. Stored: {sh_preview}... Current: {ch_preview}..."
                logger.warning(reason)
                return False, reason

            # 3. SIGNATURE VERIFICATION (if identity_tool provided)
            if identity_tool and hasattr(identity_tool, "verify_signature"):
                signature = oath_event.get("signature_full") or oath_event.get("signature")
                if signature:
                    message = stored_hash
                    try:
                        is_valid = identity_tool.verify_signature(message, signature)
                        if not is_valid:
                            logger.error("Signature verification failed for oath")
                            return False, "Signature verification failed"
                        logger.info("Signature verified for oath")
                    except Exception as sig_err:
                        logger.error(f"Signature verification error: {sig_err}")
                        return False, f"Signature verification error: {str(sig_err)}"
                else:
                    logger.warning("No signature found in oath event (continuing anyway)")

            logger.debug(f"Oath verified for {oath_event.get('agent', 'Unknown Agent')}")
            return True, "Oath is valid"

        except Exception as e:
            logger.error(f"CRITICAL ERROR in verify_oath: {e}")
            return False, f"Verification Exception: {str(e)}"
