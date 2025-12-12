"""
OPUS Assistant Plugin - Active manager for OPUS.md ecosystem.

OPUS-029 Phase 2: Dynamic Runtime Context Injection

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
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ ConfigLoader            │    │  ← Fraktale Config
    │  │ defaults.yaml + opus.yaml│   │
    │  └─────────────────────────┘    │
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ OpusContextService      │    │  ← PHASE 2: Dynamic Bootstrapping
    │  │ Synthesize + Inject     │    │     "State of Mind" for all agents
    │  └─────────────────────────┘    │
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ KernelTickHandler       │    │  ← Heartbeat via EventBus
    │  │ Stays ALIVE             │    │     Triggers context synthesis
    │  └─────────────────────────┘    │
    └─────────────────────────────────┘

Config Hierarchy:
1. defaults.yaml (shipped with plugin)
2. config/opus.yaml (system overrides)
3. Runtime overrides

Phase 2 - Dynamic Context:
- On KERNEL_TICK: Synthesize system state from all Prakriti layers
- Inject into EphemeralState as "State of Mind"
- Every spawning agent knows the current reality
- This is ACTIVE, not passive!

OPUS-015: Container-ready (.vibe packable)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader
    from vibe_core.plugins.opus_assistant.core.context_service import OpusContextService
    from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector
    from vibe_core.plugins.opus_assistant.core.observation_logger import ObservationLogger
    from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator
    from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine
    from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler

logger = logging.getLogger("OPUS_ASSISTANT")


class OpusAssistantPlugin(KernelPlugin):
    """
    OPUS Assistant - Active manager for OPUS.md ecosystem.

    IMPORTANT: This plugin provides DATA ONLY.
    The interface plugin is the MASTER for rendering.
    We NEVER render markdown, rich panels, or any UI.

    Phase 2 Capabilities:
    - opus.verify: Run @HARNESS verification
    - opus.drift_detect: Compare code vs docs
    - opus.generate: Generate OPUS.md data
    - opus.preserve: Get preserved sections from existing OPUS.md
    - opus.tick: Respond to kernel tick events
    - opus.context: Dynamic runtime context synthesis
    - opus.prompt: Get system prompt fragment for agents
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
        self._config_loader: Optional["ConfigLoader"] = None
        self._tick_handler: Optional["KernelTickHandler"] = None

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Initialize OPUS Assistant on kernel boot.

        1. Get workspace path
        2. Load fraktale config (defaults + opus.yaml)
        3. Subscribe to kernel tick (EventBus)
        4. Quick health check
        """
        self._kernel = kernel

        # Get workspace path
        self._workspace = getattr(kernel, "workspace_path", None) or Path.cwd()

        # Load fraktale config
        self._load_fraktale_config()

        # Subscribe to kernel tick
        self._setup_kernel_tick()

        # Quick health check on boot
        if self._config.get("drift", {}).get("check_on_boot", False):
            drift = self.quick_drift_check()
            if not drift.get("healthy", True):
                logger.warning(f"⚠️ OPUS drift: {len(drift.get('missing_files', []))} missing files")

        logger.info("🎯 OPUS Assistant online (fraktale config + kernel tick)")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Cleanup on kernel shutdown."""
        # Unsubscribe from events
        if self._tick_handler:
            self._tick_handler.unsubscribe()

        logger.info("🎯 OPUS Assistant shutdown")

    def _load_fraktale_config(self) -> None:
        """
        Load config using fraktale pattern.

        Merges: defaults.yaml (plugin) + opus.yaml (system)
        """
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        self._config_loader = ConfigLoader(workspace_root=self._workspace or Path.cwd())
        self._config = self._config_loader.load()

        logger.debug(f"Loaded config: {list(self._config.keys())}")

    def _setup_kernel_tick(self) -> None:
        """
        Setup kernel tick handler.

        Subscribes to EventBus for constant context feed.
        """
        if not self._config.get("kernel_tick", {}).get("enabled", True):
            logger.debug("Kernel tick disabled in config")
            return

        try:
            from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler

            self._tick_handler = KernelTickHandler(self)
            if self._tick_handler.subscribe():
                logger.debug("Kernel tick handler active")
        except ImportError:
            logger.debug("EventBus not available - tick handler disabled")
        except Exception as e:
            logger.debug(f"Could not setup kernel tick: {e}")

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
        from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        config = self._config.get("verification", {})
        engine = VerificationEngine(workspace_root=workspace, config=config)
        return engine.run_verification(quick=quick)

    def detect_drift(self, since_commit: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect drift between code and documentation.

        Returns DATA (dict), not rendered output.

        Args:
            since_commit: Git ref to compare against (default from config)

        Returns:
            Drift report dict
        """
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        detector = DriftDetector(workspace_root=workspace)

        # Use config default if not specified
        if since_commit is None:
            since_commit = self._config.get("drift", {}).get("default_since", "HEAD~10")

        report = detector.detect(since_commit=since_commit)
        return report.to_dict()

    def quick_drift_check(self) -> Dict[str, Any]:
        """
        Quick drift check (boot-time, fast).

        Returns DATA (dict), not rendered output.

        Returns:
            Quick check results dict
        """
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

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
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

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
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        generator = OpusGenerator(workspace_root=workspace)
        return generator.get_preserved_sections()

    def has_existing_opus(self) -> bool:
        """Check if OPUS.md already exists in workspace root."""
        workspace = self._workspace or Path.cwd()
        return (workspace / "OPUS.md").exists()

    def write_opus_md(self, quick: bool = False) -> Path:
        """
        Write OPUS.md directly.

        OPUS-029 Migration: opus_assistant now writes its own OPUS.md.
        Previously done by interface/renderers/opus/ (now deleted).

        Args:
            quick: Skip expensive semantic verification

        Returns:
            Path to written OPUS.md
        """
        from vibe_core.plugins.opus_assistant.render.opus_md_writer import OpusMdWriter

        workspace = self._workspace or Path.cwd()
        writer = OpusMdWriter(workspace, kernel=self._kernel)
        return writer.write(quick=quick)

    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get plugin config value.

        Args:
            key: Dot-notation key (e.g., "verification.enabled")
                 If None, returns entire config
            default: Default value if key not found

        Returns:
            Config value or default
        """
        if key is None:
            return self._config

        if self._config_loader:
            return self._config_loader.get(key, default)

        return default

    def reload_config(self) -> Dict[str, Any]:
        """
        Force reload config from files.

        Returns:
            New merged config
        """
        if self._config_loader:
            self._config = self._config_loader.reload()
        return self._config

    # =========================================================================
    # Engine Accessors (for interface plugin)
    # =========================================================================

    def get_verification_engine(self) -> "VerificationEngine":
        """Get a VerificationEngine instance."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        config = self._config.get("verification", {})
        return VerificationEngine(workspace_root=workspace, config=config)

    def get_drift_detector(self) -> "DriftDetector":
        """Get a DriftDetector instance."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        return DriftDetector(workspace_root=workspace)

    def get_opus_generator(self) -> "OpusGenerator":
        """Get an OpusGenerator instance."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        return OpusGenerator(workspace_root=workspace)

    def get_context_service(self) -> Optional["OpusContextService"]:
        """
        Get the OpusContextService instance.

        Returns:
            OpusContextService or None if tick handler not active
        """
        if self._tick_handler:
            return self._tick_handler.get_context_service()
        return None

    # =========================================================================
    # Phase 2: Context Service API
    # =========================================================================

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """
        Get current synthesized context.

        This is the "State of Mind" - what every agent should know.

        Returns:
            Current context dict or None
        """
        if self._tick_handler:
            return self._tick_handler.get_current_context()
        return None

    def get_system_prompt_fragment(self) -> str:
        """
        Get current system prompt fragment.

        This should be prepended to agent system prompts so they
        know the current "State of Mind" of the system.

        Returns:
            System prompt fragment string (markdown)
        """
        if self._tick_handler:
            return self._tick_handler.get_system_prompt_fragment()
        return ""

    def synthesize_context(self) -> Optional[Dict[str, Any]]:
        """
        Force immediate context synthesis.

        Useful for getting fresh context outside of tick cycle.

        Returns:
            Freshly synthesized context dict or None
        """
        context_service = self.get_context_service()
        if context_service:
            context = context_service.synthesize()
            context_service.inject(context)
            return context.to_dict()
        return None

    # =========================================================================
    # GAD-000: Discoverability & Observability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """
        GAD-000 Test 1: Machine-readable capability discovery.

        Returns structured data about what this plugin can do.
        """
        context_service = self.get_context_service()

        return {
            "version": self._config.get("plugin", {}).get("version", "1.2.0"),
            "phase": self._config.get("plugin", {}).get("phase", 2),
            "operations": [
                "verify",
                "detect_drift",
                "quick_drift_check",
                "generate_opus_data",
                "get_preserved_sections",
                "has_existing_opus",
                "get_config",
                "reload_config",
                # Phase 2: Context
                "get_current_context",
                "get_system_prompt_fragment",
                "synthesize_context",
            ],
            "capabilities": [
                "opus.verify",
                "opus.drift_detect",
                "opus.generate",
                "opus.preserve",
                "opus.config",
                "opus.tick",
                # Phase 2: Dynamic Context
                "opus.context",
                "opus.prompt",
            ],
            "architecture": {
                "role": "backend",
                "renders": False,
                "provides": "data_only",
                "config_pattern": "fraktale",
                "kernel_tick": self._tick_handler is not None,
                "context_service": context_service is not None,
            },
            "workspace": str(self._workspace) if self._workspace else None,
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        GAD-000 Test 2: Observability.

        Returns current plugin status including Phase 2 context info.
        """
        status = {
            "plugin_id": "opus_assistant",
            "status": "active" if self._kernel else "inactive",
            "version": self._config.get("plugin", {}).get("version", "1.2.0"),
            "phase": self._config.get("plugin", {}).get("phase", 2),
            "workspace": str(self._workspace) if self._workspace else None,
            "has_opus_md": self.has_existing_opus() if self._workspace else False,
            "config_loaded": self._config_loader is not None,
            "kernel_tick_active": self._tick_handler is not None,
        }

        # Add quick health check if active
        if self._kernel:
            quick = self.quick_drift_check()
            status["drift_health"] = quick.get("healthy", False)
            status["tracked_files"] = quick.get("total_tracked", 0)

        # Add tick handler state if available
        if self._tick_handler:
            status["tick_state"] = self._tick_handler.get_state()

        # Phase 2: Add context service status
        context_service = self.get_context_service()
        if context_service:
            status["context_service_active"] = True
            status["context_synthesis_count"] = context_service.get_synthesis_count()
            current_context = self.get_current_context()
            if current_context:
                status["current_system_health"] = current_context.get("health", {}).get("status")
                status["context_hash"] = current_context.get("context_hash", "")[:16]
        else:
            status["context_service_active"] = False

        return status

    # =========================================================================
    # Phase 3: CLI Command Handlers
    # =========================================================================

    def cmd_opus_status(self, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:status

        Shows the current "State of Mind" - live context from the system.

        Args:
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted status dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        # Get current context, or synthesize fresh if not available
        context = self.get_current_context()
        if context is None:
            context = self.synthesize_context()
        return format_status_output(context, json_mode=json)

    def cmd_opus_log(self, limit: int = 20, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:log

        Shows journal entries from OPUS.md (parsed observations).

        Args:
            limit: Max entries to show
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted log dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output, parse_journal_from_opus

        workspace = self._workspace or Path.cwd()
        opus_path = workspace / "OPUS.md"

        observations = parse_journal_from_opus(opus_path)
        return format_log_output(observations, limit=limit, json_mode=json)

    def cmd_opus_verify(self, quick: bool = False, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:verify

        Manual trigger for verification loop.

        Args:
            quick: If True, skip semantic checks (faster)
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted verification dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_verify_output

        verification = self.verify(quick=quick)
        return format_verify_output(verification, json_mode=json)

    def cmd_opus_refresh(self, quick: bool = True, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:refresh

        Manually regenerate OPUS.md.

        Args:
            quick: If True, skip semantic checks (faster, default)
            json: If True, return raw JSON-compatible data

        Returns:
            Result dict with path and status
        """
        import time

        start = time.time()
        result_path = self.write_opus_md(quick=quick)
        elapsed = time.time() - start

        result = {
            "status": "success",
            "path": str(result_path),
            "elapsed_ms": int(elapsed * 1000),
            "quick_mode": quick,
        }

        if json:
            return result

        result["output"] = f"OPUS.md refreshed in {int(elapsed * 1000)}ms"
        return result

    def get_observation_logger(self) -> Optional["ObservationLogger"]:
        """
        Get the ObservationLogger instance for direct logging.

        Returns:
            ObservationLogger or None if tick handler not active
        """
        if self._tick_handler:
            return self._tick_handler.get_observation_logger()
        return None
