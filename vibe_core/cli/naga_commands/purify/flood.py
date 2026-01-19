"""
FLOOD COMMAND - MANU's Law of Observation
==========================================

MAHAJANA: MANU (The Lawgiver)
OPCODE: PULSE_SYNC (Position 8)
PHASE: PURIFY

WHY MANU?
- Manu established the laws that govern society
- He set the rhythm and rules for dharmic life
- PULSE_SYNC is about heartbeat and synchronization
- FloodManager observes and maintains system rhythm

MANTRA WORD: HARE (Position 8)
"Hare maintains the cosmic rhythm"

PULSE_SYNC = The heartbeat of the system.
Manu's law ensures everything runs in sync.
FloodManager floods the system with observations.

Usage:
    naga flood                    # Show flood status
    naga flood --stats            # Detailed statistics
    naga flood --subscribers      # List active subscribers
    naga flood --pulse            # Show current pulse rate
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x5e296ca2"  # GenesisByte: parampara % 37 == 0

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.DHARMA_TEST,
    name="flood",
    help_text="FloodManager status and pulse sync (MANU's law - PURIFY phase)",
)
class FloodCommand(NagaCommandBase):
    """
    Flood command implementation.

    MANU governs:
    - System pulse/heartbeat
    - Observation synchronization
    - FloodManager status
    - Subscriber management

    Manu's law keeps everything in rhythm.
    The flood observes, the pulse syncs.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute flood command.

        Args:
            args: Command arguments
                --stats: Show detailed statistics
                --subscribers: List active subscribers
                --pulse: Show current pulse rate

        Returns:
            NagaCommandResult with flood status
        """
        # Parse flags
        show_stats = "--stats" in args
        show_subscribers = "--subscribers" in args
        show_pulse = "--pulse" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "manu"),
            ("opcode", "PULSE_SYNC"),
            ("phase", "purify"),
            ("position", "8"),
        ]

        output_parts.append("[MANU] FloodManager Status")
        output_parts.append("=" * 50)

        # Try to get real FloodManager status
        flood_status = self._get_flood_status()

        if flood_status["available"]:
            output_parts.append(f"  Active:        {flood_status['active']}")
            output_parts.append(f"  Observations:  {flood_status['observations']}")
            output_parts.append(f"  Subscribers:   {flood_status['subscribers']}")
            data.append(("active", str(flood_status["active"])))
            data.append(("observations", str(flood_status["observations"])))
            data.append(("subscriber_count", str(flood_status["subscribers"])))

            if show_stats:
                output_parts.append("")
                output_parts.append("  Detailed Statistics:")
                output_parts.append(f"    Total Events:    {flood_status.get('total_events', 0)}")
                output_parts.append(f"    Events/min:      {flood_status.get('events_per_min', 0):.2f}")
                output_parts.append(f"    Avg Latency:     {flood_status.get('avg_latency_ms', 0):.1f}ms")

            if show_subscribers:
                output_parts.append("")
                output_parts.append("  Active Subscribers:")
                subscribers = flood_status.get("subscriber_list", [])
                if subscribers:
                    for sub in subscribers[:10]:
                        output_parts.append(f"    • {sub}")
                    if len(subscribers) > 10:
                        output_parts.append(f"    ... and {len(subscribers) - 10} more")
                else:
                    output_parts.append("    (no active subscribers)")

            if show_pulse:
                output_parts.append("")
                output_parts.append("  Pulse Status:")
                output_parts.append(f"    Rate:            {flood_status.get('pulse_rate', 60)} bpm")
                output_parts.append(f"    Last Pulse:      {flood_status.get('last_pulse', 'N/A')}")
                output_parts.append(f"    Sync Status:     {flood_status.get('sync_status', 'UNKNOWN')}")
                data.append(("pulse_rate", str(flood_status.get("pulse_rate", 60))))

        else:
            output_parts.append("")
            output_parts.append("  FloodManager not available.")
            output_parts.append("  Boot the kernel first: steward boot")
            output_parts.append("")
            output_parts.append("  Simulated Status:")
            output_parts.append("    Active:        False")
            output_parts.append("    Observations:  0")
            output_parts.append("    Subscribers:   0")
            data.append(("active", "False"))
            data.append(("observations", "0"))
            data.append(("subscriber_count", "0"))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("PULSE_SYNC: Rhythm maintained")

        return self.success("\n".join(output_parts), data=tuple(data))

    def _get_flood_status(self) -> dict:
        """Get FloodManager status from Federation."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and federation.flood_manager:
                status = federation.flood_manager.get_status()
                return {
                    "available": True,
                    "active": status.get("active", False),
                    "observations": status.get("total_observations", 0),
                    "subscribers": status.get("subscriber_count", 0),
                    "total_events": status.get("total_events", 0),
                    "events_per_min": status.get("events_per_minute", 0.0),
                    "avg_latency_ms": status.get("avg_latency_ms", 0.0),
                    "subscriber_list": status.get("subscribers", []),
                    "pulse_rate": status.get("pulse_rate", 60),
                    "last_pulse": status.get("last_pulse", "N/A"),
                    "sync_status": status.get("sync_status", "SYNCED"),
                }
        except Exception:
            pass

        # Return default/unavailable status
        return {
            "available": False,
            "active": False,
            "observations": 0,
            "subscribers": 0,
        }


# Export for direct import
__all__ = ["FloodCommand"]
