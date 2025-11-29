"""
⚡ BOOT ORCHESTRATOR ⚡
======================

The unified boot sequence for Agent City OS.

PHOENIX VIMANA UNIFIED BOOT - Sarga Integration
-----------------------------------------------
This orchestrator now follows the Sarga (cosmic creation) sequence:
1. SHABDA (Sound) → Boot command received
2. AKASHA (Space) → Kernel memory allocated
3. VAYU (Air) → Communication channels established
4. AGNI (Fire) → Form/visibility (UI, capabilities)
5. JALA (Water) → Data streams flow (Knowledge Graph, context)
6. PRITHVI (Earth) → Persistence (Ledger, agents registered)

The system creates itself from nothing. Sound becomes form.

USAGE:
    from vibe_core.boot_orchestrator import BootOrchestrator

    orchestrator = BootOrchestrator()
    kernel = orchestrator.boot()

    # THE OPERATOR LOOP - This is where intelligence flows
    await orchestrator.run_with_operator()
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from steward.system_agents.discoverer.agent import Discoverer
from vibe_core.config import CityConfig
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.operator_adapter import (
    LocalLLMOperator,
    TerminalOperator,
    UniversalOperatorAdapter,
)
from vibe_core.protocols.operator_protocol import (
    GitState,
    Intent,
    IntentType,
    KernelStatusType,
    SystemContext,
)
from vibe_core.sarga import Element, get_sarga

logger = logging.getLogger("BOOT_ORCHESTRATOR")


class BootOrchestrator:
    """
    Unified boot orchestration for Agent City OS.

    Ensures consistent agent discovery and registration across all entry points.
    """

    def __init__(
        self,
        ledger_path: Optional[str] = None,
        project_root: Optional[Path] = None,
        config: Optional[CityConfig] = None,
    ):
        """
        Initialize the boot orchestrator.

        Args:
            ledger_path: Path to SQLite ledger (default: data/vibe_ledger.db)
            project_root: Project root directory (default: auto-detected)
            config: CityConfig instance (REQUIRED: Phoenix Config for agents)
        """
        self.ledger_path = ledger_path or "data/vibe_ledger.db"
        self.project_root = project_root or Path.cwd()
        self.config = config  # BLOCKER #0: Phoenix Config integration
        self.kernel: Optional[RealVibeKernel] = None
        self.discoverer: Optional[Discoverer] = None

        # Sarga phase components (initialized during boot)
        self.prompt_context = None  # VAYU phase
        self.oracle = None  # AGNI phase

        # Universal Operator Adapter - THE SOCKET
        self.operator_adapter: Optional[UniversalOperatorAdapter] = None
        self._running = False

    def boot(self) -> RealVibeKernel:
        """
        Execute the unified boot sequence via Sarga (cosmic creation).

        Sarga Phases:
        1. SHABDA (Sound) → Boot initiated
        2. AKASHA (Space) → Kernel created
        3. VAYU (Air) → Communication established
        4. AGNI (Fire) → Form rendered (capabilities)
        5. JALA (Water) → Data flows (Knowledge Graph, discovery)
        6. PRITHVI (Earth) → Persistence (agents registered, ledger ready)

        Returns:
            RealVibeKernel: Fully initialized kernel with all agents

        Raises:
            RuntimeError: If boot sequence fails
        """
        # Get global Sarga instance
        sarga = get_sarga()

        # Begin the cosmic creation
        sarga.begin_boot()

        # =================================================================
        # PHASE 1: SHABDA (Sound/Command) - Boot initiated
        # =================================================================
        sarga.register_phase_handler(Element.SHABDA, self._phase_shabda)
        if not sarga.execute_phase(Element.SHABDA):
            raise RuntimeError("Sarga SHABDA phase failed: Boot initiation error")

        # =================================================================
        # PHASE 2: AKASHA (Space/Memory) - Kernel created
        # =================================================================
        sarga.register_phase_handler(Element.AKASHA, self._phase_akasha)
        if not sarga.execute_phase(Element.AKASHA):
            raise RuntimeError("Sarga AKASHA phase failed: Kernel creation error")

        # =================================================================
        # PHASE 3: VAYU (Air/Communication) - Message bus + PromptContext
        # =================================================================
        sarga.register_phase_handler(Element.VAYU, self._phase_vayu)
        if not sarga.execute_phase(Element.VAYU):
            raise RuntimeError("Sarga VAYU phase failed: Communication setup error")

        # =================================================================
        # PHASE 4: AGNI (Fire/Form) - Capabilities visible
        # =================================================================
        sarga.register_phase_handler(Element.AGNI, self._phase_agni)
        if not sarga.execute_phase(Element.AGNI):
            raise RuntimeError("Sarga AGNI phase failed: Form rendering error")

        # =================================================================
        # PHASE 5: JALA (Water/Data) - Knowledge Graph + Discovery
        # =================================================================
        sarga.register_phase_handler(Element.JALA, self._phase_jala)
        if not sarga.execute_phase(Element.JALA):
            raise RuntimeError("Sarga JALA phase failed: Data stream error")

        # =================================================================
        # PHASE 6: PRITHVI (Earth/Persistence) - Agents + Ledger
        # =================================================================
        sarga.register_phase_handler(Element.PRITHVI, self._phase_prithvi)
        if not sarga.execute_phase(Element.PRITHVI):
            raise RuntimeError("Sarga PRITHVI phase failed: Persistence error")

        # Complete the cosmic creation
        sarga.complete_boot()

        # Print boot report
        logger.info(sarga.generate_boot_report())

        return self.kernel

    # =========================================================================
    # SARGA PHASE HANDLERS
    # =========================================================================

    def _phase_shabda(self) -> bool:
        """SHABDA: Sound - Boot command received, initiation logged."""
        logger.info("      → Boot command received")
        logger.info(f"      → Project root: {self.project_root}")
        logger.info(f"      → Ledger path: {self.ledger_path}")
        return True

    def _phase_akasha(self) -> bool:
        """AKASHA: Space - Create kernel, allocate memory."""
        try:
            self.kernel = RealVibeKernel(ledger_path=self.ledger_path)
            logger.info(f"      → Kernel space allocated (ledger: {self.ledger_path})")
            return True
        except Exception as e:
            logger.error(f"      → Kernel creation failed: {e}")
            return False

    def _phase_vayu(self) -> bool:
        """VAYU: Air - Establish communication channels."""
        try:
            # Initialize PromptContext (dynamic prompt generation)
            from vibe_core.runtime.prompt_context import PromptContext

            self.prompt_context = PromptContext()

            # Wire kernel to prompt context (late binding)
            if self.kernel:
                self.prompt_context.set_kernel(self.kernel)
                logger.info("      → PromptContext initialized and kernel bound")

            return True
        except Exception as e:
            logger.warning(f"      → PromptContext setup warning: {e}")
            # Non-fatal - communication still works via kernel
            return True

    def _phase_agni(self) -> bool:
        """AGNI: Fire - Make system visible (capabilities, UI)."""
        try:
            # Initialize KernelOracle (capability discovery)
            from vibe_core.runtime.oracle import KernelOracle

            if self.kernel:
                self.oracle = KernelOracle(self.kernel, self.project_root)
                capabilities = self.oracle.get_system_capabilities()
                logger.info(
                    f"      → Oracle active: {len(capabilities.get('tools', []))} tools, "
                    f"{len(capabilities.get('cartridges', []))} cartridges"
                )
            return True
        except Exception as e:
            logger.warning(f"      → Oracle setup warning: {e}")
            # Non-fatal - capabilities still work via kernel
            return True

    def _phase_jala(self) -> bool:
        """JALA: Water - Data streams flow (Knowledge Graph, discovery)."""
        try:
            # Load Knowledge Graph
            from vibe_core.knowledge.graph import get_knowledge_graph

            graph = get_knowledge_graph()
            logger.info(
                f"      → Knowledge loaded: {len(graph.nodes)} nodes, "
                f"{sum(len(e) for e in graph.edges.values())} edges"
            )

            # Register Discoverer (Genesis Agent)
            self.discoverer = Discoverer(kernel=self.kernel, config=self.config)
            self.kernel.register_agent(self.discoverer)
            logger.info("      → Discoverer (Genesis Agent) registered")

            # Discover all agents
            discovered_count = self.discoverer.discover_agents()
            logger.info(f"      → Discovered {discovered_count} agents")

            return True
        except Exception as e:
            logger.error(f"      → Data stream error: {e}")
            return False

    def _phase_prithvi(self) -> bool:
        """PRITHVI: Earth - Persistence (boot kernel, ledger ready)."""
        try:
            # Boot the kernel (finalizes manifests, ledger, scheduler)
            self.kernel.boot()
            logger.info("      → Kernel booted, ledger active")

            # Final status
            status = self.kernel.get_status()
            total_agents = status.get("agents_registered", 0)
            logger.info(f"      → Total agents registered: {total_agents}")

            return True
        except Exception as e:
            logger.error(f"      → Persistence error: {e}")
            return False

    def get_kernel(self) -> Optional[RealVibeKernel]:
        """
        Get the booted kernel instance.

        Returns:
            RealVibeKernel or None if not yet booted
        """
        return self.kernel

    def get_discoverer(self) -> Optional[Discoverer]:
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
            operator_type=self.operator_adapter.get_current_operator_type() if self.operator_adapter else None,
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

        while self._running:
            try:
                # 1. Build context from kernel state
                context = self._build_system_context()

                # 2. Get decision from operator (sends context, gets intent)
                intent = await self.operator_adapter.get_decision(context)

                # 3. Execute the intent
                result = await self._execute_intent(intent)

                # 4. Output result (if any)
                if result:
                    print(f"\n{result}\n")

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt - shutting down")
                self._running = False

            except Exception as e:
                logger.error(f"Operator loop error: {e}")
                # Don't crash - degradation will handle it

        logger.info("=" * 70)
        logger.info("🔴 AGENT CITY OS - SHUTDOWN COMPLETE")
        logger.info("=" * 70)

    def stop(self) -> None:
        """Stop the operator loop."""
        self._running = False


def quick_boot(ledger_path: Optional[str] = None) -> RealVibeKernel:
    """
    Quick boot helper for simple use cases.

    Args:
        ledger_path: Optional custom ledger path

    Returns:
        RealVibeKernel: Fully initialized kernel

    Example:
        kernel = quick_boot()
        # Use kernel...
    """
    orchestrator = BootOrchestrator(ledger_path=ledger_path)
    return orchestrator.boot()


async def boot_and_run(ledger_path: Optional[str] = None) -> None:
    """
    Boot the system AND start the operator loop.

    This is the main entry point for Agent City OS.

    Args:
        ledger_path: Optional custom ledger path

    Example:
        import asyncio
        asyncio.run(boot_and_run())
    """
    orchestrator = BootOrchestrator(ledger_path=ledger_path)
    orchestrator.boot()
    await orchestrator.run_with_operator()


if __name__ == "__main__":
    # Entry point: python -m vibe_core.boot_orchestrator
    logging.basicConfig(level=logging.INFO)
    asyncio.run(boot_and_run())
