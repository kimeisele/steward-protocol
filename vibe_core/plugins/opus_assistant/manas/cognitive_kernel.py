"""
MANAS Cognitive Kernel - The Mind of OPUS.

OPUS-032: The Awakening

"Cogito, ergo sum" - I think, therefore I am.
    - René Descartes

This is the central orchestrator of MANAS:
- Rate-limited thinking (not every tick!)
- Intent generation and management
- Human-in-the-loop approval flow
- Memory integration for learning
- Auto-execution for safe tasks

The Cognitive Kernel transforms OPUS from a reactive system
to a proactive autonomous agent.
"""

import asyncio
import hashlib
import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from vibe_core.di import ServiceRegistry
from vibe_core.event_bus import EventBus

# OPUS-171: BridgeLoader for auto-discovery of bridges
# Replaces manual imports of GenesisBridge, WeaverBridge, LoggerBridge
from vibe_core.loaders import ActionLoader, AnalyzerLoader, BridgeLoader, SenseLoader, ToolLoader
from vibe_core.orchestration_cycle import CognitiveCycle, CycleContext
from vibe_core.protocols import CognitiveKernelProtocol
from vibe_core.runtime.unified_trace import UnifiedTrace

# OPUS-167: Action Manager Extraction (Karmendriya)
from .action_manager import ActionManager

# OPUS-176: Biorhythm Processor - Extracted consciousness tick logic
from .biorhythm import BiorhythmProcessor
from .buddhi import Buddhi

# OPUS-168: Antahkarana - The Inner Instrument
from .chitta import Chitta

# OPUS-167: Intent Buffer Extraction
from .intent_buffer import IntentBuffer, IntentBufferEntry
from .intent_generator import Intent, IntentGenerator, IntentPriority, IntentRisk
from .memory_store import MemoryStore

# OPUS-167: Sense Manager Extraction
from .sense_manager import SenseManager
from .shiva import ShivaLifecycleManager  # OPUS-082: Destroyer of Illusions

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.state.cognitive_weaver import CognitiveWeaver
    from vibe_core.tools.tool_registry import ToolRegistry

    from .cortex.dharma_sense import DharmaSense
    from .cortex.karma_sense import KarmaSense
    from .cortex.prakriti_sense import PrakritiSense
    from .cortex.prana_sense import PranaSense
    from .cortex.shruta_sense import ShrutaPerception, ShrutaSense
    from .cortex.sutra_sense import SutraSense
    from .cortex.viveka_sense import VivekaSense

logger = logging.getLogger("MANAS.Kernel")

# ⚡ PHOENIX INJECTION: Import ManasConfig from Phoenix section (Dharma)
# This ensures MANAS uses the same config structure as Phoenix defines
try:
    from vibe_core.phoenix.sections.manas import ManasConfig

    logger.debug("⚡ MANAS: Using ManasConfig from Phoenix section (Dharma)")
except ImportError:
    # Fallback: Define locally if Phoenix not available
    @dataclass
    class ManasConfig:
        """Configuration for MANAS Cognitive Kernel (Local Fallback)."""

        # Thinking rate limit (minimum time between thought cycles)
        # OPUS-174: Was 60 (lobotomy!), now 10min for responsiveness
        thinking_interval_minutes: int = 10

        # Idle threshold (activate MANAS after this much idle time)
        # OPUS-174: Was 30, now 5min for faster idle detection
        idle_threshold_minutes: int = 5

        # Auto-execute safe intents without approval?
        auto_execute_safe: bool = False  # Conservative default

        # Max intents to keep in buffer
        max_intent_buffer_size: int = 10

        # Intent expiry (hours)
        intent_expiry_hours: int = 24

        # KARMA GATE: Threshold for earned autonomy (0-100)
        # High karma (Bhakti + success) grants trust for LOW risk auto-execute
        karma_auto_execute_threshold: int = 90

        # OPUS-035: Intent Throttling - Don't overwhelm the human
        # Max intents to generate per tick (prioritize CRITICAL/HIGH over LOW)
        max_intents_per_tick: int = 3

        # OPUS-035: Prioritize survival over growth
        # If True, CRITICAL/ERROR intents are processed before GENESIS intents
        survival_first: bool = True

    logger.warning("⚠️ MANAS: Phoenix section not available, using local ManasConfig fallback")


@dataclass
class IntentConfidence:
    """
    OPUS-032: Confidence is not a guess - it's a computed vector.

    Three components determine if we can auto-execute:
    1. pattern_match: Have we seen this exact failure before?
    2. karma_level: Does the system have enough "credit"?
    3. rollback_safety: Can we easily undo this action?

    Usage:
        confidence = IntentConfidence.compute(intent, memory, karma_score=85)
        if confidence.total_score >= 0.9:
            # Safe to auto-execute
    """

    pattern_match: float = 0.0  # 0.0-1.0: How often have we fixed this before?
    karma_level: float = 0.0  # 0.0-1.0: Current karma / 100
    rollback_safety: float = 0.0  # 0.0-1.0: How easy to git revert?

    @property
    def total_score(self) -> float:
        """
        Compute total confidence.

        CRITICAL: If rollback is unsafe, confidence is ZERO.
        We never auto-execute irreversible actions.
        """
        if self.rollback_safety < 0.5:
            return 0.0  # Safety first!

        # Weighted: Karma matters more than pattern matching
        return (self.pattern_match * 0.4) + (self.karma_level * 0.6)

    @classmethod
    def compute(
        cls,
        intent: "Intent",
        memory: "MemoryStore",
        karma_score: int,
    ) -> "IntentConfidence":
        """
        Factory method to compute confidence for an intent.

        Args:
            intent: The intent to evaluate
            memory: Memory store for pattern lookup
            karma_score: Current karma score (0-100)

        Returns:
            IntentConfidence with computed values
        """
        # Pattern match: Have we successfully done this before?
        success_rate = memory.get_success_rate(intent.intent_type)
        pattern_match = success_rate if success_rate else 0.0

        # Karma level: Normalize to 0-1
        karma_level = karma_score / 100.0

        # Rollback safety: Based on intent type
        safe_types = {"contract_surrender", "doc_update", "test_create", "contract_doc_update"}
        unsafe_types = {"capability_genesis", "refactor_major", "delete_file", "contract_import_fix"}

        if intent.intent_type in safe_types:
            rollback_safety = 1.0
        elif intent.intent_type in unsafe_types:
            rollback_safety = 0.3
        else:
            rollback_safety = 0.7  # Default: medium safety

        return cls(
            pattern_match=pattern_match,
            karma_level=karma_level,
            rollback_safety=rollback_safety,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/display."""
        return {
            "pattern_match": self.pattern_match,
            "karma_level": self.karma_level,
            "rollback_safety": self.rollback_safety,
            "total_score": self.total_score,
        }


class CognitiveKernel(CognitiveKernelProtocol):
    """
    MANAS Cognitive Kernel - The central Mind of OPUS.

    OPUS-095 REFACTORING: Inherits from CognitiveCycle
    - Uses unified orchestration loop (UnifiedTrace, EventBus)
    - OODA phases: _perceive(), _orient(), _decide(), _act(), _persist()
    - Integrated with system observability

    This kernel:
    1. Monitors system state via Prakriti (PERCEIVE)
    2. Generates intents when opportunities arise (DECIDE)
    3. Manages intent buffer (displayed in OPUS.md)
    4. Handles approval/rejection flow
    5. Executes approved intents (via CircuitExecutor as CognitiveProcess)
    6. Learns from outcomes via MemoryStore

    Rate Limiting:
    - MANAS doesn't think on every KERNEL_TICK
    - It activates on an hourly pulse or after idle threshold
    - This prevents token/CPU burn

    Human-in-the-Loop:
    - Most intents go to Intent Buffer for approval
    - Only SAFE risk intents can auto-execute
    - User can approve/reject from OPUS.md

    OPUS-167: SINGLETON PATTERN (Workspace-Keyed)
    - Tool discovery is expensive (~2-3 seconds per instantiation)
    - Multiple instantiations during boot caused 20+ second delays
    - Use get_instance() instead of direct instantiation
    - Same pattern as GenesisService.get_instance()
    """

    # =========================================================================
    # OPUS-167: SINGLETON PATTERN (Workspace-Keyed)
    # =========================================================================
    # "The mind is one. Multiple heads is madness." - Sankhya Philosophy
    #
    # Each workspace gets ONE CognitiveKernel instance.
    # Tool discovery happens ONCE, not 8 times during boot.
    # =========================================================================
    _instances: Dict[Path, "CognitiveKernel"] = {}

    @classmethod
    def get_instance(
        cls,
        workspace: Optional[Path] = None,
        config: Optional[ManasConfig] = None,
        trace: Optional[UnifiedTrace] = None,
        event_bus: Optional[EventBus] = None,
    ) -> "CognitiveKernel":
        """
        Get singleton CognitiveKernel instance for workspace.

        OPUS-167: This is the ONLY way to get a CognitiveKernel.
        Direct instantiation should be avoided in production code.

        The expensive tool discovery happens only on first call.
        Subsequent calls return the cached instance.

        Args:
            workspace: Workspace root (defaults to cwd)
            config: Optional ManasConfig (only used on first creation)
            trace: Optional UnifiedTrace (only used on first creation)
            event_bus: Optional EventBus (only used on first creation)

        Returns:
            CognitiveKernel singleton for the workspace
        """
        ws = workspace or Path.cwd()
        ws = ws.resolve()  # Normalize path for consistent keying

        if ws not in cls._instances:
            logger.info(f"🧠 MANAS: Creating singleton instance for {ws}")
            instance = cls(
                workspace=ws,
                config=config,
                trace=trace,
                event_bus=event_bus,
            )
            cls._instances[ws] = instance

            # Register in DI for protocol-based discovery
            ServiceRegistry.register(CognitiveKernelProtocol, instance)
        else:
            logger.debug(f"🧠 MANAS: Reusing singleton instance for {ws}")

        return cls._instances[ws]

    @classmethod
    def reset_instance(cls, workspace: Optional[Path] = None) -> None:
        """
        Reset singleton instance (for testing).

        Args:
            workspace: Workspace to reset (None = reset all)
        """
        if workspace is None:
            cls._instances.clear()
            logger.info("🧠 MANAS: All singleton instances reset")
        else:
            ws = workspace.resolve()
            if ws in cls._instances:
                del cls._instances[ws]
                logger.info(f"🧠 MANAS: Singleton instance reset for {ws}")

    @classmethod
    def has_instance(cls, workspace: Optional[Path] = None) -> bool:
        """
        Check if singleton instance exists for workspace.

        Useful to avoid triggering expensive initialization when just checking.

        Args:
            workspace: Workspace to check (defaults to cwd)

        Returns:
            True if instance already exists
        """
        ws = (workspace or Path.cwd()).resolve()
        return ws in cls._instances

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[ManasConfig] = None,
        trace: Optional[UnifiedTrace] = None,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialize MANAS Cognitive Kernel.

        OPUS-095: Integrated with CognitiveCycle for unified orchestration.

        Args:
            workspace: Workspace root
            config: Optional configuration
            trace: Optional UnifiedTrace for observability (Phase A integration)
            event_bus: Optional EventBus for phase transition events (Phase A integration)
        """
        # Initialize CognitiveCycle base class
        super().__init__()

        self._workspace = workspace or Path.cwd()
        self._config = config or ManasConfig()

        # Phase A System Integration: Setup trace and event bus if provided
        if trace and event_bus:
            self.setup(trace, event_bus, steward_context=None)

        # 🔌 WIRE: Load full config/manas.yaml for feature configs
        # ManasConfig only has core fields - features need their own sections
        self._full_config = self._load_full_config()

        # Core components
        self._memory = MemoryStore(workspace=self._workspace)

        # 🎯 OPUS-106: VEDA-4 Fractal Loaders (Private Scope)
        # OPUS has its own isolated view of capabilities - "As Above, So Below"
        # These loaders are OPUS's private brain, not shared with the system
        self._action_loader = ActionLoader(scope="opus_private")
        self._sense_loader = SenseLoader(scope="opus_private")
        self._analyzer_loader = AnalyzerLoader(scope="opus_private")
        self._tool_loader = ToolLoader(scope="opus_private", root_path=self._workspace)

        # Pre-load cortex modules (warm the cache)
        self._action_loader.load()
        self._sense_loader.load()
        self._analyzer_loader.load()
        self._tool_loader.load()
        logger.info("🎯 OPUS-106: Fractal Loaders initialized (scope=opus_private)")

        # 🧠 SEMANTIC ENGINE: The "Brain" (Lazy Loaded)
        self._semantic_engine: Any = None
        self._init_semantic_engine()

        # OPUS-167: Pass analyzer_loader to avoid duplicate loading
        self._intent_generator = IntentGenerator(
            workspace=self._workspace,
            memory_store=self._memory,
            analyzer_loader=self._analyzer_loader,
        )
        # Inject engine if available
        if self._semantic_engine:
            self._intent_generator.inject_semantic_engine(self._semantic_engine)

        # OPUS-167: Intent buffer extracted to separate class
        self._buffer = IntentBuffer(
            workspace=self._workspace,
            max_size=self._config.max_intent_buffer_size,
            expiry_hours=self._config.intent_expiry_hours,
        )

        # Rate limiting state
        self._last_thought_time: Optional[datetime] = None
        self._last_activity_time: datetime = datetime.utcnow()

        # Callbacks for execution
        self._execution_callback: Optional[Callable[[Intent], Dict[str, Any]]] = None

        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel: Optional["RealVibeKernel"] = None

        # OPUS-112: Global tool registry for direct dispatch (SYSTEM ACT mode)
        self._global_tool_registry: Optional["ToolRegistry"] = None

        # 🦁 NARASIMHA: The Cognitive Guardian (Conscience)
        from ..narasimha.guardian import CortexNarasimha

        self._narasimha = CortexNarasimha(workspace=self._workspace)

        # OPUS-167: Unified Sense Manager (replaces individual _init_* calls)
        self._sense_manager = SenseManager(
            workspace=self._workspace,
            config=self._full_config,
        )
        self._sense_manager.boot_all()

        # Inject semantic engine into sutra sense if available
        if self._sense_manager.sutra_sense and self._semantic_engine:
            self._sense_manager.sutra_sense.inject_semantic_engine(self._semantic_engine)

        # Post-boot setup for sense listeners (Shruta/Prana wiring)
        self._setup_sense_listeners()

        # 🫀 PRANA SENSE: Cooldown tracking (kernel-specific, not in SenseManager)
        # "Prana is the breath of the universe. When an agent breathes, it leaves a trace."
        self._prana_cooldowns: Dict[str, datetime] = {}  # Cooldown per agent (avoid intent spam)
        self._prana_cooldown_minutes: int = 10  # OPUS-035 pattern: 10 min between death intents

        # 🧠 OPUS-168: ANTAHKARANA - The Inner Instrument
        # Chitta (Perception Pool) + Buddhi (Intellect) form the decision layer
        # This fixes: DharmaSense checked at DECIDE time, not EXECUTE time
        self._chitta = Chitta(workspace=self._workspace)
        self._buddhi = Buddhi(workspace=self._workspace, dharma_sense=self._sense_manager.dharma_sense)
        logger.info("🧠 OPUS-168: Antahkarana initialized (Chitta + Buddhi)")

        # =================================================================
        # OPUS-171: BridgeLoader - Auto-discover all bridges (VEDA-4)
        # =================================================================
        # Replaces manual instantiation of GenesisBridge, WeaverBridge, LoggerBridge
        self._bridges, bridge_meta = BridgeLoader.discover_and_load(
            workspace=self._workspace,
            config=self._full_config,
        )
        logger.info(
            f"🌉 OPUS-171: {len(self._bridges)} bridges loaded via BridgeLoader ({', '.join(self._bridges.keys())})"
        )

        # Expose bridges as named attributes for backward compatibility
        self._genesis_bridge = self._bridges.get("genesis_bridge")
        self._weaver_bridge = self._bridges.get("weaver_bridge")
        self._logger_bridge = self._bridges.get("logger_bridge")

        # 🕉️ SHIVA: The Destroyer of Illusions - Lifecycle Manager (OPUS-082)
        shiva_config = self._full_config.get("shiva", {})
        self._shiva = ShivaLifecycleManager(workspace=self._workspace, config=shiva_config)
        self._shiva.inject_kernel(self)

        # 🌙 SANKALPA: Strategic Will - Proactive Mission Planning (OPUS-089)
        self._sankalpa = None
        self._init_sankalpa()

        # 🧠 OPUS-112: SYNAPTIC MEMORY - The Reading Brain
        # Inference engine for experience-based decision making
        from .triggers import SynapticMemory

        self._synaptic_memory = SynapticMemory.get(self._workspace)
        logger.info(
            f"🧠 OPUS-112: Synaptic Memory initialized "
            f"({self._synaptic_memory.get_stats()['total_connections']} connections)"
        )

        # OPUS-167: Action Manager (Karmendriya) - The Action Organs
        # Handles all intent execution, routing, and learning
        self._action_manager = ActionManager(
            workspace=self._workspace,
            memory=self._memory,
            synaptic=self._synaptic_memory,
        )
        # Inject dependencies that are initialized lazily
        self._action_manager.inject_narasimha(self._narasimha)

        # OPUS-176: Biorhythm Processor - handles tick(), consciousness states
        self._biorhythm = BiorhythmProcessor(kernel=self)
        self._awareness: Dict[str, Any] = {}  # Shared with biorhythm

        logger.info(
            "MANAS Cognitive Kernel initialized (with Shiva + Sankalpa + Synaptic Inference + Karmendriya + Biorhythm)"
        )

    # =========================================================================
    # 🧠 SEMANTIC ENGINE: INTELLIGENCE UPGRADE (OPUS-096)
    # =========================================================================

    def _init_semantic_engine(self) -> None:
        """
        Initialize the Semantic Engine (optional).

        This is the "Slim Build / Smart Integration" implementation.
        We attempt to graft intelligence from the environment (The Garden).
        If available (in ~/.steward/lib or site-packages), we load it.
        """
        try:
            # OPUS-096: Smart Integration - Grafting the Garden
            # We must extend runtime to find extensions in ~/.steward/lib
            try:
                from vibe_core.runtime_extensions import extend_runtime

                extend_runtime()
            except ImportError:
                # Should not happen in bundled env, but safe fallback
                pass

            # Now we can safely attempt to import the engine
            # The engine itself handles the heavy imports (numpy/torch/transformers)
            # VERIFY: Do we actually have the heavy deps?
            # SemanticRouter is lazy, so we must check explicitly to avoid False positives.
            import sentence_transformers

            from vibe_core.cortex.engines.semantic_engine import SemanticRouter

            knowledge_dir = self._workspace / "knowledge"
            self._semantic_engine = SemanticRouter(knowledge_dir=str(knowledge_dir))
            logger.info("🧠 SEMANTIC ENGINE: Connected (Intelligence Level 2)")

        except ImportError as e:
            # Graceful fallback - Slim Mode
            self._semantic_engine = None
            logger.info(f"🧠 SEMANTIC ENGINE: Not available ({e}) - Running in Lean Mode")
        except Exception as e:
            self._semantic_engine = None
            logger.warning(f"🧠 SEMANTIC ENGINE: Failed to initialize: {e}")

    @property
    def has_intelligence(self) -> bool:
        """Check if MANAS has active semantic intelligence."""
        return self._semantic_engine is not None

    # =========================================================================
    # OPUS-106: VEDA-4 FRACTAL LOADER PROPERTIES
    # =========================================================================

    @property
    def action_loader(self) -> ActionLoader:
        """
        OPUS's private ActionLoader (scope=opus_private).

        Use this for fractal routing - OPUS's isolated view of actions.
        """
        return self._action_loader

    @property
    def sense_loader(self) -> SenseLoader:
        """
        OPUS's private SenseLoader (scope=opus_private).

        Use this for fractal perception - OPUS's isolated view of senses.
        """
        return self._sense_loader

    @property
    def analyzer_loader(self) -> AnalyzerLoader:
        """
        OPUS's private AnalyzerLoader (scope=opus_private).

        Use this for fractal analysis - OPUS's isolated view of analyzers.
        """
        return self._analyzer_loader

    @property
    def tool_loader(self) -> ToolLoader:
        """
        OPUS's private ToolLoader (scope=opus_private).

        Use this for fractal tooling - OPUS's isolated view of cartridge tools.
        Actions can access tools dynamically via this loader.
        """
        return self._tool_loader

    # =========================================================================
    # OPUS-167: SENSE MANAGER PROPERTIES (Backward Compatibility)
    # =========================================================================

    @property
    def _prakriti_sense(self) -> Optional["PrakritiSense"]:
        """Prakriti Sense - delegates to SenseManager."""
        return self._sense_manager.prakriti_sense

    @property
    def _dharma_sense(self) -> Optional["DharmaSense"]:
        """Dharma Sense - delegates to SenseManager."""
        return self._sense_manager.dharma_sense

    @property
    def _sutra_sense(self) -> Optional["SutraSense"]:
        """Sutra Sense - delegates to SenseManager."""
        return self._sense_manager.sutra_sense

    @property
    def _shruta_sense(self) -> Optional["ShrutaSense"]:
        """Shruta Sense - delegates to SenseManager."""
        return self._sense_manager.shruta_sense

    @property
    def _prana_sense(self) -> Optional["PranaSense"]:
        """Prana Sense - delegates to SenseManager."""
        return self._sense_manager.prana_sense

    @property
    def _karma_sense(self) -> Optional["KarmaSense"]:
        """Karma Sense - delegates to SenseManager."""
        return self._sense_manager.karma_sense

    @property
    def _viveka_sense(self) -> Optional["VivekaSense"]:
        """Viveka Sense - delegates to SenseManager."""
        return self._sense_manager.viveka_sense

    # =========================================================================
    # OPUS-095: COGNITIVECYCLE PROPERTIES
    # =========================================================================

    @property
    def cycle_name(self) -> str:
        """Cycle name for orchestration tracking."""
        return "cognitive_kernel"

    @property
    def rate_limit_seconds(self) -> int:
        """Rate limit based on config (default 15 minutes = 900 seconds)."""
        thinking_interval_minutes = self._config.thinking_interval_minutes
        return thinking_interval_minutes * 60

    @property
    def timeout_seconds(self) -> int:
        """Max thinking time (5 minutes)."""
        return 300

    @property
    def recovery_enabled(self) -> bool:
        """Enable error recovery."""
        return True

    # =========================================================================
    # 🔌 CONFIG LOADING (OPUS-092)
    # =========================================================================

    def _load_full_config(self) -> Dict[str, Any]:
        """
        Load full config/manas.yaml.

        Phoenix ManasConfig only loads core fields (8 fields).
        Features (Sankalpa, Shiva, etc.) need their own config sections.

        Returns:
            Full config dict with all sections, or empty dict if file missing
        """
        import yaml

        config_file = Path("config/manas.yaml")
        if not config_file.exists():
            logger.warning(f"⚠️ Config file not found: {config_file}")
            return {}

        try:
            with open(config_file) as f:
                full_config = yaml.safe_load(f) or {}
            logger.info(f"🔌 Loaded full config with {len(full_config)} sections")
            return full_config
        except Exception as e:
            logger.error(f"❌ Failed to load {config_file}: {e}")
            return {}

    # =========================================================================
    # ⚡ VAJRA: KERNEL INTEGRATION (OPUS-057)
    # =========================================================================

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        Inject the core VibeKernel for ledger access and tool registry.

        OPUS-057 VAJRA: Every intent MUST be recorded in the ledger.
        Without kernel injection, MANAS operates in "shadow mode" (no ledger).

        OPUS-112 SYNAPTIC BRIDGE: Also stores reference to kernel.tool_registry
        for direct tool dispatch (SYSTEM ACT mode).

        Args:
            kernel: The RealVibeKernel instance
        """
        self._vibe_kernel = kernel

        # OPUS-112: Store tool_registry reference for direct dispatch
        if hasattr(kernel, "tool_registry"):
            self._global_tool_registry = kernel.tool_registry
            logger.info("⚡ VAJRA: Kernel injected - ledger + tool_registry ACTIVE")

            # OPUS-175: Inject ToolRegistry into ActionManager for TaskKernel
            self._action_manager.inject_tool_registry(kernel.tool_registry)
            self._action_manager.enable_task_kernel(enabled=True)
            logger.info("⚡ OPUS-175: TaskKernel execution mode ENABLED")
        else:
            self._global_tool_registry = None
            logger.info("⚡ VAJRA: Kernel injected - ledger ACTIVE (no tool_registry)")

    def inject_ledger(self, ledger: Any) -> None:
        """
        Inject a standalone ledger for autonomous mode (heartbeat).

        OPUS-074 WIRING: Allows VAJRA binding without full Kernel boot.
        Used by heartbeat.py for headless/autonomous operation.

        Args:
            ledger: SQLiteLedger or compatible ledger instance
        """
        self._ledger = ledger
        logger.info("⚡ VAJRA: Standalone Ledger injected into MANAS (headless mode)")

    # =========================================================================
    # 👁️ PRAKRITI SENSE: THE SIXTH JNANENDRIYA (OPUS-009)
    # OPUS-167: Initialization moved to SenseManager
    # =========================================================================

    def inject_prakriti_sense(self, sense: "PrakritiSense") -> None:
        """
        Inject the sixth sense for unified state awareness.

        OPUS-009: MANAS (Mind) needs Jnanendriyas (sense organs) to perceive
        Prakriti (state). This IS that sixth sense.

        With this injected, MANAS can:
        - Perceive system state health (Sattva/Rajas/Tamas)
        - Detect lobotomy (.gitignore violations)
        - Generate healing intents automatically

        Args:
            sense: PrakritiSense instance
        """
        self._sense_manager.inject("prakriti_sense", sense)
        # OPUS-167: Also inject into ActionManager for healing execution
        self._action_manager.inject_prakriti(sense)
        logger.info("👁️ PRAKRITI SENSE: Sixth Jnanendriya injected - MANAS can now perceive state")

    def _perceive_and_generate_healing_intents(self) -> List[Intent]:
        """
        Use PrakritiSense to perceive state and generate healing intents.

        Called at the start of think() to ensure MANAS is aware of
        system state health before generating other intents.

        Returns:
            List of healing intents (if any state needs attention)
        """
        if not self._prakriti_sense:
            return []

        healing_intents = []

        try:
            # Perceive state
            summary = self._prakriti_sense.on_manas_tick()

            if summary and summary.needs_attention:
                logger.info(
                    f"👁️ PRAKRITI SENSE: State needs attention - "
                    f"Tamas: {summary.tamas_count}, Rajas: {summary.rajas_count}"
                )

                # Generate healing intent for Tamas paths
                if summary.tamas_count > 0:
                    tamas_paths = self._prakriti_sense.get_tamas_paths()
                    path_names = [str(p.path.name) for p in tamas_paths[:3]]

                    intent = Intent(
                        id=f"heal_state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        intent_type="heal_system_state",
                        title=f"Heal {summary.tamas_count} Tamas state paths",
                        description=(
                            f"System state health check detected {summary.tamas_count} paths in Tamas (stale/broken). "
                            f"Paths: {', '.join(path_names)}{'...' if len(tamas_paths) > 3 else ''}. "
                            f"Healing will push state Tamas → Rajas → Sattva."
                        ),
                        reasoning="PRAKRITI SENSE detected unhealthy state that needs healing.",
                        priority=IntentPriority.HIGH,  # State health is important
                        risk=IntentRisk.SAFE,  # Healing is always safe
                        params={
                            "tamas_count": summary.tamas_count,
                            "rajas_count": summary.rajas_count,
                            "paths": [str(p.path) for p in tamas_paths],
                        },
                        auto_executable=True,  # Healing can auto-execute
                    )
                    healing_intents.append(intent)

            # Check for lobotomy
            lobotomy = self._prakriti_sense.sense_lobotomy()
            if lobotomy.has_lobotomy:
                logger.critical(f"👁️ PRAKRITI SENSE: LOBOTOMY DETECTED! {len(lobotomy.violations)} violations")

                intent = Intent(
                    id=f"fix_lobotomy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    intent_type="fix_lobotomy",
                    title=f"Fix LOBOTOMY: {len(lobotomy.violations)} state files in .gitignore",
                    description=(
                        f"CRITICAL: State files are being ignored by git! "
                        f"This causes memory loss (lobotomy). "
                        f"Affected plugins: {', '.join(lobotomy.affected_plugins)}. "
                        f"Must remove these paths from .gitignore."
                    ),
                    reasoning="State files in .gitignore = Lobotomy. The system is losing its memory.",
                    priority=IntentPriority.CRITICAL,  # Lobotomy is critical!
                    risk=IntentRisk.MEDIUM,  # Modifying .gitignore needs care
                    params={
                        "violations": lobotomy.violations,
                        "affected_plugins": lobotomy.affected_plugins,
                    },
                    auto_executable=False,  # Human should review .gitignore changes
                )
                healing_intents.append(intent)

        except Exception as e:
            logger.warning(f"👁️ PRAKRITI SENSE: Perception failed: {e}")

        return healing_intents

    # NOTE: _execute_healing and _execute_memory_review moved to ActionManager (OPUS-167)

    # =========================================================================
    # 🙏 DHARMA SENSE: THE VEDIC CONSCIENCE (OPUS-009 Extension)
    # OPUS-167: Initialization moved to SenseManager
    # =========================================================================

    def inject_dharma_sense(self, sense: "DharmaSense") -> None:
        """
        Inject the Dharma Sense for ethical alignment checks.

        OPUS-009 Extension: MANAS needs both senses:
        - PRAKRITI SENSE: "What is the state of the world?"
        - DHARMA SENSE: "Is this action righteous?"

        Args:
            sense: DharmaSense instance
        """
        self._sense_manager.inject("dharma_sense", sense)
        # OPUS-167: Also inject into ActionManager for Dharma Gate
        self._action_manager.inject_dharma(sense)
        logger.info("🙏 DHARMA SENSE: Vedic Conscience injected - MANAS now has ethical awareness")

    def _check_dharma_gate(self, intent: Intent) -> tuple:
        """
        Check Dharma Gate before intent execution.

        This is the ethical conscience check. Even if NARASIMHA (technical guardian)
        approves, DHARMA SENSE (ethical conscience) must also approve.

        "An efficient mind without dharma makes efficient catastrophes."

        Args:
            intent: The intent to check

        Returns:
            (is_permitted, reason)
        """
        if not self._dharma_sense:
            # No conscience = permissive (legacy mode)
            return True, "Dharma Sense not available - defaulting to permissive"

        try:
            verdict = self._dharma_sense.check_dharmic_alignment(intent, agent_id="manas")

            if verdict.is_dharmic:
                logger.debug(f"🙏 DHARMA GATE: PASSED - {verdict.reason}")
                return True, verdict.reason
            else:
                logger.warning(
                    f"🙏 DHARMA GATE: BLOCKED - {intent.intent_type} - "
                    f"Missing: {verdict.missing_permissions}, Bhakti: {verdict.agent_bhakti}"
                )
                return False, verdict.reason

        except Exception as e:
            logger.warning(f"🙏 DHARMA GATE: Check failed: {e}")
            # On error, default to permissive (don't block due to bugs)
            return True, f"Dharma check error: {e}"

    def _on_dharma_success(self, intent: Intent) -> None:
        """Record successful dharmic action - increases Bhakti."""
        if self._dharma_sense:
            try:
                self._dharma_sense.on_intent_success(intent)
            except Exception as e:
                logger.debug(f"🙏 DHARMA SENSE: Could not record success: {e}")

    def get_dharma_summary(self) -> Optional[Dict[str, Any]]:
        """Get Dharma summary for OPUS.md display."""
        if not self._dharma_sense:
            return None
        try:
            summary = self._dharma_sense.get_dharma_summary()
            return summary.to_dict()
        except Exception:
            return None

    # =========================================================================
    # 📜 SUTRA SENSE: THE THIRD EYE (OPUS-054)
    # OPUS-167: Initialization moved to SenseManager
    # =========================================================================

    def inject_sutra_sense(self, sense: "SutraSense") -> None:
        """
        Inject the Sutra Sense for doc/code gap detection.

        OPUS-054: MANAS needs three senses:
        - PRAKRITI SENSE: "What is the state of the world?"
        - DHARMA SENSE: "Is this action righteous?"
        - SUTRA SENSE: "What knowledge is missing?"

        Args:
            sense: SutraSense instance
        """
        self._sense_manager.inject("sutra_sense", sense)
        logger.info("📜 SUTRA SENSE: Third Eye injected - MANAS can now perceive documentation gaps")

    # =========================================================================
    # 👂 SHRUTA SENSE: The 6th Jnanendriya - Hearing Filesystem (OPUS-156)
    # OPUS-167: Initialization moved to SenseManager
    # =========================================================================

    # =========================================================================
    # 🫀 PRANA SENSE: The 7th Jnanendriya - Agent Presence (OPUS-166)
    # OPUS-167: Initialization moved to SenseManager
    # =========================================================================

    # NOTE: These helper methods remain in kernel for post-boot setup
    # The SenseManager handles basic initialization, but complex wiring
    # (like Shruta listeners and Prana registration) happens here

    def _setup_sense_listeners(self) -> None:
        """
        Post-boot setup for sense listeners and cross-sense wiring.

        Called after SenseManager.boot_all() to:
        1. Start Shruta filesystem listeners
        2. Register Prana with Shruta for real-time updates
        """
        try:
            # Setup Shruta listeners
            if self._shruta_sense:
                watch_paths = [
                    self._workspace / "vibe_core",
                    self._workspace / "tests",
                    self._workspace / "docs",
                ]
                self._shruta_sense.start_listening(paths=watch_paths)
                self._shruta_sense.register_auto_discovery()
                logger.debug("👂 SHRUTA SENSE: Listeners activated")

            # Wire Prana to Shruta
            if self._prana_sense and self._shruta_sense:
                self._prana_sense.register_with_shruta(self._shruta_sense)
                logger.debug("🫀 PRANA SENSE: Connected to ShrutaSense")

        except Exception as e:
            logger.warning(f"Sense listener setup failed: {e}")

    def _perceive_and_generate_presence_intents(self) -> List[Intent]:
        """
        Use PranaSense to perceive agent presence and generate intents.

        OPUS-166: Reacts to agent lifecycle events:
        - Deaths: Generate investigation intent (why did agent die?)
        - Births: Log acknowledgement (new agent registered)

        Returns:
            List of presence-related intents
        """
        if not self._prana_sense:
            return []

        presence_intents = []

        try:
            # Perceive current presence state
            perception = self._prana_sense.perceive()

            # React to deaths - generate investigation intents (with cooldown)
            now = datetime.utcnow()
            for death in perception.deaths:
                agent_id = death.agent_id

                # OPUS-035 Pattern: Check cooldown to avoid intent spam from flaky agents
                last_intent_time = self._prana_cooldowns.get(agent_id)
                if last_intent_time:
                    elapsed = (now - last_intent_time).total_seconds() / 60
                    if elapsed < self._prana_cooldown_minutes:
                        logger.debug(
                            f"🫀 PRANA SENSE: Skipping {agent_id} death intent - "
                            f"cooldown active ({elapsed:.1f}/{self._prana_cooldown_minutes} min)"
                        )
                        continue

                presence = self._prana_sense.get_agent_presence(agent_id)

                # Mark cooldown BEFORE generating (avoid race conditions)
                self._prana_cooldowns[agent_id] = now

                intent = Intent(
                    id=f"prana_death_{agent_id}_{datetime.utcnow().strftime('%H%M%S')}",
                    intent_type="investigate_agent_death",
                    title=f"Agent {agent_id} died",
                    description=f"Agent '{agent_id}' is no longer responding. "
                    f"Last seen: {presence.last_seen if presence else 'unknown'}. "
                    f"Investigate cause and consider restart.",
                    reasoning="PranaSense detected missing heartbeat (node.json deleted/stale). "
                    "Dead agents may indicate crashes, resource issues, or intentional shutdown.",
                    priority=IntentPriority.HIGH,
                    risk=IntentRisk.MEDIUM,
                    params={
                        "agent_id": agent_id,
                        "last_seen": presence.last_seen if presence else None,
                        "cartridge_path": str(presence.cartridge_path) if presence else None,
                    },
                    auto_executable=False,  # Human should review before restart
                    related_files=[f"agents/{agent_id}/node.json"],
                )
                presence_intents.append(intent)
                logger.info(f"🫀 PRANA SENSE: Agent '{agent_id}' died - investigation intent generated")

            # React to births - log and optionally generate welcome intent
            for birth in perception.births:
                agent_id = birth.agent_id
                logger.info(f"🫀 PRANA SENSE: Agent '{agent_id}' born - now alive")

                # For now, just log. Could generate "integrate_new_agent" intent later
                # if we want MANAS to proactively help new agents

            # Log summary
            if perception.deaths or perception.births:
                logger.info(
                    f"🫀 PRANA SENSE: {len(perception.deaths)} deaths, {len(perception.births)} births detected"
                )

        except Exception as e:
            logger.warning(f"🫀 PRANA SENSE: Perception failed: {e}")

        return presence_intents

    def inject_prana_sense(self, sense: "PranaSense") -> None:
        """
        Inject the Prana Sense for agent presence awareness.

        OPUS-166: PranaSense is the 7th Jnanendriya.

        "Prana is the breath of the universe. When an agent breathes,
         MANAS feels the vibration."

        Args:
            sense: PranaSense instance
        """
        self._prana_sense = sense
        logger.info("🫀 PRANA SENSE: Seventh Jnanendriya injected - MANAS can now perceive agent presence")

    def get_prana_summary(self) -> Optional[Dict[str, Any]]:
        """Get Prana summary for OPUS.md display."""
        if not self._prana_sense:
            return None
        try:
            perception = self._prana_sense.perceive()
            return {
                "total_registered": perception.total_registered,
                "total_alive": perception.total_alive,
                "alive_agents": perception.alive_agents,
                "dead_agents": [a.agent_id for a in perception.agents if not a.is_alive],
            }
        except Exception:
            return None

    # NOTE: _init_infrastructure_genesis removed (OPUS-167: moved to GenesisBridge)

    def inject_shruta_sense(self, sense: "ShrutaSense") -> None:
        """
        Inject the Shruta Sense for filesystem vibration detection.

        OPUS-156: The 6 Jnanendriyas (Perception Organs):
        1. PRAKRITI SENSE: "What is the state of the world?"
        2. DHARMA SENSE: "Is this action righteous?"
        3. SUTRA SENSE: "What knowledge is missing?"
        4. KARMA SENSE: "What has happened before?"
        5. VIVEKA SENSE: "Which action is best?"
        6. SHRUTA SENSE: "What changes are happening?" (NEW!)

        Args:
            sense: ShrutaSense instance
        """
        self._shruta_sense = sense
        logger.info("👂 SHRUTA SENSE: The Hearing System injected - MANAS can now perceive filesystem vibrations")

    def _perceive_filesystem_vibrations(self) -> Optional["ShrutaPerception"]:
        """
        Perceive filesystem vibrations since last check.

        Returns vibrations grouped by type and layer.
        This is called during the think cycle.

        OPUS-158: Also triggers InfrastructureGenesis for new directories.
        """
        if not self._shruta_sense:
            return None

        try:
            perception = self._shruta_sense.perceive()
            if perception.total_count > 0:
                logger.info(
                    f"👂 SHRUTA: Heard {perception.total_count} vibrations - "
                    f"created: {perception.by_type.get('created', 0)}, "
                    f"modified: {perception.by_type.get('modified', 0)}, "
                    f"deleted: {perception.by_type.get('deleted', 0)}"
                )

                # Log hot paths (files changing frequently)
                if perception.hot_paths:
                    top_hot = perception.hot_paths[:3]
                    logger.debug(f"👂 SHRUTA: Hot paths: {top_hot}")

                # OPUS-167: Genesis Bridge handles infrastructure generation
                self._genesis_bridge.process_vibrations(perception)

            return perception
        except Exception as e:
            logger.warning(f"👂 SHRUTA: Error during perception: {e}")
            return None

    # NOTE: _process_genesis_vibrations and _process_genesis_vibrations_legacy removed
    # (OPUS-167: moved to GenesisBridge)

    def get_sutra_summary(self) -> Optional[Dict[str, Any]]:
        """Get Sutra summary for OPUS.md display."""
        if not self._sutra_sense:
            return None
        try:
            summary = self._sutra_sense.perceive_gaps(refresh=False)
            gaps = self._sutra_sense.get_gaps()  # Get actual gap objects
            high_severity_gaps = [g for g in gaps if g.severity in ("high", "critical")]

            return {
                "total_docs": summary.total_docs,
                "docs_with_harness": summary.docs_with_harness,
                "docs_without_harness": summary.docs_without_harness,
                "gaps_count": summary.gaps_found,
                "health_ratio": summary.health_ratio,
                "critical_gaps": len(high_severity_gaps),
                "top_gaps": [
                    {
                        "type": g.gap_type,
                        "doc": g.doc_path.name if g.doc_path else None,
                        "code": g.code_path.name if g.code_path else None,
                        "severity": g.severity,
                        "message": g.description,
                    }
                    for g in gaps[:5]  # Top 5 gaps
                ],
            }
        except Exception as e:
            logger.debug(f"📜 SUTRA SENSE: Could not get summary: {e}")
            return None

    # =========================================================================
    # 🧵 COGNITIVE WEAVER: OPUS-167 Delegation to WeaverBridge
    # =========================================================================

    @property
    def _cognitive_weaver(self) -> Optional["CognitiveWeaver"]:
        """Backward compatibility: delegate to WeaverBridge."""
        return self._weaver_bridge.cognitive_weaver

    def inject_cognitive_weaver(self, weaver: "CognitiveWeaver") -> None:
        """Inject CognitiveWeaver via bridge."""
        self._weaver_bridge.inject_cognitive_weaver(weaver)

    def get_cognitive_context(self, focus: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get unified cognitive context via bridge."""
        return self._weaver_bridge.get_cognitive_context(focus)

    def consult_knowledge(self, action: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Consult knowledge before action via bridge."""
        return self._weaver_bridge.consult_knowledge(action, context)

    def get_cognitive_diagnosis(self) -> Optional[Dict[str, Any]]:
        """Get full system diagnosis via bridge."""
        return self._weaver_bridge.get_cognitive_diagnosis()

    # =========================================================================
    # 🌙 SANKALPA: STRATEGIC WILL (OPUS-089)
    # =========================================================================

    def _init_sankalpa(self) -> None:
        """
        Initialize Sankalpa - the Strategic Will.

        OPUS-089: Sankalpa provides proactive mission planning.
        It evaluates strategies and triggers intents based on:
        - Time (weekly audits, etc.)
        - Idle state (memory review when system is quiet)
        - Conditions (CI green, etc.)
        """
        try:
            from .cortex.sankalpa import SankalpaOrchestrator

            sankalpa_config = self._full_config.get("sankalpa", {})
            self._sankalpa = SankalpaOrchestrator(workspace=self._workspace, config=sankalpa_config)
            logger.info(f"🌙 SANKALPA: Strategic Will initialized (config: {len(sankalpa_config)} keys)")
        except Exception as e:
            logger.warning(f"🌙 SANKALPA: Could not initialize: {e}")
            self._sankalpa = None

    def _generate_sankalpa_intents(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Generate proactive intents from Sankalpa strategies.

        Called during think() to evaluate missions and trigger
        time/idle/condition-based intents.

        Args:
            context: System context

        Returns:
            List of proactive intents from Sankalpa
        """
        if not self._sankalpa:
            return []

        try:
            # Get idle time
            idle_minutes = self.idle_minutes

            # Get pending intent count
            pending_count = len(self._buffer.get_pending())

            # Ask Sankalpa to evaluate strategies
            sankalpa_intents = self._sankalpa.think(
                context=context,
                idle_minutes=idle_minutes,
                pending_intents=pending_count,
            )

            # Convert SankalpaIntents to our Intent format
            intents = []
            for si in sankalpa_intents:
                intent = Intent(
                    id=f"sankalpa_{si.strategy_id}_{datetime.utcnow().strftime('%H%M%S')}",
                    intent_type=si.intent_type,
                    title=si.title,
                    description=si.description,
                    reasoning=f"SANKALPA: {si.mission_name} - {si.strategy_name}",
                    priority=IntentPriority.MEDIUM,
                    risk=IntentRisk.LOW,
                    params=si.params,
                    auto_executable=True,  # Sankalpa intents are pre-approved
                    expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat(),
                    related_docs=["089-SANKALPA-WILL.md"] if si.strategy_id == "strategy_memory_review" else [],
                )
                intents.append(intent)

            if intents:
                self.log_insight(f"🌙 SANKALPA: Generated {len(intents)} proactive intents from strategic planning")

            return intents

        except Exception as e:
            logger.warning(f"🌙 SANKALPA: Strategy evaluation failed: {e}")
            return []

    # =========================================================================
    # 📓 OBSERVATION LOGGER: MANAS THOUGHTS → OPUS.md (OPUS-089)
    # OPUS-167: Implementation moved to LoggerBridge
    # =========================================================================

    def log_insight(self, message: str) -> None:
        """Log an insight to OPUS.md journal (delegates to LoggerBridge)."""
        self._logger_bridge.log_insight(message)

    def log_observation(self, message: str, severity: str = "info") -> None:
        """Log an observation to OPUS.md journal (delegates to LoggerBridge)."""
        self._logger_bridge.log_observation(message, severity=severity)

    def _perceive_and_generate_gap_intents(self) -> List[Intent]:
        """
        Use SutraSense to perceive documentation gaps and generate intents.

        Called during think() to ensure MANAS is aware of documentation
        health and can propose curation actions.

        Returns:
            List of gap intents (if any documentation needs attention)
        """
        if not self._sutra_sense:
            return []

        gap_intents = []

        try:
            # Generate gap intents from SutraSense
            raw_intents = self._sutra_sense.generate_gap_intents(limit=2)

            for idx, raw in enumerate(raw_intents):
                # Extract weaving from params
                params = raw.get("params", {})
                related_files = []
                related_docs = []
                if params.get("code_path"):
                    related_files.append(str(params["code_path"]))
                if params.get("doc_path"):
                    doc_name = Path(params["doc_path"]).name
                    related_docs.append(doc_name)

                # Generate unique ID with timestamp + counter to avoid duplicates
                intent = Intent(
                    id=raw.get("id", f"gap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{idx:02d}"),
                    intent_type=raw.get("intent_type", "doc_modify"),
                    title=raw.get("title", "Documentation gap detected"),
                    description=raw.get("description", ""),
                    reasoning=raw.get("reasoning", "SUTRA SENSE detected documentation gap"),
                    priority=IntentPriority(raw.get("priority", "medium")),
                    risk=IntentRisk(raw.get("risk", "low")),
                    params=params,
                    auto_executable=raw.get("auto_executable", False),
                    # Gap intents expire after 24h - if not addressed, re-perceive fresh
                    expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat(),
                    # WEAVING: Link code + doc from gap
                    related_files=related_files,
                    related_docs=related_docs,
                )
                gap_intents.append(intent)

            if gap_intents:
                logger.info(f"📜 SUTRA SENSE: Generated {len(gap_intents)} documentation gap intents")

        except Exception as e:
            logger.warning(f"📜 SUTRA SENSE: Gap perception failed: {e}")

        return gap_intents

    def _record_intent_for_clustering(self, intent: Intent) -> None:
        """
        Record intent to SutraSense for pattern detection.

        OPUS-054 Phase 2: When MANAS generates intents repeatedly for
        similar topics, this indicates a need for structured documentation.

        Args:
            intent: The intent to record
        """
        if not self._sutra_sense:
            return

        try:
            # Extract topic from intent type or params
            topic = self._extract_topic_from_intent(intent)
            if topic:
                self._sutra_sense.record_intent(
                    intent_type=intent.intent_type,
                    topic=topic,
                    title=intent.title,
                )
        except Exception as e:
            logger.debug(f"📜 SUTRA SENSE: Could not record intent: {e}")

    def _extract_topic_from_intent(self, intent: Intent) -> Optional[str]:
        """
        Extract topic category from an intent.

        Maps intent types and content to topic categories for clustering.
        """
        # Map common intent types to topics
        type_to_topic = {
            "doc_modify": "documentation",
            "code_modify": "codebase",
            "test_create": "testing",
            "git_commit": "version_control",
            "state_heal": "state_management",
            "heal_system_state": "state_management",
            "fix_lobotomy": "state_management",
            "sutra_missing_harness": "documentation",
            "sutra_missing_doc": "documentation",
            "sutra_stale_doc": "documentation",
        }

        # Check direct mapping first
        if intent.intent_type in type_to_topic:
            return type_to_topic[intent.intent_type]

        # Extract from intent type prefix
        if intent.intent_type.startswith("sutra_"):
            return "documentation"
        if intent.intent_type.startswith("roadmap_"):
            return "roadmap"
        if "dharma" in intent.intent_type.lower():
            return "vedic_governance"
        if "state" in intent.intent_type.lower():
            return "state_management"

        # Extract from params if available
        if intent.params:
            if "gap_type" in intent.params:
                return "documentation"
            if "module" in intent.params:
                return intent.params["module"]

        # Default to intent type as topic
        return intent.intent_type.replace("_", " ").split()[0] if "_" in intent.intent_type else None

    def _record_to_ledger(
        self,
        event_type: str,
        intent: Intent,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Record an intent event to the core ledger.

        OPUS-057 VAJRA: Cryptographic binding of all MANAS actions.
        OPUS-074 WIRING: Supports standalone ledger for headless mode.

        Args:
            event_type: Type of event (INTENT_PROPOSED, INTENT_EXECUTED, etc.)
            intent: The intent being recorded
            extra_data: Additional data to include

        Returns:
            Event ID if recorded, None if no ledger available
        """
        # OPUS-074: Prioritize standalone ledger, fallback to kernel.ledger
        ledger = getattr(self, "_ledger", None)
        if not ledger and self._vibe_kernel:
            ledger = self._vibe_kernel.ledger

        if not ledger:
            logger.debug("⚠️ VAJRA: No ledger - intent not ledgered (shadow mode)")
            return None

        # Build intent hash for integrity
        intent_data = {
            "id": intent.id,
            "type": intent.intent_type,
            "title": intent.title,
            "risk": intent.risk.value,
            "priority": intent.priority.value,
            "params": intent.params,
        }
        intent_hash = hashlib.sha256(json.dumps(intent_data, sort_keys=True).encode()).hexdigest()[:16]

        details = {
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "intent_title": intent.title,
            "intent_risk": intent.risk.value,
            "intent_priority": intent.priority.value,
            "intent_hash": intent_hash,
            **(extra_data or {}),
        }

        try:
            event_id = ledger.record_event(
                event_type=event_type,
                agent_id="manas",
                details=details,
            )
            logger.debug(f"⚡ VAJRA: {event_type} recorded → {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"⚡ VAJRA: Failed to record {event_type}: {e}")
            return None

    # =========================================================================
    # OPUS-095: OODA PHASE METHODS (Abstract from orchestrate())
    # =========================================================================

    async def _perceive(self) -> Tuple[List[Any], Dict[str, Any]]:
        """
        PERCEIVE Phase: Collect system state observations.

        OPUS-167: Fractal Architecture - Each sense generates its own intents.

        The 7 Jnanendriyas (Perception Organs):
        1. PRAKRITI SENSE → System state healing
        2. DHARMA SENSE → Ethical alignment (used in decide phase)
        3. SUTRA SENSE → Documentation gaps
        4. KARMA SENSE → Memory traces
        5. VIVEKA SENSE → Discriminative ranking
        6. SHRUTA SENSE → Filesystem vibrations
        7. PRANA SENSE → Agent presence

        Returns:
            (observations, metadata) where observations is list of intents discovered
        """
        metadata = {}

        # 👂 SHRUTA SENSE: Perceive filesystem vibrations FIRST
        # "Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
        shruta_perception = self._perceive_filesystem_vibrations()
        metadata["vibration_count"] = shruta_perception.total_count if shruta_perception else 0

        # OPUS-168: Senses feed CHITTA (not kernel directly)
        # This enables aggregation and deduplication before Buddhi discriminates

        # 👁️ PRAKRITI SENSE: Feed healing intents to Chitta
        if self._prakriti_sense:
            try:
                healing_intents = self._prakriti_sense.generate_intents()
                for intent in healing_intents:
                    self._chitta.receive(intent, "prakriti_sense")
                metadata["healing_count"] = len(healing_intents)
            except Exception as e:
                logger.warning(f"👁️ PRAKRITI SENSE: Intent generation failed: {e}")
                metadata["healing_count"] = 0

        # 🫀 PRANA SENSE: Feed presence intents to Chitta
        if self._prana_sense:
            try:
                context = {"_prana_cooldowns": self._prana_cooldowns}
                presence_intents = self._prana_sense.generate_intents(context)
                for intent in presence_intents:
                    self._chitta.receive(intent, "prana_sense")
                metadata["presence_count"] = len(presence_intents)
            except Exception as e:
                logger.warning(f"🫀 PRANA SENSE: Intent generation failed: {e}")
                metadata["presence_count"] = 0

        # 📜 SUTRA SENSE: Feed documentation gap intents to Chitta
        if self._sutra_sense:
            try:
                gap_intents = self._sutra_sense.generate_intents()
                for intent in gap_intents:
                    self._chitta.receive(intent, "sutra_sense")
                metadata["gap_count"] = len(gap_intents)
            except Exception as e:
                logger.warning(f"📜 SUTRA SENSE: Intent generation failed: {e}")
                metadata["gap_count"] = 0

        # 🔮 KARMA SENSE: Feed chronic pain intents to Chitta
        if self._karma_sense:
            try:
                karma_intents = self._karma_sense.generate_intents()
                for intent in karma_intents:
                    self._chitta.receive(intent, "karma_sense")
                metadata["karma_count"] = len(karma_intents)
            except Exception as e:
                logger.warning(f"🔮 KARMA SENSE: Intent generation failed: {e}")
                metadata["karma_count"] = 0

        # 🔍 VIVEKA SENSE: Feed prioritized coverage gap intents to Chitta
        if self._viveka_sense:
            try:
                viveka_intents = self._viveka_sense.generate_intents()
                for intent in viveka_intents:
                    self._chitta.receive(intent, "viveka_sense")
                metadata["viveka_count"] = len(viveka_intents)
            except Exception as e:
                logger.warning(f"🔍 VIVEKA SENSE: Intent generation failed: {e}")
                metadata["viveka_count"] = 0

        # 🌙 SANKALPA: Strategic proactive intents (still kernel-level for now)
        sankalpa_intents = self._generate_sankalpa_intents({})
        for intent in sankalpa_intents:
            self._chitta.receive(intent, "sankalpa")  # Sankalpa = subtle/strategic
        metadata["sankalpa_count"] = len(sankalpa_intents)

        # Clean up expired intents
        self._cleanup_expired_intents()

        # OPUS-168: Return Chitta pool state (not intents yet - Chitta processes in _orient)
        metadata["chitta_pool_size"] = self._chitta.pool_size
        return [], metadata  # Empty list - Chitta holds the perceptions

    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        ORIENT Phase: Process Chitta and organize perceptions.

        OPUS-168: Chitta processes raw sense data (aggregation, deduplication).
        IntentGenerator also runs analyzers that may add more intents.

        Args:
            observations: (Ignored in OPUS-168 - Chitta holds perceptions)

        Returns:
            (perceptions, metadata) where perceptions is processed PerceptionEntry list
        """
        # 🕉️ SHIVA: Sweep stale intents (destroy illusions)
        swept = self._shiva.sweep_stale_intents()
        if swept > 0:
            logger.info(f"🕉️ SHIVA: Swept {swept} fulfilled intents")

        # OPUS-168: Process Chitta (aggregation, deduplication)
        processed_perceptions = self._chitta.process()

        # Also run IntentGenerator analyzers (TriageAnalyzer uses VivekaSense/KarmaSense)
        # These add to the perception pool via Chitta
        context = {
            "observations": [p.intent for p in processed_perceptions],
            "observation_count": len(processed_perceptions),
            "observation_types": list(set(p.intent_type for p in processed_perceptions)),
        }

        # OPUS-096: Async generation for Semantic Engine
        new_intents = await self._intent_generator.generate_intents(context)

        # Feed analyzer intents to Chitta and reprocess
        for intent in new_intents:
            self._chitta.receive(intent, "intent_generator")

        # Final processing if we added new intents
        if new_intents:
            processed_perceptions = self._chitta.process()

        metadata = {
            "chitta_processed": len(processed_perceptions),
            "analyzer_generated": len(new_intents),
            "swept_count": swept,
        }

        return processed_perceptions, metadata

    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        DECIDE Phase: Buddhi discriminates which intents to execute.

        OPUS-168: This is THE KEY FIX. Buddhi uses:
        - VivekaSense logic for priority scoring
        - DharmaSense for ethical filtering (BEFORE execution!)
        - Resource and dependency checks

        Args:
            orientations: Processed PerceptionEntry list from orient phase

        Returns:
            (decisions, metadata) where decisions is approved Intent list
        """
        # OPUS-168: Buddhi does the real decision making
        # DharmaSense is checked HERE, not at execution time!
        verdicts = self._buddhi.discriminate(
            perceptions=orientations,
            max_intents=self._config.max_intents_per_tick,
        )

        # Extract approved intents from verdicts
        decisions = [v.intent for v in verdicts]

        # OPUS-035: Prioritize survival over growth (still applies to approved intents)
        if self._config.survival_first and len(decisions) > self._config.max_intents_per_tick:
            decisions = self._prioritize_survival(decisions)

        metadata = {
            "considered": len(orientations),
            "approved": len(verdicts),
            "blocked": len(orientations) - len(verdicts),
            "buddhi_stats": self._buddhi.stats,
        }

        return decisions, metadata

    async def _act(self, decisions: List[Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        ACT Phase: Execute decided intents.

        Args:
            decisions: List of intents to execute from decide phase

        Returns:
            (results, metadata) where results is execution summary dict
        """
        added = []

        for intent in decisions:
            if not self._is_intent_duplicate(intent):
                entry = IntentBufferEntry(intent=intent)

                # 🦁 NARASIMHA JUDGMENT: Judge before buffering
                verdict = self._narasimha.judge_intent(intent)
                if verdict.status == "GUILTY":
                    logger.critical(f"🦁 NARASIMHA BLOCKED INTENT: {intent.title}")
                    entry.status = "blocked"
                    entry.execution_result = {
                        "error": f"BLOCKED BY NARASIMHA: {verdict.reason}",
                        "verdict": str(verdict),
                    }

                self._buffer.add(entry)
                added.append(intent)

                # 📜 SUTRA SENSE: Record intent for clustering
                self._record_intent_for_clustering(intent)

                # ⚡ VAJRA: Record intent proposal to ledger
                self._record_to_ledger(
                    event_type="MANAS_INTENT_PROPOSED",
                    intent=intent,
                    extra_data={
                        "proposed_at": datetime.utcnow().isoformat(),
                        "auto_executable": intent.auto_executable,
                    },
                )

                # Auto-execute if safe OR if karma gate allows
                # OPUS-211: Simplified - if risk == SAFE and config allows, just do it!
                # The redundant auto_executable flag was blocking legitimate SAFE intents
                is_safe = self._config.auto_execute_safe and intent.risk == IntentRisk.SAFE
                is_trusted = self._karma_allows_auto_execute(intent)

                if is_safe or is_trusted:
                    reason = "SAFE" if is_safe else "KARMA GATE"
                    logger.info(f"🙏 MANAS: Auto-executing [{reason}]: {intent.title}")
                    self._execute_intent(entry)

        results = {
            "added_count": len(added),
            "added_intents": [i.title for i in added],
        }

        metadata = {
            "execution_phase": "act",
            "intents_processed": len(decisions),
        }

        return results, metadata

    async def _persist(self, context: "CycleContext") -> Dict[str, str]:
        """
        PERSIST Phase: Save state to disk.

        Called after all phases complete to ensure durability.

        Args:
            context: CycleContext from orchestration cycle

        Returns:
            Dict of persist errors (empty if success)
        """
        # OPUS-167: IntentBuffer handles size limit and persistence automatically
        self._buffer.save()
        logger.debug("💾 MANAS: Persisted intent buffer")

        # OPUS-096: Weaver integration - commit runtime state after MANAS cycle
        # The Weaver discovers dirty files via git status (independent of StateService)
        # This ensures files written during MANAS cycle get committed
        self._weaver_pulse()

        # Return empty dict (no errors)
        return {}

    # =========================================================================
    # RE-ENTRANCY GUARD (OPUS-088: Mirror Test)
    # =========================================================================

    def _is_self_triggered_change(self) -> bool:
        """
        🪞 Mirror Test: Erkenne, ob wir in den Spiegel schauen.

        Prüft, ob der letzte Commit von MANAS selbst stammt.
        Verhindert Resonanzkatastrophe (infinite feedback loop):
            MANAS commits → Git change → MANAS wakes → MANAS commits → ...

        Returns:
            True if last commit was made by MANAS (should skip thinking)
        """
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%s"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self._workspace),
            )
            if result.returncode != 0:
                return False

            last_commit_msg = result.stdout.strip()

            # Erkennt Standard-Signaturen von MANAS
            is_self = (
                last_commit_msg.startswith("chore(manas):")
                or last_commit_msg.startswith("fix(manas):")
                or "Generated by MANAS" in last_commit_msg
            )

            if is_self:
                logger.info("🪞 Mirror Test: Ignoring self-triggered change event")

            return is_self
        except Exception as e:
            logger.warning(f"🪞 Mirror Test: Could not check git history: {e}")
            return False

    # =========================================================================
    # CORE API
    # =========================================================================

    def tick(self) -> Dict[str, Any]:
        """
        MANAS Biorhythm tick - delegated to BiorhythmProcessor (OPUS-176).

        Returns:
            Dict with state, consciousness_level, and should_think
        """
        return self._biorhythm.tick()

    def get_awareness(self) -> Dict[str, Any]:
        """Get current awareness state (for dashboard/templates)."""
        return self._biorhythm.get_awareness()

    def _is_intent_expired(self, intent: Intent) -> bool:
        """Check if intent has expired based on config."""
        if not intent.created_at:
            return False
        expiry = timedelta(hours=self._config.intent_expiry_hours)
        return datetime.utcnow() - intent.created_at > expiry

    def think(self, context: Optional[Dict[str, Any]] = None, force: bool = False) -> List[Intent]:
        """Thin wrapper: Execute thought cycle via CognitiveCycle.orchestrate()."""
        if not force and not self._should_think():
            return []
        if (context or {}).get("trigger") in ("git_change", "file_change") and self._is_self_triggered_change():
            logger.info("🪞 MANAS: Chill. Das warst du selbst.")
            return []
        self._last_thought_time = datetime.utcnow()
        try:
            # OPUS-097: Use get_event_loop() pattern instead of asyncio.run()
            # asyncio.run() fails when called from already running event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            ctx = loop.run_until_complete(self.orchestrate(force=True))
            if ctx and ctx.results:
                added = ctx.results.get("added_intents", [])
                if added:
                    logger.info(f"MANAS: Generated {len(added)} new intents")

                # GURUKULA: Check if MANAS wants to train
                dojo_intent = self._check_training_desire()
                if dojo_intent:
                    added.append(dojo_intent)
                    logger.info("🥋 MANAS: Curiosity triggered - adding enter_dojo intent")

                return added
        except Exception as e:
            logger.error(f"MANAS: Error in orchestrate(): {e}")
        return []

    def _check_training_desire(self) -> Optional["Intent"]:
        """
        GURUKULA: Check if MANAS is curious enough to self-train.

        Returns enter_dojo Intent if curiosity threshold is met.
        """
        try:
            from vibe_core.plugins.opus_assistant.manas.dojo.agency import DojoAgency

            agency = DojoAgency(self._workspace)
            intent_dict = agency.check_training_desire()

            if intent_dict:
                from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

                return Intent(
                    intent_type="enter_dojo",
                    title="🥋 Self-directed Dojo training",
                    description="MANAS curiosity threshold reached - initiating training",
                    priority="low",  # Training is background activity
                    risk="safe",
                    reasoning=f"Curiosity sources: {intent_dict['params'].get('top_sources', [])}",
                    params=intent_dict["params"],
                )
        except ImportError:
            pass  # Dojo not available
        except Exception as e:
            logger.debug(f"MANAS: Training desire check failed: {e}")

        return None

    def approve_intent(self, intent_id: str) -> bool:
        """
        Approve an intent for execution.

        OPUS-057 VAJRA: Approvals are recorded to the ledger.

        Args:
            intent_id: ID of the intent to approve

        Returns:
            True if approved and executed successfully
        """
        entry = self._find_intent_entry(intent_id)
        if not entry:
            logger.warning(f"Intent {intent_id} not found")
            return False

        if entry.status != "pending":
            logger.warning(f"Intent {intent_id} is not pending (status: {entry.status})")
            return False

        entry.status = "approved"

        # 🔌 CABLE: Reset idle timer on user interaction
        self.record_activity()

        # ⚡ VAJRA: Record approval to ledger
        self._record_to_ledger(
            event_type="MANAS_INTENT_APPROVED",
            intent=entry.intent,
            extra_data={"approved_at": datetime.utcnow().isoformat()},
        )

        # 🦁 NARASIMHA JUDGMENT: Final check before execution
        # Even if human approved, we double check (e.g. if context changed)
        verdict = self._narasimha.judge_intent(entry.intent)
        if verdict.status == "GUILTY":
            logger.critical(f"🦁 NARASIMHA BLOCKED EXECUTION: {entry.intent.title}")
            entry.status = "blocked"
            entry.execution_result = {"error": f"BLOCKED BY NARASIMHA: {verdict.reason}"}
            return False

        return self._execute_intent(entry)

    def reject_intent(self, intent_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject an intent.

        OPUS-057 VAJRA: Rejections are recorded to the ledger.

        Args:
            intent_id: ID of the intent to reject
            reason: Optional reason for rejection

        Returns:
            True if rejected successfully
        """
        entry = self._find_intent_entry(intent_id)
        if not entry:
            logger.warning(f"Intent {intent_id} not found")
            return False

        entry.status = "rejected"

        # 🔌 CABLE: Reset idle timer on user interaction
        self.record_activity()

        # ⚡ VAJRA: Record rejection to ledger
        self._record_to_ledger(
            event_type="MANAS_INTENT_REJECTED",
            intent=entry.intent,
            extra_data={
                "rejected_at": datetime.utcnow().isoformat(),
                "reason": reason,
            },
        )

        # Record in memory (so we don't suggest it again soon)
        self._memory.record_intent_outcome(
            intent_type=entry.intent.intent_type,
            description=entry.intent.title,
            outcome="rejected",
            feedback=reason,
        )

        self._buffer.save()
        logger.info(f"Intent {intent_id} rejected: {reason or 'no reason given'}")
        return True

    def get_pending_intents(self) -> List[Intent]:
        """Get all pending intents (for OPUS.md display)."""
        return self._buffer.get_pending()

    def get_intent_buffer(self) -> List[IntentBufferEntry]:
        """Get the full intent buffer."""
        return self._buffer.get_all()

    def set_execution_callback(self, callback: Callable[[Intent], Dict[str, Any]]) -> None:
        """
        Set the callback for intent execution.

        Args:
            callback: Function that takes an Intent and returns execution result
        """
        self._execution_callback = callback

    def record_activity(self) -> None:
        """Record that system activity occurred (resets idle timer)."""
        self._last_activity_time = datetime.utcnow()

    def get_idle_minutes(self) -> int:
        """Get minutes since last activity."""
        delta = datetime.utcnow() - self._last_activity_time
        return int(delta.total_seconds() / 60)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of MANAS memory for display."""
        memories = self._memory.get_all_memories()
        successful_patterns = self._memory.get_successful_patterns(limit=5)

        # Count by outcome
        outcomes = {"success": 0, "failed": 0, "rejected": 0, "pending": 0}
        for m in memories:
            if m.outcome in outcomes:
                outcomes[m.outcome] += 1

        return {
            "total_memories": len(memories),
            "outcomes": outcomes,
            "successful_patterns": successful_patterns,
            "retention_days": self._memory.MEMORY_RETENTION_DAYS,
        }

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _should_think(self) -> bool:
        """
        Check if MANAS should think.

        OPUS-174: MANAS IS AN ORACLE - not binary 0/1 polling!

        Decision factors (in order):
        1. Biorhythm State (Turiya/Sattva) → Think (consciousness driven)
        2. High synaptic activation → Think (learned urgency)
        3. Idle threshold passed → Think (user waiting)
        4. First thought → Think
        5. Interval passed → Think (background maintenance)
        """
        now = datetime.utcnow()

        # OPUS-174: Check Biorhythm State (Consciousness Driven)
        # If we are in Turiya (Deep Think), we SHOULD think.
        # If we are in Sattva (Reflect) and it's time to organize, we should think.
        # This breaks the "legacy polling" behavior.
        if self._biorhythm:
            state = self._biorhythm.consciousness_state
            if state == "turiya":
                logger.info("🧠 MANAS: Turiya state (Deep Think) → thinking now!")
                return True
            # In Sattva, we think more often (e.g. every 5 min vs 15 min)
            if state == "sattva":
                minutes_since = (now - self._last_thought_time).total_seconds() / 60 if self._last_thought_time else 999
                if minutes_since >= 5:  # Faster reflection cycle
                    logger.debug("🧠 MANAS: Sattva state (Reflect) → thinking now!")
                    return True

        # OPUS-174: Check synaptic activation (MANAS as oracle)
        # High-weight active triggers = learned urgency
        synaptic_urgency = self._get_synaptic_urgency()
        if synaptic_urgency >= 0.8:
            logger.info(f"🧠 MANAS: High synaptic activation ({synaptic_urgency:.2f}) → thinking now!")
            return True

        # Check idle threshold
        idle_minutes = self.get_idle_minutes()
        if idle_minutes >= self._config.idle_threshold_minutes:
            logger.debug(f"MANAS: Idle for {idle_minutes} min, should think")
            return True

        # Check time since last thought
        if self._last_thought_time is None:
            return True  # First thought

        minutes_since_thought = (now - self._last_thought_time).total_seconds() / 60

        # OPUS-174: Scale interval by synaptic urgency
        # High urgency = shorter interval, low urgency = longer interval
        effective_interval = self._config.thinking_interval_minutes
        if synaptic_urgency >= 0.5:
            # Medium urgency = think sooner (half interval)
            effective_interval = effective_interval / 2
            logger.debug(f"MANAS: Medium synaptic urgency ({synaptic_urgency:.2f}), interval halved")

        if minutes_since_thought >= effective_interval:
            return True

        return False

    def _get_synaptic_urgency(self) -> float:
        """
        OPUS-174: Query synaptic memory for current urgency level.

        Checks active triggers in the system and returns max weight
        of any learned associations. High weights = learned urgency.

        Returns:
            Urgency score 0.0 - 1.0 based on synaptic activation
        """
        try:
            # Get active triggers from recent events
            active_triggers = self._get_active_triggers()

            if not active_triggers:
                return 0.0

            # Consult synaptic memory for each trigger
            max_weight = 0.0
            for trigger in active_triggers:
                recommendations = self._synaptic_memory.consult(trigger, min_weight=0.5)
                if recommendations:
                    top_weight = recommendations[0].weight
                    if top_weight > max_weight:
                        max_weight = top_weight

            return max_weight

        except Exception as e:
            logger.debug(f"Synaptic urgency check failed: {e}")
            return 0.0

    def _get_active_triggers(self) -> List[str]:
        """
        Get currently active triggers in the system.

        Checks recent events from EventBus or pending intents to
        determine what triggers are "firing" right now.
        """
        triggers = []

        # Check pending intents for triggers
        try:
            from .triggers import normalize_trigger

            for entry in self._buffer.get_all():
                if entry.status == "pending":
                    trigger = normalize_trigger(entry.intent)
                    if trigger:
                        triggers.append(trigger.value)
        except Exception:
            pass

        # Check recent observations
        try:
            if hasattr(self, "_last_observations"):
                for obs in getattr(self, "_last_observations", [])[-10:]:
                    if hasattr(obs, "trigger"):
                        triggers.append(obs.trigger)
        except Exception:
            pass

        return list(set(triggers))  # Deduplicate

    def _prioritize_survival(self, intents: List[Intent]) -> List[Intent]:
        """
        OPUS-035 + OPUS-112: Prioritize by survival, then by experience.

        Sort intents by:
        1. Priority (CRITICAL > HIGH > MEDIUM > LOW)
        2. Repair vs Genesis (repairs first)
        3. OPUS-112: Synaptic confidence (learned experience)

        Philosophy: First survive, then thrive, then trust experience.

        Args:
            intents: List of intents to prioritize

        Returns:
            Sorted list with survival intents first, boosted by learned weights
        """
        # Define priority order: CRITICAL > HIGH > MEDIUM > LOW
        priority_order = {
            IntentPriority.CRITICAL: 0,
            IntentPriority.HIGH: 1,
            IntentPriority.MEDIUM: 2,
            IntentPriority.LOW: 3,
        }

        # OPUS-112: Get synaptic confidence for each intent
        def get_synaptic_boost(intent: Intent) -> float:
            """Get confidence boost from learned experience (0.0 - 1.0)."""
            try:
                return self._synaptic_memory.get_confidence(intent)
            except Exception:
                return 0.5  # Neutral if memory unavailable

        # Sort by: priority, repair status, synaptic confidence (inverted), created_at
        def sort_key(intent: Intent) -> tuple:
            """sort_key - TODO: Add description.

            Args:
                intent: Description needed
            """
            pri = priority_order.get(intent.priority, 99)
            # Contract intents (repairs) come before semantic (genesis)
            is_repair = 0 if intent.intent_type.startswith("contract_") else 1
            # OPUS-112: Higher synaptic confidence = lower sort value (comes first)
            # We invert because lower values sort first
            synaptic_boost = 1.0 - get_synaptic_boost(intent)
            return (pri, is_repair, synaptic_boost, intent.created_at)

        return sorted(intents, key=sort_key)

    def consult_synapses(self, trigger: str) -> List[Dict[str, Any]]:
        """
        OPUS-112: Consult synaptic memory for recommended actions.

        Public API for querying learned experience.

        Args:
            trigger: Canonical trigger string (e.g., "trigger:test_failure")

        Returns:
            List of dicts with action recommendations, sorted by weight
        """
        recommendations = self._synaptic_memory.consult(trigger)
        return [
            {
                "action": rec.action,
                "weight": rec.weight,
                "confidence": rec.confidence_level,
                "trigger": rec.trigger,
            }
            for rec in recommendations
        ]

    def get_synaptic_confidence(self, intent: Intent) -> float:
        """
        OPUS-112: Get learned confidence for an intent.

        Args:
            intent: The intent to check

        Returns:
            Confidence score (0.0 - 1.0), 0.5 if no experience
        """
        return self._synaptic_memory.get_confidence(intent)

    def _karma_allows_auto_execute(self, intent: Intent) -> bool:
        """
        🙏 KARMA GATE: High karma earns trust for autonomous execution.

        Bhakti (devotion) + consistent success → earned autonomy.
        The system must PROVE itself worthy of self-governance.
        """
        if intent.risk not in (IntentRisk.LOW, IntentRisk.SAFE):
            return False  # Only LOW/SAFE can be karma-gated

        # Get karma from StateManager (where Bhakti circuit stores it)
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager(self._workspace)
            last_karma = state_mgr.get_last_karma()
        except Exception:
            return False

        if not last_karma:
            return False

        threshold = self._config.karma_auto_execute_threshold
        if last_karma.score >= threshold:
            logger.debug(f"🙏 KARMA GATE: {last_karma.score} >= {threshold}, trust granted")
            return True

        return False

    def _is_intent_duplicate(self, intent: Intent) -> bool:
        """
        Check if similar intent already exists in buffer.

        OPUS-127: Allow multiple intents of same type if title differs.
        OPUS-167: Delegates to IntentBuffer.is_duplicate()
        """
        return self._buffer.is_duplicate(intent)

    def _find_intent_entry(self, intent_id: str) -> Optional[IntentBufferEntry]:
        """Find intent entry by ID."""
        return self._buffer.find(intent_id)

    def _execute_intent(self, entry: IntentBufferEntry) -> bool:
        """
        OPUS-167: Delegate intent execution to ActionManager (Karmendriya).

        The kernel decides WHAT to do (Manas), the ActionManager does it (Karmendriya).
        """
        # Get ledger from vibe_kernel
        ledger = getattr(self, "_ledger", None)
        if not ledger and self._vibe_kernel:
            ledger = self._vibe_kernel.ledger

        return self._action_manager.execute(
            entry=entry,
            ledger=ledger,
            vibe_kernel=self._vibe_kernel,
            buffer=self._buffer,
            activity_callback=self.record_activity,
        )

    # NOTE: OPUS-110 Synaptic Learning (_update_synapses, _extract_trigger) moved to ActionManager (OPUS-167)

    def _cleanup_expired_intents(self) -> None:
        """Remove expired intents from buffer."""
        # OPUS-167: Delegates to IntentBuffer.cleanup_expired()
        expired = self._buffer.cleanup_expired()
        if expired > 0:
            logger.debug(f"MANAS: Cleaned up {expired} expired intents")

    # =========================================================================
    # PERSISTENCE (OPUS-167: Buffer persistence moved to IntentBuffer)
    # =========================================================================

    def _weaver_pulse(self) -> None:
        """OPUS-167: Delegate to WeaverBridge for state sync."""
        self._weaver_bridge.weaver_pulse()

    # =========================================================================
    # INTEGRATION POINTS
    # =========================================================================

    def get_intent_buffer_for_opus(self) -> Dict[str, Any]:
        """
        Get intent buffer formatted for OPUS.md display.

        Returns data ready to be rendered in the Intent Buffer section.
        """
        all_entries = self._buffer.get_all()
        pending = [entry for entry in all_entries if entry.status == "pending"]
        executed = [entry for entry in all_entries if entry.status == "executed"][-5:]  # Last 5

        return {
            "pending": [
                {
                    "id": entry.intent.id,
                    "title": entry.intent.title,
                    "description": entry.intent.description,
                    "priority": entry.intent.priority.value,
                    "risk": entry.intent.risk.value,
                    "reasoning": entry.intent.reasoning,
                    "auto_executable": entry.intent.auto_executable,
                }
                for entry in pending
            ],
            "recent_executed": [
                {
                    "id": entry.intent.id,
                    "title": entry.intent.title,
                    "status": entry.status,
                    "executed_at": entry.executed_at,
                    "success": entry.execution_result.get("success", False) if entry.execution_result else False,
                }
                for entry in executed
            ],
            "total_pending": len(pending),
            "idle_minutes": self.get_idle_minutes(),
            "last_thought": self._last_thought_time.isoformat() if self._last_thought_time else None,
        }
