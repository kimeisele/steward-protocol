"""
Context-Aware Agent Base Class.

Provides automatic context injection and governed prompt composition.
"""

import logging
from typing import Dict, Any, Optional, List

from vibe_core.protocols import VibeAgent

logger = logging.getLogger("CONTEXT_AWARE_AGENT")


class ContextAwareAgent(VibeAgent):
    """Base class for agents needing context injection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prompt_context = None
        self._prompt_registry = None
        self._context_initialized = False

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
        """Get dynamic context."""
        self._ensure_context_initialized()

        if self._prompt_context is None:
            return {"_error": "PromptContext not available"}

        default_keys = ["git_status", "system_time", "current_branch"]
        return self._prompt_context.resolve(keys or default_keys)

    def get_governed_prompt(
        self,
        task_name: str,
        extra_context: Optional[Dict[str, Any]] = None,
        inject_governance: bool = True
    ) -> str:
        """Get governed prompt with context injection."""
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
                inject_governance=inject_governance
            )
        except Exception as e:
            logger.warning(f"Prompt composition failed: {e}")
            return f"[Prompt composition failed: {e}]"
