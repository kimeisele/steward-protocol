"""
MANAS Router - Intent Routing Infrastructure.

OPUS-171 Phase 5: Modular Router Architecture

This module provides:
1. BaseHandler: Foundation for intent handlers
2. HandlerLoader: VEDA-4 auto-discovery for handlers
3. AgentType: Agent domain classification for future routing

Architecture:
    Current:  Intent → Router → Handler
    Future:   Intent → Router → Agent (Holon) → Handler

The "Agent-First" pattern prepares for multi-agent routing where
specialized agents handle their domain of intents.
"""

from .handlers import (
    AgentType,
    BaseHandler,
    get_all_handlers,
    get_handler_for_intent,
    get_registered_handlers,
    list_handlers,
    register_handler,
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
