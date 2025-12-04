"""
Layer 3: Phoenix Configuration Engine
Dynamic wiring of implementations to protocols.

This module provides the runtime system for connecting implementations
(Layer 2) to protocols (Layer 1) based on configuration.

DEPRECATED: This module is deprecated in favor of vibe_core.phoenix.
Use `from vibe_core.phoenix import get_config` instead of `get_phoenix_engine()`.

The new Phoenix Config V2 provides:
- Typed dataclass composition (not flat dict access)
- Fractal configuration pattern
- Hot-reload for routing rules
- Unified access to all config sources

Migration:
    # Old:
    from vibe_core.phoenix_config import get_phoenix_engine
    engine = get_phoenix_engine()
    provider = engine.get("providers.llm_provider", "")

    # New:
    from vibe_core.phoenix import get_config
    config = get_config()
    provider = config.kernel.providers.llm_provider
"""

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml

from vibe_core.protocols import VibeAgent

logger = logging.getLogger(__name__)


class PhoenixConfigEngine:
    """Dynamically wires implementations based on phoenix.yaml"""

    def __init__(self, config_path: str = "config/phoenix.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._registry: Dict[str, Type] = {}
        self._loaded = False

        try:
            self._load_config()
            self._loaded = True
            logger.info(f"✅ Phoenix engine initialized from {config_path}")
        except Exception as e:
            logger.warning(f"⚠️  Phoenix config not available: {e}")
            self.config = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load phoenix.yaml"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Phoenix config not found: {self.config_path}")

        with open(self.config_path) as f:
            self.config = yaml.safe_load(f) or {}

        return self.config

    def _import_class(self, class_path: str) -> Type:
        """
        Import class from module:class string

        Args:
            class_path: String like "vibe_core.agents.llm_agent:SimpleLLMAgent"

        Returns:
            The imported class
        """
        try:
            if ":" not in class_path:
                raise ValueError(f"Invalid class path: {class_path}. Use 'module:ClassName'")

            module_name, class_name = class_path.split(":", 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except Exception as e:
            logger.error(f"Failed to import {class_path}: {e}")
            raise

    def enforce_import_order(self) -> None:
        """
        Pre-import modules in correct order to avoid circular dependencies
        """
        if not self.config or "imports" not in self.config:
            logger.debug("No import order configured")
            return

        import_order = self.config.get("imports", {}).get("order", [])
        for module_name in import_order:
            try:
                importlib.import_module(module_name)
                logger.debug(f"Pre-imported: {module_name}")
            except ImportError as e:
                logger.warning(f"Could not pre-import {module_name}: {e}")

    def wire_agents(self) -> Dict[str, Type[VibeAgent]]:
        """
        Wire all agent implementations from config

        Returns:
            Dict mapping agent names to their classes
        """
        agents = {}

        if not self._loaded or "agents" not in self.config:
            logger.warning("No agents configured in Phoenix config")
            return agents

        system_agents = self.config.get("agents", {}).get("system_agents", [])

        for agent_config in system_agents:
            try:
                if not agent_config.get("enabled", True):
                    logger.debug(f"Agent {agent_config.get('name')} is disabled")
                    continue

                agent_name = agent_config.get("name")
                class_path = agent_config.get("class")

                if not agent_name or not class_path:
                    logger.warning(f"Invalid agent config: {agent_config}")
                    continue

                agent_class = self._import_class(class_path)
                agents[agent_name] = agent_class
                logger.info(f"Wired agent: {agent_name} → {class_path}")

            except Exception as e:
                logger.error(f"Failed to wire agent {agent_config.get('name')}: {e}")
                # Continue with other agents instead of failing

        return agents

    def wire_kernel_components(self) -> Dict[str, Type]:
        """
        Wire kernel components (ledger, scheduler, registry)

        Returns:
            Dict mapping component names to their classes
        """
        components = {}

        if not self._loaded or "system" not in self.config:
            logger.warning("No system components configured")
            return components

        kernel_config = self.config.get("system", {}).get("kernel", {})

        for component_name, class_path in kernel_config.items():
            try:
                component_class = self._import_class(class_path)
                components[component_name] = component_class
                logger.info(f"Wired component: {component_name} → {class_path}")
            except Exception as e:
                logger.error(f"Failed to wire component {component_name}: {e}")

        return components

    def get_playbook_executor_agent(self) -> Type[VibeAgent]:
        """
        Get configured executor agent class for playbooks

        Returns:
            The agent class to use as playbook executor
        """
        if not self._loaded or "playbook" not in self.config:
            raise RuntimeError("Playbook executor not configured")

        class_path = self.config["playbook"].get("executor_agent")
        if not class_path:
            raise RuntimeError("executor_agent not specified in playbook config")

        return self._import_class(class_path)

    def get_config(self) -> Dict[str, Any]:
        """Get the raw configuration dict"""
        return self.config.copy()

    def is_loaded(self) -> bool:
        """Check if config was successfully loaded"""
        return self._loaded

    # =========================================================================
    # UI Enhancement: Settings Interface Methods
    # =========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value by dotted key path.

        Args:
            key: Dotted path like "providers.llm_provider"
            default: Default value if not found

        Returns:
            Config value or default
        """
        parts = key.split(".")
        value = self.config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """
        Set config value by dotted key path.

        Args:
            key: Dotted path like "features.live_fire_enabled"
            value: New value to set

        Returns:
            True if successful, False otherwise
        """
        parts = key.split(".")
        data = self.config

        # Navigate to parent
        for part in parts[:-1]:
            if part not in data:
                data[part] = {}
            data = data[part]

        # Set value
        old_value = data.get(parts[-1])
        data[parts[-1]] = value
        logger.info(f"⚙️  Config: {key} = {value} (was: {old_value})")
        return True

    def save(self) -> bool:
        """Save config back to YAML file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"💾 Config saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            return False

    @property
    def llm_provider(self) -> str:
        """Current LLM provider class path."""
        return self.get("providers.llm_provider", "")

    @property
    def live_fire_enabled(self) -> bool:
        """Whether live fire mode is enabled."""
        return self.get("features.live_fire_enabled", False)

    @property
    def debug_mode(self) -> bool:
        """Whether debug mode is enabled."""
        return self.get("features.debug_mode", False)

    # NOTE: get_provider_info() removed - use vibe_core.settings.sections.provider.get_provider_info_from_config()
    # This keeps business logic in the section, not in infrastructure.


# Singleton instance
_engine: Optional[PhoenixConfigEngine] = None


def get_phoenix_engine() -> PhoenixConfigEngine:
    """
    Get singleton Phoenix engine instance

    Returns:
        The Phoenix configuration engine
    """
    global _engine
    if _engine is None:
        _engine = PhoenixConfigEngine()
    return _engine


def reset_phoenix_engine() -> None:
    """Reset the singleton (mainly for testing)"""
    global _engine
    _engine = None
