#!/usr/bin/env python3
"""
CartridgeRegistry - ARCH-050

Centralized registry for Vibe OS cartridges.

This registry:
1. Maintains a mapping of cartridge names to their classes
2. Enables dynamic cartridge discovery and loading
3. Supports cartridge dependency resolution
4. Provides introspection into available cartridges

Usage:
    registry = CartridgeRegistry()
    archivist = registry.get_cartridge("archivist")
    all_cartridges = registry.list_cartridges()
"""

import importlib.util
import logging
from pathlib import Path

from .base import CartridgeBase, CartridgeSpec

logger = logging.getLogger(__name__)


class CartridgeRegistry:
    """
    Centralized registry for Vibe OS cartridges.

    Enables:
    - Dynamic cartridge discovery and registration
    - Cartridge instantiation
    - Dependency resolution (future)
    - Cartridge introspection and listing
    """

    def __init__(self, vibe_root: Path | None = None):
        """
        Initialize the cartridge registry.

        Args:
            vibe_root: Path to vibe-agency root
        """
        if vibe_root is None:
            vibe_root = self._detect_vibe_root()

        self.vibe_root = Path(vibe_root)
        self._registry: dict[str, type[CartridgeBase]] = {}
        self._instances: dict[str, CartridgeBase] = {}

        # Auto-discover cartridges in vibe_core/cartridges/
        self._auto_discover()

    def _detect_vibe_root(self) -> Path:
        """Auto-detect the vibe-agency root directory."""
        cwd = Path.cwd()

        if (cwd / ".vibe").exists():
            return cwd

        for parent in cwd.parents:
            if (parent / ".vibe").exists():
                return parent

        raise RuntimeError(
            "Could not detect vibe-agency root. Please set VIBE_ROOT environment variable."
        )

    def _auto_discover(self) -> None:
        """Auto-discover cartridges in vibe_core/cartridges/ directory."""
        cartridges_dir = self.vibe_root / "vibe_core" / "cartridges"

        if not cartridges_dir.exists():
            logger.warning(f"⚠️ Cartridges directory not found: {cartridges_dir}")
            return

        # Look for cartridge directories (skip __pycache__, base.py, registry.py, etc.)
        for item in cartridges_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # Look for cartridge_main.py or __init__.py with CartridgeBase subclass
                self._load_cartridge_from_dir(item)

    def _load_cartridge_from_dir(self, cartridge_dir: Path) -> None:
        """
        Load a cartridge from a directory.

        Looks for:
        1. cartridge_main.py (primary cartridge definition)
        2. __init__.py (alternative location)
        """
        cartridge_name = cartridge_dir.name

        # Try cartridge_main.py first
        cartridge_main = cartridge_dir / "cartridge_main.py"
        if cartridge_main.exists():
            self._load_cartridge_from_file(cartridge_main, cartridge_name)
            return

        # Try __init__.py
        init_file = cartridge_dir / "__init__.py"
        if init_file.exists():
            self._load_cartridge_from_file(init_file, cartridge_name)
            return

        logger.debug(f"⚠️ No cartridge definition found in {cartridge_dir}")

    def _load_cartridge_from_file(self, file_path: Path, cartridge_name: str) -> None:
        """
        Dynamically load a cartridge class from a Python file.

        Args:
            file_path: Path to the Python file
            cartridge_name: Name of the cartridge
        """
        try:
            spec = importlib.util.spec_from_file_location(f"cartridge_{cartridge_name}", file_path)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find CartridgeBase subclass in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, CartridgeBase)
                        and attr is not CartridgeBase
                    ):
                        self._registry[cartridge_name] = attr
                        logger.info(f"✅ Registered cartridge: {cartridge_name} ({attr.__name__})")
                        return

                logger.warning(
                    f"⚠️ No CartridgeBase subclass found in {file_path} for {cartridge_name}"
                )

        except Exception as e:
            logger.warning(f"⚠️ Failed to load cartridge {cartridge_name}: {e}")

    def register_cartridge(
        self, name: str, cartridge_class: type[CartridgeBase], override: bool = False
    ) -> None:
        """
        Manually register a cartridge.

        Args:
            name: Cartridge name (e.g., "archivist")
            cartridge_class: Cartridge class (must be CartridgeBase subclass)
            override: Whether to override existing cartridge

        Raises:
            TypeError: If cartridge_class is not a CartridgeBase subclass
            ValueError: If cartridge already registered and override=False
        """
        if not issubclass(cartridge_class, CartridgeBase):
            raise TypeError(
                f"Cartridge class must inherit from CartridgeBase, got: {cartridge_class.__name__}"
            )

        if name in self._registry and not override:
            raise ValueError(
                f"Cartridge '{name}' already registered. Use override=True to replace."
            )

        old_class = self._registry.get(name)
        self._registry[name] = cartridge_class

        if old_class:
            logger.info(
                f"🔄 Cartridge override: {name} ({old_class.__name__} → {cartridge_class.__name__})"
            )
        else:
            logger.info(f"➕ Cartridge registered: {name} → {cartridge_class.__name__}")

    def get_cartridge(self, name: str, cached: bool = True) -> CartridgeBase:
        """
        Get a cartridge instance.

        Args:
            name: Cartridge name (e.g., "archivist")
            cached: Use cached instance if available (default: True)

        Returns:
            Instantiated CartridgeBase subclass

        Raises:
            ValueError: If cartridge not found
        """
        if name not in self._registry:
            raise ValueError(
                f"Cartridge '{name}' not found. Available: {list(self._registry.keys())}"
            )

        # Return cached instance if requested
        if cached and name in self._instances:
            return self._instances[name]

        # Instantiate new cartridge
        cartridge_class = self._registry[name]
        cartridge = cartridge_class(vibe_root=self.vibe_root)

        # Cache instance
        if cached:
            self._instances[name] = cartridge

        return cartridge

    def list_cartridges(self) -> dict[str, CartridgeSpec]:
        """
        List all registered cartridges with their metadata.

        Returns:
            Dictionary mapping cartridge names to CartridgeSpec
        """
        result = {}
        for name, cartridge_class in self._registry.items():
            # Instantiate temporarily to get spec
            try:
                instance = cartridge_class(vibe_root=self.vibe_root)
                result[name] = instance.get_spec()
            except Exception as e:
                logger.warning(f"⚠️ Failed to get spec for cartridge {name}: {e}")

        return result

    def get_cartridge_names(self) -> list[str]:
        """Get list of all registered cartridge names."""
        return list(self._registry.keys())

    def __repr__(self) -> str:
        """String representation for debugging."""
        cartridges = ", ".join(f"{name}({cls.__name__})" for name, cls in self._registry.items())
        return f"CartridgeRegistry({len(self._registry)} cartridges: {cartridges})"


# ============================================================================
# Singleton Instance (Convenience)
# ============================================================================

_default_registry = None


def get_default_cartridge_registry(vibe_root: Path | None = None) -> CartridgeRegistry:
    """
    Get the default global cartridge registry instance (singleton).

    Args:
        vibe_root: Path to vibe-agency root (only used for first initialization)

    Returns:
        Global CartridgeRegistry instance

    Example:
        registry = get_default_cartridge_registry()
        archivist = registry.get_cartridge("archivist")
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = CartridgeRegistry(vibe_root=vibe_root)
    return _default_registry


__all__ = ["CartridgeRegistry", "get_default_cartridge_registry"]
