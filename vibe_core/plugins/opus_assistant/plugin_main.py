"""
OPUS Assistant Plugin - Active manager for OPUS.md ecosystem.

OPUS-029: Phase 1 - Drift Detection & OPUS.md Generation
This plugin owns the verification LOGIC and data generation.
The interface plugin handles ALL rendering - we only provide DATA.

Architecture (GAD-000 Compliant):
    ┌─────────────────────────────────┐
    │      Interface Plugin           │  ← RENDERS (rich, markdown)
    │      (Frontend)                 │
    └──────────────┬──────────────────┘
                   │ calls
                   ▼
    ┌─────────────────────────────────┐
    │      opus_assistant Plugin      │  ← DATA ONLY (dicts, no rendering)
    │      (Backend)                  │
    └─────────────────────────────────┘

Phase 0: Verification Engine (DONE)
Phase 1: Drift Detection + OPUS.md Generation (CURRENT)
Phase 2: CLI commands
Phase 3: Event handlers
Phase 4: Opus Assistant Agent
Phase 5: Circuits & Playbooks
Phase 6: Ephemeral Cities
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

    from .core.drift_detector import DriftDetector
    from .core.opus_generator import OpusGenerator
    from .core.verification_logic import VerificationEngine

logger = logging.getLogger("OPUS_ASSISTANT")


class OpusAssistantPlugin(KernelPlugin):
    """
    OPUS Assistant - Active manager for OPUS.md ecosystem.

    IMPORTANT: This plugin provides DATA ONLY.
    The interface plugin is the MASTER for rendering.
    We NEVER render markdown, rich panels, or any UI.

    Capabilities:
    - opus.verify: Run @HARNESS verification
    - opus.drift_detect: Compare code vs docs
    - opus.generate: Generate OPUS.md data
    - opus.preserve: Get preserved sections from existing OPUS.md
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
        """
        Initialize OPUS Assistant on kernel boot.

        Note: We do NOT generate OPUS.md here!
        The interface plugin decides when/if to render OPUS.md.
        We only provide data when asked.
        """
        self._kernel = kernel

        # Get workspace path
        self._workspace = getattr(kernel, "workspace_path", None) or Path.cwd()

        # Load plugin config
        self._config = self._load_plugin_config()

        # Quick drift check on boot (data only, no rendering)
        if self._config.get("check_drift_on_boot", False):
            drift = self.quick_drift_check()
            if not drift.get("healthy", True):
                logger.warning(f"⚠️ OPUS drift detected: {len(drift.get('missing_files', []))} missing files")

        logger.info("🎯 OPUS Assistant online (Phase 1: Drift Detection)")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Cleanup on kernel shutdown."""
        logger.info("🎯 OPUS Assistant shutdown")

    def _load_plugin_config(self) -> Dict[str, Any]:
        """Load plugin configuration."""
        if self._kernel and hasattr(self._kernel, "get_plugin_config"):
            return self._kernel.get_plugin_config("opus_assistant") or {}
        return {}

    # =========================================================================
    # Public API - DATA ONLY, NO RENDERING!
    # =========================================================================

    def verify(self, quick: bool = False) -> Dict[str, Any]:
        """
        Run OPUS verification.

        Returns DATA (dict), not rendered output.

        Args:
            quick: If True, skip semantic checks (faster)

        Returns:
            Verification report dict
        """
        from .core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        engine = VerificationEngine(workspace_root=workspace)
        return engine.run_verification(quick=quick)

    def detect_drift(self, since_commit: str = "HEAD~10") -> Dict[str, Any]:
        """
        Detect drift between code and documentation.

        Returns DATA (dict), not rendered output.

        Args:
            since_commit: Git ref to compare against

        Returns:
            Drift report dict
        """
        from .core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        detector = DriftDetector(workspace_root=workspace)
        report = detector.detect(since_commit=since_commit)
        return report.to_dict()

    def quick_drift_check(self) -> Dict[str, Any]:
        """
        Quick drift check (boot-time, fast).

        Returns DATA (dict), not rendered output.

        Returns:
            Quick check results dict
        """
        from .core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        detector = DriftDetector(workspace_root=workspace)
        return detector.quick_check()

    def generate_opus_data(self, include_verification: bool = True) -> Dict[str, Any]:
        """
        Generate OPUS.md data.

        Returns DATA (dict) that the interface plugin can render.
        We do NOT write OPUS.md - that's the renderer's job!

        Args:
            include_verification: Whether to include verification results

        Returns:
            OpusData as dict
        """
        from .core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        generator = OpusGenerator(workspace_root=workspace)
        data = generator.generate(include_verification=include_verification)

        # Convert dataclass to dict for transport
        return {
            "generated_at": data.generated_at,
            "workspace": data.workspace,
            "version": data.version,
            "verification": data.verification,
            "drift": data.drift,
            "plugins": data.plugins,
            "preserved_sections": data.preserved_sections,
            "warnings": data.warnings,
        }

    def get_preserved_sections(self) -> Dict[str, str]:
        """
        Get preserved sections from existing OPUS.md.

        Human and AI sections are NEVER overwritten.

        Returns:
            Dict mapping section name to content
        """
        from .core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        generator = OpusGenerator(workspace_root=workspace)
        return generator.get_preserved_sections()

    def has_existing_opus(self) -> bool:
        """Check if OPUS.md already exists in workspace root."""
        workspace = self._workspace or Path.cwd()
        return (workspace / "OPUS.md").exists()

    # =========================================================================
    # Engine Accessors (for interface plugin)
    # =========================================================================

    def get_verification_engine(self) -> "VerificationEngine":
        """
        Get a VerificationEngine instance.

        For interface plugin to use directly.
        """
        from .core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        return VerificationEngine(workspace_root=workspace)

    def get_drift_detector(self) -> "DriftDetector":
        """
        Get a DriftDetector instance.

        For interface plugin to use directly.
        """
        from .core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        return DriftDetector(workspace_root=workspace)

    def get_opus_generator(self) -> "OpusGenerator":
        """
        Get an OpusGenerator instance.

        For interface plugin to use directly.
        """
        from .core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        return OpusGenerator(workspace_root=workspace)

    # =========================================================================
    # GAD-000: Discoverability & Observability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """
        GAD-000 Test 1: Machine-readable capability discovery.

        Returns structured data about what this plugin can do.
        """
        return {
            "version": "1.1.0",
            "phase": "1 (Drift Detection)",
            "operations": [
                "verify",
                "detect_drift",
                "quick_drift_check",
                "generate_opus_data",
                "get_preserved_sections",
                "has_existing_opus",
            ],
            "capabilities": [
                "opus.verify",
                "opus.drift_detect",
                "opus.generate",
                "opus.preserve",
            ],
            "architecture": {
                "role": "backend",
                "renders": False,
                "provides": "data_only",
            },
            "workspace": str(self._workspace) if self._workspace else None,
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        GAD-000 Test 2: Observability.

        Returns current plugin status.
        """
        status = {
            "plugin_id": "opus_assistant",
            "status": "active" if self._kernel else "inactive",
            "phase": "1",
            "workspace": str(self._workspace) if self._workspace else None,
            "has_opus_md": self.has_existing_opus() if self._workspace else False,
        }

        # Add quick health check if active
        if self._kernel:
            quick = self.quick_drift_check()
            status["drift_health"] = quick.get("healthy", False)
            status["tracked_files"] = quick.get("total_tracked", 0)

        return status
