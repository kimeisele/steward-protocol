"""
Hot Loader - Dynamic Plugin Loading at Runtime.

OPUS-032: THE OUROBOROS PROTOCOL

This module provides hot-loading capability without modifying the protected
PluginLoader in vibe_core/. This respects VISNU kernel protection while
still enabling runtime capability synthesis.

Usage:
    from vibe_core.plugins.runtime_extensions.hot_loader import hot_load, hot_unload

    # Load a generated plugin
    plugin = hot_load(Path("vibe_core/plugins/runtime_extensions/my_plugin"))

    # Unload when done
    hot_unload("my_plugin")
"""

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.plugin_protocol import KernelPlugin
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("OUROBOROS.HotLoader")

# Track loaded plugins for cleanup
_hot_loaded_plugins: Dict[str, "KernelPlugin"] = {}


def hot_load(
    plugin_path: Path,
    kernel: Optional["KernelProtocol"] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Optional["KernelPlugin"]:
    """
    Hot-load a plugin at runtime without system restart.

    OPUS-032: THE OUROBOROS PROTOCOL - Runtime capability synthesis.

    This allows MANAS-generated capabilities to be loaded after approval:
    1. MANAS generates code in runtime_extensions/
    2. Human approves via OPUS.md
    3. This function loads the new plugin
    4. Plugin's on_boot() registers its syscalls

    Args:
        plugin_path: Path to the plugin directory or .py file
        kernel: Optional kernel instance for immediate registration
        config: Optional configuration dict

    Returns:
        The loaded plugin instance, or None if failed

    Safety:
        - Only loads from runtime_extensions/ by default
        - Validates manifest before loading
        - Plugin can be unloaded via hot_unload()
    """
    from vibe_core.plugin_protocol import KernelPlugin

    logger.info(f"🐍 OUROBOROS: Hot-loading plugin from {plugin_path}")

    try:
        # Validate path is in allowed locations
        allowed_paths = [
            Path("vibe_core/plugins/runtime_extensions"),
        ]
        is_allowed = any(plugin_path.resolve().is_relative_to(p.resolve()) for p in allowed_paths if p.exists())
        if not is_allowed:
            logger.error(f"🚫 OUROBOROS: Path not in allowed locations: {plugin_path}")
            return None

        instance = None

        # Load based on type (directory or file)
        if plugin_path.is_dir():
            manifest_path = plugin_path / "manifest.json"
            if not manifest_path.exists():
                logger.error(f"🚫 OUROBOROS: No manifest.json in {plugin_path}")
                return None

            # Load the manifest
            import json

            manifest = json.loads(manifest_path.read_text())
            plugin_id = manifest.get("id", plugin_path.name)
            entry_file = manifest.get("entry", "plugin_main.py")

            # Import the module
            entry_path = plugin_path / entry_file
            if not entry_path.exists():
                logger.error(f"🚫 OUROBOROS: Entry file not found: {entry_path}")
                return None

            # Convert path to module name
            module_path = str(plugin_path).replace("/", ".")
            module_name = f"{module_path}.{entry_file.replace('.py', '')}"

            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, entry_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find KernelPlugin subclass
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, KernelPlugin) and attr is not KernelPlugin:
                        try:
                            instance = attr()
                            break
                        except Exception as e:
                            logger.warning(f"Could not instantiate {attr_name}: {e}")

        elif plugin_path.is_file() and plugin_path.suffix == ".py":
            # Single file plugin
            module_name = f"runtime_ext_{plugin_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find KernelPlugin subclass
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, KernelPlugin) and attr is not KernelPlugin:
                        try:
                            instance = attr()
                            break
                        except Exception as e:
                            logger.warning(f"Could not instantiate {attr_name}: {e}")
        else:
            logger.error(f"🚫 OUROBOROS: Invalid plugin path: {plugin_path}")
            return None

        if not instance:
            logger.error(f"🚫 OUROBOROS: Failed to create instance from {plugin_path}")
            return None

        # Track the loaded plugin
        _hot_loaded_plugins[instance.plugin_id] = instance

        # Register with kernel if provided
        if kernel and hasattr(kernel, "register_plugin"):
            kernel.register_plugin(instance)
            logger.info(f"✅ OUROBOROS: Registered {instance.plugin_id} with kernel")

        # Call on_boot to let plugin register its syscalls
        if hasattr(instance, "on_boot") and kernel:
            instance.on_boot(kernel)
            logger.info(f"✅ OUROBOROS: {instance.plugin_id} booted and syscalls registered")

        logger.info(f"🐍 OUROBOROS: Successfully hot-loaded {instance.plugin_id}")
        return instance

    except Exception as e:
        logger.error(f"❌ OUROBOROS: Hot-load failed: {e}")
        import traceback

        logger.debug(traceback.format_exc())
        return None


def hot_unload(
    plugin_id: str,
    kernel: Optional["KernelProtocol"] = None,
) -> bool:
    """
    Unload a hot-loaded plugin at runtime.

    Args:
        plugin_id: The plugin ID to unload
        kernel: Optional kernel instance for deregistration

    Returns:
        True if successfully unloaded
    """
    from vibe_core.runtime.syscalls import get_syscall_registry

    logger.info(f"🐍 OUROBOROS: Unloading plugin {plugin_id}")

    try:
        registry = get_syscall_registry()

        # Find and remove syscalls registered by this plugin
        caps = registry.get_capabilities()
        for syscall in caps.get("registered_syscalls", []):
            if syscall.get("plugin_id") == plugin_id:
                registry.unregister(syscall["name"])
                logger.info(f"  ↩️ Unregistered syscall: {syscall['name']}")

        # Remove from tracking
        if plugin_id in _hot_loaded_plugins:
            del _hot_loaded_plugins[plugin_id]

        # Deregister from kernel if provided
        if kernel and hasattr(kernel, "unregister_plugin"):
            kernel.unregister_plugin(plugin_id)

        logger.info(f"✅ OUROBOROS: Unloaded {plugin_id}")
        return True

    except Exception as e:
        logger.error(f"❌ OUROBOROS: Unload failed: {e}")
        return False


def get_hot_loaded_plugins() -> Dict[str, "KernelPlugin"]:
    """Get all currently hot-loaded plugins."""
    return dict(_hot_loaded_plugins)
