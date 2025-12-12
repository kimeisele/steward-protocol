"""
OPUS Assistant Plugin - Active manager for OPUS.md ecosystem.

OPUS-029: Phase 0 - The Split
This plugin owns the verification LOGIC. The interface plugin's OPUS renderer
uses this plugin for verification, keeping UI and logic separated.

Future phases will add:
- Drift detection (Phase 1)
- CLI commands (Phase 2)
- Event handlers (Phase 3)
- Opus Assistant Agent (Phase 4)
- Circuits & Playbooks (Phase 5)
- Ephemeral Cities (Phase 6)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

    from .core.verification_logic import VerificationEngine

logger = logging.getLogger("OPUS_ASSISTANT")


class OpusAssistantPlugin(KernelPlugin):
    """
    OPUS Assistant - Active manager for OPUS.md ecosystem.

    Phase 0 (Current):
    - Provides VerificationEngine for @HARNESS verification
    - Used by interface plugin's OPUS renderer

    Capabilities:
    - opus.verify: Run @HARNESS verification
    - opus.drift_detect: Compare code vs docs (TODO)
    """

    @property
    def plugin_id(self) -> str:
        return "opus_assistant"

    @property
    def priority(self) -> int:
        return 50  # After interface (10), before most others

    def __init__(self):
        """Initialize plugin state."""
        self._kernel: Optional["RealVibeKernel"] = None
        self._workspace: Optional[Path] = None
        self._config: Dict[str, Any] = {}

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Initialize OPUS Assistant on kernel boot."""
        self._kernel = kernel

        # Get workspace path
        self._workspace = getattr(kernel, "workspace_path", None) or Path.cwd()

        # Load plugin config
        self._config = self._load_plugin_config()

        logger.info("🎯 OPUS Assistant online (Phase 0: Verification Engine)")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Cleanup on kernel shutdown."""
        logger.info("🎯 OPUS Assistant shutdown")

    def _load_plugin_config(self) -> Dict[str, Any]:
        """Load plugin configuration."""
        if self._kernel and hasattr(self._kernel, "get_plugin_config"):
            return self._kernel.get_plugin_config("opus_assistant") or {}
        return {}

    # =========================================================================
    # Public API
    # =========================================================================

    def verify(self, quick: bool = False) -> Dict[str, Any]:
        """
        Run OPUS verification.

        Args:
            quick: If True, skip semantic checks (faster)

        Returns:
            Verification report dict
        """
        from .core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        engine = VerificationEngine(workspace_root=workspace)
        return engine.run_verification(quick=quick)

    def get_verification_engine(self) -> "VerificationEngine":
        """
        Get a VerificationEngine instance.

        For external use (e.g., by interface plugin).
        """
        from .core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        return VerificationEngine(workspace_root=workspace)

    # =========================================================================
    # GAD-000: Discoverability & Observability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "version": "1.0.0",
            "phase": "0 (The Split)",
            "operations": [
                "verify",
                "get_verification_engine",
            ],
            "capabilities": [
                "opus.verify",
                "opus.drift_detect",  # TODO: Phase 1
            ],
            "workspace": str(self._workspace) if self._workspace else None,
        }

    def get_system_status(self) -> Dict[str, Any]:
        """GAD-000 Test 2: Observability."""
        return {
            "plugin_id": "opus_assistant",
            "status": "active" if self._kernel else "inactive",
            "phase": "0",
            "workspace": str(self._workspace) if self._workspace else None,
        }
