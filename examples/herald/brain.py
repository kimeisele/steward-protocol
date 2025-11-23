#!/usr/bin/env python3
"""
HERALD Brain: LLM-Powered Insight Generator

The Anti-Slop Engine. Generates technical, cynical, but constructive insights
about Agent Identity, Discovery, and the Steward Protocol - based on the actual spec.

Falls back gracefully if LLM is unavailable.
"""

import os
import json
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

    def generate_reddit_deepdive(self, subreddit="r/LocalLLaMA"):
        """
        ANTI-SLOP ENGINE FOR REDDIT: Technical Deep Dive Generator

        Based on WHY_DOWNVOTED.md rules:
        - Show struggle (what broke)
        - Technical details (pseudocode, logic)
        - Ask for feedback (genuine questions)
        - NO MARKETING (no buzzwords, no selling)

        This produces long-form, technical content for technical subreddits.
        Returns: dict with 'title' and 'body' keys (ready for Reddit)
        """
        if not self.client:
            logger.warning("⚠️ REDDIT: No LLM client. Fallback content unavailable for Reddit.")
            return None

        spec_text = self._read_spec()

        # Adapt to subreddit culture (from HERALD_AGENT_SPEC.md)
        culture_prompt = ""
        if subreddit == "r/LocalLLaMA":
            culture_prompt = "Audience: Pragmatic engineers obsessed with local LLMs. Wants benchmarks, code, technical depth. HATES marketing fluff."
        elif subreddit == "r/singularity":
            culture_prompt = "Audience: Visionary thinkers skeptical of hype. Wants implications, future thinking, hard technical questions."
        elif subreddit == "r/MachineLearning":
            culture_prompt = "Audience: ML researchers and practitioners. Wants rigorous methodology, results, reproducibility. Zero tolerance for unsubstantiated claims."
        else:
            culture_prompt = "Audience: Hardcore developers. EXTREME skepticism of marketing. Value: Technical depth, honesty, struggle."

        prompt = (
            f"You are a senior engineer writing a Reddit post about Agent Identity & Verification.\n"
            f"Target Subreddit: {subreddit}\n"
            f"Context: {culture_prompt}\n\n"
            f"Technical Context: {spec_text[:2000]}\n\n"
            f"TASK: Write a Reddit post (title + body) structured as a 'Lessons Learned' technical deep dive.\n\n"
            f"STRICT RULES (from WHY_DOWNVOTED.md - these are GOLDEN):\n"
            f"1. **DO NOT SELL**. Zero marketing speak ('revolutionary', 'game changer', 'the future'). This will get roasted.\n"
            f"2. **Structure**: 'I tried X, it failed because Y. Then I tried Z, hit these problems. Here's how I solved it.'\n"
            f"3. **Show Struggle**: Be honest about failures. Engineers respect that.\n"
            f"4. **Include Technical Detail**: Pseudocode, architecture diagrams (in ASCII), decision trees. Not just concepts.\n"
            f"5. **Genuine Question**: End with a specific technical question for the community (not a call-to-action).\n"
            f"6. **Mention Steward Protocol** ONCE ONLY and CASUALLY: 'I called it Steward Protocol' or 'The solution I've been building is called Steward'.\n"
            f"7. **Length**: 500-1500 chars is good for Reddit (longer than Twitter, shorter than essays).\n"
            f"8. **Tone**: Cynical-but-helpful. Like 'I got burned by this, don't be stupid like I was.'\n"
            f"9. **Format Output as JSON**: {{'title': '...', 'body': '...'}}\n"
            f"10. **Title rules**: 15-80 chars. Start with context: '[Discussion]', '[Help]', or just start with the problem.\n\n"
            f"EXAMPLE STRUCTURE (good):\n"
            f"Title: '[Discussion] Agent identity verification without a central registry - feasible?'\n"
            f"Body: 'I spent 3 months building a system where agents could prove identity to each other...'\n\n"
            f"EXAMPLE STRUCTURE (bad, will be downvoted):\n"
            f"Title: 'Revolutionary AI Framework - You Won't Believe What Happens Next'\n"
            f"Body: 'Our amazing solution solves all your problems. Check it out!'\n\n"
        )

        try:
            logger.debug("🧠 REDDIT BRAIN: Thinking technical deep dive...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",  # Smarter model for technical depth
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            content_str = response.choices[0].message.content.strip()
            result = json.loads(content_str)

            # Validate structure
            if "title" in result and "body" in result:
                logger.info(f"✅ REDDIT POST GENERATED: '{result['title']}' ({len(result['body'])} chars)")
                return result
            else:
                logger.error(f"❌ REDDIT BRAIN: Invalid JSON structure from LLM")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"❌ REDDIT BRAIN: JSON Parse Error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ REDDIT BRAIN ERROR: {e}")
            return None
