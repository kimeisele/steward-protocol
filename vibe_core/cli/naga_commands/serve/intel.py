"""
INTEL COMMAND - SHUKA's Vision
==============================

MAHAJANA: SHUKA (The Visionary)
OPCODE: FETCH_RES (Position 8)
PHASE: SERVE

WHY SHUKA?
- Shuka can see past, present, and future
- He narrated Bhagavatam with perfect vision
- Intelligence is about SEEING clearly

MANTRA WORD: HARE (Position 8)
"Hare dispels illusion and reveals truth"

Note: While PARASHURAMA is the Avatara at position 8,
SHUKA semantically owns intelligence operations.

Usage:
    naga intel                    # Get recent intel
    naga intel --critical         # Get critical items only
    naga intel --threats          # Get active threats
    naga intel --category security # Filter by category
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x264c89eb"  # GenesisByte: parampara % 37 == 0

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(opcode=MantraOpCode.EXEC_OP, name="intel", help_text="Query NAGA intelligence (SHUKA's vision)")
class IntelCommand(NagaCommandBase):
    """
    Intel command implementation.

    Bridges NAGA collective intelligence to CLI.
    Accesses observations from all NAGAs.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute intel query.

        Args:
            args: Flags for filtering intel

        Returns:
            NagaCommandResult with intel items or error
        """
        # Parse flags
        critical_only = "--critical" in args
        threats_only = "--threats" in args
        category = None

        if "--category" in args:
            try:
                idx = args.index("--category")
                category = args[idx + 1]
            except (IndexError, ValueError):
                return self.failure("Invalid --category flag. Usage: --category <type>", exit_code=1)

        try:
            # Get intel bridge
            intel = self._get_intel(critical_only=critical_only, threats_only=threats_only, category=category)

            if not intel:
                return self.success("[SHUKA] No intelligence available.", data=(("count", "0")))

            return self.success(
                intel,
                data=(
                    ("critical_only", str(critical_only)),
                    ("threats_only", str(threats_only)),
                    ("category", category or "all"),
                    ("mahajana", "shuka"),
                ),
            )
        except Exception as e:
            return self.failure(f"Intel service unavailable: {e}", exit_code=2)

    def _get_intel(self, critical_only: bool = False, threats_only: bool = False, category: str = None) -> str:
        """
        Fetch intelligence from Chitragupta (REAL DATA, NOT PLACEHOLDER).

        WIRED to ServiceRegistry - gets actual profiling data and anomalies.
        This is the system "hearing" its own health through NAGA observation.
        """
        from vibe_core.di import ServiceRegistry

        lines = []
        lines.append("[SHUKA] Intelligence Report (via Chitragupta)")
        lines.append("=" * 55)

        try:
            # Try to get Chitragupta from registry
            from vibe_core.protocols.naga import ChitraguptaProtocol

            chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if chitragupta is None:
                lines.append("")
                lines.append("⚠️  Chitragupta not active (no profiling data)")
                lines.append("   Run with kernel boot to enable NAGA observation")
                return "\n".join(lines)

            # Get status
            status = chitragupta.get_status()
            lines.append("")
            lines.append(f"📊 NAGA Status: {'✅ HEALTHY' if status.healthy else '❌ UNHEALTHY'}")
            lines.append(f"   Profiles:  {status.details.get('profiles', 0)}")
            lines.append(f"   Anomalies: {status.details.get('anomalies_detected', 0)}")

            # Get timing summary (extended method - may not exist on all implementations)
            timing = {}
            if hasattr(chitragupta, 'get_timing_summary'):
                timing = chitragupta.get_timing_summary()
            if timing:
                lines.append("")
                lines.append("⏱️  TIMING PROFILES:")
                for component, metrics in list(timing.items())[:10]:  # Limit display
                    for metric, stats in metrics.items():
                        mean = stats.get('mean', 0)
                        stddev = stats.get('stddev', 0)
                        samples = stats.get('samples', 0)
                        status_icon = "🔴" if mean > 100 else "🟡" if mean > 50 else "🟢"
                        lines.append(f"   {status_icon} {component}.{metric}: {mean:.1f}ms ±{stddev:.1f} ({samples} samples)")

            # Get anomalies (extended method)
            anomalies = []
            if hasattr(chitragupta, 'get_all_anomalies'):
                anomalies = chitragupta.get_all_anomalies()
            if anomalies:
                lines.append("")
                lines.append("🚨 ANOMALIES DETECTED:")
                for anomaly in anomalies[:5]:  # Top 5
                    lines.append(f"   ⚠️  {anomaly.component_id}.{anomaly.metric}")
                    lines.append(f"       Current: {anomaly.current_value:.2f}")
                    if anomaly.expected_range:
                        lines.append(f"       Expected: {anomaly.expected_range[0]:.2f} - {anomaly.expected_range[1]:.2f}")
            elif not critical_only:
                lines.append("")
                lines.append("✅ No anomalies detected")

            # Karma log (recent actions)
            if not critical_only and category != "performance":
                karma = chitragupta.get_karma_log()
                if karma:
                    lines.append("")
                    lines.append("📜 RECENT KARMA (last 5):")
                    for entry in karma[-5:]:
                        lines.append(f"   • {entry.action}: {entry.component_id}")

        except Exception as e:
            lines.append("")
            lines.append(f"❌ Intel fetch failed: {e}")
            lines.append("   Chitragupta may not be initialized")

        lines.append("")
        lines.append("=" * 55)
        return "\n".join(lines)


# Export for direct import
__all__ = ["IntelCommand"]
