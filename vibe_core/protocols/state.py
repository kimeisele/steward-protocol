"""
Unified State Protocols - Layer 1: Interfaces Only

OPUS-211: Full System Integration (DI.py wiring)

Defines the interfaces for the State system components:
- Prakriti: The Supreme State Engine
- StateService: Identity Principle (Ahamkara) / Persistence
- StateSyncHolon: The Tanmatra Bridge / Discovery & Healing
- StateSyncWeaver: Meta-orchestration layer
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class StateServiceProtocol(ABC):
    """Protocol for StateService (Ahamkara aspect)."""

    @abstractmethod
    def save(self, filename: str, data: Any, create_backup: bool = True, indent: int = 2) -> Any:
        """Save state to a JSON file."""
        pass

    @abstractmethod
    def load(self, filename: str, default: Any = None) -> Any:
        """Load state from a JSON file."""
        pass

    @abstractmethod
    def append(self, filename: str, entry: Dict[str, Any]) -> Any:
        """Append entry to a JSONL file."""
        pass

    @abstractmethod
    def mark_dirty(self, path: Path) -> None:
        """Mark a file as dirty for auto-commit."""
        pass

    @abstractmethod
    def get_dirty_files(self) -> List[Path]:
        """Get list of files written since last clear."""
        pass

    @abstractmethod
    def clear_dirty_flags(self) -> None:
        """Clear dirty flags after successful commit."""
        pass


class StateSyncHolonProtocol(ABC):
    """Protocol for StateSyncHolon (Tanmatra bridge)."""

    @abstractmethod
    def discover_state_paths(self) -> Dict[str, List[Any]]:
        """Auto-discover all plugin state paths."""
        pass

    @abstractmethod
    def diagnose_guna(self, path: Path) -> Any:
        """Diagnose the current Guna of a state path."""
        pass

    @abstractmethod
    def heal_toward_sattva(self, path: Path) -> Any:
        """Apply healing force to move state toward Sattva."""
        pass

    @abstractmethod
    def process_commit_queue(self) -> int:
        """Process queued file changes and commit."""
        pass


class StateSyncWeaverProtocol(ABC):
    """Protocol for StateSyncWeaver (Meta-orchestration)."""

    @abstractmethod
    def pulse(self) -> Any:
        """Run one weave cycle (discovery + commit)."""
        pass

    @abstractmethod
    def weave(self) -> Any:
        """Full weaving cycle with cognitive intelligence."""
        pass

    @abstractmethod
    def on_session_end(self) -> Any:
        """Handle session end commit."""
        pass


class PrakritiProtocol(ABC):
    """Protocol for Prakriti (Unified State Engine)."""

    @property
    @abstractmethod
    def workspace(self) -> Path:
        """Get workspace path."""
        pass

    @abstractmethod
    def commit_if_dirty(
        self,
        message: str = "Auto-commit",
        commit_type: str = "chore",
        scope: str = "state",
        stage_patterns: Optional[List[str]] = None,
        sync_ledger: bool = True,
    ) -> Optional[Any]:
        """Commit current changes if workspace is dirty."""
        pass

    @abstractmethod
    def begin_session(self) -> Any:
        """Start a new session."""
        pass

    @abstractmethod
    def end_session(self) -> Optional[Any]:
        """End current session."""
        pass

    @abstractmethod
    def save_knowledge(self) -> None:
        """Persist Knowledge Graph state."""
        pass
