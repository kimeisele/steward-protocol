#!/usr/bin/env python3
"""
GAD-509: Circuit Breaker Protocol
==================================

Protects VIBE Agency OS from cascading failures when LLM API is degraded.

State Machine:
  CLOSED (healthy) ──(5 failures/60s)──> OPEN (failing)
                                          │
                                          ├─(30s timeout)──> HALF_OPEN (testing)
                                          │
                                          └─(probe succeeds)──> CLOSED

Implementation of the "Final Straw Defense" - prevents system collapse during:
- Anthropic API rate limiting
- OpenAI/Claude service degradation
- Network issues causing sustained failures

Version: 1.0 (GAD-509)
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """States of the circuit breaker"""

    CLOSED = "closed"  # Normal operation - requests pass through
    OPEN = "open"  # API failing - reject new requests
    HALF_OPEN = "half_open"  # Testing recovery - allow probe request


class CircuitBreakerOpenError(Exception):
    """Raised when circuit is OPEN and request is rejected"""

    pass


class CircuitBreakerHalfOpenError(Exception):
    """Raised when circuit is HALF_OPEN and request is rejected"""

    pass


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""

    failure_threshold: int = 5  # Failures before opening
    recovery_timeout_seconds: int = 30  # Time to wait before probe
    window_size_seconds: int = 60  # Rolling window for failure count
    success_threshold_half_open: int = 1  # Successes needed to close from HALF_OPEN


@dataclass
class CircuitBreakerMetrics:
    """Metrics about circuit breaker activity"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0  # Requests rejected due to OPEN state
    state_changes: list[tuple[str, str]] = field(
        default_factory=list
    )  # (timestamp, old_state, new_state)
    last_failure_time: datetime | None = None
    last_failure_error: str | None = None


class CircuitBreaker:
    """
    Circuit Breaker for LLM API protection.

    Monitors API call failures and automatically opens the circuit when
    the API shows signs of degradation. This prevents cascading failures
    and allows the system to gracefully degrade.

    Usage:
        breaker = CircuitBreaker()
        try:
            result = breaker.call(llm_client.invoke, prompt="...", model="...")
        except CircuitBreakerOpenError:
            # API is down, use fallback strategy
            result = await use_cached_response()
    """

    def __init__(self, config: CircuitBreakerConfig | None = None):
        """
        Initialize circuit breaker.

        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED

        # Failure tracking
        self.failure_count = 0
        self.failure_times: list[float] = []  # Timestamps of failures
        self.last_failure_time: float | None = None
        self.last_failure_error: str | None = None

        # Metrics
        self.metrics = CircuitBreakerMetrics()

        logger.info(
            f"Circuit Breaker initialized: "
            f"threshold={self.config.failure_threshold}, "
            f"recovery_timeout={self.config.recovery_timeout_seconds}s, "
            f"window_size={self.config.window_size_seconds}s"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerOpenError: If circuit is OPEN
            CircuitBreakerHalfOpenError: If circuit is HALF_OPEN and probe fails
            (Other exceptions from func are propagated)
        """
        # Check circuit state
        can_execute, reason = self.can_execute()
        if not can_execute:
            self.metrics.rejected_requests += 1

            if self.state == CircuitBreakerState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker OPEN: {reason}. "
                    f"LLM API showing sustained failures. "
                    f"Last error: {self.last_failure_error}"
                )
            else:  # HALF_OPEN
                raise CircuitBreakerHalfOpenError(
                    f"Circuit breaker HALF_OPEN: {reason}. "
                    f"Testing recovery with probe request only."
                )

        # Execute the function
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result

        except Exception as e:
            self._record_failure(e)
            raise

    def can_execute(self) -> tuple[bool, str]:
        """
        Check if a request can be executed.

        Returns:
            (can_execute: bool, reason: str)
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True, "OK"

        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.config.recovery_timeout_seconds:
                self._transition_to(CircuitBreakerState.HALF_OPEN)
                return (
                    True,
                    f"Transitioning to HALF_OPEN after {elapsed:.0f}s recovery timeout",
                )
            else:
                remaining = self.config.recovery_timeout_seconds - elapsed
                return False, f"Retry in {remaining:.0f}s"

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # In HALF_OPEN, we allow requests but mark them as probes
            return True, "HALF_OPEN - probe request"

        return True, "Unknown state"

    def _record_success(self):
        """Record successful request"""
        self.metrics.successful_requests += 1
        self.metrics.total_requests += 1

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Probe succeeded - return to CLOSED
            logger.info("Circuit Breaker probe succeeded - transitioning to CLOSED")
            self._transition_to(CircuitBreakerState.CLOSED)
            self.failure_count = 0
            self.failure_times.clear()

        elif self.state == CircuitBreakerState.CLOSED:
            # Normal operation - reset failure counter
            self.failure_count = 0

    def _record_failure(self, error: Exception):
        """
        Record failed request and potentially open the circuit.

        Args:
            error: The exception that was raised
        """
        self.metrics.failed_requests += 1
        self.metrics.total_requests += 1

        error_name = type(error).__name__
        error_msg = str(error)
        self.last_failure_time = time.time()
        self.last_failure_error = f"{error_name}: {error_msg[:100]}"

        # Track failure times for rolling window
        self.failure_times.append(self.last_failure_time)

        # Remove old failures outside the window
        window_start = self.last_failure_time - self.config.window_size_seconds
        self.failure_times = [t for t in self.failure_times if t >= window_start]
        self.failure_count = len(self.failure_times)

        logger.warning(
            f"LLM API failure recorded: {self.last_failure_error} "
            f"(failures: {self.failure_count}/{self.config.failure_threshold} in {self.config.window_size_seconds}s)"
        )

        # Check if we should open the circuit
        if self.failure_count >= self.config.failure_threshold:
            logger.error(
                f"Circuit Breaker OPENING! LLM API showing sustained issues. "
                f"Failures: {self.failure_count}/{self.config.failure_threshold} "
                f"in {self.config.window_size_seconds}s. "
                f"Last error: {self.last_failure_error}"
            )
            self._transition_to(CircuitBreakerState.OPEN)

    def _transition_to(self, new_state: CircuitBreakerState):
        """
        Transition to a new state.

        Args:
            new_state: The new state to transition to
        """
        old_state = self.state.value
        self.state = new_state
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.metrics.state_changes.append((timestamp, old_state, new_state.value))

        logger.info(f"Circuit Breaker state transition: {old_state} → {new_state.value}")

    def get_status(self) -> dict[str, Any]:
        """
        Get current circuit breaker status.

        Returns:
            Dictionary with current state and metrics
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.config.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "last_failure_error": self.last_failure_error,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "rejected_requests": self.metrics.rejected_requests,
                "state_changes": len(self.metrics.state_changes),
            },
        }

    def reset(self):
        """
        Manually reset the circuit breaker to CLOSED state.

        Useful for testing or manual recovery.
        """
        logger.info("Circuit Breaker manually reset to CLOSED")
        self._transition_to(CircuitBreakerState.CLOSED)
        self.failure_count = 0
        self.failure_times.clear()
        self.last_failure_time = None
        self.last_failure_error = None
