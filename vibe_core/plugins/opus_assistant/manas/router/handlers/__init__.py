"""
MANAS Intent Handlers - VEDA-4 Auto-Discovery.

OPUS-171 Phase 5: Agent-First Routing Architecture

Each handler is a standalone module (Holon) that:
1. Declares which intent types it handles
2. Declares which agent domain it belongs to (for future Agent-First routing)
3. Is auto-discovered by HandlerLoader

Usage:
    # Auto-discovery (recommended)
    from vibe_core.plugins.opus_assistant.manas.router.handlers import get_all_handlers
    handlers = get_all_handlers(workspace=Path.cwd())

    # Static import (for type hints)
    from vibe_core.plugins.opus_assistant.manas.router.handlers import SutraHandler
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import AgentType, BaseHandler, get_registered_handlers, register_handler


def get_all_handlers(
    workspace: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, BaseHandler]:
    """
    Get all handlers via VEDA-4 auto-discovery.

    Returns:
        Dict mapping handler names to instances
    """
    from vibe_core.loaders import HandlerLoader

    handlers, _ = HandlerLoader.discover_and_load(
        workspace=workspace,
        config=config,
    )
    return handlers


def list_handlers(workspace: Optional[Path] = None) -> List[str]:
    """List all discovered handler names."""
    from vibe_core.loaders import HandlerLoader

    return HandlerLoader.list_handlers(workspace)


def get_handler_for_intent(
    intent_type: str,
    workspace: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Optional[BaseHandler]:
    """
    Get the handler for a specific intent type.

    Args:
        intent_type: The intent type to find a handler for
        workspace: Workspace path
        config: Optional config

    Returns:
        Handler instance or None if not found
    """
    from vibe_core.loaders import HandlerLoader

    return HandlerLoader.get_handler_for_intent(
        intent_type=intent_type,
        workspace=workspace,
        config=config,
    )


__all__ = [
    # Base classes
    "BaseHandler",
    "register_handler",
    "get_registered_handlers",
    "AgentType",
    # Auto-discovery helpers
    "get_all_handlers",
    "list_handlers",
    "get_handler_for_intent",
]
