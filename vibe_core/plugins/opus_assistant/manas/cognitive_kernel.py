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
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from vibe_core.event_bus import EventBus
from vibe_core.loaders import ActionLoader, AnalyzerLoader, SenseLoader, ToolLoader
from vibe_core.orchestration_cycle import CognitiveCycle, CycleContext
from vibe_core.runtime.unified_trace import UnifiedTrace
from vibe_core.state import get_state_service  # P0: StateService

from .intent_generator import Intent, IntentGenerator, IntentPriority, IntentRisk
from .memory_store import MemoryStore
from .shiva import ShivaLifecycleManager  # OPUS-082: Destroyer of Illusions

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.state.cognitive_weaver import CognitiveWeaver
    from vibe_core.tools.tool_registry import ToolRegistry

    from .cortex.dharma_sense import DharmaSense, DharmaSummary
    from .cortex.genesis import InfrastructureClassifier, InfrastructureGenerator, ModuleType
    from .cortex.prakriti_sense import GunaSummary, PrakritiSense
    from .cortex.prana_sense import PranaPerception, PranaSense
    from .cortex.shruta_sense import ShrutaPerception, ShrutaSense
    from .cortex.sutra_sense import SutraSense, SutraSummary

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
        thinking_interval_minutes: int = 60  # Once per hour by default

        # Idle threshold (activate MANAS after this much idle time)
        idle_threshold_minutes: int = 30

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


@dataclass
class IntentBufferEntry:
    """An entry in the intent buffer (for OPUS.md display)."""

    intent: Intent
    status: str = "pending"  # pending, approved, rejected, executed, expired
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    executed_at: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None


class CognitiveKernel(CognitiveCycle):
    """
    The Mind of OPUS - Proactive Autonomous Cognition.

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
    """

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

        self._intent_generator = IntentGenerator(workspace=self._workspace, memory_store=self._memory)
        # Inject engine if available
        if self._semantic_engine:
            self._intent_generator.inject_semantic_engine(self._semantic_engine)

        # Intent buffer (persisted to .opus_state/manas_intents.json)
        self._intent_buffer: List[IntentBufferEntry] = []
        self._load_intent_buffer()

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

        # 👁️ PRAKRITI SENSE: The Sixth Jnanendriya (OPUS-009)
        self._prakriti_sense: Optional["PrakritiSense"] = None
        self._init_prakriti_sense()

        # 🙏 DHARMA SENSE: The Vedic Conscience (OPUS-009 Extension)
        self._dharma_sense: Optional["DharmaSense"] = None
        self._init_dharma_sense()

        # 📜 SUTRA SENSE: The Third Eye - Doc/Code Gap Detection (OPUS-054)
        self._sutra_sense: Optional["SutraSense"] = None
        self._init_sutra_sense()
        # Inject engine if available
        if self._sutra_sense and self._semantic_engine:
            self._sutra_sense.inject_semantic_engine(self._semantic_engine)

        # 👂 SHRUTA SENSE: The 6th Jnanendriya - Hearing Filesystem (OPUS-156)
        # "Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
        self._shruta_sense: Optional["ShrutaSense"] = None
        self._init_shruta_sense()

        # 🫀 PRANA SENSE: The 7th Jnanendriya - Agent Presence Awareness (OPUS-166)
        # "Prana is the breath of the universe. When an agent breathes, it leaves a trace."
        self._prana_sense: Optional["PranaSense"] = None
        self._init_prana_sense()

        # 🏛️ INFRASTRUCTURE GENESIS: The Stadtamt Service (OPUS-158)
        # Auto-generates GAD-000 compliant infrastructure for new modules
        # "Jedes Haus bekommt einen Briefkasten. Jede Straße ein Schild."
        self._infrastructure_classifier: Optional["InfrastructureClassifier"] = None
        self._infrastructure_generator: Optional["InfrastructureGenerator"] = None
        self._init_infrastructure_genesis()

        # 🧵 COGNITIVE WEAVER: State ↔ Knowledge Bridge (OPUS-106)
        self._cognitive_weaver: Optional["CognitiveWeaver"] = None
        self._init_cognitive_weaver()

        # 🕉️ SHIVA: The Destroyer of Illusions - Lifecycle Manager (OPUS-082)
        shiva_config = self._full_config.get("shiva", {})
        self._shiva = ShivaLifecycleManager(workspace=self._workspace, config=shiva_config)
        self._shiva.inject_kernel(self)

        # 🌙 SANKALPA: Strategic Will - Proactive Mission Planning (OPUS-089)
        self._sankalpa = None
        self._init_sankalpa()

        # 📓 OBSERVATION LOGGER: Make MANAS thoughts visible in OPUS.md
        self._observation_logger = None
        self._init_observation_logger()

        # 🧠 OPUS-112: SYNAPTIC MEMORY - The Reading Brain
        # Inference engine for experience-based decision making
        from .triggers import SynapticMemory

        self._synaptic_memory = SynapticMemory.get(self._workspace)
        logger.info(
            f"🧠 OPUS-112: Synaptic Memory initialized "
            f"({self._synaptic_memory.get_stats()['total_connections']} connections)"
        )

        logger.info("MANAS Cognitive Kernel initialized (with Shiva + Sankalpa + Synaptic Inference)")

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
    # =========================================================================

    def _init_prakriti_sense(self) -> None:
        """
        Initialize Prakriti Sense - the Sixth Jnanendriya.

        This provides unified state perception for MANAS.
        """
        try:
            from .cortex.prakriti_sense import PrakritiSense

            prakriti_config = self._full_config.get("prakriti_sense", {})
            self._prakriti_sense = PrakritiSense(
                workspace=self._workspace,
                config=prakriti_config,
            )
            # Boot perception
            summary = self._prakriti_sense.on_manas_boot()
            logger.info(
                f"👁️ PRAKRITI SENSE: Sixth Jnanendriya initialized - "
                f"Total: {summary.total_paths}, Health: {summary.health_ratio:.0%}"
            )
        except Exception as e:
            logger.warning(f"👁️ PRAKRITI SENSE: Could not initialize: {e}")
            self._prakriti_sense = None

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
        self._prakriti_sense = sense
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

    def _execute_healing(self, intent: Intent) -> Dict[str, Any]:
        """
        Execute a healing intent via PrakritiSense.

        Args:
            intent: The healing intent to execute

        Returns:
            Execution result
        """
        if not self._prakriti_sense:
            return {"success": False, "error": "PrakritiSense not available"}

        try:
            if intent.intent_type == "heal_system_state":
                paths = intent.params.get("paths", [])
                healed = 0
                for path_str in paths:
                    path = Path(path_str)
                    new_guna = self._prakriti_sense.heal(path)
                    if new_guna.value in ("sattva", "rajas"):
                        healed += 1

                return {
                    "success": True,
                    "healed_count": healed,
                    "total_paths": len(paths),
                }

            elif intent.intent_type == "fix_lobotomy":
                # Lobotomy fix is more complex - for now just report
                return {
                    "success": False,
                    "error": "Lobotomy fix requires manual .gitignore edit",
                    "violations": intent.params.get("violations", []),
                }

            else:
                return {"success": False, "error": f"Unknown healing intent type: {intent.intent_type}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_memory_review(self, intent: Intent) -> Dict[str, Any]:
        """
        🌙 Execute Dreaming: Consolidate wisdom from past actions.

        OPUS-089: Shiva/Sankalpa Memory Review
        Triggered by Sankalpa during idle times (The Void).
        This closes the cognitive loop: Experience → Wisdom.

        The digital equivalent of REM sleep - pattern consolidation.
        """
        logger.info("🌙 MANAS: Entering Dream State (Memory Review)...")

        try:
            # 1. Extract successful patterns (What works?)
            successful_patterns = self._memory.get_successful_patterns(limit=5)

            # 2. Extract failure patterns (What to avoid?)
            # Group recent failures by intent_type
            failure_counts: Dict[str, int] = {}
            for mem in self._memory.get_all_memories():
                if mem.outcome == "failed":
                    failure_counts[mem.intent_type] = failure_counts.get(mem.intent_type, 0) + 1

            # Sort by failure count
            failure_patterns = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # 3. Wisdom Synthesis - Log insights to OPUS.md journal
            insights = []

            if successful_patterns:
                self.log_insight("🧠 Dream Insights - Successful Patterns:")
                for pattern in successful_patterns:
                    success_rate = self._memory.get_success_rate(pattern)
                    insight_msg = f"✅ {pattern}: {success_rate:.0%} success rate"
                    self.log_insight(insight_msg)
                    insights.append({"type": pattern, "success_rate": success_rate, "status": "trusted"})

            if failure_patterns:
                self.log_insight("🧠 Dream Insights - Failure Patterns (to avoid):")
                for pattern, count in failure_patterns:
                    insight_msg = f"⚠️ {pattern}: {count} failures"
                    self.log_insight(insight_msg)
                    insights.append({"type": pattern, "failure_count": count, "status": "avoid"})

            if not successful_patterns and not failure_patterns:
                self.log_insight("🧠 Dream: No clear patterns formed yet. Mind is still young.")

            # 4. Record dream summary to memory (meta-learning)
            self._memory.record_intent_outcome(
                intent_type="memory_review",
                description="Dream cycle completed",
                outcome="success",
                context={
                    "successful_patterns": successful_patterns,
                    "failure_patterns": [p[0] for p in failure_patterns],
                    "insights_count": len(insights),
                },
            )

            logger.info(f"🌙 MANAS: Dream complete. {len(insights)} insights consolidated.")

            return {
                "success": True,
                "insights": insights,
                "successful_patterns": successful_patterns,
                "failure_patterns": [{"type": p[0], "count": p[1]} for p in failure_patterns],
                "wisdom": "Patterns consolidated into memory",
            }

        except Exception as e:
            logger.error(f"❌ Nightmare (Dream failed): {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # 🙏 DHARMA SENSE: THE VEDIC CONSCIENCE (OPUS-009 Extension)
    # =========================================================================

    def _init_dharma_sense(self) -> None:
        """
        Initialize Dharma Sense - the Vedic Conscience.

        This provides ethical alignment checks before intent execution.
        """
        try:
            from .cortex.dharma_sense import DharmaSense

            dharma_config = self._full_config.get("dharma_sense", {})
            self._dharma_sense = DharmaSense(workspace=self._workspace, agent_id="manas", config=dharma_config)
            # Boot registration
            summary = self._dharma_sense.on_manas_boot()
            logger.info(
                f"🙏 DHARMA SENSE: Conscience initialized - Ashrama: {summary.ashrama}, Bhakti: {summary.bhakti}"
            )
        except Exception as e:
            logger.warning(f"🙏 DHARMA SENSE: Could not initialize: {e}")
            self._dharma_sense = None

    def inject_dharma_sense(self, sense: "DharmaSense") -> None:
        """
        Inject the Dharma Sense for ethical alignment checks.

        OPUS-009 Extension: MANAS needs both senses:
        - PRAKRITI SENSE: "What is the state of the world?"
        - DHARMA SENSE: "Is this action righteous?"

        Args:
            sense: DharmaSense instance
        """
        self._dharma_sense = sense
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
    # =========================================================================

    def _init_sutra_sense(self) -> None:
        """
        Initialize Sutra Sense - the Third Eye.

        This provides doc/code gap detection for MANAS.
        MANAS becomes the curator of its own documentation.

        Bhagavad Gita 9.22:
        "ananyāś cintayanto māṁ... yoga-kṣemaṁ vahāmy aham"
        "I bring what is lacking (Yoga) and preserve what they have (Kshema)"
        """
        try:
            from .cortex.sutra_sense import SutraSense

            sutra_config = self._full_config.get("sutra_sense", {})
            self._sutra_sense = SutraSense(workspace=self._workspace, config=sutra_config)
            # Boot perception
            summary = self._sutra_sense.perceive_gaps(refresh=True)
            logger.info(
                f"📜 SUTRA SENSE: Third Eye opened - "
                f"{summary.total_docs} docs, {summary.gaps_found} gaps, {summary.health_ratio:.0%} health"
            )
        except Exception as e:
            logger.warning(f"📜 SUTRA SENSE: Could not initialize: {e}")
            self._sutra_sense = None

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
        self._sutra_sense = sense
        logger.info("📜 SUTRA SENSE: Third Eye injected - MANAS can now perceive documentation gaps")

    # =========================================================================
    # 👂 SHRUTA SENSE: The 6th Jnanendriya - Hearing Filesystem (OPUS-156)
    # =========================================================================

    def _init_shruta_sense(self) -> None:
        """
        Initialize Shruta Sense - the Hearing System.

        OPUS-156: This provides filesystem vibration detection for MANAS.
        MANAS can now HEAR before it SEES.

        Sanskrit: श्रुत (Shruta) = "That which is heard"

        "Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
        "At the beginning was darkness. Brahma HEARD before he SAW."
        """
        try:
            from .cortex.shruta_sense import ShrutaSense

            shruta_config = self._full_config.get("shruta_sense", {})
            self._shruta_sense = ShrutaSense(
                workspace=self._workspace,
                config=shruta_config,
            )

            # Start listening to filesystem vibrations
            watch_paths = [
                self._workspace / "vibe_core",
                self._workspace / "tests",
                self._workspace / "docs",
            ]
            self._shruta_sense.start_listening(paths=watch_paths)

            # Register auto-discovery handler
            self._shruta_sense.register_auto_discovery()

            logger.info("👂 SHRUTA SENSE: The 6th Jnanendriya activated - MANAS can now HEAR filesystem vibrations")

        except Exception as e:
            logger.warning(f"👂 SHRUTA SENSE: Could not initialize: {e}")
            self._shruta_sense = None

    # =========================================================================
    # 🫀 PRANA SENSE: The 7th Jnanendriya - Agent Presence (OPUS-166)
    # =========================================================================

    def _init_prana_sense(self) -> None:
        """
        Initialize Prana Sense - Agent Presence Awareness.

        OPUS-166: This provides awareness of which agents are alive/dead.
        Integrates with ShrutaSense for real-time presence detection.

        Sanskrit: प्राण (Prana) = Life force, breath, vital energy

        "Prana is the breath of the universe. When an agent breathes (pulses),
         it leaves a trace. When it stops breathing, the trace vanishes."
        """
        try:
            from .cortex.prana_sense import PranaSense

            prana_config = self._full_config.get("prana_sense", {})
            self._prana_sense = PranaSense(
                workspace=self._workspace,
                config=prana_config,
            )

            # Register with ShrutaSense for real-time presence updates
            if self._shruta_sense:
                self._prana_sense.register_with_shruta(self._shruta_sense)
                logger.info("🫀 PRANA SENSE: Connected to ShrutaSense for real-time presence detection")

            # Initial perception to set baseline
            perception = self._prana_sense.perceive()
            logger.info(
                f"🫀 PRANA SENSE: 7th Jnanendriya activated - "
                f"{perception.total_alive}/{perception.total_registered} agents alive"
            )

        except Exception as e:
            logger.warning(f"🫀 PRANA SENSE: Could not initialize: {e}")
            self._prana_sense = None

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

            # React to deaths - generate investigation intents
            for death in perception.deaths:
                agent_id = death.agent_id
                presence = self._prana_sense.get_agent_presence(agent_id)

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

    def _init_infrastructure_genesis(self) -> None:
        """
        Initialize the Infrastructure Genesis service (OPUS-158).

        The Stadtamt - creates GAD-000 compliant infrastructure:
        - __init__.py for discoverability
        - manifest.json for capabilities
        - Base class stubs for composability

        "Jedes Haus bekommt einen Briefkasten. Jede Straße ein Schild."
        """
        try:
            from .cortex.genesis import InfrastructureClassifier, InfrastructureGenerator

            genesis_config = self._full_config.get("genesis", {})
            enabled = genesis_config.get("enabled", True)

            if not enabled:
                logger.info("🏛️ GENESIS: Disabled by configuration")
                return

            self._infrastructure_classifier = InfrastructureClassifier(workspace=self._workspace)
            self._infrastructure_generator = InfrastructureGenerator(workspace=self._workspace)

            logger.info(
                "🏛️ INFRASTRUCTURE GENESIS: The Stadtamt Service activated - Auto-generating GAD-000 infrastructure"
            )

        except Exception as e:
            logger.warning(f"🏛️ GENESIS: Could not initialize: {e}")
            self._infrastructure_classifier = None
            self._infrastructure_generator = None

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

                # 🏛️ OPUS-158: Trigger Infrastructure Genesis for new directories
                # The Agent Virus: Auto-generate GAD-000 infrastructure
                self._process_genesis_vibrations(perception)

            return perception
        except Exception as e:
            logger.warning(f"👂 SHRUTA: Error during perception: {e}")
            return None

    def _process_genesis_vibrations(self, perception: "ShrutaPerception") -> None:
        """
        Process vibrations for Infrastructure Genesis.

        OPUS-160: Delegates to vibe_core.genesis.GenesisService (Stadtamt).
        MANAS detects gaps, Stadtamt builds infrastructure.
        """
        try:
            # Try to use vibe_core GenesisService (OPUS-160)
            from vibe_core.genesis import GenesisService, ModuleType

            genesis = GenesisService.get_instance(workspace=self._workspace)

            for vibration in perception.vibrations:
                # Only process directory creation events
                if vibration.event_type != "created" or not vibration.is_directory:
                    continue

                # Classify and ensure compliance via Stadtamt
                module_type = genesis.classify_path(vibration.path)

                if module_type == ModuleType.UNKNOWN:
                    continue

                # Call the Stadtamt for compliance
                result = genesis.ensure_compliance(vibration.path, module_type)

                if result.build_result and result.build_result.files_created_count > 0:
                    logger.info(
                        f"🏛️ STADTAMT: Created {result.build_result.files_created_count} files "
                        f"for {module_type.name}: {vibration.path.name}"
                    )

        except ImportError:
            # Fallback to OPUS-158 local genesis (legacy)
            self._process_genesis_vibrations_legacy(perception)
        except Exception as e:
            logger.warning(f"🏛️ GENESIS: Error processing vibrations: {e}")

    def _process_genesis_vibrations_legacy(self, perception: "ShrutaPerception") -> None:
        """
        Legacy genesis processing (OPUS-158 fallback).

        Used when vibe_core.genesis is not available.
        """
        if not self._infrastructure_classifier or not self._infrastructure_generator:
            return

        try:
            from .cortex.genesis import ModuleType

            for vibration in perception.vibrations:
                if vibration.event_type != "created" or not vibration.is_directory:
                    continue

                module_type = self._infrastructure_classifier.classify(vibration.path, is_directory=True)

                if module_type == ModuleType.UNKNOWN:
                    continue

                result = self._infrastructure_generator.generate(vibration.path, module_type)

                if result.files_created_count > 0:
                    logger.info(
                        f"🏛️ GENESIS (legacy): Auto-generated {result.files_created_count} files "
                        f"for {module_type.name}: {vibration.path.name}"
                    )

        except Exception as e:
            logger.warning(f"🏛️ GENESIS (legacy): Error: {e}")

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
    # 🧵 COGNITIVE WEAVER: STATE ↔ KNOWLEDGE BRIDGE (OPUS-106)
    # =========================================================================

    def _init_cognitive_weaver(self) -> None:
        """
        Initialize Cognitive Weaver - the State ↔ Knowledge Bridge.

        OPUS-106: "Gedächtnis ohne Wissen ist blind. Wissen ohne Gedächtnis ist vergesslich."

        This provides unified access to:
        - State Layer (Prakriti, StateSyncHolon) - What MANAS REMEMBERS
        - Knowledge Layer (UnifiedKnowledgeGraph) - What MANAS KNOWS
        - Session Context (OPUS.md preserved sections) - What MANAS was DOING

        The Cognitive Weaver enables MANAS to make intelligent decisions
        that combine historical state with conceptual knowledge.
        """
        try:
            from vibe_core.state.cognitive_weaver import CognitiveWeaver

            self._cognitive_weaver = CognitiveWeaver(workspace=self._workspace)

            # OPUS-106: Inject session context from OPUS.md (UI → Mind Bridge)
            self._inject_session_context_from_opus()

            # Boot diagnosis
            diagnosis = self._cognitive_weaver.diagnose()
            health = diagnosis.get("unified", {}).get("overall_health", 0)
            session_ctx = (
                "with session context" if self._cognitive_weaver.has_session_context() else "no session context"
            )
            logger.info(
                f"🧵 COGNITIVE WEAVER: State ↔ Knowledge Bridge initialized - Health: {health:.0%}, {session_ctx}"
            )
        except Exception as e:
            logger.warning(f"🧵 COGNITIVE WEAVER: Could not initialize: {e}")
            self._cognitive_weaver = None

    def _inject_session_context_from_opus(self) -> None:
        """
        OPUS-106: Extract preserved sections from OPUS.md and inject into CognitiveWeaver.

        This bridges the UI-Layer (OPUS.md) with the Mind-Layer (MANAS).
        The preserved sections contain what the previous AI/Human wrote,
        enabling continuity across sessions.
        """
        if not self._cognitive_weaver:
            return

        try:
            opus_path = self._workspace / "OPUS.md"
            if not opus_path.exists():
                return

            # Try to get preserved sections from opus_assistant
            try:
                from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
                    OpusDashboardRenderer,
                )

                renderer = OpusDashboardRenderer(self._workspace)
                preserved = renderer._extract_preserved_sections()

                if preserved:
                    self._cognitive_weaver.inject_session_context(preserved)
                    logger.debug("🧵 COGNITIVE WEAVER: Session context loaded from OPUS.md")
            except ImportError:
                logger.debug("🧵 COGNITIVE WEAVER: OpusDashboardRenderer not available")
            except Exception as e:
                logger.debug(f"🧵 COGNITIVE WEAVER: Could not extract preserved sections: {e}")

        except Exception as e:
            logger.warning(f"🧵 COGNITIVE WEAVER: Failed to inject session context: {e}")

    def inject_cognitive_weaver(self, weaver: "CognitiveWeaver") -> None:
        """
        Inject the Cognitive Weaver for unified state + knowledge access.

        OPUS-106: This enables MANAS to perceive BOTH state and knowledge
        as ONE unified consciousness.

        Args:
            weaver: CognitiveWeaver instance
        """
        self._cognitive_weaver = weaver
        logger.info("🧵 COGNITIVE WEAVER: State ↔ Knowledge Bridge injected")

    def get_cognitive_context(self, focus: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get unified cognitive context combining state + knowledge.

        OPUS-106: This is the "perception" method - what MANAS sees when
        it looks at the unified state of consciousness.

        Args:
            focus: Optional focus area (e.g., "governance", "state")

        Returns:
            Dict with unified context or None if weaver unavailable
        """
        if not self._cognitive_weaver:
            return None

        try:
            context = self._cognitive_weaver.weave(focus=focus)
            return {
                "health_score": context.health_score,
                "tamas_count": len(context.tamas_paths),
                "dirty_count": len(context.dirty_paths),
                "wisdom_notes": context.wisdom_notes,
                "recommended_actions": context.recommended_actions,
                "prompt_context": context.to_prompt_context(),
            }
        except Exception as e:
            logger.debug(f"🧵 COGNITIVE WEAVER: Could not weave context: {e}")
            return None

    def consult_knowledge(self, action: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Consult knowledge before taking an action.

        OPUS-106: Before MANAS acts, it can ask the knowledge graph:
        - Is this action allowed?
        - What constraints apply?
        - What authority is required?

        Args:
            action: The action being considered
            context: Context about the action

        Returns:
            Consultation result or None if unavailable
        """
        if not self._cognitive_weaver:
            return None

        try:
            consultation = self._cognitive_weaver.consult(action, context)
            return {
                "allowed": consultation.allowed,
                "constraints_violated": consultation.constraints_violated,
                "authority_required": consultation.authority_required,
                "recommendation": consultation.recommendation,
            }
        except Exception as e:
            logger.debug(f"🧵 COGNITIVE WEAVER: Could not consult knowledge: {e}")
            return None

    def get_cognitive_diagnosis(self) -> Optional[Dict[str, Any]]:
        """
        Get full system diagnosis from Cognitive Weaver.

        Returns combined state + knowledge health check.
        """
        if not self._cognitive_weaver:
            return None

        try:
            return self._cognitive_weaver.diagnose()
        except Exception as e:
            logger.debug(f"🧵 COGNITIVE WEAVER: Could not diagnose: {e}")
            return None

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
            pending_count = len([e for e in self._intent_buffer if e.status == "pending"])

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
    # =========================================================================

    def _init_observation_logger(self) -> None:
        """
        Initialize ObservationLogger for making MANAS thoughts visible.

        OPUS-089: The journal in OPUS.md should show MANAS's internal state,
        not just events. Dreams, insights, patterns - all visible.
        """
        try:
            from vibe_core.plugins.opus_assistant.core.observation_logger import (
                ObservationLogger,
            )

            obs_config = self._full_config.get("observation_logger", {})
            self._observation_logger = ObservationLogger(workspace_root=self._workspace, config=obs_config)
            logger.info(f"📓 OBSERVATION LOGGER: Initialized (config: {len(obs_config)} keys)")
        except Exception as e:
            logger.warning(f"📓 MANAS: Could not initialize ObservationLogger: {e}")
            self._observation_logger = None

    def log_insight(self, message: str) -> None:
        """
        Log an insight to OPUS.md journal.

        Use this to make MANAS's internal thoughts visible:
        - Dream insights from memory_review
        - Pattern recognitions
        - Self-debugging observations
        """
        if self._observation_logger:
            self._observation_logger.log_insight(message, source="MANAS")
        # Also log to Python logger for file logs
        logger.info(f"💡 MANAS INSIGHT: {message}")

    def log_observation(self, message: str, severity: str = "info") -> None:
        """
        Log an observation to OPUS.md journal.

        Args:
            message: The observation message
            severity: "info", "warn", "alert", or "insight"
        """
        if self._observation_logger:
            if severity == "insight":
                self._observation_logger.log_insight(message, source="MANAS")
            elif severity == "warn":
                self._observation_logger.log_warn(message, source="MANAS")
            elif severity == "alert":
                self._observation_logger.log_alert(message, source="MANAS")
            else:
                self._observation_logger.log_info(message, source="MANAS")

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

        The 6 Jnanendriyas (Perception Organs):
        1. PRAKRITI SENSE → System state
        2. DHARMA SENSE → Ethical alignment (used in decide phase)
        3. SUTRA SENSE → Documentation gaps
        4. KARMA SENSE → Memory traces
        5. VIVEKA SENSE → Discriminative ranking
        6. SHRUTA SENSE → Filesystem vibrations (OPUS-156)

        Returns:
            (observations, metadata) where observations is list of intents discovered
        """
        observations = []

        # 👂 SHRUTA SENSE: Perceive filesystem vibrations FIRST
        # "Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
        shruta_perception = self._perceive_filesystem_vibrations()
        vibration_count = shruta_perception.total_count if shruta_perception else 0

        # 👁️ PRAKRITI SENSE: Perceive state and generate healing intents
        healing_intents = self._perceive_and_generate_healing_intents()
        observations.extend(healing_intents)

        # 🫀 PRANA SENSE: Perceive agent presence and generate lifecycle intents
        presence_intents = self._perceive_and_generate_presence_intents()
        observations.extend(presence_intents)

        # 📜 SUTRA SENSE: Perceive documentation gaps
        gap_intents = self._perceive_and_generate_gap_intents()
        observations.extend(gap_intents)

        # 🌙 SANKALPA: Strategic proactive intents
        sankalpa_intents = self._generate_sankalpa_intents({})
        observations.extend(sankalpa_intents)

        # Clean up expired intents
        self._cleanup_expired_intents()

        metadata = {
            "vibration_count": vibration_count,  # OPUS-156: ShrutaSense
            "healing_count": len(healing_intents),
            "presence_count": len(presence_intents),  # OPUS-166: PranaSense
            "gap_count": len(gap_intents),
            "sankalpa_count": len(sankalpa_intents),
        }

        return observations, metadata

    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        ORIENT Phase: Organize and prioritize observations.

        Args:
            observations: List of intents from perceive phase

        Returns:
            (orientations, metadata) where orientations is organized/prioritized intent list
        """
        # 🕉️ SHIVA: Sweep stale intents (destroy illusions)
        swept = self._shiva.sweep_stale_intents()
        if swept > 0:
            logger.info(f"🕉️ SHIVA: Swept {swept} fulfilled intents")

        # Generate new intents from current context
        # OPUS-096: Async generation for Semantic Engine
        new_intents = await self._intent_generator.generate_intents({})

        # Combine perceptions with generated intents
        all_intents = observations + new_intents

        # Organize by priority: healing → gap → sankalpa → generated
        orientations = all_intents

        metadata = {
            "new_generated": len(new_intents),
            "total_oriented": len(orientations),
            "swept_count": swept,
        }

        return orientations, metadata

    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        DECIDE Phase: Select which intents to execute.

        Args:
            orientations: Organized intent list from orient phase

        Returns:
            (decisions, metadata) where decisions is throttled/prioritized intent list
        """
        new_intents = orientations

        # OPUS-035: Throttling - Prioritize survival over growth
        if self._config.survival_first and len(new_intents) > self._config.max_intents_per_tick:
            new_intents = self._prioritize_survival(new_intents)

        # Throttle to max_intents_per_tick
        if len(new_intents) > self._config.max_intents_per_tick:
            logger.debug(f"⚡ MANAS: Throttling {len(new_intents)} → {self._config.max_intents_per_tick}")
            new_intents = new_intents[: self._config.max_intents_per_tick]

        decisions = new_intents

        metadata = {
            "throttled_from": len(orientations),
            "decided_count": len(decisions),
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

                self._intent_buffer.append(entry)
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
                is_safe = self._config.auto_execute_safe and intent.auto_executable and intent.risk == IntentRisk.SAFE
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
        # Trim buffer to max size
        while len(self._intent_buffer) > self._config.max_intent_buffer_size:
            removed = False
            for i, entry in enumerate(self._intent_buffer):
                if entry.status != "pending":
                    self._intent_buffer.pop(i)
                    removed = True
                    break
            if not removed:
                self._intent_buffer.pop(0)

        # Save intent buffer to disk
        self._save_intent_buffer()
        logger.debug("💾 MANAS: Persisted intent buffer")

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

        self._save_intent_buffer()
        logger.info(f"Intent {intent_id} rejected: {reason or 'no reason given'}")
        return True

    def get_pending_intents(self) -> List[Intent]:
        """Get all pending intents (for OPUS.md display)."""
        return [entry.intent for entry in self._intent_buffer if entry.status == "pending"]

    def get_intent_buffer(self) -> List[IntentBufferEntry]:
        """Get the full intent buffer."""
        return list(self._intent_buffer)

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
        """Check if MANAS should think (rate limit + idle check)."""
        now = datetime.utcnow()

        # Check idle threshold
        idle_minutes = self.get_idle_minutes()
        if idle_minutes >= self._config.idle_threshold_minutes:
            logger.debug(f"MANAS: Idle for {idle_minutes} min, should think")
            return True

        # Check time since last thought
        if self._last_thought_time is None:
            return True  # First thought

        minutes_since_thought = (now - self._last_thought_time).total_seconds() / 60
        if minutes_since_thought >= self._config.thinking_interval_minutes:
            return True

        return False

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
        This enables detecting multiple harness_broken issues simultaneously.
        """
        for entry in self._intent_buffer:
            if entry.status == "pending":
                # Same type AND same title = duplicate
                if entry.intent.intent_type == intent.intent_type and entry.intent.title == intent.title:
                    return True
        return False

    def _find_intent_entry(self, intent_id: str) -> Optional[IntentBufferEntry]:
        """Find intent entry by ID."""
        for entry in self._intent_buffer:
            if entry.intent.id == intent_id:
                return entry
        return None

    def _execute_intent(self, entry: IntentBufferEntry) -> bool:
        """
        Execute an approved intent.

        OPUS-057 VAJRA: All executions are recorded to the ledger.

        Args:
            entry: The intent buffer entry to execute

        Returns:
            True if execution succeeded
        """
        intent = entry.intent
        logger.info(f"MANAS: Executing intent: {intent.title}")

        start_time = datetime.utcnow()
        success = False
        result = {}

        # 🔌 CABLE: Reset idle timer on execution
        self.record_activity()

        # ⚡ VAJRA: Record INTENT_EXECUTING to ledger BEFORE execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTING",
            intent=intent,
            extra_data={"timestamp": start_time.isoformat()},
        )

        # 🙏 DHARMA GATE: Check ethical alignment before execution (OPUS-009)
        dharma_permitted, dharma_reason = self._check_dharma_gate(intent)
        if not dharma_permitted:
            logger.warning(f"🙏 DHARMA GATE BLOCKED: {intent.title}")
            entry.status = "blocked_adharmic"
            entry.execution_result = {"error": f"BLOCKED BY DHARMA GATE: {dharma_reason}"}
            self._record_to_ledger(
                event_type="MANAS_INTENT_BLOCKED_ADHARMIC",
                intent=intent,
                extra_data={"reason": dharma_reason},
            )
            self._save_intent_buffer()
            return False

        try:
            # 👁️ PRAKRITI SENSE: Handle healing intents (OPUS-009)
            if intent.intent_type in ("heal_system_state", "fix_lobotomy"):
                result = self._execute_healing(intent)
                success = result.get("success", False)
            # 🌙 SHIVA/SANKALPA: Handle dreaming/wisdom consolidation
            elif intent.intent_type == "memory_review":
                result = self._execute_memory_review(intent)
                success = result.get("success", False)
            elif self._execution_callback:
                result = self._execution_callback(intent)
                success = result.get("success", False)
            elif intent.circuit_to_execute:
                # 🔌 CABLE: Execute via CognitiveCircuitExecutor (OPUS-083)
                logger.info(f"MANAS: Executing circuit: {intent.circuit_to_execute}")
                try:
                    from .circuit_executor import CognitiveCircuitExecutor

                    executor = CognitiveCircuitExecutor(workspace=self._workspace)
                    result = executor.execute_circuit(intent.circuit_to_execute)
                    success = result.get("success", False)
                except ImportError:
                    logger.warning("CognitiveCircuitExecutor not available")
                    result = {"error": "CircuitExecutor not available"}
                    success = False
                except Exception as exec_err:
                    logger.error(f"Circuit execution failed: {exec_err}")
                    result = {"error": str(exec_err)}
                    success = False
            else:
                # OPUS-127: Route via IntentRouter as fallback
                try:
                    from .intent_router import IntentRouter

                    router = IntentRouter(workspace=self._workspace)
                    if intent.intent_type in router._handlers:
                        logger.info(f"🔀 MANAS: Routing via IntentRouter: {intent.intent_type}")
                        result = router.route(intent)
                        success = result.get("success", False)
                    else:
                        logger.warning(f"No execution method for intent: {intent.id}")
                        result = {"error": "No execution method available"}
                except ImportError:
                    logger.warning(f"IntentRouter not available for: {intent.id}")
                    result = {"error": "No execution method available"}
                except Exception as router_err:
                    logger.error(f"IntentRouter failed: {router_err}")
                    result = {"error": str(router_err)}
                    success = False

        except Exception as e:
            logger.error(f"Intent execution failed: {e}")
            result = {"error": str(e)}
            success = False

        # Update entry
        entry.status = "executed" if success else "failed"
        entry.executed_at = datetime.utcnow().isoformat()
        entry.execution_result = result

        # Calculate execution time
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # ⚡ VAJRA: Record INTENT_EXECUTED or INTENT_FAILED to ledger AFTER execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTED" if success else "MANAS_INTENT_FAILED",
            intent=intent,
            extra_data={
                "execution_time_ms": execution_time,
                "result": result,
                "outcome": "success" if success else "failed",
            },
        )

        # Record in memory (MANAS internal)
        self._memory.record_intent_outcome(
            intent_type=intent.intent_type,
            description=intent.title,
            outcome="success" if success else "failed",
            context=intent.params,
            feedback=result.get("error"),
            execution_time_ms=execution_time,
        )

        # 🧠 OPUS-110: Synaptic Learning - Update weights based on outcome
        self._update_synapses(intent, success)

        self._save_intent_buffer()

        if success:
            # 🙏 DHARMA SENSE: Record success to increase Bhakti (OPUS-009)
            self._on_dharma_success(intent)
            logger.info(f"MANAS: Intent {intent.id} executed successfully")
        else:
            logger.warning(f"MANAS: Intent {intent.id} execution failed: {result.get('error')}")

        return success

    # =========================================================================
    # OPUS-110: SYNAPTIC LEARNING
    # =========================================================================

    def _update_synapses(self, intent: Intent, success: bool) -> None:
        """
        Update synaptic weights based on intent execution outcome.

        OPUS-110: The Learning Loop - MANAS strengthens connections that work,
        weakens connections that fail.

        Weight adjustment:
        - Success: weight += 0.1 * (1 - weight)  [asymptotic to 1.0]
        - Failure: weight -= 0.1 * weight        [asymptotic to 0.0]

        Args:
            intent: The executed intent
            success: Whether execution succeeded
        """
        # P0: Use StateService for centralized state management
        state = get_state_service(self._workspace)

        try:
            # Load current synapses via StateService
            synapses = state.load("synapses.json", default={"schema": "v1", "weights": {}, "meta": {}})

            weights = synapses.get("weights", {})

            # Determine trigger from intent context
            trigger = self._extract_trigger(intent)
            if not trigger:
                return  # No learnable trigger

            # Determine action from intent type
            action = f"action:{intent.intent_type}"

            # Get or create trigger entry
            if trigger not in weights:
                weights[trigger] = {}

            # Get current weight (default 0.5 for new connections)
            current_weight = weights[trigger].get(action, 0.5)

            # Hebbian-style learning: "neurons that fire together wire together"
            if success:
                # Strengthen: move toward 1.0
                new_weight = current_weight + 0.1 * (1.0 - current_weight)
            else:
                # Weaken: move toward 0.0
                new_weight = current_weight - 0.1 * current_weight

            # Clamp to [0.0, 1.0]
            new_weight = max(0.0, min(1.0, new_weight))

            # Update weight
            weights[trigger][action] = round(new_weight, 3)

            # Update meta
            synapses["weights"] = weights
            synapses["meta"]["last_updated"] = datetime.utcnow().isoformat()
            synapses["meta"]["total_connections"] = sum(len(v) for v in weights.values())

            # P0: Save via StateService (with automatic backup rotation)
            state.save("synapses.json", synapses)

            logger.debug(
                f"🧠 SYNAPSE: {trigger} → {action}: {current_weight:.2f} → {new_weight:.2f} ({'↑' if success else '↓'})"
            )

        except Exception as e:
            logger.warning(f"🧠 SYNAPSE UPDATE FAILED: {e}")

    def _extract_trigger(self, intent: Intent) -> Optional[str]:
        """
        Extract the canonical trigger pattern from an intent's context.

        OPUS-111: Signal Alignment - Uses TriggerRegistry for normalization.
        No more dynamic string generation that could cause vocabulary mismatch.

        Returns a canonical trigger string from TriggerPatterns, or None if
        the intent doesn't map to a learnable trigger.
        """
        from .triggers import normalize_trigger

        # OPUS-111: Use centralized normalization
        # Returns None for intents that don't have canonical triggers
        # This prevents memory pollution with non-canonical patterns
        pattern = normalize_trigger(intent)
        return pattern.value if pattern else None

    def _cleanup_expired_intents(self) -> None:
        """Remove expired intents from buffer."""
        now = datetime.utcnow()
        expiry_threshold = now - timedelta(hours=self._config.intent_expiry_hours)
        expiry_str = expiry_threshold.isoformat()

        original_count = len(self._intent_buffer)
        self._intent_buffer = [
            entry for entry in self._intent_buffer if entry.added_at >= expiry_str or entry.status == "pending"
        ]

        expired = original_count - len(self._intent_buffer)
        if expired > 0:
            logger.debug(f"MANAS: Cleaned up {expired} expired intents")

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def _get_buffer_file(self) -> Path:
        """Get path to intent buffer file."""
        return self._workspace / ".opus_state" / "manas_intents.json"

    def _load_intent_buffer(self) -> None:
        """Load intent buffer from disk."""
        try:
            buffer_file = self._get_buffer_file()
            if buffer_file.exists():
                data = json.loads(buffer_file.read_text())

                self._intent_buffer = []
                for entry_data in data.get("intents", []):
                    intent_data = entry_data.get("intent", {})

                    # Reconstruct Intent
                    intent = Intent(
                        id=intent_data.get("id", "unknown"),
                        intent_type=intent_data.get("intent_type", "unknown"),
                        title=intent_data.get("title", "Unknown"),
                        description=intent_data.get("description", ""),
                        reasoning=intent_data.get("reasoning", ""),
                        priority=IntentPriority(intent_data.get("priority", "medium")),
                        risk=IntentRisk(intent_data.get("risk", "medium")),
                        created_at=intent_data.get("created_at", datetime.utcnow().isoformat()),
                        circuit_to_execute=intent_data.get("circuit_to_execute"),
                        params=intent_data.get("params", {}),
                        auto_executable=intent_data.get("auto_executable", False),
                        expires_at=intent_data.get("expires_at"),
                    )

                    entry = IntentBufferEntry(
                        intent=intent,
                        status=entry_data.get("status", "pending"),
                        added_at=entry_data.get("added_at", datetime.utcnow().isoformat()),
                        executed_at=entry_data.get("executed_at"),
                        execution_result=entry_data.get("execution_result"),
                    )
                    self._intent_buffer.append(entry)

                logger.debug(f"Loaded {len(self._intent_buffer)} intents from disk")

        except Exception as e:
            logger.warning(f"Could not load intent buffer: {e}")
            self._intent_buffer = []

    def _save_intent_buffer(self) -> None:
        """Save intent buffer to disk via StateService (P0)."""
        try:
            data = {
                "intents": [
                    {
                        "intent": entry.intent.to_dict(),
                        "status": entry.status,
                        "added_at": entry.added_at,
                        "executed_at": entry.executed_at,
                        "execution_result": entry.execution_result,
                    }
                    for entry in self._intent_buffer
                ],
                "updated_at": datetime.utcnow().isoformat(),
            }

            # P0: Save via StateService (atomic write built-in)
            state = get_state_service(self._workspace)
            state.save("manas_intents.json", data, create_backup=False)

        except Exception as e:
            logger.warning(f"Could not save intent buffer: {e}")

    # =========================================================================
    # INTEGRATION POINTS
    # =========================================================================

    def get_intent_buffer_for_opus(self) -> Dict[str, Any]:
        """
        Get intent buffer formatted for OPUS.md display.

        Returns data ready to be rendered in the Intent Buffer section.
        """
        pending = [entry for entry in self._intent_buffer if entry.status == "pending"]
        executed = [entry for entry in self._intent_buffer if entry.status == "executed"][-5:]  # Last 5

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
