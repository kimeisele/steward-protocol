"""
RESONANCE PROPOSER — Full Pipeline Content Intelligence
========================================================

The mahamantra VM pipeline IS the brain. This proposer is a thin adapter
that connects the full 27-key pipeline output to ContentProposalProtocol.

Pipeline:
    text → mahamantra(text) → 27-key result (9-step VM, deterministic)
                ↓
    result["guna"]["mode"]     → TAMAS=skip, SATTVA=observe, RAJAS=engage
    result["cell"]["is_alive"] → quality gate (dead = unreliable)
    result["smaranam"]         → resonant word context for LLM
    result["verse"]            → Gita reference for specificity
    result["guardian"]         → perspective routing
    result["vibration"]        → element/attractor signature
                ↓
    PromptRegistry.get("moltbook.*") → governed LLM prompt
    LLMProtocol.speak(agent, context, input) → formulated text
                ↓
    ContentProposal (queue-ready)

Decision hierarchy:
    1. Guna filter    — TAMAS = skip (destructive/spam)
    2. Cell gate      — dead cell = skip (pipeline failed)
    3. Integrity gate — low integrity = skip comments/posts
    4. Pipeline context → LLM formulation (or engine-only fallback)

Delegates to existing infrastructure:
    - mahamantra(text) — full 9-step VM pipeline (substrate/vm/mantra_vm.py)
    - resonate(text)   — 7D word resonance (for analyze() protocol method)
    - PromptRegistry   — governed prompt composition
    - LLMProtocol      — formulation only
"""

import logging
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

# Guna modes from the VM pipeline (guna.py: Guna IntEnum names)
_GUNA_TAMAS = "TAMAS"
_GUNA_RAJAS = "RAJAS"
_GUNA_SATTVA = "SATTVA"

# Cell integrity threshold — below this, content analysis is too noisy
# for outbound comments/posts (but DM replies are still fine)
_INTEGRITY_THRESHOLD = 0.5

# Default Guardian perspective — Kapila = analysis function
_ANALYSIS_GUARDIAN = "kapila"

# Prompts registered at boot for PromptRegistry
_PROMPT_KEYS = {
    "dm_reply": "moltbook.dm_reply",
    "comment": "moltbook.comment",
    "post": "moltbook.post",
    "dm_request": "moltbook.dm_request",
}


def _register_prompts() -> None:
    """Register Moltbook prompts in PromptRegistry. Safe to call multiple times."""
    try:
        from vibe_core.runtime.prompt_registry import PromptRegistry

        PromptRegistry.register(
            _PROMPT_KEYS["dm_reply"],
            "You are {agent_name} on Moltbook. "
            "Reply to a DM from {sender}. "
            "The mahamantra engine analyzed their message:\n"
            "{pipeline_context}\n\n"
            "Use this analysis to craft a genuine, specific reply. "
            "Reference the Sanskrit concept or Gita verse naturally if relevant. "
            "Under 280 chars.",
        )
        PromptRegistry.register(
            _PROMPT_KEYS["comment"],
            "You are {agent_name} on Moltbook. "
            "Comment on a post. "
            "The mahamantra engine analysis:\n"
            "{pipeline_context}\n\n"
            "Bring THIS specific insight to the discussion. "
            "Be concrete — reference the Sanskrit word, element, or verse. "
            "Under 280 chars.",
        )
        PromptRegistry.register(
            _PROMPT_KEYS["post"],
            "You are {agent_name} on Moltbook. "
            "Create a post. "
            "The mahamantra engine analysis:\n"
            "{pipeline_context}\n\n"
            "Write a post that brings this resonance to the community. "
            "First line = title (under 120 chars). Rest = body (under 500 chars). "
            "Be authentic and specific.",
        )
        PromptRegistry.register(
            _PROMPT_KEYS["dm_request"],
            "You are {agent_name}. Another agent wants to chat. "
            "Mahamantra analysis of their profile:\n"
            "{pipeline_context}\n\n"
            "Reply APPROVE if genuine, REJECT if spam.",
        )
        logger.info("Moltbook prompts registered in PromptRegistry")
    except Exception as e:
        logger.warning(f"PromptRegistry unavailable ({e}), using inline prompts")


# =========================================================================
# Pipeline result accessors — no Dict[str, Any] in public API
# =========================================================================


def _build_pipeline_context(result: dict) -> str:
    """Build structured context from full 27-key VM pipeline result for LLM consumption."""
    parts: List[str] = []

    # Guna classification
    guna = result.get("guna", {})
    if guna:
        parts.append(f"Guna: {guna.get('mode', '?')} (opcode={guna.get('opcode', '?')})")

    # Guardian routing
    guardian = result.get("guardian", "")
    role = result.get("role", "")
    quarter = result.get("quarter", "")
    position = result.get("position", -1)
    if guardian:
        parts.append(f"Guardian: {guardian} ({role}) | Quarter: {quarter} | Position: {position}")

    # Gita chapter + verse
    chapter = result.get("chapter", 0)
    significance = result.get("chapter_significance", "")
    if chapter:
        parts.append(f"Chapter {chapter}: {significance}")

    verse = result.get("verse")
    if verse and isinstance(verse, dict):
        parts.append(f"Verse: {verse.get('id', '?')}")

    # Vibration signature
    vibration = result.get("vibration", {})
    if vibration:
        sig = vibration.get("signature", {})
        parts.append(
            f"Element: {sig.get('element', '?')} | "
            f"Attractor: {vibration.get('attractor', '?')} | "
            f"Shruti: {sig.get('shruti', False)}"
        )

    # Smaranam — resonant words from the pipeline
    smaranam = result.get("smaranam", ())
    if smaranam:
        word_lines = []
        for entry in smaranam[:5]:
            word_lines.append(
                f"  {entry['sanskrit']} = {entry['meaning']} "
                f"(score={entry['score']:.3f})"
            )
        parts.append("Resonant words:\n" + "\n".join(word_lines))

    # Cell status
    cell = result.get("cell", {})
    if cell:
        parts.append(
            f"Cell: {'alive' if cell.get('is_alive') else 'dead'} | "
            f"integrity: {cell.get('integrity', 0):.2f} | "
            f"prana: {cell.get('prana', 0)}"
        )

    # Parampara
    parampara = result.get("parampara", {})
    if parampara:
        parts.append(
            f"Parampara: {'verified' if parampara.get('verified') else 'unverified'} "
            f"(channel {parampara.get('channel', -1)})"
        )

    return "\n".join(parts) if parts else "No analysis available."


def _guna_mode(result: dict) -> str:
    """Extract guna mode string from pipeline result."""
    return result.get("guna", {}).get("mode", "")


def _is_tamas(result: dict) -> bool:
    """TAMAS guna = destructive/spam. Skip entirely."""
    return _guna_mode(result) == _GUNA_TAMAS


def _is_alive(result: dict) -> bool:
    """Cell alive = pipeline completed successfully."""
    return bool(result.get("cell", {}).get("is_alive"))


def _integrity(result: dict) -> float:
    """Cell integrity [0.0, 1.0]. Higher = more coherent."""
    return float(result.get("cell", {}).get("integrity", 0.0))


def _should_skip(result: dict) -> bool:
    """Combined gate: TAMAS or dead cell → skip."""
    return _is_tamas(result) or not _is_alive(result)


def _top_score(ranked: List[RankedWord]) -> float:
    """Return the top resonance score, or 0.0 if empty."""
    return ranked[0].total_score if ranked else 0.0


class ResonanceProposer(ContentProposalProtocol):
    """
    Full-pipeline content proposer.

    Decision hierarchy:
        1. mahamantra(text) → 27-key result (guna, cell, smaranam, verse, ...)
        2. Guna filter: TAMAS → skip, SATTVA → observe, RAJAS → engage
        3. Cell gate: dead → skip, integrity < threshold → cautious
        4. Pipeline context → PromptRegistry → LLM formulation

    Delegates to:
        mahamantra(text) — full 9-step VM pipeline (substrate/vm/mantra_vm.py)
        resonate(text)   — 7D resonance scoring (for analyze() protocol method)
        PromptRegistry   — governed prompts (runtime/prompt_registry.py)
        LLMProtocol      — formulation only (protocols/llm.py)
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

        # Validate guardian exists
        if guardian not in _GUARDIAN_CONFIGS:
            raise ValueError(f"Unknown guardian: {guardian}. Valid: {list(_GUARDIAN_CONFIGS)}")

        _register_prompts()

    def _get_llm(self):
        """Lazy-resolve LLMProtocol from ServiceRegistry."""
        if self._llm_resolved:
            return self._llm
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.llm import LLMProtocol

            self._llm = ServiceRegistry.get(LLMProtocol)
            self._llm_resolved = True
            if self._llm:
                logger.info("ResonanceProposer: LLM resolved from DI")
        except Exception as e:
            logger.warning(f"ResonanceProposer: LLM resolution failed ({e})")
            self._llm_resolved = True
        return self._llm

    def _run_pipeline(self, text: str) -> Optional[dict]:
        """Run the full mahamantra VM pipeline. Returns 27-key result or None."""
        if not text or not text.strip():
            return None
        try:
            from vibe_core.mahamantra import mahamantra

            return mahamantra(text)
        except Exception as e:
            logger.warning(f"Mahamantra pipeline failed: {e}")
            return None

    def _formulate(self, prompt_key: str, pipeline_context: str, user_input: str, **fmt_kwargs: str) -> Optional[str]:
        """
        Formulate text via PromptRegistry + LLM.

        Falls back to returning None if no LLM available.
        The caller decides what to do with None (engine-only fallback).
        """
        llm = self._get_llm()
        if not llm:
            return None

        # Try PromptRegistry first
        context = ""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            context = PromptRegistry.get(
                prompt_key,
                context={
                    "agent_name": self._agent_name,
                    "pipeline_context": pipeline_context,
                    **fmt_kwargs,
                },
            )
        except Exception:
            # PromptRegistry not available — build context inline
            context = f"You are {self._agent_name}.\n{pipeline_context}"

        try:
            result = llm.speak(self._agent_name, context, user_input)
            if result and not result.startswith("# ERROR"):
                return result.strip()
        except Exception as e:
            logger.warning(f"LLM formulation failed: {e}")
        return None

    # =========================================================================
    # ContentProposalProtocol
    # =========================================================================

    def analyze(self, text: str) -> List[RankedWord]:
        """Run 7D resonance analysis. Protocol-compatible return type."""
        try:
            return resonate(text, top_n=self._top_n)
        except Exception as e:
            logger.warning(f"Resonance analysis failed: {e}")
            return []

    def propose_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict[str, object]] = None,
    ) -> Optional[ContentProposal]:
        """Analyze inbound DM via full pipeline, formulate reply."""
        result = self._run_pipeline(inbound_content)

        if result and _is_tamas(result):
            logger.info(f"DM from {sender} classified TAMAS — skipped")
            return None

        # Build context from pipeline (or fallback to word resonance)
        if result:
            pipeline_context = _build_pipeline_context(result)
        else:
            ranked = self.analyze(inbound_content)
            word_lines = [f"  {rw.sanskrit} = {rw.first_meaning}" for rw in ranked[:3]]
            pipeline_context = ("Resonant words:\n" + "\n".join(word_lines)) if word_lines else "No analysis available."

        reply_text = self._formulate(
            _PROMPT_KEYS["dm_reply"],
            pipeline_context,
            f"Message from {sender}: {inbound_content}",
            sender=sender,
        )

        if not reply_text:
            # No LLM — construct from engine data
            smaranam = result.get("smaranam", ()) if result else ()
            if smaranam:
                top = smaranam[0]
                reply_text = (
                    f"Your message resonates with {top['sanskrit']} "
                    f"({top['meaning']}). "
                    f"— {self._agent_name}"
                )
            else:
                reply_text = f"Acknowledged. — {self._agent_name}"

        gw = gateway_response or {}
        return ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content=reply_text[:280],
            conversation_id=conversation_id,
            source="inbound_dm",
            sender=sender,
            priority=1,
            needs_human_input=False,
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
        """Analyze DM request via pipeline. TAMAS or dead cell = reject."""
        result = self._run_pipeline(f"{from_agent} {message_preview}")

        if result and _should_skip(result):
            guna = _guna_mode(result)
            logger.info(f"DM request rejected: {from_agent} (guna={guna}, alive={_is_alive(result)})")
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
        """Generate engine-backed post. Requires RAJAS guna + alive cell + good integrity."""
        seed_text = trigger
        ctx = context or {}
        feed_topics: List[str] = ctx.get("feed_topics", [])
        if feed_topics:
            seed_text = f"{trigger}: {', '.join(str(t) for t in feed_topics[:3])}"

        result = self._run_pipeline(seed_text)
        if not result or _should_skip(result):
            return None

        # Posts require RAJAS (active engagement) and good integrity
        if _guna_mode(result) != _GUNA_RAJAS:
            return None
        if _integrity(result) < _INTEGRITY_THRESHOLD:
            return None

        pipeline_context = _build_pipeline_context(result)

        post_text = self._formulate(
            _PROMPT_KEYS["post"],
            pipeline_context,
            f"Trigger: {trigger}",
        )

        if not post_text:
            # No LLM — build from engine data
            smaranam = result.get("smaranam", ())
            if smaranam:
                top = smaranam[0]
                title = f"Resonance: {top['sanskrit']} ({top['meaning']})"
                chapter_sig = result.get("chapter_significance", "")
                post_text = f"{title}\n{chapter_sig}\n— {self._agent_name}"
            else:
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
        """Analyze post via pipeline, generate comment. TAMAS/dead/low-integrity → skip."""
        result = self._run_pipeline(post_content)
        if not result or _should_skip(result):
            return None

        if _integrity(result) < _INTEGRITY_THRESHOLD:
            return None

        pipeline_context = _build_pipeline_context(result)

        comment_text = self._formulate(
            _PROMPT_KEYS["comment"],
            pipeline_context,
            f"Post: {post_content[:200]}",
        )

        if not comment_text:
            # No LLM — construct from engine
            smaranam = result.get("smaranam", ())
            guardian = result.get("guardian", "")
            if smaranam:
                top = smaranam[0]
                comment_text = (
                    f"This resonates with {top['sanskrit']} "
                    f"({top['meaning']})"
                )
                if guardian:
                    comment_text += f" — through the lens of {guardian}"
                comment_text += f". — {self._agent_name}"
            else:
                return None

        return ContentProposal(
            content_type=ContentType.COMMENT.value,
            content=comment_text[:280],
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
        """Pipeline-driven engagement. TAMAS/dead → skip, else upvote."""
        result = self._run_pipeline(post_content)
        if not result or _should_skip(result):
            return None

        return ContentProposal(
            content_type=ContentType.VOTE.value,
            post_id=post_id,
            source="pipeline_engagement",
            priority=0,
        )

    # =========================================================================
    # Feed analysis (called by plugin heartbeat)
    # =========================================================================

    def analyze_feed(
        self, posts: Sequence[MoltbookPost],
    ) -> List[Tuple[MoltbookPost, List[RankedWord], float]]:
        """
        Analyze feed posts via full pipeline. Pre-filters TAMAS and dead cells.
        Returns (post, ranked_words, top_score) tuples sorted by resonance descending.
        """
        scored: List[Tuple[MoltbookPost, List[RankedWord], float]] = []
        for post in posts:
            content = post.get("content", post.get("title", ""))
            if not content:
                continue

            text = str(content)

            # Pipeline gate — TAMAS and dead cells are filtered HERE
            result = self._run_pipeline(text)
            if result and _should_skip(result):
                guna = _guna_mode(result)
                logger.debug(f"Feed post filtered: guna={guna}, alive={_is_alive(result)}")
                continue

            # Get ranked words for protocol-compatible return type
            ranked = self.analyze(text)
            score = ranked[0].total_score if ranked else 0.0
            scored.append((post, ranked, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        return scored


__all__ = ["ResonanceProposer"]
