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

from .context_builders import build_moltbook_context

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
    phase: str   # INPUT, PROCESS, VALIDATE, OUTPUT
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
    "SATTVA": "contemplative",   # wisdom, reflection, philosophical depth
    "RAJAS": "active",           # engagement, creation, direct action
    "TAMAS": "transformative",   # cleanup, restructuring (if allowed at all)
}

# =========================================================================
# Intent quarter → response style (MantraOpCode quarters, opcode.py)
# =========================================================================

_INTENT_QUARTER = {
    "SYS_WAKE": "genesis", "LOAD_ROOT": "genesis",
    "ALLOC_MEM": "genesis", "INIT_THREAD": "genesis",
    "COMPILE_AST": "dharma", "BIND_SYMBOL": "dharma",
    "TYPE_CHECK": "dharma", "DHARMA_TEST": "dharma",
    "EXEC_OP": "karma", "EXTEND_CAP": "karma",
    "STATE_SYNC": "karma", "LEDGER_SIGN": "karma",
    "YIELD_CPU": "moksha", "IO_FLUSH": "moksha",
    "LOG_EMIT": "moksha", "AUDIT_SEAL": "moksha",
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

_MOLTBOOK_YAML = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "config" / "prompts" / "moltbook.yaml"

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
                status="ERROR", phase="INPUT", cycle_id=cycle_id,
                content_type=content_type, error=str(e), duration_ms=elapsed,
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
                status="ERROR", phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error=str(e), duration_ms=elapsed,
            )

        if not content:
            elapsed = (time.monotonic() - t0) * 1000
            # Distinguish TAMAS skip from LLM unavailability
            status = process_ctx.get("status", "ERROR")
            if process_ctx.get("skipped"):
                status = "SKIPPED"
                self.feedback.signal_partial(feedback_cmd, "tamas_skip", {
                    "guna": process_ctx.get("guna", ""), "guardian": process_ctx.get("guardian", ""),
                })
            elif status == "LLM_UNAVAILABLE":
                self.feedback.signal_failure(feedback_cmd, "llm_unavailable", {
                    "guna": process_ctx.get("guna", ""), "guardian": process_ctx.get("guardian", ""),
                }, duration_ms=elapsed)
            else:
                self.feedback.signal_failure(feedback_cmd, "no_content", process_ctx, duration_ms=elapsed)
            return CycleResult(
                status=status, phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error=process_ctx.get("error", "No content generated"),
                guna=process_ctx.get("guna", ""), guardian=process_ctx.get("guardian", ""),
                duration_ms=elapsed,
            )

        guna = process_ctx.get("guna", "")
        guardian = process_ctx.get("guardian", "")
        self.event_log.record_content_generated(content_type, content)
        self._emit_action(f"Generated {content_type}", {
            "content_type": content_type, "guna": guna, "guardian": guardian,
            "length": len(content),
            "zone": process_ctx.get("resonance_zone", ""),
            "rasa": process_ctx.get("rasa", ""),
        })

        # ===== VALIDATE =====
        validation = self.constitution.validate(content, content_type)
        if not validation.is_valid:
            logger.info(f"VALIDATE failed: {validation.violations}")
            self.event_log.record_content_rejected(
                content, "governance_violation", validation.violations
            )
            self.event_log.store_validation_feedback(validation.violations, content)
            self._emit_violation(f"Content rejected: {validation.violations[:2]}")
            elapsed = (time.monotonic() - t0) * 1000
            self.feedback.signal_failure(feedback_cmd, "governance_violation", {
                "guna": guna, "guardian": guardian, "violations": validation.violations[:3],
            }, duration_ms=elapsed)
            return CycleResult(
                status="VALIDATION_FAILED", phase="VALIDATE", cycle_id=cycle_id,
                content_type=content_type, content=content,
                violations=validation.violations, guna=guna, guardian=guardian,
                duration_ms=elapsed,
            )

        if validation.warnings:
            logger.info(f"VALIDATE warnings: {validation.warnings}")

        # ===== OUTPUT =====
        elapsed = (time.monotonic() - t0) * 1000
        self.feedback.signal_success(feedback_cmd, {
            "guna": guna, "guardian": guardian, "length": len(content),
        }, duration_ms=elapsed)
        self._emit("COMPLETED", f"Content generated: {content_type}", {
            "content_type": content_type, "guna": guna, "guardian": guardian,
            "length": len(content), "duration_ms": elapsed,
        })
        return CycleResult(
            status="SUCCESS", phase="OUTPUT", cycle_id=cycle_id,
            content_type=content_type, content=content,
            guna=guna, guardian=guardian, duration_ms=elapsed,
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
            status="ERROR", phase="UNKNOWN",
            cycle_id=datetime.now(timezone.utc).isoformat(),
            content_type=content_type, error="Retry loop exhausted",
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

        # Circuit executor primary (if plugin wired and has circuit)
        try:
            executor = getattr(self._plugin, "execute_content_circuit", None) if self._plugin else None
            if executor:
                result = executor(
                    seed_text, content_type,
                    post_id=ctx.get("post_id", ""),
                    sender=ctx.get("sender", ""),
                    trigger=ctx.get("trigger", "agency"),
                )
                if result and result.get("content"):
                    return result["content"], {
                        "source": "circuit",
                        "guna": result.get("guna", "RAJAS"),
                        "guardian": result.get("guardian", "unknown"),
                        "integrity": result.get("integrity", 1.0),
                        "resonance_zone": result.get("resonance_zone", ""),
                        "rasa": result.get("rasa", ""),
                    }
        except Exception as e:
            logger.debug(f"Circuit executor unavailable: {e}")

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
            pipeline_result, seed_text, content_type, input_ctx,
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
                input_tokens, output_tokens, integrity,
            )
            if not sravanam_ok:
                safe_size = SravanamCheck.compute_safe_output_size(input_tokens)
                logger.info(
                    f"SravanamCheck advisory: {sravanam_reason} "
                    f"(safe_output={safe_size}, actual={output_tokens})"
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
        """Compose content via LLM. No LLM = no content.

        Uses build_moltbook_context() → PromptRegistry.get() → LLM.
        MahaComposition provides semantic context for the prompt.
        All orchestration data (guna, rasa, zone) flows as CONTEXT, not instructions.
        """
        _load_yaml_prompts()

        engine_result = self._run_engine(input_text)

        # MahaComposition: semantic context for LLM (NOT standalone output)
        composed_words = ""
        try:
            from vibe_core.mahamantra.adapters.composition import get_composition
            composed_words = get_composition().compose(pipeline_result, input_text) or ""
        except Exception as e:
            logger.debug(f"MahaComposition unavailable: {e}")

        # Determine agent name from plugin or default
        agent_name = "steward-protocol"
        if self._plugin and hasattr(self._plugin, "_agent_name"):
            agent_name = self._plugin._agent_name

        # Content-type-specific extra context slots (for YAML template)
        extra: Dict[str, str] = {
            "guna": guna,
            "style": style,
            "resonance_zone": resonance_zone,
            "rasa_name": rasa_name,
            "rasa_meaning": rasa_meaning,
            "sravanam_status": sravanam_status,
            "composed_words": composed_words,
        }

        # Map intent category → quarter (data for context, not instruction)
        if engine_result:
            intent_cat = getattr(engine_result, "intent_category", "") or ""
            quarter = _INTENT_QUARTER.get(intent_cat, "")
            if quarter:
                extra["intent_quarter"] = quarter

        # Content-type-specific slots from input_ctx
        extra["sender"] = str(input_ctx.get("sender", ""))
        extra["trigger"] = str(input_ctx.get("trigger", content_type))
        extra["post_content"] = str(input_ctx.get("raw_input", input_text))[:500]

        # Retry feedback as context
        prev_violations = input_ctx.get("previous_violations", [])
        if prev_violations:
            extra["previous_violations"] = "; ".join(str(v) for v in prev_violations[:3])

        content = self._try_llm_compose(
            engine_result, pipeline_result, input_text,
            content_type, agent_name, extra,
        )
        if content:
            return content

        # No LLM = no content. Not word salad. Not kirtan dump.
        logger.warning("LLM unavailable — no content generated")
        return ""

    def _try_llm_compose(
        self,
        engine_result,
        pipeline_result: dict,
        input_text: str,
        content_type: str,
        agent_name: str,
        extra: Dict[str, str],
    ) -> Optional[str]:
        """Build context → fill YAML template → LLM.

        Context comes from build_moltbook_context() (shared with ResonanceProposer).
        Template comes from PromptRegistry.get() (config/prompts/moltbook.yaml).
        No hardcoded instructions. Dense context does the work.
        """
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider
            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception:
            return None

        # Build full context dict from all systems
        ctx = build_moltbook_context(
            engine_result, agent_name, input_text,
            pipeline_result=pipeline_result,
            **extra,
        )

        # Get prompt from YAML template via PromptRegistry
        prompt_key = _PROMPT_KEYS.get(content_type, "moltbook.post")
        prompt = ""
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry
            prompt = PromptRegistry.get(prompt_key, context=ctx)
        except Exception as e:
            logger.warning(f"PromptRegistry failed for {prompt_key}: {e}")

        if not prompt:
            # Fallback: structured context without YAML template
            prompt = (
                f"{ctx.get('guardian_name', '')} · {ctx.get('quarter', '')} · {ctx.get('guardian_function', '')}\n"
                f"Sektion: {ctx.get('section_name', '')} ({ctx.get('section_semantic', '')}) | "
                f"Modus: {ctx.get('section_mode', '')}\n"
                f"Vers: {ctx.get('verse_ref', '')} | Intent: {ctx.get('intent_category', '')}\n"
                f"Guna: {ctx.get('guna', '')} ({ctx.get('style', '')}) | "
                f"Zone: {ctx.get('resonance_zone', '')}\n"
                f"Rasa: {ctx.get('rasa_name', '')} ({ctx.get('rasa_meaning', '')})\n"
                f"VOKABULAR: {ctx.get('guardian_vocabulary', '')}\n"
                f"RESONANZ: {ctx.get('resonant_words', '')}\n"
                f"ANALYSE: {ctx.get('engine_output', '')}\n"
                f"{ctx.get('knowledge_context', '')}\n"
                f"{input_text}\n"
                f"{agent_name}:\n"
            )

        # Quota check before LLM call
        try:
            from vibe_core.runtime.quota_manager import OperationalQuota, QuotaExceededError
            quota = OperationalQuota()
            quota.check_before_request(estimated_tokens=512, operation=f"moltbook.{content_type}")
        except QuotaExceededError as e:
            logger.warning(f"Quota exceeded: {e}")
            return None
        except Exception as e:
            logger.debug(f"QuotaManager unavailable: {e}")

        try:
            response = provider.invoke(
                prompt="",
                model=None,  # Use config default (sonnet), NOT models[0] (opus)
                max_tokens=256,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text},
                ],
            )
            if response and response.content and not response.content.startswith("# ERROR"):
                content = response.content.strip()
                # Record usage after successful call
                try:
                    quota.record_request(
                        tokens_used=len(content.split()) + len(prompt.split()),
                        cost_usd=0.01,
                        operation=f"moltbook.{content_type}",
                    )
                except Exception as e:
                    logger.debug(f"Quota recording failed: {e}")
                return content
        except Exception as e:
            logger.warning(f"LLM failed: {e}")

        return None

    @staticmethod
    def _truncate_smart(text: str, limit: int) -> str:
        """Truncate to last sentence boundary within limit."""
        if len(text) <= limit:
            return text
        truncated = text[:limit]
        # Find last sentence boundary
        for sep in ('. ', '! ', '? ', '; ', ' — '):
            idx = truncated.rfind(sep)
            if idx > limit // 2:
                return truncated[:idx + 1].rstrip()
        # No sentence boundary — cut at last space
        idx = truncated.rfind(' ')
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
                    result["expanded_vocabulary"] = [
                        getattr(w, "meaning", str(w)) for w in expansion.words[:5]
                    ]

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
