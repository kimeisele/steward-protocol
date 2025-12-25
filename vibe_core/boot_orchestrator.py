"""
⚡ BOOT ORCHESTRATOR ⚡
======================

The unified boot sequence for Agent City OS.

OPUS-095 REFACTORING: CognitiveCycle Integration
-------------------------------------------------
Migrated to CognitiveCycle for unified orchestration.
Sarga phases reorganized into OODA loop:

1. PERCEIVE: System initialization check (SHABDA)
2. ORIENT: Kernel + Communication + Oracle setup (AKASHA/VAYU/AGNI)
3. DECIDE: Knowledge graph + Agent discovery (JALA)
4. ACT: Kernel boot + Daily Ritual + Conveyor Belt (PRITHVI)
5. PERSIST: Final kernel state saved

PHOENIX VIMANA UNIFIED BOOT - Sarga Integration
-----------------------------------------------
Sarga cosmic creation sequence:
1. SHABDA (Sound) → Boot command received
2. AKASHA (Space) → Kernel memory allocated
3. VAYU (Air) → Communication channels established
4. AGNI (Fire) → Form/visibility (UI, capabilities)
5. JALA (Water) → Data streams flow (Knowledge Graph, context)
6. PRITHVI (Earth) → Persistence (Ledger, agents registered)

The system creates itself from nothing. Sound becomes form.

OPUS-031 Layer 4: BootMode Support
----------------------------------
Supports different boot modes for different execution contexts:
- FULL: Complete boot with all components (default)
- HEADLESS: Lightweight boot for autonomous execution (< 5 seconds)
- MINIMAL: Bare kernel for testing

USAGE:
    from vibe_core.boot_orchestrator import BootOrchestrator
    from vibe_core.boot_mode import BootMode

    # Full boot (default) - via unified orchestration
    orchestrator = BootOrchestrator()
    await orchestrator.orchestrate()  # CognitiveCycle OODA loop

    # Headless boot (fast, for autonomous circuits)
    orchestrator = BootOrchestrator(boot_mode=BootMode.HEADLESS)
    kernel = await orchestrator.orchestrate()

    # THE OPERATOR LOOP - This is where intelligence flows
    await orchestrator.run_with_operator()
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.boot_mode import BootMode
from vibe_core.config import CityConfig
from vibe_core.event_bus import EventBus
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.operator_adapter import (
    LocalLLMOperator,
    TerminalOperator,
    UniversalOperatorAdapter,
)
from vibe_core.orchestration_cycle import CognitiveCycle, CycleContext
from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent
from vibe_core.protocols.operator_protocol import (
    GitState,
    IntentType,
    KernelStatusType,
    OperatorType,
    SystemContext,
)
from vibe_core.runtime.boot_sequence import BootSequence
from vibe_core.runtime.unified_trace import UnifiedTrace
from vibe_core.sarga import Element, get_sarga

logger = logging.getLogger("BOOT_ORCHESTRATOR")


class BootOrchestrator(CognitiveCycle):
    """
    Unified boot orchestration for Agent City OS.

    OPUS-095: Inherits from CognitiveCycle for unified orchestration.
    - Ensures consistent agent discovery and registration
    - Maps 6 Sarga phases to OODA loop
    - Holon wiring: parent of PranaOrchestrator (plugin pulse)
    - OPUS-031 Layer 4: Supports BootMode for different execution contexts
    """

    def __init__(
        self,
        ledger_path: Optional[str] = None,
        project_root: Optional[Path] = None,
        config: Optional[CityConfig] = None,
        boot_mode: BootMode = BootMode.FULL,
        trace: Optional[UnifiedTrace] = None,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialize the boot orchestrator.

        Args:
            ledger_path: Path to SQLite ledger (default: from PhoenixConfig)
            project_root: Project root directory (default: auto-detected)
            config: CityConfig instance (REQUIRED: Phoenix Config for agents)
            boot_mode: BootMode.FULL (default), HEADLESS, or MINIMAL
            trace: UnifiedTrace for observability
            event_bus: EventBus for phase events
        """
        super().__init__()

        # OPUS-031 Layer 4: Store boot mode for phase handlers
        self.boot_mode = boot_mode

        # OPUS-025: Resolve ledger_path from config if not provided
        if ledger_path is None:
            try:
                from vibe_core.phoenix import get_config

                phoenix_config = get_config()
                if phoenix_config and hasattr(phoenix_config, "paths"):
                    ledger_path = str(phoenix_config.paths.data.resolve("vibe_ledger"))
            except Exception:
                pass
            # Final fallback: construct from config defaults (not hardcoded string)
            if ledger_path is None:
                from pathlib import Path as _Path

                ledger_path = str(_Path("data") / "vibe_ledger.db")

        self.ledger_path = ledger_path
        self.project_root = project_root or Path.cwd()
        self.config = config  # BLOCKER #0: Phoenix Config integration
        self.kernel: Optional[RealVibeKernel] = None
        self.discoverer: Optional[Any] = None  # Lazy: Discoverer loaded at runtime

        # Sarga phase components (initialized during boot)
        self.prompt_context = None  # VAYU phase
        self.oracle = None  # AGNI phase

        # Conveyor Belt - Prompt generation for operators
        self.boot_sequence: Optional[BootSequence] = None

        # Universal Operator Adapter - THE SOCKET
        self.operator_adapter: Optional[UniversalOperatorAdapter] = None
        self._running = False
        self._parent_cycle_id: Optional[str] = None

        # Phase A Integration: ALWAYS initialize orchestration dependencies
        if not trace:
            trace = UnifiedTrace()
        if not event_bus:
            event_bus = EventBus()
        self.setup(trace, event_bus, steward_context=None)

    # ========================================================================
    # COGNITIVECYCLE CONFIGURATION
    # ========================================================================

    @property
    def cycle_name(self) -> str:
        """Cycle name for observability."""
        return "boot_sequence"

    @property
    def rate_limit_seconds(self) -> int:
        """Boot only happens once, so very high rate limit."""
        return 3600  # 1 hour - boot is one-time operation

    @property
    def timeout_seconds(self) -> int:
        """Maximum boot execution time."""
        return 600  # 10 minutes for complete boot

    @property
    def recovery_enabled(self) -> bool:
        """Enable error recovery."""
        return True

    @property
    def parent_cycle_id(self) -> Optional[str]:
        """Holon wiring: no parent (this is top-level bootstrap)."""
        return self._parent_cycle_id

    # ========================================================================
    # OODA LOOP IMPLEMENTATION (OPUS-095)
    # ========================================================================

    async def _perceive(self) -> Tuple[List[Any], Dict[str, Any]]:
        """
        PERCEIVE: System initialization check (SHABDA phase).

        Returns:
            (observations, metadata)
        """
        observations = []
        metadata = {}

        try:
            # SHABDA: Sound - Boot command received, initiation logged
            logger.info("⚡ OPUS-095: Boot sequence initiated (PERCEIVE phase)")
            logger.info(f"      → Project root: {self.project_root}")
            logger.info(f"      → Ledger path: {self.ledger_path}")
            logger.info(f"      → Boot mode: {self.boot_mode.value.upper()}")

            observations.append(
                {
                    "type": "boot_config",
                    "project_root": str(self.project_root),
                    "ledger_path": self.ledger_path,
                    "boot_mode": self.boot_mode.value,
                }
            )

            metadata["boot_config_valid"] = True

        except Exception as e:
            logger.error(f"PERCEIVE phase failed: {e}")
            metadata["error"] = str(e)

        return observations, metadata

    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        ORIENT: Kernel + Communication + Oracle setup (AKASHA/VAYU/AGNI phases).

        Returns:
            (orientations, metadata)
        """
        orientations = []
        metadata = {}

        try:
            # AKASHA: Space - Create kernel, allocate memory
            logger.info("⚡ OPUS-095: Setting up kernel space (AKASHA)")
            self.kernel = RealVibeKernel(ledger_path=self.ledger_path)
            logger.info(f"      → Kernel space allocated (ledger: {self.ledger_path})")

            # VAYU: Air - Establish communication channels
            logger.info("⚡ OPUS-095: Establishing communication (VAYU)")
            from vibe_core.runtime.prompt_context import PromptContext

            self.prompt_context = PromptContext()
            if self.kernel:
                self.prompt_context.set_kernel(self.kernel)
                logger.info("      → PromptContext initialized and kernel bound")

            # AGNI: Fire - Make system visible (capabilities, UI)
            logger.info("⚡ OPUS-095: Making system visible (AGNI)")
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol
            from vibe_core.protocols.task import TaskProtocol
            from vibe_core.runtime.oracle import KernelOracle
            from vibe_core.shuddhi.engine import ShuddhiEngine
            from vibe_core.task_management.task_manager import TaskManager

            if self.kernel:
                self.oracle = KernelOracle(self.kernel, self.project_root)

                # OPUS-212: Register Shuddhi self-healing service
                ServiceRegistry.register(ShuddhiProtocol, ShuddhiEngine())
                logger.info("      → ShuddhiProtocol registered in ServiceRegistry")

                # OPUS-212: Register Core Task Service
                task_manager = TaskManager(self.project_root, self.kernel.io)
                ServiceRegistry.register(TaskProtocol, task_manager)
                logger.info("      → TaskProtocol registered in ServiceRegistry (Core Stack)")

                capabilities = self.oracle.get_system_capabilities()
                logger.info(
                    f"      → Oracle active: {len(capabilities.get('tools', []))} tools, "
                    f"{len(capabilities.get('cartridges', []))} cartridges"
                )

            orientations.append(
                {
                    "kernel_ready": True,
                    "comms_ready": True,
                    "oracle_ready": True,
                }
            )

            metadata["kernel_space_allocated"] = True
            metadata["communication_established"] = True
            metadata["capabilities_discovered"] = len(capabilities.get("tools", []))

        except Exception as e:
            logger.error(f"ORIENT phase failed: {e}")
            metadata["error"] = str(e)
            orientations.append({"kernel_ready": False})

        return orientations, metadata

    async def _decide(self, orientations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        DECIDE: Knowledge graph + Agent discovery (JALA phase).

        Returns:
            (decisions, metadata)
        """
        decisions = []
        metadata = {}

        try:
            # JALA: Water - Data streams flow (Knowledge Graph, discovery)
            logger.info("⚡ OPUS-095: Loading knowledge and discovering agents (JALA)")

            from vibe_core.knowledge.graph import get_knowledge_graph

            graph = get_knowledge_graph()
            logger.info(
                f"      → Knowledge loaded: {len(graph.nodes)} nodes, {sum(len(e) for e in graph.edges.values())} edges"
            )

            # OPUS-031 Layer 4: Skip agent discovery in headless mode
            if self.boot_mode.should_skip_agents():
                logger.info("      → Agent discovery SKIPPED (headless mode)")
                decisions.append({"skip_discovery": True})
                metadata["discovery_skipped"] = True
                return decisions, metadata

            # Register Discoverer (Genesis Agent)
            discovered_count = 0
            try:
                from vibe_core.cartridges.system.discoverer.agent import Discoverer

                self.discoverer = Discoverer(kernel=self.kernel, config=self.config)
                self.kernel.register_agent(self.discoverer, spawn_process=False)
                logger.info("      → Discoverer (Genesis Agent) registered")

                # Discover all agents (processes are deferred to avoid deadlock)
                discovered_count = self.discoverer.discover_agents()
                logger.info(f"      → Discovered {discovered_count} agents")

                # Spawn deferred processes now that discovery is complete
                if discovered_count > 0:
                    spawned = self.kernel.spawn_deferred_agents()
                    logger.info(f"      → Spawned {spawned} agent processes")

            except ImportError as e:
                logger.warning(f"      ⚠️ Discoverer not available (container mode): {e}")
                self.discoverer = None
                # Container-only mode: agents loaded via library/*.vibe
                logger.info("      → Container mode: agents loaded from library/")

            decisions.append(
                {
                    "knowledge_graph_loaded": True,
                    "agents_discovered": discovered_count,
                }
            )

            metadata["nodes_in_graph"] = len(graph.nodes)
            metadata["agents_discovered"] = discovered_count

        except Exception as e:
            logger.error(f"DECIDE phase failed: {e}")
            metadata["error"] = str(e)

        return decisions, metadata

    async def _act(self, decisions: List[Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        ACT: Kernel boot + Daily Ritual + Conveyor Belt (PRITHVI phase).

        Returns:
            (results, metadata)
        """
        results = {}
        metadata = {}

        try:
            # PRITHVI: Earth - Persistence (boot kernel, ledger ready)
            logger.info("⚡ OPUS-095: Persistence and kernel finalization (PRITHVI)")

            # Boot the kernel (finalizes manifests, ledger, scheduler)
            # OPUS-306: Use boot_async() directly since we're in async context
            # Using sync boot() causes deadlock (60s timeout in future.result())
            if self.kernel:
                await self.kernel.boot_async(boot_mode=self.boot_mode)
                logger.info("      → Kernel booted, ledger active")

                # OPUS-031 Layer 4: Skip Daily Ritual in headless mode
                if not self.boot_mode.should_skip_daily_ritual():
                    from vibe_core.steward.daily_ritual import DailyRitual

                    self.kernel.daily_ritual = DailyRitual(self.kernel)
                    logger.info("      → Daily Ritual attached (time dimension active)")
                else:
                    logger.info("      → Daily Ritual SKIPPED (headless mode)")

                # Initialize Conveyor Belt (BootSequence) for prompt generation
                self.boot_sequence = BootSequence(self.project_root)
                logger.info("      → Conveyor Belt initialized (prompt generation ready)")

                # Final status
                status = self.kernel.get_status()
                total_agents = status.get("agents_registered", 0)
                logger.info(f"      → Total agents registered: {total_agents}")

                # OPUS-212: Start Shuddhi Kala Bridge (The Heartbeat Guardian)
                try:
                    from vibe_core.shuddhi.kala_bridge import start_kala_bridge

                    self._kala_bridge = start_kala_bridge(self.project_root)
                    logger.info("      → Shuddhi Kala Bridge active (Kala loop engaged)")
                except Exception as e:
                    logger.warning(f"⚠️ Could not start Shuddhi Kala Bridge: {e}")

                results["kernel_booted"] = True
                results["agents_registered"] = total_agents
                metadata["agents_registered"] = total_agents

        except Exception as e:
            logger.error(f"ACT phase failed: {e}")
            metadata["error"] = str(e)
            results["kernel_booted"] = False

        return results, metadata

    async def _persist(self, context: CycleContext) -> None:
        """
        PERSIST: Final kernel state saved.

        Called after all phases complete.
        """
        try:
            if self.kernel:
                # Kernel state is already persisted in _act() via kernel.boot()
                logger.info("💾 BOOT: Kernel state persisted")
        except Exception as e:
            logger.error(f"PERSIST phase failed: {e}")

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    async def boot_orchestrated(
        self, parent_cycle_id: Optional[str] = None, force: bool = False
    ) -> Optional[RealVibeKernel]:
        """
        Execute the unified boot sequence via CognitiveCycle orchestrate().

        OPUS-095: Integrates with orchestration abstraction.

        Args:
            parent_cycle_id: ID of calling cycle (if any)
            force: Bypass rate limits

        Returns:
            RealVibeKernel if successful
        """
        self._parent_cycle_id = parent_cycle_id
        await self.orchestrate(force=force)
        return self.kernel

    def boot(self) -> RealVibeKernel:
        """Thin wrapper: Execute boot sequence via orchestrate()."""
        try:
            kernel = asyncio.run(self.boot_orchestrated(force=True))
            if not kernel:
                raise RuntimeError("Boot orchestration failed")
            return kernel
        except Exception as e:
            raise RuntimeError(f"Boot sequence failed: {e}")

    def get_kernel(self) -> Optional[RealVibeKernel]:
        """
        Get the booted kernel instance.

        Returns:
            RealVibeKernel or None if not yet booted
        """
        return self.kernel

    def get_discoverer(self) -> Optional[Any]:
        """
        Get the Discoverer agent instance.

        Returns:
            Discoverer or None if not yet created
        """
        return self.discoverer

    # =========================================================================
    # OPERATOR LOOP - THE WIRING
    # =========================================================================

    def _init_operator_adapter(self) -> UniversalOperatorAdapter:
        """Initialize the operator adapter with default chain."""
        adapter = UniversalOperatorAdapter()
        adapter.register_operator(TerminalOperator(), priority=1)
        adapter.register_operator(LocalLLMOperator(), priority=2)
        # DegradedOperator is auto-registered at priority 999
        return adapter

    def _build_system_context(self) -> SystemContext:
        """Build SystemContext from current kernel state."""
        if not self.kernel:
            return SystemContext(
                boot_id="not-booted",
                kernel_status=KernelStatusType.SHUTDOWN,
            )

        status = self.kernel.get_status()
        sarga = get_sarga()

        # Get git state
        git_state = GitState()
        try:
            import subprocess

            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if branch.returncode == 0:
                git_state = GitState(
                    branch=branch.stdout.strip() or None,
                    is_clean=True,  # Simplified for now
                )
        except Exception:
            pass

        # Get available agents
        available_agents = list(self.kernel.agent_registry.keys()) if hasattr(self.kernel, "agent_registry") else []

        return SystemContext(
            boot_id=str(id(self.kernel)),
            kernel_status=KernelStatusType.READY if sarga.boot_complete else KernelStatusType.BOOTING,
            agents_registered=status.get("agents_registered", 0),
            agents_healthy=status.get("agents_registered", 0),  # Assume healthy for now
            sarga_phase=sarga.get_status().get("phases", {}).get("prithvi", {}).get("status"),
            sarga_complete=sarga.boot_complete,
            git=git_state,
            available_agents=available_agents,
            operator_type=self.operator_adapter.get_current_operator_type()
            if self.operator_adapter
            else OperatorType.HUMAN,
            degradation_level=self.operator_adapter.get_degradation_level() if self.operator_adapter else 0,
        )

    async def _execute_intent(self, intent: Intent) -> str:
        """Execute an intent and return result message."""
        logger.info(f"Executing intent: {intent.intent_type.value} - {intent.raw_input}")

        if intent.intent_type == IntentType.CONTROL:
            if intent.raw_input.lower() in ("exit", "quit", "shutdown", "stop"):
                self._running = False
                return "Shutting down Agent City..."
            elif intent.raw_input.lower() == "status":
                status = self.kernel.get_status()
                return f"Kernel: {status}"

        elif intent.intent_type == IntentType.QUERY:
            if not intent.raw_input or intent.raw_input.lower() == "status":
                status = self.kernel.get_status()
                return f"Agents: {status.get('agents_registered', 0)} | Sarga: complete"

        elif intent.intent_type == IntentType.DELEGATION:
            if intent.target_agent:
                agent = self.kernel.agent_registry.get(intent.target_agent)
                if agent:
                    return f"Delegated to {intent.target_agent}: {intent.raw_input}"
                return f"Agent not found: {intent.target_agent}"

        elif intent.intent_type == IntentType.REFLEX:
            # Reflexes are automatic, no action needed
            return ""

        # Default: treat as command
        return f"Command received: {intent.raw_input}"

    async def run_with_operator(self) -> None:
        """
        THE MAIN OPERATOR LOOP.

        This is where the system comes alive.
        The operator (Human, Claude Code, LLM, Local) controls the kernel.

        Loop:
        1. Build SystemContext from kernel state
        2. Send context to operator
        3. Get intent from operator
        4. Execute intent
        5. Repeat until shutdown
        """
        if not self.kernel:
            raise RuntimeError("Cannot run without booted kernel. Call boot() first.")

        # Initialize operator adapter
        self.operator_adapter = self._init_operator_adapter()
        self._running = True

        logger.info("=" * 70)
        logger.info("🚀 AGENT CITY OS - OPERATOR LOOP STARTED")
        logger.info(f"   Operator: {self.operator_adapter.get_current_operator_type().value}")
        logger.info("   Type 'exit' to shutdown")
        logger.info("=" * 70)

        # Run Conveyor Belt to display context and generate operator prompt
        # This shows the dashboard with kernel state, git, tests, etc.
        if self.boot_sequence:
            try:
                self.boot_sequence.run()
            except Exception as e:
                logger.warning(f"Boot sequence display failed (non-fatal): {e}")

        # Time dimension: Track ritual cycle timing
        last_ritual_time = time.time()
        RITUAL_INTERVAL = 300.0  # 5 minutes between ritual phases (adjustable)

        while self._running:
            try:
                # Get system context
                context = self._build_system_context()

                # Get intent from operator
                intent = await self.operator_adapter.query_operator(context)

                if intent:
                    # Execute intent
                    result = await self._execute_intent(intent)
                    if result:
                        await self.operator_adapter.report_result(result)

                # Ritual timing
                now = time.time()
                if now - last_ritual_time >= RITUAL_INTERVAL:
                    if self.kernel and hasattr(self.kernel, "daily_ritual"):
                        try:
                            # Trigger ritual phase
                            self.kernel.daily_ritual.trigger_phase()
                            last_ritual_time = now
                        except Exception as e:
                            logger.warning(f"Ritual trigger failed (non-fatal): {e}")

                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                self._running = False
            except Exception as e:
                logger.error(f"Operator loop error: {e}")
                await self.operator_adapter.report_error(str(e))
                self._running = False

        logger.info("🛑 AGENT CITY OS - SHUTDOWN COMPLETE")
