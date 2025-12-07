"""Tests for runtime configuration section."""

from vibe_core.phoenix.sections.runtime.section_main import (
    ActionDefaultsConfig,
    CircuitRecoveryConfig,
    LimitsConfig,
    RuntimeConfig,
    TimeoutsConfig,
)


class TestTimeoutsConfig:
    """Test TimeoutsConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = TimeoutsConfig.from_dict({})
        assert config.operator_timeout == 300.0
        assert config.action_timeout == 300
        assert config.test_timeout_ms == 5000
        assert config.ritual_interval == 300.0

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "operator_timeout": 600.0,
            "action_timeout": 500,
            "test_timeout_ms": 10000,
            "ritual_interval": 600.0,
        }
        config = TimeoutsConfig.from_dict(data)
        assert config.operator_timeout == 600.0
        assert config.action_timeout == 500
        assert config.test_timeout_ms == 10000
        assert config.ritual_interval == 600.0

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = TimeoutsConfig.from_dict({"operator_timeout": 450.0})
        serialized = original.to_dict()
        restored = TimeoutsConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestLimitsConfig:
    """Test LimitsConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = LimitsConfig.from_dict({})
        assert config.max_recursion_depth == 5
        assert config.max_circuit_transitions == 20
        assert config.max_message_size == 1048576
        assert config.max_agent_restarts == 3
        assert config.event_history_size == 1000
        assert config.pulse_threshold == 10.0

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "max_recursion_depth": 10,
            "max_circuit_transitions": 30,
            "max_message_size": 2097152,
            "max_agent_restarts": 5,
            "event_history_size": 2000,
            "pulse_threshold": 20.0,
        }
        config = LimitsConfig.from_dict(data)
        assert config.max_recursion_depth == 10
        assert config.max_circuit_transitions == 30
        assert config.max_message_size == 2097152
        assert config.max_agent_restarts == 5
        assert config.event_history_size == 2000
        assert config.pulse_threshold == 20.0

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = LimitsConfig.from_dict({"max_recursion_depth": 8})
        serialized = original.to_dict()
        restored = LimitsConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestCircuitRecoveryConfig:
    """Test CircuitRecoveryConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = CircuitRecoveryConfig.from_dict({})
        assert config.reflection_interval == 3
        assert config.stuck_threshold == 3
        assert config.max_retry_attempts == 5

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "reflection_interval": 5,
            "stuck_threshold": 5,
            "max_retry_attempts": 10,
        }
        config = CircuitRecoveryConfig.from_dict(data)
        assert config.reflection_interval == 5
        assert config.stuck_threshold == 5
        assert config.max_retry_attempts == 10

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = CircuitRecoveryConfig.from_dict({"reflection_interval": 7})
        serialized = original.to_dict()
        restored = CircuitRecoveryConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestActionDefaultsConfig:
    """Test ActionDefaultsConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = ActionDefaultsConfig.from_dict({})
        assert config.retry_count == 3

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {"retry_count": 5}
        config = ActionDefaultsConfig.from_dict(data)
        assert config.retry_count == 5

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = ActionDefaultsConfig.from_dict({"retry_count": 7})
        serialized = original.to_dict()
        restored = ActionDefaultsConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestRuntimeConfig:
    """Test RuntimeConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = RuntimeConfig.from_dict({})
        assert config.section_id == "runtime"
        assert config.source_file == "runtime.yaml"
        assert isinstance(config.timeouts, TimeoutsConfig)
        assert isinstance(config.limits, LimitsConfig)
        assert isinstance(config.circuit_recovery, CircuitRecoveryConfig)
        assert isinstance(config.action_defaults, ActionDefaultsConfig)

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "timeouts": {
                "operator_timeout": 600.0,
                "action_timeout": 500,
            },
            "limits": {
                "max_recursion_depth": 10,
                "max_message_size": 2097152,
            },
            "circuit_recovery": {
                "reflection_interval": 5,
                "max_retry_attempts": 10,
            },
            "action_defaults": {
                "retry_count": 5,
            },
        }
        config = RuntimeConfig.from_dict(data)
        assert config.timeouts.operator_timeout == 600.0
        assert config.limits.max_recursion_depth == 10
        assert config.circuit_recovery.reflection_interval == 5
        assert config.action_defaults.retry_count == 5

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = RuntimeConfig.from_dict(
            {
                "timeouts": {"operator_timeout": 450.0},
                "limits": {"max_recursion_depth": 8},
            }
        )
        serialized = original.to_dict()
        restored = RuntimeConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()

    def test_validate_valid_config(self):
        """Test validation passes for valid config."""
        config = RuntimeConfig.from_dict({})
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_max_recursion_depth(self):
        """Test validation catches invalid max_recursion_depth."""
        config = RuntimeConfig.from_dict({"limits": {"max_recursion_depth": 0}})
        errors = config.validate()
        assert len(errors) > 0
        assert any("max_recursion_depth must be >= 1" in e for e in errors)

    def test_validate_invalid_max_message_size(self):
        """Test validation catches invalid max_message_size."""
        config = RuntimeConfig.from_dict({"limits": {"max_message_size": 512}})
        errors = config.validate()
        assert len(errors) > 0
        assert any("max_message_size must be >= 1024" in e for e in errors)


class TestRuntimeConfigIntegration:
    """Test RuntimeConfig integration with PhoenixConfig."""

    def test_section_auto_discovered(self):
        """Test section is auto-discovered by SectionLoader."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        assert hasattr(config, "runtime")
        assert config.runtime is not None

    def test_section_accessible_via_getattr(self):
        """Test section accessible via config.runtime."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        section = config.runtime
        assert section.section_id == "runtime"

    def test_loads_from_yaml_file(self):
        """Test section loads actual values from config/runtime.yaml."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        # Should have values from runtime.yaml
        assert config.runtime.timeouts.operator_timeout == 300.0
        assert config.runtime.limits.max_recursion_depth == 5
        assert config.runtime.circuit_recovery.reflection_interval == 3
        assert config.runtime.action_defaults.retry_count == 3
