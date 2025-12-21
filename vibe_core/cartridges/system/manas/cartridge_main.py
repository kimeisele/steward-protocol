"""
MANAS Devata - The Cognitive Mind of the System.

OPUS-072: MANAS becomes a proper citizen of Agent City.

MANAS (Sanskrit: "mind") is the cognitive core that:
- Generates intents proactively
- Executes cognitive syscalls (SPAWN_COGNITION, GRANT_MANDATE)
- Routes tasks to specialized cortex modules

This cartridge is the IDENTITY layer. The actual cognition lives in
opus_assistant/manas/ - this is just the passport to Agent City.

Philosophy:
"The mind is the friend of the conditioned soul, and his enemy as well."
- Bhagavad Gita 6.5
"""

import logging
from typing import Any, Dict

from vibe_core.agents import ContextAwareAgent
from vibe_core.protocols import AgentManifest
from vibe_core.steward import OathMixin

logger = logging.getLogger("MANAS")


class ManasCartridge(ContextAwareAgent, OathMixin):
    """
    MANAS - The Mind Devata.

    This is a PRIVILEGED system agent that can:
    - Spawn new cognitive agents (SPAWN_COGNITION)
    - Grant capabilities to agents it creates (GRANT_MANDATE)
    - Execute cognitive operations on behalf of opus_assistant

    Capabilities:
    - cognition: General cognitive operations
    - spawn_agent: Create new agents
    - grant_capability: Grant capabilities to agents
    - syscall: Execute semantic syscalls
    """

    # This is the identity used for syscalls
    MANAS_IDENTITY = "manas"

    # OPUS-072: Privileged operations use KERNEL identity
    # MANAS acts on behalf of the kernel for these operations
    PRIVILEGED_SYSCALLS = {"GRANT_MANDATE", "REVOKE_MANDATE"}

    @classmethod
    def get_syscall_identity(cls, syscall_type: str) -> str:
        """
        Get the appropriate identity for a syscall.

        MANAS acts on behalf of KERNEL for privileged operations.
        This is architecturally correct - MANAS IS the kernel's mind.

        Args:
            syscall_type: The type of syscall being executed

        Returns:
            "KERNEL" for privileged syscalls, "manas" otherwise
        """
        if syscall_type in cls.PRIVILEGED_SYSCALLS:
            return "KERNEL"
        return cls.MANAS_IDENTITY

    def __init__(self):
        super().__init__(
            agent_id=self.MANAS_IDENTITY,
            name="MANAS",
            version="1.0.0",
            author="Steward Protocol",
            description="The Cognitive Mind - Proactive Intent Generation",
            domain="SYSTEM",
            capabilities=[
                "cognition",
                "spawn_agent",
                "grant_capability",
                "syscall",
                "intent_generation",
            ],
        )

        # Swear oath
        self.oath_mixin_init(self.agent_id)
        self.swear_oath_sync()
        logger.info("MANAS Devata initialized (The Mind Awakens)")

    def get_manifest(self) -> AgentManifest:
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author="Steward Protocol",
            description="The Cognitive Mind - Proactive Intent Generation",
            domain="SYSTEM",
            capabilities=self.capabilities,
        )

    async def process(self, task) -> Dict[str, Any]:
        """
        Process cognitive tasks.

        MANAS delegates actual cognition to opus_assistant/manas/.
        This is just the identity/routing layer.
        """
        action = task.payload.get("action", "think")

        if action == "think":
            # Delegate to CognitiveKernel
            return await self._delegate_think(task)

        if action == "status":
            return self._get_status()

        if action == "ping":
            return {"status": "success", "response": "MANAS is awake"}

        # Unknown action - try LLM fallback
        response = self.chat_with_fallback(
            prompt=f"MANAS received: {task.payload.get('message', action)}",
            context={"task_id": str(task.id)},
        )
        return {
            "status": "success",
            "response": response.content,
            "level": response.level.value if hasattr(response.level, "value") else str(response.level),
        }

    async def _delegate_think(self, task) -> Dict[str, Any]:
        """Delegate thinking to CognitiveKernel."""
        try:
            from vibe_core.plugins.opus_assistant.manas import CognitiveKernel

            # Get or create cognitive kernel
            # OPUS-167: Use singleton pattern to avoid expensive re-initialization
            kernel = CognitiveKernel.get_instance(workspace=self._workspace if hasattr(self, "_workspace") else None)

            # Inject vibe kernel if available
            if self.kernel:
                kernel.inject_kernel(self.kernel)

            # Think
            context = task.payload.get("context", {})
            intents = kernel.think(context=context, force=task.payload.get("force", False))

            return {
                "status": "success",
                "intents_generated": len(intents),
                "intents": [{"id": i.id, "title": i.title} for i in intents],
            }
        except Exception as e:
            logger.warning(f"MANAS think delegation failed: {e}")
            return {"status": "error", "error": str(e)}

    def _get_status(self) -> Dict[str, Any]:
        """Get MANAS status."""
        deg_status = self.get_degradation_status()
        return {
            "status": "success",
            "agent": self.agent_id,
            "name": self.name,
            "degradation_level": deg_status.get("level", "unknown"),
            "capabilities": self.capabilities,
            "response": "MANAS Devata operational",
        }

    def report_status(self) -> Dict[str, Any]:
        """Report MANAS status for observability."""
        deg_status = self.get_degradation_status()
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "OPERATIONAL",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "degradation_level": deg_status.get("level", "L0_OFFLINE"),
            "description": "The Cognitive Mind - Proactive Intent Generation",
        }


__all__ = ["ManasCartridge"]
