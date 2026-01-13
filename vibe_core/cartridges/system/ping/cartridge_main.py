"""
PING Agent - Minimal agent to prove the system works.

50 lines. No bullshit. Uses ContextAwareAgent + DegradationChain.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xf79d1ae4"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict

from vibe_core.agents import ContextAwareAgent
from vibe_core.protocols import AgentManifest
from vibe_core.steward import OathMixin

logger = logging.getLogger("PING")


class PingCartridge(ContextAwareAgent, OathMixin):
    """Simplest possible agent. Receives task, responds."""

    def __init__(self):
        super().__init__(
            agent_id="ping",
            name="PING",
            version="1.0.0",
            author="Steward Protocol",
            description="Minimal test agent",
            domain="SYSTEM",
            capabilities=["ping", "status"],
        )

        # Swear oath
        self.oath_mixin_init(self.agent_id)
        self.swear_oath_sync()
        logger.info("🏓 PING agent ready")

    def get_manifest(self) -> AgentManifest:
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author="Steward Protocol",
            description="Minimal test agent",
            domain="SYSTEM",
            capabilities=["ping", "status"],
        )

    async def process(self, task) -> Dict[str, Any]:
        """Process a task. Simple: ping returns pong."""
        action = task.payload.get("action", "ping")

        if action == "ping":
            return {"status": "success", "response": "pong"}

        if action == "status":
            deg_status = self.get_degradation_status()
            return {
                "status": "success",
                "agent": self.agent_id,
                "degradation_level": deg_status.get("level", "unknown"),
                "response": "PING agent operational",
            }

        # Use LLM for anything else (with offline fallback)
        response = self.chat_with_fallback(
            prompt=f"User asked: {task.payload.get('message', action)}", context={"task_id": str(task.id)}
        )
        return {
            "status": "success",
            "response": response.content,
            "level": response.level.value if hasattr(response.level, "value") else str(response.level),
        }

    def report_status(self) -> Dict[str, Any]:
        """Report PING status for observability (Article IV compliance)."""
        deg_status = self.get_degradation_status()
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "OPERATIONAL",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "degradation_level": deg_status.get("level", "L0_OFFLINE"),
            "description": "Minimal test agent for system validation",
        }


__all__ = ["PingCartridge"]
