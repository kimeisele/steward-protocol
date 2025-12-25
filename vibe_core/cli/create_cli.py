"""
OPUS-307 Phase 5: Create CLI

Scaffold new agents, circuits, and cartridges via CLI.
GAD-000 compliance: Everything must be CLI-operable.

Usage:
    steward create agent <name> [--domain <domain>]
    steward create circuit <name> [--domain <domain>]
    steward create cartridge <name> [--domain <domain>]
    steward create plugin <name>
"""

import sys
from pathlib import Path
from typing import List

from vibe_core.genesis import GenesisService
from vibe_core.genesis.types import ModuleType
from vibe_core.protocols.cli import CLIMeta, register_cli


@register_cli
class CreateCLI:
    """
    Create CLI - Scaffold new system components.

    GAD-000: The system must be fully operable via CLI.
    This includes creating new agents, circuits, and cartridges.
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="create",
            description="Scaffold new agents, circuits, cartridges",
            domain="genesis",
            subcommands=["agent", "circuit", "cartridge", "plugin"],
            tags=["create", "scaffold", "genesis", "gad-000"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry point."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_usage()
            return 0

        cmd = args[0]
        remaining = args[1:]

        if cmd == "agent":
            return self.cmd_agent(remaining)
        elif cmd == "circuit":
            return self.cmd_circuit(remaining)
        elif cmd == "cartridge":
            return self.cmd_cartridge(remaining)
        elif cmd == "plugin":
            return self.cmd_plugin(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print(__doc__)

    def _parse_args(self, args: List[str]) -> tuple:
        """Parse name and --domain flag."""
        name = None
        domain = "system"

        i = 0
        while i < len(args):
            if args[i] == "--domain" and i + 1 < len(args):
                domain = args[i + 1]
                i += 2
            elif not args[i].startswith("-"):
                name = args[i]
                i += 1
            else:
                i += 1

        return name, domain

    def cmd_agent(self, args: List[str]) -> int:
        """Create a new agent (cartridge with agent role)."""
        name, domain = self._parse_args(args)

        if not name:
            print("Usage: steward create agent <name> [--domain <domain>]")
            print("Example: steward create agent researcher --domain science")
            return 1

        # Agents are cartridges in agent_city
        target_path = Path.cwd() / "vibe_core" / "cartridges" / "agent_city" / name

        if target_path.exists():
            print(f"Agent '{name}' already exists at {target_path}")
            return 1

        genesis = GenesisService.get_instance()
        result = genesis.scaffold_new(
            path=target_path,
            module_type=ModuleType.CARTRIDGE,
            context={
                "name": name.upper(),
                "domain": domain.upper(),
                "description": f"{name.title()} Agent",
                "is_agent": True,
            },
        )

        if result.build_result.success:
            print(f"Agent '{name}' created at {target_path}")
            print(f"  Files created: {result.build_result.files_created_count}")
            print(f"  Domain: {domain}")
            print()
            print("Next steps:")
            print(f"  1. Edit {target_path}/cartridge.yaml")
            print(f"  2. Implement tools in {target_path}/tools/")
            print(f"  3. Run: steward {name} --help")
            return 0
        else:
            print(f"Failed to create agent: {result.build_result.errors}")
            return 1

    def cmd_circuit(self, args: List[str]) -> int:
        """Create a new circuit."""
        name, domain = self._parse_args(args)

        if not name:
            print("Usage: steward create circuit <name> [--domain <domain>]")
            print("Example: steward create circuit deploy_v1 --domain ops")
            return 1

        # Circuits go in playbooks directory
        target_path = Path.cwd() / "playbooks" / f"{name}.yaml"

        if target_path.exists():
            print(f"Circuit '{name}' already exists at {target_path}")
            return 1

        # Create minimal circuit YAML
        circuit_yaml = f"""# Circuit: {name}
# Domain: {domain}
# Created via: steward create circuit

id: {name}
name: {name.replace("_", " ").title()}
domain: {domain.upper()}
description: |
  TODO: Add description

# Entry state
entry: start

# States
states:
  start:
    description: Initial state
    transitions:
      - to: complete
        condition: always

  complete:
    description: Circuit complete
    terminal: true

# Agents involved
agents: []

# Tools available
tools: []
"""

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(circuit_yaml)

        print(f"Circuit '{name}' created at {target_path}")
        print()
        print("Next steps:")
        print(f"  1. Edit {target_path}")
        print("  2. Define states and transitions")
        print(f"  3. Run: steward run {name}")
        return 0

    def cmd_cartridge(self, args: List[str]) -> int:
        """Create a new cartridge."""
        name, domain = self._parse_args(args)

        if not name:
            print("Usage: steward create cartridge <name> [--domain <domain>]")
            print("Example: steward create cartridge notifier --domain comms")
            return 1

        # Cartridges go in system directory
        target_path = Path.cwd() / "vibe_core" / "cartridges" / "system" / name

        if target_path.exists():
            print(f"Cartridge '{name}' already exists at {target_path}")
            return 1

        genesis = GenesisService.get_instance()
        result = genesis.scaffold_new(
            path=target_path,
            module_type=ModuleType.CARTRIDGE,
            context={
                "name": name.upper(),
                "domain": domain.upper(),
                "description": f"{name.title()} Cartridge",
            },
        )

        if result.build_result.success:
            print(f"Cartridge '{name}' created at {target_path}")
            print(f"  Files created: {result.build_result.files_created_count}")
            print(f"  Domain: {domain}")
            print()
            print("Next steps:")
            print(f"  1. Edit {target_path}/cartridge.yaml")
            print(f"  2. Implement tools in {target_path}/tools/")
            print(f"  3. Run: steward {name} --help")
            return 0
        else:
            print(f"Failed to create cartridge: {result.build_result.errors}")
            return 1

    def cmd_plugin(self, args: List[str]) -> int:
        """Create a new plugin."""
        name, _ = self._parse_args(args)

        if not name:
            print("Usage: steward create plugin <name>")
            print("Example: steward create plugin my_feature")
            return 1

        target_path = Path.cwd() / "vibe_core" / "plugins" / name

        if target_path.exists():
            print(f"Plugin '{name}' already exists at {target_path}")
            return 1

        genesis = GenesisService.get_instance()
        result = genesis.scaffold_new(
            path=target_path,
            module_type=ModuleType.PLUGIN,
            context={
                "name": name,
                "description": f"{name.title()} Plugin",
            },
        )

        if result.build_result.success:
            print(f"Plugin '{name}' created at {target_path}")
            print(f"  Files created: {result.build_result.files_created_count}")
            print()
            print("Next steps:")
            print(f"  1. Edit {target_path}/manifest.yaml")
            print(f"  2. Implement {target_path}/plugin_main.py")
            return 0
        else:
            print(f"Failed to create plugin: {result.build_result.errors}")
            return 1


def main():
    """Entry point."""
    cli = CreateCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
