"""
OPUS-166: Prana Action - Agent Lifecycle Management.

Karmendriya: PRANA (Life Force) - The ability to manage agent presence.

Handles:
- investigate_agent_death: Analyze why an agent stopped responding
- restart_agent: Attempt to restart a dead agent
- acknowledge_agent_birth: Log new agent registration

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prana_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prana_sense.py
    required: true
wiring:
  - pattern: "class PranaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prana_action.py
  - pattern: "handled_intent_types.*investigate_agent_death"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prana_action.py
-->
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .prana_sense import PranaSense

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Prana")


class PranaAction(BaseAction):
    """
    Prana Action - Agent Lifecycle Management.

    OPUS-166: Handles agent presence events from PranaSense.

    "Prana is the breath of the universe. When an agent stops breathing,
     MANAS must investigate. When it starts again, MANAS celebrates."
    """

    # OPUS-100: VEDA-4 auto-discovery
    name = "prana_action"

    # Intent types this action handles
    handled_intent_types: Set[str] = {
        "investigate_agent_death",
        "restart_agent",
        "acknowledge_agent_birth",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Prana Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._prana_sense = PranaSense(workspace=self._workspace)
        logger.info("🫀 [PRANA_ACTION] Initialized - Agent Lifecycle Manager")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a prana-related intent.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.intent_type

        if intent_type == "investigate_agent_death":
            return self._investigate_death(intent)
        elif intent_type == "restart_agent":
            return self._restart_agent(intent)
        elif intent_type == "acknowledge_agent_birth":
            return self._acknowledge_birth(intent)
        else:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=f"Unknown intent type: {intent_type}",
            )

    def _investigate_death(self, intent: "Intent") -> ActionResult:
        """
        Investigate why an agent died.

        Checks:
        1. Last known state from node.json (if still exists)
        2. Error logs in agent cartridge
        3. KALA time state at death
        4. Possible causes (crash, shutdown, resource exhaustion)
        """
        agent_id = intent.params.get("agent_id")
        cartridge_path = intent.params.get("cartridge_path")
        last_seen = intent.params.get("last_seen")

        if not agent_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error="Missing agent_id in intent params",
            )

        logger.info(f"🔍 [PRANA_ACTION] Investigating death of agent: {agent_id}")

        investigation = {
            "agent_id": agent_id,
            "last_seen": last_seen,
            "cartridge_path": cartridge_path,
            "investigation_time": datetime.utcnow().isoformat(),
            "findings": [],
            "possible_causes": [],
            "recommended_action": None,
        }

        # Check if cartridge exists
        if cartridge_path:
            cartridge = Path(cartridge_path)
            if cartridge.exists():
                investigation["findings"].append("Cartridge directory still exists")

                # Check for node.json remnants
                node_json = cartridge / "node.json"
                if node_json.exists():
                    try:
                        with open(node_json) as f:
                            last_state = json.load(f)
                        investigation["last_state"] = last_state
                        investigation["findings"].append("Found stale node.json - agent may have crashed")
                        investigation["possible_causes"].append("CRASH - node.json exists but agent not responding")
                    except Exception as e:
                        investigation["findings"].append(f"node.json corrupted: {e}")
                        investigation["possible_causes"].append("CORRUPTION - node.json unreadable")
                else:
                    investigation["findings"].append("node.json deleted - clean shutdown or external kill")
                    investigation["possible_causes"].append("SHUTDOWN - graceful termination")

                # Check for error logs
                error_log = cartridge / "error.log"
                if error_log.exists():
                    try:
                        last_errors = error_log.read_text().split("\n")[-10:]
                        investigation["last_errors"] = last_errors
                        investigation["findings"].append(f"Found {len(last_errors)} recent error log entries")
                    except Exception:
                        pass

                # Check steward.json for agent identity
                steward_json = cartridge / "steward.json"
                if steward_json.exists():
                    try:
                        with open(steward_json) as f:
                            identity = json.load(f)
                        investigation["agent_identity"] = identity
                        investigation["findings"].append("Agent identity (DNA) intact")
                    except Exception:
                        pass
            else:
                investigation["findings"].append("Cartridge directory missing - agent fully removed")
                investigation["possible_causes"].append("DELETION - cartridge removed from filesystem")

        # Determine recommended action
        if "CRASH" in str(investigation["possible_causes"]):
            investigation["recommended_action"] = "restart_agent"
        elif "DELETION" in str(investigation["possible_causes"]):
            investigation["recommended_action"] = "manual_review"
        else:
            investigation["recommended_action"] = "monitor"

        logger.info(
            f"🫀 [PRANA_ACTION] Investigation complete: {agent_id} - "
            f"Causes: {investigation['possible_causes']}, "
            f"Recommended: {investigation['recommended_action']}"
        )

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.intent_type,
            result=investigation,
            metadata={
                "agent_id": agent_id,
                "recommended_action": investigation["recommended_action"],
            },
        )

    def _restart_agent(self, intent: "Intent") -> ActionResult:
        """
        Attempt to restart a dead agent.

        This is a placeholder - actual restart requires kernel access.
        For now, we recreate the node.json to signal "please restart".
        """
        agent_id = intent.params.get("agent_id")
        cartridge_path = intent.params.get("cartridge_path")

        if not agent_id or not cartridge_path:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error="Missing agent_id or cartridge_path in intent params",
            )

        cartridge = Path(cartridge_path)
        if not cartridge.exists():
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Cartridge directory not found: {cartridge_path}",
            )

        logger.info(f"🔄 [PRANA_ACTION] Attempting restart of agent: {agent_id}")

        try:
            # Create a "restart_requested" marker
            # The actual agent boot process should check for this
            restart_marker = cartridge / ".restart_requested"
            restart_marker.write_text(
                json.dumps(
                    {
                        "requested_at": datetime.utcnow().isoformat(),
                        "requested_by": "MANAS.PranaAction",
                        "agent_id": agent_id,
                    }
                )
            )

            logger.info(f"🫀 [PRANA_ACTION] Restart marker created for: {agent_id}")

            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "agent_id": agent_id,
                    "restart_marker": str(restart_marker),
                    "message": "Restart marker created. Agent boot process should pick this up.",
                },
            )

        except Exception as e:
            logger.error(f"🫀 [PRANA_ACTION] Restart failed for {agent_id}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Failed to create restart marker: {e}",
            )

    def _acknowledge_birth(self, intent: "Intent") -> ActionResult:
        """
        Acknowledge a new agent birth.

        For now, just logs the event. Future: could trigger onboarding,
        capability registration, etc.
        """
        agent_id = intent.params.get("agent_id")

        if not agent_id:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error="Missing agent_id in intent params",
            )

        logger.info(f"🎉 [PRANA_ACTION] Acknowledging birth of agent: {agent_id}")

        # Get current presence info
        presence = self._prana_sense.get_agent_presence(agent_id)

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.intent_type,
            result={
                "agent_id": agent_id,
                "acknowledged_at": datetime.utcnow().isoformat(),
                "presence": {
                    "is_alive": presence.is_alive if presence else False,
                    "last_seen": presence.last_seen if presence else None,
                    "status": presence.status if presence else None,
                },
                "message": f"Welcome, {agent_id}! The universe acknowledges your presence.",
            },
        )
