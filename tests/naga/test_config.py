"""
Tests for NagaConfig.

Tests:
- Default values
- Environment variable overrides
- Factory methods
- Validation
"""

import os
from unittest.mock import patch

import pytest


class TestNagaConfigDefaults:
    """Test default configuration values."""

    def test_default_trust_mode_is_strict(self):
        """Default trust mode should be strict (production safe)."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        assert config.takshaka.trust_mode == "strict"

    def test_default_gossip_disabled(self):
        """Gossip should be disabled by default (federation not ready)."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        assert config.sesha.gossip_enabled is False

    def test_default_toxicity_threshold(self):
        """Default toxicity threshold should be 0.3."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        assert config.takshaka.toxicity_threshold == 0.3

    def test_all_nagas_enabled_by_default(self):
        """All NAGAs should be enabled by default."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        assert config.sesha.enabled is True
        assert config.vasuki.enabled is True
        assert config.takshaka.enabled is True


class TestNagaConfigEnvironmentOverrides:
    """Test environment variable overrides."""

    def test_naga_strict_enables_strict_mode(self):
        """NAGA_STRICT=1 should set trust_mode to strict."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        with patch.dict(os.environ, {"NAGA_STRICT": "1"}):
            config = NagaConfig()
            assert config.takshaka.trust_mode == "strict"

    def test_naga_trust_mode_permissive(self):
        """NAGA_TRUST_MODE=permissive should override."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        with patch.dict(os.environ, {"NAGA_TRUST_MODE": "permissive"}):
            config = NagaConfig()
            assert config.takshaka.trust_mode == "permissive"

    def test_naga_gossip_enabled(self):
        """NAGA_GOSSIP_ENABLED=1 should enable gossip."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        with patch.dict(os.environ, {"NAGA_GOSSIP_ENABLED": "1"}):
            config = NagaConfig()
            assert config.sesha.gossip_enabled is True

    def test_naga_toxicity_threshold_override(self):
        """NAGA_TOXICITY_THRESHOLD should override threshold."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        with patch.dict(os.environ, {"NAGA_TOXICITY_THRESHOLD": "0.5"}):
            config = NagaConfig()
            assert config.takshaka.toxicity_threshold == 0.5

    def test_invalid_toxicity_threshold_ignored(self):
        """Invalid NAGA_TOXICITY_THRESHOLD should be ignored."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        with patch.dict(os.environ, {"NAGA_TOXICITY_THRESHOLD": "invalid"}):
            config = NagaConfig()
            assert config.takshaka.toxicity_threshold == 0.3  # default


class TestNagaConfigFactoryMethods:
    """Test factory methods."""

    def test_permissive_factory(self):
        """NagaConfig.permissive() should create permissive config."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.permissive()
        assert config.takshaka.trust_mode == "permissive"
        assert config.sesha.gossip_enabled is False

    def test_production_factory(self):
        """NagaConfig.production() should create strict config."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.production()
        assert config.takshaka.trust_mode == "strict"
        assert config.vasuki.sign_outbound is True

    def test_disabled_factory(self):
        """NagaConfig.disabled() should disable all NAGAs."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.disabled()
        assert config.sesha.enabled is False
        assert config.vasuki.enabled is False
        assert config.takshaka.enabled is False


class TestNagaConfigValidation:
    """Test configuration validation."""

    def test_valid_config_no_errors(self):
        """Valid config should have no validation errors."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        errors = config.validate()
        assert len(errors) == 0

    def test_invalid_trust_mode(self):
        """Invalid trust mode should produce error."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        config.takshaka.trust_mode = "invalid"
        errors = config.validate()
        assert any("trust_mode" in e for e in errors)

    def test_invalid_toxicity_threshold_too_high(self):
        """Toxicity threshold > 1.0 should produce error."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        config.takshaka.toxicity_threshold = 1.5
        errors = config.validate()
        assert any("toxicity_threshold" in e for e in errors)

    def test_invalid_toxicity_threshold_negative(self):
        """Negative toxicity threshold should produce error."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig()
        config.takshaka.toxicity_threshold = -0.1
        errors = config.validate()
        assert any("toxicity_threshold" in e for e in errors)


class TestNagaConfigSerialization:
    """Test to_dict/from_dict serialization."""

    def test_round_trip(self):
        """Config should survive to_dict -> from_dict round trip."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        original = NagaConfig()
        original.takshaka.trust_mode = "permissive"
        original.sesha.gossip_enabled = True

        data = original.to_dict()
        restored = NagaConfig.from_dict(data)

        assert restored.takshaka.trust_mode == "permissive"
        assert restored.sesha.gossip_enabled is True

    def test_from_empty_dict(self):
        """from_dict with empty dict should use defaults."""
        from vibe_core.phoenix.sections.naga.section_main import NagaConfig

        config = NagaConfig.from_dict({})
        assert config.takshaka.trust_mode == "strict"
        assert config.sesha.enabled is True
