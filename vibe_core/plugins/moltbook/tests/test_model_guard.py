"""
Model Guard — HARD FAIL if anyone changes the configured LLM model.

deepseek/deepseek-v3.2 is the ONLY approved model for OpenRouter.
No Anthropic. No OpenAI premium. Cost control is non-negotiable.
"""

import yaml
from pathlib import Path

_LLM_YAML = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "llm.yaml"
_REQUIRED_MODEL = "deepseek/deepseek-v3.2"

# Models that must NEVER appear as default (too expensive / wrong provider)
_BANNED_MODELS = [
    "anthropic/claude-opus-4",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-sonnet",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-3-haiku",
    "openai/gpt-4-turbo",
    "openai/gpt-4o",
    "openai/gpt-4",
]


def _load_openrouter_model() -> str:
    with open(_LLM_YAML) as f:
        cfg = yaml.safe_load(f)
    return cfg["providers"]["openrouter"]["default_model"]


class TestModelGuard:
    def test_openrouter_model_is_deepseek(self):
        """OpenRouter default MUST be deepseek/deepseek-v3.2. No exceptions."""
        model = _load_openrouter_model()
        assert model == _REQUIRED_MODEL, (
            f"WRONG MODEL: '{model}' — must be '{_REQUIRED_MODEL}'. "
            f"Change config/llm.yaml back. No Anthropic, no premium OpenAI."
        )

    def test_no_banned_models(self):
        """No expensive/banned models as OpenRouter default."""
        model = _load_openrouter_model()
        for banned in _BANNED_MODELS:
            assert model != banned, f"BANNED MODEL: '{banned}' is too expensive. Use '{_REQUIRED_MODEL}' instead."

    def test_llm_yaml_exists(self):
        """config/llm.yaml must exist."""
        assert _LLM_YAML.exists(), f"Missing: {_LLM_YAML}"
