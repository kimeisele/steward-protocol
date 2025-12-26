"""
OPUS-309 + OPUS-310: MANASCognitive Adapter

Implements OperatorCognitiveProtocol for the OPUS Assistant plugin.

Bridges:
- IntentMatcher (OPUS-310: intent → command via CommandRegistry)
- JnanaHandler (intelligent chat responses)
- BlueprintGenerator (intent → syscall)
- VedaPipeline (SHABDA → ARTHA → PRATYAYA → KARMA)

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
from vibe_core.protocols.intent import IntentMatcherProtocol, NullIntentMatcher

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

        logger.info(f"🧠 MANASCognitive initialized (workspace: {self._workspace})")

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

    async def _try_command_match(self, intent: str) -> Optional[CognitiveResult]:
        """
        OPUS-310 Phase 4: Try to match intent to a command.

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

        # Get all commands from registry
        commands = registry.list_commands()
        if not commands:
            return None

        # Match intent to commands
        matches = matcher.match(intent, commands)
        if not matches:
            logger.debug(f"🧠 IntentMatcher: no matches for '{intent}'")
            return None

        best = matches[0]
        logger.debug(f"🧠 IntentMatcher: best match '{best.command.name}' ({best.confidence:.0%})")

        # High confidence → Execute
        if best.confidence >= 0.8:
            return CognitiveResult(
                intent_type=CognitiveIntentType.EXECUTE,
                confidence=best.confidence,
                syscall_type=best.command.name,
                syscall_params=best.extracted_params,
                reasoning=f"IntentMatcher: {best.reasoning}",
            )

        # Medium confidence → Suggest options
        if best.confidence >= 0.5:
            suggestions = [m.command.name for m in matches[:3]]
            suggestion_text = f"Did you mean: {', '.join(suggestions)}?"
            return CognitiveResult(
                intent_type=CognitiveIntentType.QUERY,
                confidence=best.confidence,
                response=suggestion_text,
                reasoning=f"IntentMatcher (medium confidence): {best.reasoning}",
            )

        # Low confidence → Fall through to next handler
        logger.debug(f"🧠 IntentMatcher: low confidence ({best.confidence:.0%}), falling through")
        return None

    async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
        """
        Process natural language intent.

        OPUS-309 + OPUS-310: Main entry point from Kernel.
        Decides: chat, execute, query, or route.

        The flow (OPUS-310 Phase 4):
        1. Try IntentMatcher against CommandRegistry (no LLM, pure semantic)
        2. Try BlueprintGenerator for complex syscalls (LLM-based)
        3. Fall back to JnanaHandler for chat
        """
        # OPUS-310 Phase 4: Try command matching FIRST (no LLM required)
        command_match = await self._try_command_match(intent)
        if command_match:
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

        return caps
