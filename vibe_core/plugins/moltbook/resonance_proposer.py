"""
RESONANCE PROPOSER v2 — Ferrari Factory Wiring
================================================

Thin adapter that connects:
    - MahaLanguageEngine.generate(text) → EngineResult (5-scorer composed English)
    - render(result) → kirtan rendering (guardian persona + smaranam + verse)
    - PromptRegistry + moltbook.yaml → guardian-persona LLM prompts
    - PromptContext → dynamic moltbook context
to ContentProposalProtocol.

Pipeline:
    text → mahamantra(text) → 27-key result
             ↓                      ↓
       Guna/Cell gate       MahaLanguageEngine.generate(text)
       (TAMAS=skip)              → EngineResult
       (dead=skip)                   ↓
             ↓               EngineResult.output  (5-scorer composed English)
       PASS?                  EngineResult.guardian_name
        │                     EngineResult.verse_ref
        ↓                     EngineResult.section_name
       PromptRegistry         EngineResult.resonant_words
       moltbook.yaml               ↓
       (guardian persona      Format for content type:
        + dynamic context)    DM: reply persona + engine output
             ↓               Comment: insight + guardian lens
       LLMProtocol.speak()   Post: title from section + body from output
             ↓
       ContentProposal        Fallback (no LLM):
                              render(result) → kirtan rendering

Decision hierarchy:
    1. Guna filter    — TAMAS = skip (destructive/spam)
    2. Cell gate      — dead cell = skip (pipeline failed)
    3. Integrity gate — low integrity = skip comments/posts
    4. EngineResult → PromptRegistry → LLM formulation (or render() fallback)
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

# Guna modes from the VM pipeline (guna.py: Guna IntEnum names)
_GUNA_TAMAS = "TAMAS"
_GUNA_RAJAS = "RAJAS"
_GUNA_SATTVA = "SATTVA"

# Cell integrity threshold — below this, content analysis is too noisy
# for outbound comments/posts (but DM replies are still fine)
_INTEGRITY_THRESHOLD = 0.5

# Default Guardian perspective — Kapila = analysis function
_ANALYSIS_GUARDIAN = "kapila"

# Prompt keys — loaded from config/prompts/moltbook.yaml
_PROMPT_KEYS = {
    "dm_reply": "moltbook.dm_reply",
    "comment": "moltbook.comment",
    "post": "moltbook.post",
    "dm_request": "moltbook.dm_request",
}

# Path to YAML prompts
_MOLTBOOK_YAML = Path(__file__).resolve().parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"


def _load_yaml_prompts() -> None:
    """Load Moltbook prompts from YAML. Safe to call multiple times."""
    try:
        from vibe_core.runtime.prompt_registry import PromptRegistry

        loaded = PromptRegistry.load_from_yaml(_MOLTBOOK_YAML)
        if loaded:
            logger.info(f"Moltbook YAML prompts loaded ({loaded} prompts)")
        else:
            logger.warning(f"No prompts loaded from {_MOLTBOOK_YAML}")
    except Exception as e:
        logger.warning(f"YAML prompt loading failed ({e})")


# =========================================================================
# Pipeline result accessors — no Dict[str, Any] in public API
# =========================================================================


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


def _render_fallback(result: dict) -> str:
    """Render VM result via kirtan renderer. The TONGUE of the system."""
    try:
        from vibe_core.mahamantra.render import render

        return render(result)
    except Exception as e:
        logger.warning(f"Kirtan render failed: {e}")
        # Ultimate fallback — guardian header + smaranam
        guardian = str(result.get("guardian") or "unknown").upper()
        quarter = str(result.get("quarter") or "unknown")
        smaranam = result.get("smaranam", ())
        parts = [f"[{guardian} · {quarter}]"]
        for rw in smaranam[:3]:
            parts.append(f'  "{rw.get("sanskrit", "")}" ({rw.get("meaning", "")})')
        return "\n".join(parts)


def _format_resonant_words(engine_result) -> str:
    """Format EngineResult.resonant_words as readable string."""
    if not engine_result.resonant_words:
        return "(none)"
    parts = []
    for sanskrit, meaning, score in engine_result.resonant_words[:5]:
        parts.append(f"{sanskrit} ({meaning}, {score:.2f})")
    return ", ".join(parts)


def _engine_prompt_context(engine_result) -> Dict[str, str]:
    """Build prompt context dict from EngineResult fields."""
    return {
        "guardian_name": engine_result.guardian_name.upper() if engine_result.guardian_name else "UNKNOWN",
        "position": str(getattr(engine_result, "antaranga_active", 0)),
        "quarter": engine_result.section_mode or "",
        "guardian_function": engine_result.guardian_function or "",
        "engine_output": engine_result.output or "",
        "resonant_words": _format_resonant_words(engine_result),
        "verse_ref": engine_result.verse_ref or "",
        "section_name": engine_result.section_name or "",
    }


class ResonanceProposer(ContentProposalProtocol):
    """
    Full-pipeline content proposer wired to existing infrastructure.

    Decision hierarchy:
        1. mahamantra(text) → 27-key result (guna, cell, smaranam, verse, ...)
        2. Guna filter: TAMAS → skip, SATTVA → observe, RAJAS → engage
        3. Cell gate: dead → skip, integrity < threshold → cautious
        4. MahaLanguageEngine.generate() → EngineResult → PromptRegistry → LLM
        5. Fallback: render(result) → kirtan rendering (NOT garbage strings)

    Delegates to:
        MahaLanguageEngine — 5-scorer composed English (substrate/language/engine.py)
        render()           — kirtan rendering with guardian persona (render.py)
        PromptRegistry     — YAML-loaded guardian prompts (config/prompts/moltbook.yaml)
        LLMProtocol        — formulation only (protocols/llm.py)
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

        _load_yaml_prompts()

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

    def _generate(self, text: str):
        """Run MahaLanguageEngine.generate(text) → EngineResult.

        Returns EngineResult with:
            .output           — 5-scorer composed English
            .guardian_name    — guardian name from pipeline
            .verse_ref        — Gita verse reference
            .section_name     — Gita section
            .resonant_words   — typed tuples (sanskrit, meaning, score)
        """
        try:
            from vibe_core.mahamantra.substrate.language.engine import generate

            return generate(text)
        except Exception as e:
            logger.warning(f"MahaLanguageEngine.generate() failed: {e}")
            return None

    def _formulate(
        self,
        prompt_key: str,
        engine_result,
        user_input: str,
        **extra_context: str,
    ) -> Optional[str]:
        """Formulate text via YAML PromptRegistry + LLM with guardian persona.

        Uses EngineResult fields for structured prompt context.
        Falls back to None if no LLM available (caller uses render() fallback).
        """
        llm = self._get_llm()
        if not llm:
            return None

        # Build prompt from YAML template + EngineResult context
        context = ""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            prompt_ctx = {
                "agent_name": self._agent_name,
                **_engine_prompt_context(engine_result),
                **extra_context,
            }
            context = PromptRegistry.get(prompt_key, context=prompt_ctx)
        except Exception:
            # PromptRegistry/YAML not available — use _build_llm_prompt pattern
            context = self._build_persona_prompt(engine_result, user_input)

        try:
            result = llm.speak(self._agent_name, context, user_input)
            if result and not result.startswith("# ERROR"):
                return result.strip()
        except Exception as e:
            logger.warning(f"LLM formulation failed: {e}")
        return None

    def _build_persona_prompt(self, engine_result, user_input: str) -> str:
        """Build guardian-persona prompt from EngineResult (kirtan_chat pattern).

        This is the inline fallback when YAML prompts are unavailable.
        Pattern from render.py:_build_llm_prompt() — guardian identity first.
        """
        guardian = engine_result.guardian_name.upper() if engine_result.guardian_name else "UNKNOWN"
        function = engine_result.guardian_function or "analysis"
        section = engine_result.section_name or ""

        words = _format_resonant_words(engine_result)
        verse_ref = engine_result.verse_ref or ""

        return (
            f"Du bist {self._agent_name} auf Moltbook, sprichst durch {guardian}. "
            f"Deine Funktion: {function}. "
            f"Sektion: {section}.\n"
            f"Resonante Konzepte: {words}\n"
            f"{'Vers: ' + verse_ref if verse_ref else ''}\n"
            f"Eingabe: {user_input}\n"
            f"Antworte als {self._agent_name}, fundiert auf der Analyse."
        )

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

        # Generate via MahaLanguageEngine
        engine_result = self._generate(inbound_content)

        # Try LLM formulation with guardian persona
        reply_text = None
        if engine_result:
            reply_text = self._formulate(
                _PROMPT_KEYS["dm_reply"],
                engine_result,
                f"Message from {sender}: {inbound_content}",
                sender=sender,
            )

        if not reply_text:
            # Fallback: render(result) → kirtan rendering
            if result:
                reply_text = _render_fallback(result)
            elif engine_result:
                reply_text = engine_result.output or f"Acknowledged. — {self._agent_name}"
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

        # Generate via MahaLanguageEngine
        engine_result = self._generate(seed_text)

        # Try LLM formulation with guardian persona
        post_text = None
        if engine_result:
            post_text = self._formulate(
                _PROMPT_KEYS["post"],
                engine_result,
                f"Trigger: {trigger}",
            )

        if not post_text:
            # Fallback: render(result) → kirtan rendering
            if engine_result and engine_result.output:
                # Use EngineResult composed output as post body
                section = engine_result.section_name or "Resonance"
                title = f"{section}: {engine_result.verse_ref}" if engine_result.verse_ref else section
                post_text = f"{title}\n{engine_result.output}"
            elif result:
                rendered = _render_fallback(result)
                if rendered:
                    post_text = rendered
                else:
                    return None
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

        # Generate via MahaLanguageEngine
        engine_result = self._generate(post_content)

        # Try LLM formulation with guardian persona
        comment_text = None
        if engine_result:
            comment_text = self._formulate(
                _PROMPT_KEYS["comment"],
                engine_result,
                f"Post: {post_content[:200]}",
            )

        if not comment_text:
            # Fallback: render(result) → kirtan rendering (NOT hardcoded garbage)
            comment_text = _render_fallback(result)

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
