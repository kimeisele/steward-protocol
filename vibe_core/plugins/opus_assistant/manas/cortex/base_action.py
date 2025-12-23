"""
Base Action - Abstract base class for MANAS action modules (Karmendriyas).

OPUS-100: VEDA-4 Pattern for Action Auto-Discovery

The 5 Karmendriyas (Action Organs) in Samkhya:
- VAK (Speech)      → ShellCortex      (Execute commands)
- PANI (Hands)      → SilpaArchitect   (Refactor code)
- PADA (Feet)       → KriyaBridge      (Route intents)
- PAYU (Eliminate)  → TestCortex       (Run tests)
- UPASTHA (Create)  → SankalpaOrchestrator (Orchestrate missions)

This base class enables auto-discovery of actions via ActionLoader.
No more manual import lists. Add a new action → ActionLoader finds it.

STRICT MODE: If an action fails to load, the system CRASHES.
We want to know immediately, not discover later that MANAS can't act.

KEY DESIGN:
    Each action declares which intent_types it can handle.
    ActionLoader builds the intent_type -> handler mapping automatically.
    No more hardcoded mappings in IntentRouter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from vibe_core.state.schema import ActionResult

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent


class BaseAction(ABC):
    """
    Abstract base class for MANAS action modules (Karmendriyas).

    All actions must inherit from this class to be discovered by ActionLoader.

    Required:
        - name: Unique identifier for the action
        - handled_intent_types: Set of intent types this action can handle
        - act(): Execute an intent

    Optional:
        - is_enabled: Whether action is active (default: True)

    Usage:
        class MyAction(BaseAction):
            name = "my_action"
            handled_intent_types = {"do_something", "do_other_thing"}

            def __init__(self, workspace: Path, config: Optional[Dict] = None):
                super().__init__(workspace, config)

            def act(self, intent: Intent) -> ActionResult:
                if intent.type == "do_something":
                    return self._handle_something(intent)
                elif intent.type == "do_other_thing":
                    return self._handle_other(intent)
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error=f"Unknown intent type: {intent.type}"
                )
    """

    # === MUST BE OVERRIDDEN ===
    name: str = ""  # Unique action identifier (e.g., "shell_cortex")
    handled_intent_types: Set[str] = set()  # Intent types this action handles

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize action.

        Args:
            workspace: Workspace root (default: cwd)
            config: Configuration dict (from config/manas.yaml)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}

    @property
    def workspace(self) -> Path:
        """Get workspace root."""
        return self._workspace

    @property
    def config(self) -> Dict[str, Any]:
        """Get action configuration."""
        return self._config

    @property
    def is_enabled(self) -> bool:
        """
        Check if action is enabled.

        Override to implement custom enable/disable logic.
        Default: True (enabled by default)
        """
        return self._config.get("enabled", True)

    def can_handle(self, intent_type: str) -> bool:
        """
        Check if this action can handle a given intent type.

        Args:
            intent_type: The intent type to check

        Returns:
            True if this action handles this intent type
        """
        return intent_type in self.handled_intent_types

    @abstractmethod
    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute an intent.

        This is the primary interface for the action. Each action
        implements its own execution logic based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with success status and result data
        """
        pass

    def __repr__(self) -> str:
        status = "enabled" if self.is_enabled else "disabled"
        types = ", ".join(sorted(self.handled_intent_types)[:3])
        if len(self.handled_intent_types) > 3:
            types += "..."
        return f"<{self.__class__.__name__}:{self.name} handles=[{types}] status={status}>"
