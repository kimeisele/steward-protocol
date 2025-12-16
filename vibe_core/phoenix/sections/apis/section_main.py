"""
APIs Configuration - External API registry.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/apis/
    ARTHA: Parsed from config/apis.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as APIsConfig dataclass

Keys stay in environment variables - this section defines
WHERE to find them (which env var names).
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExternalAPIEntry:
    """Single external API configuration."""

    env_var: str = ""
    description: str = ""
    required: bool = False
    additional_vars: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExternalAPIEntry":
        return cls(
            env_var=data.get("env_var", ""),
            description=data.get("description", ""),
            required=data.get("required", False),
            additional_vars=data.get("additional_vars", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "env_var": self.env_var,
            "description": self.description,
            "required": self.required,
        }
        if self.additional_vars:
            result["additional_vars"] = self.additional_vars
        return result

    def get_key(self) -> Optional[str]:
        """Get the API key from environment."""
        return os.getenv(self.env_var) if self.env_var else None

    def is_configured(self) -> bool:
        """Check if API key is set in environment."""
        return bool(self.get_key())


@dataclass
class APIsConfig:
    """
    External APIs Configuration.

    Auto-discovered by SectionLoader -> loads from config/apis.yaml
    """

    section_id: str = "apis"
    source_file: str = "apis.yaml"

    external: Dict[str, ExternalAPIEntry] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIsConfig":
        external = {}
        for name, edata in data.get("external", {}).items():
            external[name] = ExternalAPIEntry.from_dict(edata)

        return cls(external=external)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "external": {name: e.to_dict() for name, e in self.external.items()},
        }

    def validate(self) -> List[str]:
        errors = []
        for name, entry in self.external.items():
            if entry.required and not entry.is_configured():
                errors.append(f"Required API '{name}' not configured (set {entry.env_var})")
        return errors

    def get_api(self, name: str) -> Optional[ExternalAPIEntry]:
        """Get API config by name."""
        return self.external.get(name)

    def get_env_var(self, name: str, fallback: str = "") -> str:
        """Get env var name for an API, with fallback."""
        entry = self.external.get(name)
        return entry.env_var if entry else fallback

    def list_configured(self) -> List[str]:
        """List all APIs that have keys configured."""
        return [name for name, entry in self.external.items() if entry.is_configured()]

    def list_missing(self) -> List[str]:
        """List all APIs that are missing keys."""
        return [name for name, entry in self.external.items() if not entry.is_configured()]
