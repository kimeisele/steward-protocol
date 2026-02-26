"""Moltbook Wiring Module — Circuit + AGORA + Mahamantra integration."""

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vibe_core.runtime.kernel import RealVibeKernel

logger = logging.getLogger("MOLTBOOK.WIRING")


class WiringModule:
    """Handle all kernel wiring: Circuit Executor, AGORA, Mahamantra."""

    def __init__(self):
        self.circuit_executor = None
        self.meta_circuit_manager = None
        self.agora = None
        self.mahamantra_listener = None

    def wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        """Wire CognitiveCircuitExecutor + MetaCircuitManager."""
        try:
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor_with_meta

            executor, manager = create_circuit_executor_with_meta(kernel)
            if "MOLTBOOK_CONTENT_V1" in executor.circuits:
                self.circuit_executor = executor
                self.meta_circuit_manager = manager
                logger.info(
                    f"Circuit executor wired: {len(executor.circuits)} circuits loaded"
                )
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
            logger.debug(f"AGORA wiring skipped: {e}")

    def wire_mahamantra(self, kernel: "RealVibeKernel") -> None:
        """Wire Mahamantra tick listener."""
        try:
            singularity = kernel.api("singularity") if hasattr(kernel, "api") else None
            if singularity and hasattr(singularity, "on_tick"):
                logger.info("Mahamantra wired")
            else:
                logger.debug("Mahamantra listener not wired")
        except Exception as e:
            logger.debug(f"Mahamantra wiring skipped: {e}")

    def broadcast_to_agora(
        self, content_type: str, content: str, metadata: dict
    ) -> None:
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
            logger.debug(f"AGORA broadcast failed: {e}")
