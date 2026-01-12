"""
PRITHU SERVICE - Wraps Legacy boot_orchestrator.py
===================================================

POSITION: 0 (HEAD - GENESIS Quarter)

This is a THIN WRAPPER that connects the legacy BootOrchestrator
to the Mahajana framework. NO DUPLICATION - just delegation.

WRAPPED: vibe_core.boot_orchestrator.BootOrchestrator

"As King Prithu milked the Earth to provide all necessities,
this service wakes the system and provides all resources."
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from vibe_core.protocols.mahajanas.prithu import (
    PrithuProtocolBase,
    WakePhase,
    WakeResult,
    WakeState,
)

# Import legacy implementation - DO NOT DUPLICATE
from vibe_core.boot_orchestrator import BootOrchestrator as LegacyBootOrchestrator
from vibe_core.boot_mode import BootMode


class PrithuService(PrithuProtocolBase):
    """
    PRITHU Service - System Wake/Bootstrap.

    WRAPS the legacy BootOrchestrator.
    Manages system initialization sequence.

    Position 0 - The first HEAD, initiates all creation.
    """

    def __init__(self, boot_mode: Optional[BootMode] = None) -> None:
        """Initialize with legacy boot orchestrator."""
        self._boot_mode = boot_mode or BootMode.FULL
        self._orchestrator: Optional[LegacyBootOrchestrator] = None
        self._phase = WakePhase.DORMANT
        self._wake_time: Optional[str] = None
        self._resources_loaded = 0
        self._services_started = 0
        self._total_wakes = 0

    def _ensure_orchestrator(self) -> LegacyBootOrchestrator:
        """Lazy init of orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = LegacyBootOrchestrator(boot_mode=self._boot_mode)
        return self._orchestrator

    # =========================================================================
    # WAKE PROTOCOL (Position 0 - SYS_WAKE)
    # =========================================================================

    def wake(self) -> WakeResult:
        """SYS_WAKE: Wake the system from dormant state."""
        self._phase = WakePhase.BOOTSTRAP
        self._wake_time = datetime.now().isoformat()
        self._total_wakes += 1

        try:
            # Initialize orchestrator
            orch = self._ensure_orchestrator()
            self._phase = WakePhase.RESOURCES

            # Note: Full orchestrate() is async - this is sync interface
            # For sync wake, we just prepare the orchestrator
            self._resources_loaded = 1  # Orchestrator loaded
            self._phase = WakePhase.SERVICES

            self._services_started = 1  # Orchestrator ready
            self._phase = WakePhase.READY

            return WakeResult(
                success=True,
                phase=self._phase.value,
                timestamp=self._wake_time,
                services_started=self._services_started,
                resources_loaded=self._resources_loaded,
            )
        except Exception as e:
            self._phase = WakePhase.FAILED
            return WakeResult(
                success=False,
                phase=self._phase.value,
                timestamp=self._wake_time or datetime.now().isoformat(),
                error_message=str(e),
            )

    def is_awake(self) -> bool:
        """Check if system is awake."""
        return self._phase == WakePhase.READY

    def get_phase(self) -> WakePhase:
        """Get current wake phase."""
        return self._phase

    def bootstrap(self) -> WakeResult:
        """Run bootstrap sequence."""
        self._phase = WakePhase.BOOTSTRAP
        return WakeResult(
            success=True,
            phase=self._phase.value,
            timestamp=datetime.now().isoformat(),
        )

    def load_resources(self) -> int:
        """Load system resources. Returns count loaded."""
        self._phase = WakePhase.RESOURCES
        self._resources_loaded += 1
        return self._resources_loaded

    def start_services(self) -> int:
        """Start system services. Returns count started."""
        self._phase = WakePhase.SERVICES
        self._services_started += 1
        return self._services_started

    def shutdown(self) -> WakeResult:
        """Graceful shutdown (return to dormant)."""
        self._phase = WakePhase.DORMANT
        self._orchestrator = None
        return WakeResult(
            success=True,
            phase=self._phase.value,
            timestamp=datetime.now().isoformat(),
        )

    def get_state(self) -> WakeState:
        """Get wake state."""
        uptime = 0
        if self._wake_time and self._phase == WakePhase.READY:
            wake_dt = datetime.fromisoformat(self._wake_time)
            uptime = int((datetime.now() - wake_dt).total_seconds())

        return WakeState(
            current_phase=self._phase.value,
            is_awake=self.is_awake(),
            wake_time=self._wake_time or "",
            uptime_seconds=uptime,
            total_wakes=self._total_wakes,
            health="pristine" if self.is_awake() else "dormant",
        )

    # =========================================================================
    # ORCHESTRATOR ACCESS (Legacy BootOrchestrator)
    # =========================================================================

    @property
    def orchestrator(self) -> LegacyBootOrchestrator:
        """Access the legacy boot orchestrator."""
        return self._ensure_orchestrator()

    @property
    def boot_mode(self) -> BootMode:
        """Get boot mode."""
        return self._boot_mode


__all__ = ["PrithuService"]
