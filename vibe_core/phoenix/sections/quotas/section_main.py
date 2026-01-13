"""
Quotas Configuration - Rate limits, budgets, circuit breaker settings.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/quotas/
    ARTHA: Parsed from config/quotas.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as QuotasConfig dataclass
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x1b37973a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RateLimitsConfig:
    """Rate limiting configuration."""

    requests_per_minute: int = 10
    tokens_per_minute: int = 10000

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RateLimitsConfig":
        return cls(
            requests_per_minute=data.get("requests_per_minute", 10),
            tokens_per_minute=data.get("tokens_per_minute", 10000),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": self.requests_per_minute,
            "tokens_per_minute": self.tokens_per_minute,
        }


@dataclass
class BudgetConfig:
    """Budget limits configuration."""

    cost_per_hour_usd: float = 2.0
    cost_per_day_usd: float = 5.0
    cost_per_request_usd: float = 0.10
    alert_threshold: float = 0.80

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BudgetConfig":
        return cls(
            cost_per_hour_usd=data.get("cost_per_hour_usd", 2.0),
            cost_per_day_usd=data.get("cost_per_day_usd", 5.0),
            cost_per_request_usd=data.get("cost_per_request_usd", 0.10),
            alert_threshold=data.get("alert_threshold", 0.80),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost_per_hour_usd": self.cost_per_hour_usd,
            "cost_per_day_usd": self.cost_per_day_usd,
            "cost_per_request_usd": self.cost_per_request_usd,
            "alert_threshold": self.alert_threshold,
        }


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    window_size_seconds: int = 60
    success_threshold_half_open: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitBreakerConfig":
        return cls(
            failure_threshold=data.get("failure_threshold", 5),
            recovery_timeout_seconds=data.get("recovery_timeout_seconds", 30),
            window_size_seconds=data.get("window_size_seconds", 60),
            success_threshold_half_open=data.get("success_threshold_half_open", 1),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout_seconds,
            "window_size_seconds": self.window_size_seconds,
            "success_threshold_half_open": self.success_threshold_half_open,
        }


@dataclass
class QuotasConfig:
    """
    Quotas Configuration.

    Auto-discovered by SectionLoader -> loads from config/quotas.yaml
    """

    section_id: str = "quotas"
    source_file: str = "quotas.yaml"

    rate_limits: RateLimitsConfig = field(default_factory=RateLimitsConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuotasConfig":
        return cls(
            rate_limits=RateLimitsConfig.from_dict(data.get("rate_limits", {})),
            budget=BudgetConfig.from_dict(data.get("budget", {})),
            circuit_breaker=CircuitBreakerConfig.from_dict(data.get("circuit_breaker", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rate_limits": self.rate_limits.to_dict(),
            "budget": self.budget.to_dict(),
            "circuit_breaker": self.circuit_breaker.to_dict(),
        }

    def validate(self) -> List[str]:
        errors = []
        if self.rate_limits.requests_per_minute < 1:
            errors.append("rate_limits.requests_per_minute must be >= 1")
        if self.budget.alert_threshold < 0 or self.budget.alert_threshold > 1:
            errors.append("budget.alert_threshold must be between 0 and 1")
        return errors
