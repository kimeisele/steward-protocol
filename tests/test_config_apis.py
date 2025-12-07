"""Tests for apis configuration section."""

import os
import pytest
from vibe_core.phoenix.sections.apis.section_main import APIsConfig, ExternalAPIEntry


class TestExternalAPIEntry:
    """Test ExternalAPIEntry loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = ExternalAPIEntry.from_dict({})
        assert config.env_var == ""
        assert config.description == ""
        assert config.required is False
        assert config.additional_vars == []

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "env_var": "TEST_API_KEY",
            "description": "Test API",
            "required": True,
            "additional_vars": ["TEST_SECRET", "TEST_TOKEN"],
        }
        config = ExternalAPIEntry.from_dict(data)
        assert config.env_var == "TEST_API_KEY"
        assert config.description == "Test API"
        assert config.required is True
        assert config.additional_vars == ["TEST_SECRET", "TEST_TOKEN"]

    def test_to_dict_with_additional_vars(self):
        """Test serialization includes additional_vars if set."""
        entry = ExternalAPIEntry(
            env_var="TEST_KEY",
            description="Test",
            required=True,
            additional_vars=["SECRET"],
        )
        result = entry.to_dict()
        assert "additional_vars" in result
        assert result["additional_vars"] == ["SECRET"]

    def test_to_dict_without_additional_vars(self):
        """Test serialization excludes additional_vars if empty."""
        entry = ExternalAPIEntry(env_var="TEST_KEY", description="Test")
        result = entry.to_dict()
        assert "additional_vars" not in result

    def test_get_key_returns_env_value(self):
        """Test get_key returns value from environment."""
        os.environ["TEST_API_KEY_123"] = "secret_value"
        entry = ExternalAPIEntry(env_var="TEST_API_KEY_123")
        assert entry.get_key() == "secret_value"
        del os.environ["TEST_API_KEY_123"]

    def test_get_key_returns_none_if_not_set(self):
        """Test get_key returns None if env var not set."""
        entry = ExternalAPIEntry(env_var="NONEXISTENT_KEY_XYZ")
        assert entry.get_key() is None

    def test_is_configured_true_if_env_set(self):
        """Test is_configured returns True if key is set."""
        os.environ["TEST_API_KEY_456"] = "value"
        entry = ExternalAPIEntry(env_var="TEST_API_KEY_456")
        assert entry.is_configured() is True
        del os.environ["TEST_API_KEY_456"]

    def test_is_configured_false_if_env_not_set(self):
        """Test is_configured returns False if key not set."""
        entry = ExternalAPIEntry(env_var="NONEXISTENT_KEY_ABC")
        assert entry.is_configured() is False


class TestAPIsConfig:
    """Test APIsConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = APIsConfig.from_dict({})
        assert config.section_id == "apis"
        assert config.source_file == "apis.yaml"
        assert config.external == {}

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "external": {
                "tavily": {
                    "env_var": "TAVILY_API_KEY",
                    "description": "Web search API",
                    "required": False,
                },
                "twitter": {
                    "env_var": "TWITTER_API_KEY",
                    "description": "Twitter API",
                    "required": True,
                    "additional_vars": ["TWITTER_SECRET"],
                },
            }
        }
        config = APIsConfig.from_dict(data)
        assert "tavily" in config.external
        assert "twitter" in config.external
        assert config.external["tavily"].env_var == "TAVILY_API_KEY"
        assert config.external["twitter"].required is True
        assert config.external["twitter"].additional_vars == ["TWITTER_SECRET"]

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = APIsConfig.from_dict(
            {
                "external": {
                    "test": {
                        "env_var": "TEST_KEY",
                        "description": "Test API",
                    }
                }
            }
        )
        serialized = original.to_dict()
        restored = APIsConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()

    def test_validate_valid_config(self):
        """Test validation passes for valid config with no required APIs."""
        config = APIsConfig.from_dict(
            {
                "external": {
                    "optional": {
                        "env_var": "OPTIONAL_KEY",
                        "required": False,
                    }
                }
            }
        )
        errors = config.validate()
        assert errors == []

    def test_validate_required_api_not_configured(self):
        """Test validation catches required API not configured."""
        config = APIsConfig.from_dict(
            {
                "external": {
                    "required_api": {
                        "env_var": "REQUIRED_MISSING_KEY_XYZ",
                        "required": True,
                    }
                }
            }
        )
        errors = config.validate()
        assert len(errors) > 0
        assert any("required_api" in e and "not configured" in e for e in errors)

    def test_validate_required_api_configured(self):
        """Test validation passes if required API is configured."""
        os.environ["REQUIRED_TEST_KEY_789"] = "value"
        config = APIsConfig.from_dict(
            {
                "external": {
                    "required_api": {
                        "env_var": "REQUIRED_TEST_KEY_789",
                        "required": True,
                    }
                }
            }
        )
        errors = config.validate()
        assert errors == []
        del os.environ["REQUIRED_TEST_KEY_789"]

    def test_get_api_exists(self):
        """Test get_api returns API if exists."""
        config = APIsConfig.from_dict(
            {
                "external": {
                    "tavily": {
                        "env_var": "TAVILY_API_KEY",
                        "description": "Web search",
                    }
                }
            }
        )
        api = config.get_api("tavily")
        assert api is not None
        assert api.env_var == "TAVILY_API_KEY"

    def test_get_api_not_exists(self):
        """Test get_api returns None if not exists."""
        config = APIsConfig.from_dict({})
        api = config.get_api("nonexistent")
        assert api is None

    def test_get_env_var_exists(self):
        """Test get_env_var returns env var name if API exists."""
        config = APIsConfig.from_dict(
            {"external": {"test": {"env_var": "TEST_KEY"}}}
        )
        env_var = config.get_env_var("test")
        assert env_var == "TEST_KEY"

    def test_get_env_var_not_exists_with_fallback(self):
        """Test get_env_var returns fallback if API doesn't exist."""
        config = APIsConfig.from_dict({})
        env_var = config.get_env_var("nonexistent", "FALLBACK_KEY")
        assert env_var == "FALLBACK_KEY"

    def test_list_configured(self):
        """Test list_configured returns only configured APIs."""
        os.environ["CONFIGURED_KEY_111"] = "value"
        config = APIsConfig.from_dict(
            {
                "external": {
                    "configured": {"env_var": "CONFIGURED_KEY_111"},
                    "not_configured": {"env_var": "NOT_SET_KEY_222"},
                }
            }
        )
        configured = config.list_configured()
        assert "configured" in configured
        assert "not_configured" not in configured
        del os.environ["CONFIGURED_KEY_111"]

    def test_list_missing(self):
        """Test list_missing returns only missing APIs."""
        os.environ["CONFIGURED_KEY_333"] = "value"
        config = APIsConfig.from_dict(
            {
                "external": {
                    "configured": {"env_var": "CONFIGURED_KEY_333"},
                    "missing": {"env_var": "MISSING_KEY_444"},
                }
            }
        )
        missing = config.list_missing()
        assert "missing" in missing
        assert "configured" not in missing
        del os.environ["CONFIGURED_KEY_333"]


class TestAPIsConfigIntegration:
    """Test APIsConfig integration with PhoenixConfig."""

    def test_section_auto_discovered(self):
        """Test section is auto-discovered by SectionLoader."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        assert hasattr(config, "apis")
        assert config.apis is not None

    def test_section_accessible_via_getattr(self):
        """Test section accessible via config.apis."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        section = config.apis
        assert section.section_id == "apis"

    def test_loads_from_yaml_file(self):
        """Test section loads actual values from config/apis.yaml."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        # Should have APIs from apis.yaml
        assert "tavily" in config.apis.external
        assert "twitter" in config.apis.external
        assert config.apis.external["tavily"].env_var == "TAVILY_API_KEY"
