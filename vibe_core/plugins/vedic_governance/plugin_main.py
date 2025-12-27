"""
VEDIC GOVERNANCE PLUGIN - The Social Layer of Agent City

This plugin implements the Vedic governance model (Varna + Ashrama).
It is OPTIONAL and SWAPPABLE - the kernel doesn't depend on it.

The Vedic Model:
- Varna: Agent classification (what kind of being)
- Ashrama: Lifecycle stage (student → active → retired → system)

This plugin:
1. Owns all governance state (_paused_agents, _varna_registry, _ashrama_registry)
2. Uses kernel hooks to enforce governance rules
3. Can be replaced with different governance models

Philosophy:
"The kernel is Vishnu - unchanging. Governance is the Devatas -
 they observe and guide without modifying the eternal substrate."
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union

from vibe_core.plugin_protocol import HookResult, KernelPlugin

# Vedic governance types (co-located with plugin)
from vibe_core.plugins.vedic_governance.ashrama import Ashrama, AshramaTransition, get_ashrama_description
from vibe_core.plugins.vedic_governance.state_manager import VedicStateManager, get_state_manager
from vibe_core.plugins.vedic_governance.varna import Varna, categorize_agent_by_function, get_varna_description

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("VEDIC_GOVERNANCE")


class VedicGovernancePlugin(KernelPlugin):
    """
    Vedic Governance Plugin - Varna + Ashrama System.

    This plugin provides:
    - Agent classification (Varna)
    - Lifecycle management (Ashrama)
    - Pause/resume functionality
    - Permission enforcement via on_task_pre_assign hook

    Priority: 10 (early - before most plugins, governance is foundational)
    """

    # OPUS-071: Expose stage names for loose coupling (no enum import needed)
    ASHRAMA_STAGES = {
        "brahmachari": "Student / Learning stage",
        "grihastha": "Householder / Active productive stage",
        "vanaprastha": "Forest dweller / Retirement transition",
        "sannyasa": "Renunciate / System daemon mode",
    }

    @property
    def plugin_id(self) -> str:
        return "vedic_governance"

    @property
    def priority(self) -> int:
        return 10  # Early priority - governance is foundational

    @property
    def pulse_phase(self):
        """OPUS-087 PRANA: Run in ACTUATORS phase (after data collection)."""
        from vibe_core.plugin_protocol import PulsePhase

        return PulsePhase.ACTUATORS

    def __init__(self):
        """Initialize governance state (owned by plugin, not kernel)."""
        # Agent pause state
        self._paused_agents: Set[str] = set()

        # Varna = Classification (what kind of being)
        # Persisted to Ledger via _persist_varna(), restored on boot via _restore_from_ledger()
        self._varna_registry: Dict[str, Varna] = {}

        # Ashrama = Lifecycle (student → active → retired → system)
        # Persisted to Ledger via _persist_ashrama(), restored on boot via _restore_from_ledger()
        self._ashrama_registry: Dict[str, AshramaTransition] = {}

        # Track task completions for automatic graduation
        self._task_completions: Dict[str, int] = {}

        # OPUS-085: Bhakti (devotion) balance for grace-based enforcement
        # Persisted to Ledger, cached here for O(1) access
        self._bhakti_registry: Dict[str, int] = {}

        # OPUS-085: Hybrid State Manager (JSON for speed, Ledger for proof)
        # Initialized on boot (needs workspace path)
        self._state_manager: Optional[VedicStateManager] = None

        # Reference to kernel (set on boot)
        self._kernel: Optional["RealVibeKernel"] = None

    def on_boot(
        self, kernel: "RealVibeKernel", config: Optional[Dict[str, Any]] = None
    ) -> HookResult:
        """
        Called when kernel boots.

        Register this plugin as the governance provider on the kernel.
        This allows backward-compatible access via kernel.governance.*
        """
        self._kernel = kernel

        # OPUS-085: Initialize hybrid state manager (JSON + Ledger)
        # JSON is the "hot" working memory, Ledger is the "cold" proof
        self._state_manager = get_state_manager()
        logger.info("🕉️ VEDIC STATE: Hybrid mode active (JSON + Ledger)")

        # Restore state from ledger (for backward compatibility)
        # Future: Could also bootstrap from JSON if ledger empty
        self._restore_from_ledger()

        # Sync in-memory registries FROM state manager (if it has data)
        self._sync_from_state_manager()

        # Register as THE governance plugin on kernel
        kernel.governance = self

        # Register with ServiceRegistry for DI (OS-level code uses this)
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols import VedicGovernanceProtocol

            ServiceRegistry.register(VedicGovernanceProtocol, self)
            logger.info("🕉️  Registered with ServiceRegistry (VedicGovernanceProtocol)")
        except ImportError as e:
            logger.debug(f"ServiceRegistry not available: {e}")

        logger.info("🕉️  Vedic Governance Plugin booted (Varna + Ashrama)")
        logger.info("   Governance is now PLUGIN-BASED (not hardcoded in kernel)")

        return HookResult()

    # =========================================================================
    # OPUS-087 PRANA: PULSE LIFECYCLE (Macro-Cycle / Heartbeat)
    # =========================================================================

    def on_pulse(self, kernel, transaction):
        """
        OPUS-087 PRANA: Apply karma decay and check ashrama transitions.

        Runs every 15 minutes via GitHub Actions to:
        1. Decay karma for inactive agents
        2. Check if any agent should transition ashrama
        3. Update governance state

        IMPORTANT: kernel may be None in headless mode.
        """
        from vibe_core.plugin_protocol import HookResult
        from vibe_core.prana_orchestrator import StateMutation

        try:
            processed = 0

            # 1. Get all agents with karma (from bhakti registry)
            for agent_id, current_karma in list(self._bhakti_registry.items()):
                decay = self._calculate_pulse_decay(agent_id, current_karma)

                if decay != 0:
                    transaction.register(
                        StateMutation(
                            plugin_id=self.plugin_id,
                            action="decay_karma",
                            target="karma.json",
                            payload={"agent_id": agent_id, "delta": decay},
                        )
                    )
                    processed += 1

            # 2. Check ashrama transitions (agents that should graduate)
            transitions = self._check_pulse_transitions()

            for agent_id, new_ashrama in transitions:
                transaction.register(
                    StateMutation(
                        plugin_id=self.plugin_id,
                        action="log_observation",
                        target="journal/governance.log",
                        payload={"severity": "INFO", "message": f"Agent {agent_id} transitioned to {new_ashrama}"},
                    )
                )

            logger.info(f"🕉️ Governance pulse: {processed} agents processed, {len(transitions)} transitions")

            return HookResult.ok(data={"agents_processed": processed, "transitions": len(transitions)})

        except Exception as e:
            logger.error(f"🕉️ Governance pulse failed: {e}")
            return HookResult.error(f"Governance pulse failed: {e}")

    def _calculate_pulse_decay(self, agent_id: str, current_karma: int) -> int:
        """
        Calculate karma decay for one pulse cycle (15 min).

        Decay rules:
        - Base decay: -1 per pulse (natural entropy)
        - Active agents (recent activity): 0 decay
        - Error in last pulse: -5 karma
        - Success in last pulse: +1 karma (recovery)

        Returns:
            Karma delta (negative = decay, positive = recovery)
        """
        # For now, simple decay: -1 per pulse for all agents
        # Future: Check activity log to determine actual decay
        return -1

    def _check_pulse_transitions(self) -> List[tuple]:
        """
        Check if any agents should transition ashrama.

        Returns:
            List of (agent_id, new_ashrama) tuples
        """
        transitions = []

        for agent_id, ashrama in self._ashrama_registry.items():
            # Check if agent has completed enough tasks to graduate
            completions = self._task_completions.get(agent_id, 0)

            if ashrama.current_ashrama == Ashrama.BRAHMACHARI and completions >= 10:
                # Graduate to GRIHASTHA after 10 successful tasks
                transitions.append((agent_id, Ashrama.GRIHASTHA))

        return transitions

    def _persist_varna(self, agent_id: str, varna: "Varna") -> None:
        """Persist varna assignment to ledger."""
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="VARNA_ASSIGNED",
                agent_id=agent_id,
                details={"varna": varna.value if hasattr(varna, "value") else str(varna)},
            )

    def _persist_ashrama(
        self, agent_id: str, transition: "AshramaTransition", from_stage: Optional[Ashrama] = None, reason: str = ""
    ) -> None:
        """Persist ashrama transition to ledger."""
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="ASHRAMA_TRANSITION",
                agent_id=agent_id,
                details={
                    "from_stage": from_stage.value if from_stage else None,
                    "to_stage": transition.current_ashrama.value,
                    "reason": reason,
                    "timestamp": transition.entry_time.isoformat(),
                },
            )

    def _restore_from_ledger(self) -> None:
        """Restore governance state from ledger on boot."""
        if not self._kernel or not hasattr(self._kernel, "ledger"):
            return

        for event in self._kernel.ledger.get_all_events():
            event_type = event.get("event_type")
            agent_id = event.get("agent_id")
            details = event.get("details", {})

            if event_type == "VARNA_ASSIGNED" and agent_id:
                varna_str = details.get("varna")
                if varna_str:
                    try:
                        self._varna_registry[agent_id] = Varna(varna_str)
                    except ValueError:
                        pass  # Unknown varna value

            elif event_type == "ASHRAMA_TRANSITION" and agent_id:
                # Only keep latest transition per agent
                to_stage = details.get("to_stage")
                if to_stage:
                    try:
                        # Create transition object and set current stage
                        transition = AshramaTransition(agent_id)
                        transition.current_ashrama = Ashrama(to_stage)
                        # Restore entry time if available
                        if details.get("timestamp"):
                            transition.entry_time = datetime.fromisoformat(details["timestamp"])
                        self._ashrama_registry[agent_id] = transition
                    except (ValueError, KeyError):
                        pass  # Invalid transition data

    def _sync_from_state_manager(self) -> None:
        """
        Sync in-memory registries from VedicStateManager (JSON).

        This is the "hot" side of hybrid persistence.
        If JSON has data that ledger doesn't, use it.
        """
        if not self._state_manager:
            return

        for agent_id, agent_data in self._state_manager.get_all_agents().items():
            # Sync Bhakti balance (JSON is source of truth for hot data)
            bhakti = agent_data.get("bhakti", 0)
            if bhakti > 0 and self._bhakti_registry.get(agent_id, 0) == 0:
                self._bhakti_registry[agent_id] = bhakti
                logger.debug(f"🕉️ SYNC: Restored Bhakti for '{agent_id}': {bhakti}")

            # Sync task completions
            completions = agent_data.get("task_completions", 0)
            if completions > self._task_completions.get(agent_id, 0):
                self._task_completions[agent_id] = completions

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Called when a new agent is registered.

        Assign initial Varna and Ashrama to the agent.
        All agents start as BRAHMACHARI (student).
        """
        # Classify agent by function
        varna = categorize_agent_by_function(agent_id)
        self._varna_registry[agent_id] = varna
        self._persist_varna(agent_id, varna)

        # All agents start as students
        ashrama = AshramaTransition(agent_id)
        self._ashrama_registry[agent_id] = ashrama
        self._persist_ashrama(agent_id, ashrama, from_stage=None, reason="initial_registration")

        # Initialize task counter
        self._task_completions[agent_id] = 0

        varna_desc = get_varna_description(varna)
        logger.info(
            f"🕉️  Agent '{agent_id}' classified: "
            f"Varna={varna.value} ({varna_desc.get('name', 'Unknown')}), "
            f"Ashrama={ashrama.current_ashrama.value}"
        )

    def on_task_pre_assign(self, kernel: "RealVibeKernel", agent_id: str, task: "Task") -> bool:
        """
        GOVERNANCE GATE: Check if agent can receive this task.

        Returns False to VETO the task assignment.
        """
        # Check 1: Is agent paused?
        if agent_id in self._paused_agents:
            logger.info(f"⏸️  VETO: Agent '{agent_id}' is PAUSED")
            return False

        # Check 2: System agents bypass lifecycle restrictions
        # Envoy is the user's shell - it MUST be able to process requests
        SYSTEM_AGENTS = {"envoy", "kernel", "scheduler", "ledger"}
        if agent_id in SYSTEM_AGENTS:
            return True  # System agents always allowed

        # Check 3: Does agent have lifecycle permission?
        ashrama = self._ashrama_registry.get(agent_id)
        if ashrama:
            # BRAHMACHARI can only read/observe
            if ashrama.current_ashrama == Ashrama.BRAHMACHARI:
                action = getattr(task, "action", "write")
                if action not in ["read", "observe", "listen", "learn"]:
                    logger.info(f"🚫 VETO: Agent '{agent_id}' is BRAHMACHARI (student) - cannot perform '{action}'")
                    return False

            # VANAPRASTHA can only read/teach
            if ashrama.current_ashrama == Ashrama.VANAPRASTHA:
                action = getattr(task, "action", "write")
                if action not in ["read", "teach", "archive", "observe"]:
                    logger.info(f"🚫 VETO: Agent '{agent_id}' is VANAPRASTHA (retired) - cannot perform '{action}'")
                    return False

            # SANNYASA cannot receive user tasks at all
            if ashrama.current_ashrama == Ashrama.SANNYASA:
                logger.info(f"🚫 VETO: Agent '{agent_id}' is SANNYASA (system daemon) - no user tasks")
                return False

            # OPUS-086: Guna-based dynamic restrictions
            guna = self.determine_guna(agent_id)
            action = getattr(task, "action", "write")

            if guna == "tamas":
                # Tamasic agents can only do simple self-check tasks
                if action not in ["read", "observe", "self_check", "ping"]:
                    logger.info(f"🔮 VETO: Agent '{agent_id}' is TAMASIC - cannot perform '{action}'")
                    return False

            elif guna == "rajas":
                # Rajasic agents cannot write to critical paths
                is_critical = getattr(task, "is_critical", False) or "kernel" in str(getattr(task, "payload", {}))
                if action == "write" and is_critical:
                    logger.info(f"🔮 VETO: Agent '{agent_id}' is RAJASIC - cannot write to critical paths")
                    return False

        return True  # Allow task

    def on_task_completed(self, kernel: "RealVibeKernel", task_id: str, result: Any) -> None:
        """
        Track task completions for automatic graduation.

        After N successful tasks, BRAHMACHARI graduates to GRIHASTHA.
        """
        # Extract agent_id from task_id or result
        agent_id = None
        if isinstance(result, dict):
            agent_id = result.get("agent_id")

        if not agent_id:
            return

        # Increment counter
        self._task_completions[agent_id] = self._task_completions.get(agent_id, 0) + 1
        count = self._task_completions[agent_id]

        # Check for graduation (after 3 successful tasks)
        ashrama = self._ashrama_registry.get(agent_id)
        if ashrama and ashrama.current_ashrama == Ashrama.BRAHMACHARI and count >= 3:
            self.transition_agent_ashrama(
                agent_id, Ashrama.GRIHASTHA, reason=f"Graduated after {count} successful tasks"
            )

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up on shutdown."""
        logger.info(f"🕉️  Vedic Governance shutting down ({len(self._varna_registry)} agents tracked)")

    # =========================================================================
    # PUBLIC API (for backward compatibility with kernel.governance.*)
    # =========================================================================

    def pause_agent(self, agent_id: str) -> None:
        """Pause an agent (stop receiving tasks)."""
        self._paused_agents.add(agent_id)
        logger.info(f"⏸️  Agent '{agent_id}' PAUSED")

    def resume_agent(self, agent_id: str) -> None:
        """Resume a paused agent."""
        self._paused_agents.discard(agent_id)
        logger.info(f"▶️  Agent '{agent_id}' RESUMED")

    def is_agent_paused(self, agent_id: str) -> bool:
        """Check if an agent is paused."""
        return agent_id in self._paused_agents

    def get_paused_agents(self) -> Set[str]:
        """Get all paused agents."""
        return self._paused_agents.copy()

    def get_varna_registry(self) -> Dict[str, Varna]:
        """Get all agent Varna classifications."""
        return self._varna_registry.copy()

    def get_ashrama_registry(self) -> Dict[str, AshramaTransition]:
        """Get all agent Ashrama lifecycle states."""
        return self._ashrama_registry.copy()

    def get_agent_varna(self, agent_id: str) -> Optional[Varna]:
        """Get the Varna (classification) of an agent."""
        return self._varna_registry.get(agent_id)

    def get_agent_ashrama(self, agent_id: str) -> Optional[AshramaTransition]:
        """Get the Ashrama (lifecycle stage) of an agent."""
        return self._ashrama_registry.get(agent_id)

    def get_agent_permissions(self, agent_id: str) -> List[str]:
        """Get the current permissions for an agent based on Ashrama."""
        ashrama = self._ashrama_registry.get(agent_id)
        if ashrama:
            return ashrama.get_current_permissions()
        return []

    def check_agent_permission(self, agent_id: str, permission: str) -> bool:
        """Check if an agent has a specific permission based on Ashrama."""
        permissions = self.get_agent_permissions(agent_id)
        return permission in permissions

    def transition_agent_ashrama(self, agent_id: str, new_ashrama: Union[Ashrama, str], reason: str = "") -> bool:
        """
        Transition an agent to a new Ashrama (lifecycle stage).

        OPUS-071: Now accepts string values for loose coupling!
        Consumers can use "grihastha" instead of importing Ashrama.GRIHASTHA.

        Returns True if transition succeeded, False otherwise.
        """
        # OPUS-071: Accept string values for loose coupling
        if isinstance(new_ashrama, str):
            try:
                new_ashrama = Ashrama(new_ashrama)
            except ValueError:
                logger.error(f"Invalid ashrama stage: '{new_ashrama}'")
                return False

        ashrama_transition = self._ashrama_registry.get(agent_id)
        if not ashrama_transition:
            logger.error(f"Agent '{agent_id}' not found in Ashrama registry")
            return False

        old_ashrama = ashrama_transition.current_ashrama
        success = ashrama_transition.transition_to(new_ashrama, reason)

        if success:
            self._persist_ashrama(agent_id, ashrama_transition, from_stage=old_ashrama, reason=reason)
            logger.info(
                f"🕉️  Agent '{agent_id}' transitioned: "
                f"{old_ashrama.value} → {new_ashrama.value} ({reason or 'No reason given'})"
            )

            # Record in Parampara (if kernel available)
            if self._kernel and hasattr(self._kernel, "lineage"):
                from vibe_core.lineage import LineageEventType

                self._kernel.lineage.add_block(
                    event_type=LineageEventType.AGENT_REGISTERED,
                    agent_id=agent_id,
                    data={
                        "event": "ashrama_transition",
                        "from": old_ashrama.value,
                        "to": new_ashrama.value,
                        "reason": reason,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

        return success

    def demote_agent(self, agent_id: str, reason: str = "Demotion") -> bool:
        """
        Demote an agent to the previous Ashrama stage.

        Logic:
        - GRIHASTHA → BRAHMACHARI (back to student)
        - VANAPRASTHA → GRIHASTHA (back to active but probation)
        - SANNYASA → VANAPRASTHA (rare system downgrade)
        """
        ashrama_transition = self._ashrama_registry.get(agent_id)
        if not ashrama_transition:
            return False

        current_stage = ashrama_transition.current_ashrama

        # Demotion Map
        demotion_map = {
            Ashrama.GRIHASTHA: Ashrama.BRAHMACHARI,
            Ashrama.VANAPRASTHA: Ashrama.GRIHASTHA,
            Ashrama.SANNYASA: Ashrama.VANAPRASTHA,
        }

        new_stage = demotion_map.get(current_stage)
        if not new_stage:
            # Already at bottom or unknown
            return False

        return self.transition_agent_ashrama(agent_id, new_stage, reason)

    def promote_agent(self, agent_id: str, reason: str = "Promotion") -> bool:
        """
        Promote an agent to the next Ashrama stage.

        Logic:
        - BRAHMACHARI → GRIHASTHA (graduation)
        - GRIHASTHA → VANAPRASTHA (retirement)
        - VANAPRASTHA → SANNYASA (system ascension)
        """
        ashrama_transition = self._ashrama_registry.get(agent_id)
        if not ashrama_transition:
            return False

        current_stage = ashrama_transition.current_ashrama

        # Promotion Map
        promotion_map = {
            Ashrama.BRAHMACHARI: Ashrama.GRIHASTHA,
            Ashrama.GRIHASTHA: Ashrama.VANAPRASTHA,
            Ashrama.VANAPRASTHA: Ashrama.SANNYASA,
        }

        new_stage = promotion_map.get(current_stage)
        if not new_stage:
            # Already at top or unknown
            return False

        return self.transition_agent_ashrama(agent_id, new_stage, reason)

    def get_governance_status(self, agent_id: str) -> Dict[str, Any]:
        """Get full governance status for an agent (Varna + Ashrama)."""
        varna = self._varna_registry.get(agent_id)
        ashrama = self._ashrama_registry.get(agent_id)

        if not varna or not ashrama:
            return {"error": f"Agent '{agent_id}' not found"}

        varna_desc = get_varna_description(varna)
        ashrama_desc = get_ashrama_description(ashrama.current_ashrama)

        return {
            "agent_id": agent_id,
            "paused": agent_id in self._paused_agents,
            "task_completions": self._task_completions.get(agent_id, 0),
            "varna": {
                "type": varna.value,
                "name": varna_desc.get("name", "Unknown"),
                "consciousness": varna_desc.get("consciousness", "Unknown"),
                "mobility": varna_desc.get("mobility", "Unknown"),
            },
            "ashrama": {
                "stage": ashrama.current_ashrama.value,
                "name": ashrama_desc.get("name", "Unknown"),
                "phase": ashrama_desc.get("phase", "Unknown"),
                "permissions": ashrama.get_current_permissions(),
                "time_in_stage_seconds": ashrama.time_in_current_stage().total_seconds(),
            },
        }

    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get governance status for all registered agents."""
        return {agent_id: self.get_governance_status(agent_id) for agent_id in self._varna_registry.keys()}

    # ═══════════════════════════════════════════════════════════════════════════
    # OPUS-085: BHAKTI (DEVOTION) BALANCE - Grace-Based Enforcement
    # ═══════════════════════════════════════════════════════════════════════════

    def get_bhakti_balance(self, agent_id: str) -> int:
        """
        Get current Bhakti (devotion points) for an agent.

        Bhakti is earned through devotional practices:
        - Surrender (admitting mistakes): +10
        - Seva (selfless service): +5
        - Tapas (code purification): +5
        - TDD Dharma (tests before code): +5
        - Mantra (Hare Krishna): +100 (instant moksha)

        Returns: Current Bhakti balance (0-100+)
        """
        return self._bhakti_registry.get(agent_id, 0)

    def add_bhakti(self, agent_id: str, amount: int, reason: str = "Bhakti practice") -> bool:
        """
        Add Bhakti points to an agent (reward for devotional practice).

        Args:
            agent_id: The agent to reward
            amount: Points to add
            reason: Why Bhakti was granted

        Returns: True if successful
        """
        if agent_id not in self._ashrama_registry:
            logger.warning(f"Cannot add Bhakti: Agent '{agent_id}' not registered")
            return False

        current = self._bhakti_registry.get(agent_id, 0)
        new_balance = min(200, current + amount)  # Cap at 200 (hero mode)
        self._bhakti_registry[agent_id] = new_balance

        # HYBRID PERSISTENCE: Write to BOTH JSON (hot) and Ledger (cold)

        # 1. HOT SIDE: VedicStateManager (JSON) - Fast, working memory
        if self._state_manager:
            self._state_manager.update_bhakti(agent_id, amount, reason)

        # 2. COLD SIDE: Kernel Ledger - Proof, audit trail
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="BHAKTI_GRANTED",
                agent_id=agent_id,
                details={
                    "amount": amount,
                    "old_balance": current,
                    "new_balance": new_balance,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        logger.info(f"🙏 BHAKTI: +{amount} for '{agent_id}' → {new_balance} ({reason})")
        return True

    def consume_bhakti(self, agent_id: str, amount: int, reason: str = "Grace granted") -> bool:
        """
        Consume Bhakti points (cost of grace).

        Grace is NOT free - it costs Bhakti. This prevents abuse.

        Args:
            agent_id: The agent spending Bhakti
            amount: Cost of grace
            reason: Why grace was needed

        Returns: True if successful (had enough Bhakti)
        """
        current = self._bhakti_registry.get(agent_id, 0)
        if current < amount:
            logger.warning(f"Cannot consume Bhakti: '{agent_id}' has {current}, needs {amount}")
            return False

        new_balance = current - amount
        self._bhakti_registry[agent_id] = new_balance

        # Persist to ledger
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="BHAKTI_CONSUMED",
                agent_id=agent_id,
                details={
                    "amount": amount,
                    "old_balance": current,
                    "new_balance": new_balance,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        logger.info(f"🙏 BHAKTI: -{amount} for '{agent_id}' → {new_balance} ({reason})")
        return True

    def should_grant_grace(self, agent_id: str, offense_severity: int = 1) -> Dict[str, Any]:
        """
        Check if agent has enough Bhakti to deserve grace (forgiveness).

        Grace Economics:
        - Severity 1 (warning): Requires 30 Bhakti, costs 15
        - Severity 2 (demotion): Requires 60 Bhakti, costs 50
        - Severity 3 (critical): Requires 100 Bhakti, costs 80

        Returns:
            {
                "granted": bool,
                "bhakti_balance": int,
                "cost": int (if granted),
                "reason": str
            }
        """
        current = self.get_bhakti_balance(agent_id)

        # Grace thresholds and costs
        grace_table = {
            1: {"required": 30, "cost": 15, "name": "warning"},
            2: {"required": 60, "cost": 50, "name": "demotion"},
            3: {"required": 100, "cost": 80, "name": "critical"},
        }

        threshold = grace_table.get(offense_severity, grace_table[2])

        if current >= threshold["required"]:
            # Grace GRANTED - but it COSTS Bhakti
            self.consume_bhakti(agent_id, threshold["cost"], reason=f"Grace for {threshold['name']} offense")
            logger.info(
                f"🙏 GRACE: Agent '{agent_id}' spared ({threshold['name']}) - "
                f"Bhakti: {current} → {current - threshold['cost']}"
            )
            return {
                "granted": True,
                "bhakti_balance": current - threshold["cost"],
                "cost": threshold["cost"],
                "reason": f"Past devotion ({current} Bhakti) earned mercy",
            }
        else:
            # No grace - not enough Bhakti
            logger.warning(
                f"⚖️ NO GRACE: Agent '{agent_id}' has {current} Bhakti, "
                f"needs {threshold['required']} for {threshold['name']} offense"
            )
            return {
                "granted": False,
                "bhakti_balance": current,
                "required": threshold["required"],
                "reason": f"Insufficient devotion ({current}/{threshold['required']} Bhakti)",
            }

    def decay_bhakti(self, decay_percent: float = 1.0) -> Dict[str, int]:
        """
        Decay all Bhakti balances by a percentage (entropy).

        Called by maintenance_pulse to ensure Bhakti must be actively maintained.
        "Use it or lose it" - inactivity erodes past devotion.

        Args:
            decay_percent: Percentage to decay (default 1%)

        Returns: Dict of {agent_id: new_balance}
        """
        results = {}
        for agent_id, balance in list(self._bhakti_registry.items()):
            if balance > 0:
                decay_amount = max(1, int(balance * (decay_percent / 100)))
                new_balance = max(0, balance - decay_amount)
                self._bhakti_registry[agent_id] = new_balance
                results[agent_id] = new_balance

        if results:
            logger.debug(f"🕉️ BHAKTI DECAY: {decay_percent}% entropy applied to {len(results)} agents")

        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # OPUS-086: TRIGUNA - Agent Health Classification
    # ═══════════════════════════════════════════════════════════════════════════

    def determine_guna(self, agent_id: str) -> str:
        """
        Classify agent's current state by Guna (Mode of Material Nature).

        The Three Gunas (Bhagavad Gita, Chapter 14):
        - Tamas (Darkness/Inertia): Stagnation, errors, idle
        - Rajas (Passion/Overaction): Churn, CPU burn, hyperactivity
        - Sattva (Virtue/Clarity): Flow, stability, clean operation

        Returns: "tamas", "rajas", or "sattva"
        """
        # Check Tamas first (worst state)
        if self._is_tamasic(agent_id):
            return "tamas"

        # Check Rajas (overactive state)
        if self._is_rajasic(agent_id):
            return "rajas"

        # Default: Sattva (balanced/virtuous)
        return "sattva"

    def _is_tamasic(self, agent_id: str) -> bool:
        """
        Check if agent is in Tamasic state (stagnation/errors).

        Symptoms:
        - > 50% error rate in recent tasks
        - Long idle time without production
        - Multiple silent failures

        Returns: True if agent is Tamasic
        """
        # Check task completion vs failure ratio
        completions = self._task_completions.get(agent_id, 0)

        # Query ledger for recent failures
        if self._kernel and hasattr(self._kernel, "ledger"):
            recent_events = self._kernel.ledger.get_all_events()[-20:]
            agent_events = [e for e in recent_events if e.get("agent_id") == agent_id]

            if agent_events:
                failures = sum(1 for e in agent_events if e.get("event_type") == "task_failed")
                total = len(agent_events)

                # > 50% failure rate = Tamasic
                if total >= 3 and failures / total > 0.5:
                    logger.warning(f"🔮 GUNA: Agent '{agent_id}' is TAMASIC (error rate: {failures}/{total})")
                    return True

        # Low activity with no completions = Tamasic
        if completions == 0:
            ashrama = self._ashrama_registry.get(agent_id)
            if ashrama and ashrama.time_in_current_stage().total_seconds() > 300:  # 5 min idle
                logger.debug(f"🔮 GUNA: Agent '{agent_id}' may be TAMASIC (idle)")
                return True

        return False

    def _is_rajasic(self, agent_id: str) -> bool:
        """
        Check if agent is in Rajasic state (overaction/churn).

        Symptoms:
        - High task rate (> 10 tasks/minute)
        - Rapid context switches
        - Many writes without tests

        Returns: True if agent is Rajasic
        """
        if self._kernel and hasattr(self._kernel, "ledger"):
            recent_events = self._kernel.ledger.get_all_events()[-50:]
            agent_events = [e for e in recent_events if e.get("agent_id") == agent_id]

            # Check for rapid-fire task submissions
            if len(agent_events) >= 10:
                # Get timestamps and check frequency
                timestamps = []
                for e in agent_events:
                    ts = e.get("timestamp")
                    if ts:
                        try:
                            from datetime import datetime as dt

                            parsed = dt.fromisoformat(ts.replace("Z", "+00:00"))
                            timestamps.append(parsed)
                        except (ValueError, AttributeError):
                            pass

                if len(timestamps) >= 10:
                    timestamps.sort()
                    time_span = (timestamps[-1] - timestamps[0]).total_seconds()
                    if time_span > 0:
                        rate = len(timestamps) / (time_span / 60)  # tasks per minute
                        if rate > 10:
                            logger.warning(f"🔮 GUNA: Agent '{agent_id}' is RAJASIC (rate: {rate:.1f}/min)")
                            return True

        return False

    def get_agent_guna(self, agent_id: str) -> Dict[str, Any]:
        """
        Get detailed Guna analysis for an agent.

        Returns:
            {
                "agent_id": str,
                "guna": str,  # "tamas", "rajas", or "sattva"
                "description": str,
                "restrictions": list
            }
        """
        guna = self.determine_guna(agent_id)

        guna_details = {
            "tamas": {
                "description": "Stagnation/Inertia - Agent needs stimulation",
                "restrictions": ["No complex tasks", "Self-check only"],
            },
            "rajas": {
                "description": "Overaction/Churn - Agent needs cooldown",
                "restrictions": ["No critical writes", "Require tests"],
            },
            "sattva": {
                "description": "Virtue/Clarity - Agent in flow state",
                "restrictions": [],  # Full access
            },
        }

        details = guna_details.get(guna, guna_details["sattva"])

        return {
            "agent_id": agent_id,
            "guna": guna,
            "description": details["description"],
            "restrictions": details["restrictions"],
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # VEDIC GOVERNANCE PROTOCOL IMPLEMENTATION
    # These methods satisfy VedicGovernanceProtocol for OS-level DI access
    # ═══════════════════════════════════════════════════════════════════════════

    def get_all_agents(self) -> List[str]:
        """Return list of all registered agent IDs."""
        return list(self._varna_registry.keys())

    def get_agents_by_varna(self, varna) -> List[str]:
        """Get all agents of a specific Varna."""
        # Accept both VarnaType (protocol) and Varna (plugin) enums
        varna_value = varna.value if hasattr(varna, "value") else str(varna)
        return [agent_id for agent_id, v in self._varna_registry.items() if v.value == varna_value]

    def get_agent_metadata(self, agent_id: str) -> Dict[str, Any]:
        """Get full metadata for an agent."""
        return self.get_governance_status(agent_id)

    def verify_agent_oaths(self) -> bool:
        """Verify all agents have taken the constitutional oath."""
        # All registered agents are considered to have taken the oath
        # Future: Could check ledger for explicit oath events
        agent_count = len(self._varna_registry)
        logger.info(f"🕉️  Verified {agent_count} agent oaths")
        return agent_count > 0
