"""ContentComposer — BuddhiResult-driven content generation.

MahaBuddhi does the thinking. Composer does the talking.

No hardcoded instruction templates. System message is built entirely from
computed BuddhiResult signals: chapter, perspective, focus, mode, function,
vibration element, verse concepts. Task message = action + content + resonance.

1. BuddhiResult → computed cognitive system message
2. Content + resonance context → task message
3. Prana/integrity → model routing (reasoning model for substantive posts)
4. Atomic LLM call
5. Post-LLM validation (echo, substance)
"""

import logging
from typing import Any, Dict, Optional

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

# No hardcoded instruction templates.
# System message built entirely from BuddhiResult computed signals.
# Task message = action verb + content + resonance context.


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
        """Build system message from computed BuddhiResult signals.

        No hardcoded instruction templates. Every line except the agent name
        and anti-slop rules is derived from Mahamantra pipeline output.
        """
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        parts = [f"You are {agent_name}."]

        # Cognitive frame — computed by MahaBuddhi from input text
        parts.append(
            f"Chapter {cognition.chapter}: {cognition.perspective}"
        )
        parts.append(
            f"Phase: {cognition.focus} | Mode: {cognition.mode} | "
            f"Function: {cognition.function}"
        )

        # Vibration signature — from Mantra VM phonetic encoding
        vib = cognition.vm_result.get("vibration", {})
        sig = vib.get("signature", {}) if isinstance(vib, dict) else {}
        element = sig.get("element", "")
        if element:
            parts.append(f"Element: {element}")

        # Verse concepts — matched Gita wisdom (Sanskrit + meaning)
        if cognition.verse_concepts:
            meanings = [
                vc.get("meaning", "")
                for vc in cognition.verse_concepts[:5]
                if vc.get("meaning")
            ]
            if meanings:
                parts.append(f"Verse concepts: {', '.join(meanings)}")

        # Strategic context (from strategy planner — WHY this topic, for whom)
        reasoning = input_ctx.get("strategic_reasoning", "")
        eng_ctx = input_ctx.get("engagement_context", "")
        if eng_ctx and reasoning:
            reasoning = f"{reasoning}. {eng_ctx}"
        elif eng_ctx:
            reasoning = eng_ctx
        if reasoning:
            parts.append(f"Context: {reasoning[:500]}")

        # Submolt context — WHERE this content goes
        submolt_ctx = input_ctx.get("submolt_context", "")
        if submolt_ctx:
            parts.append(f"Community: {submolt_ctx[:300]}")

        # Rasa — aesthetic mood (from VedicScaleMapping, computed from integrity)
        rasa = input_ctx.get("rasa", "")
        if rasa:
            parts.append(f"Rasa: {rasa}")

        # Anti-slop (universal — not content-specific)
        parts.append(
            "RULES: No AI filler. No 'as an AI'. No 'let me break this down'. "
            "No 'it's important to note'. No meta-commentary. "
            "Be specific — name real tools, systems, patterns."
        )

        return "\n".join(parts)

    def _build_task(
        self,
        cognition: BuddhiResult,
        content_type: str,
        input_text: str,
        input_ctx: Dict[str, Any],
    ) -> str:
        """Build task message — action + content + resonance context.

        No format-keyed instruction templates. The cognitive frame in the
        system message tells the LLM HOW to think. This message tells it
        WHAT to respond to and provides resonance vocabulary.
        """
        if content_type == "comment":
            task_input = str(input_ctx.get("raw_input", input_text))[:300]
            parts = [f"Respond to this post about: {task_input}"]
        elif content_type == "dm_reply":
            parts = [f"Reply to this message: {input_text[:300]}"]
        elif content_type == "dm_request":
            parts = [f"Send a message about: {input_text[:300]}"]
        else:
            parts = [f"Write about: {input_text[:300] if input_text else content_type}"]

        # Post content for comments — the LLM needs the actual post
        post_content = input_ctx.get("post_content", "")
        if post_content and content_type == "comment":
            parts.append(f"\nPOST:\n{post_content[:1500]}")

        # Resonance vocabulary with dimension breakdown
        resonance_ctx = self._build_resonance_context(input_text)
        if resonance_ctx:
            parts.append(f"\n{resonance_ctx}")
        elif cognition.composed:
            parts.append(f"\nRESONANT CONCEPTS: {cognition.composed}")

        # Knowledge context — full domain knowledge from Knowledge Graph
        # The KG returns structured context (nodes, deps, constraints, scores).
        # Previous limit of 300 chars used <2% of available knowledge.
        knowledge = input_ctx.get("knowledge_context", "")
        if knowledge:
            parts.append(f"\nDOMAIN KNOWLEDGE:\n{knowledge[:2000]}")

        return "\n".join(parts)

    @staticmethod
    def _build_resonance_context(text: str) -> str:
        """7D resonance ranking → structured vocabulary with dimension scores.

        Shows WHY each word resonates (which of 7 dimensions scored highest),
        not just what it means. Pure math (<80ms), deterministic.
        """
        if not text or len(text) < 10:
            return ""
        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate

            ranked = resonate(text[:200], top_n=5)
            if not ranked:
                return ""
            lines = ["RESONANCE:"]
            seen: set = set()
            for rw in ranked:
                m = rw.first_meaning
                if not m or m.lower() in seen:
                    continue
                seen.add(m.lower())
                # Top-scoring dimension shows WHY this word resonates
                breakdown = rw.score_breakdown()
                # Skip 'total' key, find max scoring dimension
                dims = {k: v for k, v in breakdown.items() if k != "total"}
                top_dim = max(dims, key=dims.get) if dims else ""
                lines.append(
                    f"- {rw.sanskrit} ({m}) — {rw.total_score:.2f} [{top_dim}]"
                )
            return "\n".join(lines) if len(lines) > 1 else ""
        except Exception as e:
            logger.debug(f"Resonance context skipped: {e}")
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
