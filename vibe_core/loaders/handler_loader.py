"""
Handler Loader - Auto-discovery for MANAS Intent Handlers.

OPUS-171 Phase 5: VEDA-4 Pattern for Handler Discovery

INHERITS: CodeModuleLoader (VEDA-4 compliant)

PATTERN:
    Same as ActionLoader/SenseLoader/BridgeLoader but for handlers.
    Scans: vibe_core/plugins/opus_assistant/manas/router/handlers/*.py
    Discovers: Classes inheriting from BaseHandler

AGENT-FIRST ROUTING:
    HandlerLoader also builds an intent_type → handler mapping
    and an agent_type → handlers mapping for future Agent-First routing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeRegistry,
)

logger = logging.getLogger("HANDLER.LOADER")


# Type aliases
HandlerRegistry = CodeRegistry
HandlerMetadata = CodeMetadata


class HandlerLoadError(CodeModuleLoadError):
    """Raised when handler loading fails in STRICT MODE."""

    pass


class HandlerLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Intent Handlers.

    OPUS-171 Phase 5: VEDA-4 Pattern for Handlers.

    Handlers are modular intent processors extracted from IntentRouter.
    Each handler declares:
    - name: Unique handler identifier
    - intent_types: List of intent types it can process
    - agent_type: Which agent domain it belongs to (Agent-First)

    Usage:
        # Discover and load all handlers
        handlers, meta = HandlerLoader.discover_and_load(
            workspace=Path.cwd(),
            config=manas_config,
        )

        # Get handler for a specific intent type
        handler = HandlerLoader.get_handler_for_intent("update_readme")

        # Get all handlers for an agent type
        doc_handlers = HandlerLoader.get_handlers_by_agent("documentation")
    """

    # === LOADER CONFIG ===
    item_type = "handler"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/router/handlers")]
    file_pattern = "*_handler.py"
    base_class_name = "BaseHandler"

    # === STRICT MODE ===
    strict_mode = False  # Handlers are optional (IntentRouter has fallbacks)

    # === CACHE FOR INTENT TYPE MAPPING ===
    _intent_type_map: Dict[str, str] = {}  # intent_type → handler_name
    _agent_type_map: Dict[str, List[str]] = {}  # agent_type → [handler_names]

    @classmethod
    def discover_and_load(
        cls,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """
        Discover and load all handlers, building intent type mappings.

        Returns:
            Tuple of (handlers_dict, metadata_dict)
        """
        handlers, meta = super().discover_and_load(workspace=workspace, config=config)

        # Build intent type → handler mapping
        cls._intent_type_map.clear()
        cls._agent_type_map.clear()

        for name, handler in handlers.items():
            # Map intent types to handler
            for intent_type in handler.get_intent_types():
                if intent_type in cls._intent_type_map:
                    existing = cls._intent_type_map[intent_type]
                    logger.warning(
                        f"Intent type '{intent_type}' already mapped to '{existing}', overwriting with '{name}'"
                    )
                cls._intent_type_map[intent_type] = name

            # Map agent type to handlers
            agent_type = handler.get_agent_type()
            if agent_type not in cls._agent_type_map:
                cls._agent_type_map[agent_type] = []
            cls._agent_type_map[agent_type].append(name)

        logger.info(f"HandlerLoader: {len(handlers)} handlers loaded, {len(cls._intent_type_map)} intent types mapped")

        return handlers, meta

    # === HANDLER-SPECIFIC METHODS ===

    @classmethod
    def get_handler(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific handler by name."""
        return cls.get_item(name, workspace)

    @classmethod
    def list_handlers(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered handler names."""
        return cls.list_items(workspace)

    @classmethod
    def get_handler_for_intent(
        cls,
        intent_type: str,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        Get the handler for a specific intent type.

        Args:
            intent_type: The intent type to find a handler for
            workspace: Workspace path
            config: Optional config

        Returns:
            Handler instance or None if not found
        """
        # Ensure handlers are loaded
        handlers, _ = cls.discover_and_load(workspace=workspace, config=config)

        handler_name = cls._intent_type_map.get(intent_type)
        if handler_name:
            return handlers.get(handler_name)

        return None

    @classmethod
    def get_handlers_by_agent(
        cls,
        agent_type: str,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Get all handlers for an agent type (Agent-First routing).

        Args:
            agent_type: The agent type (e.g., "documentation", "git")
            workspace: Workspace path
            config: Optional config

        Returns:
            List of handler instances for this agent type
        """
        handlers, _ = cls.discover_and_load(workspace=workspace, config=config)

        handler_names = cls._agent_type_map.get(agent_type, [])
        return [handlers[name] for name in handler_names if name in handlers]

    @classmethod
    def get_intent_type_map(cls) -> Dict[str, str]:
        """Get the intent_type → handler_name mapping."""
        return dict(cls._intent_type_map)

    @classmethod
    def get_agent_type_map(cls) -> Dict[str, List[str]]:
        """Get the agent_type → handler_names mapping."""
        return {k: list(v) for k, v in cls._agent_type_map.items()}


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("handler", HandlerLoader)
