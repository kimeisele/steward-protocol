"""
Action Loader - Auto-discovery for MANAS Action modules (Karmendriyas).

OPUS-100: VEDA-4 Pattern for Action Auto-Discovery

The 5 Karmendriyas (Action Organs) in Samkhya:
- VAK (Speech)      → ShellAction      (Execute commands)
- PANI (Hands)      → SilpaAction      (Refactor code)
- PADA (Feet)       → KriyaAction      (Route intents)
- PAYU (Eliminate)  → TestAction       (Run tests)
- UPASTHA (Create)  → SankalpaAction   (Orchestrate missions)

STRICT MODE ENABLED:
    - Any load failure CRASHES with full traceback
    - No silent skipping of broken actions
    - If MANAS loses the ability to act, it KNOWS immediately

WHY THIS EXISTS:
    IntentRouter currently has hardcoded intent_type -> handler mappings.
    When someone adds a new action, they must update the router manually.
    ActionLoader auto-discovers actions and their handled intent types.

KEY FEATURE:
    Each action declares its `handled_intent_types`.
    ActionLoader builds the global intent_type -> action mapping.
    IntentRouter can query: ActionLoader.get_handler("commit_changes")
"""

import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type

from vibe_core.loaders.base_loader import LoaderRegistry

logger = logging.getLogger("ACTION.LOADER")


# Type aliases
ActionRegistry = Dict[str, Any]  # action_name -> instance
ActionMetadata = Dict[str, Dict[str, Any]]  # action_name -> metadata
IntentHandlerMap = Dict[str, str]  # intent_type -> action_name


class ActionLoadError(Exception):
    """Raised when action loading fails in STRICT MODE."""

    pass


class ActionLoader:
    """
    Auto-discovery loader for MANAS Action modules (Karmendriyas).

    STRICT MODE: Crashes on any error. No silent failures.

    Unlike SenseLoader (which scans *_sense.py), ActionLoader scans
    *_action.py files for BaseAction subclasses.

    KEY FEATURE: Builds intent_type -> action mapping automatically.

    Usage:
        # Discover and instantiate all actions
        actions, meta = ActionLoader.discover_and_load(workspace=Path.cwd())

        # Get handler for an intent type
        handler_name = ActionLoader.get_handler_for_intent("commit_changes")
        if handler_name:
            action = actions[handler_name]
            result = action.act(intent)

        # Or directly
        action = ActionLoader.get_action_for_intent("commit_changes")
        if action:
            result = action.act(intent)
    """

    # === LOADER CONFIG ===
    item_type = "action"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_action.py"  # Only scan files ending in _action.py
    base_class_name = "BaseAction"  # String match for loose coupling

    # === STRICT MODE ===
    strict_mode = True  # CRASH on errors, no silent skip

    # === CLASS-LEVEL CACHE ===
    _action_cache: Optional[ActionRegistry] = None
    _metadata_cache: Optional[ActionMetadata] = None
    _intent_handler_map: Optional[IntentHandlerMap] = None

    @classmethod
    def discover_and_load(
        cls,
        scan_paths: Optional[List[Path]] = None,
        workspace: Optional[Path] = None,
        force_refresh: bool = False,
        strict: Optional[bool] = None,
    ) -> Tuple[ActionRegistry, ActionMetadata]:
        """
        Discover and load all actions. CACHED after first call.

        Also builds the intent_type -> action_name mapping.

        STRICT MODE: Any failure raises ActionLoadError.

        Args:
            scan_paths: Override default paths
            workspace: Workspace to pass to action constructors
            force_refresh: If True, bypass cache
            strict: Override class-level strict_mode

        Returns:
            Tuple of (action_instances, metadata)

        Raises:
            ActionLoadError: If any action fails to load (in strict mode)
        """
        # Return cached if available
        if not force_refresh and cls._action_cache is not None:
            return cls._action_cache, cls._metadata_cache or {}

        paths = scan_paths or cls.scan_paths
        workspace = workspace or Path.cwd()
        is_strict = strict if strict is not None else cls.strict_mode

        actions: ActionRegistry = {}
        metadata: ActionMetadata = {}
        intent_map: IntentHandlerMap = {}
        errors: List[str] = []

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"[action] Scan path does not exist: {base_path}")
                continue

            logger.info(f"[action] Scanning {base_path}...")

            # Scan *_action.py files
            for py_file in sorted(base_path.glob(cls.file_pattern)):
                # Skip test files
                if py_file.name.startswith("test_"):
                    continue

                try:
                    action_classes = cls._load_action_classes(py_file)

                    for action_class in action_classes:
                        try:
                            # Instantiate with workspace
                            instance = action_class(workspace=workspace)
                            name = instance.name

                            actions[name] = instance

                            # Get handled intent types
                            handled_types = getattr(instance, "handled_intent_types", set())

                            # Build intent -> action mapping
                            for intent_type in handled_types:
                                if intent_type in intent_map:
                                    # Conflict! Two actions claim same intent
                                    logger.warning(
                                        f"  ⚠️ Intent conflict: {intent_type} "
                                        f"claimed by both {intent_map[intent_type]} and {name}"
                                    )
                                intent_map[intent_type] = name

                            metadata[name] = {
                                "class": action_class.__name__,
                                "file": str(py_file),
                                "enabled": instance.is_enabled,
                                "handled_intent_types": list(handled_types),
                            }
                            logger.info(
                                f"  ✅ Loaded: {name} ({action_class.__name__}) "
                                f"handles {len(handled_types)} intent types"
                            )

                        except Exception as e:
                            error_msg = f"Failed to instantiate {action_class.__name__} from {py_file.name}: {e}"
                            logger.error(f"  ❌ {error_msg}")
                            errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Failed to load action module {py_file.name}: {e}"
                    logger.error(f"  ❌ {error_msg}")
                    errors.append(error_msg)

        # STRICT MODE: Crash on ANY error
        if is_strict and errors:
            error_summary = "\n".join(f"  - {e}" for e in errors)
            raise ActionLoadError(
                f"STRICT MODE: {len(errors)} action(s) failed to load:\n{error_summary}\n\n"
                f"Fix these errors before continuing. MANAS cannot act without its hands."
            )

        # Cache results
        cls._action_cache = actions
        cls._metadata_cache = metadata
        cls._intent_handler_map = intent_map

        logger.info(f"[action] Loaded {len(actions)} actions, {len(intent_map)} intent mappings (cached)")
        return actions, metadata

    @classmethod
    def _load_action_classes(cls, py_file: Path) -> List[Type]:
        """
        Load action classes from a Python file.

        Finds all classes that inherit from BaseAction.
        Uses proper module import to preserve package context for relative imports.
        """
        import importlib

        try:
            parts = py_file.parts
            vibe_idx = None
            for i, part in enumerate(parts):
                if part == "vibe_core":
                    vibe_idx = i
                    break

            if vibe_idx is None:
                raise ImportError(f"Cannot determine module path for {py_file}")

            module_path = ".".join(parts[vibe_idx:]).replace(".py", "")
            module = importlib.import_module(module_path)
            module_name = module.__name__

        except Exception as e:
            raise ImportError(f"Failed to import {py_file}: {e}")

        # Find BaseAction subclasses
        action_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module_name:
                continue
            if cls._is_action_subclass(obj):
                action_classes.append(obj)

        return action_classes

    @classmethod
    def _is_action_subclass(cls, candidate: Type) -> bool:
        """Check if candidate inherits from BaseAction."""
        if candidate.__name__ == cls.base_class_name:
            return False
        for base in inspect.getmro(candidate):
            if base.__name__ == cls.base_class_name:
                return True
        return False

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached action data."""
        cls._action_cache = None
        cls._metadata_cache = None
        cls._intent_handler_map = None

    @classmethod
    def get_action(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific action by name."""
        actions, _ = cls.discover_and_load(workspace=workspace)
        return actions.get(name)

    @classmethod
    def list_actions(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered action names."""
        actions, _ = cls.discover_and_load(workspace=workspace)
        return list(actions.keys())

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

        Args:
            intent_type: The intent type to look up

        Returns:
            Action instance or None if no handler registered
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


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("action", ActionLoader)
