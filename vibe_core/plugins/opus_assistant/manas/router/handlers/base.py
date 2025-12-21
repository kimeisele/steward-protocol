"""
Base Handler - Foundation for VEDA-4 Intent Handlers.

OPUS-171 Phase 5: Agent-First Routing Architecture

DESIGN PRINCIPLES:
1. Each handler is a standalone module (Holon)
2. Handlers self-register their intent types
3. Future: Handlers can delegate to Agents (Agent-First)

PATTERN:
    class SutraHandler(BaseHandler):
        name = "sutra"
        intent_types = ["update_readme", "update_opus_documentation", ...]

        def handle(self, intent: Intent) -> Dict[str, Any]:
            # Handler-specific logic
            ...

AGENT-FIRST ROUTING (Future):
    Current:  Intent → Router → Handler
    Future:   Intent → Router → Agent → Handler

    The BaseHandler.agent_type attribute enables future routing to
    specialized agents (Holons) that contain multiple handlers.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Set

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler")


class BaseHandler(ABC):
    """
    Abstract base class for intent handlers.

    OPUS-171 Phase 5: VEDA-4 compliant handler pattern.

    Subclasses MUST define:
    - name: Unique handler name (e.g., "sutra", "shell", "silpa")
    - intent_types: List of intent types this handler processes
    - handle(): The main handler logic

    Subclasses MAY define:
    - agent_type: Which agent domain this handler belongs to (Agent-First)
    - priority: Handler priority for conflict resolution (higher = first)

    Usage:
        class SutraHandler(BaseHandler):
            name = "sutra"
            intent_types = ["update_readme", "update_opus_documentation"]
            agent_type = "documentation"  # Future: route via DocAgent

            def handle(self, intent: Intent) -> Dict[str, Any]:
                return {"success": True, "handler": self.name}
    """

    # === REQUIRED CLASS ATTRIBUTES ===
    name: ClassVar[str] = ""  # Handler name (e.g., "sutra", "shell")
    intent_types: ClassVar[List[str]] = []  # Intent types this handler processes

    # === OPTIONAL CLASS ATTRIBUTES (Agent-First) ===
    agent_type: ClassVar[str] = "generic"  # Agent domain for future routing
    priority: ClassVar[int] = 0  # Handler priority (higher = first)

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the handler.

        Args:
            workspace: Workspace path (default: cwd)
            config: Optional configuration dict
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}
        self._kernel = None  # Injected later

    def inject_kernel(self, kernel: Any) -> None:
        """Inject the kernel for ledger/state access."""
        self._kernel = kernel

    @abstractmethod
    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """
        Handle an intent.

        Args:
            intent: The intent to handle

        Returns:
            Dict with at least:
            - success: bool
            - handler: str (handler name)

        Must be implemented by subclasses.
        """
        pass

    def can_handle(self, intent_type: str) -> bool:
        """
        Check if this handler can process an intent type.

        Default implementation checks against intent_types list.
        Override for more complex matching logic.
        """
        return intent_type in self.intent_types

    def get_intent_types(self) -> List[str]:
        """Get all intent types this handler can process."""
        return list(self.intent_types)

    # === AGENT-FIRST ROUTING HELPERS ===

    @classmethod
    def get_agent_type(cls) -> str:
        """Get the agent domain for this handler."""
        return cls.agent_type

    @classmethod
    def get_priority(cls) -> int:
        """Get handler priority for conflict resolution."""
        return cls.priority

    # === LIFECYCLE HOOKS ===

    def on_load(self) -> None:
        """Called when handler is loaded by HandlerLoader."""
        logger.debug(f"Handler loaded: {self.name} ({len(self.intent_types)} intent types)")

    def on_unload(self) -> None:
        """Called when handler is unloaded."""
        pass

    # === REPRESENTATION ===

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} intents={len(self.intent_types)}>"


# =============================================================================
# Handler Registration (for auto-discovery)
# =============================================================================

# Global registry of handler classes (populated by HandlerLoader)
_handler_registry: Dict[str, type] = {}


def register_handler(cls: type) -> type:
    """
    Decorator to register a handler class.

    Usage:
        @register_handler
        class SutraHandler(BaseHandler):
            ...
    """
    if not issubclass(cls, BaseHandler):
        raise TypeError(f"{cls.__name__} must be a subclass of BaseHandler")

    if not cls.name:
        raise ValueError(f"{cls.__name__} must define 'name' class attribute")

    _handler_registry[cls.name] = cls
    return cls


def get_registered_handlers() -> Dict[str, type]:
    """Get all registered handler classes."""
    return dict(_handler_registry)


# =============================================================================
# Agent Type Constants (for Agent-First routing)
# =============================================================================


class AgentType:
    """Agent domain types for future routing."""

    DOCUMENTATION = "documentation"  # Sutra, docs, harness
    GIT = "git"  # Shell, commit, push, PR
    TESTING = "testing"  # Test, mutation, coverage
    AUDIT = "audit"  # Dharma, wiring, security
    STRATEGY = "strategy"  # Sankalpa, planning
    RESEARCH = "research"  # Vidya, knowledge
    GENESIS = "genesis"  # Silpa, code generation
    GENERIC = "generic"  # Default fallback


__all__ = [
    "BaseHandler",
    "register_handler",
    "get_registered_handlers",
    "AgentType",
]
