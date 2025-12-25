"""
OPUS-307: Config CLI

CLI interface for Phoenix config/settings (YAML-based).

Usage:
    steward config list               # List all config files
    steward config show <section>     # Show section config
    steward config validate           # Validate all configs
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.section_service import SectionService

logger = logging.getLogger("CONFIG_CLI")


@register_cli
class ConfigCLI:
    """
    CLI for Config/Settings management.

    OPUS-307: Unified config access via Phoenix sections.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="config",
            description="Phoenix config management (list, show, validate)",
            domain="system",
            subcommands=["list", "show", "validate"],
            tags=["config", "settings", "phoenix"],
        )

    def __init__(self):
        """Initialize config CLI."""
        self._config_dir = Path("config")

    def run(self, args: List[str]) -> int:
        """Execute config command."""
        if not args:
            return self._cmd_list([])

        subcommand = args[0]
        sub_args = args[1:]

        commands = {
            "list": self._cmd_list,
            "show": self._cmd_show,
            "validate": self._cmd_validate,
            "--help": self._cmd_help,
            "-h": self._cmd_help,
        }

        handler = commands.get(subcommand)
        if handler:
            return handler(sub_args)

        print(f"Unknown subcommand: {subcommand}")
        return self._cmd_help([])

    def _cmd_list(self, args: List[str]) -> int:
        """List all config files."""
        if not self._config_dir.exists():
            print(f"Config directory not found: {self._config_dir}")
            return 1

        yaml_files = sorted(self._config_dir.glob("*.yaml"))

        print(f"\n{'=' * 60}")
        print(f"CONFIG FILES ({len(yaml_files)} total)")
        print(f"{'=' * 60}\n")

        for f in yaml_files:
            size = f.stat().st_size
            name = f.stem
            print(f"  {name:<20} {size:>6} bytes  {f}")

        print(f"\n{'=' * 60}")
        print("Usage: steward config show <name>")
        print(f"{'=' * 60}")
        return 0

    def _cmd_show(self, args: List[str]) -> int:
        """Show section config."""
        if not args:
            print("Usage: steward config show <name>")
            return 1

        name = args[0]
        yaml_path = self._config_dir / f"{name}.yaml"

        if not yaml_path.exists():
            print(f"Config not found: {yaml_path}")
            print(f"Available: {', '.join(f.stem for f in self._config_dir.glob('*.yaml'))}")
            return 1

        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)

            print(f"\n{'=' * 60}")
            print(f"CONFIG: {name}")
            print(f"{'=' * 60}\n")

            # Pretty print YAML
            print(yaml.dump(data, default_flow_style=False, indent=2, allow_unicode=True))

            print(f"{'=' * 60}")
            return 0

        except Exception as e:
            print(f"Error reading {yaml_path}: {e}")
            return 1

    def _cmd_validate(self, args: List[str]) -> int:
        """Validate all configs."""
        if not self._config_dir.exists():
            print(f"Config directory not found: {self._config_dir}")
            return 1

        yaml_files = sorted(self._config_dir.glob("*.yaml"))
        errors = []
        valid = 0

        print(f"\n{'=' * 60}")
        print("VALIDATING CONFIGS")
        print(f"{'=' * 60}\n")

        for f in yaml_files:
            try:
                with open(f) as file:
                    data = yaml.safe_load(file)
                if data is None:
                    errors.append((f.stem, "Empty file"))
                    print(f"  [!] {f.stem:<20} Empty file")
                else:
                    valid += 1
                    keys = len(data) if isinstance(data, dict) else "N/A"
                    print(f"  [✓] {f.stem:<20} Valid ({keys} keys)")
            except yaml.YAMLError as e:
                errors.append((f.stem, str(e)))
                print(f"  [✗] {f.stem:<20} YAML Error: {e}")
            except Exception as e:
                errors.append((f.stem, str(e)))
                print(f"  [✗] {f.stem:<20} Error: {e}")

        print(f"\n{'=' * 60}")
        print(f"Valid: {valid}/{len(yaml_files)}")
        if errors:
            print(f"Errors: {len(errors)}")
        print(f"{'=' * 60}")

        return 0 if not errors else 1

    def _cmd_help(self, args: List[str]) -> int:
        """Show help."""
        print("""
Usage: steward config <command> [args]

Commands:
  list              List all config files in config/
  show <name>       Show config content (e.g., 'llm', 'agents')
  validate          Validate all YAML configs

Examples:
  steward config list
  steward config show llm
  steward config show agents
  steward config validate
""")
        return 0
