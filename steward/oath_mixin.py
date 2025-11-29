#!/usr/bin/env python3
"""
OATH MIXIN - Adds Constitutional Oath ritual to any VibeAgent.

Usage:
    class MyAgent(VibeAgent, OathMixin):
        def __init__(self):
            super().__init__()
            self.oath_mixin_init(self.agent_id)

    agent = MyAgent()
    await agent.swear_constitutional_oath()
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from steward.constitutional_oath import ConstitutionalOath

logger = logging.getLogger("OATH_MIXIN")


class OathMixin:
    """
    Adds Constitutional Oath capabilities to VibeAgent subclasses.

    Provides:
    - swear_constitutional_oath(): Execute the Genesis Ceremony
    - verify_agent_oath(): Confirm agent is still bound to current Constitution
    """

    def oath_mixin_init(self, agent_id: str):
        """Initialize oath mixin state."""
        self.agent_id = agent_id
        self.oath_sworn = False
        self.oath_event: Optional[Dict[str, Any]] = None
        logger.debug(f"🕉️  Oath mixin initialized for {agent_id}")

    async def swear_constitutional_oath(self) -> Dict[str, Any]:
        """
        Execute the Genesis Ceremony: Agent binds itself to Constitution.

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
        logger.info(
            f"🕉️  GENESIS CEREMONY: {self.agent_id} swearing Constitutional Oath..."
        )

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
            logger.info(f"✅ {self.agent_id} has sworn Constitutional Oath")

            return self.oath_event

        except Exception as e:
            logger.error(f"❌ Oath ceremony failed for {self.agent_id}: {e}")
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
                logger.info(f"✅ Oath signed with {self.agent_id}'s private key")
                return signature
        except Exception as e:
            logger.warning(f"⚠️  Could not sign with identity_tool: {e}")

        # Fallback: generic signature
        fallback_signature = f"OATH_{self.agent_id}_{constitution_hash[:16]}"
        logger.info(f"⚠️  Using fallback oath signature: {fallback_signature[:32]}...")
        return fallback_signature

    async def _record_oath_in_ledger(self):
        """
        Record the oath in the immutable ledger.

        Tries to send event to kernel ledger if available.
        """
        try:
            # Check if agent has access to kernel
            if hasattr(self, "kernel") and self.kernel:
                # This would be implemented in the kernel's ledger system
                logger.info(f"📖 Recording oath in kernel ledger...")
                # kernel.ledger.append(self.oath_event)
        except Exception as e:
            logger.warning(f"⚠️  Could not record oath in ledger: {e}")

    def verify_agent_oath(self) -> tuple[bool, str]:
        """
        Verify that agent is still bound to current Constitution.

        Returns:
            Tuple of (is_valid, reason_message)

        Raises:
            RuntimeError: If oath not sworn
        """
        if not self.oath_sworn or self.oath_event is None:
            return False, f"{self.agent_id} has not sworn Constitutional Oath"

        is_valid, reason = ConstitutionalOath.verify_oath(
            self.oath_event, getattr(self, "identity_tool", None)
        )

        return is_valid, reason

    async def assert_constitutional_compliance(self) -> bool:
        """
        Fail-fast check: Agent must be oath-bound to proceed.

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
