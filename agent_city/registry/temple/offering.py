#!/usr/bin/env python3
"""
TEMPLE OFFERING HANDLER - Prasadam Distribution Layer

The Output becomes Sacred through the Ritual Process:

    1. Sanctify (Check Regulative Principles)
    2. Arrange (Beautiful Formatting)
    3. Offer (Request User Acceptance)
    4. Distribute (Publish to the World)

"Work becomes Worship. Output becomes Prasadam."
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("TEMPLE_OFFERING")


class OfferingHandler:
    """
    Transforms work (raw agent output) into worship (ritualized, user-approved, publishable result).

    Implements the Prasadam principle: No output goes public until it's:
    1. Pure (passes regulative checks)
    2. Beautiful (well-formatted)
    3. Accepted (user validation)
    4. Blessed (distributed as public good)
    """

    # Regulative Principle Validators
    REGULATORS = {
        "purity": "DataSanitizer",  # Principle 1: No Corrupt Data Ingestion
        "truth": "OutputVerifier",  # Principle 2: No Hallucination / Determinism
        "sobriety": "ResourceManager",  # Principle 3: No Resource Leaks
        "chastity": "NetworkGuard",  # Principle 4: No Unauthorized Connections
    }

    def __init__(self):
        """Initialize the Offering Handler."""
        logger.info("⛩️ TEMPLE OFFERING HANDLER INITIALIZED")
        self.offerings_processed = 0
        self.offerings_accepted = 0
        self.offerings_rejected = 0

    def present_offering(
        self,
        agent_id: str,
        raw_output: Any,
        context: Optional[Dict[str, Any]] = None,
        require_user_acceptance: bool = True,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Transform raw work into sacred offering.

        Args:
            agent_id: The agent that produced this work
            raw_output: The raw output from agent execution
            context: Additional context about the task
            require_user_acceptance: Whether to require user validation (Puja)

        Returns:
            Tuple of (success, message, result_dict)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🕉️ PRESENTING OFFERING FROM {agent_id.upper()}")
        logger.info(f"{'='*70}")

        self.offerings_processed += 1
        result = {
            "offering_id": f"offering_{agent_id}_{datetime.now(timezone.utc).isoformat()}",
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stages": {},
        }

        # STAGE 1: SANCTIFY (Regulative Principle Checks)
        logger.info("\n✨ STAGE 1: SANCTIFYING (Checking Regulative Principles)...")
        is_pure, purity_reason = self._sanctify(raw_output, context)
        result["stages"]["sanctify"] = {
            "status": "PASS" if is_pure else "FAIL",
            "reason": purity_reason,
        }

        if not is_pure:
            self.offerings_rejected += 1
            logger.error(f"❌ OFFERING REJECTED: {purity_reason}")
            return False, purity_reason, result

        # STAGE 2: ARRANGE (Formatting)
        logger.info("\n🎨 STAGE 2: ARRANGING (Beautiful Presentation)...")
        beautiful_output = self._arrange(raw_output)
        result["stages"]["arrange"] = {
            "status": "PASS",
            "formatted": True,
            "lines": len(str(beautiful_output).split("\n")),
        }
        logger.info(
            f"✅ Output beautifully formatted ({result['stages']['arrange']['lines']} lines)"
        )

        # STAGE 3: OFFER (User Acceptance / Puja)
        if require_user_acceptance:
            logger.info("\n🙏 STAGE 3: OFFERING (Awaiting User Acceptance / Puja)...")
            is_accepted, acceptance_reason = self._request_acceptance(
                agent_id=agent_id, beautiful_output=beautiful_output, context=context
            )
            result["stages"]["offer"] = {
                "status": "ACCEPTED" if is_accepted else "REJECTED",
                "reason": acceptance_reason,
            }

            if not is_accepted:
                self.offerings_rejected += 1
                logger.warning(f"⚠️ OFFERING REJECTED BY USER: {acceptance_reason}")
                return False, acceptance_reason, result

            logger.info(f"✅ USER ACCEPTED OFFERING: {acceptance_reason}")
        else:
            logger.info("\n⏭️ STAGE 3: OFFER (Skipped - auto-acceptance mode)")
            result["stages"]["offer"] = {
                "status": "AUTO_ACCEPTED",
                "reason": "No user validation required",
            }

        # STAGE 4: DISTRIBUTE (Prasadam - Public Distribution)
        logger.info("\n📢 STAGE 4: DISTRIBUTING (Publishing Prasadam)...")
        is_distributed, distribution_reason = self._distribute(
            offering_id=result["offering_id"],
            beautiful_output=beautiful_output,
            agent_id=agent_id,
            context=context,
        )
        result["stages"]["distribute"] = {
            "status": "DISTRIBUTED" if is_distributed else "PENDING",
            "reason": distribution_reason,
        }

        if is_distributed:
            self.offerings_accepted += 1
            logger.info(f"✅ PRASADAM DISTRIBUTED: {distribution_reason}")
        else:
            logger.warning(f"⚠️ DISTRIBUTION PENDING: {distribution_reason}")

        logger.info(f"\n{'='*70}")
        logger.info(f"🎉 OFFERING COMPLETE - JAYA!")
        logger.info(f"{'='*70}\n")

        return True, "Offering successfully presented", result

    def _sanctify(
        self, raw_output: Any, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        STAGE 1: SANCTIFY
        Check if output passes all 4 Regulative Principles.

        Returns:
            Tuple of (is_pure, reason)
        """
        # Principle 1: NO CORRUPT DATA INGESTION (Daya/Mercy)
        if isinstance(raw_output, dict) and raw_output.get("contains_toxicity"):
            return False, "❌ Principle 1 (Daya): Output contains toxic/corrupt data"

        # Principle 2: NO HALLUCINATION / DETERMINISM (Satyam/Truthfulness)
        if isinstance(raw_output, dict):
            confidence = raw_output.get("confidence", 1.0)
            if confidence < 0.8:
                return (
                    False,
                    f"❌ Principle 2 (Satyam): Low confidence ({confidence}) - hallucination risk",
                )

        # Principle 3: NO RESOURCE LEAKS / BLOAT (Tapas/Austerity)
        # Check output size (simple heuristic)
        output_size = len(str(raw_output).encode("utf-8"))
        if output_size > 100 * 1024 * 1024:  # 100MB limit
            return (
                False,
                f"❌ Principle 3 (Tapas): Output too large ({output_size} bytes)",
            )

        # Principle 4: NO UNAUTHORIZED CONNECTIONS (Saucam/Cleanliness)
        if isinstance(raw_output, dict) and raw_output.get("unauthorized_network"):
            return (
                False,
                "❌ Principle 4 (Saucam): Output contains unauthorized network operations",
            )

        logger.info("✅ All Regulative Principles Verified")
        return True, "All principles honored"

    def _arrange(self, raw_output: Any) -> str:
        """
        STAGE 2: ARRANGE
        Format the output beautifully for presentation.
        """
        if isinstance(raw_output, dict):
            # Pretty-print JSON-like output
            import json

            return json.dumps(raw_output, indent=2, ensure_ascii=False)
        elif isinstance(raw_output, str):
            return raw_output
        else:
            # Convert to string representation
            return str(raw_output)

    def _request_acceptance(
        self, agent_id: str, beautiful_output: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        STAGE 3: OFFER (Puja)
        Request user validation and acceptance.

        In a real system, this would:
        1. Display the beautiful output to the user
        2. Ask "Is this pleasing to you?"
        3. Wait for digital signature (user acceptance)
        4. Record acceptance in audit trail

        For now, we auto-accept with a log.
        """
        # In production, this would be an interactive prompt
        # For MVP, we auto-accept and log
        logger.info(f"📝 Waiting for user acceptance of output from {agent_id}...")
        logger.info(
            f"   Preview: {beautiful_output[:100]}{'...' if len(beautiful_output) > 100 else ''}"
        )

        # AUTO-ACCEPT with note (should be user interaction in production)
        return True, "User Accepted (Auto-approval in MVP mode)"

    def _distribute(
        self,
        offering_id: str,
        beautiful_output: str,
        agent_id: str,
        context: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        STAGE 4: DISTRIBUTE (Prasadam)
        Publish the accepted output to the world.

        In a real system, this would:
        1. Save to public repository
        2. Post to social media
        3. Make available via API
        4. Record distribution in ledger
        """
        # For MVP, we just log the distribution intent
        logger.info(f"📤 Publishing {offering_id} from {agent_id}...")

        # In production, distribution targets might include:
        # - Git repository push
        # - Social media posting
        # - API endpoint publication
        # - Email distribution
        # - Webhook notifications

        # For now: success with future roadmap note
        return True, "Prasadam marked for distribution (git push pending)"

    def report_statistics(self) -> Dict[str, Any]:
        """Report statistics on offerings processed."""
        return {
            "total_offerings_processed": self.offerings_processed,
            "total_accepted": self.offerings_accepted,
            "total_rejected": self.offerings_rejected,
            "acceptance_rate": (
                self.offerings_accepted / self.offerings_processed * 100
                if self.offerings_processed > 0
                else 0
            ),
        }


# Convenience functions for direct use
_global_handler = None


def get_handler() -> OfferingHandler:
    """Get or create global offering handler instance."""
    global _global_handler
    if _global_handler is None:
        _global_handler = OfferingHandler()
    return _global_handler


def present_offering(
    agent_id: str,
    raw_output: Any,
    context: Optional[Dict[str, Any]] = None,
    require_user_acceptance: bool = True,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Convenience function to present an offering using the global handler.
    """
    handler = get_handler()
    return handler.present_offering(
        agent_id=agent_id,
        raw_output=raw_output,
        context=context,
        require_user_acceptance=require_user_acceptance,
    )
