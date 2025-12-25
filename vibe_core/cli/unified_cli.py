"""
UnifiedCLI - Single entry point for all CLI operations.
Combines Fractal CLI (Plugin-based) with Legacy StewardCLI (System commands).

WIRED TO PRAKRITI: Unified State Engine (OPUS-009)
"""

import argparse
import asyncio
import json
import logging
import tempfile
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, TextColumn, TransferSpeedColumn

from vibe_core.boot_mode import BootMode  # OPUS-031 Layer 4: Autonomous Conductor
from vibe_core.cli.executor import CLIExecutor
from vibe_core.cli.loader import CLILoader
from vibe_core.cli.protocol import CLICommand
from vibe_core.di import ServiceRegistry
from vibe_core.protocols import PrakritiProtocol

# Import Legacy CLI for fallback/system commands
# Suppress deprecation warning during import if we add it later
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from vibe_core.cli.legacy import StewardCLI

# OPUS-307 Phase E+: CLIProtocol (Anti-God-Object)
# Import CLIRegistry and trigger registration of all CLI handlers
# OPUS-307 Phase D/E+: Protocol-based CLI handlers
# These imports trigger @register_cli decorator - DO NOT REMOVE
import vibe_core.cli.audit_cli  # noqa: F401 - registers "audit" (OPUS-307 Phase 4)
import vibe_core.cli.cartridge_bridge  # noqa: F401 - registers "cartridges" (OPUS-307)
import vibe_core.cli.circuit_cli  # noqa: F401 - registers "circuit"
import vibe_core.cli.config_cli  # noqa: F401 - registers "config" (OPUS-307)
import vibe_core.cli.create_cli  # noqa: F401 - registers "create" (OPUS-307 Phase 5)
import vibe_core.cli.genesis_cli  # noqa: F401 - registers "genesis" (OPUS-307)
import vibe_core.cli.knowledge_cli  # noqa: F401 - registers "knowledge"
import vibe_core.cli.plugins_cli  # noqa: F401 - registers "plugins" (OPUS-307)
import vibe_core.cli.prakriti_cli  # noqa: F401 - registers "prakriti" (OPUS-307)
import vibe_core.cli.prompts_cli  # noqa: F401 - registers "prompts" (OPUS-307)
import vibe_core.cli.remedies_cli  # noqa: F401 - registers "remedies"
import vibe_core.cli.run_cli  # noqa: F401 - registers "run"
import vibe_core.cli.sections_cli  # noqa: F401 - registers "sections" (OPUS-307)
import vibe_core.cli.standards_cli  # noqa: F401 - registers "standards"
import vibe_core.cli.tool_cli  # noqa: F401 - registers "tool"

# OPUS-307: Register dynamic cartridge CLI bridges (lazy loading)
from vibe_core.cli.cartridge_bridge import register_cartridge_bridges
from vibe_core.protocols.cli import CLIRegistry

register_cartridge_bridges()

logger = logging.getLogger("UNIFIED_CLI")


class UnifiedCLI:
    """
    GAD-000 compliant CLI that unifies:
    1. System commands (boot, stop, status) -> Legacy StewardCLI
    2. Plugin commands (verify, etc) -> Fractal CLIExecutor
    """

    @property
    def prakriti(self) -> PrakritiProtocol:
        """Lazy access to unified state engine via DI."""
        prakriti = ServiceRegistry.get(PrakritiProtocol)
        if not prakriti:
            # Fallback for CLI standalone mode
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti.from_workspace(".")
            ServiceRegistry.register(PrakritiProtocol, prakriti)
        return prakriti

    def __init__(self):
        self._loader = CLILoader()
        self._executor = CLIExecutor()
        self._legacy = StewardCLI()

        # OPUS-307 Phase E+: Protocol-based CLI handlers are discovered via CLIRegistry
        # No more hardcoded instances - handlers register themselves via @register_cli
        # Registered CLIs: tool, circuit, run, knowledge, standards, remedies

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
            "chat": self.cmd_chat,  # OPUS-042: SAMVADA - Human-MANAS dialogue
            "observe": self.cmd_observe,  # OPUS-108: Observer Loop - MANAS cognition monitor
            "poke": self.cmd_poke,  # OPUS-109: Intent Defibrillator - force-execute stuck intents
        }

        # OPUS-075: MANAS HIL Bridge commands
        # MOVED to 'opus_assistant' plugin via manifest.json
        self._manas_cmds = {}

        # OPUS-031 Layer 4: Autonomous Conductor commands
        self._conductor_cmds = {
            "execute": self.cmd_execute,
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

        # 2. OPUS-307 Phase E+: Protocol-based CLI handlers via CLIRegistry
        # GAD-000 COMPLIANT: No hardcoding, dynamic discovery
        # PROMPT.md: "Protocol statt konkrete Klassen"
        # Handles: tool, circuit, run, knowledge, standards, remedies
        cli_handler = CLIRegistry.get(command_name)
        if cli_handler is not None:
            return cli_handler.run(remaining_args)

        # 3. Check Plugin Commands
        commands = self._loader.discover_commands()
        if command_name in commands:
            cmd_def = commands[command_name]
            return self._dispatch_plugin(cmd_def, remaining_args)

        # 3. PRAKRITI Commands - Wired to Unified State
        if command_name in self._prakriti_cmds:
            handler = self._prakriti_cmds[command_name]
            return handler(remaining_args)

        # 4. OPUS-075: MANAS HIL Bridge Commands
        if command_name in self._manas_cmds:
            handler = self._manas_cmds[command_name]
            return handler(remaining_args)

        # 5. OPUS-031 Layer 4: Autonomous Conductor Commands
        if command_name in self._conductor_cmds:
            handler = self._conductor_cmds[command_name]
            return handler(remaining_args)

        # 5. GAD-000 Introspection Commands
        if command_name == "capabilities":
            caps = self.get_capabilities()
            print(json.dumps(caps, indent=2))
            return 0

        # 6. Help / Unknown
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

        response = asyncio.run(self._executor.execute(cmd, parsed_args))

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
            status = self.prakriti.get_system_status()
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
                diff = self.prakriti.diff_main()
            else:
                diff = self.prakriti.diff("HEAD~1")

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
    # OPUS-108: OBSERVER LOOP - Real-Time MANAS Cognition Monitor
    # =========================================================================

    def cmd_observe(self, args: List[str]) -> int:
        """
        OPUS-108: Observer Loop - Live Monitoring of MANAS Cognition.

        Directly taps into cognitive state files to show what MANAS is thinking.
        NO FAKE DASHBOARDS. Raw intents and state.

        This is the OPERATOR CONTROL PANEL - not for humans, for the CLI Operator
        (Claude Code, automated systems) to observe MANAS before approving actions.

        Usage:
            steward observe              # Single snapshot
            steward observe --live       # Continuous monitoring (tail -f mode)
            steward observe --interval 5 # Custom refresh interval
            steward observe --raw        # Raw JSON output
        """
        import time
        from datetime import datetime

        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        parser = argparse.ArgumentParser(prog="steward observe")
        parser.add_argument("--live", action="store_true", help="Continuous monitoring mode")
        parser.add_argument("--interval", type=int, default=2, help="Refresh interval in seconds")
        parser.add_argument("--raw", action="store_true", help="Raw JSON output (machine-readable)")
        parsed_args, _ = parser.parse_known_args(args)

        console = Console()

        def render_frame() -> None:
            """Render a single observation frame."""
            # 1. Load Intent Queue (Sankalpa - The Will)
            intent_path = Path(".opus_state/manas_intents.json")
            if intent_path.exists():
                try:
                    intents = json.loads(intent_path.read_text())
                except Exception as e:
                    intents = {"error": str(e)}
            else:
                intents = []

            # 2. Load Memory State (Smriti - The Memory)
            memory_path = Path(".opus_state/manas_memory.json")
            if memory_path.exists():
                try:
                    memory = json.loads(memory_path.read_text())
                except Exception:
                    memory = {}
            else:
                memory = {}

            # 3. Load Synaptic Weights (if exists)
            synapse_path = Path(".opus_state/synapses.json")
            if synapse_path.exists():
                try:
                    synapses = json.loads(synapse_path.read_text())
                except Exception:
                    synapses = {"schema": "v1", "weights": {}}
            else:
                synapses = {"schema": "v1", "weights": {}}

            # 4. OPUS-174: Load MANAS Biorhythm Awareness (Consciousness State)
            awareness_path = Path(".opus_state/manas_awareness.json")
            if awareness_path.exists():
                try:
                    awareness = json.loads(awareness_path.read_text())
                except Exception:
                    awareness = {"state": "unknown", "consciousness_level": 0.0}
            else:
                awareness = {"state": "unknown", "consciousness_level": 0.0, "tick": 0}

            # 5. Load Session State
            session_path = Path(".opus_state/session.json")
            session = {}
            if session_path.exists():
                try:
                    session = json.loads(session_path.read_text())
                except Exception:
                    pass

            # RAW MODE: Just dump JSON
            if parsed_args.raw:
                output = {
                    "timestamp": datetime.now().isoformat(),
                    "awareness": awareness,  # OPUS-174: Biorhythm state first!
                    "intents": intents,
                    "memory": memory,
                    "synapses": synapses,
                    "session": session,
                }
                print(json.dumps(output, indent=2, default=str))
                return

            # FORMATTED MODE: Rich console output
            console.clear()
            console.rule(f"[bold red]MANAS OBSERVER CONTROL :: {datetime.now().strftime('%H:%M:%S')}")

            # OPUS-174: Consciousness State Panel (BIORHYTHM)
            state = awareness.get("state", "unknown")
            level = awareness.get("consciousness_level", 0.0)
            tick = awareness.get("tick", 0)
            inputs = awareness.get("inputs", {})

            # Color-code by state
            state_colors = {
                "turiya": "bold magenta",
                "sattva": "bold green",
                "rajas": "bold yellow",
                "tamas": "dim white",
                "unknown": "dim red",
            }
            state_color = state_colors.get(state, "white")

            # Build consciousness bar (visual representation)
            bar_width = 20
            filled = int(level * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)

            # Build panel content
            awareness_content = (
                f"[{state_color}]State: {state.upper()}[/{state_color}]\n"
                f"Level: [{state_color}]{bar}[/{state_color}] {level:.2f}\n"
                f"Tick: {tick}\n"
            )

            # Add input breakdown if available
            if inputs:
                urgency = inputs.get("synaptic_urgency", 0)
                health = inputs.get("prakriti_health", 0)
                rhythm = inputs.get("kala_rhythm", 0.5)
                awareness_content += (
                    f"\n[dim]Inputs:[/dim]\n"
                    f"  Synaptic Urgency: {urgency:.2f} (×0.5)\n"
                    f"  Prakriti Health:  {health:.2f} (×0.3)\n"
                    f"  Kala Rhythm:      {rhythm:.2f} (×0.2)"
                )

            console.print(
                Panel(
                    awareness_content,
                    title=f"[{state_color}]CONSCIOUSNESS (BIORHYTHM)[/{state_color}]",
                    border_style=state_color.replace("bold ", ""),
                )
            )

            # Session Status Panel
            session_status = session.get("status", "UNKNOWN")
            focus = session.get("current_focus", "None")
            console.print(
                Panel(
                    f"Status: {session_status}\nFocus: {focus}", title="[bold blue]Session State", border_style="blue"
                )
            )

            # Intent Queue Table
            table = Table(title="Intent Queue (Sankalpa)", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim", width=10)
            table.add_column("Type", width=15)
            table.add_column("Description", width=40)
            table.add_column("Status", justify="center", width=12)

            if isinstance(intents, list):
                for intent in intents[:10]:  # Limit display
                    i_id = str(intent.get("id", "???"))[:10]
                    i_type = intent.get("type", intent.get("intent_type", "unknown"))
                    i_desc = intent.get("description", intent.get("title", str(intent)))[:40]
                    i_status = intent.get("status", "PENDING")

                    status_color = (
                        "green"
                        if i_status in ("COMPLETED", "completed")
                        else "yellow"
                        if i_status in ("PENDING", "pending")
                        else "red"
                    )
                    table.add_row(i_id, i_type, i_desc, f"[{status_color}]{i_status}[/{status_color}]")

                if len(intents) > 10:
                    table.add_row("...", f"+{len(intents) - 10} more", "", "")
            else:
                table.add_row("-", "Error/Empty", str(intents)[:40], "[dim]N/A[/dim]")

            console.print(table)

            # Synapse Count + Consciousness Summary
            weight_count = len(synapses.get("weights", {}))
            console.print(
                f"\n[dim]Synapses: {weight_count} | Consciousness: {state.upper()} ({level:.2f}) | "
                f"Interval: {parsed_args.interval}s | Ctrl+C to exit[/dim]"
            )

        try:
            if parsed_args.live:
                while True:
                    render_frame()
                    time.sleep(parsed_args.interval)
            else:
                render_frame()
                return 0
        except KeyboardInterrupt:
            console.print("\n[bold red]Observer disconnected.[/bold red]")
            return 0
        except Exception as e:
            print(f"❌ OBSERVER ERROR: {e}")
            return 1

    # =========================================================================
    # OPUS-109: INTENT DEFIBRILLATOR - Force-Execute Stuck Intents
    # =========================================================================

    def cmd_poke(self, args: List[str]) -> int:
        """
        OPUS-109: Intent Defibrillator - Force-execute stuck intents.

        When intents are stuck in 'pending', this command shocks them back to life.
        The Operator's manual override for the cognitive system.

        Usage:
            steward poke                    # List all pending intents
            steward poke <intent_id>        # Execute specific intent
            steward poke --first            # Execute first pending intent
            steward poke --all              # Execute ALL pending intents (dangerous)
            steward poke --dry-run <id>     # Show what would happen without executing
        """
        from rich.console import Console
        from rich.table import Table

        parser = argparse.ArgumentParser(prog="steward poke")
        parser.add_argument("intent_id", nargs="?", help="Intent ID to execute")
        parser.add_argument("--first", action="store_true", help="Execute first pending intent")
        parser.add_argument("--all", action="store_true", help="Execute ALL pending intents")
        parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
        parsed_args, _ = parser.parse_known_args(args)

        console = Console()

        # Load intents
        intent_path = Path(".opus_state/manas_intents.json")
        if not intent_path.exists():
            console.print("[red]❌ No intent file found. MANAS has no pending thoughts.[/red]")
            return 1

        try:
            data = json.loads(intent_path.read_text())
            entries = data.get("intents", [])
        except Exception as e:
            console.print(f"[red]❌ Failed to load intents: {e}[/red]")
            return 1

        # Filter pending
        pending = [e for e in entries if e.get("status") == "pending"]

        if not pending:
            console.print("[green]✅ No pending intents. MANAS mind is clear.[/green]")
            return 0

        # No args = list pending
        if not parsed_args.intent_id and not parsed_args.first and not parsed_args.all:
            console.print(f"\n[bold]⚡ DEFIBRILLATOR: {len(pending)} pending intents[/bold]\n")
            table = Table(show_header=True, header_style="bold yellow")
            table.add_column("ID", width=25)
            table.add_column("Type", width=20)
            table.add_column("Title", width=40)
            table.add_column("Age")

            from datetime import datetime

            for entry in pending[:20]:
                intent = entry.get("intent", {})
                i_id = intent.get("id", "???")
                i_type = intent.get("intent_type", "unknown")
                i_title = intent.get("title", "")[:40]
                created = intent.get("created_at", "")
                age = "?"
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        delta = datetime.now() - dt.replace(tzinfo=None)
                        if delta.days > 0:
                            age = f"{delta.days}d"
                        elif delta.seconds > 3600:
                            age = f"{delta.seconds // 3600}h"
                        else:
                            age = f"{delta.seconds // 60}m"
                    except Exception:
                        pass
                table.add_row(i_id, i_type, i_title, age)

            console.print(table)
            console.print("\n[dim]Use: steward poke <intent_id> to execute[/dim]")
            return 0

        # Load MANAS kernel for execution
        try:
            from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

            # OPUS-167: Use singleton pattern to avoid expensive re-initialization
            kernel = CognitiveKernel.get_instance(workspace=Path("."))
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize MANAS kernel: {e}[/red]")
            return 1

        # Determine which intents to execute
        targets = []
        if parsed_args.all:
            targets = [e.get("intent", {}).get("id") for e in pending]
            console.print(f"[yellow]⚠️  EXECUTING ALL {len(targets)} PENDING INTENTS[/yellow]")
        elif parsed_args.first:
            targets = [pending[0].get("intent", {}).get("id")]
        elif parsed_args.intent_id:
            targets = [parsed_args.intent_id]

        # Execute
        success_count = 0
        for intent_id in targets:
            if parsed_args.dry_run:
                console.print(f"[dim]DRY-RUN: Would execute {intent_id}[/dim]")
                continue

            console.print(f"⚡ Shocking intent: [bold]{intent_id}[/bold]...")
            try:
                result = kernel.approve_intent(intent_id)
                if result:
                    console.print("   [green]✅ EXECUTED[/green]")
                    success_count += 1
                else:
                    console.print("   [red]❌ FAILED (check logs)[/red]")
            except Exception as e:
                console.print(f"   [red]❌ ERROR: {e}[/red]")

        if not parsed_args.dry_run:
            console.print(f"\n[bold]Defibrillator complete: {success_count}/{len(targets)} intents executed[/bold]")

        return 0 if success_count == len(targets) else 1

    # =========================================================================
    # OPUS-042: SAMVADA - Human-MANAS Real-Time Dialogue
    # =========================================================================

    def cmd_chat(self, args: List[str]) -> int:
        """
        Send a message to MANAS and get a response.

        OPUS-042: SAMVADA (The Dialogue)
        OPUS-075: Now uses headless mode (JnanaHandler direct) - no daemon needed!

        Usage:
            steward chat "Status report"
            steward chat Check the CI status
            steward chat "What intents are pending?"
        """
        if not args:
            print("Usage: steward chat <message>")
            print('       steward chat "Status report"')
            print("       steward chat Check the CI status")
            print("\n❌ No message provided")
            return 1

        # Join all args into a single message (handles unquoted multi-word)
        message = " ".join(args)

        try:
            # OPUS-075 FIX: Use headless mode instead of socket
            # This works without daemon - direct JnanaHandler invocation
            import asyncio
            from pathlib import Path

            from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler
            from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

            handler = JnanaHandler(workspace=Path.cwd())

            # OPUS-080: Wire up LLM provider for intelligent responses
            # JnanaHandler expects .chat(prompt) -> str, but providers have .invoke() -> LLMResponse
            # Create adapter to bridge the interface gap
            try:
                from vibe_core.runtime.providers.factory import get_default_provider

                provider = get_default_provider()
                if hasattr(provider, "invoke") and provider.__class__.__name__ != "NoOpProvider":
                    # Create adapter: chat(prompt) -> invoke(prompt).content
                    class LLMAdapter:
                        def __init__(self, provider):
                            self._provider = provider

                        def chat(self, prompt):
                            # Use haiku for fast, cheap chat responses
                            response = self._provider.invoke(
                                prompt=prompt if isinstance(prompt, str) else str(prompt),
                                model="anthropic/claude-3.5-haiku",  # Fast & cheap
                                max_tokens=1024,
                                temperature=0.7,
                            )
                            return response.content

                    handler.configure_llm(LLMAdapter(provider))
                    logger.info("MANAS: LLM provider configured (OpenRouter)")
            except Exception as e:
                logger.debug(f"LLM provider not available: {e} - using basic mode")

            msg = SamvadaMessage(content=message, msg_type="chat")
            response = asyncio.run(handler.handle(msg))

            if response.success:
                print(f"🗣️ MANAS: {response.content}")
                return 0
            else:
                print(f"❌ Error: {response.error}")
                return 1

        except Exception as e:
            print(f"❌ Chat failed: {e}")
            import traceback

            traceback.print_exc()
            return 1

    # =========================================================================
    # OPUS-075: MANAS HIL BRIDGE COMMANDS
    # =========================================================================

    def cmd_pending(self, args: List[str]) -> int:
        """
        List pending intents awaiting human approval.

        Usage:
            steward pending
            steward pending --json
        """
        from pathlib import Path

        from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

        router = IntentRouter(workspace=Path.cwd())
        pending = router.list_pending_intents()

        json_output = "--json" in args

        if json_output:
            print(json.dumps(pending, indent=2, default=str))
            return 0

        if not pending:
            print("📭 No pending intents")
            return 0

        print("📬 PENDING INTENTS (awaiting approval)")
        print("=" * 60)

        for intent in pending:
            print(f"\n🆔 {intent['id']}")
            print(f"   Type:       {intent['intent_type']}")
            print(f"   Title:      {intent['title']}")
            print(f"   Confidence: {intent.get('confidence', 0.5):.2f}")
            print(f"   Reason:     {intent.get('gate_reason', 'unknown')}")
            print(f"   Queued:     {intent.get('queued_at', 'unknown')}")
        """List pending - Moved to plugin."""
        print("❌ Moved to plugin 'opus_assistant'")
        return 1

    def cmd_approve(self, args: List[str]) -> int:
        """Approve intent - Moved to plugin."""
        print("❌ Moved to plugin 'opus_assistant'")
        return 1

    def cmd_reject(self, args: List[str]) -> int:
        """Reject intent - Moved to plugin."""
        print("❌ Moved to plugin 'opus_assistant'")
        return 1

    def cmd_karma(self, args: List[str]) -> int:
        """Show karma - Moved to plugin."""
        print("❌ Moved to plugin 'opus_assistant'")
        return 1

    # =========================================================================
    # OPUS-031 Layer 4: AUTONOMOUS CONDUCTOR COMMANDS
    # =========================================================================

    def cmd_execute(self, args: List[str]) -> int:
        """
        Execute a circuit directly with optional headless boot.

        OPUS-031 Layer 4: The Ignition Key for Autonomous Operation.

        Usage:
            steward execute --circuit <path>              # Full boot + execute
            steward execute --circuit <path> --headless   # Fast headless boot
            steward execute --circuit <path> --input "..." # Execute with custom input

        This command:
        1. Boots the kernel in the appropriate mode (FULL or HEADLESS)
        2. Loads the specified circuit YAML
        3. Executes the circuit via CognitiveCircuitExecutor
        4. Returns the result

        Headless mode (< 5 seconds boot):
        - NO agent discovery
        - NO network gateway
        - NO daily ritual
        - Perfect for CI/CD, maintenance circuits, autonomous operation
        """
        from pathlib import Path

        import yaml

        # Parse arguments
        circuit_path = None
        user_input = None
        headless = False
        non_interactive = False

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--circuit" and i + 1 < len(args):
                circuit_path = args[i + 1]
                i += 2
            elif arg == "--input" and i + 1 < len(args):
                user_input = args[i + 1]
                i += 2
            elif arg == "--headless":
                headless = True
                i += 1
            elif arg == "--non-interactive":
                non_interactive = True
                i += 1
            else:
                i += 1

        if not circuit_path:
            print("❌ Missing required argument: --circuit <path>")
            print("\nUsage:")
            print("  steward execute --circuit <path> [--input <text>] [--headless]")
            return 1

        circuit_file = Path(circuit_path)
        if not circuit_file.exists():
            # Try relative to knowledge/circuits
            alt_path = Path("knowledge/circuits") / circuit_path
            if alt_path.exists():
                circuit_file = alt_path
            else:
                print(f"❌ Circuit file not found: {circuit_path}")
                return 1

        # Use provided input or fallback to default
        final_input = user_input or f"CLI execute: {circuit_file.stem}"

        # Determine boot mode
        boot_mode = BootMode.HEADLESS if headless else BootMode.FULL

        print("🚀 AUTONOMOUS CIRCUIT EXECUTION")
        print("=" * 50)
        print(f"   Circuit: {circuit_file}")
        print(f"   Mode:    {boot_mode.value.upper()}")
        print(f"   Input:   {final_input}")
        if non_interactive:
            print("   Prompts: DISABLED")
        print()

        try:
            # Load circuit definition
            with open(circuit_file) as f:
                circuit_def = yaml.safe_load(f)

            circuit_id = circuit_def.get("circuit", {}).get("id", "UNKNOWN")
            print(f"📋 Loaded circuit: {circuit_id}")

            # Boot kernel with appropriate mode
            print(f"\n⚡ Booting kernel ({boot_mode.value})...")
            from vibe_core.kernel_impl import RealVibeKernel

            kernel = RealVibeKernel(ledger_path=Path("data/vibe_ledger.db"))
            kernel.boot(boot_mode=boot_mode)
            print("✅ Kernel online")

            # Get or create circuit executor
            print("\n🔄 Executing circuit...")
            from vibe_core.cartridges.system.envoy.blueprint_generator import (
                CompilationResult,
            )
            from vibe_core.cortex.engines.circuit_engine import (
                CognitiveCircuitExecutor,
            )

            executor = CognitiveCircuitExecutor(kernel)

            # Extract circuit definition (handle both nested and flat formats)
            circuit_inner = circuit_def.get("circuit", circuit_def)

            # Create a minimal compilation result for direct execution
            compilation = CompilationResult(
                is_syscall=False,
                syscall_request=None,
                playbook_vars={"circuit_id": circuit_id},
                confidence=1.0,
            )

            # Execute circuit directly
            result = executor._execute_circuit(
                circuit_def=circuit_inner,
                raw_input=final_input,
                compilation=compilation,
                requester_id="cli:execute",
            )

            # Display result
            print()
            print("=" * 50)
            if result.success:
                print(f"✅ Circuit completed: {result.final_state}")
                print(f"   States visited: {len(result.state_history)}")
                print(f"   Syscalls: {result.syscall_count}")
            else:
                print(f"❌ Circuit failed: {result.final_state}")
                if result.error:
                    print(f"   Error: {result.error}")

            # Cleanup
            try:
                kernel.shutdown()
            except Exception:
                pass  # Best effort cleanup

            return 0 if result.success else 1

        except Exception as e:
            print(f"❌ Execution failed: {e}")
            import traceback

            traceback.print_exc()
            return 1

    # =========================================================================
    # HELP
    # =========================================================================

    def _print_help(self, plugin_commands: Dict[str, CLICommand]):
        print("🎛️  STEWARD UNIFIED CLI")
        print("=======================")

        print("\nSYSTEM COMMANDS:")
        for name in sorted(self._legacy_map.keys()):
            print(f"  {name:<15} (System)")

        print("\nUNIFIED RUN (OPUS-307 D+++):")
        print("  run              THE unified command - Tool/Circuit/Agent")
        print("                   'steward run <capability>' - Pratyaya decides")
        print("                   'steward run list' - List all capabilities")
        print("                   'steward run info <cap>' - Show details")

        print("\nTOOL PROTOCOL (OPUS-307 D):")
        print("  tool             Use 'steward tool --help' for subcommands")

        print("\nCIRCUIT PROTOCOL (OPUS-307 D++):")
        print("  circuit          Use 'steward circuit --help' for subcommands")

        print("\nOPUS-307 UNIFIED SERVICES:")
        print("  config           Config management (list, show, validate)")
        print("  prompts          Prompt registry (list, get, info)")
        print("  sections         Phoenix sections (list, info)")
        print("  plugins          Plugin registry (list, info, status)")

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

        print("\nMANAS HIL BRIDGE (Human-In-The-Loop):")
        manas_help = {
            "pending": "List pending intents [--json]",
            "approve": "Approve intent <id> or --all",
            "reject": "Reject intent <id> [--reason]",
            "karma": "Show karma statistics [--json]",
        }
        for name, help_text in manas_help.items():
            print(f"  {name:<15} {help_text}")

        print("\nCONDUCTOR COMMANDS (Autonomous Execution):")
        conductor_help = {
            "execute": "Execute circuit [--circuit <path>] [--headless]",
        }
        for name, help_text in conductor_help.items():
            print(f"  {name:<15} {help_text}")

        print("\nPLUGIN COMMANDS:")
        for name, cmd in sorted(plugin_commands.items()):
            print(f"  {name:<15} {cmd.help}")
