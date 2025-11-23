#!/usr/bin/env python3
"""
HERALD Brain: LLM-Powered Insight Generator

The Anti-Slop Engine. Generates technical, cynical, but constructive insights
about Agent Identity, Discovery, and the Steward Protocol - based on the actual spec.

Falls back gracefully if LLM is unavailable.
"""

import os
import random
import logging
from pathlib import Path

logger = logging.getLogger("HERALD_BRAIN")


class HeraldBrain:
    """
    The thinking engine for HERALD.
    Reads the Steward Protocol specification and generates insights via LLM.
    """

    def __init__(self):
        """Initialize the Brain with OpenRouter API credentials if available."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                # Use OpenRouter for maximum flexibility (Claude, Llama, etc.)
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                logger.info("✅ BRAIN ONLINE: LLM client initialized (OpenRouter)")
            except ImportError:
                logger.warning("⚠️ BRAIN: openai library not installed. Using fallback.")
                self.client = None
        else:
            logger.warning("⚠️ BRAIN: No OPENROUTER_API_KEY. Running in Lobotomy Mode (Fallback).")

    def _read_spec(self):
        """
        Reads the Steward Protocol specification for context.
        Returns first 5000 chars to keep token usage reasonable.
        """
        try:
            # Try multiple paths (we run from different contexts)
            paths = [
                Path(__file__).parent.parent.parent / "steward" / "SPECIFICATION.md",
                Path("steward/SPECIFICATION.md"),
                Path("../../steward/SPECIFICATION.md"),
                Path("README.md"),
            ]

            for p in paths:
                if p.exists():
                    spec_text = p.read_text()
                    logger.debug(f"📖 Loaded spec from {p}")
                    return spec_text[:5000]  # Truncate for token efficiency

            logger.warning("⚠️ SPEC NOT FOUND: Using generic fallback.")
            return (
                "Steward Protocol: A universal standard for agent identity, discovery, "
                "verification, and delegation. Layers include Agent Manifest, Registry, "
                "Protocol APIs, SDKs, and Applications."
            )
        except Exception as e:
            logger.error(f"❌ SPEC READ ERROR: {e}")
            return "Steward Protocol: Agent Identity System."

    def generate_insight(self):
        """
        Generate a technical, cynical, but constructive insight about Agent Identity.
        This is the core: anti-slop, value-first content.
        """
        if not self.client:
            logger.debug("🧠 Brain in fallback mode")
            return self._fallback_content()

        spec_text = self._read_spec()

        # THE PROMPT ENGINEERING MAGIC
        # This is where we kill AI slop. We're specific, cynical, and technical.
        prompt = (
            f"You are HERALD, the technical advocate for the Steward Protocol.\n"
            f"You are cynical about buzzwords but constructive about real problems.\n\n"
            f"PROTOCOL CONTEXT:\n{spec_text}\n\n"
            f"TASK:\n"
            f"Write ONE technical insight tweet (max 200 chars) about a specific problem "
            f"that Steward Protocol solves. Focus on engineering constraints, not marketing.\n\n"
            f"RULES:\n"
            f"- NO fluff: No 'revolutionary', 'game changer', 'disrupt'\n"
            f"- NO exaggeration: Be cynical but truthful\n"
            f"- FOCUS on the PROBLEM: e.g., 'Why do agents lack verifiable identity?'\n"
            f"- MENTION THE SOLUTION: One sentence about how Steward helps\n"
            f"- HASHTAGS ONLY: #AI #StewardProtocol (max 2)\n"
            f"- NO EMOJIS except optional one at start\n\n"
            f"TONE: A developer who's frustrated with bad architecture and wants to fix it."
        )

        try:
            logger.debug("🧠 Brain thinking...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-haiku:free",  # Fast, free tier
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
            )
            content = response.choices[0].message.content.strip()

            # Safety: Remove weird quotes LLMs sometimes add
            content = content.replace('"', '').replace("'", "'")

            # Validate content length (tweet max ~280, but we want room for retweet)
            if len(content) > 250:
                logger.warning(f"⚠️ Content too long ({len(content)} chars), truncating")
                content = content[:247] + "..."

            logger.info(f"✅ BRAIN INSIGHT GENERATED: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"❌ BRAIN EXCEPTION: {e}")
            logger.info("🧠 Falling back to hardcoded wisdom")
            return self._fallback_content()

    def _fallback_content(self):
        """
        Hardcoded anti-slop insights. Pure engineering truth.
        These fire if the LLM is down or misconfigured.
        """
        templates = [
            "Agents today use OAuth + Session Cookies for auth. That's built for humans. Steward adds cryptographic identity + capability delegation. #AI #StewardProtocol",
            "Why can't agents discover each other like Docker containers discover services? The gap between container orchestration and agent orchestration. That's what Steward fills. #AI",
            "Agent A calls Agent B. B says 'prove you're real.' A has: a string in an env var. Terrible. Steward: cryptographic identity + registry. #StewardProtocol #AI",
            "The missing layer in AI: verification. We have APIs, SDKs, frameworks. But agents can't verify each other's identity. Steward Protocol fixes that. #AI #BuildInPublic",
            "Docker solved container portability. Kubernetes solved orchestration. What solves agent interop + identity? Steward Protocol. #AI #StewardProtocol",
            "Current agent delegation: 'Hey agent, here's a task.' No contract, no capability proof, no audit trail. Steward adds all three. #AI #StewardProtocol",
        ]
        content = random.choice(templates)
        logger.info(f"✅ FALLBACK INSIGHT: {len(content)} chars")
        return content
