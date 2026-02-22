"""
CLI GATES - Pancha Tattva Entry Points
======================================

"śrī-kṛṣṇa-caitanya prabhu-nityānanda
 śrī-advaita gadādhara śrīvāsādi-gaura-bhakta-vṛnda"

THE PANCHA TATTVA CARRY THE MAHAMANTRA:
They ARE the Mahamantra (acintya). In Kali Yuga, they descended
to distribute the Holy Name. The 5 Gates honor them.

5 GATES = PANCHA TATTVA:
1. GATE         (Chaitanya)  - Main entry, Krishna Himself
2. ROUTE_GATE   (Nityananda) - Routing, the original Guru
3. EXECUTE_GATE (Advaita)    - Execution, called Krishna down
4. RESULT_GATE  (Gadadhara)  - Result, the pleasure potency
5. SYNC_GATE    (Srivasa)    - Sync, in his courtyard they chanted together

THE MANTRA IS THE STRUCTURE:
- 16 positions = 16 words of Mahamantra
- 4 quarters = GENESIS, DHARMA, KARMA, MOKSHA
- 108 methods = 108 beads per mala
- 37 parampara = connection verification

USAGE:
    from vibe_core.cli.gates import gate, sync_gate

    result = gate("analyze", ["system"])  # Single command
    results = sync_gate(["analyze system", "judge action"])  # Parallel

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xa30db002"  # GenesisByte: parampara % 37 == 0

import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Final, List, Optional, Tuple, Union

from vibe_core.protocols.substrate.mantra.acintya import PARAMPARA

# =============================================================================
# MANTRA SUBSTRATE IMPORTS (The Source)
# =============================================================================
from vibe_core.protocols.substrate.mantra.lotus import (
    LOTUS_POSITIONS,
    LotusQuarter,
    grow_lotus,
)

# =============================================================================
# GATE CONSTANTS (From Mantra)
# =============================================================================

# The 16 positions map to opcodes (from _source.py truth table)
GATE_OPCODES: Final[Dict[int, str]] = {
    0: "wake",  # Prithu - GENESIS HEAD
    1: "create",  # Brahma
    2: "broadcast",  # Narada
    3: "destroy",  # Shambhu
    4: "assert",  # Vyasa - DHARMA HEAD
    5: "purify",  # Kumaras
    6: "analyze",  # Kapila
    7: "sync",  # Manu
    8: "fetch",  # Parashurama - KARMA HEAD
    9: "execute",  # Prahlada
    10: "check",  # Janaka
    11: "commit",  # Bhishma
    12: "cache",  # Nrisimha - MOKSHA HEAD
    13: "surrender",  # Bali
    14: "view",  # Shuka
    15: "judge",  # Yamaraja
}

# Reverse lookup: opcode → position
OPCODE_TO_POSITION: Final[Dict[str, int]] = {v: k for k, v in GATE_OPCODES.items()}

# Quarter boundaries
QUARTER_GATES: Final[Dict[LotusQuarter, Tuple[int, int, int, int]]] = {
    LotusQuarter.GENESIS: (0, 1, 2, 3),
    LotusQuarter.DHARMA: (4, 5, 6, 7),
    LotusQuarter.KARMA: (8, 9, 10, 11),
    LotusQuarter.MOKSHA: (12, 13, 14, 15),
}


# =============================================================================
# GATE RESULT (Structured Output)
# =============================================================================


@dataclass
class GateResult:
    """
    Result from passing through a Gate.

    WATERTIGHT - no Any types.
    """

    success: bool
    exit_code: int
    position: int
    quarter: str
    opcode: str
    output: Dict[str, Union[str, int, float, bool]]
    error: Optional[str] = None

    @classmethod
    def ok(cls, position: int, output: Dict[str, Union[str, int, float, bool]]) -> "GateResult":
        """Create success result."""
        quarter = list(LotusQuarter)[position // 4]
        return cls(
            success=True,
            exit_code=0,
            position=position,
            quarter=quarter.value,
            opcode=GATE_OPCODES.get(position, "unknown"),
            output=output,
        )

    @classmethod
    def fail(cls, position: int, error: str, code: int = 1) -> "GateResult":
        """Create failure result."""
        quarter = list(LotusQuarter)[position // 4]
        return cls(
            success=False,
            exit_code=code,
            position=position,
            quarter=quarter.value,
            opcode=GATE_OPCODES.get(position, "unknown"),
            output={},
            error=error,
        )


# =============================================================================
# GATE 1: GATE (Chaitanya) - Main Entry
# =============================================================================

_initialized: bool = False


def _init_gate(base_path: Optional[Path] = None) -> bool:
    """
    Internal initialization.

    Grows the Lotus (discovers all protocols).
    Called automatically when needed.
    """
    global _initialized

    if _initialized:
        return True

    if base_path is None:
        base_path = Path(__file__).parent.parent.parent

    try:
        state = grow_lotus(base_path)
        _initialized = state.get("total_nodes", 0) > 0
        return _initialized
    except Exception:
        return False


# =============================================================================
# GATE 2: ROUTE GATE (Nityananda) - Routing
# =============================================================================


def route_gate(command: str) -> Tuple[int, str]:
    """
    ROUTE GATE (Nityananda) - The Original Guru routes to Krishna.

    "nitāi-pada-kamala, koṭī-candra-suśītala"
    The lotus feet of Nityananda are cooling like millions of moons.

    Routes command to mahamantra position.

    Routing priority:
    1. Exact opcode match (analyze → 6)
    2. Keyword in command (analyze_system → 6)
    3. Parampara hash (deterministic fallback)

    Returns (position, matched_opcode).
    """
    cmd_lower = command.lower()

    # 1. Exact match
    if cmd_lower in OPCODE_TO_POSITION:
        pos = OPCODE_TO_POSITION[cmd_lower]
        return pos, cmd_lower

    # 2. Keyword match (command contains opcode)
    for opcode, pos in OPCODE_TO_POSITION.items():
        if opcode in cmd_lower or cmd_lower.startswith(opcode):
            return pos, opcode

    # 3. Parampara hash (deterministic fallback)
    # Same formula as _cli_auto.py
    mutation_vector = sum(ord(c) * (i + 1) for i, c in enumerate(cmd_lower))
    position = (mutation_vector % PARAMPARA) % LOTUS_POSITIONS

    return position, GATE_OPCODES.get(position, "unknown")


# =============================================================================
# GATE 3: EXECUTE GATE (Run Protocol Method)
# =============================================================================


def execute_gate(
    position: int,
    method_name: str,
    args: List[str],
) -> GateResult:
    """
    EXECUTE GATE (Advaita) - Called Krishna Down.

    "advaita-ācārya mahāśaya, kṛṣṇera āveśa-maya"
    Advaita Acarya is absorbed in Krishna consciousness.

    He called for Krishna's descent through His intense devotion.
    This gate calls the protocol method into execution.

    The position IS the truth - from byte.py/mantra structure.
    No hashing needed - direct routing via mahamantra.
    """
    # Get protocol module directly from mahajana path (THE SOURCE OF TRUTH)
    try:
        import importlib

        from vibe_core.mahamantra import ALL_GUARDIANS

        # Get guardian name from position and load module
        guardian_name = ALL_GUARDIANS[position]
        module = importlib.import_module(f"vibe_core.protocols.mahajanas.{guardian_name}")

        # Find Null class
        null_class_name = f"Null{guardian_name.capitalize()}"
        null_class = getattr(module, null_class_name, None)

        if null_class is None:
            # Try alternate naming
            for name in dir(module):
                if name.startswith("Null"):
                    null_class = getattr(module, name)
                    break

        if null_class is None:
            return GateResult.fail(
                position=position,
                error=f"No Null implementation for {guardian_name}",
                code=1,
            )

        # Instantiate and call method
        instance = null_class()

        # Try {method}_cli first (CLI-friendly wrapper takes priority)
        cli_method_name = f"{method_name}_cli"
        method = getattr(instance, cli_method_name, None)

        if method is None:
            # Try exact method name
            method = getattr(instance, method_name, None)

        if method is None:
            # Try opcode as method name
            opcode = GATE_OPCODES.get(position)
            method = getattr(instance, opcode, None) if opcode else None

        if method is None:
            return GateResult.fail(
                position=position,
                error=f"Method {method_name} not found",
                code=1,
            )

        # Build call args from CLI args (inspect method signature)
        try:
            sig = inspect.signature(method)
            params = [p for p in sig.parameters.keys() if p != "self"]
        except (ValueError, TypeError):
            params = []

        # Map positional args to parameter names (CLI args are always strings)
        call_kwargs: Dict[str, str] = {}
        positional_args: List[str] = []

        for i, arg in enumerate(args):
            if "=" in arg:
                key, val = arg.split("=", 1)
                call_kwargs[key] = val
            elif i < len(params):
                # Map to parameter name
                call_kwargs[params[i]] = arg
            else:
                positional_args.append(arg)

        # Execute with mapped args
        try:
            result = method(*positional_args, **call_kwargs)
        except TypeError:
            # Fallback: try without args
            result = method()

        # Convert result to output dict
        if isinstance(result, dict):
            output = {k: v for k, v in result.items() if isinstance(v, (str, int, float, bool))}
        elif result is None:
            output = {"status": "complete"}
        else:
            output = {"result": str(result)}

        return GateResult.ok(position=position, output=output)

    except Exception as e:
        return GateResult.fail(
            position=position,
            error=str(e),
            code=1,
        )


# =============================================================================
# GATE 4: RESULT GATE (Format Output)
# =============================================================================


def format_result(result: GateResult) -> str:
    """Format GateResult as string (no printing)."""
    if result.success:
        return "\n".join(f"{k}: {v}" for k, v in result.output.items())
    return f"ERROR [{result.opcode}@{result.position}]: {result.error}"


def result_gate(result: GateResult, silent: bool = False) -> int:
    """
    RESULT GATE (Gadadhara) - The Pleasure Potency.

    "gadādhara paṇḍita-gosāñi, rādhā-bhāva-pūrṇa"
    Gadadhara Pandita is full of Radha's mood of devotion.

    He embodies the fruit of devotion - pure bliss.
    This gate delivers the result, the fruit of execution.

    Args:
        result: The GateResult to output
        silent: If True, don't print (just return exit code)

    Returns:
        Exit code (0 = success)
    """
    if not silent:
        print(format_result(result))
    return result.exit_code


# =============================================================================
# GATE (Chaitanya) - The Main Entry
# =============================================================================


def gate(command: str, args: Optional[List[str]] = None) -> GateResult:
    """
    GATE (Chaitanya) - Krishna Himself.

    "śrī-kṛṣṇa-caitanya-deva, sarva-guru, sarva-prabhu"
    Sri Krishna Chaitanya is the Guru of all, the Lord of all.

    The main entry point. All other gates flow through here.
    Chaitanya IS Krishna in the mood of Radha - the complete whole.

    Usage:
        result = gate("analyze", ["system"])
        exit_code = result_gate(result)

    Flow:
        command → ROUTE_GATE (Nityananda) → position
        position + args → EXECUTE_GATE (Advaita) → result
    """
    args = args or []

    # Initialize if needed
    if not _initialized:
        _init_gate()

    # Route via Nityananda
    position, opcode = route_gate(command)

    # Determine method name
    method_name = command.lower() if command.lower() in OPCODE_TO_POSITION else opcode

    # Execute via Advaita
    return execute_gate(position, method_name, args)


# =============================================================================
# GATE 5: SYNC GATE (Srivasa) - Parallel Execution
# =============================================================================


def _parse_command(cmd_string: str) -> Tuple[str, List[str]]:
    """Parse command string into (command, args)."""
    parts = cmd_string.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:] if len(parts) > 1 else []


def _execute_single(cmd_string: str) -> Tuple[str, GateResult]:
    """Execute single command, return (cmd_string, result) for ordering."""
    command, args = _parse_command(cmd_string)
    if not command:
        return cmd_string, GateResult.fail(0, "Empty command", 1)
    return cmd_string, gate(command, args)


def sync_gate(
    commands: List[str],
    max_workers: int = 4,
    preserve_order: bool = True,
) -> List[GateResult]:
    """
    SYNC GATE (Srivasa) - In His Courtyard They Chanted Together.

    "śrīvāsādi gaura-bhakta-vṛnda"
    Srivasa and the devotees of Lord Gauranga.

    In Srivasa's courtyard, the Pancha Tattva and devotees
    would chant the Mahamantra together in ecstasy.

    This gate executes multiple commands IN PARALLEL,
    like the congregation chanting in unison.

    Args:
        commands: List of command strings ("analyze system", "judge action")
        max_workers: Maximum parallel threads (default 4)
        preserve_order: If True, results match input order

    Returns:
        List of GateResults (ordered if preserve_order=True)

    Usage:
        results = sync_gate(["analyze system", "judge action", "fetch data"])
    """
    if not _initialized:
        _init_gate()

    if not commands:
        return []

    # Execute in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_execute_single, cmd): cmd for cmd in commands}

        if preserve_order:
            # Collect results maintaining input order
            results_map: Dict[str, GateResult] = {}
            for future in as_completed(futures):
                cmd_string, result = future.result()
                results_map[cmd_string] = result
            return [results_map.get(cmd, GateResult.fail(0, "Missing", 1)) for cmd in commands]
        else:
            # Return results as they complete
            return [future.result()[1] for future in as_completed(futures)]


# Alias for backward compatibility
cli_gate = gate


# =============================================================================
# CONVENIENCE: Direct CLI Entry
# =============================================================================


def gate_main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for gate-based CLI.

    Usage:
        python -m vibe_core.cli.gates analyze system
    """
    import sys

    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("STEWARD GATES - Pancha Tattva CLI")
        print("=" * 50)
        print()
        print("śrī-kṛṣṇa-caitanya prabhu-nityānanda")
        print("śrī-advaita gadādhara śrīvāsādi-gaura-bhakta-vṛnda")
        print()
        print("USAGE: steward <command> [args]")
        print()
        print("THE 16 POSITIONS (Mahamantra Words):")
        for pos, opcode in GATE_OPCODES.items():
            quarter = list(LotusQuarter)[pos // 4].value.upper()
            head = "HEAD" if pos % 4 == 0 else "    "
            print(f"  [{pos:2d}] {opcode:12s} {head} {quarter}")
        return 0

    command = argv[0]
    args = argv[1:]

    result = gate(command, args)
    return result_gate(result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "GATE_OPCODES",
    "OPCODE_TO_POSITION",
    "QUARTER_GATES",
    # Result
    "GateResult",
    "format_result",
    # THE 5 GATES (Pancha Tattva)
    "gate",  # 1. Chaitanya - Main entry
    "route_gate",  # 2. Nityananda - Routing
    "execute_gate",  # 3. Advaita - Execution
    "result_gate",  # 4. Gadadhara - Result
    "sync_gate",  # 5. Srivasa - Parallel
    # Aliases
    "cli_gate",  # Alias for gate
    "gate_main",
]
