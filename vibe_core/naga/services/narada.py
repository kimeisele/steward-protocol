"""
NARADA SERVICE - Der Spion.

Narada - Der kosmische Journalist. Reist überall, weiß alles.

"Narada Muni ki Jai!" - Der Messenger der Götter.

Responsibilities:
- Intercept function calls via @spy decorator
- Observe without modifying (pure observation)
- Report to Cortex for pattern analysis
- Sign all observations (37th Principle)

Integration:
- Auto-discovered by Narada via @naga_service decorator
- NOTE: Narada is GOVERNANCE, not a real Naga (no CorrectionHandler)
"""

import asyncio
import functools
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import NagaStatus, NagaType
from vibe_core.protocols.naga.groups import Observation, ObserveProtocol
from vibe_core.protocols.naga.types import ObservationDict

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.identity import NagaIdentity

logger = logging.getLogger("NARADA")


@dataclass
class NaradaObservation:
    """A single observation from the spy decorator."""

    function_name: str
    args_count: int
    kwargs_keys: List[str]
    result_type: Optional[str] = None
    exception_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    observer_id: str = ""
    signature: Optional[bytes] = None


@naga_service(
    name="Narada",
    lord=NagaLord.NARADA,
    # NOTE: No drift_source - Narada is pure observer (no CorrectionHandler)
    capabilities=[NagaCapability.OBSERVATION],
    protocol_class="vibe_core.protocols.naga.NaradaProtocol",
)
class NaradaService(NagaBaseService, ObserveProtocol):
    """
    Narada - The Cosmic Journalist.

    Observes function calls without modifying behavior.
    Reports patterns to NagaCortex for analysis.

    INTERFACE GROUP: ObserveProtocol (observe, get_observations, get_observation_count)
    SEVA: Narada BEOBACHTET FÜR Prahlad - er injizierte Wissen in Prahlad im Mutterleib!
    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        identity: Optional["NagaIdentity"] = None,
        max_buffer_size: int = 1000,
    ):
        """
        Initialize Narada.

        Args:
            cortex: NagaCortex for reporting observations
            identity: NagaIdentity for signing observations
            max_buffer_size: Maximum observations to buffer
        """
        super().__init__(service_name="Narada")

        self._cortex = cortex
        self._identity = identity
        self._max_buffer_size = max_buffer_size

        self._observation_buffer: List[NaradaObservation] = []
        self._observations_count = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        logger.info("🐍 NARADA initialized - The Journalist watches")

    def get_status(self) -> NagaStatus:
        """Get current status."""
        return NagaStatus(
            naga_type=NagaType.NARADA,
            healthy=True,
            events_processed=self._observations_count,
            errors=self._errors,
            last_heartbeat=self._last_heartbeat,
            details={
                "buffer_size": len(self._observation_buffer),
                "max_buffer": self._max_buffer_size,
            },
        )

    def spy(self, func: Callable) -> Callable:
        """
        Decorator to observe function calls.

        Usage:
            @narada.spy
            def my_function(x, y):
                return x + y
        """
        if asyncio.iscoroutinefunction(func):
            return self._spy_async(func)
        return self._spy_sync(func)

    def _spy_sync(self, func: Callable) -> Callable:
        """Spy decorator for sync functions."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            observation = NaradaObservation(
                function_name=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys()),
                observer_id=self._identity.agent_id if self._identity else "",
            )

            try:
                result = func(*args, **kwargs)
                observation.result_type = type(result).__name__
                return result
            except Exception as e:
                observation.exception_type = type(e).__name__
                raise
            finally:
                try:
                    observation.duration_ms = (time.perf_counter() - start_time) * 1000
                    self._record_observation(observation)
                except Exception as e:
                    # NARADA SAFETY: Observation failure must NEVER kill the application
                    import sys

                    sys.stderr.write(f"!!! NARADA SPY FAILURE: Could not record observation: {e}\n")

        return wrapper

    def _spy_async(self, func: Callable) -> Callable:
        """Spy decorator for async functions."""

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            observation = NaradaObservation(
                function_name=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys()),
                observer_id=self._identity.agent_id if self._identity else "",
            )

            try:
                result = await func(*args, **kwargs)
                observation.result_type = type(result).__name__
                return result
            except Exception as e:
                observation.exception_type = type(e).__name__
                raise
            finally:
                try:
                    observation.duration_ms = (time.perf_counter() - start_time) * 1000
                    self._record_observation(observation)
                except Exception as e:
                    # NARADA SAFETY: Observation failure must NEVER kill the application
                    import sys

                    sys.stderr.write(f"!!! NARADA SPY FAILURE: Could not record observation: {e}\n")

        return wrapper

    def _record_observation(self, observation: NaradaObservation) -> None:
        """Record an observation to buffer and optionally report to cortex."""
        # Sign if identity available
        if self._identity:
            observation.signature = self._sign_observation(observation)

        # Add to buffer (with size limit)
        self._observation_buffer.append(observation)
        if len(self._observation_buffer) > self._max_buffer_size:
            self._observation_buffer.pop(0)

        self._observations_count += 1
        self._last_heartbeat = datetime.now()

        # Report to cortex if configured
        if self._cortex:
            try:
                self._cortex.receive_narada_observation(observation)
            except Exception as e:
                logger.warning(f"Failed to report to cortex: {e}")
                self._errors += 1

    def _sign_observation(self, observation: NaradaObservation) -> bytes:
        """Sign an observation with identity."""
        if not self._identity:
            return b""

        payload = f"{observation.function_name}:{observation.timestamp.isoformat()}"
        return self._identity.sign(payload.encode())

    @naga_governed(operation="export_observations")
    def export_observations(self) -> List[NaradaObservation]:
        """Export and clear observation buffer."""
        observations = list(self._observation_buffer)
        self._observation_buffer.clear()
        return observations

    # =========================================================================
    # ObserveProtocol Implementation (Interface Group - Seva for Prahlad)
    # =========================================================================

    def observe(self, event_type: str, source: str, data: str) -> Observation:
        """
        Observe an event (ObserveProtocol).

        SEVA: Narada observes FÜR Prahlad - reporting what needs attention.
        This is the generic observation method for the Interface Group.

        Args:
            event_type: Type of event being observed
            source: Source of the event
            data: Serialized event data (string, not Dict!)

        Returns:
            Observation record
        """
        observation = Observation(
            event_type=event_type,
            source=source,
            timestamp=datetime.now(),
            data=data,
        )

        # Also record as NaradaObservation for internal tracking
        internal_obs = NaradaObservation(
            function_name=f"observe:{event_type}",
            args_count=1,
            kwargs_keys=["source", "data"],
            result_type="Observation",
            observer_id=self._identity.agent_id if self._identity else "",
        )
        self._record_observation(internal_obs)

        return observation

    def get_observations(self, since: Optional[datetime] = None) -> List[Observation]:
        """
        Get recorded observations (ObserveProtocol).

        SEVA: Returns what Narada has seen FÜR Prahlad's governance.

        Args:
            since: Only return observations after this time (optional)

        Returns:
            List of Observation records
        """
        result: List[Observation] = []
        for obs in self._observation_buffer:
            if since is None or obs.timestamp >= since:
                # Convert NaradaObservation to generic Observation
                result.append(
                    Observation(
                        event_type=f"spy:{obs.function_name}",
                        source="narada",
                        timestamp=obs.timestamp,
                        data=f"args={obs.args_count},kwargs={obs.kwargs_keys},result={obs.result_type}",
                    )
                )
        return result

    def get_observation_count(self) -> int:
        """Get total observation count (ObserveProtocol)."""
        return self._observations_count

    # =========================================================================
    # NaradaProtocol - Fractal Entry Point for NagaProxy
    # =========================================================================

    @naga_governed(operation="receive_proxy_observation")
    def receive_proxy_observation(self, observation: ObservationDict) -> None:
        """
        Receive observation from NagaProxy.

        This is the ONE entry point. Narada routes internally:
        - Records to internal buffer (always)
        - Routes to Chitragupta (profiling)
        - Routes to Sesha (audit)
        - Routes to Kaliya (reliability/exceptions)
        - Reports to Cortex (patterns)

        NagaProxy doesn't know about other NAGAs - fractal separation.
        """
        # Record as NaradaObservation
        internal_obs = NaradaObservation(
            function_name=f"{observation.get('service_type', 'unknown')}.{observation.get('method_name', 'unknown')}",
            args_count=observation.get("args_count", 0),
            kwargs_keys=observation.get("kwargs_keys", []),
            result_type=observation.get("result_type"),
            exception_type=observation.get("exception_type"),
            duration_ms=observation.get("duration_ms", 0.0),
            observer_id=self._identity.agent_id if self._identity else "",
        )
        self._record_observation(internal_obs)

        # Route to Chitragupta (profiling)
        self._route_to_chitragupta(observation)

        # Route to Sesha (audit)
        self._route_to_sesha(observation)

        # Route to Kaliya (reliability) - UNLOCKING NAGA INTELLIGENCE
        if observation.get("exception_type"):
            self._route_to_kaliya(observation)

    def _route_to_chitragupta(self, observation: ObservationDict) -> None:
        """Route timing to Chitragupta for profiling."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import ChitraguptaProtocol

            chitragupta = ServiceRegistry.get(ChitraguptaProtocol)
            if chitragupta:
                component_id = f"{observation.get('service_type', '')}.{observation.get('method_name', '')}"
                chitragupta.record(component_id, "duration_ms", observation.get("duration_ms", 0.0))
        except Exception as e:
            logger.debug(f"Chitragupta routing failed: {e}")

    def _route_to_kaliya(self, observation: ObservationDict) -> None:
        """Route exceptions to Kaliya for reliability tracking."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import KaliyaProtocol

            kaliya = ServiceRegistry.get(KaliyaProtocol)
            if kaliya:
                # Use service type as component ID for quarantine scope
                component_id = observation.get("service_type", "unknown_service")
                kaliya.record_violation(component_id)
                logger.info(f"Reported violation to Kaliya for {component_id}")
        except Exception as e:
            logger.debug(f"Kaliya routing failed: {e}")

    def _route_to_sesha(self, observation: ObservationDict) -> None:
        """Route to Sesha for audit trail (via PUBLIC API)."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import EventRecord, SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                event: EventRecord = {
                    "event_type": "PROXY_OBSERVATION",
                    "agent_id": f"proxy.{observation.get('service_type', 'unknown')}",
                    "details": {
                        "method": observation.get("method_name", ""),
                        "duration_ms": observation.get("duration_ms", 0.0),
                        "args_count": observation.get("args_count", 0),
                        "result_type": observation.get("result_type") or "None",
                        "exception_type": observation.get("exception_type") or "",
                    },
                }
                sesha.record_event(event)
        except Exception as e:
            logger.debug(f"Sesha routing failed: {e}")
