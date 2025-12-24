"""
KernelOps - Isolated Kernel Operations

Extracted from kernel_impl.py to reduce kernel size.
Contains self-contained operations that don't need tight kernel coupling:
- Health monitoring (Auditor/Immune System)
- Resource quota synchronization
- Repo access granting
- Pulse (heartbeat/snapshot)
"""

import json
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("KERNEL_OPS")


def _check_eventbus_zombies(kernel: "RealVibeKernel") -> None:
    """
    🐍 VRITRASURA DETECTION: Check EventBus for zombie subscribers.

    A zombie subscriber receives events but never processes them,
    potentially hoarding resources and causing backpressure.

    When zombies are detected, this function:
    1. Logs the detection
    2. Registers threat with Narasimha (escalates to kill-switch)

    The EventBus tracks subscriber health via SubscriberMetrics.
    This function bridges detection → enforcement.
    """
    import time

    from vibe_core.narasimha import ThreatIndicator, ThreatLevel, get_narasimha

    try:
        # Get EventBus status (includes zombie detection)
        bus_status = kernel._event_bus.get_status()

        zombies = bus_status.get("zombie_subscribers", [])
        stalled = bus_status.get("stalled_handlers", [])

        if not zombies and not stalled:
            return  # All healthy

        narasimha = get_narasimha()

        # Process zombie subscribers (hoarding messages without ACK)
        for zombie in zombies:
            callback_id = zombie.get("callback_id", "unknown")
            ack_rate = zombie.get("ack_rate", 0)
            events_pending = zombie.get("events_sent", 0) - zombie.get("events_completed", 0)

            logger.warning(
                f"🐍 VRITRASURA DETECTED: Zombie subscriber '{callback_id}' "
                f"(ACK rate: {ack_rate:.1%}, pending: {events_pending})"
            )

            # Register threat with Narasimha
            # Zombie behavior is ORANGE (serious) - escalates to RED after 3 detections
            indicator = ThreatIndicator(
                indicator_type="resource_hoarding",
                agent_id=callback_id,
                severity=ThreatLevel.ORANGE,
                description=f"Zombie subscriber detected: {ack_rate:.1%} ACK rate, {events_pending} events pending",
                evidence={
                    "callback_id": callback_id,
                    "ack_rate": ack_rate,
                    "events_pending": events_pending,
                    "detection_source": "eventbus_health_check",
                },
                timestamp=time.time(),
            )
            narasimha.register_threat(indicator)

        # Process stalled handlers (haven't completed anything recently)
        for handler in stalled:
            callback_id = handler.get("callback_id", "unknown")
            stall_seconds = handler.get("seconds_since_complete", 0)
            events_pending = handler.get("events_pending", 0)

            logger.warning(
                f"🐍 VRITRASURA DETECTED: Stalled handler '{callback_id}' "
                f"(stalled: {stall_seconds:.0f}s, pending: {events_pending})"
            )

            # Stalled handlers are more severe - they block throughput
            severity = ThreatLevel.ORANGE if stall_seconds < 120 else ThreatLevel.RED

            indicator = ThreatIndicator(
                indicator_type="throughput_strangulation",
                agent_id=callback_id,
                severity=severity,
                description=f"Stalled handler: {stall_seconds:.0f}s without completion, {events_pending} events pending",
                evidence={
                    "callback_id": callback_id,
                    "seconds_stalled": stall_seconds,
                    "events_pending": events_pending,
                    "detection_source": "eventbus_health_check",
                },
                timestamp=time.time(),
            )
            narasimha.register_threat(indicator)

        # Log summary
        total_issues = len(zombies) + len(stalled)
        if total_issues > 0:
            logger.warning(f"🐍 VRITRASURA: {total_issues} subscriber health issue(s) reported to Narasimha")

    except Exception as e:
        logger.error(f"❌ EventBus zombie check failed: {e}")


def check_system_health(kernel: "RealVibeKernel") -> None:
    """
    🛡️ IMMUNE SYSTEM WATCHDOG (Incremental)

    Called after every task execution.
    If Auditor detects CRITICAL_VIOLATION -> Kernel shuts down.

    OPUS-208: Updated to be incremental (O(1)) instead of full scan (O(N)).
    Uses persistent trust anchor to maintain hash chain integrity across checks.

    VRITRASURA FIX: Also checks EventBus for zombie subscribers and wires
    detected zombies to Narasimha kill-switch.
    """
    # Import here to avoid circular imports
    try:
        from vibe_core.cartridges.system.auditor.tools.invariant_tool import (
            InvariantSeverity,
        )

        AUDITOR_AVAILABLE = True
    except ImportError:
        AUDITOR_AVAILABLE = False

    # VRITRASURA FIX: Check EventBus for zombie subscribers
    _check_eventbus_zombies(kernel)

    if not AUDITOR_AVAILABLE or not kernel._auditor:
        return

    try:
        # OPUS-208: 1. Load anchor from DB meta-table (avoids full scan on restart)
        # Tuple: (last_id, last_trusted_hash)
        # Default to (0, "0"*64) if no anchor exists (genesis state)
        anchor = kernel._ledger.get_meta("health_anchor") or (0, "0" * 64)
        last_id, last_hash = anchor

        # OPUS-208: 2. Query ONLY new events
        new_events = kernel._ledger.get_events_since(last_id)

        if not new_events:
            # No new events, nothing to verify
            return

        # OPUS-208: 3. Verify chain continuity using the anchor hash
        # If verify_incremental exists on auditor, use it. Otherwise fall back to verify_ledger (less efficient)
        if hasattr(kernel._auditor, "verify_incremental"):
            report = kernel._auditor.verify_incremental(new_events, start_hash=last_hash)
        else:
            # Fallback for legacy auditors (will re-verify all provided events, but at least we only pass new ones)
            # Note: This loses chain link verification if auditor doesn't support start_hash
            report = kernel._auditor.verify_ledger(new_events)

        # If there's a CRITICAL violation, halt the kernel
        if not report.passed:
            for violation in report.violations:
                if violation.severity == InvariantSeverity.CRITICAL.value:
                    # Don't halt on VOID violations in normal operation (they need context)
                    # Only halt on event-based violations (BROADCAST_LICENSE, DUPLICATES, etc)
                    if "VOID" not in violation.invariant_name:
                        logger.critical(f"🛡️  IMMUNE SYSTEM ALERT: {violation.invariant_name} - {violation.message}")
                        kernel.shutdown(reason=f"Immune system reaction: {violation.invariant_name}")
                        return
                    else:
                        logger.debug("⚠️  VOID check skipped (requires external context)")

        # Log health check (non-critical)
        if report.violations:
            logger.debug(f"⚠️  Auditor info: {len(report.violations)} issue(s) detected in new batch")
        else:
            # Only log success if we actually checked something significant or periodically
            if len(new_events) > 10:
                logger.debug(f"✅ System health check passed ({len(new_events)} new events)")

        # OPUS-208: 4. Persist new anchor atomically
        # New anchor is the ID and Hash of the LAST event in the verified batch
        if new_events:
            latest_event = new_events[-1]
            new_anchor = (latest_event["id"], latest_event["current_hash"])
            kernel._ledger.set_meta("health_anchor", new_anchor)

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")


def sync_resource_quotas(kernel: "RealVibeKernel") -> None:
    """
    Phase 3: Sync resource quotas with CivicBank credits.

    This makes credits REAL by updating CPU/RAM limits based on balance.
    Runs every 60 seconds to avoid excessive bank queries.
    """
    import time

    current_time = time.time()
    if current_time - kernel._last_quota_sync < 60:  # Sync every 60 seconds
        return

    try:
        # Get CivicBank (lazy loaded)
        bank = kernel.get_bank()

        # Update quotas for all agents
        for agent_id in kernel._agent_registry.keys():
            try:
                # Query credit balance
                balance = bank.get_balance(agent_id)

                # Update quota
                kernel.resource_manager.set_quota(agent_id, credits=balance)

                # Enforce on running process
                proc_info = kernel.process_manager.processes.get(agent_id)
                if proc_info and proc_info.process.is_alive():
                    kernel.resource_manager.enforce_quota(agent_id, proc_info.process)

            except Exception as e:
                logger.debug(f"⚠️  Failed to sync quota for {agent_id}: {e}")

        kernel._last_quota_sync = current_time
        logger.debug("💰 Resource quotas synced with CivicBank")

    except Exception as e:
        logger.debug(f"⚠️  Quota sync failed: {e}")


def grant_repo_access(kernel: "RealVibeKernel", agent_id: str) -> None:
    """
    Phase 4b: Grant controlled repo access via symlink.

    Scribe and Archivist need to read the main repo.
    We create a symlink in their sandbox pointing to the repo.

    Security: This is a controlled escape. Only specific agents get it.
    """
    try:
        import os

        from vibe_core.vfs import VirtualFileSystem

        vfs = VirtualFileSystem(agent_id)
        repo_path = os.getcwd()  # /Users/ss/Downloads/steward-protocol

        # Create symlink: sandbox/repo -> actual repo
        vfs.create_symlink(repo_path, "repo")

        logger.info(f"🔗 {agent_id} granted repo access: {vfs.get_sandbox_path()}/repo -> {repo_path}")

    except Exception as e:
        logger.error(f"❌ Failed to grant repo access to {agent_id}: {e}")


def pulse(kernel: "RealVibeKernel") -> None:
    """
    💓 HEARTBEAT: Generate real-time snapshot of kernel state.

    Event Sourcing → State Projection:
    - Collects current state from all agents
    - Writes vibe_snapshot.json (immutable state view)
    - Renders OPERATIONS.md (human-readable dashboard)
    """
    try:
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_status": kernel._status.value,
            "agents": {},
            "scheduler": kernel._scheduler.get_queue_status(),
            "ledger_stats": {
                "total_events": kernel._ledger.count_events(),
            },
        }

        # Collect agent status
        for agent_id, agent in kernel._agent_registry.items():
            try:
                # 1. Start with base status
                agent_status = agent.report_status() if hasattr(agent, "report_status") else {"status": "UNKNOWN"}

                # 2. Check if agent is actually running (process check)
                is_alive = True
                if agent_id in kernel.process_manager.processes:
                    is_alive = kernel.process_manager.processes[agent_id].process.is_alive()

                if not is_alive:
                    agent_status["status"] = "CRASHED"
                    agent_status["error"] = "Process is not responding"

                # 3. Mark paused agents (via governance plugin)
                if kernel.governance and hasattr(kernel.governance, "is_agent_paused"):
                    if kernel.governance.is_agent_paused(agent_id):
                        agent_status["status"] = "PAUSED"

                snapshot["agents"][agent_id] = agent_status

            except Exception as e:
                logger.warning(f"⚠️  Could not get status from {agent_id}: {e}")
                snapshot["agents"][agent_id] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Write snapshot through I/O Service (atomic + audited)
        result = kernel.io.write_snapshot("vibe_snapshot.json", snapshot, writer_id="KERNEL")
        if result.success:
            logger.info("💓 Pulse written: vibe_snapshot.json (via I/O Service)")
        else:
            logger.error(f"❌ Pulse snapshot write failed: {result.error}")

    except Exception as e:
        logger.error(f"❌ Pulse failed: {e}")


async def execute_playbook(
    kernel: "RealVibeKernel",
    playbook_path: str,
    input_data: Dict[str, Any],
    user_input: str = "",
) -> Dict[str, Any]:
    """
    Execute a playbook through the DeterministicExecutor.

    This method enables nested playbook execution, allowing playbooks to call
    other playbooks via the CALL_PLAYBOOK action type.

    Args:
        kernel: The kernel instance
        playbook_path: Path to the playbook YAML file (relative to knowledge/playbooks/)
        input_data: Input parameters for the playbook
        user_input: Optional user input string (defaults to empty string)

    Returns:
        Dictionary with execution results

    Example:
        result = await kernel.execute_playbook(
            playbook_path="vibe_core/playbook/circuits/wiring_audit.yaml",
            input_data={"scope": "full"},
            user_input="Run wiring audit"
        )
    """
    # Import here to avoid circular dependency
    import os

    from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

    # Get or create executor instance
    if not hasattr(kernel, "_playbook_executor"):
        kernel._playbook_executor = DeterministicExecutor()

    # Extract playbook_id from path (e.g., "wiring_audit" from "circuits/wiring_audit.yaml")
    playbook_id = os.path.splitext(os.path.basename(playbook_path))[0]

    # Create a minimal intent vector (playbooks don't always need full intent analysis)
    class MinimalIntentVector:
        def __init__(self, user_input: str):
            self.raw_input = user_input
            self.concepts = set()
            self.target_agent = None

    intent_vector = MinimalIntentVector(user_input or "Nested playbook execution")

    # Execute the playbook
    logger.info(f"🎯 Kernel executing playbook: {playbook_id} from {playbook_path}")
    start_time = time.time()
    result = await kernel._playbook_executor.execute(
        playbook_id=playbook_id,
        user_input=user_input or str(input_data),
        intent_vector=intent_vector,
        kernel=kernel,
        emit_event=None,
    )
    duration_ms = (time.time() - start_time) * 1000

    if isinstance(result, dict):
        result["duration_ms"] = duration_ms

    return result


def narasimha_destroy_agent(
    kernel: "RealVibeKernel",
    agent_id: str,
    trigger: Any,
) -> None:
    """
    ⚡ NARASIMHA DESTRUCTION HANDLER - Called when Narasimha activates.

    This is the REAL kill-switch. When Narasimha detects an existential threat,
    this method executes total annihilation of the rogue agent:
    1. Kill process (if running)
    2. Revoke all capabilities
    3. Remove from registry
    4. Log to ledger (immutable record)
    5. Record in Parampara blockchain

    Args:
        kernel: The kernel instance
        agent_id: The agent to destroy
        trigger: The threat that triggered destruction (ThreatIndicator)
    """
    from vibe_core.lineage import LineageEventType

    logger.critical(f"⚡⚡⚡ NARASIMHA EXECUTING: Destroying agent '{agent_id}' ⚡⚡⚡")

    # 1. Kill process immediately
    if agent_id in kernel.process_manager.processes:
        proc_info = kernel.process_manager.processes[agent_id]
        try:
            if proc_info.process.is_alive():
                proc_info.process.terminate()
                proc_info.process.join(timeout=1)
                if proc_info.process.is_alive():
                    proc_info.process.kill()  # SIGKILL if terminate fails
            logger.critical(f"🔥 Process killed: {agent_id}")
        except Exception as e:
            logger.error(f"Process kill failed: {e}")

    # 2. Revoke all capabilities (use CapabilityRegistry)
    if kernel._capability_registry.is_registered(agent_id):
        kernel._capability_registry.revoke_all(
            agent_id=agent_id,
            revoker_id="NARASIMHA",
            reason=f"Kill-switch activated: {trigger.threat_type.value}",
        )
        logger.critical(f"🔒 Capabilities revoked: {agent_id}")

    # 3. Remove from agent registry (internal - doesn't affect MappingProxyType view)
    if agent_id in kernel._agent_registry:
        del kernel._agent_registry[agent_id]
        logger.critical(f"🗑️  Removed from registry: {agent_id}")

        # PLUGIN HOOK: Notify plugins about agent removal
        for plugin in kernel._plugins:
            plugin.on_agent_unregistered(kernel, agent_id)

    # 4. Log to ledger (immutable record of destruction)
    kernel._ledger.record_event(
        event_type="NARASIMHA_DESTRUCTION",
        agent_id=agent_id,
        details={
            "trigger_type": trigger.indicator_type,
            "severity": trigger.severity.value,
            "description": trigger.description,
            "evidence": trigger.evidence,
            "timestamp": trigger.timestamp,
        },
    )
    logger.critical(f"📜 Destruction logged to ledger: {agent_id}")

    # 5. Mark in lineage (permanent blockchain record)
    kernel.lineage.add_block(
        event_type=LineageEventType.AGENT_DESTROYED,
        agent_id=agent_id,
        data={
            "reason": trigger.indicator_type,
            "description": trigger.description,
            "destroyer": "NARASIMHA",
        },
    )
    logger.critical(f"⛓️  Destruction recorded in Parampara: {agent_id}")
    logger.critical(f"✝️ NARASIMHA COMPLETE: Agent '{agent_id}' has been annihilated.")
