#!/usr/bin/env python3
"""
HERALD Brain: The Agency Model (v1.2)

Enterprise-Grade Multi-Agent Architecture:
- ResearchEngine: Market intelligence via Tavily (The Eyes)
- SeniorEditor: Quality assurance via Reflexion Pattern (The Quality Gate)
- HeraldBrain: Content orchestrator with dual-mode generation (The Core)
  - Twitter Mode: Real-time, snappy insights (150-250 chars)
  - Reddit Mode: Deep technical analysis (800-2000 chars)

The Agency Model:
1. Research: Scan market for problems (Tavily API)
2. Draft: Generate content (Haiku for Twitter, Sonnet for Reddit)
3. Critique: Editor reviews draft against quality criteria
4. Refine: Editor rewrites if needed (Reflexion Pattern)
5. Publish: Only approved content goes out

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
from examples.herald.aligner import VibeAligner

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


# --- MODULE 2: THE QUALITY GATE (Editorial) ---
class SeniorEditor:
    """
    The Ruthless Quality Assurance Layer.
    Critiques content drafts and rewrites them if they fail standards.

    This is the 'Reflexion Pattern' - the agent critiques its own work.
    No slop gets through. No marketing fluff. Pure technical value.
    """

    def __init__(self, client):
        self.client = client

    def critique_and_refine(self, draft, platform="twitter", max_retries=1):
        """
        Reviews a content draft and improves it if necessary.

        Args:
            draft: The initial content to review
            platform: "twitter" or "reddit" (affects scoring criteria)
            max_retries: How many rewrite attempts (default 1 to avoid infinite loops)

        Returns:
            str: Either the original draft (if good) or a refined version
        """
        if not self.client:
            logger.debug("🎨 EDITOR: No LLM available, passing draft as-is")
            return draft

        # Platform-specific quality criteria
        criteria = {
            "twitter": [
                "Is it generic AI slop? (ChatGPT-sounding clichés)",
                "Is it overly promotional? (Selling instead of teaching)",
                "Is it boring or obvious?",
                "Does it lack technical substance?"
            ],
            "reddit": [
                "Does it read like a sales pitch?",
                "Is it missing code examples or technical depth?",
                "Does it use buzzwords without explanations?",
                "Is the tone inappropriate for the subreddit culture?"
            ]
        }

        rules = criteria.get(platform, criteria["twitter"])
        rules_text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(rules))

        prompt = (
            f"You are a Ruthless Senior Editor at a top-tier tech publication.\n"
            f"Review this {platform.upper()} draft:\n\n"
            f"'{draft}'\n\n"
            f"QUALITY CRITERIA (fail if ANY apply):\n{rules_text}\n\n"
            f"TASK:\n"
            f"- If draft is GOOD (passes all criteria), reply ONLY: PASS\n"
            f"- If draft is BAD, rewrite it to be:\n"
            f"  * More technically specific (use concrete examples)\n"
            f"  * More cynical/honest (no hype)\n"
            f"  * More actionable (what can the reader DO with this?)\n\n"
            f"Return ONLY 'PASS' or the rewritten content. No explanations."
        )

        try:
            logger.debug("🎨 EDITOR: Reviewing draft...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",  # Editor needs high IQ
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            verdict = response.choices[0].message.content.strip()

            if verdict == "PASS" or verdict.startswith("PASS"):
                logger.info("✅ EDITOR: Draft approved (no changes needed)")
                return draft
            else:
                # Clean the rewrite
                refined = verdict.replace('"', '').replace("'", "'")
                logger.info(f"🎨 EDITOR: Draft rewritten\n  WAS: {draft[:60]}...\n  NOW: {refined[:60]}...")
                return refined

        except Exception as e:
            logger.error(f"❌ EDITOR ERROR: {e}")
            logger.info("🎨 EDITOR: Falling back to original draft")
            return draft


# --- MODULE 3: THE CORE (Processing) ---
class HeraldBrain:
    """
    The thinking engine for HERALD.
    Dual-mode content generator:
    1. Twitter: Quick, cynical insights (150-250 chars)
    2. Reddit: Deep technical dives (800-2000 chars with code)
    """

    def __init__(self):
        """Initialize the Brain with OpenRouter API, Research Engine, Senior Editor, and Governance."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.researcher = ResearchEngine()
        self.client = None
        self.editor = None
        self.aligner = VibeAligner()  # The Governance Module (The Conscience)

        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            self.editor = SeniorEditor(self.client)  # The Quality Gate
            logger.info("✅ BRAIN ONLINE: LLM client initialized (OpenRouter)")
            logger.info("✅ EDITOR ONLINE: Quality gate active")
            logger.info("🛡️ ALIGNER ONLINE: Governance enforcement active")
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
            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            # Validate length
            if len(raw_draft) > 250:
                logger.warning(f"⚠️ Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            logger.info(f"✅ TWITTER DRAFT GENERATED: {len(raw_draft)} chars")

            # QUALITY GATE 1: Editor reviews and refines the draft
            if self.editor:
                edited_content = self.editor.critique_and_refine(raw_draft, platform="twitter")
            else:
                logger.debug("⚠️ EDITOR: Not available, using raw draft")
                edited_content = raw_draft

            # QUALITY GATE 2: Aligner checks against governance (ethical constraints)
            final_content = self.aligner.align(edited_content, platform="twitter", client=self.client)

            if not final_content:
                # Governance rejected the content. Fallback to safe spec reading.
                logger.warning("⚠️ ALIGNER REJECTED: Content violates governance. Switching to fallback.")
                return self._fallback_content()

            logger.info(f"✅ FINAL TWITTER CONTENT: {len(final_content)} chars (passed editor + aligner)")
            return final_content

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
            draft_result = json.loads(content)

            logger.info(f"✅ REDDIT DRAFT GENERATED: {len(draft_result.get('body', ''))} chars")

            # QUALITY GATE 1: Editor reviews the body (title is usually fine)
            edited_body = draft_result.get('body', '')
            if self.editor and edited_body:
                refined_body = self.editor.critique_and_refine(
                    edited_body,
                    platform="reddit"
                )
                draft_result['body'] = refined_body
                logger.info(f"✅ EDITOR REFINED REDDIT POST: {len(refined_body)} chars")

            # QUALITY GATE 2: Aligner checks against governance (ethical constraints)
            aligned_body = self.aligner.align(draft_result['body'], platform="reddit", client=self.client)

            if not aligned_body:
                # Governance rejected the content. Return None to indicate failure.
                logger.warning("⚠️ ALIGNER REJECTED: Reddit post violates governance.")
                return None

            draft_result['body'] = aligned_body
            logger.info(f"✅ FINAL REDDIT POST: {len(aligned_body)} chars (passed editor + aligner)")
            return draft_result

        except Exception as e:
            logger.error(f"❌ BRAIN REDDIT ERROR: {e}")
            return None
