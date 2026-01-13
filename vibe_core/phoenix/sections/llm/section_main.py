"""
LLM Configuration - Local LLM and provider settings.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/llm/
    ARTHA: Parsed from config/llm.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as LLMConfig dataclass
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x19f53a32"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LocalLLMConfig:
    """Local LLM (llama.cpp) configuration."""

    model_name: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    model_repo: str = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    n_ctx: int = 2048
    n_threads: Optional[int] = None  # None = auto-detect
    n_batch: int = 512
    default_max_tokens: int = 256
    default_temperature: float = 0.7

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalLLMConfig":
        return cls(
            model_name=data.get("model_name", "qwen2.5-0.5b-instruct-q4_k_m.gguf"),
            model_repo=data.get("model_repo", "Qwen/Qwen2.5-0.5B-Instruct-GGUF"),
            n_ctx=data.get("n_ctx", 2048),
            n_threads=data.get("n_threads"),
            n_batch=data.get("n_batch", 512),
            default_max_tokens=data.get("default_max_tokens", 256),
            default_temperature=data.get("default_temperature", 0.7),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_repo": self.model_repo,
            "n_ctx": self.n_ctx,
            "n_threads": self.n_threads,
            "n_batch": self.n_batch,
            "default_max_tokens": self.default_max_tokens,
            "default_temperature": self.default_temperature,
        }


@dataclass
class ProviderEntry:
    """Single LLM provider configuration."""

    default_model: str = ""
    api_key_env: str = ""
    base_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderEntry":
        return cls(
            default_model=data.get("default_model", ""),
            api_key_env=data.get("api_key_env", ""),
            base_url=data.get("base_url"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "default_model": self.default_model,
            "api_key_env": self.api_key_env,
        }
        if self.base_url:
            result["base_url"] = self.base_url
        return result


@dataclass
class LLMConfig:
    """
    LLM Configuration.

    Auto-discovered by SectionLoader -> loads from config/llm.yaml
    """

    section_id: str = "llm"
    source_file: str = "llm.yaml"

    local: LocalLLMConfig = field(default_factory=LocalLLMConfig)
    providers: Dict[str, ProviderEntry] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        providers = {}
        for name, pdata in data.get("providers", {}).items():
            providers[name] = ProviderEntry.from_dict(pdata)

        return cls(
            local=LocalLLMConfig.from_dict(data.get("local", {})),
            providers=providers,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "local": self.local.to_dict(),
            "providers": {name: p.to_dict() for name, p in self.providers.items()},
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.local.model_name:
            errors.append("local.model_name is required")
        return errors

    def get_provider(self, name: str) -> Optional[ProviderEntry]:
        """Get provider config by name."""
        return self.providers.get(name)
