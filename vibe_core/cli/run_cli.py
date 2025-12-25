"""
OPUS-307 D+++: Unified Run CLI

THE SINGLE COMMAND for all capabilities.
No more "steward tool run" vs "steward circuit run".

Just: steward run <capability> [--params]

Pratyaya decides whether it's a Tool, Circuit, or Agent.

Usage:
    steward run heal_codebase --file main.py
    steward run watchman.standards --action inspect_all
    steward run simple_query --input "What is the system status?"
"""

import json
import logging
import sys
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.capability import CapabilityMeta, CapabilityResult, CapabilityType
from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.unified_registry import UnifiedRegistry

logger = logging.getLogger("RUN_CLI")


@register_cli
class RunCLI:
    """
    Unified execution CLI.

    THE FRACTAL PRINCIPLE IN ACTION:
    - User doesn't need to know if capability is tool/circuit/agent
    - Pratyaya (UnifiedRegistry) handles the routing
    - Same interface for everything
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="run",
            description="Unified Capability CLI (fractal execution)",
            domain="execution",
            subcommands=["list", "info", "search"],
            tags=["run", "capability", "fractal", "unified"],
        )

    def __init__(self):
        self._registry: Optional[UnifiedRegistry] = None

    def _ensure_registry(self) -> UnifiedRegistry:
        """Lazy-load unified registry via ServiceRegistry (OPUS-307 DI pattern)."""
        if self._registry is None:
            # OPUS-307: Use ServiceRegistry DI instead of get_instance() singleton
            self._registry = ServiceRegistry.get(UnifiedRegistry)
            if self._registry is None:
                # Fallback: create and register
                self._registry = UnifiedRegistry()
                ServiceRegistry.register(UnifiedRegistry, self._registry)
            self._registry.discover_all()
        return self._registry

    def run(self, args: List[str]) -> int:
        """
        Main entry point.

        Routes to: list, info, run (default), search
        """
        if not args:
            self._print_usage()
            return 1

        # Check for subcommands
        first = args[0]

        if first == "list":
            return self.cmd_list(args[1:])
        elif first == "info":
            return self.cmd_info(args[1:])
        elif first == "search":
            return self.cmd_search(args[1:])
        elif first in ("--help", "-h", "help"):
            self._print_usage()
            return 0
        else:
            # Default: treat first arg as capability_id
            return self.cmd_run(args)

    def _print_usage(self):
        """Print usage."""
        print("""
Unified Run CLI (OPUS-307 D+++)

THE FRACTAL PRINCIPLE: Tool, Circuit, Agent are all just "capabilities".

Usage:
    steward run <capability> [--param=value]    Execute capability
    steward run list [--type atomic|molecular]  List all capabilities
    steward run info <capability>               Show capability details
    steward run search <query>                  Search capabilities

Examples:
    steward run heal_codebase --file main.py
    steward run watchman.standards --action inspect_all
    steward run simple_query --input "status?"
    steward run list --type molecular
    steward run search heal
""")

    def cmd_list(self, args: List[str]) -> int:
        """List all capabilities."""
        registry = self._ensure_registry()

        as_json = "--json" in args
        cap_type = None

        for i, arg in enumerate(args):
            if arg == "--type" and i + 1 < len(args):
                type_str = args[i + 1].lower()
                if type_str == "atomic":
                    cap_type = CapabilityType.ATOMIC
                elif type_str == "molecular":
                    cap_type = CapabilityType.MOLECULAR
                elif type_str == "organic":
                    cap_type = CapabilityType.ORGANIC

        if cap_type:
            capabilities = registry.list_by_type(cap_type)
        else:
            capabilities = registry.list_all()

        if as_json:
            output = {
                "total": len(capabilities),
                "capabilities": [
                    {
                        "id": m.capability_id,
                        "type": m.capability_type.value,
                        "description": m.description[:100],
                    }
                    for m in capabilities
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"CAPABILITIES ({len(capabilities)} total)")
            print(f"{'=' * 60}\n")

            # Group by type
            by_type: Dict[CapabilityType, List[CapabilityMeta]] = {}
            for m in capabilities:
                if m.capability_type not in by_type:
                    by_type[m.capability_type] = []
                by_type[m.capability_type].append(m)

            type_names = {
                CapabilityType.ATOMIC: "ATOMIC (Tools)",
                CapabilityType.MOLECULAR: "MOLECULAR (Circuits)",
                CapabilityType.ORGANIC: "ORGANIC (Agents)",
            }

            for ctype, caps in sorted(by_type.items(), key=lambda x: x[0].value):
                print(f"[{type_names.get(ctype, ctype.value)}] ({len(caps)})")
                print("-" * 50)
                for m in sorted(caps, key=lambda x: x.capability_id):
                    desc = m.description[:45] + "..." if len(m.description) > 45 else m.description
                    print(f"  {m.capability_id:<35} {desc}")
                print()

        return 0

    def cmd_info(self, args: List[str]) -> int:
        """Show capability info."""
        if not args:
            print("Error: capability_id required")
            return 1

        cap_id = args[0]
        as_json = "--json" in args

        registry = self._ensure_registry()
        meta = registry.get_meta(cap_id)

        if not meta:
            print(f"Error: Capability '{cap_id}' not found")
            print("\nTry: steward run search <query>")
            return 1

        cap = registry.get(cap_id)

        if as_json:
            output = {
                "id": meta.capability_id,
                "type": meta.capability_type.value,
                "description": meta.description,
                "version": meta.version,
                "parameters": meta.parameters_schema,
                "tags": meta.tags,
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            type_name = {
                CapabilityType.ATOMIC: "Tool (ATOMIC)",
                CapabilityType.MOLECULAR: "Circuit (MOLECULAR)",
                CapabilityType.ORGANIC: "Agent (ORGANIC)",
            }.get(meta.capability_type, meta.capability_type.value)

            print(f"\n{'=' * 60}")
            print(f"CAPABILITY: {meta.capability_id}")
            print(f"{'=' * 60}")
            print(f"Type:        {type_name}")
            print(f"Version:     {meta.version}")
            print(f"Description: {meta.description}")
            if meta.tags:
                print(f"Tags:        {', '.join(meta.tags)}")
            if meta.source_file:
                print(f"Source:      {meta.source_file}")
            print()

            if meta.parameters_schema:
                print("PARAMETERS:")
                print("-" * 40)
                for name, spec in meta.parameters_schema.items():
                    req = "[required]" if spec.get("required") else "[optional]"
                    desc = spec.get("description", "")[:40]
                    print(f"  --{name:<20} {req} {desc}")
                print()

        return 0

    def cmd_search(self, args: List[str]) -> int:
        """Search capabilities."""
        if not args:
            print("Error: search query required")
            return 1

        query = " ".join(args)
        registry = self._ensure_registry()
        results = registry.search(query)

        if not results:
            print(f"No capabilities found matching: {query}")
            return 1

        print(f"\nFound {len(results)} capabilities matching '{query}':\n")
        for m in results:
            type_icon = {"atomic": "[T]", "molecular": "[C]", "organic": "[A]"}.get(m.capability_type.value, "[?]")
            desc = m.description[:50] + "..." if len(m.description) > 50 else m.description
            print(f"  {type_icon} {m.capability_id:<35} {desc}")

        return 0

    def cmd_run(self, args: List[str]) -> int:
        """
        Execute a capability.

        This is the main action. Pratyaya decides the executor.
        """
        if not args:
            print("Error: capability_id required")
            return 1

        cap_id = args[0]
        remaining = args[1:]

        # Parse parameters
        params: Dict[str, Any] = {}
        as_json = False

        i = 0
        while i < len(remaining):
            arg = remaining[i]
            if arg == "--json":
                as_json = True
            elif arg.startswith("--") and "=" in arg:
                key, value = arg[2:].split("=", 1)
                params[key] = value
            elif arg.startswith("--") and i + 1 < len(remaining):
                key = arg[2:]
                value = remaining[i + 1]
                params[key] = value
                i += 1
            i += 1

        registry = self._ensure_registry()
        cap = registry.get(cap_id)

        if not cap:
            print(f"Error: Capability '{cap_id}' not found")
            # Suggest similar
            similar = registry.search(cap_id)
            if similar:
                print("\nDid you mean:")
                for m in similar[:5]:
                    print(f"  - {m.capability_id}")
            return 1

        meta = registry.get_meta(cap_id)
        type_name = meta.capability_type.value if meta else "unknown"

        print(f"Executing {cap_id} ({type_name})...")

        try:
            result: CapabilityResult = cap.execute(params)

            if as_json:
                print(
                    json.dumps(
                        {
                            "capability_id": result.capability_id,
                            "type": result.capability_type.value,
                            "success": result.success,
                            "output": result.output,
                            "error": result.error,
                            "execution_time_ms": result.execution_time_ms,
                            "metadata": result.metadata,
                        },
                        indent=2,
                        default=str,
                    )
                )
            else:
                if result.success:
                    print(f"\n✅ {cap_id} completed successfully")
                    print(f"Time: {result.execution_time_ms:.2f}ms")
                    if result.output:
                        print(f"Output: {result.output}")
                    if result.metadata:
                        for k, v in result.metadata.items():
                            print(f"  {k}: {v}")
                else:
                    print(f"\n❌ {cap_id} failed")
                    if result.error:
                        print(f"Error: {result.error}")

            return 0 if result.success else 1

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            print(f"Error: {e}")
            return 1
