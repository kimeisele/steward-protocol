import importlib
import logging
import pkgutil
from pathlib import Path
from typing import List

from .plugin_protocol import KernelPlugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Auto-discovery loader for Kernel Plugins.
    """

    @staticmethod
    def discover(plugin_dir: str = "vibe_core/plugins") -> List[KernelPlugin]:
        """
        Auto-discover and load all plugins from the specified directory.

        Args:
            plugin_dir: Relative path to the plugins directory (default: "vibe_core/plugins")

        Returns:
            List of instantiated KernelPlugin objects, sorted by priority.
        """
        plugins: List[KernelPlugin] = []

        # Resolve absolute path
        # Assuming plugin_dir is relative to the project root or current working directory
        # We'll try to find it relative to this file's parent (vibe_core) first
        base_path = Path(__file__).parent.parent
        plugin_path = base_path / plugin_dir

        if not plugin_path.exists():
            # Fallback: try relative to CWD
            plugin_path = Path(plugin_dir)
            if not plugin_path.exists():
                logger.warning(f"⚠️  Plugin directory not found: {plugin_path}")
                return plugins

        logger.info(f"🔌 Discovering plugins in: {plugin_path}")

        # Ensure the directory is a python package (has __init__.py)
        if not (plugin_path / "__init__.py").exists():
            logger.warning(f"⚠️  Plugin directory missing __init__.py: {plugin_path}")
            return plugins

        # Convert file path to module path (e.g., vibe_core/plugins -> vibe_core.plugins)
        # This assumes the directory structure matches the package structure
        # We'll construct the package name based on the directory name relative to base
        try:
            relative_path = plugin_path.relative_to(base_path)
            package_name = str(relative_path).replace("/", ".")
        except ValueError:
            # Fallback if not relative to base
            package_name = plugin_dir.replace("/", ".")

        for module_info in pkgutil.iter_modules([str(plugin_path)]):
            try:
                full_module_name = f"{package_name}.{module_info.name}"
                module = importlib.import_module(full_module_name)

                # Find KernelPlugin subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, KernelPlugin) and attr is not KernelPlugin:
                        # Instantiate and add
                        try:
                            plugin_instance = attr()
                            plugins.append(plugin_instance)
                            logger.debug(
                                f"   ✅ Loaded plugin: {plugin_instance.plugin_id} (priority: {plugin_instance.priority})"
                            )
                        except Exception as e:
                            logger.error(f"   ❌ Failed to instantiate plugin {attr_name}: {e}")

            except Exception as e:
                logger.error(f"❌ Failed to load plugin module {module_info.name}: {e}")

        # Sort by priority (lower first)
        sorted_plugins = sorted(plugins, key=lambda p: p.priority)

        logger.info(f"🔌 Total plugins loaded: {len(sorted_plugins)}")
        return sorted_plugins
