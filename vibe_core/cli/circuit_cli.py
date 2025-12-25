"""
OPUS-307 Phase D++: Circuit Protocol CLI

Auto-generated CLI for all circuits. Zero manual wiring.
Reads directly from CircuitLoader (circuit_id, description, states).

Usage:
    steward circuit list                           # List all circuits
    steward circuit info <name>                    # Show circuit schema
    steward circuit run <name> [--input=value]     # Execute circuit
    steward circuit status <execution_id>          # Check execution status
"""

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from vibe_core.loaders.circuit_loader import CircuitLoader, CircuitMeta, CircuitMetadata, CircuitRegistry
from vibe_core.protocols.cli import CLIMeta, register_cli

if TYPE_CHECKING:
    from vibe_core.cortex.engines.circuit_engine import CognitiveCircuitExecutor

logger = logging.getLogger("CIRCUIT_CLI")


@register_cli
class CircuitCLI:
    """
    Auto-generated CLI for Circuit Protocol.

    No manual command definitions needed.
    Discovers all circuits and generates CLI from their schemas.

    OPUS-307 D++: Shabda (CLI command) → Pratyaya (CircuitExecutor) → Karma (Result)
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="circuit",
            description="Circuit Protocol CLI (list, info, run, status)",
            domain="execution",
            subcommands=["list", "info", "run", "status"],
            tags=["circuit", "execution", "state_machine"],
        )

    def __init__(self):
        """Initialize circuit CLI."""
        self._circuits: Optional[CircuitRegistry] = None
        self._metadata: Optional[CircuitMetadata] = None
        self._executor: Optional["CognitiveCircuitExecutor"] = None

    def _ensure_circuits(self) -> Tuple[CircuitRegistry, CircuitMetadata]:
        """Lazy-load circuits via CircuitLoader."""
        if self._circuits is None:
            self._circuits, self._metadata = CircuitLoader.discover_and_load()
        return self._circuits, self._metadata or {}

    def run(self, args: List[str]) -> int:
        """
        Main entry point for circuit CLI.

        Routes to: list, info, run, status
        """
        if not args:
            self._print_usage()
            return 1

        subcommand = args[0]
        remaining = args[1:]

        if subcommand == "list":
            return self.cmd_list(remaining)
        elif subcommand == "info":
            return self.cmd_info(remaining)
        elif subcommand == "run":
            return self.cmd_run(remaining)
        elif subcommand == "status":
            return self.cmd_status(remaining)
        elif subcommand in ("--help", "-h", "help"):
            self._print_usage()
            return 0
        else:
            print(f"Unknown subcommand: {subcommand}")
            self._print_usage()
            return 1

    def _print_usage(self):
        """Print circuit CLI usage."""
        print("""
Circuit Protocol CLI (OPUS-307 Phase D++)

Usage:
    steward circuit list [--json] [--type <type>]    List all circuits
    steward circuit info <circuit_id>                Show circuit details
    steward circuit run <circuit_id> [--input=...]   Execute circuit
    steward circuit status <execution_id>            Check execution status

Examples:
    steward circuit list
    steward circuit list --json
    steward circuit list --type state_machine
    steward circuit info heal_codebase
    steward circuit run auto_heal --input "fix all violations"
    steward circuit status exec_123456
""")

    def cmd_list(self, args: List[str]) -> int:
        """
        List all discovered circuits.

        Usage:
            steward circuit list
            steward circuit list --json
            steward circuit list --type state_machine
        """
        circuits, metadata = self._ensure_circuits()

        # Parse args
        as_json = "--json" in args
        circuit_type = None
        for i, arg in enumerate(args):
            if arg == "--type" and i + 1 < len(args):
                circuit_type = args[i + 1]

        # Filter by type if specified
        if circuit_type:
            filtered_meta = {k: v for k, v in metadata.items() if v.circuit_type == circuit_type}
        else:
            filtered_meta = metadata

        if as_json:
            output = {
                "total": len(filtered_meta),
                "circuits": [
                    {
                        "circuit_id": meta.circuit_id,
                        "type": meta.circuit_type,
                        "description": meta.description,
                        "version": meta.version,
                        "file": str(meta.file_path),
                    }
                    for meta in filtered_meta.values()
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"CIRCUITS ({len(filtered_meta)} total)")
            print(f"{'=' * 60}\n")

            # Group by type
            by_type: Dict[str, List[CircuitMeta]] = {}
            for meta in filtered_meta.values():
                if meta.circuit_type not in by_type:
                    by_type[meta.circuit_type] = []
                by_type[meta.circuit_type].append(meta)

            for ctype, circuits_of_type in sorted(by_type.items()):
                print(f"[{ctype.upper()}] ({len(circuits_of_type)} circuits)")
                print("-" * 40)
                for meta in sorted(circuits_of_type, key=lambda x: x.circuit_id):
                    desc = meta.description[:50] + "..." if len(meta.description) > 50 else meta.description
                    print(f"  {meta.circuit_id:<30} {desc}")
                print()

        return 0

    def cmd_info(self, args: List[str]) -> int:
        """
        Show detailed circuit information.

        Usage:
            steward circuit info <circuit_id>
            steward circuit info heal_codebase --json
        """
        if not args:
            print("Error: circuit_id required")
            print("Usage: steward circuit info <circuit_id>")
            return 1

        circuit_id = args[0]
        as_json = "--json" in args

        circuits, metadata = self._ensure_circuits()

        if circuit_id not in metadata:
            print(f"Error: Circuit '{circuit_id}' not found")
            print(f"Available circuits: {list(metadata.keys())[:10]}...")
            return 1

        meta = metadata[circuit_id]
        definition = circuits[circuit_id]

        if as_json:
            output = {
                "circuit_id": meta.circuit_id,
                "type": meta.circuit_type,
                "description": meta.description,
                "version": meta.version,
                "file": str(meta.file_path),
                "triggers": meta.triggers,
                "definition": definition,
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            print(f"\n{'=' * 60}")
            print(f"CIRCUIT: {meta.circuit_id}")
            print(f"{'=' * 60}")
            print(f"Type:        {meta.circuit_type}")
            print(f"Version:     {meta.version}")
            print(f"Description: {meta.description}")
            print(f"File:        {meta.file_path}")
            print()

            # Show states if state_machine
            if "states" in definition:
                print("STATES:")
                print("-" * 40)
                for state_id, state_def in definition.get("states", {}).items():
                    desc = state_def.get("description", "")[:40]
                    print(f"  {state_id:<25} {desc}")
                print()

            # Show triggers
            if meta.triggers:
                print("TRIGGERS:")
                print("-" * 40)
                for trigger in meta.triggers:
                    print(f"  - {trigger}")
                print()

        return 0

    def cmd_run(self, args: List[str]) -> int:
        """
        Execute a circuit.

        Usage:
            steward circuit run <circuit_id>
            steward circuit run heal_codebase --input "fix all"
            steward circuit run auto_heal --headless
        """
        if not args:
            print("Error: circuit_id required")
            print("Usage: steward circuit run <circuit_id> [--input=...]")
            return 1

        circuit_id = args[0]
        user_input = None
        headless = "--headless" in args
        as_json = "--json" in args

        # Parse --input
        for i, arg in enumerate(args):
            if arg.startswith("--input="):
                user_input = arg.split("=", 1)[1]
            elif arg == "--input" and i + 1 < len(args):
                user_input = args[i + 1]

        circuits, metadata = self._ensure_circuits()

        if circuit_id not in circuits:
            print(f"Error: Circuit '{circuit_id}' not found")
            return 1

        # Get circuit definition
        circuit_def = circuits[circuit_id]

        try:
            # Import executor
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor
            from vibe_core.service_registry import ServiceRegistry

            # OPUS-307: Circuits require kernel for syscall execution
            kernel = ServiceRegistry.get("kernel")
            if kernel is None:
                print("❌ Circuit execution requires kernel. Use 'steward run' with full boot.")
                return

            executor = create_circuit_executor(kernel=kernel)

            # Execute
            print(f"Executing circuit: {circuit_id}...")
            result = executor.execute(user_input=user_input or "")

            if as_json:
                print(
                    json.dumps(
                        {
                            "circuit_id": circuit_id,
                            "success": result.success,
                            "final_state": result.final_state,
                            "output": result.output,
                            "error": result.error if hasattr(result, "error") else None,
                        },
                        indent=2,
                        default=str,
                    )
                )
            else:
                if result.success:
                    print("\n✅ Circuit completed successfully")
                    print(f"Final state: {result.final_state}")
                    if result.output:
                        print(f"Output: {result.output}")
                else:
                    print("\n❌ Circuit failed")
                    if hasattr(result, "error") and result.error:
                        print(f"Error: {result.error}")

            return 0 if result.success else 1

        except Exception as e:
            logger.error(f"Circuit execution failed: {e}", exc_info=True)
            print(f"Error executing circuit: {e}")
            return 1

    def cmd_status(self, args: List[str]) -> int:
        """
        Check execution status.

        Usage:
            steward circuit status <execution_id>

        Note: For MVP, this checks filesystem state.
        Future: Query kernel for active executions.
        """
        if not args:
            print("Error: execution_id required")
            print("Usage: steward circuit status <execution_id>")
            return 1

        execution_id = args[0]

        # MVP: Check state directory
        state_dir = Path("state/circuit_executions")
        state_file = state_dir / f"{execution_id}.json"

        if state_file.exists():
            with open(state_file) as f:
                status = json.load(f)
            print(json.dumps(status, indent=2))
            return 0
        else:
            print(f"No execution found with ID: {execution_id}")
            print("Note: Only persisted executions are tracked.")
            return 1
