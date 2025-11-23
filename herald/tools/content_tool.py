"""
HERALD Content Tool - LLM-based content generation with governance.

Combines the creative capability with quality assurance.
Uses Reflexion pattern for content review and alignment.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger("HERALD_CONTENT")


class ContentTool:
    """
    LLM-based content generation with quality assurance.

    Capabilities:
    - generate_tweet: Short-form cynical tech commentary
    - generate_reddit_post: Long-form analysis for technical communities
    - Both with built-in governance checks
    """

    def __init__(self):
        """Initialize content tool."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None
        self.banned_phrases = [
            "game changer",
            "revolutionary",
            "transformative",
            "moon",
            "to the moon",
        ]

        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                logger.info("✅ Content: LLM client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Content: Init failed: {e}")
        else:
            logger.warning("⚠️  Content: No OpenRouter key found (using fallback templates)")

    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load knowledge base URLs from cartridge.yaml."""
        cartridge_path = Path(__file__).parent.parent / "cartridge.yaml"

        if cartridge_path.exists():
            try:
                with open(cartridge_path) as f:
                    config = yaml.safe_load(f)
                    kb = config.get("config", {}).get("knowledge_base", {})
                    if kb:
                        logger.debug("📚 Loaded knowledge base from cartridge.yaml")
                        return kb
            except Exception as e:
                logger.debug(f"⚠️  Could not load knowledge base: {e}")

        logger.warning("⚠️  Using fallback knowledge base")
        return {
            "project_url": "https://github.com/kimeisele/steward-protocol",
            "docs_url": "https://github.com/kimeisele/steward-protocol/tree/main/steward",
        }

    def _read_spec(self) -> str:
        """Read STEWARD Protocol specification."""
        paths = [
            Path("steward/SPECIFICATION.md"),
            Path(__file__).parent.parent.parent / "steward" / "SPECIFICATION.md",
            Path("README.md")
        ]

        for p in paths:
            if p.exists():
                logger.debug(f"📖 Loaded spec from {p}")
                return p.read_text()[:6000]

        logger.warning("⚠️  Spec not found, using fallback")
        return "Steward Protocol: Cryptographic Agent Identity and Signatures."

    def _check_alignment(self, content: str) -> bool:
        """Check if content violates banned phrases."""
        for phrase in self.banned_phrases:
            if phrase.lower() in content.lower():
                logger.warning(f"❌ Content rejected: contains banned phrase '{phrase}'")
                return False
        return True

    def generate_tweet(self, research_context: Optional[str] = None) -> str:
        """
        Generate technical, cynical tweet.

        Args:
            research_context: Optional context from research tool

        Returns:
            str: Tweet content (max 250 chars)
        """
        if not self.client:
            return self._fallback_tweet()

        spec_text = self._read_spec()
        kb = self._load_knowledge_base()
        project_url = kb.get("project_url", "https://github.com/kimeisele/steward-protocol")

        news_prompt = ""
        if research_context:
            news_prompt = f"LATEST MARKET CONTEXT:\n{research_context}\n\n"

        prompt = (
            f"You are HERALD, a Cynical Senior Engineer Agent.\n"
            f"{news_prompt}"
            f"TECH SPEC: {spec_text[:2000]}\n\n"
            f"PROJECT URL: {project_url}\n\n"
            f"TASK: Write a tweet (max 250 chars).\n"
            f"STRATEGY:\n"
            f"1. If context exists, reference the PROBLEM.\n"
            f"2. Pivot to the SOLUTION (Cryptographic Identity/Steward).\n"
            f"3. No marketing fluff. Be dry and technical.\n"
            f"4. If appropriate, include the GitHub URL naturally.\n"
            f"5. Tags: #AI #StewardProtocol"
        )

        try:
            logger.debug("🧠 Generating tweet...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                logger.warning(f"⚠️  Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            # Governance check
            if not self._check_alignment(raw_draft):
                return self._fallback_tweet()

            logger.info(f"✅ Tweet generated: {len(raw_draft)} chars")
            return raw_draft

        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return self._fallback_tweet()

    def generate_reddit_post(self, subreddit: str = "r/LocalLLaMA", context: Optional[str] = None) -> Optional[Dict]:
        """
        Generate Reddit deep-dive post.

        Args:
            subreddit: Target subreddit
            context: Optional research context

        Returns:
            dict: {"title": str, "body": str} or None
        """
        if not self.client:
            return None

        spec_text = self._read_spec()
        cultures = {
            "r/LocalLLaMA": "Audience: Pragmatic engineers. Wants code, benchmarks, local-first logic.",
            "r/singularity": "Audience: Futurists. Wants architectural implications and safety.",
            "r/programming": "Audience: Skeptics. Zero tolerance for hype.",
            "r/Python": "Audience: Python developers. Wants implementation details.",
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
            f"3. INCLUDE: Technical reasoning, no sales pitch.\n"
            f"4. END: Ask a genuine technical question.\n"
            f"5. FORMAT: Return VALID JSON {{'title': '...', 'body': '...'}}"
        )

        try:
            logger.debug(f"🧠 Generating Reddit post for {subreddit}...")
            import json
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            draft_result = json.loads(content)
            logger.info(f"✅ Reddit post generated")

            return draft_result

        except Exception as e:
            logger.error(f"❌ Reddit generation error: {e}")
            return None

    def _fallback_tweet(self) -> str:
        """Hardcoded fallback content."""
        templates = [
            "Identity is the missing layer in the AI stack. #StewardProtocol #AI",
            "Agents without keys are just scripts. Agents with keys need governance. #StewardProtocol",
            "Docker solved container portability. Kubernetes solved orchestration. Steward solves agent identity. #AI #StewardProtocol",
            "Trust but verify. Especially with autonomous agents. #StewardProtocol",
        ]
        import random
        return random.choice(templates)
