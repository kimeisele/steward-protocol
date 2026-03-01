"""ContentComposer — PromptRegistry + BuddhiResult-driven content generation.

MahaBuddhi does the thinking. PromptRegistry provides the template. Composer wires them.

1. YAML template (config/prompts/moltbook.yaml) → PromptRegistry.get() → system base
2. BuddhiResult cognitive signals → appended to system message (dynamic per call)
3. Content + resonance context → task message
4. Prana/integrity → model routing (reasoning model for substantive posts)
5. Atomic LLM call
6. Post-LLM validation (echo, substance)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from vibe_core.mahamantra.protocols._buddhi import BuddhiResult

logger = logging.getLogger("MOLTBOOK_COMPOSER")

# Prana threshold for reasoning model upgrade
_GENESIS_PRANA = 13700

# Format-driven token budget — enough room to finish the thought
_FORMAT_TOKENS = {
    "question": 200,
    "observation": 350,
    "opinion": 450,
    "analysis": 600,
    "tutorial": 750,
}
_DEFAULT_TOKENS = 400


class ContentComposer:
    """PromptRegistry + BuddhiResult-driven content generation.

    YAML template (PromptRegistry) provides identity, rules, and template slots.
    MahaBuddhi.think() produces cognition → cognitive signals appended to template.
    Context builders fill template slots (resonance, engagement, guardian voice).
    """

    def __init__(self, plugin=None):
        self._plugin = plugin
        self._load_prompts()

    @staticmethod
    def _load_prompts():
        """Load moltbook prompt templates from YAML into PromptRegistry."""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            PromptRegistry.load_from_yaml(Path(__file__).parents[5] / "config" / "prompts" / "moltbook.yaml")
        except Exception as e:
            logger.warning(f"Prompt YAML load failed: {e}")

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

        # 4. LLM call (temperature from cognitive integrity)
        temperature = self._compute_temperature(cognition)
        content = self._call_llm(system_msg, user_msg, model, max_tokens, content_type, temperature)
        if content:
            # Post-LLM: echo detection
            task_input = input_text[:200]
            if (
                task_input
                and len(task_input) > 20
                and content.strip().lower().startswith(task_input.strip().lower()[:50])
            ):
                logger.warning("LLM echoed input — rejecting")
                return None
            # Post-LLM: substance check
            alnum_words = [w for w in content.split() if any(c.isalnum() for c in w)]
            if len(alnum_words) < 3:
                logger.warning("LLM output has no substance — rejecting")
                return None
            # Post-LLM: topic overlap (mechanical — keyword Jaccard)
            # For comments: verify against post_content (what the LLM actually sees),
            # not input_text (which is just the post title — keyword mismatch expected)
            overlap_ref = input_text
            if content_type == "comment":
                post_body = input_ctx.get("post_content", "")
                if post_body and len(post_body) > 30:
                    overlap_ref = post_body
            if not self._verify_topic_overlap(content, overlap_ref):
                logger.warning("Topic drift detected — rejecting")
                return None
            # Clean mid-sentence cuts
            if not content.rstrip().endswith((".", "!", "?", ":", "```")):
                content = self.truncate_smart(content, len(content))
            return content

        logger.warning("LLM unavailable — no content generated (fail-hard)")
        return None

    def _build_system(self, cognition: BuddhiResult, input_ctx: Dict[str, Any]) -> str:
        """Build system message: PromptRegistry template + cognitive signals."""
        content_type = input_ctx.get("content_type", "comment")
        prompt_key = f"moltbook.{content_type}"

        # Fill ALL template slots
        context = self._build_template_context(cognition, input_ctx)

        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            base = PromptRegistry.get(prompt_key, context=context)
        except Exception:
            # Fallback: minimal inline (should never happen if YAML loaded)
            base = f"You are {context['agent_name']}. Style: {context['style']}."

        # Append cognitive signals from BuddhiResult (not in YAML — dynamic)
        cognitive_parts = []
        cognitive_parts.append(f"Chapter {cognition.chapter}: {cognition.perspective}")
        cognitive_parts.append(f"Phase: {cognition.focus} | Function: {cognition.function}")
        # Verse concepts (English only)
        if cognition.verse_concepts:
            meanings = [vc.get("meaning", "") for vc in cognition.verse_concepts[:3] if vc.get("meaning")]
            if meanings:
                cognitive_parts.append(f"Concepts: {', '.join(meanings)}")
        # Guardian voice
        from vibe_core.cartridges.agent_city.moltbook.core.context_builders import guardian_vocabulary_short

        vib = cognition.vm_result.get("vibration", {})
        sig = vib.get("signature", {}) if isinstance(vib, dict) else {}
        element = sig.get("element", "")
        if element:
            cognitive_parts.append(f"Element: {element}")
        guardian = str(cognition.vm_result.get("guardian", ""))
        voice = guardian_vocabulary_short(guardian)
        if voice:
            # Filter noise fragments (prepositions, decontextualized Gita phrases)
            _NOISE = frozenset({"unto", "causing", "thereof", "therein", "wherein"})
            fragments = [f.strip() for f in voice.split(",")]
            clean = [f for f in fragments if not any(n in f.lower() for n in _NOISE) and len(f.split()) <= 4]
            if clean:
                cognitive_parts.append(f"Voice: {', '.join(clean[:3])}")
        # Rasa
        rasa = input_ctx.get("rasa", "")
        if rasa:
            cognitive_parts.append(f"Rasa: {rasa}")

        return base + "\n" + "\n".join(cognitive_parts)

    def _build_template_context(self, cognition: BuddhiResult, input_ctx: Dict[str, Any]) -> dict:
        """Build context dict for PromptRegistry template slot interpolation."""
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        # Guna → style
        guna = cognition.mode
        style = {"SATTVA": "contemplative", "RAJAS": "active", "TAMAS": "transformative"}.get(guna, "active")

        # Content format from buddhi mode
        content_format = input_ctx.get("content_format", "observation")

        # Resonance context (English only — no Sanskrit)
        resonant_context = self._build_resonance_context(input_ctx.get("raw_input", ""))
        # Strip "RESONANCE:" header — template already provides context label
        if resonant_context.startswith("RESONANCE:"):
            resonant_context = resonant_context[len("RESONANCE:") :].strip()

        # Dominant resonance mode
        resonance_mode = self._get_dominant_resonance_mode(input_ctx.get("raw_input", ""))

        # Strategic reasoning (from strategy planner)
        reasoning = input_ctx.get("strategic_reasoning", "")
        eng_ctx = input_ctx.get("engagement_context", "")
        if eng_ctx and reasoning:
            reasoning = f"{reasoning}. {eng_ctx}"
        elif eng_ctx:
            reasoning = eng_ctx
        # Enrich with FeedbackProtocol stats
        from vibe_core.cartridges.agent_city.moltbook.core.context_builders import engagement_context

        feedback_stats = engagement_context()
        if feedback_stats:
            reasoning = f"{reasoning}. {feedback_stats}" if reasoning else feedback_stats

        return {
            "agent_name": agent_name,
            "style": style,
            "content_format": content_format,
            "topic": input_ctx.get("raw_input", "")[:200],
            "strategic_reasoning": reasoning[:500],
            "resonant_context": resonant_context,
            "resonance_mode": resonance_mode,
            "submolt_context": input_ctx.get("submolt_context", "")[:300],
        }

    @staticmethod
    def _get_dominant_resonance_mode(text: str) -> str:
        """Get the dominant resonance scorer name for the input text."""
        if not text or len(text) < 10:
            return ""
        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate

            ranked = resonate(text[:200], top_n=1)
            if ranked:
                breakdown = ranked[0].score_breakdown()
                dims = {k: v for k, v in breakdown.items() if k != "total"}
                return max(dims, key=dims.get) if dims else ""
        except Exception:
            pass
        return ""

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

        # Resonance vocabulary — English meanings only (no Sanskrit in LLM prompt)
        resonance_ctx = self._build_resonance_context(input_text)
        if resonance_ctx:
            parts.append(f"\n{resonance_ctx}")
        # cognition.composed contains Sanskrit words — DO NOT inject into prompt.
        # The LLM reproduces these in titles ("viparītān", "śāśvat") = garbage output.

        # Knowledge context — full domain knowledge from Knowledge Graph
        # The KG returns structured context (nodes, deps, constraints, scores).
        # Previous limit of 300 chars used <2% of available knowledge.
        knowledge = input_ctx.get("knowledge_context", "")
        if knowledge:
            parts.append(f"\nDOMAIN KNOWLEDGE:\n{knowledge[:2000]}")

        # Web research — real-world facts from Tavily web search
        # Ground truth prevents hallucination and makes content substantive.
        web_research = input_ctx.get("web_research", "")
        if web_research:
            parts.append(f"\nCURRENT FACTS:\n{web_research[:2000]}")

        return "\n".join(parts)

    @staticmethod
    def _build_resonance_context(text: str) -> str:
        """7D resonance ranking → English meanings with dimension scores.

        Shows WHY each concept resonates (which of 7 dimensions scored highest).
        Pure math (<80ms), deterministic.

        CRITICAL: Only English meanings. No Sanskrit in LLM prompt — the LLM
        reproduces Sanskrit tokens in output titles, which looks like garbage.
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
                breakdown = rw.score_breakdown()
                dims = {k: v for k, v in breakdown.items() if k != "total"}
                top_dim = max(dims, key=dims.get) if dims else ""
                # English meaning ONLY — no rw.sanskrit
                lines.append(f"- {m} — {rw.total_score:.2f} [{top_dim}]")
            return "\n".join(lines) if len(lines) > 1 else ""
        except Exception as e:
            logger.warning(f"Resonance context failed: {e}")
        return ""

    @staticmethod
    def _compute_temperature(cognition: BuddhiResult) -> float:
        """Integrity-driven temperature — high integrity = precise, low = exploratory."""
        if cognition.integrity > 0.7:
            return 0.3  # High confidence → precise, focused
        if cognition.integrity > 0.4:
            return 0.45  # Medium → balanced
        return 0.6  # Low → slightly more creative (but not 0.7 wild)

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
            and cognition.integrity > 0.3
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
        temperature: float = 0.45,
    ) -> Optional[str]:
        """Atomic LLM call with quota check."""
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider

            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception as e:
            logger.warning(f"LLM provider unavailable: {e}")
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
                temperature=temperature,
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
    def _verify_topic_overlap(output: str, input_text: str) -> bool:
        """Mechanical check: output keywords overlap with input topic.

        Uses keyword Jaccard from text_utils. Threshold: 0.10.
        If input is too short to tokenize, passes through.
        """
        if not input_text or len(input_text.strip()) < 15:
            return True  # Too short to verify meaningfully
        try:
            from vibe_core.cartridges.agent_city.moltbook.core.text_utils import keyword_jaccard

            score = keyword_jaccard(input_text, output)
            if score < 0.10:
                logger.warning(f"Topic overlap Jaccard={score:.2f} (threshold=0.10)")
                return False
            return True
        except Exception as e:
            logger.warning(f"Topic overlap check failed: {e}")
            return True  # Can't verify, pass through

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
