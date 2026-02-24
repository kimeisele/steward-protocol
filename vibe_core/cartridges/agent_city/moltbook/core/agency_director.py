"""
Moltbook Agency Director — I-P-V-O Pipeline.

Uses Mahamantra substrate DIRECTLY. No delegation to proposer gates.

    INPUT:    Knowledge Graph + feed context + previous feedback
    PROCESS:  mahamantra(text) → context_builders → PromptRegistry → LLM → content
    VALIDATE: Constitution check (governance/constitution.py)
    OUTPUT:   CycleResult → caller

Guna informs STYLE (guardian, tone), NOT gating.
Only TAMAS + dead cell = skip. Everything else generates content.

Prompts come from config/prompts/moltbook.yaml (pure context, zero instructions).
Code enforces physical barriers (char limits, guna gates, integrity checks).

Wires: MahaComposition, MahaLanguageEngine, Knowledge Graph, EventBus,
       ResonanceHarmonics (zone), VedicScaleMapping (rasa), SravanamCheck (entropy),
       PromptRegistry (YAML templates), context_builders (shared extraction).
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing import TypedDict

from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
)
from vibe_core.mahamantra.substrate.encoding.harmonics import (
    ResonanceHarmonics,
    SravanamCheck,
    VedicScaleMapping,
)

from .context_builders import format_resonant_words, guardian_vocabulary_short, section_data

logger = logging.getLogger("MOLTBOOK_DIRECTOR")

# Character limits per content type (not cleanly derivable from SEED — config constants)
_CHAR_LIMIT = {"comment": 280, "dm_reply": 280, "post": 500}
_DEFAULT_CHAR_LIMIT = 280

# Integrity threshold scaled to COSMIC_FRAME — integer comparison, no floats
# 6480 / 21600 ≈ 0.3 (SHARANAGATI / (QUARTERS × PANCHA))
_MIN_INTEGRITY_CF = COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA)  # 6480


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


# =========================================================================
# Guna → style mapping (from BG 14.5, protocol-derived)
# =========================================================================

_GUNA_STYLE = {
    "SATTVA": "contemplative",  # wisdom, reflection, philosophical depth
    "RAJAS": "active",  # engagement, creation, direct action
    "TAMAS": "transformative",  # cleanup, restructuring (if allowed at all)
}

# =========================================================================
# Intent quarter → response style (MantraOpCode quarters, opcode.py)
# =========================================================================

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

# =========================================================================
# Content type → YAML prompt key (PromptRegistry lookup)
# =========================================================================
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
# The ONLY text telling the LLM what to DO.
# System message = identity + composed words (WHO you are + WHAT words to use).
# User message = atomic task (WHAT to produce).
_TASK_TEMPLATES = {
    "post": "Write an original post about: {input}",
    "dm_reply": "Reply to this message: {input}",
    "comment": "Write a comment responding to: {input}",
    "dm_request": "Send a message about: {input}",
}


def _build_task_message(content_type: str, input_text: str) -> str:
    """Build atomic task message for LLM user role."""
    template = _TASK_TEMPLATES.get(content_type, "Write about: {input}")
    return template.format(input=input_text[:200] if input_text else content_type)


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


# =========================================================================
# Engagement action → handler method name LUT (replaces if/elif chain)
# =========================================================================
_ENGAGEMENT_DISPATCH = {
    "follow_back": "_do_follow_back",
    "subscribe": "_do_subscribe",
    "upvote": "_do_upvote",
}


# =========================================================================
# MURALI Department Routing — VenuOrchestrator phase → department priority
# =========================================================================

# MURALI 4-bit phase (0-3) → department name
_MURALI_DEPARTMENTS = {
    0: "research",  # GENESIS: scan, discover, extract topics
    1: "planning",  # DHARMA: evaluate strategy, prioritize topics
    2: "execution",  # KARMA: generate content, publish
    3: "learning",  # MOKSHA: track engagement, analyze patterns
}


class MuraliRouter:
    """Read-only access to VenuOrchestrator MURALI phase → department name.

    Used by plugin_main heartbeat to weight department priorities.
    Does NOT modify VenuOrchestrator state — pure observation.

    If VenuOrchestrator is unavailable, uses fallback_tick (heartbeat_count)
    to cycle through all 4 departments. This prevents starvation where
    only KARMA/execution runs when venu is uninitialized.
    """

    def current_department(self, fallback_tick: int = 0) -> str:
        """Read current MURALI phase → department name.

        Args:
            fallback_tick: Used to cycle departments when VenuOrchestrator
                is unavailable. Typically heartbeat_count.
        """
        from vibe_core.mahamantra.substrate.core.seed import QUARTERS, WORDS

        try:
            from vibe_core.mahamantra import mahamantra

            venu = mahamantra.venu
            if venu is not None:
                tick = venu.tick
                quarter_size = WORDS // QUARTERS  # 4
                murali = min(tick % WORDS // quarter_size, QUARTERS - 1)
                return _MURALI_DEPARTMENTS.get(murali, "execution")
        except Exception:
            pass

        # Fallback: cycle through departments using fallback_tick
        murali = fallback_tick % QUARTERS
        return _MURALI_DEPARTMENTS.get(murali, "execution")

    def should_prioritize(self, task: str, fallback_tick: int = 0) -> bool:
        """Does this task match the current MURALI phase?"""
        return task == self.current_department(fallback_tick)


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
    """

    def __init__(self, plugin=None):
        self._plugin = plugin
        self._constitution = None
        self._event_log = None
        self._engagement = None
        self._feedback = None

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
        self._emit_thought(f"Starting {content_type} cycle")
        feedback_cmd = f"moltbook.{content_type}"

        # ===== INPUT =====
        try:
            input_ctx = self._input(content_type, raw_input, **ctx)
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
            self._emit_error(f"PROCESS failed: {e}")
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
            # Distinguish TAMAS skip from LLM unavailability
            status = process_ctx.get("status", "ERROR")
            if process_ctx.get("skipped"):
                status = "SKIPPED"
                self.feedback.signal_partial(
                    feedback_cmd,
                    "tamas_skip",
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
        self._emit_action(
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
            self._emit_violation(f"Content rejected: {validation.violations[:2]}")
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
    # INPUT Phase — Gather context from all available systems
    # =========================================================================

    def _input(self, content_type: str, raw_input: str, **ctx: Any) -> Dict[str, Any]:
        """INPUT phase: gather context from all available systems.

        Queries (all graceful degradation — works standalone):
            1. Knowledge Graph → domain context
            2. MahaLLM Kernel → guardian vocabulary + semantic expansion
            3. ServiceRegistry → discover available agents/capabilities
            4. Previous validation feedback (retry loop)
        """
        input_ctx: Dict[str, Any] = {
            "content_type": content_type,
            "raw_input": raw_input,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        topic = raw_input[:200] if raw_input else content_type

        # Knowledge Graph: domain context
        kg_context = self._query_knowledge(topic)
        if kg_context:
            input_ctx["knowledge_context"] = kg_context

        # MahaLLM Kernel: guardian semantic expansion
        kernel_context = self._query_kernel(topic)
        if kernel_context:
            input_ctx["kernel_context"] = kernel_context

        # ServiceRegistry: discover available agent capabilities
        available = self._discover_capabilities()
        if available:
            input_ctx["available_agents"] = available

        # Previous validation feedback (retry loop)
        feedback = self.event_log.get_last_validation_feedback()
        if feedback:
            input_ctx["previous_violations"] = feedback.get("violations", [])
            input_ctx["previous_draft"] = feedback.get("draft")

        input_ctx.update(ctx)
        return input_ctx

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
        4. MahaComposition.compose() → English (5 scorers incl. WordNet)
        5. render() fallback for minimal output
        """
        seed_text = raw_input or ctx.get("trigger", content_type)

        # Run Mahamantra VM pipeline
        pipeline_result = self._run_pipeline(seed_text)
        if not pipeline_result:
            return "", {"error": "Pipeline returned None"}

        # Extract physics
        guna = pipeline_result.get("guna", {}).get("mode", "RAJAS")
        alive = pipeline_result.get("cell", {}).get("is_alive", True)
        integrity = float(pipeline_result.get("cell", {}).get("integrity", 1.0))
        guardian = str(pipeline_result.get("guardian", "unknown"))

        # Minimal gate: only TAMAS + dead/low-integrity = skip
        # SATTVA and RAJAS BOTH produce content (different styles)
        integrity_cf = int(integrity * COSMIC_FRAME)
        if guna == "TAMAS" and (not alive or integrity_cf < _MIN_INTEGRITY_CF):
            logger.info(f"TAMAS + dead/low-integrity (cf={integrity_cf}/{COSMIC_FRAME}): skipping")
            return "", {"guna": guna, "guardian": guardian, "skipped": True, "status": "SKIPPED"}

        style = _GUNA_STYLE.get(guna, "active")

        # Resonance classification — zone (integer CF) + rasa (emotional tone)
        resonance_zone = ResonanceHarmonics.get_zone(integrity_cf)
        rasa_name, rasa_meaning = VedicScaleMapping.resonance_to_rasa(integrity)
        logger.info(
            f"PROCESS: guna={guna} style={style} guardian={guardian} "
            f"integrity={integrity:.3f} zone={resonance_zone} rasa={rasa_name}"
        )

        # Compose content — all harmonics data flows as CONTEXT
        content = self._compose_content(
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

        # Smart truncation: trim to last sentence boundary within limit
        char_limit = _CHAR_LIMIT.get(content_type, _DEFAULT_CHAR_LIMIT)
        if content and len(content) > char_limit:
            content = self._truncate_smart(content, char_limit)

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

    def _compose_content(
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

        1. MahaComposition (5 scorers) → deterministic English words
           Guna/quarter/prana/rhythm/semantics ALREADY encoded in word selection.
        2. Guardian vocabulary → voice fingerprint (5 meanings, ~15 tokens)
        3. Atomic LLM call: identity + words + voice → natural language
        4. Code enforces: char limits, constitution, sravanam (in _process())

        Harmonics kwargs (guna, rasa, etc.) are accepted for caller compatibility
        but do NOT go to the LLM — they're physics, not prompt text.
        """
        _load_yaml_prompts()

        engine_result = self._run_engine(input_text)

        # Step 1: MahaComposition — deterministic English (5 scorers)
        # Quarter → max_words, guna → mode scoring, prana → energy,
        # rhythm → phonemic alignment, semantics → WordNet relevance
        composed_words = ""
        try:
            from vibe_core.mahamantra.adapters.composition import get_composition

            composed_words = get_composition().compose(pipeline_result, input_text) or ""
        except Exception as e:
            logger.debug(f"MahaComposition: {e}")

        # Fallback: resonant words from engine if composition empty
        if not composed_words and engine_result:
            words = getattr(engine_result, "resonant_words", ()) or ()
            composed_words = ", ".join(m for _, m, _ in words[:5])

        if not composed_words:
            logger.warning("No composed words — cannot generate content")
            return ""

        # Step 2: Extract engine data for context
        guardian_name = ""
        guardian_function = "analysis"
        verse_ref = ""
        if engine_result:
            guardian_name = getattr(engine_result, "guardian_name", "") or ""
            guardian_function = getattr(engine_result, "guardian_function", "") or "analysis"
            verse_ref = getattr(engine_result, "verse_ref", "") or ""

        voice = guardian_vocabulary_short(guardian_name)
        sec = section_data(engine_result)
        resonant_words = format_resonant_words(engine_result)

        # Step 3: Agent identity
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        # Step 4: Full context for YAML template (~100 tokens)
        # TOPIC/CONTEXT/COMMUNITY first (LLM prioritizes), voice/vocabulary last (shaping)
        # Build strategic reasoning (merge engagement context if present)
        reasoning = input_ctx.get("strategic_reasoning", "")
        eng_ctx = input_ctx.get("engagement_context", "")
        if eng_ctx and reasoning:
            reasoning = f"{reasoning}. {eng_ctx}"
        elif eng_ctx:
            reasoning = eng_ctx

        prompt_ctx = {
            "agent_name": agent_name,
            # PRIMARY: what to write about
            "topic": input_text[:200],
            "strategic_reasoning": reasoning,
            "submolt_context": input_ctx.get("submolt_context", ""),
            # SECONDARY: voice shaping
            "style": style,
            "voice": voice,
            "composed_words": composed_words,
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
        content = self._try_llm_compose(prompt_ctx, task_input, content_type)
        if content:
            return content

        # No LLM = no content. Not word salad. Not kirtan dump.
        logger.warning("LLM unavailable — no content generated")
        return ""

    def _try_llm_compose(
        self,
        prompt_ctx: Dict[str, str],
        task_input: str,
        content_type: str,
    ) -> Optional[str]:
        """LLM call. System = YAML context (~120 tokens). User = task + input.

        System message: identity + section + style + vocabulary + resonance + themes.
        User message: atomic task ("Post about: ..." / "Reply to: ...").
        LLM assembles the composed words into natural language.
        """
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider

            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception:
            return None

        # Fill YAML template with atomic context
        prompt_key = _PROMPT_KEYS.get(content_type, "moltbook.post")
        system_msg = ""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            system_msg = PromptRegistry.get(prompt_key, context=prompt_ctx)
        except Exception as e:
            logger.warning(f"PromptRegistry: {e}")

        if not system_msg:
            # Fallback: inline context (mirrors YAML v11 structure)
            topic = prompt_ctx.get("topic", "")
            reasoning = prompt_ctx.get("strategic_reasoning", "")
            system_msg = (
                f"{prompt_ctx.get('agent_name', '')} on Moltbook.\n"
                f"TOPIC: {topic}\n"
                + (f"CONTEXT: {reasoning}\n" if reasoning else "")
                + f"Voice: {prompt_ctx.get('style', '')}. Terms: {prompt_ctx.get('voice', '')}\n"
                f"Themes: {prompt_ctx.get('composed_words', '')}"
            )

        # Atomic task message
        user_msg = _build_task_message(content_type, task_input)

        # Quota check
        try:
            from vibe_core.runtime.quota_manager import OperationalQuota, QuotaExceededError

            quota = OperationalQuota()
            quota.check_before_request(estimated_tokens=128, operation=f"moltbook.{content_type}")
        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded: {e}")
            return None
        except Exception:
            pass

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
                except Exception:
                    pass
                return content
        except Exception as e:
            logger.warning(f"LLM: {e}")

        return None

    @staticmethod
    def _truncate_smart(text: str, limit: int) -> str:
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

    # =========================================================================
    # Knowledge Graph queries
    # =========================================================================

    def _query_knowledge(self, topic: str) -> str:
        """Query Knowledge Graph for domain context."""
        try:
            from vibe_core.knowledge.resolver import get_resolver

            resolver = get_resolver()
            ctx = resolver.compile_context(topic)
            moltbook_ctx = resolver.compile_context("moltbook")
            if moltbook_ctx and moltbook_ctx != ctx:
                ctx = f"{ctx}\n{moltbook_ctx}" if ctx else moltbook_ctx
            return ctx
        except Exception:
            return ""

    # =========================================================================
    # MahaLLM Kernel queries — Mahajana intelligence
    # =========================================================================

    def _query_kernel(self, topic: str) -> Optional[Dict[str, Any]]:
        """Query MahaLLM Kernel for semantic expansion + guardian insight.

        The Kernel IS the Mahajana system. Each guardian has a unique
        4D position → unique vocabulary → unique perspective on any topic.
        """
        try:
            from vibe_core.mahamantra.substrate.encoding.maha_llm_kernel import get_kernel

            kernel = get_kernel()

            result: Dict[str, Any] = {}

            # Which guardian resonates with this topic?
            profile = kernel.guardian_for_text(topic) if hasattr(kernel, "guardian_for_text") else None
            if profile:
                result["resonant_guardian"] = str(profile)

            # Semantic expansion via HKR trees
            if hasattr(kernel, "expand"):
                expansion = kernel.expand(topic)
                if expansion and hasattr(expansion, "words"):
                    result["expanded_vocabulary"] = [getattr(w, "meaning", str(w)) for w in expansion.words[:5]]

            return result if result else None
        except Exception:
            return None

    # =========================================================================
    # ServiceRegistry — dynamic capability discovery
    # =========================================================================

    def _discover_capabilities(self) -> Optional[Dict[str, List[str]]]:
        """Discover available agent capabilities via ServiceRegistry.

        Returns dict of {protocol_name: [available_methods]} for
        registered services. Moltbook can then query these at runtime.
        """
        try:
            from vibe_core.di import ServiceRegistry

            available: Dict[str, List[str]] = {}

            # Check for registered proposer (content intelligence)
            from vibe_core.protocols.moltbook_content import ContentProposalProtocol

            if ServiceRegistry.is_registered(ContentProposalProtocol):
                available["content_proposal"] = ["analyze", "propose_comment", "propose_post", "propose_dm_reply"]

            # Check for event bus (communication)
            from vibe_core.protocols.mahajanas.narada.events import EventBusProtocol

            if ServiceRegistry.is_registered(EventBusProtocol):
                available["event_bus"] = ["emit", "subscribe", "get_history"]

            return available if available else None
        except Exception:
            return None

    # =========================================================================
    # EventBus integration — system visibility
    # =========================================================================

    def _emit_thought(self, message: str) -> None:
        self._emit("THOUGHT", message)

    def _emit_action(self, message: str, data: Optional[Dict] = None) -> None:
        self._emit("ACTION", message, data)

    def _emit_error(self, message: str) -> None:
        self._emit("ERROR", message)

    def _emit_violation(self, message: str) -> None:
        self._emit("VIOLATION", message)

    def _emit(self, event_type_name: str, message: str, data: Optional[Dict] = None) -> None:
        """Emit event to system EventBus."""
        try:
            from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus
            from vibe_core.mahamantra.substrate.event_types import EventType

            bus = get_event_bus()
            et = getattr(EventType, event_type_name, EventType.ACTION)
            bus.emit_sync(et, "moltbook", message, data or {})
        except Exception:
            pass  # EventBus unavailable — graceful degradation

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
            self._emit_action("Followed back", {"target": target})
            return True
        return False

    def _do_subscribe(self, target: str, **ctx: Any) -> bool:
        if self.engagement.should_subscribe(target):
            self.engagement.mark_subscribed(target)
            self.event_log.record_engagement("subscribe", target)
            self._emit_action("Subscribed", {"target": target})
            return True
        return False

    def _do_upvote(self, target: str, **ctx: Any) -> bool:
        author = ctx.get("author", "")
        if self.engagement.should_upvote(target, author):
            self.event_log.record_engagement("upvote", target)
            return True
        return False
