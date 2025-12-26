"""
OPUS-309 + OPUS-310 + OPUS-311: MANASCognitive Adapter

Implements OperatorCognitiveProtocol for the OPUS Assistant plugin.

Bridges:
- IntentMatcher (OPUS-310: intent → command via CommandRegistry)
- JnanaHandler (intelligent chat responses)
- BlueprintGenerator (intent → syscall)
- VedaPipeline (SHABDA → ARTHA → PRATYAYA → KARMA)

OPUS-311 Sprint 3: Autonomy Protocols
- MemoryProtocol: Session context, entity resolution ("the second one")
- FeedbackProtocol: Pain/pleasure signals for learning
- ReflectionProtocol: Pattern analysis, improvement proposals

PROMPT.md: "Protocol statt konkrete Klassen"
GAD-000: AI operates the system on behalf of human.

Flow (OPUS-310 Phase 4):
1. Try IntentMatcher against CommandRegistry (no LLM, pure semantic)
2. Try BlueprintGenerator for complex syscalls (LLM-based)
3. Fall back to JnanaHandler for chat

Usage:
    # In plugin_main.py on_boot():
    from .cognitive import MANASCognitive
    kernel.register_cognitive(MANASCognitive(workspace=kernel.workspace_path))
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.cognition import (
    CognitiveContext,
    CognitiveResult,
    OperatorCognitiveProtocol,
)
from vibe_core.protocols.cognition import (
    IntentType as CognitiveIntentType,
)
from vibe_core.protocols.feedback import (
    FeedbackProtocol,
    get_feedback_safe,
)
from vibe_core.protocols.intent import IntentMatcherProtocol, NullIntentMatcher

# OPUS-311 Sprint 3: Autonomy Protocols
from vibe_core.protocols.memory import (
    Entity,
    MemoryProtocol,
    get_memory_safe,
)
from vibe_core.protocols.reflection import (
    ExecutionRecord,
    ReflectionProtocol,
    get_reflection_safe,
)

logger = logging.getLogger("MANAS.Cognitive")


class MANASCognitive:
    """
    OPUS-309: Implements OperatorCognitiveProtocol.

    This is the bridge between:
    - Kernel's process_operator_input()
    - MANAS's JnanaHandler + BlueprintGenerator

    The Kernel doesn't know MANAS exists.
    The Kernel only knows this implements OperatorCognitiveProtocol.
    """

    def __init__(self, workspace: Optional[Path] = None, kernel: Optional[Any] = None):
        """
        Initialize MANASCognitive.

        Args:
            workspace: Workspace path for context
            kernel: Optional kernel reference for advanced features
        """
        self._workspace = workspace or Path.cwd()
        self._kernel = kernel
        self._jnana_handler = None  # Lazy loaded
        self._blueprint_generator = None  # Lazy loaded
        self._intent_matcher: Optional[IntentMatcherProtocol] = None  # OPUS-310 Phase 4
        self._command_registry = None  # Lazy loaded

        # OPUS-311 Sprint 3: Autonomy Protocols (DI with fallbacks)
        self._memory: MemoryProtocol = get_memory_safe()
        self._feedback: FeedbackProtocol = get_feedback_safe()
        self._reflection: ReflectionProtocol = get_reflection_safe()

        logger.info(f"🧠 MANASCognitive initialized (workspace: {self._workspace})")
        logger.debug("🧠 Autonomy protocols: Memory, Feedback, Reflection")

    def _ensure_jnana_handler(self):
        """Lazy-load JnanaHandler."""
        if self._jnana_handler is None:
            try:
                from .manas.cortex.jnana import JnanaHandler

                self._jnana_handler = JnanaHandler(workspace=self._workspace)
                logger.debug("🧠 JnanaHandler loaded")
            except ImportError as e:
                logger.warning(f"🧠 JnanaHandler not available: {e}")
        return self._jnana_handler

    def _ensure_blueprint_generator(self):
        """Lazy-load BlueprintGenerator."""
        if self._blueprint_generator is None:
            try:
                from vibe_core.cartridges.system.envoy.blueprint_generator import (
                    BlueprintGenerator,
                    create_blueprint_generator,
                )

                self._blueprint_generator = create_blueprint_generator(self._kernel)
                logger.debug("🧠 BlueprintGenerator loaded")
            except ImportError as e:
                logger.warning(f"🧠 BlueprintGenerator not available: {e}")
        return self._blueprint_generator

    def _ensure_intent_matcher(self) -> IntentMatcherProtocol:
        """
        OPUS-310 Phase 4: Lazy-load IntentMatcher.

        Arjuna-Pattern: Falls back to NullIntentMatcher on failure.
        """
        if self._intent_matcher is None:
            try:
                from vibe_core.cli.intent_matcher import CommandAwareIntentMatcher

                self._intent_matcher = CommandAwareIntentMatcher()
                logger.debug("🧠 CommandAwareIntentMatcher loaded")
            except ImportError as e:
                logger.warning(f"🧠 IntentMatcher not available: {e}")
                self._intent_matcher = NullIntentMatcher()
        return self._intent_matcher

    def _ensure_command_registry(self):
        """
        OPUS-310: Lazy-load CommandRegistry.

        Single source of truth for all commands.
        Triggers scan_all() if not already scanned.
        """
        if self._command_registry is None:
            try:
                from vibe_core.cli.command_registry import CommandRegistry

                self._command_registry = CommandRegistry.get_instance()

                # Ensure commands are scanned
                stats = self._command_registry.stats()
                if stats["total"] == 0:
                    self._command_registry.scan_all()
                    stats = self._command_registry.stats()

                logger.debug(f"🧠 CommandRegistry loaded ({stats['total']} commands)")
            except ImportError as e:
                logger.warning(f"🧠 CommandRegistry not available: {e}")
        return self._command_registry

    def _resolve_entity_references(self, intent: str, session_id: Optional[str]) -> tuple[str, Optional[Entity]]:
        """
        OPUS-311: Resolve entity references like "the second one".

        Uses MemoryProtocol to look up last entities from session.

        Returns:
            (resolved_intent, resolved_entity) - entity is None if no reference found
        """
        if not session_id:
            return intent, None

        # Check for ordinal references
        ordinal_patterns = [
            "the first",
            "the second",
            "the third",
            "the fourth",
            "the fifth",
            "the last",
            "that one",
            "the one",
            "it",
        ]

        intent_lower = intent.lower()
        for pattern in ordinal_patterns:
            if pattern in intent_lower:
                entity = self._memory.resolve_reference(pattern, session_id)
                if entity:
                    # Replace reference with entity name/id
                    resolved = intent_lower.replace(pattern, entity.name)
                    logger.debug(f"🧠 Resolved '{pattern}' → '{entity.name}'")
                    return resolved, entity

        return intent, None

    def _remember_result_entities(
        self,
        result: CognitiveResult,
        session_id: Optional[str],
    ) -> None:
        """
        OPUS-311: Extract and remember entities from result.

        Enables future "the second one" resolution.
        """
        if not session_id:
            return

        # Try to extract entities from syscall_params or response
        entities = []

        # Check if result contains agent list
        if result.syscall_params and "agents" in result.syscall_params:
            agents = result.syscall_params["agents"]
            if isinstance(agents, list):
                for i, agent in enumerate(agents):
                    name = agent.get("name", agent) if isinstance(agent, dict) else str(agent)
                    entities.append(
                        Entity(
                            type="agent",
                            id=str(i),
                            name=name,
                            position=i + 1,
                        )
                    )

        # Check if result contains task list
        if result.syscall_params and "tasks" in result.syscall_params:
            tasks = result.syscall_params["tasks"]
            if isinstance(tasks, list):
                for i, task in enumerate(tasks):
                    name = task.get("id", task) if isinstance(task, dict) else str(task)
                    entities.append(
                        Entity(
                            type="task",
                            id=str(i),
                            name=name,
                            position=i + 1,
                        )
                    )

        if entities:
            self._memory.remember_entities(entities, session_id)
            logger.debug(f"🧠 Remembered {len(entities)} entities for session {session_id}")

    def record_execution_result(
        self,
        command: str,
        args: List[str],
        success: bool,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        session_id: Optional[str] = None,
    ) -> None:
        """
        OPUS-311: Record execution result for learning.

        Called after command execution to:
        1. Signal Feedback (pain/pleasure)
        2. Record in Reflection (pattern analysis)

        This enables the Autonomy Loop to learn from experience.
        """
        context = {"args": args, "session_id": session_id}

        # Signal Feedback
        if success:
            self._feedback.signal_success(command, context, duration_ms, session_id)
        else:
            self._feedback.signal_failure(command, error or "unknown", context, duration_ms, session_id)

        # Record for Reflection
        record = ExecutionRecord(
            command=command,
            args=args,
            success=success,
            error=error,
            duration_ms=duration_ms,
            session_id=session_id,
            context=context,
        )
        self._reflection.record_execution(record)

        logger.debug(f"🧠 Recorded execution: {command} ({'✅' if success else '❌'})")

    async def _try_command_match(self, intent: str, session_id: Optional[str] = None) -> Optional[CognitiveResult]:
        """
        OPUS-310 Phase 4: Try to match intent to a command.

        OPUS-311: Now resolves entity references and checks failure patterns.

        Uses CommandRegistry + IntentMatcher.
        No LLM calls - pure semantic matching.

        Returns:
            CognitiveResult if high/medium confidence match
            None if no match (falls through to next handler)
        """
        registry = self._ensure_command_registry()
        matcher = self._ensure_intent_matcher()

        if not registry:
            return None

        # OPUS-311: Resolve entity references ("the second one" → "archivist")
        resolved_intent, resolved_entity = self._resolve_entity_references(intent, session_id)
        if resolved_entity:
            logger.debug(f"🧠 Resolved entity: {resolved_entity.name} ({resolved_entity.type})")

        # Get all commands from registry
        commands = registry.list_commands()
        if not commands:
            return None

        # Match intent to commands (use resolved intent)
        matches = matcher.match(resolved_intent, commands)
        if not matches:
            logger.debug(f"🧠 IntentMatcher: no matches for '{resolved_intent}'")
            return None

        best = matches[0]
        logger.debug(f"🧠 IntentMatcher: best match '{best.command.name}' ({best.confidence:.0%})")

        # OPUS-311: Check for failure warnings
        warning = self._feedback.should_warn(best.command.name, {"intent": intent})
        if warning:
            logger.warning(f"🧠 Feedback warning: {warning}")
            # Add warning to reasoning but don't block execution
            best_reasoning = f"{best.reasoning} (⚠️ {warning})"
        else:
            best_reasoning = best.reasoning

        # High confidence → Execute
        if best.confidence >= 0.8:
            # If we resolved an entity, inject it into params
            params = best.extracted_params.copy() if best.extracted_params else {}
            if resolved_entity:
                params["_resolved_entity"] = {
                    "type": resolved_entity.type,
                    "id": resolved_entity.id,
                    "name": resolved_entity.name,
                }

            return CognitiveResult(
                intent_type=CognitiveIntentType.EXECUTE,
                confidence=best.confidence,
                syscall_type=best.command.name,
                syscall_params=params,
                reasoning=f"IntentMatcher: {best_reasoning}",
            )

        # Medium confidence → Suggest options
        if best.confidence >= 0.5:
            suggestions = [m.command.name for m in matches[:3]]
            suggestion_text = f"Did you mean: {', '.join(suggestions)}?"
            return CognitiveResult(
                intent_type=CognitiveIntentType.QUERY,
                confidence=best.confidence,
                response=suggestion_text,
                reasoning=f"IntentMatcher (medium confidence): {best_reasoning}",
            )

        # Low confidence → Fall through to next handler
        logger.debug(f"🧠 IntentMatcher: low confidence ({best.confidence:.0%}), falling through")
        return None

    async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
        """
        Process natural language intent.

        OPUS-309 + OPUS-310 + OPUS-311: Main entry point from Kernel.
        Decides: chat, execute, query, or route.

        The flow (OPUS-310 Phase 4 + OPUS-311):
        1. Resolve entity references ("the second one" → "archivist")
        2. Try IntentMatcher against CommandRegistry (no LLM, pure semantic)
        3. Try BlueprintGenerator for complex syscalls (LLM-based)
        4. Fall back to JnanaHandler for chat
        5. Remember entities from result for future reference
        """
        session_id = context.session_id

        # OPUS-310 Phase 4: Try command matching FIRST (no LLM required)
        # OPUS-311: Pass session_id for entity resolution
        command_match = await self._try_command_match(intent, session_id)
        if command_match:
            # OPUS-311: Remember entities from result
            self._remember_result_entities(command_match, session_id)
            return command_match

        # Try to detect execution intent via BlueprintGenerator (LLM-based)
        blueprint_gen = self._ensure_blueprint_generator()
        if blueprint_gen:
            try:
                # BlueprintGenerator has pattern matching for syscalls
                blueprint = await blueprint_gen.generate_blueprint(
                    raw_input=intent, context={"source": "cognitive_protocol"}
                )

                if blueprint and blueprint.get("syscall_type"):
                    # Execution intent detected
                    return CognitiveResult(
                        intent_type=CognitiveIntentType.EXECUTE,
                        confidence=blueprint.get("confidence", 0.8),
                        syscall_type=blueprint.get("syscall_type"),
                        syscall_params=blueprint.get("params", {}),
                        reasoning=f"BlueprintGenerator detected: {blueprint.get('syscall_type')}",
                    )
            except Exception as e:
                logger.debug(f"🧠 BlueprintGenerator check: {e}")

        # Fall back to chat response via JnanaHandler
        jnana = self._ensure_jnana_handler()
        if jnana:
            try:
                # JnanaHandler generates intelligent responses
                response = await self._generate_jnana_response(intent, context)
                return CognitiveResult(
                    intent_type=CognitiveIntentType.CHAT,
                    confidence=0.9,
                    response=response,
                    reasoning="JnanaHandler chat response",
                )
            except Exception as e:
                logger.warning(f"🧠 JnanaHandler failed: {e}")

        # Ultimate fallback: Route to Envoy
        return CognitiveResult(
            intent_type=CognitiveIntentType.ROUTE,
            confidence=0.5,
            target="envoy",
            reasoning="No handler available, routing to Envoy",
        )

    async def _generate_jnana_response(self, prompt: str, context: CognitiveContext) -> str:
        """Generate response using JnanaHandler."""
        jnana = self._ensure_jnana_handler()
        if not jnana:
            return "[JnanaHandler not available]"

        try:
            # JnanaHandler.handle() takes SamvadaMessage, not (prompt, context)
            from .manas.cortex.samvada import SamvadaMessage

            # Build message with context in metadata
            msg = SamvadaMessage(
                content=prompt,
                msg_type="chat",
                metadata={
                    "kernel_status": context.kernel_status,
                    "active_agents": context.active_agents,
                    "pending_tasks": context.pending_tasks,
                    "session_id": context.session_id,
                },
            )

            # JnanaHandler.handle() is async and takes SamvadaMessage
            response = await jnana.handle(msg)

            # Extract content from SamvadaResponse
            if hasattr(response, "content"):
                return str(response.content)
            return str(response)
        except Exception as e:
            logger.error(f"🧠 JnanaHandler error: {e}")
            return f"[Error processing: {e}]"

    async def generate_response(self, prompt: str, context: CognitiveContext) -> str:
        """
        Generate intelligent response (for CHAT intents).

        Delegates to JnanaHandler.
        """
        return await self._generate_jnana_response(prompt, context)

    def get_capabilities(self) -> List[str]:
        """
        GAD-000: Discoverability.

        Returns capabilities this cognitive layer provides.
        """
        caps = ["chat", "intent_detection"]

        # OPUS-310 Phase 4: Intent matching via CommandRegistry
        registry = self._ensure_command_registry()
        if registry:
            stats = registry.stats()
            caps.append(f"command_matching ({stats['total']} commands)")

        if self._ensure_blueprint_generator():
            caps.extend(["syscall_generation", "spawn_cognition", "dispatch_task", "allocate_prana"])

        if self._ensure_jnana_handler():
            caps.extend(["intelligent_response", "context_aware_chat", "drift_detection", "knowledge_query"])

        # OPUS-311 Sprint 3: Autonomy protocols
        caps.extend(
            [
                "session_memory",  # MemoryProtocol
                "entity_resolution",  # "the second one" → agent
                "feedback_learning",  # FeedbackProtocol
                "pattern_detection",  # ReflectionProtocol
            ]
        )

        return caps

    def get_autonomy_stats(self) -> Dict[str, Any]:
        """
        OPUS-311: Get autonomy protocol statistics.

        Returns:
            Stats from Memory, Feedback, and Reflection protocols
        """
        return {
            "memory": self._memory.get_stats().__dict__,
            "feedback": self._feedback.get_stats().__dict__,
            "reflection": self._reflection.get_stats().__dict__,
        }
