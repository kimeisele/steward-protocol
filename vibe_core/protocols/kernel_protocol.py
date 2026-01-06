"""
KernelProtocol - The Sovereign Interface

PHASE 0 OF OPERATION LASAGNE: The Constitutional Break

This protocol defines WHAT the kernel does, not HOW it does it.
All plugins MUST depend on this protocol, NOT on RealVibeKernel.

Dependency Inversion Principle (SOLID 'D'):
    HIGH-LEVEL (Kernel) and LOW-LEVEL (Plugins) both depend on ABSTRACTION.

Current Problem:
    Kernel -> imports -> Plugin
    Plugin -> imports -> Kernel
    = Circular Dependency = Distributed Monolith = MAYAVAD

Solution:
    Kernel -> implements -> KernelProtocol
    Plugin -> depends on -> KernelProtocol
    = Clean Architecture = Dependency Inversion = VAISHNAVA

Usage in Plugins:
    # WRONG (creates circular dependency):
    from vibe_core.kernel_impl import RealVibeKernel
    def on_boot(self, kernel: RealVibeKernel): ...

    # CORRECT (depends on abstraction):
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    def on_boot(self, kernel: KernelProtocol): ...
"""

from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

from vibe_core.protocols.kernel_types import (
    CapabilitiesReport,
    CapabilityResult,
    KernelStatus,
    KernelStatusReport,
    SystemStatusReport,
    TaskResult,
)

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService
    from vibe_core.lineage import LineageChain
    from vibe_core.phoenix.config import PhoenixConfig
    from vibe_core.protocols.agent import AgentManifest, VibeAgent
    from vibe_core.protocols.cognition import (
        CognitiveKernelProtocol,
        CognitiveResult,
        SignedOperatorInput,
    )
    from vibe_core.protocols.economy import BankProtocol, VaultProtocol
    from vibe_core.protocols.event import EventBusProtocol
    from vibe_core.protocols.ledger import VibeLedger
    from vibe_core.protocols.manifestation import ManifestationProtocol
    from vibe_core.protocols.state import PrakritiProtocol
    from vibe_core.scheduling import Task


@runtime_checkable
class KernelProtocol(Protocol):
    """
    The Sovereign Interface - What every Kernel MUST provide.

    This is the contract between the Kernel and all Plugins/Services.
    RealVibeKernel implements this protocol.

    Plugins type-hint against this, never against RealVibeKernel.
    """

    # =========================================================================
    # CORE PROPERTIES (Read-Only State)
    # =========================================================================

    @property
    def agent_registry(self) -> Dict[str, "VibeAgent"]:
        """Get all registered agents {agent_id: agent}. READ-ONLY."""
        ...

    @property
    def status(self) -> KernelStatus:
        """Get kernel status (STOPPED, BOOTING, RUNNING, HALTED, SHUTTING_DOWN)."""
        ...

    @property
    def config(self) -> "PhoenixConfig":
        """Get kernel configuration."""
        ...

    @property
    def ledger(self) -> "VibeLedger":
        """Get the immutable event ledger."""
        ...

    # =========================================================================
    # AGENT LIFECYCLE (The Gate)
    # =========================================================================

    def register_agent(self, agent: "VibeAgent", spawn_process: bool = True) -> None:
        """
        Register an agent with the kernel.

        THE GATE: Constitutional Oath verification happens here.
        """
        ...

    def terminate_agent(self, agent_id: str, reason: str = "Unknown") -> bool:
        """
        Terminate an agent and free resources.

        THE KNIFE: Durvasa Protocol.
        """
        ...

    def get_agent_manifest(self, agent_id: str) -> Optional["AgentManifest"]:
        """Get manifest for an agent."""
        ...

    # =========================================================================
    # TASK SCHEDULING
    # =========================================================================

    def submit_task(self, task: "Task") -> str:
        """Submit a task to the scheduler. Returns task_id."""
        ...

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result of a completed task."""
        ...

    # =========================================================================
    # CAPABILITY MANAGEMENT
    # =========================================================================

    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get current capabilities for an agent."""
        ...

    def revoke_capability(
        self,
        agent_id: str,
        capabilities: List[str],
        revoker_id: str,
        reason: Optional[str] = None,
    ) -> CapabilityResult:
        """Revoke capabilities from an agent."""
        ...

    def grant_capability(
        self,
        agent_id: str,
        capabilities: List[str],
        granter_id: str,
        reason: Optional[str] = None,
    ) -> CapabilityResult:
        """Grant capabilities to an agent."""
        ...

    # =========================================================================
    # EVENT SYSTEM (Phase 6: Direct EventBus exposure)
    # =========================================================================

    @property
    def event_bus(self) -> "EventBusProtocol":
        """
        Direct access to the EventBus.

        PHASE 6 OPERATION LASAGNE: No more wrapper methods.
        Plugins use event_bus.subscribe(), event_bus.emit() directly.

        Usage:
            # Subscribe to events
            kernel.event_bus.subscribe(my_callback, "agent.born")

            # Emit events
            await kernel.event_bus.emit(event)
        """
        ...

    # =========================================================================
    # COGNITIVE LAYER (OPUS-309)
    # =========================================================================

    def register_cognitive(self, cognitive: "CognitiveKernelProtocol") -> None:
        """Register a cognitive plugin for operator input processing."""
        ...

    async def process_operator_input(
        self,
        input_text: str,
        session_id: Optional[str] = None,
        signed_input: Optional["SignedOperatorInput"] = None,
    ) -> "CognitiveResult":
        """Process natural language input from operator."""
        ...

    def get_cognitive_capabilities(self) -> List[str]:
        """Get capabilities of the registered cognitive layer."""
        ...

    # =========================================================================
    # STATE & OBSERVABILITY (GAD-000)
    # =========================================================================

    def get_status(self) -> KernelStatusReport:
        """Get full kernel status."""
        ...

    def get_system_status(self) -> SystemStatusReport:
        """GAD-000: AI-readable system state."""
        ...

    def get_capabilities(self) -> CapabilitiesReport:
        """GAD-000: Machine-readable capability discovery."""
        ...

    def get_ledger_hash(self) -> str:
        """Get cryptographic hash of ledger state."""
        ...

    # =========================================================================
    # SERVICES (Injected)
    # =========================================================================

    @property
    def io(self) -> "KernelIOService":
        """Get the I/O service for file operations."""
        ...

    @property
    def manifestation(self) -> "ManifestationProtocol":
        """Get the manifestation service for Markdown rendering."""
        ...

    @property
    def prakriti(self) -> "PrakritiProtocol":
        """Get the Prakriti state engine."""
        ...

    @property
    def lineage(self) -> "LineageChain":
        """Get the Parampara lineage chain."""
        ...

    # =========================================================================
    # ECONOMY (ServiceRegistry Access)
    # =========================================================================

    def get_bank(self) -> "BankProtocol":
        """Get CivicBank via ServiceRegistry."""
        ...

    def get_vault(self) -> "VaultProtocol":
        """Get CivicVault via ServiceRegistry."""
        ...


@runtime_checkable
class KernelFactoryProtocol(Protocol):
    """
    Factory for creating Kernel instances.

    Used by EphemeralCities to spawn child kernels WITHOUT
    importing RealVibeKernel directly.

    Usage:
        # In plugin (CORRECT):
        factory = ServiceRegistry.get(KernelFactoryProtocol)
        child = factory.create_kernel(config)

        # NOT this (WRONG - creates circular dependency):
        from vibe_core.kernel_impl import RealVibeKernel
        child = RealVibeKernel(config=config)
    """

    def create_kernel(
        self,
        config: "PhoenixConfig",
        ledger_path: str = ":memory:",
        parent: Optional[KernelProtocol] = None,
        load_plugins: bool = True,
        test_mode: bool = False,
    ) -> KernelProtocol:
        """
        Create a new kernel instance.

        Args:
            config: PhoenixConfig for the kernel
            ledger_path: Path to ledger (":memory:" for ephemeral)
            parent: Optional parent kernel (for child kernels)
            load_plugins: Whether to auto-load plugins
            test_mode: Whether to run in test mode

        Returns:
            A kernel implementing KernelProtocol
        """
        ...
