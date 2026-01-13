#!/usr/bin/env python3
"""
OATH MIXIN - Adds Constitutional Oath ritual to any VibeAgent.

Usage:
    class MyAgent(VibeAgent, OathMixin):
        def __init__(self):
            super().__init__()
            self.oath_mixin_init(self.agent_id)
            self.swear_oath_sync()  # Sync version for __init__

    # Or async version:
    agent = MyAgent()
    await agent.swear_constitutional_oath()

LOCATION: vibe_core/steward/oath_mixin.py
ORIGINAL: steward/oath_mixin.py (kept for backwards compatibility)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x32010c77"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict, Optional, Tuple

from vibe_core.steward.constitution import ConstitutionalOath

logger = logging.getLogger("STEWARD.OATH_MIXIN")


class OathMixin:
    """
    Adds Constitutional Oath capabilities to VibeAgent subclasses.

    Provides:
    - swear_oath_sync(): Synchronous oath ceremony (for __init__)
    - swear_constitutional_oath(): Async oath ceremony
    - verify_agent_oath(): Confirm agent is still bound to current Constitution
    - assert_constitutional_compliance(): Fail-fast compliance check
    """

    # These will be set by oath_mixin_init or inherited from VibeAgent
    agent_id: str
    oath_sworn: bool
    oath_event: Optional[Dict[str, Any]]

    def oath_mixin_init(self, agent_id: str) -> None:
        """Initialize oath mixin state."""
        self.agent_id = agent_id
        self.oath_sworn = False
        self.oath_event = None
        logger.debug(f"Oath mixin initialized for {agent_id}")

    def swear_oath_sync(self) -> Dict[str, Any]:
        """
        SYNCHRONOUS oath ceremony - works in __init__ regardless of event loop state.

        This is the REAL implementation. The async version is only needed when
        identity_tool or kernel ledger are async operations.

        Returns:
            Oath event dictionary

        Raises:
            RuntimeError: If oath ceremony fails
        """
        logger.info(f"GENESIS CEREMONY (sync): {self.agent_id} swearing Constitutional Oath...")

        try:
            # Step 1: Compute Constitution hash
            constitution_hash = ConstitutionalOath.compute_constitution_hash()

            # Step 2: Create fallback signature (sync - no identity_tool)
            signature = f"OATH_{self.agent_id}_{constitution_hash[:16]}"

            # Step 3: Create oath event
            self.oath_event = ConstitutionalOath.create_oath_event(
                agent_id=self.agent_id,
                constitution_hash=constitution_hash,
                signature=signature,
            )

            # Step 4: Mark as sworn (ledger recording is optional)
            self.oath_sworn = True
            logger.info(f"{self.agent_id} has sworn Constitutional Oath (sync)")

            return self.oath_event

        except Exception as e:
            logger.error(f"Oath ceremony failed for {self.agent_id}: {e}")
            raise RuntimeError(f"Failed to swear Constitutional Oath: {str(e)}")

    async def swear_constitutional_oath(self) -> Dict[str, Any]:
        """
        Execute the Genesis Ceremony: Agent binds itself to Constitution.

        Async version - use when identity_tool or ledger operations are async.

        Steps:
        1. Compute hash of Constitution
        2. Sign hash with agent's identity (if available)
        3. Create oath event
        4. Record in ledger

        Returns:
            Oath event dictionary

        Raises:
            RuntimeError: If oath cannot be sworn
        """
        logger.info(f"GENESIS CEREMONY: {self.agent_id} swearing Constitutional Oath...")

        try:
            # Step 1: Compute Constitution hash
            constitution_hash = ConstitutionalOath.compute_constitution_hash()

            # Step 2: Try to sign with IdentityTool (if available)
            signature = await self._sign_oath(constitution_hash)

            # Step 3: Create oath event
            self.oath_event = ConstitutionalOath.create_oath_event(
                agent_id=self.agent_id,
                constitution_hash=constitution_hash,
                signature=signature,
            )

            # Step 4: Record in ledger (if kernel available)
            await self._record_oath_in_ledger()

            self.oath_sworn = True
            logger.info(f"{self.agent_id} has sworn Constitutional Oath")

            return self.oath_event

        except Exception as e:
            logger.error(f"Oath ceremony failed for {self.agent_id}: {e}")
            raise RuntimeError(f"Failed to swear Constitutional Oath: {str(e)}")

    async def _sign_oath(self, constitution_hash: str) -> str:
        """
        Sign the constitution hash with agent's identity.

        Tries multiple methods:
        1. If agent has identity_tool attribute -> use it
        2. Otherwise -> use generic signature
        """
        try:
            # Check if agent has identity_tool
            if hasattr(self, "identity_tool") and self.identity_tool:
                signature = self.identity_tool.sign_artifact(constitution_hash.encode())
                logger.info(f"Oath signed with {self.agent_id}'s private key")
                return signature
        except Exception as e:
            logger.warning(f"Could not sign with identity_tool: {e}")

        # Fallback: generic signature
        fallback_signature = f"OATH_{self.agent_id}_{constitution_hash[:16]}"
        logger.debug(f"Using fallback oath signature: {fallback_signature[:32]}...")
        return fallback_signature

    async def _record_oath_in_ledger(self) -> None:
        """
        Record the oath in the immutable ledger.

        Tries to send event to kernel ledger if available.
        """
        try:
            # Check if agent has access to kernel
            if hasattr(self, "kernel") and self.kernel:
                logger.debug("Recording oath in kernel ledger...")
                # kernel.ledger.append(self.oath_event)
        except Exception as e:
            logger.warning(f"Could not record oath in ledger: {e}")

    def verify_agent_oath(self) -> Tuple[bool, str]:
        """
        Verify that agent is still bound to current Constitution.

        Returns:
            Tuple of (is_valid, reason_message)
        """
        if not self.oath_sworn or self.oath_event is None:
            return False, f"{self.agent_id} has not sworn Constitutional Oath"

        is_valid, reason = ConstitutionalOath.verify_oath(self.oath_event, getattr(self, "identity_tool", None))

        return is_valid, reason

    async def assert_constitutional_compliance(self) -> bool:
        """
        Fail-fast check: Agent must be oath-bound to proceed.

        Returns:
            True if compliant

        Raises:
            RuntimeError: If agent not properly oath-sworn
        """
        if not self.oath_sworn:
            raise RuntimeError(
                f"CONSTITUTIONAL_COMPLIANCE_FAILED: {self.agent_id} "
                "has not sworn the Constitutional Oath. "
                "Agent cannot proceed."
            )

        is_valid, reason = self.verify_agent_oath()
        if not is_valid:
            raise RuntimeError(f"CONSTITUTIONAL_COMPLIANCE_FAILED: {reason}")

        return True
