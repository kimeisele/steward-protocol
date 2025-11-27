#!/usr/bin/env python3
"""
GAD-510: Operational Quota Manager
====================================

Tracks and enforces operational quotas to prevent surprise cost spikes and
API rate limit hits.

Quotas tracked:
  - Requests per minute (RPM)
  - Tokens per minute (TPM)
  - Cost per hour
  - Cost per day

Implementation of operational safeguards - prevents runaway API costs.

GAD-510.1: Dynamic Quota Configuration
- Loads quota limits from environment variables
- Falls back to safe defaults if undefined
- Configurable limits prevent surprises and enable custom budgets

Version: 1.1 (GAD-510 + GAD-510.1)
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Phoenix config, fall back to environment variables
try:
    from vibe_core.config import get_config

    _PHOENIX_AVAILABLE = True
except ImportError:
    _PHOENIX_AVAILABLE = False
    get_config = None


class QuotaExceededError(Exception):
    """Raised when an operational quota would be exceeded"""

    pass


def _load_quota_limits_from_config() -> dict[str, Any]:
    """
    Load quota limits from Phoenix configuration or environment variables.

    Phoenix automatically loads from environment variables or .env file:
    - VIBE_QUOTA_REQUESTS_PER_MINUTE: Requests per minute (default: 10)
    - VIBE_QUOTA_TOKENS_PER_MINUTE: Tokens per minute (default: 10000)
    - VIBE_QUOTA_COST_PER_HOUR_USD: Cost per hour (default: 2.0)
    - VIBE_QUOTA_COST_PER_DAY_USD: Cost per day (default: 5.0)

    If Phoenix is not available, falls back to environment variables.

    Returns:
        Dictionary with quota limit keys and values from Phoenix config or env
    """
    # If Phoenix is available, use it
    if _PHOENIX_AVAILABLE and get_config:
        try:
            config = get_config()
            return {
                "requests_per_minute": config.quotas.requests_per_minute,
                "tokens_per_minute": config.quotas.tokens_per_minute,
                "cost_per_hour_usd": config.quotas.cost_per_hour_usd,
                "cost_per_day_usd": config.quotas.cost_per_day_usd,
            }
        except Exception as e:
            logger.debug(f"Phoenix config unavailable, falling back to environment variables: {e}")

    # Fallback: Load from environment variables
    try:
        import os

        return {
            "requests_per_minute": int(os.environ.get("VIBE_QUOTA_REQUESTS_PER_MINUTE", "10")),
            "tokens_per_minute": int(os.environ.get("VIBE_QUOTA_TOKENS_PER_MINUTE", "10000")),
            "cost_per_hour_usd": float(os.environ.get("VIBE_QUOTA_COST_PER_HOUR_USD", "2.0")),
            "cost_per_day_usd": float(os.environ.get("VIBE_QUOTA_COST_PER_DAY_USD", "5.0")),
        }
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid quota environment variables, using safe defaults: {e}")
        return {
            "requests_per_minute": 10,
            "tokens_per_minute": 10000,
            "cost_per_hour_usd": 2.0,
            "cost_per_day_usd": 5.0,
        }


@dataclass
class QuotaLimits:
    """Quota limits configuration (GAD-510.1: Environment-configurable)"""

    requests_per_minute: int = 10  # Default: Safe limit
    tokens_per_minute: int = 10000  # Default: Safe limit
    concurrent_requests: int = 10  # Max parallel invocations
    cost_per_request_usd: float = 0.50  # Alert if single request > $0.50
    cost_per_hour_usd: float = 2.0  # Default: $2/hour safe limit
    cost_per_day_usd: float = 5.0  # Default: $5/day safe limit

    @classmethod
    def from_environment(cls) -> "QuotaLimits":
        """
        Create QuotaLimits from Phoenix configuration.

        Returns:
            QuotaLimits instance with values loaded from config or defaults
        """
        limits_dict = _load_quota_limits_from_config()
        return cls(**limits_dict)


@dataclass
class QuotaMetrics:
    """Metrics about quota usage"""

    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    requests_this_minute: int = 0
    tokens_this_minute: int = 0
    cost_this_hour_usd: float = 0.0
    cost_this_day_usd: float = 0.0
    quota_violations: list[dict[str, Any]] = field(default_factory=list)
    minute_start_time: float = field(default_factory=time.time)
    hour_start_time: float = field(default_factory=time.time)
    day_start_time: float = field(default_factory=time.time)


class OperationalQuota:
    """
    Manages and enforces operational quotas.

    Prevents:
    - Unexpected API rate limit hits
    - Runaway cost spikes
    - Resource exhaustion

    Usage:
        quota = OperationalQuota()

        # Pre-flight check
        try:
            quota.check_before_request(estimated_tokens=5000, operation="feature_implementation")
        except QuotaExceededError as e:
            logger.error(f"Cannot execute request: {e}")
            return

        # Record actual usage
        quota.record_request(tokens_used=4800, cost_usd=0.24, operation="feature_implementation")
    """

    def __init__(self, limits: QuotaLimits | None = None):
        """
        Initialize quota manager.

        Args:
            limits: QuotaLimits configuration (loads from env vars if None)
        """
        self.limits = limits or QuotaLimits.from_environment()
        self.metrics = QuotaMetrics()

        logger.info(
            f"Quota Manager initialized: "
            f"RPM={self.limits.requests_per_minute}, "
            f"TPM={self.limits.tokens_per_minute}, "
            f"cost/hour=${self.limits.cost_per_hour_usd}, "
            f"cost/day=${self.limits.cost_per_day_usd}"
        )

    def check_before_request(
        self,
        estimated_tokens: int,
        operation: str = "unknown",
    ) -> tuple[bool, str]:
        """
        Pre-flight check before sending a request to LLM.

        Args:
            estimated_tokens: Estimated tokens this request will use
            operation: Human-readable description of the operation

        Returns:
            (can_execute: bool, reason: str)

        Raises:
            QuotaExceededError: If quota would be exceeded
        """
        # Update rolling windows
        self._update_rolling_windows()

        # Check 1: Request rate limit
        if self.metrics.requests_this_minute >= self.limits.requests_per_minute:
            raise QuotaExceededError(
                f"Request rate limit exceeded: {self.metrics.requests_this_minute}/"
                f"{self.limits.requests_per_minute} RPM"
            )

        # Check 2: Token rate limit
        if self.metrics.tokens_this_minute + estimated_tokens > self.limits.tokens_per_minute:
            raise QuotaExceededError(
                f"Token rate limit would be exceeded: "
                f"{self.metrics.tokens_this_minute + estimated_tokens}/"
                f"{self.limits.tokens_per_minute} TPM. "
                f"Estimated tokens: {estimated_tokens}"
            )

        # Check 3: Estimate cost and check against limits
        estimated_cost = self._estimate_cost(estimated_tokens)

        if estimated_cost > self.limits.cost_per_request_usd:
            logger.warning(
                f"High-cost request detected: ${estimated_cost:.2f} "
                f"for operation '{operation}' ({estimated_tokens} tokens)"
            )
            # Raise error - require explicit approval for high-cost requests
            raise QuotaExceededError(
                f"High-cost request: ${estimated_cost:.2f} exceeds limit of "
                f"${self.limits.cost_per_request_usd:.2f}. "
                f"Operation: '{operation}'"
            )

        # Check 4: Hourly cost limit
        if self.metrics.cost_this_hour_usd + estimated_cost > self.limits.cost_per_hour_usd:
            remaining = self.limits.cost_per_hour_usd - self.metrics.cost_this_hour_usd
            logger.warning(
                f"Hourly cost limit approaching: "
                f"${self.metrics.cost_this_hour_usd:.2f}/"
                f"${self.limits.cost_per_hour_usd:.2f}, "
                f"remaining: ${remaining:.2f}"
            )
            raise QuotaExceededError(
                f"Hourly cost limit would be exceeded: "
                f"${self.metrics.cost_this_hour_usd + estimated_cost:.2f}/"
                f"${self.limits.cost_per_hour_usd:.2f}. "
                f"Request cost: ${estimated_cost:.2f}"
            )

        # Check 5: Daily cost limit
        if self.metrics.cost_this_day_usd + estimated_cost > self.limits.cost_per_day_usd:
            remaining = self.limits.cost_per_day_usd - self.metrics.cost_this_day_usd
            logger.warning(
                f"Daily cost limit approaching: "
                f"${self.metrics.cost_this_day_usd:.2f}/"
                f"${self.limits.cost_per_day_usd:.2f}, "
                f"remaining: ${remaining:.2f}"
            )
            raise QuotaExceededError(
                f"Daily cost limit would be exceeded: "
                f"${self.metrics.cost_this_day_usd + estimated_cost:.2f}/"
                f"${self.limits.cost_per_day_usd:.2f}. "
                f"Request cost: ${estimated_cost:.2f}"
            )

        return True, "OK"

    def record_request(
        self,
        tokens_used: int,
        cost_usd: float,
        operation: str = "unknown",
    ):
        """
        Record a completed request.

        Args:
            tokens_used: Actual tokens used
            cost_usd: Actual cost in USD
            operation: Human-readable description of the operation
        """
        # Update rolling windows
        self._update_rolling_windows()

        # Record metrics
        self.metrics.total_requests += 1
        self.metrics.total_tokens += tokens_used
        self.metrics.total_cost_usd += cost_usd
        self.metrics.requests_this_minute += 1
        self.metrics.tokens_this_minute += tokens_used
        self.metrics.cost_this_hour_usd += cost_usd
        self.metrics.cost_this_day_usd += cost_usd

        logger.info(
            f"Request recorded: {operation} "
            f"({tokens_used} tokens, ${cost_usd:.4f}). "
            f"Running totals - RPM: {self.metrics.requests_this_minute}, "
            f"TPM: {self.metrics.tokens_this_minute}, "
            f"Hour: ${self.metrics.cost_this_hour_usd:.2f}, "
            f"Day: ${self.metrics.cost_this_day_usd:.2f}"
        )

        # Check if approaching limits (for warning)
        if self.metrics.cost_this_hour_usd > self.limits.cost_per_hour_usd * 0.8:
            logger.warning(
                f"Hourly cost at 80% of limit: "
                f"${self.metrics.cost_this_hour_usd:.2f}/"
                f"${self.limits.cost_per_hour_usd:.2f}"
            )

        if self.metrics.cost_this_day_usd > self.limits.cost_per_day_usd * 0.8:
            logger.warning(
                f"Daily cost at 80% of limit: "
                f"${self.metrics.cost_this_day_usd:.2f}/"
                f"${self.limits.cost_per_day_usd:.2f}"
            )

    def _update_rolling_windows(self):
        """Update rolling time windows"""
        now = time.time()

        # Reset minute window if 60s passed
        if now - self.metrics.minute_start_time >= 60:
            self.metrics.requests_this_minute = 0
            self.metrics.tokens_this_minute = 0
            self.metrics.minute_start_time = now

        # Reset hour window if 3600s passed
        if now - self.metrics.hour_start_time >= 3600:
            self.metrics.cost_this_hour_usd = 0.0
            self.metrics.hour_start_time = now

        # Reset day window if 86400s passed
        if now - self.metrics.day_start_time >= 86400:
            self.metrics.cost_this_day_usd = 0.0
            self.metrics.day_start_time = now

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost for a given number of tokens.

        Based on Claude 3.5 Sonnet pricing:
        - Input: $3 per million tokens
        - Output: $15 per million tokens

        Conservative estimate assumes equal input/output ratio.

        Args:
            tokens: Number of tokens

        Returns:
            Estimated cost in USD
        """
        # Assume 50% input, 50% output for conservative estimate
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens

        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0

        return input_cost + output_cost

    def get_status(self) -> dict[str, Any]:
        """
        Get current quota usage status.

        Returns:
            Dictionary with current metrics and limits
        """
        self._update_rolling_windows()

        return {
            "requests": {
                "this_minute": self.metrics.requests_this_minute,
                "limit": self.limits.requests_per_minute,
                "percent_used": (
                    self.metrics.requests_this_minute / self.limits.requests_per_minute * 100
                ),
            },
            "tokens": {
                "this_minute": self.metrics.tokens_this_minute,
                "limit": self.limits.tokens_per_minute,
                "percent_used": (
                    self.metrics.tokens_this_minute / self.limits.tokens_per_minute * 100
                ),
            },
            "cost": {
                "this_hour_usd": round(self.metrics.cost_this_hour_usd, 4),
                "limit_per_hour_usd": self.limits.cost_per_hour_usd,
                "this_day_usd": round(self.metrics.cost_this_day_usd, 4),
                "limit_per_day_usd": self.limits.cost_per_day_usd,
                "total_usd": round(self.metrics.total_cost_usd, 4),
            },
            "totals": {
                "total_requests": self.metrics.total_requests,
                "total_tokens": self.metrics.total_tokens,
                "quota_violations": len(self.metrics.quota_violations),
            },
        }

    def reset(self):
        """
        Manually reset quota counters.

        Useful for testing or explicit user intervention.
        """
        logger.info("Quota Manager manually reset")
        self.metrics = QuotaMetrics()
