"""
Context-Aware Agent Base Class with Offline-First Capabilities.

Provides:
1. Automatic context injection (PromptContext + PromptRegistry)
2. Graceful degradation via DegradationChain
3. chat_with_fallback() for offline-capable LLM interactions
4. Tool injection pattern for passing DegradationChain to tools

Usage:
    class MyAgent(ContextAwareAgent):
        def __init__(self):
            super().__init__(
                agent_id="my_agent",
                name="MyAgent",
                ...
            )
            # Inject degradation chain into tools
            self.my_tool = MyTool(degradation_chain=self.get_degradation_chain())

        def process(self, task):
            # Use chat_with_fallback for offline-capable responses
            response = self.chat_with_fallback(
                prompt="User asked: " + task.payload.get("message"),
                context={"task_id": task.id}
            )
            return {"status": "success", "response": response.content}
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.llm.degradation_chain import DegradationChain, DegradationResponse

from vibe_core.protocols import VibeAgent

logger = logging.getLogger("CONTEXT_AWARE_AGENT")


class ContextAwareAgent(VibeAgent):
    """
    Base class for agents needing context injection and offline-first capabilities.

    This is the recommended base class for agents that:
    - Need LLM capabilities (content generation, chat, etc.)
    - Should work offline with graceful degradation
    - Want automatic context injection

    Key Features:
    - DegradationChain: Automatic fallback (LocalLLM → Templates → Error)
    - PromptContext: Dynamic context (git status, time, branch, etc.)
    - Tool Injection: Pass degradation_chain to tools for offline capability
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Context systems (lazy initialized)
        self._prompt_context = None
        self._prompt_registry = None
        self._context_initialized = False

        # Degradation chain (lazy initialized)
        self._degradation_chain = None
        self._degradation_initialized = False

        logger.info(f"ContextAwareAgent initialized: {self.agent_id}")

    # =========================================================================
    # DEGRADATION CHAIN (Offline-First)
    # =========================================================================

    def _ensure_degradation_initialized(self) -> None:
        """Lazy initialization of DegradationChain."""
        if self._degradation_initialized:
            return

        try:
            from vibe_core.llm.degradation_chain import DegradationChain

            self._degradation_chain = DegradationChain()
            logger.info(
                f"{self.agent_id}: DegradationChain initialized "
                f"(level: {self._degradation_chain.current_level.value})"
            )
        except Exception as e:
            logger.warning(f"{self.agent_id}: DegradationChain unavailable: {e}")

        self._degradation_initialized = True

    def get_degradation_chain(self) -> Optional[DegradationChain]:
        """
        Get the DegradationChain instance for tool injection.

        Use this to pass the chain to tools that need offline capability:

            self.research_tool = ResearchTool(
                degradation_chain=self.get_degradation_chain()
            )

        Returns:
            DegradationChain instance or None if unavailable
        """
        self._ensure_degradation_initialized()
        return self._degradation_chain

    def chat_with_fallback(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        semantic_confidence: float = 0.5,
    ) -> DegradationResponse:
        """
        Generate a response with automatic offline fallback.

        This is the main entry point for LLM interactions. It uses DegradationChain
        to provide graceful degradation:

        1. If LocalLLM available → Use it
        2. If offline → Use template matching
        3. If nothing works → Return helpful error with guidance

        Args:
            prompt: The user input or generated prompt
            context: Optional context dict (merged with agent context)
            semantic_confidence: Confidence score from semantic routing (0.0-1.0)

        Returns:
            DegradationResponse with content, level, confidence, fallback_used

        Example:
            response = self.chat_with_fallback(
                prompt="What is the status of the system?",
                context={"task_id": "123"}
            )
            print(response.content)  # The response text
            print(response.level)    # DegradationLevel.FULL or .TEMPLATES
        """
        self._ensure_degradation_initialized()

        if self._degradation_chain is None:
            # Absolute fallback - no DegradationChain available
            from vibe_core.llm.degradation_chain import (
                DegradationLevel,
                DegradationResponse,
            )

            return DegradationResponse(
                content=f"[Agent {self.agent_id} offline - DegradationChain unavailable]",
                level=DegradationLevel.MINIMAL,
                confidence=0.0,
                fallback_used="error",
                user_guidance="System offline. Run: steward install-llm",
            )

        # Merge context if provided
        full_context = self.get_context() if context is None else {**self.get_context(), **context}

        # Add agent context
        full_context["agent_id"] = self.agent_id
        full_context["agent_name"] = self.name

        # Use DegradationChain for response
        return self._degradation_chain.respond(
            user_input=prompt,
            semantic_confidence=semantic_confidence,
            detected_intent=full_context.get("intent"),
        )

    def get_degradation_status(self) -> Dict[str, Any]:
        """
        Get the current degradation status.

        Returns:
            Dict with level, local_llm_available, templates_loaded
        """
        self._ensure_degradation_initialized()

        if self._degradation_chain is None:
            return {
                "level": "unavailable",
                "local_llm_available": False,
                "templates_loaded": 0,
                "error": "DegradationChain not initialized",
            }

        return self._degradation_chain.get_status()

    # =========================================================================
    # CONTEXT INJECTION (PromptContext + PromptRegistry)
    # =========================================================================

    def _ensure_context_initialized(self) -> None:
        """Lazy initialization of context systems."""
        if self._context_initialized:
            return

        try:
            from vibe_core.runtime.prompt_context import get_prompt_context

            self._prompt_context = get_prompt_context()
        except Exception as e:
            logger.warning(f"{self.agent_id}: PromptContext unavailable: {e}")

        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            self._prompt_registry = PromptRegistry
        except Exception as e:
            logger.warning(f"{self.agent_id}: PromptRegistry unavailable: {e}")

        self._context_initialized = True

    def get_context(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get dynamic context from PromptContext.

        Args:
            keys: Optional list of context keys to resolve.
                  Default: ["git_status", "system_time", "current_branch"]

        Returns:
            Dict with resolved context values
        """
        self._ensure_context_initialized()

        if self._prompt_context is None:
            return {"_error": "PromptContext not available"}

        default_keys = ["git_status", "system_time", "current_branch"]
        return self._prompt_context.resolve(keys or default_keys)

    def get_governed_prompt(
        self,
        task_name: str,
        extra_context: Optional[Dict[str, Any]] = None,
        inject_governance: bool = True,
    ) -> str:
        """
        Get governed prompt with context injection.

        Uses PromptRegistry to compose prompts with:
        - Agent-specific templates
        - Dynamic context injection
        - Governance rules (if inject_governance=True)

        Args:
            task_name: Name of the task/template to compose
            extra_context: Additional context to inject
            inject_governance: Whether to inject governance rules

        Returns:
            Composed prompt string
        """
        self._ensure_context_initialized()

        if self._prompt_registry is None:
            return f"[PromptRegistry not available for task: {task_name}]"

        context = self.get_context()
        if extra_context:
            context.update(extra_context)

        context["agent_id"] = self.agent_id

        try:
            return self._prompt_registry.compose(
                agent=self.agent_id.upper(),
                task=task_name,
                context=context,
                inject_governance=inject_governance,
            )
        except Exception as e:
            logger.warning(f"Prompt composition failed: {e}")
            return f"[Prompt composition failed: {e}]"


# =============================================================================
# TOOL MIXIN (For tools that need offline capability)
# =============================================================================


class OfflineCapableMixin:
    """
    Mixin for tools that need offline-first capability.

    Add this to any tool that should work offline:

        class MyTool(OfflineCapableMixin):
            def __init__(self, degradation_chain=None):
                self.init_offline_capability(degradation_chain)

            def search(self, query):
                if self.is_offline:
                    return self.fallback_response(query)
                else:
                    return self._api_search(query)
    """

    _degradation_chain: Optional[DegradationChain] = None

    def init_offline_capability(self, degradation_chain: Optional[DegradationChain] = None):
        """
        Initialize offline capability with optional DegradationChain.

        Args:
            degradation_chain: DegradationChain instance from parent agent
        """
        self._degradation_chain = degradation_chain

    @property
    def is_offline(self) -> bool:
        """
        Check if we're in offline mode (no API access).

        Returns True if:
        - No DegradationChain available, or
        - DegradationChain level is not FULL
        """
        if self._degradation_chain is None:
            return True  # Assume offline if no chain

        from vibe_core.llm.degradation_chain import DegradationLevel

        return self._degradation_chain.current_level != DegradationLevel.FULL

    @property
    def degradation_level(self) -> str:
        """Get current degradation level as string."""
        if self._degradation_chain is None:
            return "unknown"
        return self._degradation_chain.current_level.value

    def fallback_response(self, query: str, tool_name: str = "Tool") -> Dict[str, Any]:
        """
        Generate a fallback response when offline.

        Args:
            query: The original query/request
            tool_name: Name of the tool for logging

        Returns:
            Dict with fallback response and metadata
        """
        if self._degradation_chain is None:
            return {
                "status": "offline",
                "content": f"[{tool_name} offline - no degradation chain]",
                "fallback_used": "error",
                "user_guidance": "Install local LLM: steward install-llm",
            }

        response = self._degradation_chain.respond(
            user_input=query,
            semantic_confidence=0.3,  # Low confidence triggers template fallback
            detected_intent=tool_name.lower(),
        )

        return {
            "status": "offline",
            "content": response.content,
            "level": response.level.value,
            "fallback_used": response.fallback_used,
            "user_guidance": response.user_guidance,
        }
