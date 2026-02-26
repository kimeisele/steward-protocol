"""ContentComposer — deterministic pre-processing → atomic LLM call.

Extracted from AgencyDirector._compose_content() / _try_llm_compose().

1. MahaComposition (5 scorers) runs for backend analytics (NOT injected into prompt)
2. Pipeline data (guna→style, topic, reasoning) fills YAML template slots
3. Atomic LLM call: identity + style + topic + context → content
4. Code enforces: char limits, constitution, sravanam (in caller)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("MOLTBOOK_COMPOSER")

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

# Content-type → atomic task (user message for LLM)
_TASK_TEMPLATES = {
    "post": "Write an original post about: {input}",
    "dm_reply": "Reply to this message: {input}",
    "comment": "Write a comment responding to: {input}",
    "dm_request": "Send a message about: {input}",
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


def _build_task_message(content_type: str, input_text: str, knowledge: str = "") -> str:
    """Build atomic task message for LLM user role.

    Includes KG domain context when available — gives the LLM real knowledge
    beyond just the topic name.
    """
    template = _TASK_TEMPLATES.get(content_type, "Write about: {input}")
    msg = template.format(input=input_text[:200] if input_text else content_type)
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
    ) -> str:
        """Deterministic pre-processing → atomic LLM call.

        1. MahaComposition (5 scorers) runs for backend analytics (NOT injected into prompt)
        2. Pipeline data (guna→style, topic, reasoning) fills YAML template slots
        3. Atomic LLM call: identity + style + topic + context → content
        4. Code enforces: char limits, constitution, sravanam (in caller)
        """
        _load_yaml_prompts()

        engine_result = self._run_engine(input_text)

        # Step 1: MahaComposition — deterministic English (5 scorers)
        composed_words = ""
        try:
            from vibe_core.mahamantra.adapters.composition import get_composition

            composed_words = get_composition().compose(pipeline_result, input_text) or ""
        except Exception as e:
            logger.warning(f"MahaComposition failed: {e}")

        # Fallback: resonant words from engine if composition empty
        if not composed_words and engine_result:
            words = getattr(engine_result, "resonant_words", ()) or ()
            composed_words = ", ".join(m for _, m, _ in words[:5])

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

        prompt_ctx = {
            "agent_name": agent_name,
            "topic": input_text[:200],
            "strategic_reasoning": reasoning,
            "submolt_context": input_ctx.get("submolt_context", ""),
            "style": style,
            "knowledge_context": knowledge_context,
        }

        # Step 5: Task input (content-type-specific fragment)
        task_input = input_text
        if content_type == "comment":
            task_input = str(input_ctx.get("raw_input", input_text))[:200]
        elif content_type == "dm_reply":
            task_input = input_text[:200]
        else:
            task_input = str(input_ctx.get("trigger", input_text))[:200]

        # Step 6: Atomic LLM call
        content = self._try_llm(prompt_ctx, task_input, content_type)
        if content:
            return content

        # No LLM = no content. Not word salad. Not kirtan dump.
        logger.warning("LLM unavailable — no content generated")
        return ""

    def _try_llm(
        self,
        prompt_ctx: Dict[str, str],
        task_input: str,
        content_type: str,
    ) -> Optional[str]:
        """LLM call. System = YAML template (PromptRegistry SSOT). User = task + input.

        System message: identity + style + topic + context (from YAML v12).
        User message: atomic task ("Post about: ..." / "Reply to: ...").
        No fallback. PromptRegistry is the single path.
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

        # Atomic task message (includes KG domain context when available)
        user_msg = _build_task_message(content_type, task_input, prompt_ctx.get("knowledge_context", ""))

        # Quota check
        try:
            from vibe_core.runtime.quota_manager import OperationalQuota, QuotaExceededError

            quota = OperationalQuota()
            quota.check_before_request(estimated_tokens=128, operation=f"moltbook.{content_type}")
        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded: {e}")
            return None
        except Exception as e:
            logger.debug(f"Quota check skipped: {e}")

        try:
            response = provider.invoke(
                prompt="",
                model=None,  # Config default (deepseek/deepseek-v3.2)
                max_tokens=128,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            if response and response.content and not response.content.startswith("# ERROR"):
                content = response.content.strip()
                try:
                    quota.record_request(
                        tokens_used=len(content.split()) + len(system_msg.split()),
                        cost_usd=0.001,
                        operation=f"moltbook.{content_type}",
                    )
                except Exception as e:
                    logger.debug(f"Quota record skipped: {e}")
                return content
        except Exception as e:
            logger.warning(f"LLM: {e}")

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
