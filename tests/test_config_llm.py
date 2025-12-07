"""Tests for llm configuration section."""

import pytest
from vibe_core.phoenix.sections.llm.section_main import LLMConfig, LocalLLMConfig, ProviderEntry


class TestLocalLLMConfig:
    """Test LocalLLMConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = LocalLLMConfig.from_dict({})
        assert config.model_name == "qwen2.5-0.5b-instruct-q4_k_m.gguf"
        assert config.model_repo == "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
        assert config.n_ctx == 2048
        assert config.n_threads is None
        assert config.n_batch == 512
        assert config.default_max_tokens == 256
        assert config.default_temperature == 0.7

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "model_name": "custom-model.gguf",
            "model_repo": "Custom/Repo",
            "n_ctx": 4096,
            "n_threads": 8,
            "n_batch": 1024,
            "default_max_tokens": 512,
            "default_temperature": 0.9,
        }
        config = LocalLLMConfig.from_dict(data)
        assert config.model_name == "custom-model.gguf"
        assert config.model_repo == "Custom/Repo"
        assert config.n_ctx == 4096
        assert config.n_threads == 8
        assert config.n_batch == 1024
        assert config.default_max_tokens == 512
        assert config.default_temperature == 0.9

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = LocalLLMConfig.from_dict({"n_ctx": 4096, "n_threads": 4})
        serialized = original.to_dict()
        restored = LocalLLMConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()


class TestProviderEntry:
    """Test ProviderEntry loading."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = ProviderEntry.from_dict({})
        assert config.default_model == ""
        assert config.api_key_env == ""
        assert config.base_url is None

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "default_model": "gpt-4",
            "api_key_env": "OPENAI_KEY",
            "base_url": "https://api.openai.com",
        }
        config = ProviderEntry.from_dict(data)
        assert config.default_model == "gpt-4"
        assert config.api_key_env == "OPENAI_KEY"
        assert config.base_url == "https://api.openai.com"

    def test_to_dict_with_base_url(self):
        """Test serialization includes base_url if set."""
        entry = ProviderEntry(
            default_model="gpt-4",
            api_key_env="OPENAI_KEY",
            base_url="https://api.openai.com",
        )
        result = entry.to_dict()
        assert "base_url" in result
        assert result["base_url"] == "https://api.openai.com"

    def test_to_dict_without_base_url(self):
        """Test serialization excludes base_url if None."""
        entry = ProviderEntry(default_model="gpt-4", api_key_env="OPENAI_KEY")
        result = entry.to_dict()
        assert "base_url" not in result


class TestLLMConfig:
    """Test LLMConfig loading and validation."""

    def test_from_dict_defaults(self):
        """Test loading with empty dict uses defaults."""
        config = LLMConfig.from_dict({})
        assert config.section_id == "llm"
        assert config.source_file == "llm.yaml"
        assert isinstance(config.local, LocalLLMConfig)
        assert config.providers == {}

    def test_from_dict_custom_values(self):
        """Test loading with custom values."""
        data = {
            "local": {
                "model_name": "custom.gguf",
                "n_ctx": 4096,
            },
            "providers": {
                "anthropic": {
                    "default_model": "claude-3-opus",
                    "api_key_env": "ANTHROPIC_API_KEY",
                },
                "openai": {
                    "default_model": "gpt-4",
                    "api_key_env": "OPENAI_API_KEY",
                },
            },
        }
        config = LLMConfig.from_dict(data)
        assert config.local.model_name == "custom.gguf"
        assert config.local.n_ctx == 4096
        assert "anthropic" in config.providers
        assert "openai" in config.providers
        assert config.providers["anthropic"].default_model == "claude-3-opus"

    def test_to_dict_roundtrip(self):
        """Test serialization roundtrip."""
        original = LLMConfig.from_dict(
            {
                "local": {"n_ctx": 4096},
                "providers": {
                    "anthropic": {
                        "default_model": "claude-3-opus",
                        "api_key_env": "ANTHROPIC_API_KEY",
                    }
                },
            }
        )
        serialized = original.to_dict()
        restored = LLMConfig.from_dict(serialized)
        assert original.to_dict() == restored.to_dict()

    def test_validate_valid_config(self):
        """Test validation passes for valid config."""
        config = LLMConfig.from_dict({})
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_config(self):
        """Test validation catches invalid config."""
        config = LLMConfig.from_dict({"local": {"model_name": ""}})
        errors = config.validate()
        assert len(errors) > 0
        assert "model_name is required" in errors[0]

    def test_get_provider_exists(self):
        """Test get_provider returns provider if exists."""
        config = LLMConfig.from_dict(
            {
                "providers": {
                    "anthropic": {
                        "default_model": "claude-3-opus",
                        "api_key_env": "ANTHROPIC_API_KEY",
                    }
                }
            }
        )
        provider = config.get_provider("anthropic")
        assert provider is not None
        assert provider.default_model == "claude-3-opus"

    def test_get_provider_not_exists(self):
        """Test get_provider returns None if not exists."""
        config = LLMConfig.from_dict({})
        provider = config.get_provider("nonexistent")
        assert provider is None


class TestLLMConfigIntegration:
    """Test LLMConfig integration with PhoenixConfig."""

    def test_section_auto_discovered(self):
        """Test section is auto-discovered by SectionLoader."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        assert hasattr(config, "llm")
        assert config.llm is not None

    def test_section_accessible_via_getattr(self):
        """Test section accessible via config.llm."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        section = config.llm
        assert section.section_id == "llm"

    def test_loads_from_yaml_file(self):
        """Test section loads actual values from config/llm.yaml."""
        from vibe_core.phoenix.config import get_config, reset_config

        reset_config()
        config = get_config()
        # Should have providers from llm.yaml
        assert "anthropic" in config.llm.providers
        assert "openai" in config.llm.providers
        assert config.llm.local.model_name == "qwen2.5-0.5b-instruct-q4_k_m.gguf"
