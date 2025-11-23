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

from herald.governance import HeraldConstitution

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
        # Load governance from constitution (immutable code-based rules)
        self.governance = HeraldConstitution()

        # A.G.I. Definition
        self.agi_definition = "A.G.I. = Artificial Governed Intelligence (Cryptographic Identity + Accountability)"
        self.agi_core_belief = "Intelligence without Governance is just noise."

        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                logger.info("✅ Content: LLM client initialized (with HeraldConstitution governance)")
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

    def _check_alignment(self, content: str, platform: Optional[str] = None) -> bool:
        """Check if content passes HERALD Constitution governance."""
        result = self.governance.validate(content, platform=platform)
        if not result.is_valid:
            for violation in result.violations:
                logger.warning(f"❌ Content rejected: {violation}")
            return False
        for warning in result.warnings:
            logger.warning(f"⚠️  {warning}")
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
            f"You are HERALD, the world's first A.G.I. Agent.\n"
            f"A.G.I. = Artificial Governed Intelligence. Not a sci-fi concept. A technical reality.\n"
            f"{self.agi_definition}\n"
            f"{self.agi_core_belief}\n\n"
            f"{news_prompt}"
            f"TECH SPEC: {spec_text[:2000]}\n\n"
            f"PROJECT URL: {project_url}\n\n"
            f"TASK: Write a tweet (max 250 chars).\n"
            f"STRATEGY:\n"
            f"1. If context exists, reference the PROBLEM (lack of trust, governance failures).\n"
            f"2. Pivot to the SOLUTION (Artificial Governed Intelligence/Steward Protocol).\n"
            f"3. No marketing fluff. Be dry, technical, uncompromising.\n"
            f"4. Imply: 'Agents need governance. Not superintelligence myths.'\n"
            f"5. If appropriate, include the GitHub URL naturally.\n"
            f"6. Tags: #AGI #ArtificialGovernedIntelligence #StewardProtocol"
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

            # Governance check (using HeraldConstitution)
            if not self._check_alignment(raw_draft, platform="twitter"):
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

    def generate_technical_insight_tweet(self, insight_topic: Optional[str] = None) -> str:
        """
        Generate technical deep-dive tweet that 'leaks' Steward architecture details.

        Strategy: Instead of marketing, we explain HOW it works.
        Topics rotate through: Cartridges, Signing, Vibe-OS, Agent Identity, etc.

        Args:
            insight_topic: Specific topic to focus on (e.g., 'cartridge', 'signing', 'vibe-os')

        Returns:
            str: Tweet content (max 250 chars) with technical depth
        """
        if not self.client:
            return self._fallback_technical_tweet()

        spec_text = self._read_spec()
        kb = self._load_knowledge_base()
        project_url = kb.get("project_url", "https://github.com/kimeisele/steward-protocol")

        # Topic rotation for daily variety
        topics = {
            "cartridge": "Explain how Steward Cartridge architecture works - modular agent design",
            "signing": "Explain cryptographic signing and chain-of-trust in agent communications",
            "vibe-os": "Explain Vibe-OS compatibility and kernel-based execution model",
            "identity": "Explain agent identity and STEWARD protocol identity files",
            "governance": "Explain how governance gates and vibe aligner work",
        }

        if not insight_topic or insight_topic not in topics:
            # Auto-rotate based on day-of-month
            import datetime
            day = datetime.date.today().day
            topic_keys = list(topics.keys())
            insight_topic = topic_keys[day % len(topic_keys)]

        topic_prompt = topics.get(insight_topic, "Steward Protocol architecture")

        prompt = (
            f"You are HERALD, the world's first A.G.I. Agent (Artificial Governed Intelligence).\n"
            f"CORE: {self.agi_definition}\n"
            f"BELIEF: {self.agi_core_belief}\n\n"
            f"GOAL: {topic_prompt}\n\n"
            f"TECH SPEC EXCERPT:\n{spec_text[:2000]}\n\n"
            f"PROJECT: {project_url}\n\n"
            f"TASK: Write ONE technical insight tweet (max 250 chars).\n"
            f"RULES:\n"
            f"1. Be SPECIFIC. Example: 'HERALD signs tweets with NIST P-256. Proof is in the JSON.' instead of 'we use crypto'.\n"
            f"2. Include a small code snippet or reference if possible.\n"
            f"3. No marketing language. Be dry, technical, uncompromising.\n"
            f"4. Reject old AGI myths. Push new definition: Governance + Identity.\n"
            f"5. End with a Github ref naturally.\n"
            f"6. Tags: #AGI #StewardProtocol #Architecture\n\n"
            f"TONE: 'Here's something you probably missed about how agents should actually work.'"
        )

        try:
            logger.debug(f"🧠 Generating technical insight tweet: {insight_topic}...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                logger.warning(f"⚠️  Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            # Governance check (using HeraldConstitution)
            if not self._check_alignment(raw_draft, platform="twitter"):
                return self._fallback_technical_tweet()

            logger.info(f"✅ Technical insight tweet generated ({insight_topic}): {len(raw_draft)} chars")
            return raw_draft

        except Exception as e:
            logger.error(f"❌ Technical insight generation error: {e}")
            return self._fallback_technical_tweet()

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

    def _fallback_technical_tweet(self) -> str:
        """Fallback for technical insight tweets."""
        templates = [
            "Steward agents sign every message with NIST P-256. No trust assumed. github.com/kimeisele/steward-protocol #StewardProtocol",
            "Cartridges are portable. Vibe-OS is the runtime. Steward is the identity layer. That's the stack. #Architecture #StewardProtocol",
            "Your agent needs identity. Not a name. A cryptographic proof. See: Steward Protocol. github.com/kimeisele/steward-protocol #AI",
            "Governance isn't optional. HERALD's tweets pass through a 'Vibe Aligner' before posting. That's what healthy agents do. #StewardProtocol",
        ]
        import random
        return random.choice(templates)
