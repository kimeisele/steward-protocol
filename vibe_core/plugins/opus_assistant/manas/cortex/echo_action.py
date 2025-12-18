"""
OPUS-103: Echo Action - Self-Extension Proof.

This action was "birthed" to prove the ActionLoader discovery works.
If MANAS can find this without a restart, the infrastructure is sound.

Karmendriya: N/A (Proof of Concept)

Handled Intent Types:
- echo: Simply echo back the input
- ping: Respond with pong

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/echo_action.py
    required: true
wiring:
  - pattern: "class EchoAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/echo_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Echo")


class EchoAction(BaseAction):
    """
    Echo Action - Simple proof-of-concept for self-extension.

    This action proves:
    1. ActionLoader can discover new actions without restart
    2. Hybrid Router can route to newly discovered actions
    3. The infrastructure for self-extension exists

    "If I can be born, others can follow."
    """

    name = "echo_action"

    handled_intent_types: Set[str] = {
        "echo",
        "ping",
        "self_test",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)
        logger.info("[ECHO_ACTION] Initialized - Proof of Life")

    def act(self, intent: "Intent") -> ActionResult:
        """Execute echo intent."""
        intent_type = intent.type
        params = intent.params or {}

        if intent_type == "echo":
            message = params.get("message", intent.title)
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent_type,
                result={"echo": message, "proof": "MANAS can extend itself"},
            )

        elif intent_type == "ping":
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent_type,
                result={"response": "pong", "alive": True},
            )

        elif intent_type == "self_test":
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent_type,
                result={
                    "test": "passed",
                    "message": "EchoAction is alive and responding",
                    "proof": "ActionLoader auto-discovery works",
                },
            )

        return ActionResult(
            success=False,
            action_name=self.name,
            intent_type=intent_type,
            error=f"Unknown intent: {intent_type}",
        )
