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

from vibe_core.cartridges.agent_city.moltbook.core.context_builders import (
    guardian_vocabulary_short,
)
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

# Content-type → atomic task (user message for LLM)
_TASK_TEMPLATES = {
    "dm_reply": "Reply to: {input}",
    "comment": "Comment on: {input}",
    "post": "Post about: {input}",
    "dm_request": "Message: {input}",
}


def _build_task_message(prompt_key: str, input_text: str) -> str:
    """Build atomic task message for LLM user role."""
    # Extract content type from prompt key (e.g., "moltbook.dm_reply" → "dm_reply")
    ct = prompt_key.rsplit(".", 1)[-1] if "." in prompt_key else prompt_key
    template = _TASK_TEMPLATES.get(ct, "Write about: {input}")
    return template.format(input=input_text[:200] if input_text else "")

# Knowledge Graph node IDs → ContentType mapping (knowledge/moltbook/platform.yaml)
_KG_CONTENT_TYPE_NODES = {
    ContentType.DM_REPLY.value: "moltbook_dm",
    ContentType.DM_INITIATE.value: "moltbook_dm_request",
    ContentType.POST.value: "moltbook_post",
    ContentType.COMMENT.value: "moltbook_comment",
    ContentType.VOTE.value: "moltbook_vote",
}


def _kg_priority(content_type: str) -> int:
    """Get priority from Knowledge Graph metrics (knowledge/moltbook/platform.yaml).

    Falls back to 1 if KG unavailable. This replaces hardcoded priority=1
    with the graph-defined priorities: DM=9, Post=7, Comment=6, Vote=4.
    """
    node_id = _KG_CONTENT_TYPE_NODES.get(content_type)
    if not node_id:
        return 1
    try:
        from vibe_core.knowledge.resolver import get_resolver
        from vibe_core.knowledge.schema import MetricType

        resolver = get_resolver()
        priority = resolver.graph.get_metric(node_id, MetricType.PRIORITY)
        return int(priority) if priority else 1
    except Exception:
        return 1


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
# Context builders — delegated to shared module (context_builders.py)
# =========================================================================
# build_moltbook_context imported at top from core.context_builders


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
        # Per-heartbeat cache: avoid running pipeline/engine twice for same text
        self._pipeline_cache: Dict[str, Optional[dict]] = {}
        self._engine_cache: Dict[str, object] = {}
        self._cache_max = 32  # Max cached entries before flush

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
                logger.info("LLM provider resolved — intelligent content generation active")
            else:
                self._llm = None
                logger.warning(
                    "No LLM provider available — content generation uses kirtan rendering only. "
                    "Configure an LLM provider for richer output."
                )
        except Exception as e:
            self._llm = None
            logger.warning(f"LLM provider resolution failed: {e} — using kirtan fallback")
        self._llm_resolved = True
        return self._llm

    def _run_pipeline(self, text: str) -> Optional[dict]:
        """Mahamantra VM pipeline → 27-key result. Cached per text."""
        if not text or not text.strip():
            return None
        if text in self._pipeline_cache:
            return self._pipeline_cache[text]
        try:
            from vibe_core.mahamantra import mahamantra

            result = mahamantra(text)
            if len(self._pipeline_cache) >= self._cache_max:
                self._pipeline_cache.clear()
            self._pipeline_cache[text] = result
            return result
        except Exception as e:
            logger.warning(f"Pipeline failed: {e}")
            return None

    def _generate(self, text: str):
        """MahaLanguageEngine → EngineResult. Cached per text."""
        if text in self._engine_cache:
            return self._engine_cache[text]
        try:
            from vibe_core.mahamantra.substrate.language.engine import generate

            result = generate(text)
            if len(self._engine_cache) >= self._cache_max:
                self._engine_cache.clear()
            self._engine_cache[text] = result
            return result
        except Exception as e:
            logger.warning(f"Engine failed: {e}")
            return None

    def flush_cache(self) -> None:
        """Clear pipeline/engine caches. Call between heartbeats."""
        self._pipeline_cache.clear()
        self._engine_cache.clear()

    def _compose(
        self,
        prompt_key: str,
        engine_result,
        user_input: str,
        pipeline_result: Optional[dict] = None,
        **extra: str,
    ) -> Optional[str]:
        """Deterministic pre-processing → atomic LLM → fallback chain.

        1. MahaComposition (5 scorers) → deterministic English (standalone-quality)
        2. Resonant words from engine → vocabulary hint (LLM-only, not standalone)
        3. If LLM: atomic prompt (identity + words) → natural language
        4. If no LLM: MahaComposition output directly (already English)
        5. Last resort: kirtan rendering

        MahaComposition runs BEFORE LLM (pre-processing), not after (fallback).
        """
        # Step 1: MahaComposition — deterministic English (standalone-quality)
        composed = ""
        if pipeline_result:
            try:
                from vibe_core.mahamantra.adapters.composition import MahaComposition

                composer = MahaComposition()
                composed = composer.compose(pipeline_result, user_input) or ""
            except Exception as e:
                logger.debug(f"MahaComposition: {e}")

        # Vocabulary hint: composed words OR resonant words (for LLM input)
        # Resonant words are raw meanings — only useful as LLM input, not standalone
        vocab = composed
        if not vocab and engine_result:
            words = getattr(engine_result, "resonant_words", ()) or ()
            vocab = ", ".join(m for _, m, _ in words[:5])

        # Step 2: Guardian voice
        guardian_name = getattr(engine_result, "guardian_name", "") or "" if engine_result else ""
        guardian_function = getattr(engine_result, "guardian_function", "") or "analysis" if engine_result else "analysis"
        voice = guardian_vocabulary_short(guardian_name)

        # Step 3: Atomic prompt context
        prompt_ctx = {
            "agent_name": self._agent_name,
            "guardian_name": guardian_name.upper() if guardian_name else "KAPILA",
            "guardian_function": guardian_function,
            "composed_words": vocab,
            "voice": voice,
        }

        # Step 4: Try LLM with atomic prompt
        provider = self._get_provider()
        if provider and vocab:
            system_msg = ""
            try:
                from vibe_core.runtime.prompt_registry import PromptRegistry

                system_msg = PromptRegistry.get(prompt_key, context=prompt_ctx)
            except Exception as e:
                logger.warning(f"PromptRegistry: {e}")

            if not system_msg:
                system_msg = (
                    f"{self._agent_name} · {prompt_ctx['guardian_name']}\n"
                    f"Words: {vocab}\n"
                    f"Voice: {voice}"
                )

            user_msg = _build_task_message(prompt_key, user_input)

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
                    return response.content.strip()
            except Exception as e:
                logger.warning(f"LLM: {e}")

        # Step 5: No LLM — MahaComposition output only (not raw resonant words)
        if composed:
            return composed

        # Step 6: Last resort — kirtan rendering
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
            priority=_kg_priority(ContentType.DM_REPLY.value),
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
            priority=_kg_priority(ContentType.DM_INITIATE.value),
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
            priority=_kg_priority(ContentType.POST.value),
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
        # Comments are RAJAS (write) — same gate as propose_post()
        if _guna_mode(result) != _GUNA_RAJAS:
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

        proposal = ContentProposal(
            content_type=ContentType.COMMENT.value,
            content=comment[:280],
            post_id=post_id,
            source=trigger,
            priority=_kg_priority(ContentType.COMMENT.value),
        )

        # Thread context: pass parent_id for reply chains
        if context:
            parent_id = context.get("parent_id")
            if parent_id:
                proposal["parent_id"] = parent_id

        return proposal

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
            priority=_kg_priority(ContentType.VOTE.value),
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
