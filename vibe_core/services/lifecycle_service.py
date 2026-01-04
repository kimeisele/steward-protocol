"""
LifecycleService - Kernel Boot/Shutdown/Tick Logic

GEMINI DIRECTIVE: "A CEO (Kernel) does not screw bolts at the assembly line."

This service owns all process lifecycle logic:
- boot() / boot_async()
- shutdown() / shutdown_async()
- tick_async()
- run_forever()

The kernel becomes a CONTAINER for services, not a God Object.

Usage:
    # In kernel __init__:
    self._lifecycle = LifecycleService(self)

    # Kernel delegates:
    async def boot_async(self, mode):
        await self._lifecycle.boot_async(mode)
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vibe_core.boot_mode import BootMode
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("LIFECYCLE")


class LifecycleService:
    """
    Kernel lifecycle management - boot, shutdown, tick, run.

    Extracted from kernel to reduce God Object pattern.
    The kernel holds state, this service drives the lifecycle.
    """

    def __init__(self, kernel: "KernelProtocol"):
        """
        Initialize with kernel reference.

        Args:
            kernel: The kernel instance (for state access)
        """
        self._kernel = kernel
        self._last_pulse_time = 0.0
        self._gateway_task: Optional[asyncio.Task] = None
        logger.info("🔄 LifecycleService initialized")

    # =========================================================================
    # BOOT
    # =========================================================================

    def boot(self, boot_mode: "BootMode | None" = None) -> None:
        """
        Boot the kernel synchronously (backward compatibility wrapper).

        For new code, prefer boot_async() in async contexts.
        """
        import asyncio

        from vibe_core.boot_mode import BootMode

        if boot_mode is None:
            boot_mode = BootMode.FULL

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures

            future = concurrent.futures.Future()

            async def _boot_and_signal():
                try:
                    await self.boot_async(boot_mode)
                    future.set_result(None)
                except Exception as e:
                    future.set_exception(e)

            loop.create_task(_boot_and_signal())
            future.result(timeout=60)
        except RuntimeError:
            asyncio.run(self.boot_async(boot_mode))

    async def boot_async(self, boot_mode: "BootMode | None" = None) -> None:
        """
        🚀 ASYNC BOOT - Register manifests, activate Prakriti, start Gateway.
        """
        from vibe_core.boot_mode import BootMode
        from vibe_core.lineage import LineageEventType
        from vibe_core.protocols.ledger import KernelStatus

        if boot_mode is None:
            boot_mode = BootMode.FULL

        self._kernel._status = KernelStatus.BOOTING
        self._kernel._boot_time = time.time()
        logger.info(f"⚙️  KERNEL BOOTING ASYNC... (mode: {boot_mode.value})")

        # Record boot in Parampara
        self._kernel.lineage.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id=None,
            data={
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "agents_registered": len(self._kernel.agent_registry),
                "boot_mode": boot_mode.value,
            },
        )

        # Register all agent manifests
        for agent_id, agent in self._kernel.agent_registry.items():
            try:
                if hasattr(agent, "get_manifest"):
                    manifest = agent.get_manifest()
                    self._kernel.manifest_registry.register(manifest)
                    logger.info(f"   📜 {agent_id}: {manifest.description}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to register manifest for {agent_id}: {e}")

        self._kernel._status = KernelStatus.RUNNING
        logger.info("✅ KERNEL RUNNING (ASYNC)")

        # Prakriti activation
        try:
            self._kernel.prakriti.begin_session()
            self._kernel.prakriti.sync_ledger_git(strategy="git_wins")
            if self._kernel.prakriti.is_dirty:
                self._kernel.prakriti.recover_from_crash()
        except Exception as e:
            logger.error(f"❌ Prakriti Boot Failure: {e}")

        # Start background persistence
        try:
            from vibe_core.state.state_service import get_state_service

            workspace = getattr(self._kernel, "_workspace", None)
            ss = get_state_service(workspace)
            ss.start_background_worker()
        except Exception as e:
            logger.warning(f"⚠️  Failed to start background persistence: {e}")

        # Initial pulse
        await self._kernel._pulse()

        # Start gateway task
        if boot_mode.should_skip_gateway():
            logger.info("🚫 Network Gateway SKIPPED (headless mode)")
            self._gateway_task = None
        else:
            self._gateway_task = asyncio.create_task(self._run_gateway_async())
            logger.info("🌐 Network Gateway task started")

    # =========================================================================
    # RUN LOOP
    # =========================================================================

    async def run_forever(self) -> None:
        """
        🔄 MAIN KERNEL LOOP - Runs tick_async() at 100ms intervals.
        """
        from vibe_core.protocols.ledger import KernelStatus

        logger.info("🔄 Entering Unified Async Kernel loop...")
        try:
            while self._kernel._status == KernelStatus.RUNNING:
                await self.tick_async()
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("🛑 Kernel loop cancelled")
        finally:
            if self._kernel._status == KernelStatus.RUNNING:
                await self.shutdown_async("Loop terminated")

    async def tick_async(self) -> None:
        """
        💓 ASYNC TICK - Drives heartbeat, scheduler, and event emission.
        """
        from vibe_core.protocols.ledger import KernelStatus

        self._kernel.enforce_entropy_limits()

        if self._kernel._status != KernelStatus.RUNNING:
            return

        # Plugin Hook: Pre-Tick
        for plugin in self._kernel._plugins:
            plugin.on_tick_pre(self._kernel)

        task = self._kernel._scheduler.next_task()

        if not task:
            # Idle Pulse
            if time.time() - self._last_pulse_time >= 5.0:
                await self._kernel._pulse()
                self._last_pulse_time = time.time()
        else:
            await self._execute_task(task)

        # Native heartbeat
        from vibe_core.protocols.event import Event, EventType

        await self._kernel.event_bus.emit(
            Event(event_type=EventType.KERNEL_TICK, agent_id="kernel", message="Kernel heartbeat tick")
        )

    async def _execute_task(self, task) -> None:
        """Execute a single task from the scheduler."""
        agent = self._kernel.agent_registry.get(task.agent_id)
        if not agent:
            error = f"Agent {task.agent_id} not found"
            logger.error(f"❌ {error}")
            self._kernel.ledger.record_failure(task, error)
            return

        try:
            self._kernel.ledger.record_start(task)

            # Check for isolated process
            has_process = (
                self._kernel.process_manager
                and task.agent_id in self._kernel.process_manager.processes
                and self._kernel.process_manager.processes[task.agent_id].process.is_alive()
            )

            if has_process:
                self._kernel.process_manager.send_task(task.agent_id, task)
            else:
                # Execute natively
                if asyncio.iscoroutinefunction(agent.process):
                    result = await agent.process(task)
                else:
                    result = agent.process(task)

                self._kernel.ledger.record_completion(task, result)

                for plugin in self._kernel._plugins:
                    plugin.on_task_completed(self._kernel, task.task_id, result)

            # Maintenance
            await self._kernel._pulse()
            self._kernel._check_system_health()
            if self._kernel.process_manager:
                self._kernel.process_manager.check_health()
            self._kernel._process_ipc_events()
            self._kernel._sync_resource_quotas()

            for plugin in self._kernel._plugins:
                plugin.on_tick_post(self._kernel)

            # Manifestation tick
            self._kernel.manifestation.tick()

        except Exception as e:
            from vibe_core.faults import kernel_fault

            error = str(kernel_fault("task_tick_async", str(e)))
            logger.exception(f"❌ Task {task.task_id} failed: {error}")
            self._kernel.ledger.record_failure(task, error)
            for plugin in self._kernel._plugins:
                plugin.on_task_failed(self._kernel, task.task_id, error)

    async def _run_gateway_async(self) -> None:
        """Runs the NetworkGateway as an asyncio task."""
        if self._kernel.gateway is None:
            logger.warning("🌐 Gateway not available (sangha_network plugin not loaded)")
            return
        try:
            await self._kernel.gateway.start()
        except Exception as e:
            logger.error(f"🌐 Gateway task crashed: {e}")

    # =========================================================================
    # SHUTDOWN
    # =========================================================================

    async def shutdown_async(self, reason: str = "User shutdown") -> None:
        """
        🛑 ASYNC SHUTDOWN - Stop gateway, preserve state, cleanup.
        """
        from vibe_core.ledger import SQLiteLedger
        from vibe_core.lineage import LineageEventType
        from vibe_core.protocols.ledger import KernelStatus

        logger.critical(f"🛑 KERNEL SHUTTING DOWN ASYNC: {reason}")

        # Record shutdown
        if hasattr(self._kernel, "lineage"):
            self._kernel.lineage.add_block(
                event_type=LineageEventType.KERNEL_SHUTDOWN,
                agent_id=None,
                data={"reason": reason},
            )
            self._kernel.lineage.close()

        # Preserve Prakriti state
        try:
            if hasattr(self._kernel, "prakriti"):
                self._kernel.prakriti.end_session()
        except Exception as e:
            logger.error(f"❌ State preservation failed: {e}")

        # Stop background persistence
        try:
            from vibe_core.state.state_service import get_state_service

            workspace = getattr(self._kernel, "_workspace", None)
            ss = get_state_service(workspace)
            if ss._worker_task:
                ss._worker_task.cancel()
                logger.info("🛑 StateService: Background scribe stopped.")
        except Exception as e:
            logger.warning(f"⚠️ KERNEL: StateService shutdown failed: {e}")

        # Plugin Hook
        for plugin in self._kernel._plugins:
            plugin.on_shutdown(self._kernel)

        self._kernel._status = KernelStatus.STOPPED

        # Cancel Gateway
        if self._gateway_task:
            self._gateway_task.cancel()
            try:
                await self._gateway_task
            except asyncio.CancelledError:
                pass

        # Cleanup processes
        if self._kernel.process_manager:
            self._kernel.process_manager.shutdown()
        if isinstance(self._kernel._ledger, SQLiteLedger):
            self._kernel._ledger.close()

    def shutdown(self, reason: str = "User shutdown") -> None:
        """
        🛑 SYNC SHUTDOWN - Wrapper for shutdown_async.
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.shutdown_async(reason))
        except RuntimeError:
            asyncio.run(self.shutdown_async(reason))


__all__ = ["LifecycleService"]
