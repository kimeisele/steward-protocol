"""Moltbook Wiring Module — Circuit + AGORA + Mahamantra integration."""

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from vibe_core.runtime.kernel import RealVibeKernel

logger = logging.getLogger("MOLTBOOK.WIRING")


class CircuitExecutor(Protocol):
    """Circuit executor interface."""

    circuits: dict


class MetaCircuitManager(Protocol):
    """Meta circuit manager interface."""

    pass


class AgoraAgent(Protocol):
    """AGORA agent interface."""

    def publish_message(
        self,
        source: str,
        message_type: str,
        content: str,
        metadata: dict,
    ) -> None:
        """Publish message to AGORA."""
        ...


class WiringModule:
    """Handle all kernel wiring: Circuit Executor, AGORA, Mahamantra."""

    def __init__(self) -> None:
        self.circuit_executor: CircuitExecutor | None = None
        self.meta_circuit_manager: MetaCircuitManager | None = None
        self.agora: AgoraAgent | None = None

    def wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        """Wire CognitiveCircuitExecutor + MetaCircuitManager."""
        try:
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor_with_meta

            executor, manager = create_circuit_executor_with_meta(kernel)
            if "MOLTBOOK_CONTENT_V1" in executor.circuits:
                self.circuit_executor = executor
                self.meta_circuit_manager = manager
                logger.info(f"Circuit executor wired: {len(executor.circuits)} circuits loaded")
            else:
                logger.warning("MOLTBOOK_CONTENT_V1 not found in circuits")
        except Exception as e:
            logger.warning(f"Circuit executor wiring failed: {e}")

    def wire_agora(self, kernel: "RealVibeKernel") -> None:
        """Wire AGORA broadcast channel for federation."""
        try:
            agora = kernel.get_agent("agora") if hasattr(kernel, "get_agent") else None
            if agora and hasattr(agora, "publish_message"):
                self.agora = agora
                logger.info("AGORA broadcast wired")
            else:
                logger.info("AGORA not available")
        except Exception as e:
            logger.warning(f"AGORA wiring skipped: {e}")

    def broadcast_to_agora(self, content_type: str, content: str, metadata: dict) -> None:
        """Broadcast content to AGORA."""
        if not self.agora:
            return
        try:
            self.agora.publish_message(
                source="moltbook",
                message_type="narrative",
                content=content[:500],
                metadata={
                    "content_type": content_type,
                    **metadata,
                },
            )
        except Exception as e:
            logger.warning(f"AGORA broadcast failed: {e}")
