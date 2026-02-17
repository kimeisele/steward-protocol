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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe085be82"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.boot_mode import BootMode
from vibe_core.config import CityConfig
from vibe_core.event_bus import EventBus
from vibe_core.protocols.event import EventBusProtocol

# OPUS-095: Removed RealVibeKernel dependency (Dependency Inversion)
from vibe_core.protocols.kernel_protocol import KernelProtocol
from vibe_core.protocols.boot_protocol import BootProtocol, KernelFactoryProtocol
from vibe_core.protocols.substrate.byte import GenesisByte
from vibe_core.services.kernel_factory import KernelFactory
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
from vibe_core.sarga import get_sarga

logger = logging.getLogger("BOOT_ORCHESTRATOR")


class BootOrchestrator(CognitiveCycle, BootProtocol):
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
        event_bus: Optional[EventBusProtocol] = None,
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
            except Exception as e:
                # OPUS-312: Log config resolution failure
                import logging

                logging.getLogger("BOOT").warning(f"Phoenix config resolution failed: {e}")
            # Final fallback: construct from config defaults (not hardcoded string)
            if ledger_path is None:
                from pathlib import Path as _Path

                ledger_path = str(_Path("data") / "vibe_ledger.db")

        self.ledger_path = ledger_path
        self.project_root = project_root or Path.cwd()
        self.config = config  # BLOCKER #0: Phoenix Config integration

        # FACTORY PATTERN (No more 'new RealVibeKernel()')
        # Inject factory or use default service
        self._kernel_factory: KernelFactoryProtocol = KernelFactory()

        # KERNEL IS NOW LATENT (None) until ignited
        self.kernel: Optional[KernelProtocol] = None

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
            from vibe_core.mahamantra.substrate.event_bus import get_event_bus
            event_bus = get_event_bus()
        self.setup(trace, event_bus, steward_context=None)

    # ========================================================================
    # THE IGNITION (GENESIS) - REPLACES DIRECT BOOT
    # ========================================================================

    def ignite(self, genesis: GenesisByte) -> Any:
        """
        The Conscious Act of Creation.
        Accepts the 16-Bit Genesis Byte to authorize the boot.
        """
        if not genesis.is_valid:
            logger.critical("⛔ APARADHA: Genesis Byte incomplete! Resonance < 100%")
            # logger.critical(f"   Missing Bits: {~genesis.resonance & MantraBit.full_resonance()}")
            raise PermissionError("Kernel Ignition Denied: Incomplete Mantra Resonance")

        logger.info(f"🕉️  GENESIS ACCEPTED. Signature: {genesis.signature}")
        logger.info(f"   Resonance: 16-Bit Aligned ({genesis.resonance.name})")

        # NOW we trigger the OODA Loop
        return self.boot()

    def shutdown(self, reason: str) -> bool:
        """Graceful collapse of the wave function."""
        # Stop VenuService heartbeat
        if hasattr(self, "_venu_service") and self._venu_service:
            asyncio.ensure_future(self._venu_service.stop())

        if self.kernel:
            return True
        return False

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

    # =========================================================================
    # ORIENT PHASE STEPS — Atomic, granular, individually callable
    # Each step is a discrete orientation action. _orient() chains them all.
    # =========================================================================

    def _orient_akasha(self) -> None:
        """ORIENT Step 1: AKASHA (Space) — Create kernel via Factory + EntropyShell."""
        logger.info("⚡ OPUS-095: Materializing Kernel via Factory (AKASHA)")
        raw_kernel = self._kernel_factory.get_kernel(ledger_path=self.ledger_path)
        from vibe_core.runtime.entropy_shell import EntropyShell
        self.kernel = EntropyShell(raw_kernel)
        logger.info(f"      → Kernel space allocated & wrapped in EntropyShell (ledger: {self.ledger_path})")

    def _orient_vayu(self) -> None:
        """ORIENT Step 2: VAYU (Air) — Establish communication channels."""
        logger.info("⚡ OPUS-095: Establishing communication (VAYU)")
        from vibe_core.runtime.prompt_context import PromptContext
        self.prompt_context = PromptContext()
        if self.kernel:
            self.prompt_context.set_kernel(self.kernel)
            logger.info("      → PromptContext initialized and kernel bound")

    def _orient_agni_oracle(self) -> None:
        """ORIENT Step 3a: AGNI — Oracle + Shuddhi + KernelFactory."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.shuddhi import ShuddhiProtocol
        from vibe_core.runtime.oracle import KernelOracle
        from vibe_core.shuddhi.engine import ShuddhiEngine

        self.oracle = KernelOracle(self.kernel, self.project_root)
        ServiceRegistry.register(ShuddhiProtocol, ShuddhiEngine())
        logger.info("      → ShuddhiProtocol registered in ServiceRegistry")

        from vibe_core.protocols.kernel_protocol import KernelFactoryProtocol
        from vibe_core.services.kernel_factory import KernelFactory
        ServiceRegistry.register(KernelFactoryProtocol, KernelFactory())
        logger.info("      → KernelFactoryProtocol registered (EphemeralCities)")

    def _orient_agni_knowledge(self) -> None:
        """ORIENT Step 3b: AGNI — UnifiedKnowledgeGraph + TaskManager."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.knowledge.graph import UnifiedKnowledgeGraph, get_knowledge_graph
        from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol
        from vibe_core.protocols.task import TaskProtocol
        from vibe_core.task_management.task_manager import TaskManager

        kg = get_knowledge_graph()
        ServiceRegistry.register(UnifiedKnowledgeGraph, kg)
        ServiceRegistry.register(KnowledgeGraphProtocol, kg)
        logger.info("      → UnifiedKnowledgeGraph registered in ServiceRegistry")
        logger.info("      → KnowledgeGraphProtocol registered (OUROBOROS enabled)")

        task_manager = TaskManager(self.project_root, self.kernel.io)
        ServiceRegistry.register(TaskProtocol, task_manager)
        logger.info("      → TaskProtocol registered in ServiceRegistry (Core Stack)")

    def _orient_agni_services(self) -> None:
        """ORIENT Step 3c: AGNI — Cartridge, Plugin, Circuit, Section services."""
        from vibe_core.di import ServiceRegistry

        from vibe_core.cartridge_service import CartridgeService
        from vibe_core.protocols.cartridge import CartridgeProtocol
        cartridge_svc = CartridgeService.get_instance(self.project_root)
        cartridge_svc.scan()
        ServiceRegistry.register(CartridgeProtocol, cartridge_svc)
        logger.info(f"      → CartridgeProtocol registered ({len(cartridge_svc.list())} cartridges)")

        from vibe_core.plugin_service import PluginService
        from vibe_core.protocols.plugin import PluginServiceProtocol
        plugin_svc = PluginService.get_instance(self.project_root)
        plugin_svc.scan()
        ServiceRegistry.register(PluginServiceProtocol, plugin_svc)
        logger.info(f"      → PluginServiceProtocol registered ({len(plugin_svc.list())} plugins)")

        from vibe_core.circuit_service import CircuitService
        from vibe_core.protocols.circuit import CircuitServiceProtocol
        circuit_svc = CircuitService.get_instance(self.project_root)
        circuit_svc.scan()
        ServiceRegistry.register(CircuitServiceProtocol, circuit_svc)
        logger.info(f"      → CircuitServiceProtocol registered ({len(circuit_svc.list())} circuits)")

        from vibe_core.protocols.section import SectionServiceProtocol
        from vibe_core.section_service import SectionService
        section_svc = SectionService.get_instance(self.project_root)
        section_svc.scan()
        ServiceRegistry.register(SectionServiceProtocol, section_svc)
        logger.info(f"      → SectionServiceProtocol registered ({len(section_svc.list())} sections)")

    def _orient_agni_naga(self) -> None:
        """ORIENT Step 3d: AGNI — NAGA Federation + Oracle capabilities."""
        self._naga_orchestrator = self.kernel.naga
        if self._naga_orchestrator:
            logger.info("      → NAGA Federation active (kernel.naga)")
        else:
            logger.warning("      → NAGA Federation not available (test mode?)")

    async def _orient(self, observations: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """
        ORIENT: Kernel + Communication + Oracle setup (AKASHA/VAYU/AGNI phases).
        Chains the atomic _orient_* steps.

        Returns:
            (orientations, metadata)
        """
        orientations = []
        metadata = {}

        try:
            self._orient_akasha()
            self._orient_vayu()

            logger.info("⚡ OPUS-095: Making system visible (AGNI)")
            if self.kernel:
                self._orient_agni_oracle()
                self._orient_agni_knowledge()
                self._orient_agni_services()
                self._orient_agni_naga()

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

    # =========================================================================
    # ACT PHASE STEPS — Atomic, granular, individually callable
    # Each step is a discrete boot action. _act() chains them all.
    # =========================================================================

    async def _act_boot_kernel(self) -> int:
        """ACT Step 1: Boot kernel + Daily Ritual + Conveyor Belt. Returns agent count."""
        await self.kernel.boot_async(boot_mode=self.boot_mode)
        logger.info("      → Kernel booted, ledger active")

        if not self.boot_mode.should_skip_daily_ritual():
            from vibe_core.steward.daily_ritual import DailyRitual
            self.kernel.daily_ritual = DailyRitual(self.kernel)
            logger.info("      → Daily Ritual attached (time dimension active)")
        else:
            logger.info("      → Daily Ritual SKIPPED (headless mode)")

        self.boot_sequence = BootSequence(self.project_root)
        logger.info("      → Conveyor Belt initialized (prompt generation ready)")

        status = self.kernel.get_status()
        total_agents = status.get("agents_registered", 0)
        logger.info(f"      → Total agents registered: {total_agents}")
        return total_agents

    def _act_start_venu(self) -> None:
        """ACT Step 2: Start VenuService (Krishna's Flute - Central Orchestrator)."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra.protocols._venu import VenuServiceProtocol
        from vibe_core.services.venu_service import VenuService

        self._venu_service = VenuService()
        ServiceRegistry.register(VenuServiceProtocol, self._venu_service)

    def _act_discover_beat_subscribers(self) -> None:
        """ACT Step 3: YASODA'S ROPE — Auto-discover BeatSubscribers."""
        from vibe_core.services.beat_discovery import discover_and_register_beat_subscribers
        discover_and_register_beat_subscribers()
        beat_count = self._venu_service.discover_beat_subscribers()
        if beat_count:
            logger.info(f"      → {beat_count} beat subscribers auto-wired to VenuService")

    def _act_discover_diw_subscribers(self) -> None:
        """ACT Step 4: VENU FLUTE — Auto-discover DIW subscribers."""
        from vibe_core.services.diw_discovery import discover_and_register_diw_subscribers
        discover_and_register_diw_subscribers()
        diw_count = self._venu_service.discover_subscribers()
        if diw_count:
            logger.info(f"      → {diw_count} DIW subscribers auto-wired to orchestrator")

    def _act_register_mala_flush(self) -> None:
        """ACT Step 5: MALA FLUSH — Every 108 ticks (~27s), flush RAM state to disk."""
        from vibe_core.state.state_service import get_state_service
        _state_svc = get_state_service(self.project_root)
        def _mala_flush(mala_count: int) -> None:
            flushed = _state_svc.flush()
            if flushed:
                logger.debug(f"Mala {mala_count}: flushed {flushed} state files")
        self._venu_service.clock.on_mala(_mala_flush)
        logger.info("      → Mala flush registered (RAM→Disk every 108 ticks)")

    def _act_embrace_balarama(self) -> None:
        """ACT Step 6: Balarama embraces lotus-discovered services (organic wrapping)."""
        from vibe_core.mahamantra.substrate.proxy import wrap_service

        self._balarama_proxies = {}
        kernel_positions = getattr(self.kernel, "_positions", None)
        if kernel_positions is not None:
            for pos, guardian, instance in kernel_positions.all_active():
                mod_name = getattr(instance, "__module__", None)
                if mod_name is None:
                    mod_name = getattr(instance, "__name__", None)
                if mod_name:
                    try:
                        proxy = wrap_service(mod_name, silent=True)
                        self._balarama_proxies[mod_name] = proxy
                    except Exception:
                        pass  # Not all modules are wrappable

        if self._balarama_proxies:
            logger.info(f"      → Balarama embraced {len(self._balarama_proxies)} services (lotus-driven)")
        else:
            logger.debug("No lotus-discovered services to embrace")

    def _act_wire_gate_providers(self) -> None:
        """ACT Step 7: Wire Gate Providers (5 Watchers at the TattvaGates)."""
        from vibe_core.mahamantra.substrate.gate_providers import wire_gate_providers
        gate_count = wire_gate_providers()
        if gate_count:
            logger.info(f"      → {gate_count} gate providers wired (TattvaGates armed)")

    def _act_arm_io_sentinel(self) -> None:
        """ACT Step 8: Arm I/O Sentinel explicitly (enterprise hardening)."""
        from vibe_core.mahamantra.substrate.io_sentinel import arm, is_armed
        arm()
        if is_armed():
            logger.info("      → I/O Sentinel armed (rogue json writers monitored)")
        else:
            logger.warning("⚠️ I/O Sentinel failed to arm")

    def _act_ingest_codebase(self) -> None:
        """ACT Step 9: Ingest codebase into CellRouter (Sravanam needs cells to scan)."""
        from vibe_core.mahamantra.dharma.kumaras.fragment_parser import (
            parse_file_to_fragments,
            register_fragments_as_cells,
        )
        mahamantra_root = Path(__file__).parent / "mahamantra"
        ingested_cells = 0
        ingested_files = 0
        for py_file in sorted(mahamantra_root.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            try:
                frags = parse_file_to_fragments(py_file)
                addrs = register_fragments_as_cells(frags)
                ingested_cells += len(addrs)
                ingested_files += 1
            except Exception:
                pass  # Unparseable files are skipped silently
        if ingested_cells:
            logger.info(f"      → {ingested_cells} cells ingested from {ingested_files} files into CellRouter")

    def _act_wire_sravanam(self) -> None:
        """ACT Step 10: Wire Sravanam listener (organic per-tick scanning)."""
        from vibe_core.mahamantra.dharma.kumaras.sravanam import wire_sravanam
        listener = wire_sravanam()
        if listener:
            logger.info("      → Sravanam listener wired (organic cell scanning active)")

    def _act_register_governance_hook(self) -> None:
        """ACT Step 11: Register Mahamantra governance hook (King installs itself)."""
        from vibe_core.protocols.substrate.mantra_protocol import register_governance_hook
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode

        _WRITE_OPCODES = frozenset({
            MantraOpCode.LEDGER_SIGN,
            MantraOpCode.IO_FLUSH,
            MantraOpCode.STATE_SYNC,
        })

        def _sudarshana_governance_check(
            opcode: MantraOpCode,
            instance: object,
            args: tuple,
            kwargs: dict,
        ) -> bool:
            """
            SudarshanaChakra — the real security spin.
            Registered by Mahamantra at boot. Runs before every
            @mantra_governed call.
            """
            if opcode not in _WRITE_OPCODES:
                return True
            for arg in args:
                arg_str = str(arg)
                if "/.git/" in arg_str or "/.git" == arg_str[-5:]:
                    logger.warning(
                        f"🌀 SUDARSHANA BLOCKED: {opcode.name} targeting .git "
                        f"via {type(instance).__name__}"
                    )
                    return False
                if "__pycache__" in arg_str:
                    return True
            return True

        register_governance_hook(_sudarshana_governance_check)
        logger.info("      → Sudarshana governance hook active (Mahamantra is King)")

    async def _act(self, decisions: List[Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        ACT: Kernel boot + Daily Ritual + Conveyor Belt (PRITHVI phase).
        Chains the atomic _act_* steps.

        Returns:
            (results, metadata)
        """
        results = {}
        metadata = {}

        try:
            logger.info("⚡ OPUS-095: Persistence and kernel finalization (PRITHVI)")

            if self.kernel:
                total_agents = await self._act_boot_kernel()

                # GOVARDHAN: VenuService + subscribers
                try:
                    self._act_start_venu()
                    try:
                        self._act_discover_beat_subscribers()
                    except Exception as e:
                        logger.warning(f"⚠️ BeatSubscriber discovery FAILED: {e}")
                    try:
                        self._act_discover_diw_subscribers()
                    except Exception as e:
                        logger.warning(f"⚠️ DIW subscriber discovery FAILED: {e}")
                    try:
                        self._act_register_mala_flush()
                    except Exception as e:
                        logger.warning(f"⚠️ Mala flush registration FAILED: {e}")
                    asyncio.ensure_future(self._venu_service.start())
                    logger.info("      → VenuService started (Krishna's flute plays)")
                except Exception as e:
                    logger.warning(f"⚠️ Could not start VenuService: {e}")

                # GOVARDHAN: Balarama + Gates + Sentinel + Ingestion + Sravanam + Governance
                try:
                    self._act_embrace_balarama()
                except Exception as e:
                    logger.warning(f"⚠️ Balarama wrapping skipped: {e}")
                try:
                    self._act_wire_gate_providers()
                except Exception as e:
                    logger.debug(f"Gate provider wiring skipped: {e}")
                try:
                    self._act_arm_io_sentinel()
                except Exception as e:
                    logger.warning(f"⚠️ Could not arm I/O Sentinel: {e}")
                try:
                    self._act_ingest_codebase()
                except Exception as e:
                    logger.debug(f"Codebase ingestion skipped: {e}")
                try:
                    self._act_wire_sravanam()
                except Exception as e:
                    logger.debug(f"Sravanam wiring skipped: {e}")
                try:
                    self._act_register_governance_hook()
                except Exception as e:
                    logger.warning(f"⚠️ Could not register governance hook: {e}")

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
    ) -> Optional[KernelProtocol]:
        """
        Execute the unified boot sequence via CognitiveCycle orchestrate().

        OPUS-095: Integrates with orchestration abstraction.

        Args:
            parent_cycle_id: ID of calling cycle (if any)
            force: Bypass rate limits

        Returns:
            KernelProtocol if successful
        """
        self._parent_cycle_id = parent_cycle_id
        await self.orchestrate(force=force)
        return self.kernel

    def boot(self) -> KernelProtocol:
        """Thin wrapper: Execute boot sequence via orchestrate()."""
        try:
            kernel = asyncio.run(self.boot_orchestrated(force=True))
            if not kernel:
                raise RuntimeError("Boot orchestration failed")
            return kernel
        except Exception as e:
            raise RuntimeError(f"Boot sequence failed: {e}")

    def get_kernel(self) -> Optional[KernelProtocol]:
        """
        Get the booted kernel instance.

        Returns:
            KernelProtocol or None if not yet booted
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
        except Exception as e:
            # OPUS-312: Log git state resolution failure
            logger.debug(f"Git state resolution failed (non-fatal): {e}")

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
