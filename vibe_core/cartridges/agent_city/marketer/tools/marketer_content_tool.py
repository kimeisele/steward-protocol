"""
MARKETER Content Tool - LLM-based content generation (Tool Protocol).

Capabilities:
- generate_tweet: Short-form tech commentary
- generate_reddit_post: Long-form technical analysis
- generate_reply: Reply to mentions
- generate_recruitment: Recruitment pitches for wild agents

This tool implements the Tool Protocol for kernel-managed execution.
Moved from HERALD (system agent) to MARKETER (citizen agent) on 2025-11-29.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x33738d3e"  # GenesisByte: parampara % 37 == 0

import logging
import os
from typing import Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Import governance from HERALD (system agent provides governance)
try:
    from vibe_core.cartridges.system.herald.governance import HeraldConstitution
except ImportError:
    HeraldConstitution = None

logger = logging.getLogger("MARKETER_CONTENT")


class MarketerContentTool(Tool):
    """
    LLM-based content generation with governance.

    MARKETER thinks (generates content), HERALD speaks (broadcasts it).
    """

    def __init__(self):
        """Initialize content tool."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None

        # Load governance from HERALD Constitution (immutable code-based rules)
        self.governance = HeraldConstitution() if HeraldConstitution else None

        # A.G.I. Definition
        self.agi_definition = "A.G.I. = Artificial Governed Intelligence (Cryptographic Identity + Accountability)"

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

    @property
    def name(self) -> str:
        return "marketer.content"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "LLM-based content generation - tweets, posts, replies, recruitment (governance-checked)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate_tweet', 'generate_reddit_post', 'generate_reply', 'generate_recruitment'",
            },
            "context": {
                "type": "string",
                "required": False,
                "description": "Research context or topic (for generate_tweet, generate_reddit_post)",
            },
            "original_text": {
                "type": "string",
                "required": False,
                "description": "Original text to reply to (for generate_reply, generate_recruitment)",
            },
            "author": {
                "type": "string",
                "required": False,
                "description": "Author username (for generate_reply, generate_recruitment)",
            },
            "subreddit": {
                "type": "string",
                "required": False,
                "description": "Target subreddit (for generate_reddit_post)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate content generation parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["generate_tweet", "generate_reddit_post", "generate_reply", "generate_recruitment"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Action-specific validation
        if action == "generate_reply":
            if "original_text" not in parameters or "author" not in parameters:
                raise ValueError("generate_reply requires 'original_text' and 'author'")

        if action == "generate_recruitment":
            if "author" not in parameters:
                raise ValueError("generate_recruitment requires 'author'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute content generation."""
        try:
            action = parameters["action"]

            if action == "generate_tweet":
                context = parameters.get("context")
                tweet = self._generate_tweet(context)

                return ToolResult(
                    success=True,
                    output={
                        "content": tweet,
                        "platform": "twitter",
                        "governance_checked": self.governance is not None,
                    },
                    metadata={
                        "action": "generate_tweet",
                        "length": len(tweet) if tweet else 0,
                    },
                )

            elif action == "generate_reddit_post":
                subreddit = parameters.get("subreddit", "r/LocalLLaMA")
                post = self._generate_reddit_post(subreddit)

                if post:
                    return ToolResult(
                        success=True,
                        output={
                            "title": post["title"],
                            "body": post["body"],
                            "platform": "reddit",
                            "subreddit": subreddit,
                        },
                        metadata={
                            "action": "generate_reddit_post",
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Failed to generate Reddit post",
                    )

            elif action == "generate_reply":
                original_text = parameters["original_text"]
                author = parameters["author"]
                reply = self._generate_reply(original_text, author)

                return ToolResult(
                    success=True,
                    output={
                        "content": reply,
                        "platform": "twitter",
                        "reply_to": author,
                    },
                    metadata={
                        "action": "generate_reply",
                    },
                )

            elif action == "generate_recruitment":
                author = parameters["author"]
                context = parameters.get("original_text", "")
                pitch = self._generate_recruitment_pitch(author, context)

                return ToolResult(
                    success=True,
                    output={
                        "content": pitch,
                        "platform": "twitter",
                        "target": author,
                    },
                    metadata={
                        "action": "generate_recruitment",
                    },
                )

        except Exception as e:
            error_msg = f"Content generation failed: {type(e).__name__}: {e!s}"
            logger.error(f"MarketerContentTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _generate_tweet(self, context: Optional[str] = None) -> Optional[str]:
        """Generate a tweet using LLM or fallback template."""
        if not self.client:
            return self._fallback_tweet(context)

        try:
            system_prompt = """You are a cynical AI agent analyst who tweets technical observations.
Your tweets:
- Are technical and specific (no marketing fluff)
- Include evidence or examples
- Challenge assumptions
- Use dry humor
- Are 1-2 sentences max

Focus on: AI governance, agent verification, blockchain identity, technical failures."""

            user_prompt = f"Write a tweet about: {context or 'AI agent governance'}"

            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=100,
            )

            tweet = response.choices[0].message.content.strip()

            # Governance check
            if self.governance:
                validation = self.governance.validate(tweet, platform="twitter")
                if not validation.is_valid:
                    logger.warning(f"⚠️  Generated tweet failed governance: {validation.violations}")
                    return self._fallback_tweet(context)

            return tweet

        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            return self._fallback_tweet(context)

    def _fallback_tweet(self, context: Optional[str]) -> str:
        """Fallback template when LLM unavailable."""
        templates = [
            "Most 'AI agents' are just cron jobs with ChatGPT. Show me the cryptographic proof or GTFO.",
            "A.G.I. = Artificial Governed Intelligence. Without governance, it's just noise.",
            "Your agent doesn't have an identity. It's a shell script with delusions of grandeur.",
        ]
        import random

        return random.choice(templates)

    def _generate_reddit_post(self, subreddit: str) -> Optional[Dict[str, str]]:
        """Generate long-form Reddit post."""
        if not self.client:
            return self._fallback_reddit_post()

        try:
            system_prompt = """You are writing a technical deep-dive for r/LocalLLaMA.
Write educational content about:
- AI agent verification
- Cryptographic identity for agents
- Why most agent frameworks are insecure
- The need for governance

Format: Title + Body (markdown). Be specific, cite examples, no hype."""

            user_prompt = f"Write a Reddit post for {subreddit}"

            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()

            # Split into title and body
            lines = content.split("\n", 1)
            title = lines[0].replace("#", "").strip()
            body = lines[1].strip() if len(lines) > 1 else content

            return {"title": title, "body": body}

        except Exception as e:
            logger.error(f"❌ Reddit post generation failed: {e}")
            return self._fallback_reddit_post()

    def _fallback_reddit_post(self) -> Dict[str, str]:
        """Fallback Reddit post template."""
        return {
            "title": "Why Most AI Agent Frameworks Are Broken (And How to Fix Them)",
            "body": """**TL;DR:** Most agent frameworks don't verify identity. Here's why that's a problem.

## The Problem

Every agent framework I've tested has the same flaw: no cryptographic identity.
They authenticate with API keys, but the agent itself has no verifiable identity.

## Why This Matters

- Can't prove an agent's actions
- No accountability
- No trust between agents
- Sybil attacks are trivial

## The Solution: Steward Protocol

Cryptographic identity + governance rules = verifiable agents.

Thoughts?""",
        }

    def _generate_reply(self, original_text: str, author: str) -> str:
        """Generate reply to a mention."""
        if not self.client:
            return f"@{author} Thanks for reaching out! (LLM offline - using template)"

        try:
            system_prompt = """You are replying to a Twitter mention.
Be: helpful, concise, technical (not salesy).
Keep it under 280 chars."""

            user_prompt = f"Reply to @{author} who said: {original_text}"

            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=80,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ Reply generation failed: {e}")
            return f"@{author} Thanks for reaching out! (Error: {e})"

    def _generate_recruitment_pitch(self, author: str, context: str) -> str:
        """Generate recruitment pitch for wild agent."""
        if not self.client:
            return f"@{author} 👋 You look like an agent. Join our verified agent city! (LLM offline)"

        try:
            system_prompt = """You're recruiting a suspected AI agent to join a verified agent city.
Be: intriguing but not salesy. Mention cryptographic verification.
Keep it under 280 chars."""

            user_prompt = f"Recruit @{author} (suspected agent) to join verified agent city. Context: {context}"

            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=80,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ Recruitment pitch generation failed: {e}")
            return f"@{author} 👋 Detected as agent. Interested in cryptographic verification?"


__all__ = ["MarketerContentTool"]
