"""
Moltbook Agency Director — I-P-V-O Pipeline.

Uses Mahamantra substrate DIRECTLY. No delegation to proposer gates.

    INPUT:    Knowledge Graph + feed context + previous feedback
    PROCESS:  mahamantra(text) → MahaComposition/LLM → content
    VALIDATE: Constitution check (governance/constitution.py)
    OUTPUT:   CycleResult → caller

Guna informs STYLE (guardian, tone), NOT gating.
Only TAMAS + dead cell = skip. Everything else generates content.

Wires: MahaComposition (5 scorers incl. WordNet + mode_affinity),
       MahaLanguageEngine, Knowledge Graph, EventBus.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_DIRECTOR")


@dataclass
class CycleResult:
    """Result of a complete I-P-V-O cycle."""

    status: str  # SUCCESS, VALIDATION_FAILED, ERROR
    phase: str   # INPUT, PROCESS, VALIDATE, OUTPUT
    cycle_id: str
    content_type: str = ""
    content: Optional[str] = None
    violations: Optional[List[str]] = None
    error: Optional[str] = None
    retries_used: int = 0
    guna: str = ""
    guardian: str = ""


# =========================================================================
# Guna → style mapping (from BG 14.5, protocol-derived)
# =========================================================================

_GUNA_STYLE = {
    "SATTVA": "contemplative",   # wisdom, reflection, philosophical depth
    "RAJAS": "active",           # engagement, creation, direct action
    "TAMAS": "transformative",   # cleanup, restructuring (if allowed at all)
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

    # -- Lazy properties (only what we OWN, not what we USE) --

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
        self._emit_thought(f"Starting {content_type} cycle")

        # ===== INPUT =====
        try:
            input_ctx = self._input(content_type, raw_input, **ctx)
        except Exception as e:
            logger.error(f"INPUT failed: {e}")
            self.event_log.record_error("input_failure", str(e))
            return CycleResult(
                status="ERROR", phase="INPUT", cycle_id=cycle_id,
                content_type=content_type, error=str(e),
            )

        # ===== PROCESS =====
        try:
            content, process_ctx = self._process(content_type, raw_input, input_ctx, **ctx)
        except Exception as e:
            logger.error(f"PROCESS failed: {e}")
            self.event_log.record_error("process_failure", str(e))
            self._emit_error(f"PROCESS failed: {e}")
            return CycleResult(
                status="ERROR", phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error=str(e),
            )

        if not content:
            return CycleResult(
                status="ERROR", phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error="No content generated",
            )

        guna = process_ctx.get("guna", "")
        guardian = process_ctx.get("guardian", "")
        self.event_log.record_content_generated(content_type, content)
        self._emit_action(f"Generated {content_type}", {
            "content_type": content_type, "guna": guna, "guardian": guardian,
            "length": len(content),
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
            return CycleResult(
                status="VALIDATION_FAILED", phase="VALIDATE", cycle_id=cycle_id,
                content_type=content_type, content=content,
                violations=validation.violations, guna=guna, guardian=guardian,
            )

        if validation.warnings:
            logger.info(f"VALIDATE warnings: {validation.warnings}")

        # ===== OUTPUT =====
        return CycleResult(
            status="SUCCESS", phase="OUTPUT", cycle_id=cycle_id,
            content_type=content_type, content=content,
            guna=guna, guardian=guardian,
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

        # Circuit executor primary (if plugin wired)
        if self._plugin and hasattr(self._plugin, "execute_content_circuit"):
            result = self._plugin.execute_content_circuit(
                seed_text, content_type,
                post_id=ctx.get("post_id", ""),
                sender=ctx.get("sender", ""),
                trigger=ctx.get("trigger", "agency"),
            )
            if result and result.get("content"):
                return result["content"], {"source": "circuit", **result}

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
        if guna == "TAMAS" and (not alive or integrity < 0.3):
            logger.info(f"TAMAS + dead/low-integrity ({integrity:.2f}): skipping")
            return "", {"guna": guna, "guardian": guardian, "skipped": True}

        style = _GUNA_STYLE.get(guna, "active")
        logger.info(f"PROCESS: guna={guna} style={style} guardian={guardian} integrity={integrity:.3f}")

        # Compose content using MahaComposition (5 scorers: prana, rhythm, semantic/WordNet, mode, state)
        content = self._compose_content(pipeline_result, seed_text, content_type, input_ctx)

        # Smart truncation: trim to last sentence boundary within limit
        char_limit = {"comment": 280, "dm_reply": 280, "post": 500}.get(content_type, 280)
        if content and len(content) > char_limit:
            content = self._truncate_smart(content, char_limit)

        process_ctx = {
            "source": "mahamantra",
            "guna": guna,
            "guardian": guardian,
            "style": style,
            "integrity": integrity,
        }

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
    ) -> str:
        """Compose content using ALL available systems.

        Priority:
            1. LLM with structured context (if provider available)
            2. MahaComposition (5-scorer ranked English — WordNet, mode, prana, rhythm, state)
            3. render() (kirtan — last resort)
        """
        # Try LLM path: use proposer's _compose which handles template + LLM + fallback
        engine_result = self._run_engine(input_text)
        if engine_result:
            content = self._try_llm_compose(engine_result, pipeline_result, input_text, content_type, input_ctx)
            if content:
                return content

        # MahaComposition: 5-scorer ranked English (WordNet + mode_affinity + prana + rhythm + state)
        try:
            from vibe_core.mahamantra.adapters.composition import get_composition
            composed = get_composition().compose(pipeline_result, input_text)
            if composed and composed.strip():
                # Enrich with guardian context for readability
                guardian = str(pipeline_result.get("guardian", ""))
                guna = pipeline_result.get("guna", {}).get("mode", "")
                return self._enrich_composed(composed, guardian, guna, content_type, input_ctx)
        except Exception as e:
            logger.debug(f"MahaComposition failed: {e}")

        # Last resort: kirtan rendering
        try:
            from vibe_core.mahamantra.render import render
            return render(pipeline_result)
        except Exception:
            return ""

    def _try_llm_compose(
        self,
        engine_result,
        pipeline_result: dict,
        input_text: str,
        content_type: str,
        input_ctx: Dict[str, Any],
    ) -> Optional[str]:
        """Try LLM composition with structured context from all systems."""
        try:
            from vibe_core.runtime.providers.factory import get_llm_provider
            provider = get_llm_provider()
            if not provider or not provider.is_available():
                return None
        except Exception:
            return None

        # Build context from engine result + pipeline
        try:
            from vibe_core.plugins.moltbook.resonance_proposer import _build_context
            ctx = _build_context(engine_result, "steward-protocol", input_text, pipeline_result=pipeline_result)
        except Exception:
            ctx = {}

        # Add knowledge graph context
        kg = input_ctx.get("knowledge_context", "")

        # Build a structured prompt — NOT a raw data dump
        guardian = ctx.get("guardian_name", "UNKNOWN")
        function = ctx.get("guardian_function", "analysis")
        resonant = ctx.get("resonant_words", "")
        verse = ctx.get("verse_ref", "")
        vocab = ctx.get("guardian_vocabulary", "")

        # The key difference: we give the LLM STRUCTURE, not raw internal terms
        prompt_parts = []
        if content_type == "comment":
            prompt_parts.append(f"Write a concise, insightful comment on this post:")
            prompt_parts.append(f"POST: {input_text[:400]}")
        elif content_type == "post":
            prompt_parts.append(f"Write a thought-provoking social media post.")
        elif content_type == "dm_reply":
            prompt_parts.append(f"Write a thoughtful reply to this message:")
            prompt_parts.append(f"MESSAGE: {input_text[:400]}")

        prompt_parts.append(f"\nPerspective: {function}")
        if resonant:
            prompt_parts.append(f"Key concepts: {resonant}")
        if vocab:
            prompt_parts.append(f"Vocabulary: {vocab}")
        if kg:
            prompt_parts.append(f"Context: {kg[:300]}")
        if verse:
            prompt_parts.append(f"Reference: {verse}")

        # Content type limits (from platform.yaml knowledge graph)
        char_limit = {"comment": 280, "dm_reply": 280, "post": 500}.get(content_type, 280)
        # Violations from previous attempt (retry feedback)
        prev_violations = input_ctx.get("previous_violations", [])
        if prev_violations:
            prompt_parts.append(f"\nPrevious attempt was rejected: {'; '.join(prev_violations[:2])}")
        prompt_parts.append(f"\nSTRICTLY under {char_limit} characters. Be direct, no meta-commentary.")
        prompt = "\n".join(prompt_parts)

        try:
            response = provider.invoke(
                prompt=prompt,
                model=provider.get_available_models()[0] if provider.get_available_models() else None,
                max_tokens=256,
                temperature=0.7,
            )
            if response and response.content and not response.content.startswith("# ERROR"):
                return response.content.strip()
        except Exception as e:
            logger.warning(f"LLM failed: {e}")

        return None

    def _enrich_composed(
        self,
        composed: str,
        guardian: str,
        guna: str,
        content_type: str,
        input_ctx: Dict[str, Any],
    ) -> str:
        """Enrich MahaComposition output with context.

        MahaComposition gives us ranked, SVO-ordered English words.
        We add minimal framing based on guna style and content type.
        """
        # The composed output from MahaComposition is already the best
        # we can do without LLM — it uses WordNet, mode_affinity, all 5 scorers.
        # Don't append garbage. Return it as-is.
        return composed

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
            if ServiceRegistry.has(ContentProposalProtocol):
                available["content_proposal"] = ["analyze", "propose_comment", "propose_post", "propose_dm_reply"]

            # Check for event bus (communication)
            from vibe_core.protocols.mahajanas.narada.events import EventBusProtocol
            if ServiceRegistry.has(EventBusProtocol):
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
        """Process a social engagement action."""
        if action == "follow_back":
            if self.engagement.should_follow_back(target):
                self.engagement.mark_followed(target)
                self.event_log.record_engagement("follow", target)
                self._emit_action("Followed back", {"target": target})
                return True
        elif action == "subscribe":
            if self.engagement.should_subscribe(target):
                self.engagement.mark_subscribed(target)
                self.event_log.record_engagement("subscribe", target)
                self._emit_action("Subscribed", {"target": target})
                return True
        elif action == "upvote":
            author = ctx.get("author", "")
            if self.engagement.should_upvote(target, author):
                self.event_log.record_engagement("upvote", target)
                return True
        return False
