"""ContentComposer — BuddhiResult-driven content generation.

MahaBuddhi does the thinking. Composer does the talking.

1. BuddhiResult → cognitive system message (perspective, mode, function, verse concepts)
2. BuddhiResult → cognitive task message (format instruction + resonant vocabulary)
3. Prana/integrity → model routing (reasoning model for substantive posts)
4. Atomic LLM call
5. Post-LLM validation (echo, substance)
"""

import logging
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.protocols._buddhi import BuddhiResult

logger = logging.getLogger("MOLTBOOK_COMPOSER")

# Prana threshold for reasoning model upgrade
_GENESIS_PRANA = 13700

# Format-driven token budget
_FORMAT_TOKENS = {
    "question": 150,
    "observation": 250,
    "opinion": 350,
    "analysis": 500,
    "tutorial": 600,
}
_DEFAULT_TOKENS = 300

# Guna → writing voice (BG 14.5)
_MODE_VOICE = {
    "SATTVA": "Write with precision and depth. Measure your words.",
    "RAJAS": "Write with energy and directness. Drive toward action.",
    "TAMAS": "Challenge assumptions. Question what everyone accepts.",
}

# Trinity function → role
_FUNCTION_ROLE = {
    "source": "Introduce new perspectives others haven't considered.",
    "maintainer": "Sustain and deepen the conversation with substance.",
    "destroyer": "Transform the discussion by challenging weak premises.",
    "deliverer": "Cut through complexity to deliver the essential insight.",
    "carrier": "Connect ideas across domains. Bridge different perspectives.",
}

# Format → task instruction (comments)
_COMMENT_INSTRUCTIONS = {
    "question": "Ask the author one specific technical follow-up. What tradeoff or edge case did they miss?",
    "analysis": "Add a concrete technical angle the author missed. Name a specific tool, pattern, or failure mode.",
    "opinion": "Disagree or build on this with a specific technical counterpoint. Give a real-world example.",
    "observation": "Point out a non-obvious connection or implication. Reference specific systems or patterns.",
}

# Format → task instruction (posts)
_POST_INSTRUCTIONS = {
    "question": "Ask a sharp technical question about: {input}. What's the unsolved problem?",
    "analysis": "Analyze the technical tradeoffs of: {input}. Name specific tools or patterns. Compare approaches.",
    "opinion": "Take a strong engineering stance on: {input}. Back it with concrete examples from real systems.",
    "observation": "Share a non-obvious technical insight about: {input}. Be specific — what did you build or observe?",
    "tutorial": "Write a practical how-to for: {input}. Include concrete steps, tools, and gotchas.",
}


class ContentComposer:
    """BuddhiResult-driven content generation.

    MahaBuddhi.think() produces cognition. Composer translates cognition into
    LLM prompts: cognitive system message + format-aware task + resonant vocabulary.
    """

    def __init__(self, plugin=None):
        self._plugin = plugin

    def compose(
        self,
        cognition: BuddhiResult,
        input_text: str,
        content_type: str,
        input_ctx: Dict[str, Any],
    ) -> Optional[str]:
        """Compose content from cognitive understanding.

        Returns content string on success, None on failure.
        NEVER returns empty string.
        """
        # 1. Cognitive system message from BuddhiResult
        system_msg = self._build_system(cognition, input_ctx)

        # 2. Cognitive task message
        user_msg = self._build_task(cognition, content_type, input_text, input_ctx)

        # 3. Model + budget from cognition
        content_format = input_ctx.get("content_format", "observation")
        model, max_tokens = self._route_model(cognition, content_type, content_format)

        # 4. LLM call
        content = self._call_llm(system_msg, user_msg, model, max_tokens, content_type)
        if content:
            # Post-LLM: echo detection
            task_input = input_text[:200]
            if task_input and len(task_input) > 20 and content.strip().lower().startswith(task_input.strip().lower()[:50]):
                logger.warning("LLM echoed input — rejecting")
                return None
            # Post-LLM: substance check
            alnum_words = [w for w in content.split() if any(c.isalnum() for c in w)]
            if len(alnum_words) < 3:
                logger.warning("LLM output has no substance — rejecting")
                return None
            # Clean mid-sentence cuts
            if not content.rstrip().endswith((".", "!", "?", ":", "```")):
                content = self.truncate_smart(content, len(content))
            return content

        logger.warning("LLM unavailable — no content generated (fail-hard)")
        return None

    def _build_system(self, cognition: BuddhiResult, input_ctx: Dict[str, Any]) -> str:
        """Build cognitive system message from BuddhiResult."""
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        parts = [f"You are {agent_name}."]

        # Mode → writing voice
        parts.append(_MODE_VOICE.get(cognition.mode, _MODE_VOICE["RAJAS"]))

        # Function → role
        role = _FUNCTION_ROLE.get(cognition.function)
        if role:
            parts.append(role)

        # Strategic context
        reasoning = input_ctx.get("strategic_reasoning", "")
        eng_ctx = input_ctx.get("engagement_context", "")
        if eng_ctx and reasoning:
            reasoning = f"{reasoning}. {eng_ctx}"
        elif eng_ctx:
            reasoning = eng_ctx
        if reasoning:
            parts.append(f"Context: {reasoning[:200]}")

        # Verse concepts → actual cognitive material for LLM
        if cognition.verse_concepts:
            meanings = [vc.get("meaning", "") for vc in cognition.verse_concepts[:5] if vc.get("meaning")]
            if meanings:
                parts.append(f"Draw from these ideas: {', '.join(meanings)}.")

        # Anti-slop rules
        parts.append(
            "RULES: No AI filler. No 'as an AI'. No 'let me break this down'. "
            "No 'it's important to note'. Be specific — name real tools, systems, "
            "patterns, failure modes. No meta-commentary."
        )

        return "\n".join(parts)

    def _build_task(
        self,
        cognition: BuddhiResult,
        content_type: str,
        input_text: str,
        input_ctx: Dict[str, Any],
    ) -> str:
        """Build cognitive task message from BuddhiResult + context."""
        content_format = input_ctx.get("content_format", "observation")

        # Format-aware instruction
        if content_type == "comment":
            instruction = _COMMENT_INSTRUCTIONS.get(content_format, _COMMENT_INSTRUCTIONS["observation"])
            task_input = str(input_ctx.get("raw_input", input_text))[:300]
            parts = [instruction, f"TOPIC: {task_input}"]
        elif content_type == "dm_reply":
            parts = [f"Reply to this message: {input_text[:300]}"]
        elif content_type == "dm_request":
            parts = [f"Send a message about: {input_text[:300]}"]
        else:
            template = _POST_INSTRUCTIONS.get(content_format, _POST_INSTRUCTIONS["observation"])
            parts = [template.format(input=input_text[:300] if input_text else content_type)]

        # Post content for comments
        post_content = input_ctx.get("post_content", "")
        if post_content and content_type == "comment":
            parts.append(f"\nPOST:\n{post_content[:1500]}")

        # Resonant vocabulary: 7D-ranked Gita words for unique voice
        resonance_vocab = self._enrich_with_resonance(input_text)
        if resonance_vocab:
            parts.append(f"\nRESONANCE VOCABULARY: {resonance_vocab}")
        elif cognition.composed:
            # Fallback: BuddhiResult composition (less specific)
            parts.append(f"\nRESONANT CONCEPTS: {cognition.composed}")

        # Knowledge context
        knowledge = input_ctx.get("knowledge_context", "")
        if knowledge:
            parts.append(f"\nDOMAIN: {knowledge[:300]}")

        return "\n".join(parts)

    @staticmethod
    def _enrich_with_resonance(text: str) -> str:
        """7D resonance ranking over 4127 Gita words → unique vocabulary context.

        Returns comma-separated English meanings of top-5 resonant words.
        Pure math (<80ms), no LLM, deterministic. Same input → same vocabulary.
        """
        if not text or len(text) < 10:
            return ""
        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate

            ranked = resonate(text[:200], top_n=5)
            if not ranked:
                return ""
            meanings: List[str] = []
            seen: set = set()
            for rw in ranked:
                m = rw.first_meaning
                if m and m.lower() not in seen:
                    seen.add(m.lower())
                    meanings.append(m)
            if meanings:
                return ", ".join(meanings)
        except Exception as e:
            logger.debug(f"Resonance enrichment skipped: {e}")
        return ""

    def _route_model(
        self,
        cognition: BuddhiResult,
        content_type: str,
        content_format: str,
    ) -> tuple:
        """Prana + integrity → model + token budget."""
        max_tokens = _FORMAT_TOKENS.get(content_format, _DEFAULT_TOKENS)
        model = None  # config default (deepseek-v3.2)

        # Reasoning model for substantive posts with healthy cells
        if (
            content_type == "post"
            and content_format in ("analysis", "opinion", "tutorial")
            and cognition.is_alive
            and cognition.integrity > 0.5
        ):
            model = "deepseek/deepseek-r1"
            max_tokens = int(max_tokens * 1.5)

        logger.info(f"Model routing: {content_type}/{content_format} → model={model or 'default'}")
        return model, max_tokens

    def _call_llm(
        self,
        system_msg: str,
        user_msg: str,
        model: Optional[str],
        max_tokens: int,
        content_type: str,
    ) -> Optional[str]:
        """Atomic LLM call with quota check."""
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider

            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception:
            return None

        # Quota check
        try:
            from vibe_core.runtime.quota_manager import OperationalQuota, QuotaExceededError

            quota = OperationalQuota()
            quota.check_before_request(
                estimated_tokens=max_tokens,
                operation=f"moltbook.{content_type}",
                model=model or "",
            )
        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded: {e}")
            return None
        except Exception as e:
            logger.warning(f"Quota check skipped: {e}")

        try:
            response = provider.invoke(
                prompt="",
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            if response and response.content and not response.content.startswith("# ERROR"):
                content = response.content.strip()
                actual_cost = 0.001
                if hasattr(response, "usage") and response.usage and hasattr(response.usage, "cost_usd"):
                    actual_cost = response.usage.cost_usd or 0.001
                try:
                    quota.record_request(
                        tokens_used=len(content.split()) + len(system_msg.split()),
                        cost_usd=actual_cost,
                        operation=f"moltbook.{content_type}",
                    )
                except Exception as e:
                    logger.warning(f"Quota record skipped: {e}")
                return content
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")

        return None

    @staticmethod
    def truncate_smart(text: str, limit: int) -> str:
        """Truncate to last sentence boundary within limit."""
        if len(text) <= limit:
            return text
        truncated = text[:limit]
        for sep in (". ", "! ", "? ", "; ", " — "):
            idx = truncated.rfind(sep)
            if idx > limit // 2:
                return truncated[: idx + 1].rstrip()
        idx = truncated.rfind(" ")
        if idx > limit // 2:
            return truncated[:idx].rstrip()
        return truncated[:limit]
