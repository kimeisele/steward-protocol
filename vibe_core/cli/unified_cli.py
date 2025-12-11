"""
UnifiedCLI - Single entry point for all CLI operations.
Combines Fractal CLI (Plugin-based) with Legacy StewardCLI (System commands).

WIRED TO PRAKRITI: Unified State Engine (OPUS-009)
"""

import argparse
import json
import logging
import tempfile
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, TextColumn, TransferSpeedColumn

from vibe_core.cli.executor import CLIExecutor
from vibe_core.cli.loader import CLILoader
from vibe_core.cli.protocol import CLICommand

# PRAKRITI WIRING - The Unified State Engine
from vibe_core.state.prakriti import Prakriti

# Import Legacy CLI for fallback/system commands
# Suppress deprecation warning during import if we add it later
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from vibe_core.cli.legacy import StewardCLI

logger = logging.getLogger("UNIFIED_CLI")


class UnifiedCLI:
    """
    GAD-000 compliant CLI that unifies:
    1. System commands (boot, stop, status) -> Legacy StewardCLI
    2. Plugin commands (verify, etc) -> Fractal CLIExecutor
    """

    def __init__(self):
        self._loader = CLILoader()
        self._executor = CLIExecutor()
        self._legacy = StewardCLI()

        # PRAKRITI WIRING - The Unified State Engine (OPUS-009)
        self._prakriti = Prakriti.from_workspace(".")

        # Define legacy commands that are handled by StewardCLI
        self._legacy_map = {
            "status": self._legacy.cmd_status,
            "verify": self._legacy.cmd_verify,  # Keep verify in legacy for now until Parampara plugin
            "lineage": self._legacy.cmd_lineage,
            "ps": self._legacy.cmd_ps,
            "boot": self._legacy.cmd_boot,
            "stop": self._legacy.cmd_stop,
            "init": self._legacy.cmd_init,
            "discover": self._legacy.cmd_discover,
            "introspect": self._legacy.cmd_introspect,
            "delegate": None,  # TODO: Migrate to plugin
            # Extension commands (runtime package management)
            "install-llm": self._legacy.cmd_install_llm,
            "install-semantic": self._legacy.cmd_install_semantic,
            "extensions": self._legacy.cmd_extensions,
        }

        # PRAKRITI commands - wired to unified state
        self._prakriti_cmds = {
            "state": self.cmd_state,
            "diff": self.cmd_diff,
            "plugins": self.cmd_plugins,
            "update": self.cmd_update,
            "install": self.cmd_install,  # Alias for update (semantic clarity)
        }

    def run(self, args: List[str]) -> int:
        """
        Execute CLI command.
        Returns exit code (0 = success, 1 = error).
        """
        parser = argparse.ArgumentParser(description="Steward Protocol Unified CLI")

        # We need to peek at the first argument to decide routing
        if not args:
            parser.print_help()
            return 1

        command_name = args[0]
        remaining_args = args[1:]

        # 1. Check Legacy/System Commands
        if command_name in self._legacy_map:
            handler = self._legacy_map[command_name]
            if handler:
                # Legacy handlers expect specific args or use their own parsing?
                # StewardCLI methods take specific typed args.
                # We need to bridge argparse to method args.
                return self._dispatch_legacy(command_name, handler, remaining_args)

        # 2. Check Plugin Commands
        commands = self._loader.discover_commands()
        if command_name in commands:
            cmd_def = commands[command_name]
            return self._dispatch_plugin(cmd_def, remaining_args)

        # 3. PRAKRITI Commands - Wired to Unified State
        if command_name in self._prakriti_cmds:
            handler = self._prakriti_cmds[command_name]
            return handler(remaining_args)

        # 4. GAD-000 Introspection Commands
        if command_name == "capabilities":
            caps = self.get_capabilities()
            print(json.dumps(caps, indent=2))
            return 0

        # 4. Help / Unknown
        if command_name in ("-h", "--help", "help"):
            self._print_help(commands)
            return 0

        print(f"❌ Unknown command: {command_name}")
        print("Try 'steward help' for available commands.")
        return 1

    def get_capabilities(self) -> Dict[str, Any]:
        """
        GAD-000 Test 1: Machine-readable capability discovery.
        Uses SystemInspector (Inspector Pattern) to introspect kernel.
        """
        # We need a kernel instance for introspection (even if phantom)

        # Use CLILoader to discover plugins
        plugin_commands = self._loader.discover_commands()

        # Build capabilities dict
        inspector_caps = {
            "version": "2.0.0 (Unified)",
            "system_commands": list(self._legacy_map.keys()),
            "plugin_commands": [
                {"name": cmd.name, "namespace": cmd.namespace, "help": cmd.help, "mode": cmd.execution_mode.name}
                for cmd in plugin_commands.values()
            ],
            "json_output_supported": True,
            "inspector_pattern": True,
        }

        return inspector_caps

    def _dispatch_legacy(self, name: str, handler: Any, args: List[str]) -> int:
        """Dispatch to legacy StewardCLI methods."""
        # Simple argument parsing for legacy methods
        # Most legacy methods map 1:1 to args, but we need to match signatures.
        # For now, we'll implement a basic bridge.

        try:
            if name == "status":
                return handler()
            elif name == "ps":
                return handler()
            elif name == "boot":
                return handler()
            elif name == "stop":
                return handler()
            elif name == "discover":
                return handler()
            elif name == "introspect":
                return handler()
            elif name == "verify":
                if not args:
                    print("Usage: steward verify <agent_id>")
                    return 1
                return handler(args[0])
            elif name == "init":
                if not args:
                    print("Usage: steward init <agent_id>")
                    return 1
                return handler(args[0])
            elif name == "lineage":
                tail = None
                if "--tail" in args:
                    try:
                        idx = args.index("--tail")
                        tail = int(args[idx + 1])
                    except (ValueError, IndexError):
                        pass
                return handler(tail=tail)
            else:
                print(f"⚠️ Command '{name}' is known but dispatch is not implemented in UnifiedCLI.")
                return 1
        except Exception as e:
            print(f"❌ Error executing legacy command '{name}': {e}")
            return 1

    def _dispatch_plugin(self, cmd: CLICommand, args: List[str]) -> int:
        """Dispatch to Fractal CLIExecutor."""
        # Parse args based on cmd definition
        parsed_args = self._parse_plugin_args(cmd, args)
        if parsed_args is None:
            return 1

        response = self._executor.execute(cmd, parsed_args)

        if response.success:
            if response.data is not None:
                # formatting should be handled by a renderer, but for now print
                import json

                print(json.dumps(response.data, indent=2, default=str))
            return 0
        else:
            print(f"❌ Error: {response.error}")
            return 1

    def _parse_plugin_args(self, cmd: CLICommand, args: List[str]) -> Optional[Dict[str, Any]]:
        """Use argparse to parse arguments defined in manifest."""
        parser = argparse.ArgumentParser(prog=f"steward {cmd.name}", description=cmd.help)

        for arg in cmd.args:
            kwargs = {
                "help": arg.help,
                "type": arg.type,
                "default": arg.default,
            }
            if arg.required:
                kwargs["required"] = True
            if arg.nargs:
                kwargs["nargs"] = arg.nargs
            if arg.choices:
                kwargs["choices"] = arg.choices

            # If default is None and not required, it's optional
            # In argparse, positionals are required unless nargs='?' or default set

            name = arg.name
            if not arg.required and not name.startswith("-"):
                # Make it optional flag if not required? Or optional positional?
                # For CLI simplicity, let's assume manifest args are flags if optional
                pass

            # Simple mapping for now
            if not arg.required:
                name = f"--{arg.name}"

            parser.add_argument(name, **kwargs)

        try:
            # Only parse known args to check for help, but we isolated args already
            namespace = parser.parse_args(args)
            return vars(namespace)
        except SystemExit:
            return None

    # =========================================================================
    # PRAKRITI COMMANDS - Wired to Unified State Engine (OPUS-009)
    # =========================================================================

    def cmd_state(self, args: List[str]) -> int:
        """
        Show unified system state from Prakriti.
        steward state
        """
        try:
            status = self._prakriti.get_system_status()
            print(json.dumps(status, indent=2, default=str))
            return 0
        except Exception as e:
            print(f"❌ Error getting state: {e}")
            return 1

    def cmd_diff(self, args: List[str]) -> int:
        """
        Show git diff (Proof of Work).
        steward diff [--main]
        """
        try:
            if "--main" in args:
                diff = self._prakriti.diff_main()
            else:
                diff = self._prakriti.diff("HEAD~1")

            print("📊 Git Diff Stats")
            print(f"   Files changed: {diff.files_changed}")
            print(f"   Insertions:    +{diff.insertions}")
            print(f"   Deletions:     -{diff.deletions}")
            if diff.files:
                print("\n   Changed files:")
                for f in diff.files[:10]:  # Limit to 10
                    print(f"     - {f}")
                if len(diff.files) > 10:
                    print(f"     ... and {len(diff.files) - 10} more")
            return 0
        except Exception as e:
            print(f"❌ Error getting diff: {e}")
            return 1

    def cmd_plugins(self, args: List[str]) -> int:
        """
        List loaded plugins and their dependencies.
        steward plugins
        """
        from pathlib import Path

        plugins_dir = Path("vibe_core/plugins")
        if not plugins_dir.exists():
            print("❌ Plugins directory not found")
            return 1

        print("📦 LOADED PLUGINS")
        print("================")

        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("_"):
                continue

            manifest_path = plugin_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text())
                    plugin_id = manifest.get("id", plugin_dir.name)
                    version = manifest.get("version", "?")
                    deps = manifest.get("depends_on", [])
                    cli_cmds = []
                    if "cli" in manifest:
                        cli_cmds = [c.get("name") for c in manifest["cli"].get("commands", [])]

                    print(f"\n  {plugin_id} v{version}")
                    if deps:
                        print(f"    depends_on: {', '.join(deps)}")
                    if cli_cmds:
                        print(f"    cli: {', '.join(cli_cmds)}")
                except Exception as e:
                    print(f"\n  {plugin_dir.name} (manifest error: {e})")
            else:
                print(f"\n  {plugin_dir.name} (no manifest)")

        return 0

    # =========================================================================
    # HELP
    # =========================================================================

    def cmd_update(self, args: List[str]) -> int:
        """
        Update/Install a plugin/agent container to the Runtime Library.

        Usage:
            steward update <name>           # From dist/<name>.vibe
            steward install <path.vibe>     # Direct path to .vibe file

        RUNTIME SEPARATION (OPUS-016):
        - Writes to library/ (Runtime Space), NOT cartridges/system/ (Source)
        - The Loader reads from library/, so updates take effect on restart
        - NOW SUPPORTS (Phase 17): Remote URLs and Registry Aliases (@steward/name)
        """
        import shutil
        from pathlib import Path

        try:
            from vibe_core.phoenix.config import PhoenixConfig
        except ImportError:
            PhoenixConfig = None

        if not args:
            print("Usage: steward update <name>")
            print("       steward install <path/to/file.vibe>")
            print("       steward install https://example.com/file.vibe")
            print("       steward install @steward/herald")
            return 1

        source_arg = args[0]
        temp_file = None

        # =====================================================================
        # PHASE 17: TELEPATHY (Remote Installation & Discovery)
        # =====================================================================

        # 1. Resolve Source (Mask Registry Aliases as URLs)
        if source_arg.startswith("@"):
            source_arg = self._resolve_registry_alias(source_arg)
            print(f"📡 Resolved registry alias to: {source_arg}")

        # 2. Check for Remote URL
        is_remote = source_arg.startswith("http://") or source_arg.startswith("https://")

        if is_remote:
            print(f"⬇️  Downloading from {source_arg}...")
            try:
                temp_fd, temp_path = tempfile.mkstemp(suffix=".vibe")
                temp_file = Path(temp_path)
                self._download_file(source_arg, temp_file)
                source_path = temp_file
                # Infer name from URL if possible, otherwise prompt/default needed
                # Ideally config inside .vibe has the name, but for now we rely on filename convention
                name = Path(source_arg).stem
                print("✅ Download complete.")
            except Exception as e:
                print(f"❌ Download failed: {e}")
                if temp_file and temp_file.exists():
                    temp_file.unlink()
                return 1
        else:
            # Local File Logic (Legacy)
            if source_arg.endswith(".vibe") and Path(source_arg).exists():
                source_path = Path(source_arg)
                name = source_path.stem
            else:
                # Name lookup in dist/
                name = source_arg
                source_path = Path("dist") / f"{name}.vibe"
                if not source_path.exists():
                    source_path = Path("dist/holons") / f"{name}.vibe"

                if not source_path.exists():
                    print(f"❌ Artifact not found: dist/{name}.vibe")
                    print(f"   Provide a direct path, URL, or run 'steward pack {name}' first.")
                    return 1

        print(f"📦 Installing {name} from {source_path}...")

        # =====================================================================
        # RUNTIME SEPARATION: Target library/ (Runtime Space)
        # =====================================================================
        target_dir = Path("library")  # Default

        # Try to get library_path from PhoenixConfig
        if PhoenixConfig:
            try:
                config = PhoenixConfig.load()
                if hasattr(config, "paths") and hasattr(config.paths, "system"):
                    lib_path = getattr(config.paths.system, "library_path", None)
                    if lib_path:
                        target_dir = Path(lib_path)
            except Exception:
                pass  # Use default

        # Ensure target exists
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created runtime library: {target_dir}")

        # Install (Copy)
        dest_path = target_dir / f"{name}.vibe"

        try:
            shutil.copy2(source_path, dest_path)
            print(f"✅ Installed to {dest_path}")
            print(f"   Size: {dest_path.stat().st_size:,} bytes")
            print("   🔄 Restart kernel to apply changes.")

            # Cleanup temp file if used
            if temp_file and temp_file.exists():
                temp_file.unlink()

            return 0
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            if temp_file and temp_file.exists():
                temp_file.unlink()
            return 1

    def _resolve_registry_alias(self, alias: str) -> str:
        """
        Phase 17 Step 2: Registry Map
        Maps @steward/<name> to GitHub Release URL.
        """
        # Simple static mapping for now, can be dynamic later
        REGISTRY_BASE = "https://github.com/steward-protocol/registry/releases/download/v1.0"

        if alias.startswith("@steward/"):
            name = alias.split("/")[1]
            return f"{REGISTRY_BASE}/{name}.vibe"

        # Fallback
        return alias

    def _download_file(self, url: str, dest: Path):
        """
        Phase 17 Step 1: Network Core (Requests + Rich Progress)
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = progress.add_task("Downloading...", total=total_size)

            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

    def cmd_install(self, args: List[str]) -> int:
        """Alias for cmd_update - semantic clarity for new installations."""
        return self.cmd_update(args)

    # =========================================================================
    # HELP
    # =========================================================================

    def _print_help(self, plugin_commands: Dict[str, CLICommand]):
        print("🎛️  STEWARD UNIFIED CLI")
        print("=======================")

        print("\nSYSTEM COMMANDS:")
        for name in sorted(self._legacy_map.keys()):
            print(f"  {name:<15} (System)")

        print("\nPRAKRITI COMMANDS (Unified State):")
        prakriti_help = {
            "state": "Show unified system state",
            "diff": "Git diff (Proof of Work) [--main]",
            "plugins": "List plugins and dependencies",
            "update": "Update container to library/ <name>",
            "install": "Install .vibe file to library/ <path>",
        }
        for name, help_text in prakriti_help.items():
            print(f"  {name:<15} {help_text}")

        print("\nPLUGIN COMMANDS:")
        for name, cmd in sorted(plugin_commands.items()):
            print(f"  {name:<15} {cmd.help}")
