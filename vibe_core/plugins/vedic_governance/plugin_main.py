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

from vibe_core.plugin_protocol import KernelPlugin

# Vedic governance types (co-located with plugin)
from vibe_core.plugins.vedic_governance.ashrama import Ashrama, AshramaTransition, get_ashrama_description
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

        # Reference to kernel (set on boot)
        self._kernel: Optional["RealVibeKernel"] = None

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Called when kernel boots.

        Register this plugin as the governance provider on the kernel.
        This allows backward-compatible access via kernel.governance.*
        """
        self._kernel = kernel

        # Restore state from ledger
        self._restore_from_ledger()

        # Register as THE governance plugin on kernel
        kernel.governance = self

        logger.info("🕉️  Vedic Governance Plugin booted (Varna + Ashrama)")
        logger.info("   Governance is now PLUGIN-BASED (not hardcoded in kernel)")

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
            permissions = ashrama.get_current_permissions()

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
