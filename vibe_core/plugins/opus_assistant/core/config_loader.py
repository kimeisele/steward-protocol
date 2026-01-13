"""
OPUS Assistant Config Loader - Fraktale Config Pattern.

OPUS-029: Proper config loading with layered merging.

Config Hierarchy (later overrides earlier):
1. defaults.yaml (shipped with plugin)
2. config/opus.yaml (system-level overrides)
3. Runtime overrides (passed to methods)

This follows Phoenix config pattern - no hardcoding.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x3dfbd51b"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dicts. Override wins on conflicts.

    Args:
        base: Base config dict
        override: Override config dict

    Returns:
        Merged dict (new instance, doesn't modify inputs)
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


class ConfigLoader:
    """
    Loads and merges config from multiple sources.

    Fraktale Pattern:
    - Plugin ships defaults.yaml
    - System can override in config/opus.yaml
    - Runtime can override specific values

    Usage:
        loader = ConfigLoader(workspace_root=Path("."))
        config = loader.load()
        # config is merged: defaults + opus.yaml overrides
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize config loader.

        Args:
            workspace_root: Project root directory
        """
        self._root = Path(workspace_root)
        self._plugin_dir = Path(__file__).parent.parent
        self._cached_config: Optional[Dict[str, Any]] = None

    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load merged config.

        Args:
            force_reload: Bypass cache and reload from files

        Returns:
            Merged config dict
        """
        if self._cached_config is not None and not force_reload:
            return self._cached_config

        # Layer 1: Plugin defaults
        defaults = self._load_defaults()

        # Layer 2: System overrides (config/opus.yaml)
        system = self._load_system_config()

        # Merge
        self._cached_config = deep_merge(defaults, system)

        return self._cached_config

    def _load_defaults(self) -> Dict[str, Any]:
        """Load defaults.yaml from plugin directory."""
        defaults_path = self._plugin_dir / "defaults.yaml"

        if not defaults_path.exists():
            return {}

        try:
            return yaml.safe_load(defaults_path.read_text()) or {}
        except Exception:
            return {}

    def _load_system_config(self) -> Dict[str, Any]:
        """Load system overrides from config/opus.yaml."""
        system_path = self._root / "config" / "opus.yaml"

        if not system_path.exists():
            return {}

        try:
            data = yaml.safe_load(system_path.read_text()) or {}
            # The opus.yaml might have verification/etc at root level
            # We need to restructure to match our schema
            return self._normalize_system_config(data)
        except Exception:
            return {}

    def _normalize_system_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize system config to match plugin schema.

        opus.yaml might have flat structure, we need nested.
        """
        result = {}

        # Map verification section
        if "verification" in data:
            result["verification"] = data["verification"]

        # Map other known sections
        for key in ["drift", "generation", "preservation", "kernel_tick", "gad_000"]:
            if key in data:
                result[key] = data[key]

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "verification.enabled")
            default: Default value if key not found

        Returns:
            Config value or default
        """
        config = self.load()
        parts = key.split(".")
        current = config

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def reload(self) -> Dict[str, Any]:
        """Force reload config from files."""
        return self.load(force_reload=True)
