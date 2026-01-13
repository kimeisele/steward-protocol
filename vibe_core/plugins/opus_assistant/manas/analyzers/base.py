"""
Base Analyzer - Abstract interface for MANAS analyzers.

OPUS-032: Foundation for modular intent generation.

All analyzers inherit from BaseAnalyzer and implement analyze().
This allows the IntentGenerator to orchestrate multiple analyzers
without knowing their implementation details.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x90c51df1"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import Intent types from parent module
from ..intent_generator import Intent


@dataclass
class AnalyzerConfig:
    """Configuration for an analyzer."""

    enabled: bool = True
    cooldown_minutes: int = 60  # Minimum time between generating same intent type
    max_intents_per_run: int = 3  # Don't overwhelm with too many intents


class BaseAnalyzer(ABC):
    """
    Abstract base class for MANAS analyzers.

    Each analyzer:
    1. Examines a specific aspect of system state
    2. Returns a list of intents when action is needed
    3. Respects cooldowns to avoid spam

    Usage:
        class MyAnalyzer(BaseAnalyzer):
            @property
            def name(self) -> str:
                return "my_analyzer"

            def analyze(self, context: Dict[str, Any]) -> List[Intent]:
                # Examine context, generate intents
                return [Intent(...)]
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        """
        Initialize analyzer.

        Args:
            workspace: Workspace root path
            config: Optional configuration
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or AnalyzerConfig()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name for this analyzer.

        Used for logging and cooldown tracking.
        """
        pass

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze system state and generate intents.

        Args:
            context: Current system context from ContextService

        Returns:
            List of intents to add to the buffer
        """
        pass

    @property
    def is_enabled(self) -> bool:
        """Check if this analyzer is enabled."""
        return self._config.enabled

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} enabled={self.is_enabled}>"
