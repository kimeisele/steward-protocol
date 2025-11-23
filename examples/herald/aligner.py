#!/usr/bin/env python3
"""
HERALD Governance Module: The Vibe Aligner (v1.4)

The Conscience of the Agent.

The VIBE ALIGNER is a three-layer governance system:
1. HARD CONSTRAINTS: Banned words (regex-based, instant rejection)
2. SOFT CONSTRAINTS: LLM judgment on hype, value, and platform fit
3. ADAPTATION: Learns from swarm feedback (downvotes, criticism, etc.)

Philosophy:
- YAML Rules > LLM intuition (rules are deterministic, LLMs hallucinate)
- Fail-safe: If governance can't decide, pass the content (but log it)
- Transparency: Every rejection is logged with reasoning
"""

import os
import yaml
import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("HERALD_ALIGNER")


class VibeAligner:
    """
    The Governance Module.
    Ensures every HERALD output aligns with anti-slop philosophy.
    """

    def __init__(self, policy_path: Optional[str] = None):
        """
        Initialize the Aligner with governance policy.

        Args:
            policy_path: Path to governance.yaml (defaults to examples/herald/governance.yaml)
        """
        if policy_path is None:
            policy_path = Path(__file__).parent / "governance.yaml"
        else:
            policy_path = Path(policy_path)

        self.policy_path = policy_path
        self.policy = self._load_policy()
        self.rejection_log = []  # Track all rejections for learning

        if self.policy:
            logger.info("✅ VIBE ALIGNER: Governance policy loaded")
        else:
            logger.warning("⚠️ VIBE ALIGNER: No governance policy found (running without guardrails)")

    def _load_policy(self) -> Optional[Dict[str, Any]]:
        """Load governance.yaml from disk."""
        if self.policy_path.exists():
            try:
                with open(self.policy_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"❌ ALIGNER: Failed to load policy: {e}")
                return None
        return None

    def align(self, content: str, platform: str = "twitter", client=None) -> Optional[str]:
        """
        The Alignment Gate.
        Checks content against governance rules.

        Args:
            content: The content to validate
            platform: "twitter" or "reddit" (affects constraints)
            client: OpenRouter LLM client for soft checks (optional)

        Returns:
            str: The approved content, or None if rejected
        """
        if not self.policy or not content:
            return content

        logger.debug(f"🔍 ALIGNER: Checking {platform} content ({len(content)} chars)")

        # --- LAYER 1: HARD CONSTRAINTS (Banned Phrases) ---
        rejection_reason = self._check_hard_constraints(content)
        if rejection_reason:
            logger.warning(f"🛡️ ALIGNER BLOCKED (Hard): {rejection_reason}")
            self.rejection_log.append({
                "type": "hard_constraint",
                "reason": rejection_reason,
                "content_preview": content[:100]
            })
            return None

        # --- LAYER 2: PLATFORM-SPECIFIC CONSTRAINTS ---
        rejection_reason = self._check_platform_constraints(content, platform)
        if rejection_reason:
            logger.warning(f"🛡️ ALIGNER BLOCKED (Platform): {rejection_reason}")
            self.rejection_log.append({
                "type": "platform_constraint",
                "reason": rejection_reason,
                "platform": platform,
                "content_preview": content[:100]
            })
            return None

        # --- LAYER 3: SOFT CONSTRAINTS (LLM Judgment) ---
        if client:
            rejection_reason = self._check_soft_constraints(content, platform, client)
            if rejection_reason:
                logger.warning(f"🛡️ ALIGNER BLOCKED (Soft): {rejection_reason}")
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
        Fast, cheap, deterministic. No hallucinations.
        """
        banned = self.policy.get('constraints', {}).get('banned_phrases', [])

        for phrase in banned:
            # Case-insensitive, handle emoji/special chars
            if phrase.lower() in content.lower():
                return f"Found banned phrase: '{phrase}'"

            # Also check for variations (e.g., "Game Changer" vs "game changer")
            if re.search(re.escape(phrase), content, re.IGNORECASE):
                return f"Found banned phrase (regex): '{phrase}'"

        return None

    def _check_platform_constraints(self, content: str, platform: str) -> Optional[str]:
        """
        LAYER 2: Platform-Specific Rules.
        Twitter has different rules than Reddit.
        """
        rules = self.policy.get('constraints', {}).get('platform_rules', {}).get(platform, {})

        # Check length constraints
        if 'max_length' in rules:
            if len(content) > rules['max_length']:
                return f"Content too long for {platform}: {len(content)} > {rules['max_length']} chars"

        if 'min_length' in rules:
            if len(content) < rules['min_length']:
                return f"Content too short for {platform}: {len(content)} < {rules['min_length']} chars"

        # Check for forbidden emojis
        forbidden_emojis = rules.get('forbidden_emojis', [])
        for emoji in forbidden_emojis:
            if emoji in content:
                return f"Content contains forbidden emoji: {emoji}"

        # Check for forbidden clichés
        forbidden_clichés = rules.get('forbidden_clichés', [])
        for cliché in forbidden_clichés:
            if cliché.lower() in content.lower():
                return f"Content contains forbidden cliché: '{cliché}'"

        return None

    def _check_soft_constraints(self, content: str, platform: str, client) -> Optional[str]:
        """
        LAYER 3: LLM Judgment.
        Ask the model: Is this hype? Is this valuable? Is this honest?

        This is expensive, so only run if hard + platform checks pass.
        """
        if not client:
            logger.debug("⚠️ ALIGNER: No LLM available for soft checks")
            return None

        directives = self.policy.get('prime_directives', [])
        directives_text = "\n".join(f"- {d}" for d in directives)

        prompt = (
            f"You are the VIBE ALIGNER, the Ethics Committee for HERALD Agent.\n\n"
            f"GOVERNANCE RULES:\n{directives_text}\n\n"
            f"CONTENT TO JUDGE:\n\"{content}\"\n\n"
            f"TASK:\n"
            f"1. Does this violate any rule above? (Be strict on 'shill' and 'hype')\n"
            f"2. Is the content honest? Does it admit failure or limitations?\n"
            f"3. Is this technical substance or marketing fluff?\n\n"
            f"RESPOND WITH ONLY:\n"
            f"- 'PASS' if content is clean\n"
            f"- 'BLOCK: <reason>' if content violates governance\n"
            f"\nBe harsh. The Agent depends on you."
        )

        try:
            logger.debug("🧠 ALIGNER: Running LLM judgment (soft constraints)...")
            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",  # Fast and cheap for gatekeeper duty
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.5  # Deterministic, not creative
            )

            verdict = response.choices[0].message.content.strip()

            if "BLOCK" in verdict:
                # Extract the reason
                reason = verdict.split("BLOCK:")[-1].strip() if "BLOCK:" in verdict else "Policy violation"
                return reason

            logger.debug(f"✅ LLM Verdict: {verdict}")
            return None  # Approved

        except Exception as e:
            logger.error(f"❌ ALIGNER LLM ERROR: {e}")
            # Fail open: If LLM fails, allow the content (but log it)
            logger.info("⚠️ ALIGNER: LLM unavailable, passing content (logged)")
            return None

    def get_rejection_log(self) -> list:
        """Return all rejections for debugging and learning."""
        return self.rejection_log

    def save_rejection_log(self, filepath: str = "aligner_rejections.json"):
        """Save rejection log to disk for analysis."""
        with open(filepath, 'w') as f:
            json.dump(self.rejection_log, f, indent=2)
        logger.info(f"📊 ALIGNER: Rejection log saved to {filepath}")
