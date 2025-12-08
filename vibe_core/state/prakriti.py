"""
Prakriti - The Unified State Engine

OPUS-009: "The Repository IS the Mind"

Prakriti (Sanskrit: "Primordial Matter") unifies state across three layers:
- STHULA (Layer 1): Git + Files (Physical)
- PRANA (Layer 2): Kernel + Ephemeral (Runtime)
- PURUSHA (Layer 3): Personas (Identity) - Phase 3

GAD-000 Compliant:
- All methods return dict/dataclass
- Errors use StructuredError with codes
- get_capabilities() for discoverability
- get_system_status() for observability
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .ephemeral_state import EphemeralState
from .file_state import FileState
from .git_state import GitDiff, GitState
from .kernel_state import KernelState

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("PRAKRITI")


@dataclass
class StateSnapshot:
    """Complete state snapshot across all layers."""

    timestamp: float
    git: Dict[str, Any]
    files: Dict[str, Any]
    kernel: Optional[Dict[str, Any]] = None
    ephemeral: Optional[Dict[str, Any]] = None
    # Phase 3: personas: Dict[str, Any] = None


class Prakriti:
    """The Fractal State Engine.

    The unified interface for all state operations in the Steward Protocol.
    Treats:
    - Every Agent as a Commit
    - Every Decision as a Branch
    - Every Learning as a Merge

    Layers:
    - Layer 1 (STHULA): Git + Files (Physical)
    - Layer 2 (PRANA): Kernel + Ephemeral (Runtime)
    - Layer 3 (PURUSHA): Personas (Identity) - Phase 3
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize Prakriti for a workspace.

        Args:
            workspace_path: Root of the workspace (default: cwd)
        """
        self._workspace = Path(workspace_path) if workspace_path else Path.cwd()

        # Layer 1: Physical State (STHULA)
        self.git = GitState(self._workspace)
        self.files = FileState(self._workspace)

        # Layer 2: Runtime State (PRANA)
        self.kernel = KernelState()
        self.ephemeral = EphemeralState()

        # Layer 3: Identity (PURUSHA) - Phase 3
        # self.personas = {}

        logger.info(f"[PRAKRITI] Initialized at {self._workspace}")

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def from_workspace(cls, path: str) -> "Prakriti":
        """Create Prakriti instance from workspace path.

        Args:
            path: Path to workspace root

        Returns:
            Prakriti instance
        """
        return cls(Path(path))

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: What can Prakriti do?"""
        return {
            "version": "2.0.0-phase2",
            "operations": ["snapshot", "verify", "diff", "status", "inject_kernel"],
            "layers": {
                "sthula": {
                    "status": "active",
                    "components": ["git", "files"],
                },
                "prana": {
                    "status": "active",
                    "components": ["kernel", "ephemeral"],
                },
                "purusha": {
                    "status": "phase3",
                    "components": ["personas"],
                },
            },
            "workspace": str(self._workspace),
            "git": self.git.get_capabilities(),
            "files": self.files.get_capabilities(),
            "kernel": self.kernel.get_capabilities(),
            "ephemeral": self.ephemeral.get_capabilities(),
        }

    # =========================================================================
    # GAD-000: Observability
    # =========================================================================

    def get_system_status(self) -> Dict[str, Any]:
        """GAD-000 Test 2: Current state summary."""
        return {
            "timestamp": time.time(),
            "workspace": str(self._workspace),
            "git": self.git.status(),
            "files": self.files.status(),
            "kernel": self.kernel.status(),
            "ephemeral": self.ephemeral.status(),
            # Phase 3: "personas": list(self.personas.keys()),
        }

    # =========================================================================
    # Core Operations
    # =========================================================================

    def snapshot(self) -> StateSnapshot:
        """Take a complete state snapshot.

        Returns:
            StateSnapshot with all layer states
        """
        return StateSnapshot(
            timestamp=time.time(),
            git=self.git.status(),
            files=self.files.status(),
            kernel=self.kernel.status(),
            ephemeral=self.ephemeral.status(),
        )

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """Inject kernel reference for Layer 2 state access.

        Args:
            kernel: The RealVibeKernel instance
        """
        self.kernel.inject_kernel(kernel)
        logger.info("[PRAKRITI] Kernel injected into Layer 2")

    def verify(self) -> Dict[str, Any]:
        """Verify workspace consistency.

        Returns:
            Dict with verification results
        """
        issues = []

        # Check git repo
        if not self.git.is_git_repo():
            issues.append(
                {
                    "layer": "git",
                    "issue": "Not a git repository",
                    "severity": "warning",
                }
            )

        # Check for uncommitted changes
        if self.git.is_dirty():
            dirty_files = self.files.dirty_files()
            issues.append(
                {
                    "layer": "git",
                    "issue": "Uncommitted changes",
                    "severity": "info",
                    "details": {"dirty_count": len(dirty_files)},
                }
            )

        return {
            "status": "ok" if not issues else "issues_found",
            "issues": issues,
            "git_branch": self.git.current_branch(),
            "git_sha": self.git.short_sha(),
        }

    def diff(self, base_ref: str = "HEAD~1") -> GitDiff:
        """Get diff from base_ref to HEAD.

        This is the "Proof of Work" - what did the agent actually do?

        Args:
            base_ref: Git ref to diff against

        Returns:
            GitDiff with stats
        """
        return self.git.diff(base_ref)

    def diff_main(self) -> GitDiff:
        """Get diff from main branch to HEAD.

        Useful for verifying agent work before merge.

        Returns:
            GitDiff with stats
        """
        return self.git.diff_main()

    # =========================================================================
    # Convenience Properties
    # =========================================================================

    @property
    def workspace(self) -> Path:
        """Get workspace path."""
        return self._workspace

    @property
    def branch(self) -> str:
        """Get current git branch."""
        return self.git.current_branch()

    @property
    def is_dirty(self) -> bool:
        """Check if workspace has uncommitted changes."""
        return self.git.is_dirty()

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self) -> str:
        return f"Prakriti(workspace={self._workspace}, branch={self.branch})"
