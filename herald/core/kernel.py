"""
VIBE KERNEL - System Bootloader & Dependency Injection
Ensures HERALD runs identically in container, CI/CD, and local environments.

Architecture Pattern: VibeOS Standard
- Single Source of Truth (YAML config)
- Explicit environment validation (GAD-000)
- Structured error handling
- Capability-based DI
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from importlib import import_module


class KernelBootError(Exception):
    """Structured kernel boot failure."""
    pass


class VibeKernel:
    """
    Industrial-grade system bootloader and dependency injector.

    Guarantees:
    1. Environment validation (required vars check)
    2. Config loading (single YAML source)
    3. Capability registration and lifecycle
    4. Unified error handling (GAD-000 format)
    """

    def __init__(self, config_path: str = "herald/config/system.yaml"):
        """
        Initialize kernel with config.

        Args:
            config_path: Path to system.yaml (defaults to project structure)

        Raises:
            KernelBootError: If config missing or invalid
        """
        self.config_path = Path(config_path)
        self.config = None
        self.logger = self._setup_logging()
        self.capabilities = {}
        self._loaded = False
        self._booted = False

    def _setup_logging(self) -> logging.Logger:
        """Configure logging from scratch."""
        logger = logging.getLogger("VIBE_KERNEL")

        if not logger.handlers:  # Only setup once
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def _load_config(self) -> Dict[str, Any]:
        """
        Load YAML configuration (Single Source of Truth).

        Raises:
            KernelBootError: If config file missing or invalid
        """
        if not self.config_path.exists():
            error = {
                "error": "CONFIG_MISSING",
                "config_path": str(self.config_path),
                "message": f"System config not found at {self.config_path}",
                "action": "Ensure herald/config/system.yaml exists"
            }
            self.logger.critical(json.dumps(error))
            raise KernelBootError(error["message"])

        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            if not config or "system" not in config:
                raise ValueError("Invalid config: missing 'system' section")

            return config

        except yaml.YAMLError as e:
            error = {
                "error": "CONFIG_PARSE_ERROR",
                "file": str(self.config_path),
                "details": str(e)
            }
            self.logger.critical(json.dumps(error))
            raise KernelBootError(f"Config parse error: {e}")

    def _validate_environment(self) -> bool:
        """
        Validate all required environment variables (GAD-000 compliance).

        Returns:
            True if all required vars present

        Raises:
            KernelBootError: If required vars missing
        """
        required_vars = self.config.get("environment", {}).get("required_vars", [])
        missing = []

        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            error = {
                "error": "ENVIRONMENT_INCOMPLETE",
                "missing_keys": missing,
                "total_required": len(required_vars),
                "action": "Check .env or GitHub Secrets configuration",
                "details": f"Missing {len(missing)}/{len(required_vars)} required variables"
            }
            self.logger.critical(json.dumps(error))
            raise KernelBootError(f"Missing environment vars: {missing}")

        return True

    def load(self) -> "VibeKernel":
        """
        Load configuration (separable from boot).
        Allows inspection before full initialization.
        """
        self.logger.info("🔌 VIBE KERNEL: Loading configuration...")

        self.config = self._load_config()
        self._loaded = True

        self.logger.info(f"✅ Config loaded: {self.config_path}")
        self.logger.info(f"   System: {self.config['system']['name']} v{self.config['system']['version']}")

        return self

    def boot(self) -> "VibeKernel":
        """
        Complete boot sequence (load + validate environment).

        Sequence:
        1. Load config
        2. Validate environment
        3. Log system status

        Raises:
            KernelBootError: If any step fails
        """
        if not self._loaded:
            self.load()

        self.logger.info("🚀 VIBE KERNEL: Boot sequence initiated")
        self.logger.info("=" * 70)

        # Validate environment
        try:
            self._validate_environment()
            self.logger.info("✅ ENVIRONMENT: All required variables present")
        except KernelBootError as e:
            self.logger.critical(f"❌ BOOT FAILED: {e}")
            sys.exit(1)

        self._booted = True

        self.logger.info("=" * 70)
        self.logger.info("✅ KERNEL BOOT COMPLETE")
        self.logger.info(f"   System: {self.config['system']['name']}")
        self.logger.info(f"   Capabilities: {len(self.config.get('capabilities', {}))} modules")
        self.logger.info("=" * 70)

        return self

    def register_capability(self, name: str, instance: Any) -> "VibeKernel":
        """
        Register a capability (module instance).

        Args:
            name: Capability name (e.g., "research", "creative")
            instance: Instance of capability class

        Returns:
            self (for chaining)
        """
        if not self._booted:
            raise RuntimeError("Kernel must boot before registering capabilities")

        self.capabilities[name] = instance
        self.logger.info(f"🧩 CAPABILITY LOADED: {name}")

        return self

    def get_capability(self, name: str) -> Optional[Any]:
        """
        Retrieve registered capability instance.

        Args:
            name: Capability name

        Returns:
            Capability instance or None
        """
        if name not in self.capabilities:
            self.logger.warning(f"⚠️  Capability not registered: {name}")
            return None

        return self.capabilities[name]

    def execute(self, capability: str, action: str, **kwargs) -> Optional[Any]:
        """
        Execute a capability action (orchestration).

        Args:
            capability: Capability name (e.g., "research")
            action: Action method name (e.g., "search")
            **kwargs: Arguments to pass to action method

        Returns:
            Result from capability action

        Raises:
            RuntimeError: If capability/action not found
        """
        cap = self.get_capability(capability)

        if not cap:
            self.logger.error(f"❌ Capability not available: {capability}")
            raise RuntimeError(f"Capability '{capability}' not registered")

        if not hasattr(cap, action):
            self.logger.error(f"❌ Action not found: {capability}.{action}")
            raise RuntimeError(f"Action '{action}' not found on {capability}")

        try:
            self.logger.debug(f"🔄 Executing: {capability}.{action}")
            result = getattr(cap, action)(**kwargs)
            return result

        except Exception as e:
            self.logger.error(f"❌ Execution failed: {capability}.{action}")
            self.logger.error(f"   Error: {str(e)}")
            raise

    def get_config(self, path: str = None) -> Any:
        """
        Get configuration value by dot-path.

        Examples:
            kernel.get_config("capabilities.research.max_results")
            kernel.get_config("system.name")

        Args:
            path: Dot-separated path (e.g., "capabilities.research.enabled")

        Returns:
            Config value or entire config dict if path is None
        """
        if path is None:
            return self.config

        parts = path.split(".")
        value = self.config

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def status(self) -> Dict[str, Any]:
        """
        Get kernel status (for debugging/monitoring).

        Returns:
            Dict with system status info
        """
        return {
            "system": self.config.get("system", {}).get("name"),
            "version": self.config.get("system", {}).get("version"),
            "booted": self._booted,
            "capabilities_loaded": len(self.capabilities),
            "capabilities": list(self.capabilities.keys()),
            "config_path": str(self.config_path),
        }
