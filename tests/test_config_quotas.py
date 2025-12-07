"""Tests for quotas configuration section."""

import pytest
from vibe_core.phoenix.sections.quotas.section_main import (
    QuotasConfig,
    RateLimitsConfig,
    BudgetConfig,
    CircuitBreakerConfig,
)


class TestRateLimitsConfig:
    """Test RateLimitsConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = RateLimitsConfig.from_dict({})
        assert config.requests_per_minute == 10
        assert config.tokens_per_minute == 10000

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "requests_per_minute": 20,
            "tokens_per_minute": 20000,
        }
        config = RateLimitsConfig.from_dict(data)
        assert config.requests_per_minute == 20
        assert config.tokens_per_minute == 20000

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = RateLimitsConfig.from_dict({"requests_per_minute": 50})
        serialized = original.to_dict()
        restored = RateLimitsConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestBudgetConfig:
    """Test BudgetConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = BudgetConfig.from_dict({})
        assert config.cost_per_hour_usd == 2.0
        assert config.cost_per_day_usd == 5.0
        assert config.cost_per_request_usd == 0.10
        assert config.alert_threshold == 0.80

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "cost_per_hour_usd": 5.0,
            "cost_per_day_usd": 10.0,
            "cost_per_request_usd": 0.20,
            "alert_threshold": 0.90,
        }
        config = BudgetConfig.from_dict(data)
        assert config.cost_per_hour_usd == 5.0
        assert config.cost_per_day_usd == 10.0
        assert config.cost_per_request_usd == 0.20
        assert config.alert_threshold == 0.90

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = BudgetConfig.from_dict({"cost_per_hour_usd": 3.0})
        serialized = original.to_dict()
        restored = BudgetConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = CircuitBreakerConfig.from_dict({})
        assert config.failure_threshold == 5
        assert config.recovery_timeout_seconds == 30
        assert config.window_size_seconds == 60
        assert config.success_threshold_half_open == 1

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "failure_threshold": 10,
            "recovery_timeout_seconds": 60,
            "window_size_seconds": 120,
            "success_threshold_half_open": 2,
        }
        config = CircuitBreakerConfig.from_dict(data)
        assert config.failure_threshold == 10
        assert config.recovery_timeout_seconds == 60
        assert config.window_size_seconds == 120
        assert config.success_threshold_half_open == 2

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = CircuitBreakerConfig.from_dict({"failure_threshold": 7})
        serialized = original.to_dict()
        restored = CircuitBreakerConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestQuotasConfig:
    """Test QuotasConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = QuotasConfig.from_dict({})
        assert config.section_id == "quotas"
        assert config.source_file == "quotas.yaml"
        assert isinstance(config.rate_limits, RateLimitsConfig)
        assert isinstance(config.budget, BudgetConfig)
        assert isinstance(config.circuit_breaker, CircuitBreakerConfig)

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "rate_limits": {
                "requests_per_minute": 20,
                "tokens_per_minute": 20000,
            },
            "budget": {
                "cost_per_hour_usd": 5.0,
                "cost_per_day_usd": 10.0,
                "alert_threshold": 0.90,
            },
            "circuit_breaker": {
                "failure_threshold": 10,
                "recovery_timeout_seconds": 60,
            },
        }
        config = QuotasConfig.from_dict(data)
        assert config.rate_limits.requests_per_minute == 20
        assert config.budget.cost_per_hour_usd == 5.0
        assert config.circuit_breaker.failure_threshold == 10

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = QuotasConfig.from_dict(
            {
                "rate_limits": {"requests_per_minute": 20},
                "budget": {"cost_per_hour_usd": 3.0},
            }
        )
        serialized = original.to_dict()
        restored = QuotasConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()

    def test_validate_valid_config(self):
        """Test validation passes for valid config."""
        config = QuotasConfig.from_dict({})
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_requests_per_minute(self):
        """Test validation catches invalid requests_per_minute."""
        config = QuotasConfig.from_dict({"rate_limits": {"requests_per_minute": 0}})
        errors = config.validate()
        assert len(errors) > 0
        assert any("requests_per_minute must be >= 1" in e for e in errors)

    def test_validate_invalid_alert_threshold_low(self):
        """Test validation catches alert_threshold < 0."""
        config = QuotasConfig.from_dict({"budget": {"alert_threshold": -0.1}})
        errors = config.validate()
        assert len(errors) > 0
        assert any("alert_threshold must be between 0 and 1" in e for e in errors)

    def test_validate_invalid_alert_threshold_high(self):
        """Test validation catches alert_threshold > 1."""
        config = QuotasConfig.from_dict({"budget": {"alert_threshold": 1.5}})
        errors = config.validate()
        assert len(errors) > 0
        assert any("alert_threshold must be between 0 and 1" in e for e in errors)


class TestQuotasConfigIntegration:
    """Test QuotasConfig integration with PhoenixConfig."""

    def test_section_auto_discovered(self):
        """Test section is auto-discovered by SectionLoader."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        assert hasattr(config, "quotas")
        assert config.quotas is not None

    def test_section_accessible_via_getattr(self):
        """Test section accessible via config.quotas."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        section = config.quotas
        assert section.section_id == "quotas"

    def test_loads_from_yaml_file(self):
        """Test section loads actual values from config/quotas.yaml."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        # Should have values from quotas.yaml
        assert config.quotas.rate_limits.requests_per_minute == 10
        assert config.quotas.budget.cost_per_hour_usd == 2.0
        assert config.quotas.circuit_breaker.failure_threshold == 5
