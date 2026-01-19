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

from vibe_core.mahamantra.substrate.seed import NavaBhakti


class ChantResult(TypedDict):
    """Typed result for cli_chant command (KIRTANAM - Chanting)."""
    success: bool
    bhakti: str  # NavaBhakti.KIRTANAM
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
        bhakti=NavaBhakti.KIRTANAM.value,
        rounds=rounds,
        ticks=total_ticks,
        final_position=results[-1]["position"] if results else 0,
        final_guardian=results[-1]["guardian"] if results else "unknown",
        cycle_count=reactor._cycle_count,
        switch_count=reactor._switch_count,
        parampara_connected=reactor.is_parampara_connected,
    )


# =============================================================================
# LISTEN - Event Visibility (Shravanam before Kirtanam)
# =============================================================================

# EventEntry comes from the Priester (event_bridge) - no file I/O here
from vibe_core.mahamantra.cli.event_bridge import EventEntry, get_events


class ListenResult(TypedDict):
    """Typed result for cli_listen command (SRAVANAM - Hearing)."""
    success: bool
    bhakti: str  # NavaBhakti.SRAVANAM
    source: str
    total_entries: int
    filtered_entries: int
    entries: List[EventEntry]


def cli_listen(
    source: str = "all",
    tail: int = 10,
    severity: str = "",
    json: bool = False,
) -> ListenResult:
    """
    CLI Entry Point for Listen command.

    SHRAVANAM (Hearing) - The first process of devotional service.
    Before you chant, you must hear.

    The Temple receives clean offerings from the Priest (event_bridge).
    No file I/O here - that's the Priest's work.

    Args:
        source: Event source (violations, syscalls, all)
        tail: Number of entries to show (default: 10)
        severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
        json: Output as JSON

    Returns:
        ListenResult with event entries.
    """
    # The Priest fetches the offerings (event_bridge handles all I/O)
    entries, total_entries = get_events(
        source=source,
        limit=tail,
        severity_filter=severity if severity else None,
    )

    # === PRESENTATION ONLY (The Temple's work) ===
    if not json:
        print("=" * 70)
        display_source = source if source else "all"
        print(f"MAHAMANTRA LISTEN - Shravanam (source={display_source}, tail={tail})")
        print("=" * 70)

        if not entries:
            print("No entries found.")
        else:
            for entry in entries:
                src = entry.get("source", "?")[:4]
                ts = entry.get("timestamp", "")[:19]
                sev = entry.get("severity", "")
                msg = entry.get("message", "")[:50]

                if sev:
                    sev_symbol = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
                    print(f"[{src}] {ts} {sev_symbol} {sev:8s} | {msg}")
                else:
                    syscall = entry.get("syscall_type", "")
                    result = entry.get("result", "")
                    result_symbol = "✓" if result == "SUCCESS" else "✗"
                    print(f"[{src}] {ts} {result_symbol} {syscall:20s} | {msg}")

        print("-" * 70)
        print(f"Total: {total_entries} | Shown: {len(entries)}")
        print("=" * 70)

    return ListenResult(
        success=True,
        bhakti=NavaBhakti.SRAVANAM.value,
        source=source,
        total_entries=total_entries,
        filtered_entries=len(entries),
        entries=entries,
    )


# =============================================================================
# RESOLVE - Mahajana Lookup (Vandanam - Praying/Requesting)
# =============================================================================


class ResolveResult(TypedDict):
    """Typed result for cli_resolve command (VANDANAM - Praying)."""
    success: bool
    bhakti: str  # NavaBhakti.VANDANAM
    name: str
    position: int
    aliases: tuple  # Tuple[str, ...]
    description: str
    quarter: str


def cli_resolve(
    name: str,
    json: bool = False,
) -> ResolveResult:
    """
    CLI Entry Point for Resolve command.

    VANDANAM (Praying) - Humbly requesting knowledge.
    "Who is this Mahajana? What is their position?"

    Args:
        name: Mahajana name, alias, or position (0-15)
        json: Output as JSON

    Returns:
        ResolveResult with mahajana details.
    """
    # SSOT imports from seed.py
    from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, get_quarter_name
    # Core logic from scanner.py (Separation of Concerns)
    from vibe_core.mahamantra.substrate.scanner import resolve_mahajana

    try:
        alias = resolve_mahajana(name)
        quarter = get_quarter_name(alias.position)

        result = ResolveResult(
            success=True,
            bhakti=NavaBhakti.VANDANAM.value,
            name=alias.name,
            position=alias.position,
            aliases=alias.aliases,
            description=alias.description,
            quarter=quarter,
        )

        if not json:
            print("=" * 60)
            print(f"MAHAMANTRA RESOLVE - Vandanam (query={name})")
            print("=" * 60)
            print(f"  Name:        {alias.name}")
            print(f"  Position:    {alias.position}")
            print(f"  Quarter:     {quarter.upper()}")
            print(f"  Description: {alias.description}")
            print(f"  Aliases:     {', '.join(alias.aliases)}")
            print("-" * 60)
            # Parampara context (circular: pos 0 wraps to pos 15)
            prev_pos = (alias.position - 1) % 16
            next_pos = (alias.position + 1) % 16
            print(f"  Parampara:   ...{ALL_GUARDIANS[prev_pos]} -> [{alias.name}] -> {ALL_GUARDIANS[next_pos]}...")
            print("=" * 60)

        return result

    except ValueError as e:
        result = ResolveResult(
            success=False,
            bhakti=NavaBhakti.VANDANAM.value,
            name=name,
            position=-1,
            aliases=(),
            description=str(e),
            quarter="unknown",
        )

        if not json:
            print("=" * 60)
            print(f"MAHAMANTRA RESOLVE - Vandanam (query={name})")
            print("=" * 60)
            print(f"  ERROR: {e}")
            print("-" * 60)
            print("  Valid inputs:")
            print("    - Sanskrit name: brahma, narada, vyasa, ...")
            print("    - English alias: creator, messenger, boot, ...")
            print("    - Position: 0-15")
            print("=" * 60)

        return result


# =============================================================================
# SERVE - Task Execution (Pada Sevanam - Serving the Feet)
# =============================================================================


class ServeResult(TypedDict):
    """Typed result for cli_serve command (PADA_SEVANAM - Execution)."""
    success: bool
    bhakti: str  # NavaBhakti.PADA_SEVANAM
    task_id: str
    task_name: str
    status: str  # "queued", "executed", "failed"
    execution_time_ms: int
    message: str


def cli_serve(
    task: str,
    execute: bool = False,
    priority: str = "",
    json: bool = False,
) -> ServeResult:
    """
    CLI Entry Point for Serve command.

    PADA_SEVANAM (Serving the Feet) - Execution of duty.
    "Janaka acts without attachment. The work is the offering."

    Submits tasks to JanakaService for execution.
    The task enters the queue and can be executed immediately.

    Args:
        task: Task description to execute
        execute: If True, execute immediately (default: queue only)
        priority: Task priority (critical, high, normal, low)
        json: Output as JSON

    Returns:
        ServeResult with task status.
    """
    from datetime import datetime

    from vibe_core.services.janaka_service import JanakaService
    from vibe_core.protocols.mahajanas.janaka import TaskPriority

    # Map priority string to enum (default to normal if empty)
    priority = priority or "normal"
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "normal": TaskPriority.NORMAL,
        "low": TaskPriority.LOW,
    }
    task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)

    # Get JanakaService (The Executor)
    janaka = JanakaService()

    start_time = datetime.now()

    # Submit the task
    task_id = janaka.submit(
        name=task[:50],  # Truncate long names
        task_input=task,
        priority=task_priority,
        sovereign_id="cli_serve",
    )

    status = "queued"
    message = f"Task queued with priority {priority}"
    exec_time_ms = 0

    # Execute if requested
    if execute:
        exec_result = janaka.execute(task_id)
        exec_time_ms = exec_result.get("execution_time_ms", 0)

        if exec_result.get("success"):
            status = "executed"
            message = exec_result.get("output_repr", "Task executed")
        else:
            status = "failed"
            message = exec_result.get("error_message", "Execution failed")

    end_time = datetime.now()
    total_time_ms = int((end_time - start_time).total_seconds() * 1000)

    result = ServeResult(
        success=status != "failed",
        bhakti=NavaBhakti.PADA_SEVANAM.value,
        task_id=task_id,
        task_name=task[:50],
        status=status,
        execution_time_ms=exec_time_ms or total_time_ms,
        message=message,
    )

    # === PRESENTATION ===
    if not json:
        print("=" * 60)
        print(f"MAHAMANTRA SERVE - Pada Sevanam")
        print("=" * 60)
        print(f"  Task:     {task[:50]}{'...' if len(task) > 50 else ''}")
        print(f"  ID:       {task_id}")
        print(f"  Priority: {priority.upper()}")
        print(f"  Status:   {status.upper()}")
        print(f"  Time:     {result['execution_time_ms']}ms")
        print("-" * 60)
        print(f"  {message}")
        print("=" * 60)

    return result


__all__ = [
    "cli_chant", "ChantResult",
    "cli_listen", "ListenResult", "EventEntry",
    "cli_resolve", "ResolveResult",
    "cli_serve", "ServeResult",
]
