"""
BRAHMA SERVICE - Creation & Genesis
===================================

Implements BrahmaProtocol (Creation/Genesis).
Wraps ManifestRegistry and CapabilityRegistry.

"Brahma is the first created being, who creates the rest."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xc238a5ea"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.protocols.capability import CapabilityModifyResult

from vibe_core.capability_registry import CapabilityRegistry
from vibe_core.ledger import VibeLedger
from vibe_core.manifest_registry import InMemoryManifestRegistry
from vibe_core.protocols.mahajanas.brahma import (
    AllocationResult,
    BrahmaProtocol,
    GenesisPhase,
    GenesisState,
)
from vibe_core.protocols.mahajanas.router import Mahajana

logger = logging.getLogger("BRAHMA_SERVICE")


class BrahmaService(BrahmaProtocol):
    """
    BrahmaService - The Creator.
    Manages system genesis, manifest registry, capability registry, and initial memory allocation.
    """

    def __init__(self, ledger: VibeLedger):
        self._phase = GenesisPhase.DORMANT
        self._manifest_registry = InMemoryManifestRegistry()
        self._capability_registry = CapabilityRegistry(ledger)
        self._wake_time: Optional[str] = None
        self._root_loaded = False
        self._allocated_bytes = 0
        self._creation_id: Optional[str] = None
        self._child_kernels: List[object] = []

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BRAHMA  # Position 1

    # =========================================================================
    # BrahmaProtocol Implementation
    # =========================================================================

    def wake(self, sovereign_id: str) -> bool:
        """SYS_WAKE: Wake the system."""
        if self._phase != GenesisPhase.DORMANT:
            logger.warning("🌅 BRAHMA: System already awake")
            return True

        logger.info(f"🌅 BRAHMA: Awakening system (Sovereign: {sovereign_id})")
        self._phase = GenesisPhase.AWAKENING
        self._wake_time = datetime.now().isoformat()
        self._creation_id = f"gen_{int(datetime.now().timestamp())}"
        return True

    def load_root(self, root_path: str) -> bool:
        """LOAD_ROOT: Load root configuration/manifests."""
        if self._phase not in [GenesisPhase.AWAKENING, GenesisPhase.LOADING]:
            logger.error("🌱 BRAHMA: Cannot load root - System not awakening")
            return False

        logger.info(f"🌱 BRAHMA: Loading root from {root_path}")
        self._phase = GenesisPhase.LOADING
        self._root_loaded = True
        return True

    def alloc_mem(self, size_bytes: int) -> AllocationResult:
        """ALLOC_MEM: Allocate memory (symbolic/tracking)."""
        if self._phase == GenesisPhase.DORMANT:
            return {
                "success": False,
                "allocated_bytes": 0,
                "address": "0x0",
                "error_message": "System dormant",
            }

        self._phase = GenesisPhase.ALLOCATING
        self._allocated_bytes += size_bytes
        logger.info(f"💾 BRAHMA: Allocated {size_bytes} bytes")

        if self._root_loaded:
            self._phase = GenesisPhase.ACTIVE

        return {
            "success": True,
            "allocated_bytes": size_bytes,
            "address": f"0x{size_bytes:x}",
            "error_message": "",
        }

    def get_phase(self) -> GenesisPhase:
        return self._phase

    def is_created(self) -> bool:
        return self._phase == GenesisPhase.ACTIVE

    def get_creation_timestamp(self) -> str:
        return self._wake_time or ""

    def get_state(self) -> GenesisState:
        return {
            "phase": self._phase.value,
            "wake_time": self._wake_time or "",
            "root_loaded": self._root_loaded,
            "memory_allocated_bytes": self._allocated_bytes,
            "creation_id": self._creation_id or "",
            "health": "healthy",
        }

    # =========================================================================
    # Capability Registry Delegation
    # =========================================================================

    def register_capabilities(self, agent_id: str, capabilities: List[str]) -> None:
        """Register agent capabilities."""
        self._capability_registry.register_agent(agent_id, capabilities)

    def has_capability(self, agent_id: str, capability: str) -> bool:
        """Check if agent has capability."""
        return self._capability_registry.has_capability(agent_id, capability)

    def grant_capability(
        self, agent_id: str, capabilities: List[str], granter_id: str, reason: Optional[str] = None
    ) -> CapabilityModifyResult:
        """Grant capabilities."""
        return self._capability_registry.grant(agent_id, capabilities, granter_id, reason)

    def revoke_capability(
        self, agent_id: str, capabilities: List[str], revoker_id: str, reason: Optional[str] = None
    ) -> CapabilityModifyResult:
        """Revoke capabilities."""
        return self._capability_registry.revoke(agent_id, capabilities, revoker_id, reason)

    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities for agent."""
        return sorted(list(self._capability_registry.get_capabilities(agent_id)))

    # =========================================================================
    # Registry Delegation (Legacy Support)
    # =========================================================================

    def register_manifest(self, manifest: object) -> None:
        self._manifest_registry.register(manifest)  # type: ignore

    def get_manifest(self, agent_id: str) -> Optional[object]:
        return self._manifest_registry.lookup(agent_id)

    def list_manifests(self) -> List[object]:
        return list(self._manifest_registry.list_all())

    def find_manifests_by_capability(self, capability: str) -> List[object]:
        return list(self._manifest_registry.find_by_capability(capability))

    # =========================================================================
    # 4D Hypercube / Ephemeral Operations
    # =========================================================================

    def spawn_child_kernel(
        self,
        config: object,
        parent_kernel: object,
        ledger_path: str = ":memory:",
    ) -> object:
        """
        🌀 SPAWN EPHEMERAL CITY (4D Hypercube Operation)
        Delegate creation to Brahma.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        logger.info(f"🌀 BRAHMA: Spawning ephemeral child kernel (parent: {id(parent_kernel)})")

        child = RealVibeKernel(
            ledger_path=ledger_path,
            config=config,  # type: ignore
            parent=parent_kernel,  # type: ignore
        )

        self._child_kernels.append(child)
        logger.info(f"🌀 BRAHMA: Child kernel spawned (id: {id(child)})")
        return child

    # =========================================================================
    # Agent Registration (The Primary Creation Logic)
    # =========================================================================

    def register_agent(self, kernel: object, agent: object, spawn_process: bool = True) -> None:
        """
        Register an agent and inject kernel reference.
        Delegated from Kernel to Brahma (Creation).
        """
        from vibe_core.agent_interface import AgentSystemInterface
        from vibe_core.lineage import LineageEventType

        agent_id = getattr(agent, "agent_id", "unknown")

        # OPUS-015/020: Check if agent requests process isolation
        execution_mode = getattr(agent, "_execution_mode", "thread")
        if execution_mode == "process":
            spawn_process = True
            logger.info(f"🔒 Agent '{agent_id}' forcing PROCESS isolation")

        # GOVERNANCE GATE: Let plugins decide
        plugins = getattr(kernel, "_plugins", [])
        for plugin in plugins:
            if hasattr(plugin, "on_agent_pre_register"):
                if not plugin.on_agent_pre_register(kernel, agent):
                    raise PermissionError(f"PLUGIN_VETO: Agent '{agent_id}' registration denied")

        # STEP 4: THE REGISTRATION
        agent_registry = getattr(kernel, "_agent_registry", {})
        agent_registry[agent_id] = agent

        # STEP 4.5: SECURITY - Register capabilities
        agent_caps = getattr(agent, "capabilities", [])
        self.register_capabilities(agent_id, agent_caps)

        # GOVERNANCE HOOK
        for plugin in plugins:
            if hasattr(plugin, "on_agent_registered"):
                plugin.on_agent_registered(kernel, agent_id)

        # STEP 4.6: INJECT KERNEL REFERENCE
        if hasattr(agent, "set_kernel"):
            agent.set_kernel(kernel)

        # PHASE 1.1: INJECT SYSTEM INTERFACE
        if hasattr(agent, "system"):
            agent.system = AgentSystemInterface(kernel, agent_id)  # type: ignore

        # OPUS-009: PRAKRITI - Load or create persona
        prakriti = getattr(kernel, "prakriti", None)
        if prakriti and hasattr(prakriti, "personas"):
            persona = prakriti.personas.get(agent_id)
            if not persona:
                manifest = getattr(agent, "get_manifest", lambda: None)()
                if manifest:
                    persona = prakriti.personas.create_default(
                        agent_id=agent_id,
                        display_name=getattr(manifest, "name", agent_id),
                        dharma=getattr(manifest, "description", ""),
                    )
            if hasattr(agent, "persona"):
                agent.persona = persona

        # Phase 5: Record in Lineage
        if hasattr(kernel, "lineage"):
            manifest = getattr(agent, "get_manifest", lambda: None)()
            if manifest:
                kernel.lineage.add_block(
                    event_type=LineageEventType.AGENT_REGISTERED,
                    agent_id=agent_id,
                    data={
                        "name": getattr(manifest, "name", ""),
                        "version": getattr(manifest, "version", ""),
                        "author": getattr(manifest, "author", ""),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

        logger.info(f"🛡️  ✅ BRAHMA: Agent '{agent_id}' registered ({'process' if spawn_process else 'thread'}).")

    # =========================================================================
    # Discovery & Vision (Brahma sees the Registry)
    # =========================================================================

    def get_capabilities(self, kernel: object) -> Dict[str, object]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        agent_registry = getattr(kernel, "_agent_registry", {})
        plugins = getattr(kernel, "_plugins", [])

        return {
            "version": "1.0",
            "kernel_status": str(getattr(kernel, "status", "UNKNOWN")),
            "registered_agents": list(agent_registry.keys()),
            "plugins_loaded": [getattr(p, "plugin_id", "unknown") for p in plugins],
        }

    def load_plugins(self, kernel: object) -> Tuple[Dict[str, object], Dict[str, object]]:
        """
        Discover and load plugins.
        Delegated from Kernel to Brahma (The Creator).
        """
        import os
        from pathlib import Path

        from vibe_core.plugin_loader import PluginLoader
        from vibe_core.loaders.manifest_registry import ManifestRegistry

        # OPUS-307 Phase F: Ensure manifests are scanned
        ManifestRegistry.scan_all()

        custom_paths_env = os.environ.get("VIBE_PLUGIN_PATH", "")
        if custom_paths_env:
            scan_paths = [Path(p.strip()) for p in custom_paths_env.split(":") if p.strip()]
            return PluginLoader.discover_and_load(scan_paths=scan_paths)
        else:
            return PluginLoader.discover_from_registry()

    def bootstrap(self, kernel: object, config: object) -> None:
        """
        Bootstrap the kernel state and Sangha (Plugins).
        Delegated from Kernel to Brahma (Genesis).
        """
        # 1. BLUEPRINTS - Brahma stores the patterns of existence
        setattr(kernel, "_agent_registry_blueprint", lambda: {})

        # 2. PLUGINS - Discover and load the Sangha
        plugins_map, metadata = self.load_plugins(kernel)
        setattr(kernel, "_plugins_map", plugins_map)
        setattr(kernel, "_plugin_metadata", metadata)

        # Sort and store plugins
        plugins = sorted(
            plugins_map.values(),
            key=lambda p: int(getattr(p, "priority", 50)),
        )
        setattr(kernel, "_plugins", plugins)

        # 3. BOOT - Wake the Plugins
        self.boot_plugins(kernel, plugins)

        logger.info(f"✨ BRAHMA: Bootstrap complete. Community size: {len(plugins)}")

    async def boot_orchestration(self, kernel: object, boot_mode: Any) -> None:
        """🚀 THE ASYNC BOOT ORCHESTRATION (Genesis). Delegated from Kernel."""
        import asyncio
        import time

        from vibe_core.lineage import LineageEventType

        # Set boot time and status
        setattr(kernel, "_status", "BOOTING")
        setattr(kernel, "_boot_time", time.time())

        logger.info(f"⚙️  BRAHMA: Booting system async (mode: {boot_mode.value})")

        # Phase 5: Record Kernel Boot in Parampara
        if hasattr(kernel, "lineage"):
            kernel.lineage.add_block(
                event_type=LineageEventType.KERNEL_BOOT,
                agent_id=None,
                data={"version": "2.0.0", "boot_mode": boot_mode.value},
            )

        # Register manifests
        agent_registry = getattr(kernel, "_agent_registry", {})
        for agent_id, agent in agent_registry.items():
            if hasattr(agent, "get_manifest"):
                manifest = agent.get_manifest()
                self._manifest_registry.register(manifest)
                logger.info(f"   📜 BRAHMA: Registered {agent_id}")

        setattr(kernel, "_status", "RUNNING")  # KernelStatus.RUNNING
        logger.info("✅ BRAHMA: KERNEL RUNNING (ASYNC)")

        # [OPUS-027] PRAKRITI ACTIVATION (The Awakening)
        prakriti = getattr(kernel, "prakriti", None)
        if prakriti:
            try:
                prakriti.begin_session()
                prakriti.sync_ledger_git(strategy="git_wins")
                if prakriti.is_dirty:
                    prakriti.recover_from_crash()
            except Exception as e:
                logger.error(f"❌ BRAHMA: Prakriti Boot Failure: {e}")

        # 🍎 ASYNC PERSISTENCE (ADR-204)
        try:
            from vibe_core.state.state_service import get_state_service

            workspace = getattr(kernel, "_workspace", None)
            ss = get_state_service(workspace)
            ss.start_background_worker()
        except Exception as e:
            logger.warning(f"⚠️ BRAHMA: Failed to start background persistence: {e}")

        # PULSE: Write initial snapshot on boot
        if hasattr(kernel, "_pulse"):
            await kernel._pulse()  # Accessing internal pulse wrapper in kernel impl

        # Phase 18: Gateway as Task
        if not boot_mode.should_skip_gateway():
            if hasattr(kernel, "_run_gateway_async"):
                task = asyncio.create_task(kernel._run_gateway_async())
                setattr(kernel, "_gateway_task", task)
                logger.info("🌐 BRAHMA: Network Gateway task started")
            else:
                logger.warning("🌐 BRAHMA: Gateway async runner missing")
        else:
            logger.info("🚫 BRAHMA: Network Gateway SKIPPED (headless mode)")

    def terminate_agent(self, kernel: object, agent_id: str, reason: str = "Unknown") -> bool:
        """Terminate agent. Delegated from Kernel."""
        agent_registry = getattr(kernel, "_agent_registry", {})
        if agent_id not in agent_registry:
            return False

        logger.warning(f"🔪 BRAHMA: Terminating {agent_id} ({reason})")

        # 1. Stop process
        proc_mgr = getattr(kernel, "process_manager", None)
        if proc_mgr and agent_id in proc_mgr.processes:
            proc_mgr.processes[agent_id].process.terminate()
            del proc_mgr.processes[agent_id]

        # 2. Cleanup
        del agent_registry[agent_id]
        self.revoke_capability(agent_id, ["*"], "KERNEL", reason)

        return True

    def can_modify_capability(self, kernel: object, actor_id: str, target_id: str) -> bool:
        """Capability permission gate."""
        enforcer = getattr(kernel, "_capability_enforcer", None)
        if enforcer:
            return bool(enforcer.can_revoke(actor_id, target_id))
        return actor_id == "kernel"

    def boot_plugins(self, kernel: object, plugins: List[object]) -> None:
        """Boot all plugins in priority order."""
        for plugin in plugins:
            if hasattr(plugin, "on_boot"):
                try:
                    plugin.on_boot(kernel)
                except Exception as e:
                    logger.error(f"❌ BRAHMA: Plugin boot failed: {e}")
