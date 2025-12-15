"""
PRATYAYA ANALYZER - Cognitive Self-Falsification via Red Team.

OPUS-077: The Immune System Reflex.

Runs Red Team attacks in dream state (TestKernel sandbox),
converts vulnerabilities into CRITICAL intents for remediation.

This is THE REFLEX - the missing piece that closes the loop:
    Attack → Detect → Intent → Action

Philosophy: "The system proves itself by trying to break itself."
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base import BaseAnalyzer

logger = logging.getLogger("MANAS.Pratyaya")


class PratyayaAnalyzer(BaseAnalyzer):
    """
    Self-falsification analyzer using Red Team orchestration.

    Periodically runs attack simulations in isolated TestKernel,
    then generates CRITICAL intents for any vulnerabilities found.

    Trigger: Set context["pratyaya_trigger"] = True

    The 52nd analyzer: Not fixing (50%) or creating (51%),
    but VERIFYING the system can defend itself.
    """

    @property
    def name(self) -> str:
        return "pratyaya"

    @property
    def description(self) -> str:
        return "Self-test via cognitive mutation (OPUS-077)"

    def analyze(self, context: Dict[str, Any]) -> List:
        """
        Run Red Team in Swapna (dream state), return vulnerability intents.

        Only runs if explicitly triggered via context flag.
        Uses existing test_red_team_attacks.py infrastructure.
        """
        from ..intent_generator import Intent, IntentPriority, IntentRisk

        # Only run if explicitly triggered (avoid running on every heartbeat)
        if not context.get("pratyaya_trigger"):
            return []

        logger.info("🧪 PRATYAYA: Entering Swapna (dream state)...")

        intents = []

        try:
            # Import Red Team runner (uses TestKernel.minimal() internally)
            from tests.hardening.test_red_team_attacks import run_red_team

            # Run all attacks in isolated sandbox
            results = run_red_team()

            vulnerabilities = results.get("vulnerabilities", 0)
            secure = results.get("secure", 0)
            attack_results = results.get("results", {})

            logger.info(f"🧪 PRATYAYA: Dream complete. Vulnerable: {vulnerabilities}, Secure: {secure}")

            # THE REFLEX: Convert vulnerabilities to CRITICAL intents
            for attack_name, result in attack_results.items():
                if result.exploited:
                    recommendation = result.details.get("recommendation", "Security patch required")

                    intent = Intent(
                        id=f"pratyaya_{attack_name.lower()}_{datetime.utcnow().strftime('%H%M%S')}",
                        intent_type="SECURITY_PATCH_NEEDED",
                        title=f"🚨 Vulnerability: {attack_name}",
                        description=result.message,
                        reasoning=recommendation,
                        priority=IntentPriority.CRITICAL,
                        risk=IntentRisk.HIGH,
                        params={
                            "attack_name": attack_name,
                            "evidence": result.message,
                            "fix": recommendation,
                            "dream_timestamp": datetime.utcnow().isoformat(),
                        },
                        auto_executable=False,  # Security fixes need human review
                        expires_at=(datetime.utcnow() + timedelta(days=7)).isoformat(),
                    )
                    intents.append(intent)
                    logger.warning(f"🚨 VULNERABILITY DETECTED: {attack_name}")

            # If all attacks blocked, log success (no intent needed)
            if vulnerabilities == 0:
                logger.info("✅ PRATYAYA: All attacks blocked. System is secure.")

        except ImportError as e:
            logger.error(f"PRATYAYA: Cannot import Red Team suite: {e}")
        except Exception as e:
            logger.error(f"PRATYAYA: Dream state error: {e}")

        return intents
