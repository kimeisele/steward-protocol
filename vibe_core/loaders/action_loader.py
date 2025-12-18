"""
Action Loader - Auto-discovery for MANAS Action modules (Karmendriyas).

OPUS-100: VEDA-4 Pattern for Action Auto-Discovery

The 5 Karmendriyas (Action Organs) in Samkhya:
- VAK (Speech)      → ShellAction      (Execute commands)
- PANI (Hands)      → SilpaAction      (Refactor code)
- PADA (Feet)       → KriyaAction      (Route intents)
- PAYU (Eliminate)  → TestAction       (Run tests)
- UPASTHA (Create)  → SankalpaAction   (Orchestrate missions)

INHERITS: CodeModuleLoader (VEDA-4 compliant)

KEY FEATURE:
    Each action declares its `handled_intent_types`.
    ActionLoader builds the global intent_type -> action mapping.
    IntentRouter can query: ActionLoader.get_handler_for_intent("commit_changes")
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeModuleMeta,
    CodeRegistry,
)

logger = logging.getLogger("ACTION.LOADER")


# Type aliases (backward compat)
ActionRegistry = CodeRegistry
ActionMetadata = CodeMetadata
IntentHandlerMap = Dict[str, str]  # intent_type -> action_name


class ActionLoadError(CodeModuleLoadError):
    """Raised when action loading fails in STRICT MODE."""

    pass


class ActionLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Action modules (Karmendriyas).

    INHERITS: CodeModuleLoader for VEDA-4 compliance.

    KEY FEATURE: Builds intent_type -> action mapping automatically.

    Usage (Global - class methods):
        # Discover and instantiate all actions
        actions, meta = ActionLoader.discover_and_load(workspace=Path.cwd())

        # Get handler for an intent type
        handler_name = ActionLoader.get_handler_for_intent("commit_changes")

    Usage (Fractal - instance methods):
        # Create scoped loader for OPUS internal use
        opus_actions = ActionLoader(
            scope="opus_private",
            scan_paths=[Path("vibe_core/plugins/opus_assistant/manas/cortex")]
        )
        actions, _ = opus_actions.load()
        action = opus_actions.get_for_intent("commit_changes")
    """

    # === LOADER CONFIG ===
    item_type = "action"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_action.py"
    base_class_name = "BaseAction"

    # === STRICT MODE ===
    strict_mode = True

    # === INTENT HANDLER MAP ===
    _intent_handler_map: Optional[IntentHandlerMap] = None

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
        strict: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ActionRegistry, ActionMetadata]:
        """
        Discover and load all actions. Also builds intent_type -> action mapping.
        """
        # Use parent's discovery
        instances, metadata = super().discover_and_load(
            scan_paths=scan_paths,
            workspace=workspace,
            force_refresh=force_refresh,
            strict=strict,
            config=config,
        )

        # Build intent handler map (ACTION-SPECIFIC)
        if force_refresh or cls._intent_handler_map is None:
            cls._intent_handler_map = {}
            for name, instance in instances.items():
                handled_types = getattr(instance, "handled_intent_types", set())
                for intent_type in handled_types:
                    if intent_type in cls._intent_handler_map:
                        logger.warning(
                            f"⚠️ Intent conflict: {intent_type} "
                            f"claimed by both {cls._intent_handler_map[intent_type]} and {name}"
                        )
                    cls._intent_handler_map[intent_type] = name

        return instances, metadata

    @classmethod
    def _post_process_instance(cls, instance: Any, meta: CodeModuleMeta) -> None:
        """Add handled_intent_types to metadata."""
        handled_types = getattr(instance, "handled_intent_types", set())
        meta.extra["handled_intent_types"] = list(handled_types)

    @classmethod
    def _should_skip_file(cls, py_file: Path) -> bool:
        """Skip test files but allow test_action.py."""
        name = py_file.name
        if name.startswith("_"):
            return True
        # Skip unit test files but NOT actual action files named test_action.py
        if name.startswith("test_") and name != "test_action.py":
            return True
        if name == "base.py":
            return True
        return False

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached data including intent map."""
        super().clear_cache()
        cls._intent_handler_map = None

    # === ACTION-SPECIFIC METHODS ===

    @classmethod
    def get_action(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific action by name."""
        return cls.get_item(name, workspace)

    @classmethod
    def list_actions(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered action names."""
        return cls.list_items(workspace)

    @classmethod
    def get_handler_for_intent(cls, intent_type: str, workspace: Optional[Path] = None) -> Optional[str]:
        """
        Get the action name that handles a given intent type.

        Args:
            intent_type: The intent type to look up

        Returns:
            Action name or None if no handler registered
        """
        cls.discover_and_load(workspace=workspace)
        if cls._intent_handler_map is None:
            return None
        return cls._intent_handler_map.get(intent_type)

    @classmethod
    def get_action_for_intent(cls, intent_type: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """
        Get the action instance that handles a given intent type.
        """
        handler_name = cls.get_handler_for_intent(intent_type, workspace)
        if handler_name is None:
            return None
        return cls.get_action(handler_name, workspace)

    @classmethod
    def get_intent_handler_map(cls, workspace: Optional[Path] = None) -> IntentHandlerMap:
        """Get the full intent_type -> action_name mapping."""
        cls.discover_and_load(workspace=workspace)
        return cls._intent_handler_map or {}

    # =========================================================================
    # INSTANCE METHODS (FRACTAL PATTERN)
    # =========================================================================

    def __init__(
        self,
        scope: str = "global",
        scan_paths: Optional[List[Path]] = None,
    ):
        """
        Create a scoped ActionLoader instance.

        FRACTAL PRINCIPLE:
            - scope="global" → Uses class-level scan_paths
            - scope="opus_private" → Uses custom paths, isolated cache

        Args:
            scope: Loader scope identifier
            scan_paths: Override scan paths for this instance
        """
        super().__init__(scope=scope, scan_paths=scan_paths)
        # Instance-level intent handler map (not shared with class)
        self._inst_intent_map: Optional[IntentHandlerMap] = None

    def load(
        self,
        force_refresh: bool = False,
    ) -> Tuple[ActionRegistry, ActionMetadata]:
        """
        Instance method for scoped loading.

        Also builds instance-level intent handler map.
        """
        instances, metadata = super().load(force_refresh=force_refresh)

        # Build intent handler map for this instance
        if force_refresh or self._inst_intent_map is None:
            self._inst_intent_map = {}
            for name, instance in instances.items():
                handled_types = getattr(instance, "handled_intent_types", set())
                for intent_type in handled_types:
                    if intent_type in self._inst_intent_map:
                        logger.warning(
                            f"⚠️ [{self._scope}] Intent conflict: {intent_type} "
                            f"claimed by both {self._inst_intent_map[intent_type]} and {name}"
                        )
                    self._inst_intent_map[intent_type] = name

        return instances, metadata

    def get_for_intent(self, intent_type: str) -> Optional[Any]:
        """
        Get the action instance that handles a given intent type.

        Instance method for fractal/scoped usage.
        """
        self.load()  # Ensure loaded
        if self._inst_intent_map is None:
            return None
        handler_name = self._inst_intent_map.get(intent_type)
        if handler_name is None:
            return None
        return self.get(handler_name)

    def get_intent_map(self) -> IntentHandlerMap:
        """Get the intent_type -> action_name mapping (instance-level)."""
        self.load()  # Ensure loaded
        return self._inst_intent_map or {}


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("action", ActionLoader)
