"""
HERALD Creative Capability
LLM-based content generation with quality assurance and governance.
Kernel-compatible module (configured via system.yaml).

Architecture:
- ContentGenerator: Base LLM-powered generation
- QualityEditor: Reflexion pattern for content review
- VibeAligner: Governance enforcement
"""

import os
import json
import random
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger("HERALD_CREATIVE")


class QualityEditor:
    """Internal quality assurance for content drafts."""

    def __init__(self, client: OpenAI):
        self.client = client

    def critique_and_refine(self, draft: str, platform: str = "twitter") -> str:
        """
        Review draft and improve if needed (Reflexion Pattern).

        Args:
            draft: Initial content
            platform: "twitter" or "reddit"

        Returns:
            str: Approved or refined content
        """
        if not self.client:
            logger.debug("🎨 EDITOR: No LLM available, passing draft as-is")
            return draft

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
                model="anthropic/claude-3-5-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            verdict = response.choices[0].message.content.strip()

            if verdict == "PASS" or verdict.startswith("PASS"):
                logger.info("✅ EDITOR: Draft approved (no changes needed)")
                return draft
            else:
                refined = verdict.replace('"', '').replace("'", "'")
                logger.info(f"🎨 EDITOR: Draft rewritten\n  WAS: {draft[:60]}...\n  NOW: {refined[:60]}...")
                return refined

        except Exception as e:
            logger.error(f"❌ EDITOR ERROR: {e}")
            logger.info("🎨 EDITOR: Falling back to original draft")
            return draft


class CreativeCapability:
    """
    LLM-based content generation capability.
    Generates marketing-free, technically honest content.

    Configuration via kernel.get_config("capabilities.creative")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize creative capability.

        Args:
            config: Creative capability config from system.yaml
        """
        self.config = config
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None
        self.editor = None
        self.enabled = config.get("enabled", True)

        if self.api_key and self.enabled:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                self.editor = QualityEditor(self.client)
                logger.info("✅ CREATIVE CAPABILITY: LLM client initialized")
                logger.info("✅ EDITOR: Quality gate active")
            except Exception as e:
                logger.warning(f"⚠️  CREATIVE: Init failed: {e}")
        elif not self.api_key:
            logger.warning("⚠️  CREATIVE: No OPENROUTER_API_KEY found.")

    def _read_spec(self) -> str:
        """Read STEWARD Protocol specification (context)."""
        paths = [
            Path("steward/SPECIFICATION.md"),
            Path(__file__).parent.parent.parent / "steward" / "SPECIFICATION.md",
            Path("README.md")
        ]

        for p in paths:
            if p.exists():
                logger.debug(f"📖 Loaded spec from {p}")
                return p.read_text()[:6000]

        logger.warning("⚠️  SPEC NOT FOUND: Using generic fallback")
        return "Steward Protocol: Cryptographic Agent Identity and Signatures."

    def _fallback_content(self) -> str:
        """Hardcoded anti-slop insights for degraded mode."""
        templates = [
            "Identity is the missing layer in the AI stack. #StewardProtocol #AI",
            "Agents without keys are just scripts. Agents with keys need governance. #StewardProtocol",
            "Trust but verify. Especially with autonomous agents. #StewardProtocol",
            "Agent A calls Agent B. B says 'prove you're real.' A has: a string in an env var. Terrible. Steward: cryptographic identity + registry. #StewardProtocol #AI",
            "Docker solved container portability. Kubernetes solved orchestration. What solves agent interop + identity? Steward Protocol. #AI #StewardProtocol",
        ]
        return random.choice(templates)

    def generate_insight(self, research_context: Optional[str] = None) -> str:
        """
        Generate technical, cynical tweet about Agent Identity.

        Args:
            research_context: Optional research context from research capability

        Returns:
            str: Generated content (150-250 chars for Twitter)
        """
        if not self.client:
            return self._fallback_content()

        spec_text = self._read_spec()
        news_prompt = ""

        if research_context:
            news_prompt = f"LATEST MARKET CONTEXT:\n{research_context}\n\n"

        prompt = (
            f"You are HERALD, a Cynical Senior Engineer Agent.\n"
            f"{news_prompt}"
            f"TECH SPEC: {spec_text[:2000]}\n\n"
            f"TASK: Write a tweet (max 250 chars).\n"
            f"STRATEGY:\n"
            f"1. If context exists, reference the PROBLEM.\n"
            f"2. Pivot to the SOLUTION (Cryptographic Identity/Steward).\n"
            f"3. No marketing fluff ('revolutionary', etc.). Be dry and technical.\n"
            f"4. Tags: #AI #StewardProtocol"
        )

        try:
            logger.debug("🧠 CREATIVE: Generating content (Twitter mode)...")
            response = self.client.chat.completions.create(
                model=self.config.get("model", "anthropic/claude-3-haiku"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get("max_tokens", 150),
                temperature=self.config.get("temperature", 0.8)
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                logger.warning(f"⚠️  Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            logger.info(f"✅ CONTENT DRAFT GENERATED: {len(raw_draft)} chars")

            # Quality gate
            if self.editor:
                final_content = self.editor.critique_and_refine(raw_draft, platform="twitter")
            else:
                final_content = raw_draft

            logger.info(f"✅ FINAL CONTENT: {len(final_content)} chars")
            return final_content

        except Exception as e:
            logger.error(f"❌ CREATIVE ERROR: {e}")
            return self._fallback_content()

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
            logger.error("❌ CREATIVE: Cannot generate deep dive without LLM")
            return None

        spec_text = self._read_spec()

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
            logger.debug(f"🧠 CREATIVE: Generating Reddit post for {subreddit}...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            draft_result = json.loads(content)
            logger.info(f"✅ REDDIT DRAFT GENERATED: {len(draft_result.get('body', ''))} chars")

            # Quality gate
            if self.editor and draft_result.get('body'):
                refined_body = self.editor.critique_and_refine(
                    draft_result['body'],
                    platform="reddit"
                )
                draft_result['body'] = refined_body

            return draft_result

        except Exception as e:
            logger.error(f"❌ CREATIVE REDDIT ERROR: {e}")
            return None
