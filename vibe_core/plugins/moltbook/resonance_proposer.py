"""
RESONANCE PROPOSER v3 — Content Intelligence Layer
=====================================================

Single path. No instructions in prompts.
System physics (guna/integrity/section mode) enforce quality.
LLM gets DENSE CONTEXT and assembles words.
No LLM = kirtan rendering via render(result).

The system IS the constraint:
    - Guna gate = TAMAS filter (destructive → skip)
    - Integrity gate = noise filter (low coherence → skip)
    - Section mode = rhetoric shaping (FILTER/VERB/QUALITY/CORE/...)
    - Dense context = semantic grounding (resonant/template/section/knowledge)

Quality comes from CONTEXT DENSITY, not from "please don't be sloppy".
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
    RankedWord,
    resonate,
)
from vibe_core.mahamantra.substrate.encoding.seed_to_words import (
    _GUARDIAN_CONFIGS,
)
from vibe_core.protocols.moltbook import MoltbookPost
from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentProposalProtocol,
    ContentType,
)

logger = logging.getLogger("MOLTBOOK.RESONANCE")

_GUNA_TAMAS = "TAMAS"
_GUNA_RAJAS = "RAJAS"
_GUNA_SATTVA = "SATTVA"

_INTEGRITY_THRESHOLD = 0.5
_ANALYSIS_GUARDIAN = "kapila"

_PROMPT_KEYS = {
    "dm_reply": "moltbook.dm_reply",
    "comment": "moltbook.comment",
    "post": "moltbook.post",
    "dm_request": "moltbook.dm_request",
}

_MOLTBOOK_YAML = Path(__file__).resolve().parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"


def _load_yaml_prompts() -> None:
    """Load Moltbook prompts from YAML."""
    try:
        from vibe_core.runtime.prompt_registry import PromptRegistry

        loaded = PromptRegistry.load_from_yaml(_MOLTBOOK_YAML)
        if loaded:
            logger.info(f"Moltbook prompts loaded ({loaded})")
    except Exception as e:
        logger.warning(f"YAML prompt load failed ({e})")


# =========================================================================
# Pipeline gates — deterministic, not instructional
# =========================================================================


def _guna_mode(result: dict) -> str:
    return result.get("guna", {}).get("mode", "")


def _is_tamas(result: dict) -> bool:
    return _guna_mode(result) == _GUNA_TAMAS


def _is_alive(result: dict) -> bool:
    return bool(result.get("cell", {}).get("is_alive"))


def _integrity(result: dict) -> float:
    return float(result.get("cell", {}).get("integrity", 0.0))


def _should_skip(result: dict) -> bool:
    return _is_tamas(result) or not _is_alive(result)


# =========================================================================
# Context builders — extract structured data from systems
# =========================================================================


def _format_resonant_words(engine_result) -> str:
    """EngineResult.resonant_words → structured context string."""
    if not engine_result.resonant_words:
        return ""
    return ", ".join(f"{s} ({m})" for s, m, _ in engine_result.resonant_words[:7])


def _format_template_words(engine_result) -> str:
    """EngineResult.template_words → grammatical skeleton string."""
    if not engine_result.template_words:
        return ""
    return ", ".join(f"{m} [{r}]" for _, m, r in engine_result.template_words[:7] if m)


def _section_data(engine_result) -> Dict[str, str]:
    """Section Router → semantic mode + element."""
    section = engine_result.section_name or ""
    mode = engine_result.section_mode or "CORE"
    try:
        from vibe_core.mahamantra.substrate.language.section_router import SECTION_SIGNATURES

        sig = SECTION_SIGNATURES.get(section, {})
        return {
            "section_name": section,
            "section_mode": mode,
            "section_semantic": str(sig.get("semantic", "")),
            "section_element": str(sig.get("element", "")),
        }
    except Exception:
        return {"section_name": section, "section_mode": mode, "section_semantic": "", "section_element": ""}


def _knowledge_context(topic: str) -> str:
    """KnowledgeResolver → graph-aware context."""
    try:
        from vibe_core.knowledge.resolver import get_resolver

        return get_resolver().compile_context(topic)
    except Exception:
        return ""


def _build_context(
    engine_result,
    agent_name: str,
    user_input: str,
    **extra: str,
) -> Dict[str, str]:
    """Build ALL context from ALL systems into one dict.

    This dict fills the YAML template slots. No instructions — just data.
    """
    guardian = engine_result.guardian_name.upper() if engine_result.guardian_name else "UNKNOWN"
    guardian_cfg = _GUARDIAN_CONFIGS.get(engine_result.guardian_name or "", {})
    section = _section_data(engine_result)

    return {
        "agent_name": agent_name,
        "guardian_name": guardian,
        "position": str(guardian_cfg.get("position", 0)),
        "quarter": engine_result.section_mode or "karma",
        "guardian_function": engine_result.guardian_function or "analysis",
        "engine_output": engine_result.output or "",
        "resonant_words": _format_resonant_words(engine_result),
        "template_words": _format_template_words(engine_result),
        "verse_ref": engine_result.verse_ref or "",
        "knowledge_context": _knowledge_context(user_input[:200]),
        "user_input": user_input,
        "derivation": engine_result.derivation or "",
        **section,
        **extra,
    }


# =========================================================================
# ResonanceProposer
# =========================================================================


class ResonanceProposer(ContentProposalProtocol):
    """
    Content Intelligence layer. System physics enforce quality.
    LLM gets dense context, assembles words.
    No LLM = kirtan rendering via render(result).
    """

    def __init__(
        self,
        agent_name: str = "steward-protocol",
        guardian: str = _ANALYSIS_GUARDIAN,
        top_n: int = 7,
    ):
        self._agent_name = agent_name
        self._guardian = guardian
        self._top_n = top_n
        self._llm = None
        self._llm_resolved = False

        if guardian not in _GUARDIAN_CONFIGS:
            raise ValueError(f"Unknown guardian: {guardian}. Valid: {list(_GUARDIAN_CONFIGS)}")

        _load_yaml_prompts()

    def _get_provider(self):
        """Lazy-resolve LLM Provider (the REAL LLM, not the template mock)."""
        if self._llm_resolved:
            return self._llm
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider

            provider = get_llm_provider()
            if provider and provider.is_available():
                self._llm = provider
            else:
                self._llm = None
        except Exception:
            self._llm = None
        self._llm_resolved = True
        return self._llm

    def _run_pipeline(self, text: str) -> Optional[dict]:
        """Mahamantra VM pipeline → 27-key result."""
        if not text or not text.strip():
            return None
        try:
            from vibe_core.mahamantra import mahamantra

            return mahamantra(text)
        except Exception as e:
            logger.warning(f"Pipeline failed: {e}")
            return None

    def _generate(self, text: str):
        """MahaLanguageEngine → EngineResult."""
        try:
            from vibe_core.mahamantra.substrate.language.engine import generate

            return generate(text)
        except Exception as e:
            logger.warning(f"Engine failed: {e}")
            return None

    def _compose(
        self,
        prompt_key: str,
        engine_result,
        user_input: str,
        pipeline_result: Optional[dict] = None,
        **extra: str,
    ) -> Optional[str]:
        """Context → YAML template → LLM → content. No LLM = kirtan rendering."""
        ctx = _build_context(engine_result, self._agent_name, user_input, **extra)

        # Fill YAML template with context
        prompt = ""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            prompt = PromptRegistry.get(prompt_key, context=ctx)
        except Exception:
            pass

        if not prompt:
            prompt = (
                f"{ctx['guardian_name']} · {ctx['quarter']} · {ctx['guardian_function']}\n"
                f"Sektion: {ctx['section_name']} ({ctx['section_semantic']})\n"
                f"Vers: {ctx['verse_ref']}\n"
                f"RESONANZ: {ctx['resonant_words']}\n"
                f"ANALYSE: {ctx['engine_output']}\n"
                f"{ctx['knowledge_context']}\n"
                f"INPUT: {user_input}\n"
            )

        # Try real LLM provider (NOT the template mock LLMEngine.speak())
        provider = self._get_provider()
        if provider:
            try:
                response = provider.invoke(
                    prompt=prompt,
                    model=provider.get_available_models()[0] if provider.get_available_models() else None,
                    max_tokens=512,
                    temperature=0.7,
                )
                if response and response.content and not response.content.startswith("# ERROR"):
                    return response.content.strip()
            except Exception as e:
                logger.warning(f"LLM provider failed: {e}")

        # Fallback: kirtan rendering (the system's tongue without enrichment)
        if pipeline_result:
            try:
                from vibe_core.mahamantra.render import render

                return render(pipeline_result)
            except Exception:
                pass

        return None

    # =========================================================================
    # ContentProposalProtocol
    # =========================================================================

    def analyze(self, text: str) -> List[RankedWord]:
        try:
            return resonate(text, top_n=self._top_n)
        except Exception:
            return []

    def propose_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict[str, object]] = None,
    ) -> Optional[ContentProposal]:
        result = self._run_pipeline(inbound_content)
        if result and _is_tamas(result):
            return None

        engine_result = self._generate(inbound_content)
        if not engine_result:
            return None

        reply = self._compose(
            _PROMPT_KEYS["dm_reply"],
            engine_result,
            inbound_content,
            pipeline_result=result,
            sender=sender,
        )
        if not reply:
            return None

        gw = gateway_response or {}
        return ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content=reply[:280],
            conversation_id=conversation_id,
            source="inbound_dm",
            sender=sender,
            priority=1,
            gateway_success=bool(gw.get("success")),
            gateway_position=gw.get("position", -1),
            gateway_guardian=gw.get("guardian", "unknown"),
            gateway_guna=gw.get("guna", "sattva"),
        )

    def propose_dm_request_action(
        self,
        request_id: str,
        from_agent: str,
        message_preview: str,
    ) -> Optional[ContentProposal]:
        result = self._run_pipeline(f"{from_agent} {message_preview}")
        if result and _should_skip(result):
            return None

        return ContentProposal(
            content_type=ContentType.DM_INITIATE.value,
            content="",
            to_agent=from_agent,
            source="dm_request_pipeline",
            sender=from_agent,
            priority=1,
        )

    def propose_post(
        self,
        trigger: str,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[ContentProposal]:
        seed_text = trigger
        ctx = context or {}
        feed_topics: List[str] = ctx.get("feed_topics", [])
        if feed_topics:
            seed_text = f"{trigger}: {', '.join(str(t) for t in feed_topics[:3])}"

        result = self._run_pipeline(seed_text)
        if not result or _should_skip(result):
            return None
        if _guna_mode(result) != _GUNA_RAJAS:
            return None
        if _integrity(result) < _INTEGRITY_THRESHOLD:
            return None

        engine_result = self._generate(seed_text)
        if not engine_result:
            return None

        post_text = self._compose(
            _PROMPT_KEYS["post"],
            engine_result,
            seed_text,
            pipeline_result=result,
            trigger=trigger,
        )
        if not post_text:
            return None

        lines = post_text.strip().split("\n", 1)
        title = lines[0].strip().lstrip("#").strip()[:120]
        content = lines[1].strip() if len(lines) > 1 else post_text

        return ContentProposal(
            content_type=ContentType.POST.value,
            title=title,
            content=content[:500],
            source=trigger,
            priority=1,
        )

    def propose_comment(
        self,
        post_id: str,
        post_content: str,
        trigger: str,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[ContentProposal]:
        result = self._run_pipeline(post_content)
        if not result or _should_skip(result):
            return None
        if _integrity(result) < _INTEGRITY_THRESHOLD:
            return None

        engine_result = self._generate(post_content)
        if not engine_result:
            return None

        comment = self._compose(
            _PROMPT_KEYS["comment"],
            engine_result,
            post_content[:200],
            pipeline_result=result,
            post_content=post_content[:500],
        )
        if not comment:
            return None

        return ContentProposal(
            content_type=ContentType.COMMENT.value,
            content=comment[:280],
            post_id=post_id,
            source=trigger,
            priority=1,
        )

    def should_engage(
        self,
        post_id: str,
        post_content: str,
        author: str,
    ) -> Optional[ContentProposal]:
        result = self._run_pipeline(post_content)
        if not result or _should_skip(result):
            return None

        return ContentProposal(
            content_type=ContentType.VOTE.value,
            post_id=post_id,
            source="pipeline_engagement",
            priority=0,
        )

    def analyze_feed(
        self,
        posts: Sequence[MoltbookPost],
    ) -> List[Tuple[MoltbookPost, List[RankedWord], float]]:
        scored: List[Tuple[MoltbookPost, List[RankedWord], float]] = []
        for post in posts:
            content = post.get("content", post.get("title", ""))
            if not content:
                continue
            text = str(content)
            result = self._run_pipeline(text)
            if result and _should_skip(result):
                continue
            ranked = self.analyze(text)
            score = ranked[0].total_score if ranked else 0.0
            scored.append((post, ranked, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        return scored


__all__ = ["ResonanceProposer"]
