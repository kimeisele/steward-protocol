"""
Base Sense - Abstract base class for MANAS perception modules.

OPUS-099: VEDA-4 Pattern for Cortex Auto-Discovery

The 5 Jnanendriyas (Perception Organs) in Samkhya:
- SHROTRA (Hearing)  → SamvadaListener
- TVAK (Touch)       → PrakritiSense
- CHAKSHU (Sight)    → SutraSense
- RASANA (Taste)     → DharmaSense
- GHRANA (Smell)     → JnanaHandler

This base class enables auto-discovery of senses via SenseLoader.
No more manual import lists. Add a new sense → SenseLoader finds it.

STRICT MODE: If a sense fails to load, the system CRASHES.
We want to know immediately, not discover later that MANAS is blind.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseSense(ABC):
    """
    Abstract base class for MANAS perception modules (Jnanendriyas).

    All senses must inherit from this class to be discovered by SenseLoader.

    Required:
        - name: Unique identifier for the sense
        - perceive(): Main perception method (returns sense-specific data)

    Optional:
        - is_enabled: Whether sense is active (default: True)

    Usage:
        class MySense(BaseSense):
            name = "my_sense"

            def __init__(self, workspace: Path, config: Optional[Dict] = None):
                super().__init__(workspace, config)

            def perceive(self, context: Optional[Dict] = None):
                # Sense-specific perception logic
                return SomePerceptionResult(...)
    """

    # === MUST BE OVERRIDDEN ===
    name: str = ""  # Unique sense identifier (e.g., "prakriti_sense")

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize sense.

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
        """Get sense configuration."""
        return self._config

    @property
    def is_enabled(self) -> bool:
        """
        Check if sense is enabled.

        Override to implement custom enable/disable logic.
        Default: True (enabled by default)
        """
        return self._config.get("enabled", True)

    @abstractmethod
    def perceive(self, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Main perception method.

        This is the primary interface for the sense. Each sense
        implements its own perception logic and returns sense-specific data.

        Args:
            context: Optional context dict for perception

        Returns:
            Sense-specific perception result (e.g., GunaSummary, DharmaSummary)
        """
        pass

    def __repr__(self) -> str:
        status = "enabled" if self.is_enabled else "disabled"
        return f"<{self.__class__.__name__}:{self.name} status={status}>"
