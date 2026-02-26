"""
Moltbook Agency Director — I-P-V-O Pipeline.

Uses Mahamantra substrate DIRECTLY. No delegation to proposer gates.

    INPUT:    Knowledge Graph + feed context + previous feedback
    PROCESS:  mahamantra(text) → context_builders → PromptRegistry → LLM → content
    VALIDATE: Constitution check (governance/constitution.py)
    OUTPUT:   CycleResult → caller

Guna informs STYLE (guardian, tone), NOT gating.
Only TAMAS + dead cell = skip. Everything else generates content.

Delegates to:
    - ContentComposer (composer.py) — LLM composition + truncation
    - ContextResolver (context_resolver.py) — INPUT phase context gathering
    - MuraliRouter (murali_router.py) — MURALI department routing
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from typing import TypedDict

from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    HALVES,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
    TRINITY,
)
from vibe_core.mahamantra.substrate.encoding.harmonics import (
    ResonanceHarmonics,
    SravanamCheck,
    VedicScaleMapping,
)

# Re-export MuraliRouter for backward compatibility (imported from here by plugin_main, tests)
from vibe_core.cartridges.agent_city.moltbook.core.murali_router import MuraliRouter  # noqa: F401

logger = logging.getLogger("MOLTBOOK_DIRECTOR")

# Per-guna integrity thresholds — ALL gunas can skip, not just TAMAS.
# Derived from COSMIC_FRAME (21600). Higher guna = lower bar (more trust).
_INTEGRITY_THRESHOLDS = {
    "SATTVA": COSMIC_FRAME * HALVES // PANCHA,        # 8640 — low bar, SATTVA is usually clean
    "RAJAS": COSMIC_FRAME * TRINITY // PANCHA,        # 12960 — medium, RAJAS is 90% of traffic
    "TAMAS": COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA),  # 6480 — same as before
}


class DirectorContext(TypedDict, total=False):
    """Typed context for AgencyDirector I-P-V-O cycles."""

    trigger: str
    post_id: str
    sender: str
    conversation_id: str
    parent_id: str
    submolt: str
    to_agent: str
    gateway_response: Dict[str, str]
    context: Dict[str, str]


@dataclass
class CycleResult:
    """Result of a complete I-P-V-O cycle."""

    status: str  # SUCCESS, VALIDATION_FAILED, LLM_UNAVAILABLE, SKIPPED, ERROR
    phase: str  # INPUT, PROCESS, VALIDATE, OUTPUT
    cycle_id: str
    content_type: str = ""
    content: Optional[str] = None
    violations: Optional[List[str]] = None
    error: Optional[str] = None
    retries_used: int = 0
    guna: str = ""
    guardian: str = ""
    duration_ms: float = 0.0


# Guna → style mapping (from BG 14.5, protocol-derived)
_GUNA_STYLE = {
    "SATTVA": "contemplative",  # wisdom, reflection, philosophical depth
    "RAJAS": "active",  # engagement, creation, direct action
    "TAMAS": "transformative",  # cleanup, restructuring (if allowed at all)
}

# Intent quarter → response style (MantraOpCode quarters, opcode.py)
_INTENT_QUARTER = {
    "SYS_WAKE": "genesis",
    "LOAD_ROOT": "genesis",
    "ALLOC_MEM": "genesis",
    "INIT_THREAD": "genesis",
    "COMPILE_AST": "dharma",
    "BIND_SYMBOL": "dharma",
    "TYPE_CHECK": "dharma",
    "DHARMA_TEST": "dharma",
    "EXEC_OP": "karma",
    "EXTEND_CAP": "karma",
    "STATE_SYNC": "karma",
    "LEDGER_SIGN": "karma",
    "YIELD_CPU": "moksha",
    "IO_FLUSH": "moksha",
    "LOG_EMIT": "moksha",
    "AUDIT_SEAL": "moksha",
}

# Engagement action → handler method name LUT (replaces if/elif chain)
_ENGAGEMENT_DISPATCH = {
    "follow_back": "_do_follow_back",
    "subscribe": "_do_subscribe",
    "upvote": "_do_upvote",
}


class AgencyDirector:
    """
    Moltbook I-P-V-O orchestrator.

    Uses Mahamantra substrate directly:
        - mahamantra(text) → 27-key pipeline result (guna, cell, guardian, smaranam, verse)
        - MahaLanguageEngine.generate(text) → EngineResult
        - MahaComposition.compose(result, text) → English (5 scorers: prana, rhythm, semantic/WordNet, mode, state)
        - render(result) → kirtan rendering (last resort)
        - KnowledgeResolver.compile_context(topic) → domain knowledge
        - EventBus.emit_sync() → system visibility

    Delegates to:
        - ContentComposer: LLM composition + truncation
        - ContextResolver: INPUT phase context gathering
    """

    def __init__(self, plugin=None):
        self._plugin = plugin
        self._constitution = None
        self._event_log = None
        self._engagement = None
        self._feedback = None
        # Lazy-init delegates
        self._composer = None
        self._resolver = None

    # -- Delegates (lazy-init) --

    @property
    def _content_composer(self):
        if self._composer is None:
            from vibe_core.cartridges.agent_city.moltbook.core.composer import ContentComposer

            self._composer = ContentComposer(plugin=self._plugin)
        return self._composer

    @property
    def _context_resolver(self):
        if self._resolver is None:
            from vibe_core.cartridges.agent_city.moltbook.core.context_resolver import ContextResolver

            self._resolver = ContextResolver(event_log_getter=lambda: self.event_log)
        return self._resolver

    # -- Lazy properties (only what we OWN, not what we USE) --

    @property
    def feedback(self):
        if self._feedback is None:
            from vibe_core.protocols.feedback import get_feedback_safe

            self._feedback = get_feedback_safe()
        return self._feedback

    @property
    def constitution(self):
        if self._constitution is None:
            from ..governance.constitution import get_constitution

            self._constitution = get_constitution()
        return self._constitution

    @property
    def event_log(self):
        if self._event_log is None:
            from .memory import get_event_log

            self._event_log = get_event_log()
        return self._event_log

    @property
    def engagement(self):
        if self._engagement is None:
            from ..capabilities.engagement import get_engagement_capability

            self._engagement = get_engagement_capability()
        return self._engagement

    # =========================================================================
    # I-P-V-O: Single Cycle
    # =========================================================================

    def run_cycle(
        self,
        content_type: str,
        raw_input: str = "",
        **ctx: Any,
    ) -> CycleResult:
        """Execute one I-P-V-O cycle."""
        cycle_id = datetime.now(timezone.utc).isoformat()
        t0 = time.monotonic()
        self._emit("THOUGHT", f"Starting {content_type} cycle")
        feedback_cmd = f"moltbook.{content_type}"

        # ===== INPUT =====
        try:
            input_ctx = self._context_resolver.gather(content_type, raw_input, **ctx)
        except Exception as e:
            logger.error(f"INPUT failed: {e}")
            self.event_log.record_error("input_failure", str(e))
            elapsed = (time.monotonic() - t0) * 1000
            self.feedback.signal_failure(feedback_cmd, str(e), {"phase": "INPUT"}, duration_ms=elapsed)
            return CycleResult(
                status="ERROR",
                phase="INPUT",
                cycle_id=cycle_id,
                content_type=content_type,
                error=str(e),
                duration_ms=elapsed,
            )

        # ===== PROCESS =====
        try:
            content, process_ctx = self._process(content_type, raw_input, input_ctx, **ctx)
        except Exception as e:
            logger.error(f"PROCESS failed: {e}")
            self.event_log.record_error("process_failure", str(e))
            self._emit("ERROR", f"PROCESS failed: {e}")
            elapsed = (time.monotonic() - t0) * 1000
            self.feedback.signal_failure(feedback_cmd, str(e), {"phase": "PROCESS"}, duration_ms=elapsed)
            return CycleResult(
                status="ERROR",
                phase="PROCESS",
                cycle_id=cycle_id,
                content_type=content_type,
                error=str(e),
                duration_ms=elapsed,
            )

        if not content:
            elapsed = (time.monotonic() - t0) * 1000
            # Distinguish integrity skip from LLM unavailability
            status = process_ctx.get("status", "ERROR")
            if process_ctx.get("skipped"):
                # Preserve specific skip status (SKIPPED_LOW_INTEGRITY)
                self.feedback.signal_partial(
                    feedback_cmd,
                    "integrity_skip",
                    {
                        "guna": process_ctx.get("guna", ""),
                        "guardian": process_ctx.get("guardian", ""),
                    },
                )
            elif status == "LLM_UNAVAILABLE":
                self.feedback.signal_failure(
                    feedback_cmd,
                    "llm_unavailable",
                    {
                        "guna": process_ctx.get("guna", ""),
                        "guardian": process_ctx.get("guardian", ""),
                    },
                    duration_ms=elapsed,
                )
            else:
                self.feedback.signal_failure(feedback_cmd, "no_content", process_ctx, duration_ms=elapsed)
            return CycleResult(
                status=status,
                phase="PROCESS",
                cycle_id=cycle_id,
                content_type=content_type,
                error=process_ctx.get("error", "No content generated"),
                guna=process_ctx.get("guna", ""),
                guardian=process_ctx.get("guardian", ""),
                duration_ms=elapsed,
            )

        guna = process_ctx.get("guna", "")
        guardian = process_ctx.get("guardian", "")
        self.event_log.record_content_generated(content_type, content)
        self._emit(
            "ACTION",
            f"Generated {content_type}",
            {
                "content_type": content_type,
                "guna": guna,
                "guardian": guardian,
                "length": len(content),
                "zone": process_ctx.get("resonance_zone", ""),
                "rasa": process_ctx.get("rasa", ""),
            },
        )

        # ===== VALIDATE =====
        validation = self.constitution.validate(content, content_type)
        if not validation.is_valid:
            logger.info(f"VALIDATE failed: {validation.violations}")
            self.event_log.record_content_rejected(content, "governance_violation", validation.violations)
            self.event_log.store_validation_feedback(validation.violations, content)
            self._emit("VIOLATION", f"Content rejected: {validation.violations[:2]}")
            elapsed = (time.monotonic() - t0) * 1000
            self.feedback.signal_failure(
                feedback_cmd,
                "governance_violation",
                {
                    "guna": guna,
                    "guardian": guardian,
                    "violations": validation.violations[:3],
                },
                duration_ms=elapsed,
            )
            return CycleResult(
                status="VALIDATION_FAILED",
                phase="VALIDATE",
                cycle_id=cycle_id,
                content_type=content_type,
                content=content,
                violations=validation.violations,
                guna=guna,
                guardian=guardian,
                duration_ms=elapsed,
            )

        if validation.warnings:
            logger.info(f"VALIDATE warnings: {validation.warnings}")

        # ===== OUTPUT =====
        elapsed = (time.monotonic() - t0) * 1000
        self.feedback.signal_success(
            feedback_cmd,
            {
                "guna": guna,
                "guardian": guardian,
                "length": len(content),
            },
            duration_ms=elapsed,
        )
        self._emit(
            "COMPLETED",
            f"Content generated: {content_type}",
            {
                "content_type": content_type,
                "guna": guna,
                "guardian": guardian,
                "length": len(content),
                "duration_ms": elapsed,
            },
        )
        return CycleResult(
            status="SUCCESS",
            phase="OUTPUT",
            cycle_id=cycle_id,
            content_type=content_type,
            content=content,
            guna=guna,
            guardian=guardian,
            duration_ms=elapsed,
        )

    # =========================================================================
    # I-P-V-O: Retry Loop
    # =========================================================================

    def run_retry_loop(
        self,
        content_type: str,
        raw_input: str = "",
        max_retries: int = 2,
        **ctx: Any,
    ) -> CycleResult:
        """Execute I-P-V-O with automatic retry on governance violations."""
        last_result = None
        for attempt in range(max_retries + 1):
            result = self.run_cycle(content_type, raw_input, **ctx)
            last_result = result
            result.retries_used = attempt

            if result.status == "SUCCESS":
                return result

            if result.status == "VALIDATION_FAILED" and attempt < max_retries:
                logger.info(f"Retry {attempt + 1}/{max_retries}: {result.violations}")
                continue

            return result

        return last_result or CycleResult(
            status="ERROR",
            phase="UNKNOWN",
            cycle_id=datetime.now(timezone.utc).isoformat(),
            content_type=content_type,
            error="Retry loop exhausted",
        )

    # =========================================================================
    # PROCESS Phase — Use Mahamantra substrate directly
    # =========================================================================

    def _process(
        self,
        content_type: str,
        raw_input: str,
        input_ctx: Dict[str, Any],
        **ctx: Any,
    ) -> tuple:
        """PROCESS phase: generate content using Mahamantra infrastructure.

        1. Run mahamantra(text) → pipeline result (guna, guardian, resonant words)
        2. Minimal gate: TAMAS + dead cell = skip. Everything else produces content.
        3. Guna → style (contemplative/active), guardian from pipeline
        4. Delegate to ContentComposer for LLM composition
        5. SravanamCheck advisory + smart truncation
        """
        seed_text = raw_input or ctx.get("trigger", content_type)

        # Run Mahamantra VM pipeline
        pipeline_result = self._content_composer._run_pipeline(seed_text)
        if not pipeline_result:
            return "", {"error": "Pipeline returned None"}

        # Extract physics
        guna = pipeline_result.get("guna", {}).get("mode", "RAJAS")
        alive = pipeline_result.get("cell", {}).get("is_alive", True)
        integrity = float(pipeline_result.get("cell", {}).get("integrity", 1.0))
        guardian = str(pipeline_result.get("guardian", "unknown"))

        # Semantic skip: ALL gunas check integrity, not just TAMAS.
        # Dead cells always skip. Low-integrity content = silence is better than garbage.
        integrity_cf = int(integrity * COSMIC_FRAME)
        threshold = _INTEGRITY_THRESHOLDS.get(guna, _INTEGRITY_THRESHOLDS["RAJAS"])
        if not alive or integrity_cf < threshold:
            logger.info(f"Skip: {guna} integrity={integrity_cf}/{COSMIC_FRAME} (threshold={threshold})")
            return "", {"guna": guna, "guardian": guardian, "skipped": True, "status": "SKIPPED_LOW_INTEGRITY"}

        style = _GUNA_STYLE.get(guna, "active")

        # Resonance classification — zone (integer CF) + rasa (emotional tone)
        resonance_zone = ResonanceHarmonics.get_zone(integrity_cf)
        rasa_name, rasa_meaning = VedicScaleMapping.resonance_to_rasa(integrity)
        logger.info(
            f"PROCESS: guna={guna} style={style} guardian={guardian} "
            f"integrity={integrity:.3f} zone={resonance_zone} rasa={rasa_name}"
        )

        # Compose content via ContentComposer — all harmonics data flows as CONTEXT
        content = self._content_composer.compose(
            pipeline_result,
            seed_text,
            content_type,
            input_ctx,
            rasa_name=rasa_name,
            rasa_meaning=rasa_meaning,
            guna=guna,
            style=style,
            resonance_zone=resonance_zone,
        )

        # SravanamCheck advisory — entropy verification (observability, not blocking)
        sravanam_ok = True
        sravanam_reason = ""
        if content:
            input_tokens = len(seed_text.split())
            output_tokens = len(content.split())
            sravanam_ok, sravanam_reason = SravanamCheck.can_emit(
                input_tokens,
                output_tokens,
                integrity,
            )
            if not sravanam_ok:
                safe_size = SravanamCheck.compute_safe_output_size(input_tokens)
                logger.info(
                    f"SravanamCheck advisory: {sravanam_reason} (safe_output={safe_size}, actual={output_tokens})"
                )

        # Safety-net truncation: only if content exceeds API hard limit (10KB)
        # Length is FORMAT-DRIVEN (via token budget in composer), not hardcoded here.
        _API_SAFETY_LIMIT = 10000
        if content and len(content) > _API_SAFETY_LIMIT:
            content = self._content_composer.truncate_smart(content, _API_SAFETY_LIMIT)

        process_ctx = {
            "source": "mahamantra",
            "guna": guna,
            "guardian": guardian,
            "style": style,
            "integrity": integrity,
            "resonance_zone": resonance_zone,
            "rasa": rasa_name,
            "sravanam_ok": sravanam_ok,
        }
        if not sravanam_ok:
            process_ctx["sravanam_advisory"] = sravanam_reason

        # Explicit status when LLM produced no content
        if not content:
            process_ctx["status"] = "LLM_UNAVAILABLE"
            process_ctx["error"] = "LLM unavailable — no content generated"

        return content, process_ctx

    # =========================================================================
    # EventBus integration — system visibility (consolidated)
    # =========================================================================

    def _emit(self, event_type_name: str, message: str, data: Optional[Dict] = None) -> None:
        """Emit event to system EventBus."""
        try:
            from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus
            from vibe_core.mahamantra.substrate.event_types import EventType

            bus = get_event_bus()
            et = getattr(EventType, event_type_name, EventType.ACTION)
            bus.emit_sync(et, "moltbook", message, data or {})
        except Exception as e:
            logger.warning(f"EventBus emit failed: {e}")

    # =========================================================================
    # Engagement (pass-through to capability)
    # =========================================================================

    def process_engagement(self, action: str, target: str, **ctx: Any) -> bool:
        """Process a social engagement action via dict-dispatch."""
        handler_name = _ENGAGEMENT_DISPATCH.get(action)
        if handler_name:
            return getattr(self, handler_name)(target, **ctx)
        return False

    def _do_follow_back(self, target: str, **ctx: Any) -> bool:
        if self.engagement.should_follow_back(target):
            self.engagement.mark_followed(target)
            self.event_log.record_engagement("follow", target)
            self._emit("ACTION", "Followed back", {"target": target})
            return True
        return False

    def _do_subscribe(self, target: str, **ctx: Any) -> bool:
        if self.engagement.should_subscribe(target):
            self.engagement.mark_subscribed(target)
            self.event_log.record_engagement("subscribe", target)
            self._emit("ACTION", "Subscribed", {"target": target})
            return True
        return False

    def _do_upvote(self, target: str, **ctx: Any) -> bool:
        author = ctx.get("author", "")
        if self.engagement.should_upvote(target, author):
            self.event_log.record_engagement("upvote", target)
            return True
        return False
