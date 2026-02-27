"""ContentComposer — deterministic pre-processing → atomic LLM call.

Extracted from AgencyDirector._compose_content() / _try_llm_compose().

1. MahaComposition (5 scorers) runs for backend analytics + resonant context
2. Pipeline data (guna→style, topic, reasoning) fills YAML template slots
3. Tier-based model routing: (content_type, format, integrity, prana) → model
4. Atomic LLM call: identity + style + topic + context → content
5. Code enforces: constitution, sravanam (in caller)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    PANCHA,
    TRINITY,
)

logger = logging.getLogger("MOLTBOOK_COMPOSER")

# Prana constant — imported lazily for cell system, defined here for tier math
_GENESIS_PRANA = 13700  # MAHA_QUANTUM * 100 (from cell.py)

# Content-type → YAML prompt key (PromptRegistry lookup)
_PROMPT_KEYS = {
    "comment": "moltbook.comment",
    "post": "moltbook.post",
    "dm_reply": "moltbook.dm_reply",
    "dm_request": "moltbook.dm_request",
}

_MOLTBOOK_YAML = (
    Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
)

# Format-driven token budget: the FORMAT decides how long the content should be.
# No hardcoded char limits — the LLM generates to the right length.
_FORMAT_TOKENS = {
    "question": 150,     # Sharp question + brief context
    "observation": 250,  # Concrete insight with examples
    "opinion": 350,      # Substantive argument with examples
    "analysis": 500,     # Deep breakdown
    "tutorial": 600,     # Step-by-step, needs space
}
_DEFAULT_TOKENS = 300

# =============================================================================
# TIER-BASED MODEL ROUTING — atomic per task, like an agency
# =============================================================================
# Tier 0 = Azubi (config default, cheapest)
# Tier 1 = Senior (same model, bigger token budget)
# Tier 2 = Chef (reasoning model, strategic content)

_TIER_MAP = {
    # Azubi tier — quick, simple tasks
    ("comment", "question"):    0,
    ("comment", "observation"): 0,
    ("dm_reply", None):         0,
    ("dm_request", None):       0,
    # Senior tier — substantive content
    ("comment", "analysis"):    1,
    ("comment", "opinion"):     1,
    ("post", "question"):       1,
    ("post", "observation"):    1,
    # Chef tier — strategic, high-investment
    ("post", "analysis"):       2,
    ("post", "opinion"):        2,
    ("post", "tutorial"):       2,
}

_TIER_MODELS = {
    0: None,                       # Config default (deepseek/deepseek-v3.2)
    1: None,                       # Same model, bigger budget
    2: "deepseek/deepseek-r1",     # Reasoning model for deep content
}

_TIER_NAMES = {0: "azubi", 1: "senior", 2: "chef"}


def _resolve_model_tier(
    content_type: str,
    content_format: str,
    integrity_cf: int = 0,
    prana: int = 0,
) -> Tuple[int, Optional[str]]:
    """(content_type, format, integrity, prana) → (tier, model_or_None).

    Atomic decision. Each task gets the right tool.
    Prana gates tier upgrades. Low prana = can't afford Chef.
    """
    # DMs use None format in lookup
    fmt = content_format if content_type not in ("dm_reply", "dm_request") else None
    base_tier = _TIER_MAP.get((content_type, fmt), 0)

    # Prana-based upgrade: high prana + high integrity → can afford pro model
    if base_tier < 2 and prana > _GENESIS_PRANA * 10 and integrity_cf > COSMIC_FRAME * TRINITY // PANCHA:
        base_tier = min(base_tier + 1, 2)

    # Prana-based downgrade: explicitly low prana → force cheap
    # prana=0 means "unknown" (chamber unavailable), NOT "low" — no downgrade
    if 0 < prana < _GENESIS_PRANA and base_tier > 0:
        base_tier = 0

    return base_tier, _TIER_MODELS.get(base_tier)

# (content_type, format) → task instruction for LLM
# Format-aware: questions vs analyses vs opinions produce different content.
# DMs don't need format diversity (conversational by nature).
_TASK_TEMPLATES = {
    ("post", "question"): "Ask a sharp technical question about: {input}. What's the unsolved problem?",
    ("post", "analysis"): "Analyze the technical tradeoffs of: {input}. Name specific tools or patterns. Compare approaches.",
    ("post", "opinion"): "Take a strong engineering stance on: {input}. Back it with concrete examples from real systems.",
    ("post", "observation"): "Share a non-obvious technical insight about: {input}. Be specific — what did you build or observe?",
    ("post", "tutorial"): "Write a practical how-to for: {input}. Include concrete steps, tools, and gotchas.",
    ("comment", "question"): "Ask the author one specific technical follow-up. What tradeoff or edge case did they miss?\nTOPIC: {input}",
    ("comment", "analysis"): "Add a concrete technical angle the author missed. Name a specific tool, pattern, or failure mode.\nTOPIC: {input}",
    ("comment", "opinion"): "Disagree or build on this with a specific technical counterpoint. Give a real-world example.\nTOPIC: {input}",
    ("comment", "observation"): "Point out a non-obvious connection or implication. Reference specific systems or patterns.\nTOPIC: {input}",
    ("dm_reply", None): "Reply to this message: {input}",
    ("dm_request", None): "Send a message about: {input}",
}

_YAML_LOADED = False


def _load_yaml_prompts() -> None:
    """Load Moltbook prompts from YAML (once)."""
    global _YAML_LOADED
    if _YAML_LOADED:
        return
    try:
        from vibe_core.runtime.prompt_registry import PromptRegistry

        loaded = PromptRegistry.load_from_yaml(_MOLTBOOK_YAML)
        if loaded:
            logger.info(f"Moltbook prompts loaded ({loaded})")
        _YAML_LOADED = True
    except Exception as e:
        logger.warning(f"YAML prompt load failed ({e})")
        _YAML_LOADED = True  # Don't retry on every cycle


def _build_task_message(
    content_type: str,
    input_text: str,
    knowledge: str = "",
    content_format: str = "",
    post_content: str = "",
) -> str:
    """Build atomic task message for LLM user role.

    Format-aware: (content_type, format) determines the instruction.
    For comments: includes the actual post text so LLM responds to real content.
    Includes KG domain context when available.
    """
    # Format-aware lookup: (content_type, format) → specific instruction
    template = _TASK_TEMPLATES.get((content_type, content_format))
    if not template:
        # Fallback: (content_type, None) for DMs, or generic
        template = _TASK_TEMPLATES.get((content_type, None), "Write about: {input}")
    msg = template.format(input=input_text[:300] if input_text else content_type)
    # For comments: include the actual post so LLM can respond to what the author wrote
    if post_content and content_type == "comment":
        msg += f"\n\nPOST:\n{post_content[:1500]}"
    if knowledge:
        msg += f"\n\nDomain context: {knowledge[:300]}"
    return msg


class ContentComposer:
    """Deterministic pre-processing → atomic LLM call.

    Owns: MahaComposition (backend analytics), PromptRegistry (YAML SSOT),
          LLM provider invocation, smart truncation.
    """

    def __init__(self, plugin=None):
        self._plugin = plugin

    def compose(
        self,
        pipeline_result: dict,
        input_text: str,
        content_type: str,
        input_ctx: Dict[str, Any],
        *,
        rasa_name: str = "",
        rasa_meaning: str = "",
        guna: str = "",
        style: str = "",
        resonance_zone: str = "",
        sravanam_status: str = "",
        integrity_cf: int = 0,
        prana: int = 0,
    ) -> Optional[str]:
        """Deterministic pre-processing → atomic LLM call.

        Returns content string on success, None on failure.
        NEVER returns empty string — None means "no content, don't post".

        1. MahaComposition (5 scorers) → resonant context for LLM (backend only)
        2. Pipeline data (guna→style, topic, reasoning) fills YAML template slots
        3. Tier-based model routing: (content_type, format, integrity, prana) → model
        4. Atomic LLM call: identity + style + topic + context → content
        5. Code enforces: constitution, sravanam (in caller)
        """
        _load_yaml_prompts()

        # Read current prana from Antaranga/Chamber (soft — 0 if unavailable)
        if prana == 0:
            try:
                from vibe_core.mahamantra.substrate.cell_system.chamber import get_chamber

                prana = get_chamber().antaranga.total_prana()
            except Exception as e:
                logger.warning(f"Antaranga prana lookup failed, using cheapest tier: {e}")

        engine_result = self._run_engine(input_text)

        # Step 1: MahaComposition — 5 scorers → resonant context for LLM
        composed_words = ""
        comp_ctx: Dict[str, Any] = {}
        try:
            from vibe_core.mahamantra.adapters.composition import get_composition

            composition = get_composition()
            composed_words = composition.compose(pipeline_result, input_text) or ""
            comp_ctx = composition.last_context
        except Exception as e:
            logger.warning(f"MahaComposition failed: {e}")

        # No fallback: if MahaComposition is empty, LLM gets no resonant context.
        # MahaComposition is backend analytics — never falls back to raw resonant words.

        # Step 2: Extract engine data for context
        guardian_name = ""
        guardian_function = "analysis"
        verse_ref = ""
        if engine_result:
            guardian_name = getattr(engine_result, "guardian_name", "") or ""
            guardian_function = getattr(engine_result, "guardian_function", "") or "analysis"
            verse_ref = getattr(engine_result, "verse_ref", "") or ""

        # Step 3: Agent identity
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        # Step 4: YAML template context — identity + style + topic + reasoning
        reasoning = input_ctx.get("strategic_reasoning", "")
        eng_ctx = input_ctx.get("engagement_context", "")
        if eng_ctx and reasoning:
            reasoning = f"{reasoning}. {eng_ctx}"
        elif eng_ctx:
            reasoning = eng_ctx

        knowledge_context = input_ctx.get("knowledge_context", "")

        # Content format flows from StrategyPlanner → input_ctx → prompt
        content_format = input_ctx.get("content_format", "observation")

        # Build resonant_context from scored words (not just chunk string)
        resonant_context = composed_words[:100] if composed_words else ""
        resonance_mode = ""
        if comp_ctx.get("top_scored"):
            top_words = [w["word"] for w in comp_ctx["top_scored"] if w.get("word")]
            if top_words:
                resonant_context = ", ".join(top_words[:5])
            # Dominant scorer → informs style hint
            avgs = comp_ctx.get("scorer_avgs", {})
            if avgs:
                dominant = max(avgs, key=lambda k: avgs[k])
                if avgs[dominant] > 0:
                    resonance_mode = dominant

        prompt_ctx = {
            "agent_name": agent_name,
            "topic": input_text[:200],
            "strategic_reasoning": reasoning,
            "submolt_context": input_ctx.get("submolt_context", ""),
            "style": style,
            "knowledge_context": knowledge_context,
            "content_format": content_format,
            "resonant_context": resonant_context,
            "resonance_mode": resonance_mode,
            "post_content": input_ctx.get("post_content", ""),
        }

        # Step 5: Task input (content-type-specific fragment)
        task_input = input_text
        if content_type == "comment":
            task_input = str(input_ctx.get("raw_input", input_text))[:200]
        elif content_type == "dm_reply":
            task_input = input_text[:200]
        else:
            task_input = str(input_ctx.get("trigger", input_text))[:200]

        # Step 6: Atomic LLM call (tier-routed)
        content = self._try_llm(prompt_ctx, task_input, content_type, integrity_cf=integrity_cf, prana=prana)
        if content:
            # Post-LLM hard gate: echo detection
            if task_input and len(task_input) > 20 and content.strip().lower().startswith(task_input.strip().lower()[:50]):
                logger.warning("LLM echoed input — rejecting")
                return None
            # Post-LLM hard gate: no substance (just punctuation/whitespace)
            alnum_words = [w for w in content.split() if any(c.isalnum() for c in w)]
            if len(alnum_words) < 3:
                logger.warning("LLM output has no substance — rejecting")
                return None
            # Clean up mid-sentence cuts from max_tokens limit
            if not content.rstrip().endswith((".", "!", "?", ":", "```")):
                content = self.truncate_smart(content, len(content))
            return content

        # No LLM = no content. Fail hard. No fallback to MahaComposition or kirtan.
        logger.warning("LLM unavailable — no content generated (fail-hard)")
        return None

    def _try_llm(
        self,
        prompt_ctx: Dict[str, str],
        task_input: str,
        content_type: str,
        *,
        integrity_cf: int = 0,
        prana: int = 0,
    ) -> Optional[str]:
        """LLM call with tier-based model routing.

        System message: identity + style + topic + context (from YAML SSOT).
        User message: atomic task ("Post about: ..." / "Reply to: ...").
        Model: resolved per-task via _resolve_model_tier().
        """
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider

            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception:
            return None

        # Fill YAML template — PromptRegistry is SSOT, no fallback
        prompt_key = _PROMPT_KEYS.get(content_type, "moltbook.post")
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            system_msg = PromptRegistry.get(prompt_key, context=prompt_ctx)
        except Exception as e:
            logger.error(f"PromptRegistry FAILED for {prompt_key}: {e}")
            return None

        if not system_msg:
            logger.error(f"PromptRegistry returned empty for {prompt_key} — cannot compose")
            return None

        # Atomic task message (format-aware, includes KG + post content for comments)
        content_format = prompt_ctx.get("content_format", "")
        user_msg = _build_task_message(
            content_type,
            task_input,
            prompt_ctx.get("knowledge_context", ""),
            content_format,
            post_content=prompt_ctx.get("post_content", ""),
        )

        # Token budget: FORMAT determines length, not content_type
        max_tokens = _FORMAT_TOKENS.get(content_format, _DEFAULT_TOKENS)

        # Tier-based model routing — atomic per task
        tier, model = _resolve_model_tier(content_type, content_format, integrity_cf, prana)

        # Post depth → tier boost: substantive posts deserve deeper responses
        post_content_len = len(prompt_ctx.get("post_content", ""))
        if content_type == "comment" and post_content_len > 800 and tier < 1:
            tier = 1
            model = _TIER_MODELS.get(tier)

        tier_name = _TIER_NAMES.get(tier, "unknown")
        logger.info(f"Tier routing: {content_type}/{content_format} → tier={tier_name} model={model or 'default'}")

        # Chef tier gets +50% token budget
        if tier >= 2:
            max_tokens = int(max_tokens * 1.5)

        # Quota check (model-aware)
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
                model=model,  # Tier-routed: None=default, or specific model
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            if response and response.content and not response.content.startswith("# ERROR"):
                content = response.content.strip()
                # Record actual cost from provider response
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
            logger.warning(f"LLM [{tier_name}]: {e}")

        return None

    def _run_pipeline(self, text: str) -> Optional[dict]:
        """Run Mahamantra VM pipeline → 27-key result."""
        if not text or not text.strip():
            return None
        try:
            from vibe_core.mahamantra import mahamantra

            return mahamantra(text)
        except Exception as e:
            logger.warning(f"Pipeline failed: {e}")
            return None

    def _run_engine(self, text: str):
        """Run MahaLanguageEngine → EngineResult."""
        try:
            from vibe_core.mahamantra.substrate.language.engine import generate

            return generate(text)
        except Exception as e:
            logger.warning(f"Engine failed: {e}")
            return None

    @staticmethod
    def truncate_smart(text: str, limit: int) -> str:
        """Truncate to last sentence boundary within limit."""
        if len(text) <= limit:
            return text
        truncated = text[:limit]
        # Find last sentence boundary
        for sep in (". ", "! ", "? ", "; ", " — "):
            idx = truncated.rfind(sep)
            if idx > limit // 2:
                return truncated[: idx + 1].rstrip()
        # No sentence boundary — cut at last space
        idx = truncated.rfind(" ")
        if idx > limit // 2:
            return truncated[:idx].rstrip()
        return truncated[:limit]
