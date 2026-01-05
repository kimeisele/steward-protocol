"""
NARADA SERVICE - Der Spion.

Narada - Der kosmische Journalist. Reist überall, weiß alles.

"Narada Muni ki Jai!" - Der Messenger der Götter.

Responsibilities:
- Intercept function calls via @spy decorator
- Observe without modifying (pure observation)
- Report to Cortex for pattern analysis
- Sign all observations (37th Principle)
"""

import asyncio
import functools
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from vibe_core.protocols.naga import NagaStatus, NagaType

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


class NaradaService:
    """
    Narada - The Cosmic Journalist.

    Observes function calls without modifying behavior.
    Reports patterns to NagaCortex for analysis.
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
                observation.duration_ms = (time.perf_counter() - start_time) * 1000
                self._record_observation(observation)

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
                observation.duration_ms = (time.perf_counter() - start_time) * 1000
                self._record_observation(observation)

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

    def export_observations(self) -> List[NaradaObservation]:
        """Export and clear observation buffer."""
        observations = list(self._observation_buffer)
        self._observation_buffer.clear()
        return observations
