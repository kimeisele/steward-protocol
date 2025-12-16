import logging
from pathlib import Path

from vibe_core.plugin_loader import PluginLoader

logging.basicConfig(level=logging.ERROR)

print("Scanning plugins...")
try:
    # Use default scan paths + runtime_extensions
    scan_paths = [Path("vibe_core/plugins"), Path("vibe_core/plugins/runtime_extensions")]
    plugins_map, _ = PluginLoader.discover_and_load(scan_paths=scan_paths)
    plugins = list(plugins_map.values())
    sorted_plugins = sorted(plugins, key=lambda p: p.priority)

    print("\n--- PLUGIN BOOT ORDER ---")
    for p in sorted_plugins:
        print(f"Priority {p.priority}: {p.plugin_id} ({p.__class__.__name__})")
except Exception as e:
    print(f"Error scanning: {e}")
