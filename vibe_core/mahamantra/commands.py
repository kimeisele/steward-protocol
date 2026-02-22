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

import logging
from typing import Dict, List, TypedDict

from vibe_core.mahamantra.substrate.seed import NavaBhakti

logger = logging.getLogger(__name__)


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


# =============================================================================
# CLI_CHANT — Routes through lotus.execute() (the VM)
# =============================================================================
# The VM already does kirtan + yajna + chamber work inside execute_cycle().
# cli_chant(rounds=N) = call lotus.execute("Hare Krishna") N times.
# Audio/network are I/O side effects using the VM's output.
# =============================================================================

def _chant_fail(final_position: int = -1, final_guardian: str = "BLOCKED") -> ChantResult:
    """Return a failed ChantResult."""
    return ChantResult(
        success=False, bhakti=NavaBhakti.KIRTANAM.value, rounds=0, ticks=0,
        final_position=final_position, final_guardian=final_guardian,
        cycle_count=0, switch_count=0, parampara_connected=False,
    )


def cli_chant(
    rounds: int = 1,
    verbose: bool = False,
    audio: bool = False,
    dest: str = "",
) -> ChantResult:
    """
    CLI Entry Point for Chant command.

    Routes ALL computation through lotus.execute() → execute_cycle() (the VM).
    Each round = one lotus.execute("Hare Krishna") call which internally runs
    the full 12-step NavaBhakti pipeline including kirtan + yajna (16 ticks).

    Audio and Vimana streaming are I/O side effects that use the VM's output
    (DIW data, cell state) rather than computing their own.
    """
    import asyncio
    import sys

    from vibe_core.mahamantra.substrate.harmonics import SravanamCheck
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
    from vibe_core.mahamantra.substrate.seed import WORDS

    # Validate epoch lock
    if not SravanamCheck.validate_epoch_lock():
        return _chant_fail()

    # I/O setup (side effects — not computation)
    sound_engine = None
    vimana_client = None
    if audio:
        from vibe_core.mahamantra.sound.audio_engine import PranaSoundEngine
        sound_engine = PranaSoundEngine()
    if dest:
        try:
            from vibe_core.mahamantra.net.vimana import VimanaClient
            host, port = dest.split(":")
            vimana_client = VimanaClient(host, int(port))
        except ValueError:
            print(f"Invalid destination format: {dest}. Use host:port")
            return _chant_fail(final_position=0, final_guardian="")

    lotus = get_mahamantra()
    total_ticks = rounds * WORDS
    round_results: List[Dict[str, object]] = []

    effective_verbose = verbose and not audio
    if effective_verbose:
        print("=" * 60)
        print("MAHAMANTRA CHANT - Through VM Pipeline")
        if dest:
            print(f"Streaming to Vimana: {dest}")
        print("=" * 60)
        print(f"Rounds: {rounds} | Ticks per round: {WORDS} | Total: {total_ticks}")
        print("-" * 60)

    async def _stream_loop():
        """Handle async I/O (vimana) around synchronous VM calls."""
        if vimana_client:
            await vimana_client.connect()

        for round_num in range(rounds):
            # === COMPUTATION: Through the VM ===
            result = lotus.execute("Hare Krishna")
            round_results.append(result)

            # === I/O SIDE EFFECTS: Use VM output ===
            position = result.get("position", 0)
            guardian = result.get("guardian", "unknown")
            diw_data = result.get("diw", {})
            execution = result.get("execution", {})
            kirtan_cycles = execution.get("kirtan_cycles", 1)
            yajna = result.get("yajna", {})

            if effective_verbose:
                print(
                    f"[{round_num:02d}] ~ {str(guardian):12s} | "
                    f"KIRTAN   | pos={position:2d} | "
                    f"cycles={kirtan_cycles} | phase={yajna.get('phase', '?')}"
                )

            # Audio synthesis from VM's DIW output
            if sound_engine and diw_data:
                from vibe_core.mahamantra.protocols.diw import pack
                synth_diw = pack(
                    venu=diw_data.get("venu", 0),
                    vamsi=diw_data.get("vamsi", 0),
                    murali=diw_data.get("murali", 0),
                )
                pcm = sound_engine.synthesize(synth_diw)
                sys.stdout.buffer.write(pcm)

            # Vimana streaming from VM's cell output
            if vimana_client:
                cell = result.get("cell", {})
                await vimana_client.send(cell)

        if vimana_client:
            await vimana_client.close()

    try:
        asyncio.run(_stream_loop())
    except KeyboardInterrupt as _exc:
        logger.exception("Unexpected error: %s", _exc)

    # === BUILD RESULT from VM outputs ===
    last = round_results[-1] if round_results else {}
    last_execution = last.get("execution", {}) if last else {}
    last_yajna = last.get("yajna", {}) if last else {}

    total_cycles = sum(
        r.get("execution", {}).get("kirtan_cycles", 0) for r in round_results
    )
    total_switches = sum(
        r.get("yajna", {}).get("switch_count", 0) for r in round_results
    )

    if effective_verbose:
        print("-" * 60)
        print(f"Completed {rounds} round(s) through VM pipeline")
        print(f"  Total kirtan cycles: {total_cycles}")
        print(f"  Total yajna switches: {total_switches}")
        print("=" * 60)
    elif not audio:
        final_pos = last.get("position", 0)
        final_guard = last.get("guardian", "unknown")
        print(
            f"CHANT: {rounds}r × {WORDS}t → [{final_guard}@{final_pos}] "
            f"Cycles={total_cycles} Switches={total_switches}"
        )

    return ChantResult(
        success=True,
        bhakti=NavaBhakti.KIRTANAM.value,
        rounds=rounds,
        ticks=total_ticks,
        final_position=last.get("position", 0),
        final_guardian=str(last.get("guardian", "unknown")),
        cycle_count=total_cycles,
        switch_count=total_switches,
        parampara_connected=last.get("parampara", {}).get("verified", False),
    )


class VimanaServeResult(TypedDict):
    """Result for Vimana Server."""

    success: bool
    host: str
    port: int


def cli_vimana_serve(
    port: int = 10800,
    host: str = "0.0.0.0",
) -> VimanaServeResult:
    """
    Start Vimana Server.

    Args:
        port: Port to listen on (default 10800)
        host: Host to bind (default 0.0.0.0)
    """
    import asyncio

    from vibe_core.mahamantra.net.vimana import VimanaServer
    from vibe_core.mahamantra.substrate.chamber import SankirtanChamber

    print(f"VIMANA SERVE - Listening on {host}:{port}")
    chamber = SankirtanChamber.create()
    server = VimanaServer(host, port, chamber)

    try:
        asyncio.run(server.serve_forever())
    except KeyboardInterrupt:
        print("\nVimana Server Stopped.")

    return VimanaServeResult(success=True, host=host, port=port)


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

    Routes through lotus.execute() to register the listen intent in the VM,
    then fetches events as an I/O concern.

    Args:
        source: Event source (violations, syscalls, all)
        tail: Number of entries to show (default: 10)
        severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
        json: Output as JSON

    Returns:
        ListenResult with event entries.
    """
    # === COMPUTATION: Route through the VM ===
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
    lotus = get_mahamantra()
    lotus.execute(f"listen {source}")

    # === I/O: Fetch events (event_bridge handles all I/O) ===
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

    Routes through lotus.execute() to register the resolve intent in the VM,
    then performs the lookup as an I/O concern.

    Args:
        name: Mahajana name, alias, or position (0-15)
        json: Output as JSON

    Returns:
        ResolveResult with mahajana details.
    """
    # === COMPUTATION: Route through the VM ===
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
    lotus = get_mahamantra()
    lotus.execute(f"resolve {name}")

    # === I/O: Lookup from SSOT ===
    from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, WORDS, get_quarter_name
    from vibe_core.mahamantra.substrate.wiring import get_position_from_name

    try:
        # Use SSOT (wiring.py) instead of scanner
        pos = get_position_from_name(name)
        if pos is None:
            # Try by index
            try:
                idx = int(name)
                if 0 <= idx < WORDS:
                    pos_name = ALL_GUARDIANS[idx]
                    pos = get_position_from_name(pos_name)
            except ValueError as _exc:
                logger.exception("Unexpected error: %s", _exc)

        if pos is None:
            raise ValueError(f"Unknown mahajana: {name}")

        guardian_name = pos.guardian.value
        quarter = get_quarter_name(pos.index)

        result = ResolveResult(
            success=True,
            bhakti=NavaBhakti.VANDANAM.value,
            name=guardian_name,
            position=pos.index,
            aliases=(),  # SSOT doesn't track aliases
            description=f"Position {pos.index} in {quarter}",
            quarter=quarter,
        )

        if not json:
            print("=" * 60)
            print(f"MAHAMANTRA RESOLVE - Vandanam (query={name})")
            print("=" * 60)
            print(f"  Name:        {guardian_name}")
            print(f"  Position:    {pos.index}")
            print(f"  Quarter:     {quarter.upper()}")
            print(f"  Word:        {pos.word.value}")
            print(f"  Role:        {'HEAD' if pos.is_head else 'WORKER'}")
            print("-" * 60)
            # Parampara context (circular: pos 0 wraps to pos WORDS-1)
            prev_pos = (pos.index - 1) % WORDS  # SSOT
            next_pos = (pos.index + 1) % WORDS  # SSOT
            print(f"  Parampara:   ...{ALL_GUARDIANS[prev_pos]} -> [{guardian_name}] -> {ALL_GUARDIANS[next_pos]}...")
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

    Routes through lotus.execute() first to compute position/guardian routing
    for the task, then submits to JanakaService with VM-computed context.

    Args:
        task: Task description to execute
        execute: If True, execute immediately (default: queue only)
        priority: Task priority (critical, high, normal, low)
        json: Output as JSON

    Returns:
        ServeResult with task status.
    """
    from datetime import datetime

    from vibe_core.mahamantra.karma.janaka import JanakaService, TaskPriority
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

    # === COMPUTATION: Route task through the VM ===
    lotus = get_mahamantra()
    vm_result = lotus.execute(task)

    # VM tells us WHERE this task belongs (position, guardian, opcode)
    vm_position = vm_result.get("position", 10)  # 10 = Janaka's position
    vm_guardian = vm_result.get("guardian", "janaka")
    vm_seed = vm_result.get("vibration", {}).get("seed", 0)

    # Map priority string to enum (default to normal if empty)
    priority = priority or "normal"
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "normal": TaskPriority.NORMAL,
        "low": TaskPriority.LOW,
    }
    task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)

    # Get JanakaService through Mahajana folder (canonical path)
    janaka = JanakaService()

    start_time = datetime.now()

    # Submit the task with VM-computed routing context
    task_id = janaka.submit(
        name=task[:50],  # Truncate long names
        task_input=task,
        priority=task_priority,
        sovereign_id=f"cli_serve[{vm_guardian}@{vm_position}]",
    )

    status = "queued"
    message = f"Task queued with priority {priority} (VM: {vm_guardian}@{vm_position})"
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
        print("MAHAMANTRA SERVE - Pada Sevanam (Through VM Pipeline)")
        print("=" * 60)
        print(f"  Task:     {task[:50]}{'...' if len(task) > 50 else ''}")
        print(f"  ID:       {task_id}")
        print(f"  Priority: {priority.upper()}")
        print(f"  VM Route: {vm_guardian}@{vm_position} (seed={vm_seed})")
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

    Routes through lotus.execute() for deterministic computation (vibration,
    resonant words, verse, guardian). VedaExplorer and LLM use VM output
    as context — they are I/O concerns, not computation.

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

    # Interactive mode (REPL is inherently multi-turn I/O)
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

    # === COMPUTATION: Route message through the VM ===
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

    lotus = get_mahamantra()
    vm_result = lotus.execute(message)

    # VM gives us deterministic context for the message
    vm_guardian = vm_result.get("guardian", "unknown")
    vm_position = vm_result.get("position", 0)
    vm_verse = vm_result.get("verse", {})
    vm_smaranam = vm_result.get("smaranam", ())
    vm_composed = vm_result.get("composed", "")
    vm_parampara = vm_result.get("parampara", {})

    # === I/O: VedaExplorer / LLM use VM output as context ===
    # CREATIVE MODE: Kirtan-Flow (canonical VM pipeline + optional LLM)
    if explorer_mode == ExplorerMode.CREATIVE:
        from vibe_core.mahamantra.render import kirtan_chat

        response = kirtan_chat(message, use_llm=True)

        veda_result = {
            "success": True,
            "intent": "creative",
            "response": response,
            "llm_used": True,
            "kirtan_flow": True,
        }
    else:
        veda_result = explorer.process(message)

    # Enrich with VM computation
    if vm_composed and not veda_result.get("llm_used"):
        # Deterministic path: use VM-composed output
        veda_result["response"] = vm_composed or veda_result.get("response", "")

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

        print("=" * 60)
        print("VEDA EXPLORER - Atma Nivedanam (Through VM Pipeline)")
        print("=" * 60)
        print(f"  Mode:     {explorer_mode.value.upper()} ({naga_status})")
        print(f"  VM Route: {vm_guardian}@{vm_position}")
        if vm_verse:
            print(f"  Verse:    {vm_verse}")
        if vm_smaranam:
            words = ", ".join(s.get("sanskrit", "?") for s in vm_smaranam[:3])
            print(f"  Smaranam: {words}")
        print(f"  LLM:      {'Available' if explorer.llm_available else 'Not available'}")
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
