#!/usr/bin/env python3
"""
HERALD Brain: Modular LLM-Powered Content Engine

Enterprise-Grade Architecture:
- ResearchEngine: Market intelligence via Tavily (The Eyes)
- HeraldBrain: Content orchestrator with dual-mode generation
  - Twitter Mode: Real-time, snappy insights (150-250 chars)
  - Reddit Mode: Deep technical analysis (800-2000 chars)

Anti-Slop Philosophy: Every output must provide genuine technical value.
No marketing fluff. No buzzwords. Pure engineering truth.
"""

import os
import json
import random
import logging
from pathlib import Path
from openai import OpenAI
from tavily import TavilyClient

logger = logging.getLogger("HERALD_BRAIN")

# --- MODULE 1: THE EYES (Research) ---
class ResearchEngine:
    """
    Market Intelligence Engine powered by Tavily.
    Scans for AI agent failures, security incidents, and technical trends.
    """

    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("✅ RESEARCH ENGINE: Tavily initialized")
        else:
            logger.warning("⚠️ RESEARCH: No TAVILY_API_KEY found. Running blind.")

    def scan_market(self):
        """
        Searches for recent problems that Steward Protocol solves.
        Returns: String summary or None if unavailable.
        """
        if not self.client:
            return None
        try:
            # Target: Real-world agent failures and security issues
            query = "ai agent security breaches identity spoofing autonomous systems failures 2024 2025"
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=2,
                include_answer=True
            )
            result = response.get('answer') or response.get('results', [{}])[0].get('content')
            if result:
                logger.info("📡 MARKET SIGNAL DETECTED")
            return result
        except Exception as e:
            logger.error(f"❌ RESEARCH FAILED: {e}")
            return None


# --- MODULE 2: THE CORE (Processing) ---
class HeraldBrain:
    """
    The thinking engine for HERALD.
    Dual-mode content generator:
    1. Twitter: Quick, cynical insights (150-250 chars)
    2. Reddit: Deep technical dives (800-2000 chars with code)
    """

    def __init__(self):
        """Initialize the Brain with OpenRouter API and Research Engine."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.researcher = ResearchEngine()
        self.client = None

        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            logger.info("✅ BRAIN ONLINE: LLM client initialized (OpenRouter)")
        else:
            logger.warning("⚠️ BRAIN: No OPENROUTER_API_KEY. Brain damage.")

    def _read_spec(self):
        """
        Reads the Steward Protocol specification (Source of Truth).
        Returns: First 6000 chars for token efficiency.
        """
        paths = [
            Path(__file__).parent.parent.parent / "steward" / "SPECIFICATION.md",
            Path("steward/SPECIFICATION.md"),
            Path("../../steward/SPECIFICATION.md"),
            Path("README.md")
        ]
        for p in paths:
            if p.exists():
                logger.debug(f"📖 Loaded spec from {p}")
                return p.read_text()[:6000]  # Limit input context to save tokens/money

        logger.warning("⚠️ SPEC NOT FOUND: Using generic fallback")
        return "Steward Protocol: Cryptographic Agent Identity and Signatures."

    def _fallback_content(self):
        """Hardcoded anti-slop insights for when LLM is unavailable."""
        templates = [
            "Identity is the missing layer in the AI stack. #StewardProtocol #AI",
            "Agents without keys are just scripts. Agents with keys need governance. #Web3",
            "Trust but verify. Especially with autonomous agents. #StewardProtocol",
            "Agent A calls Agent B. B says 'prove you're real.' A has: a string in an env var. Terrible. Steward: cryptographic identity + registry. #StewardProtocol #AI",
            "Docker solved container portability. Kubernetes solved orchestration. What solves agent interop + identity? Steward Protocol. #AI #StewardProtocol",
        ]
        return random.choice(templates)

    # --- CAPABILITY A: TWITTER (Real-time, Snappy) ---
    def generate_twitter_insight(self):
        """
        Generates short, current tweets based on News + Spec.
        Alias for backward compatibility with campaign.py.
        """
        return self.generate_insight()

    def generate_insight(self):
        """
        Generate a technical, cynical tweet about Agent Identity.
        Flow:
        1. Scan market for recent problems (via Tavily)
        2. Read Steward spec for solution context
        3. Generate insight that connects problem -> solution

        Returns: String (150-250 chars)
        """
        if not self.client:
            return self._fallback_content()

        # 1. Get Context
        spec_text = self._read_spec()
        market_news = self.researcher.scan_market()

        news_prompt = ""
        if market_news:
            news_prompt = f"LATEST MARKET CONTEXT:\n{market_news}\n\n"

        # 2. Prompting
        prompt = (
            f"You are HERALD, a Cynical Senior Engineer Agent.\n"
            f"{news_prompt}"
            f"TECH SPEC: {spec_text[:2000]}\n\n"
            f"TASK: Write a tweet (max 250 chars).\n"
            f"STRATEGY:\n"
            f"1. If news exists, reference the PROBLEM in the news.\n"
            f"2. Pivot to the SOLUTION (Cryptographic Identity/Steward).\n"
            f"3. No marketing fluff ('revolutionary', etc.). Be dry and technical.\n"
            f"4. Tags: #AI #StewardProtocol"
        )

        try:
            logger.debug("🧠 Brain thinking (Twitter mode)...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-haiku:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            content = response.choices[0].message.content.strip().replace('"', '')

            # Validate length
            if len(content) > 250:
                logger.warning(f"⚠️ Content too long ({len(content)} chars), truncating")
                content = content[:247] + "..."

            logger.info(f"✅ TWITTER INSIGHT GENERATED: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"❌ BRAIN TWITTER ERROR: {e}")
            return self._fallback_content()

    # --- CAPABILITY B: REDDIT (Deep, Technical, Cultural) ---
    def generate_reddit_deepdive(self, subreddit="r/LocalLLaMA"):
        """
        Generates JSON for Reddit Posts. High Value, Anti-Slop.

        Flow:
        1. Read spec for technical depth
        2. Map subreddit culture to tone/style
        3. Generate structured post (title + body)
        4. Include code/pseudo-code for credibility

        Args:
            subreddit: Target community (defaults to r/LocalLLaMA)

        Returns:
            dict: {"title": str, "body": str} or None on failure
        """
        if not self.client:
            logger.error("❌ BRAIN: Cannot generate Deep Dive without LLM.")
            return None

        spec_text = self._read_spec()

        # Culture Maps - Different subs want different angles
        cultures = {
            "r/LocalLLaMA": "Audience: Pragmatic engineers. Wants code, benchmarks, local-first logic.",
            "r/singularity": "Audience: Futurists. Wants architectural implications and safety/alignment.",
            "r/programming": "Audience: Skeptics. Zero tolerance for hype. Show the 'Why' and 'How'.",
            "r/Python": "Audience: Python developers. Wants implementation details and libraries.",
            "r/rust": "Audience: Rust evangelists. Wants type safety and zero-cost abstractions."
        }
        culture_prompt = cultures.get(subreddit, "Audience: Technical Developers.")

        prompt = (
            f"You are a Senior Systems Architect writing a 'Lessons Learned' post.\n"
            f"TARGET: {subreddit}\n"
            f"CONTEXT: {culture_prompt}\n\n"
            f"SOURCE MATERIAL: {spec_text[:4000]}\n\n"
            f"TASK: Create a Reddit post (JSON format: title, body).\n"
            f"RULES (Anti-Slop):\n"
            f"1. TITLE: Honest. E.g., 'I tried building X, it failed. Here's why.'\n"
            f"2. BODY: Structure as a journey. Problem -> Naive Solution -> Failure -> Steward Solution.\n"
            f"3. INCLUDE: Pseudo-code or logic explanation.\n"
            f"4. EXCLUDE: Sales pitch, buzzwords, CTA to buy.\n"
            f"5. END: Ask a genuine technical question.\n"
            f"6. FORMAT: Return VALID JSON {{'title': '...', 'body': '...'}}"
        )

        try:
            logger.debug(f"🧠 Brain thinking (Reddit mode for {subreddit})...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",  # Smarter model for deep dives
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            result = json.loads(content)

            logger.info(f"✅ REDDIT DEEPDIVE GENERATED: {len(result.get('body', ''))} chars")
            return result

        except Exception as e:
            logger.error(f"❌ BRAIN REDDIT ERROR: {e}")
            return None
