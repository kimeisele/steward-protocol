"""
OPUS-307: Genesis CLI - The Stadtamt Made Visible

GAD-000 COMPLIANT: Infrastructure compliance is now observable.

"Every module must pass the 7-Point DNA test."

Usage:
    steward genesis audit [path]         Audit compliance of path/module
    steward genesis check [path]         Quick compliance check
    steward genesis classify <path>      Classify module type
    steward genesis scaffold <path>      Scaffold new module
    steward genesis types                List all module types
    steward genesis templates            List available templates
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("GENESIS_CLI")


@register_cli
class GenesisCLI:
    """
    Genesis CLI - Window into the Stadtamt.

    Makes infrastructure compliance visible. GAD-000 observability.
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="genesis",
            description="Infrastructure Compliance CLI - Stadtamt Made Visible",
            domain="infrastructure",
            subcommands=["audit", "check", "classify", "scaffold", "types", "templates"],
            tags=["genesis", "stadtamt", "compliance", "infrastructure"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry point."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_usage()
            return 0

        cmd = args[0]
        remaining = args[1:]

        if cmd == "audit":
            return self.cmd_audit(remaining)
        elif cmd == "check":
            return self.cmd_check(remaining)
        elif cmd == "classify":
            return self.cmd_classify(remaining)
        elif cmd == "scaffold":
            return self.cmd_scaffold(remaining)
        elif cmd == "types":
            return self.cmd_types(remaining)
        elif cmd == "templates":
            return self.cmd_templates(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print(__doc__)

    def _get_genesis(self):
        """Get GenesisService instance."""
        from vibe_core.genesis import GenesisService

        return GenesisService.get_instance()

    # =========================================================================
    # Commands
    # =========================================================================

    def cmd_audit(self, args: List[str]) -> int:
        """Audit compliance of a path/module."""
        as_json = "--json" in args
        path_str = None

        for arg in args:
            if not arg.startswith("--"):
                path_str = arg
                break

        path = Path(path_str) if path_str else Path(".")
        genesis = self._get_genesis()

        # Classify the path
        module_type = genesis.classify_path(path)

        # Run compliance audit
        result = genesis.ensure_compliance(path, module_type)

        output = {
            "path": str(path),
            "module_type": module_type.value if hasattr(module_type, "value") else str(module_type),
            "compliant": result.compliant if hasattr(result, "compliant") else result.success,
            "success": result.success,
            "message": result.message if hasattr(result, "message") else "",
            "created_files": result.created_files if hasattr(result, "created_files") else [],
            "missing_files": result.missing_files if hasattr(result, "missing_files") else [],
        }

        if as_json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("🏛️  GENESIS AUDIT - Stadtamt Compliance Check")
            print("=" * 60)
            print(f"\n📁 Path: {output['path']}")
            print(f"📦 Type: {output['module_type']}")

            status_icon = "✅" if output["compliant"] else "❌"
            print(f"📋 Status: {status_icon} {'COMPLIANT' if output['compliant'] else 'NON-COMPLIANT'}")

            if output.get("missing_files"):
                print(f"\n⚠️  Missing Files ({len(output['missing_files'])}):")
                for f in output["missing_files"]:
                    print(f"    • {f}")

            if output.get("created_files"):
                print(f"\n✅ Created Files ({len(output['created_files'])}):")
                for f in output["created_files"]:
                    print(f"    • {f}")

            if output.get("message"):
                print(f"\n💬 {output['message']}")

            print("\n" + "=" * 60)

        return 0 if output["compliant"] else 1

    def cmd_check(self, args: List[str]) -> int:
        """Quick compliance check."""
        as_json = "--json" in args
        path_str = None

        for arg in args:
            if not arg.startswith("--"):
                path_str = arg
                break

        path = Path(path_str) if path_str else Path(".")
        genesis = self._get_genesis()

        # Quick check
        is_compliant = genesis.quick_check(path)
        module_type = genesis.classify_path(path)

        output = {
            "path": str(path),
            "module_type": module_type.value if hasattr(module_type, "value") else str(module_type),
            "compliant": is_compliant,
        }

        if as_json:
            print(json.dumps(output, indent=2))
        else:
            status_icon = "✅" if is_compliant else "❌"
            print(f"{status_icon} {path}: {output['module_type']} - {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}")

        return 0 if is_compliant else 1

    def cmd_classify(self, args: List[str]) -> int:
        """Classify module type from path."""
        as_json = "--json" in args

        if not args or all(a.startswith("--") for a in args):
            print("Error: path required")
            return 1

        path_str = next(a for a in args if not a.startswith("--"))
        path = Path(path_str)
        genesis = self._get_genesis()

        module_type = genesis.classify_path(path)

        output = {
            "path": str(path),
            "module_type": module_type.value if hasattr(module_type, "value") else str(module_type),
        }

        if as_json:
            print(json.dumps(output, indent=2))
        else:
            print(f"📦 {path}: {output['module_type']}")

        return 0

    def cmd_scaffold(self, args: List[str]) -> int:
        """Scaffold a new module."""
        as_json = "--json" in args
        dry_run = "--dry-run" in args

        if not args or all(a.startswith("--") for a in args):
            print("Error: path required")
            print("Usage: steward genesis scaffold <path> [--dry-run]")
            return 1

        path_str = next(a for a in args if not a.startswith("--"))
        path = Path(path_str)

        # Get genesis with dry_run setting
        from vibe_core.genesis import GenesisService

        genesis = GenesisService(dry_run=dry_run)

        # Classify and scaffold
        module_type = genesis.classify_path(path)

        if module_type.value == "unknown":
            print(f"⚠️  Cannot classify path: {path}")
            print("    Supported paths:")
            print("    - vibe_core/plugins/<name>")
            print("    - vibe_core/cartridges/system/<name>")
            print("    - vibe_core/cartridges/agent_city/<name>")
            return 1

        result = genesis.scaffold_new(path, module_type, context={"name": path.name})

        output = {
            "path": str(path),
            "module_type": module_type.value,
            "success": result.success,
            "dry_run": dry_run,
            "created_files": result.created_files if hasattr(result, "created_files") else [],
        }

        if as_json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("🏗️  GENESIS SCAFFOLD")
            print("=" * 60)
            print(f"\n📁 Path: {output['path']}")
            print(f"📦 Type: {output['module_type']}")
            print(f"🔧 Dry Run: {'Yes' if dry_run else 'No'}")

            if output["success"]:
                print("\n✅ Scaffolded successfully!")
                if output.get("created_files"):
                    print(f"\n📄 Created Files ({len(output['created_files'])}):")
                    for f in output["created_files"]:
                        print(f"    • {f}")
            else:
                print("\n❌ Scaffold failed")

            print("\n" + "=" * 60)

        return 0 if output["success"] else 1

    def cmd_types(self, args: List[str]) -> int:
        """List all module types."""
        as_json = "--json" in args

        from vibe_core.genesis.types import ModuleType

        types = [{"name": mt.name, "value": mt.value} for mt in ModuleType]

        if as_json:
            print(json.dumps({"types": types}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("📦 MODULE TYPES")
            print("=" * 60 + "\n")
            for t in types:
                print(f"  • {t['name']:<15} ({t['value']})")
            print("\n" + "=" * 60)

        return 0

    def cmd_templates(self, args: List[str]) -> int:
        """List available templates."""
        as_json = "--json" in args

        genesis = self._get_genesis()
        template_registry = genesis.templates

        # Get all registered templates
        all_templates = {}
        for module_type in template_registry._templates:
            templates = template_registry.get_templates(module_type)
            all_templates[module_type.value if hasattr(module_type, "value") else str(module_type)] = list(
                templates.keys()
            )

        if as_json:
            print(json.dumps({"templates": all_templates}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("📄 AVAILABLE TEMPLATES")
            print("=" * 60 + "\n")
            for module_type, templates in all_templates.items():
                print(f"  {module_type}:")
                for t in templates:
                    print(f"    • {t}")
            print("\n" + "=" * 60)

        return 0


def main():
    """Entry point for direct execution."""
    cli = GenesisCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
