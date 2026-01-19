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


class EventEntry(TypedDict, total=False):
    """Single event entry from any source."""
    timestamp: str
    source: str
    severity: str
    message: str
    file_path: str
    rule_id: str
    syscall_type: str
    result: str


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

    Reads from:
    - violations.jsonl (Watchman code violations)
    - syscalls.jsonl (System calls log)

    Args:
        source: Event source (violations, syscalls, all)
        tail: Number of entries to show (default: 10)
        severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
        json: Output as JSON

    Returns:
        ListenResult with event entries.
    """
    import json as json_module
    from pathlib import Path

    # JSONL file locations
    vibe_state = Path(".vibe/state")
    sources_map = {
        "violations": vibe_state / "ouroboros" / "violations.jsonl",
        "syscalls": vibe_state / "plugins" / "opus_assistant" / "syscalls.jsonl",
    }

    entries: List[EventEntry] = []

    # Determine which sources to read
    if source == "all":
        sources_to_read = list(sources_map.keys())
    elif source in sources_map:
        sources_to_read = [source]
    else:
        sources_to_read = list(sources_map.keys())

    # Read from each source
    for src_name in sources_to_read:
        src_path = sources_map[src_name]
        if not src_path.exists():
            continue

        try:
            with open(src_path, "r") as f:
                lines = f.readlines()

            # Parse JSONL
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json_module.loads(line)

                    # Normalize to EventEntry format
                    entry: EventEntry = {
                        "source": src_name,
                        "timestamp": data.get("ingested_at") or data.get("timestamp", ""),
                    }

                    if src_name == "violations":
                        entry["severity"] = data.get("severity", "")
                        entry["message"] = data.get("message", "")
                        entry["file_path"] = data.get("file_path", "")
                        entry["rule_id"] = data.get("rule_id", "")
                    elif src_name == "syscalls":
                        entry["syscall_type"] = data.get("syscall_type", "")
                        entry["result"] = data.get("result", "")
                        entry["message"] = data.get("intent", "")

                    entries.append(entry)
                except json_module.JSONDecodeError:
                    continue
        except Exception:
            continue

    total_entries = len(entries)

    # Filter by severity if specified
    if severity:
        severity_upper = severity.upper()
        entries = [e for e in entries if e.get("severity", "").upper() == severity_upper]

    # Sort by timestamp (newest first) and take tail
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    entries = entries[:tail]

    # Output
    if not json:
        print("=" * 70)
        print(f"MAHAMANTRA LISTEN - Shravanam (source={source}, tail={tail})")
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


__all__ = ["cli_chant", "ChantResult", "cli_listen", "ListenResult", "EventEntry"]
