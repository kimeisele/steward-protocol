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

    ŚRAVAṆAM CHECK:
    - Before chanting (kīrtanam), system must be phase-locked
    - Uses SravanamCheck.validate_epoch_lock() for boot validation

    Args:
        rounds: Number of complete cycles (default: 1)
        verbose: If True, print each tick

    Returns:
        ChantResult with cycle results (machine-readable).
    """
    # Lazy imports to keep module load fast
    from vibe_core.mahamantra import mahamantra
    from vibe_core.mahamantra.substrate.seed import WORDS
    from vibe_core.mahamantra.substrate.harmonics import SravanamCheck
    from vibe_core.mahamantra.chamber import SankirtanChamber
    from vibe_core.mahamantra.cell import MahaCellUnified
    from vibe_core.mahamantra.orchestrator import THE_FLUTE_CYCLE

    # EPOCH LOCK CHECK (Boot validation - 1972 signature)
    if not SravanamCheck.validate_epoch_lock():
        return ChantResult(
            success=False,
            bhakti=NavaBhakti.KIRTANAM.value,
            rounds=0,
            ticks=0,
            final_position=-1,
            final_guardian="BLOCKED",
            cycle_count=0,
            switch_count=0,
            parampara_connected=False,
        )

    results: List[Dict[str, object]] = []
    total_ticks = rounds * WORDS  # 1 round = 16 positions

    # Spawn SANKIRTAN CHAMBER (The New Engine)
    chamber = SankirtanChamber.create()
    
    # Create the Seed Cell (The Mantra itself)
    # A single cell chanting through the cycles
    seed_cell = MahaCellUnified.create(
        source=0,  # Genesis
        target=1,  # Evolution
        operation=0, # Chant
        initial_state="Hare Krishna"
    )

    if verbose:
        print("=" * 60)
        print("MAHAMANTRA CHANT - Sankirtan Chamber Active")
        print("=" * 60)
        print(f"Rounds: {rounds} | Ticks: {total_ticks}")
        print("-" * 60)

    for tick_num in range(total_ticks):
        # Get tick state from Singularity clock (still valid for timing)
        tick_state = mahamantra.tick()

        # Step 1: Dance (Transform Cell & Update Registry)
        chamber.dance(seed_cell)
        
        # Step 2: Metrics
        # Map Orchestrator state to legacy Shadow state for compatibility
        # Name encoding: (diw >> 16) & 0x3 -> 0=H, 1=K, 2=R
        current_diw = THE_FLUTE_CYCLE[chamber.tick % WORDS]
        name_idx = (current_diw >> 16) & 0x3
        guardian_name = ["HARE", "KRISHNA", "RAMA", "?"][name_idx]
        
        state = {
            "position": chamber.tick % WORDS,
            "guardian": guardian_name,
            "phase": "kirtan", # Active chanting
            "opcode": "TRANSFORM",
            "resonance": chamber.resonance_count,
            "transformations": chamber.total_transformations,
            "active_cells": len(chamber.active_cells),
        }

        if verbose:
            print(
                f"[{tick_num:02d}] ~ {guardian_name:12s} | "
                f"KIRTAN   | pos={state['position']:2d} | "
                f"res={state['resonance']} | cells={state['active_cells']}"
            )

        results.append(state)

    if verbose:
        print("-" * 60)
        print(f"Completed {rounds} round(s)")
        print(f"  Resonance: {chamber.resonance_count} | Transformations: {chamber.total_transformations}")
        print(f"  Active Cells (Registry): {len(chamber.active_cells)}")
        print("=" * 60)
    else:
        # Always show minimal summary
        final_pos = results[-1]["position"] if results else 0
        final_guard = results[-1]["guardian"] if results else "unknown"
        print(f"CHANT: {rounds}r × {total_ticks}t → [{final_guard}@{final_pos}] Res={chamber.resonance_count} Cells={len(chamber.active_cells)}")

    return ChantResult(
        success=True,
        bhakti=NavaBhakti.KIRTANAM.value,
        rounds=rounds,
        ticks=total_ticks,
        final_position=results[-1]["position"] if results else 0,
        final_guardian=results[-1]["guardian"] if results else "unknown",
        cycle_count=chamber.resonance_count, # Mapped from resonance
        switch_count=chamber.total_transformations, # Mapped from transformations
        parampara_connected=len(chamber.active_cells) > 0, # Presence implies connection
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
    from vibe_core.mahamantra.karma.janaka import TaskPriority

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


# =============================================================================
# VEDA - Veda-Explorer Interface (ATMA_NIVEDANAM - Complete Self-Surrender)
# =============================================================================


class VedaCLIResult(TypedDict):
    """Typed result for cli_veda command (ATMA_NIVEDANAM - Self-Surrender)."""

    success: bool
    bhakti: str  # NavaBhakti.ATMA_NIVEDANAM
    mode: str  # "restricted", "enhanced", "creative"
    intent: str
    response: str
    llm_used: bool


def cli_veda(
    message: str = "",
    mode: str = "enhanced",
    interactive: bool = False,
    json: bool = False,
) -> VedaCLIResult:
    """
    CLI Entry Point for Veda command.

    ATMA_NIVEDANAM (Self-Surrender) - Complete dedication.
    "Whatever you do, offer it to Me." (BG 9.27)

    The Veda-Explorer chat interface - neuro-symbolic processing.
    Deterministic first, LLM fallback.

    Args:
        message: Message to process (ignored if interactive)
        mode: Explorer mode (restricted, enhanced, creative)
        interactive: Run in interactive REPL mode
        json: Output as JSON

    Returns:
        VedaCLIResult with processed response.
    """
    from vibe_core.mahamantra.cli.veda_explorer import (
        ExplorerMode,
        VedaExplorer,
    )

    # Map mode string to enum
    mode_map = {
        "restricted": ExplorerMode.RESTRICTED,
        "enhanced": ExplorerMode.ENHANCED,
        "creative": ExplorerMode.CREATIVE,
    }
    explorer_mode = mode_map.get(mode.lower(), ExplorerMode.ENHANCED)

    # Create explorer
    explorer = VedaExplorer(mode=explorer_mode)

    # Interactive mode
    if interactive:
        explorer.repl()
        return VedaCLIResult(
            success=True,
            bhakti=NavaBhakti.ATMA_NIVEDANAM.value,
            mode=explorer_mode.value,
            intent="repl",
            response="REPL session ended.",
            llm_used=False,
        )

    # Single message mode
    if not message:
        result = VedaCLIResult(
            success=False,
            bhakti=NavaBhakti.ATMA_NIVEDANAM.value,
            mode=explorer_mode.value,
            intent="empty",
            response="No message provided. Use --interactive for REPL mode.",
            llm_used=False,
        )
        if not json:
            print("=" * 60)
            print("VEDA EXPLORER - Atma Nivedanam")
            print("=" * 60)
            print("  ERROR: No message provided.")
            print("  Use --interactive for REPL mode.")
            print("  Or: steward chat 'your message here'")
            print("=" * 60)
        return result

    # Process message
    # ŚRAVAṆAM CHECK: Must hear before speaking
    from vibe_core.mahamantra.substrate.harmonics import SravanamCheck
    import time

    # Get current tick (based on system time modulo JIVA_CYCLE)
    current_tick = int(time.time() * 1000) % 432  # ms modulo JIVA_CYCLE

    # Estimate tokens (rough: 1 token ≈ 4 chars)
    input_tokens = len(message) // 4 + 1
    # Estimate output will be 2x input (conservative for 2:1 ratio)
    estimated_output = input_tokens * 2

    # Default resonance (will be updated by actual processing)
    resonance = 0.5  # REFINE zone - safe default

    # Dynamic emission check
    can_emit, reason, delay = SravanamCheck.can_emit_dynamic(
        input_tokens=input_tokens,
        output_tokens=estimated_output,
        resonance=resonance,
        tick=current_tick,
        strict=False,  # Not strict for chat
    )

    if not can_emit and delay > 0:
        # Wait for next Gajra if delay is small
        if delay <= SravanamCheck.MAX_EGO_OFFSET:
            time.sleep(delay * 0.001)  # Convert to seconds (rough)
            current_tick = (current_tick + delay) % 432

    # CREATIVE MODE: Use NAGA-flooded chat (Layer -1 integration)
    if explorer_mode == ExplorerMode.CREATIVE:
        try:
            from vibe_core.mahamantra.chat import flooded_routed_chat, get_guardian_for_message

            # Route to appropriate guardian with NAGA flooding
            guardian = get_guardian_for_message(message)
            response = flooded_routed_chat(message)

            veda_result = {
                "success": True,
                "intent": "creative",
                "response": f"[NAGA x {guardian.upper()}] {response}",
                "llm_used": True,
                "naga_flooded": True,
            }
        except Exception as e:
            # Fall back to regular explorer on error
            veda_result = explorer.process(message)
            veda_result["naga_error"] = str(e)
    else:
        veda_result = explorer.process(message)

    result = VedaCLIResult(
        success=veda_result.get("success", False),
        bhakti=NavaBhakti.ATMA_NIVEDANAM.value,
        mode=explorer_mode.value,
        intent=veda_result.get("intent", "unknown"),
        response=veda_result.get("response", ""),
        llm_used=veda_result.get("llm_used", False),
    )

    # === PRESENTATION ===
    if not json:
        naga_status = "FLOODED" if veda_result.get("naga_flooded") else "Standard"
        ego_offset = SravanamCheck.calculate_ego_offset(current_tick)
        on_gajra = SravanamCheck.is_on_gajra(current_tick)
        phase_dist, nearest_sync = SravanamCheck.calculate_phase_angle(current_tick)

        print("=" * 60)
        print("VEDA EXPLORER - Atma Nivedanam")
        print("=" * 60)
        print(f"  Mode: {explorer_mode.value.upper()} ({naga_status})")
        print(f"  LLM:  {'Available' if explorer.llm_available else 'Not available'}")
        print(f"  Phase: tick={current_tick} ego={ego_offset} {'GAJRA' if on_gajra else ''} sync→{nearest_sync}")
        print("-" * 60)
        print(f"  Input: {message}")
        print(f"  Intent: {result['intent']}")
        print("-" * 60)
        print(result["response"])
        if result["llm_used"]:
            print("  [LLM used]")
        if veda_result.get("naga_flooded"):
            print("  [NAGA: Chitragupta, Takshaka, Narada, Sesha]")
        print("=" * 60)

    return result


__all__ = [
    "cli_chant",
    "ChantResult",
    "cli_listen",
    "ListenResult",
    "EventEntry",
    "cli_resolve",
    "ResolveResult",
    "cli_serve",
    "ServeResult",
    "cli_veda",
    "VedaCLIResult",
]
