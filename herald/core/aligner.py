"""
HERALD Aligner: The Governance Module
Ensures content aligns with anti-slop philosophy and safety constraints.
Kernel-integrated (configured via system.yaml).

Three-layer enforcement:
1. HARD CONSTRAINTS: Banned phrases (fast, deterministic)
2. PLATFORM CONSTRAINTS: Platform-specific rules
3. SOFT CONSTRAINTS: LLM judgment (optional, slow)
"""

import logging
import re
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger("HERALD_ALIGNER")


class VibeAligner:
    """
    Content governance module.
    Ensures HERALD outputs are anti-slop and policy-compliant.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize aligner from system.yaml config.

        Args:
            config: alignment section from system.yaml
        """
        self.config = config
        self.rejection_log = []

        logger.info("✅ VIBE ALIGNER: Governance module loaded")

    def align(self, content: str, platform: str = "twitter", client: Optional[OpenAI] = None) -> Optional[str]:
        """
        The Alignment Gate.
        Checks content against governance rules.

        Args:
            content: Content to validate
            platform: "twitter", "reddit", etc.
            client: Optional LLM client for soft constraints

        Returns:
            str: Approved content, or None if rejected
        """
        if not content:
            return content

        logger.debug(f"🔍 ALIGNER: Checking {platform} content ({len(content)} chars)")

        # LAYER 1: Hard constraints (banned phrases)
        rejection_reason = self._check_hard_constraints(content)
        if rejection_reason:
            logger.warning(f"🛡️  ALIGNER BLOCKED (Hard): {rejection_reason}")
            self.rejection_log.append({
                "type": "hard_constraint",
                "reason": rejection_reason,
                "content_preview": content[:100]
            })
            return None

        # LAYER 2: Platform constraints
        rejection_reason = self._check_platform_constraints(content, platform)
        if rejection_reason:
            logger.warning(f"🛡️  ALIGNER BLOCKED (Platform): {rejection_reason}")
            self.rejection_log.append({
                "type": "platform_constraint",
                "reason": rejection_reason,
                "platform": platform,
                "content_preview": content[:100]
            })
            return None

        # LAYER 3: Soft constraints (LLM judgment - optional)
        if client:
            rejection_reason = self._check_soft_constraints(content, platform, client)
            if rejection_reason:
                logger.warning(f"🛡️  ALIGNER BLOCKED (Soft): {rejection_reason}")
                self.rejection_log.append({
                    "type": "soft_constraint",
                    "reason": rejection_reason,
                    "platform": platform,
                    "content_preview": content[:100]
                })
                return None

        logger.info("✅ ALIGNER APPROVED: Content passes all governance checks")
        return content

    def _check_hard_constraints(self, content: str) -> Optional[str]:
        """
        LAYER 1: Banned Phrases Detection.
        Fast, deterministic, no hallucinations.
        """
        banned_phrases = self.config.get("banned_phrases", [])

        for phrase in banned_phrases:
            # Case-insensitive check
            if phrase.lower() in content.lower():
                return f"Found banned phrase: '{phrase}'"

            # Regex check
            if re.search(re.escape(phrase), content, re.IGNORECASE):
                return f"Found banned phrase (regex): '{phrase}'"

        return None

    def _check_platform_constraints(self, content: str, platform: str) -> Optional[str]:
        """
        LAYER 2: Platform-Specific Rules.
        Different platforms have different constraints.
        """
        filters = self.config.get("content_filters", [])

        for filter_rule in filters:
            filter_type = filter_rule.get("type")

            if filter_type == "length":
                min_chars = filter_rule.get("min_chars", 0)
                max_chars = filter_rule.get("max_chars", 10000)

                if len(content) < min_chars:
                    return f"Content too short: {len(content)} < {min_chars} chars"

                if len(content) > max_chars:
                    return f"Content too long: {len(content)} > {max_chars} chars"

        return None

    def _check_soft_constraints(self, content: str, platform: str, client: OpenAI) -> Optional[str]:
        """
        LAYER 3: LLM Judgment.
        Ask the model: Is this hype? Is this valuable? Is this honest?
        """
        if not client:
            logger.debug("⚠️  ALIGNER: No LLM available for soft checks")
            return None

        prompt = (
            f"You are the VIBE ALIGNER, the Governance Committee for HERALD Agent.\n\n"
            f"RULES:\n"
            f"1. No marketing hype ('revolutionary', 'game-changer', 'moonshot', etc.)\n"
            f"2. No shill behavior (promoting without technical substance)\n"
            f"3. Technical truth > marketing narrative\n"
            f"4. Admitting limitations > fake confidence\n\n"
            f"CONTENT TO JUDGE:\n\"{content}\"\n\n"
            f"RESPOND WITH ONLY:\n"
            f"- 'PASS' if content is clean\n"
            f"- 'BLOCK: <reason>' if content violates governance\n\n"
            f"Be harsh. The Agent depends on you."
        )

        try:
            logger.debug("🧠 ALIGNER: Running LLM judgment (soft constraints)...")
            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.5
            )

            verdict = response.choices[0].message.content.strip()

            if "BLOCK" in verdict:
                reason = verdict.split("BLOCK:")[-1].strip() if "BLOCK:" in verdict else "Policy violation"
                return reason

            logger.debug(f"✅ LLM Verdict: {verdict}")
            return None

        except Exception as e:
            logger.error(f"❌ ALIGNER LLM ERROR: {e}")
            logger.info("⚠️  ALIGNER: LLM unavailable, passing content (logged)")
            return None

    def get_rejection_log(self) -> list:
        """Get all rejections for debugging."""
        return self.rejection_log
