"""
MAHAMANTRA CLI COMMANDS - Shastrically Correct Handlers
========================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

CLI handlers for Mahamantra commands. Each handler:
- Takes typed kwargs from cli.yaml options
- Returns typed Dict with success/error status
- Is stateless (Computation on Demand pattern)

NO KERNEL REQUIRED. These are OFFLINE commands.
The CLI is the ignition button - spawns Shadow Reactor on demand.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"  # GenesisByte: parampara % 37 == 0

from typing import Dict, List, TypedDict


class ChantResult(TypedDict):
    """Typed result for cli_chant command."""
    success: bool
    rounds: int
    ticks: int
    final_position: int
    final_guardian: str
    cycle_count: int
    switch_count: int
    parampara_connected: bool


def cli_chant(
    rounds: int = 1,
    verbose: bool = False,
) -> ChantResult:
    """
    CLI Entry Point for Chant command.

    COMPUTATION ON DEMAND:
    - Spawns Shadow Reactor (no singleton, fresh per invocation)
    - Executes n rounds (1 round = 16 ticks = full Yajna cycle)
    - Returns machine-readable state

    Args:
        rounds: Number of complete cycles (default: 1)
        verbose: If True, print each tick

    Returns:
        ChantResult with cycle results (machine-readable).
    """
    # Lazy imports to keep module load fast
    from vibe_core.mahamantra import mahamantra
    from vibe_core.mahamantra.substrate.seed import WORDS

    results: List[Dict[str, object]] = []
    total_ticks = rounds * WORDS  # 1 round = 16 positions

    # Spawn a Shadow Reactor (SANKIRTAN pattern - no singleton)
    reactor = mahamantra.shadow.spawn(auto_discover=True)

    if verbose:
        print("=" * 60)
        print("MAHAMANTRA CHANT - Computation on Demand")
        print("=" * 60)
        print(f"Rounds: {rounds} | Ticks: {total_ticks}")
        print("-" * 60)

    for tick_num in range(total_ticks):
        # Get tick state from Singularity clock
        tick_state = mahamantra.tick()

        # Process through Shadow Reactor (Yajna cycle)
        shadow_state = reactor.tick(tick_state)

        if verbose:
            phase = shadow_state["phase"]
            phase_symbol = {"bhoga": "+", "prasadam": "~", "return": "<"}
            symbol = phase_symbol.get(phase, " ")
            print(
                f"[{tick_num:02d}] {symbol} {shadow_state['guardian']:12s} | "
                f"{phase:8s} | pos={shadow_state['position']:2d} | "
                f"opcode={shadow_state['opcode']}"
            )

        results.append(dict(shadow_state))

    if verbose:
        print("-" * 60)
        print(f"Completed {rounds} round(s)")
        print(f"  Cycles: {reactor._cycle_count} | Switches: {reactor._switch_count}")
        connected = "YES" if reactor.is_parampara_connected else "NO"
        print(f"  Parampara: {connected}")
        print("=" * 60)

    return ChantResult(
        success=True,
        rounds=rounds,
        ticks=total_ticks,
        final_position=results[-1]["position"] if results else 0,
        final_guardian=results[-1]["guardian"] if results else "unknown",
        cycle_count=reactor._cycle_count,
        switch_count=reactor._switch_count,
        parampara_connected=reactor.is_parampara_connected,
    )


__all__ = ["cli_chant", "ChantResult"]
