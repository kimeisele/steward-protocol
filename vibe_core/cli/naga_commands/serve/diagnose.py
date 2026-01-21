"""
HEAR COMMAND - NAGA DIAGNOSTICS (System Self-Diagnostics)
==================================================

MAHAJANA: NARADA (The Divine Messenger)
OPCODE: OBSERVE (Position 1)
PHASE: SERVE

WHY NARADA?
- Narada travels between worlds, bringing news
- He is the original guru - first to teach through diagnoseing (diagnostics)
- "evam parampara-praptam" - knowledge received through disciplic succession

NAGA DIAGNOSTICS (Diagnoseing):
In Vedic tradition, diagnostics is the FIRST step of bhakti-yoga.
Before one can act, one must HEAR - receive knowledge from authority.

The system "diagnoses" from its NAGAs:
- Chitragupta reports karma (timing, anomalies)
- Narada reports observations
- The kernel reports dharma breaches

This is INTROSPECTIVE - the system listening to itself.
Different from `intel` which is external intelligence.

Usage:
    naga diagnose                     # Full diagnostic report
    naga diagnose --brief             # Quick health check
    naga diagnose --anomalies         # Only show anomalies
    naga diagnose --bottlenecks       # Only show slow operations
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 1
__genesis__ = "0x7a3b8c01"  # GenesisByte: parampara % 37 == 0

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(opcode=MantraOpCode.AUDIT_SEAL, name="diagnose", help_text="System self-diagnostics (NAGA DIAGNOSTICS - diagnoseing from NAGAs)")
class DiagnoseCommand(NagaCommandBase):
    """
    Diagnose command implementation - NAGA DIAGNOSTICS.

    The system listens to its own health through parampara:
    Chitragupta → Narada → CLI → User

    This is the first step of system awareness:
    "One cannot act properly without first diagnoseing properly."
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute diagnose command - system self-diagnostics.

        Args:
            args: Flags for filtering output
                --brief: Quick health summary
                --anomalies: Show only anomalies
                --bottlenecks: Show only slow operations

        Returns:
            NagaCommandResult with diagnostic report
        """
        # Parse flags
        brief_mode = "--brief" in args
        anomalies_only = "--anomalies" in args
        bottlenecks_only = "--bottlenecks" in args

        try:
            report = self._generate_diagnostic_report(
                brief=brief_mode,
                anomalies_only=anomalies_only,
                bottlenecks_only=bottlenecks_only,
            )

            return self.success(
                report,
                data=(
                    ("mahajana", "narada"),
                    ("command", "diagnose"),
                    ("mode", "brief" if brief_mode else "full"),
                ),
            )
        except Exception as e:
            return self.failure(f"Diagnostic failed: {e}", exit_code=1)

    def _generate_diagnostic_report(
        self,
        brief: bool = False,
        anomalies_only: bool = False,
        bottlenecks_only: bool = False,
    ) -> str:
        """
        Generate diagnostic report by listening to NAGAs.

        NAGA DIAGNOSTICS - The system diagnoses from:
        1. Chitragupta (karma records - timing, anomalies)
        2. ServiceRegistry (dharma breaches)
        3. Kernel state (health indicators)
        """
        from vibe_core.di import ServiceRegistry

        lines = []
        lines.append("🙏 NAGA DIAGNOSTICS - System Self-Diagnostics")
        lines.append("=" * 55)
        lines.append("   'evam parampara-praptam' - received through parampara")
        lines.append("")

        # === CHITRAGUPTA REPORT (Karma Records) ===
        chitragupta_report = self._diagnose_from_chitragupta(
            anomalies_only=anomalies_only,
            bottlenecks_only=bottlenecks_only,
        )

        if not brief or anomalies_only or bottlenecks_only:
            lines.extend(chitragupta_report)

        # === DHARMA BREACH CHECK ===
        if not anomalies_only and not bottlenecks_only:
            dharma_report = self._check_dharma_breaches()
            lines.extend(dharma_report)

        # === HEALTH SUMMARY ===
        if brief:
            summary = self._generate_health_summary()
            lines.extend(summary)

        # === RECOMMENDATIONS ===
        if not brief:
            recommendations = self._generate_recommendations(chitragupta_report)
            if recommendations:
                lines.append("")
                lines.append("📋 RECOMMENDATIONS:")
                for rec in recommendations:
                    lines.append(f"   • {rec}")

        lines.append("")
        lines.append("=" * 55)
        lines.append("🙏 NAGA DIAGNOSTICS complete - now you have diagnosed")

        return "\n".join(lines)

    def _diagnose_from_chitragupta(
        self,
        anomalies_only: bool = False,
        bottlenecks_only: bool = False,
    ) -> List[str]:
        """Diagnose karma records from Chitragupta."""
        from vibe_core.di import ServiceRegistry

        lines = []

        try:
            from vibe_core.protocols.naga import ChitraguptaProtocol

            chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if chitragupta is None:
                lines.append("📿 CHITRAGUPTA (Karma Records):")
                lines.append("   ⚠️  Not active - no karma being recorded")
                lines.append("   💡 Enable via kernel boot for full observation")
                lines.append("")
                return lines

            # Get status
            status = chitragupta.get_status()
            profile_count = status.details.get('profiles', 0)
            anomaly_count = status.details.get('anomalies_detected', 0)

            if not bottlenecks_only:
                lines.append("📿 CHITRAGUPTA (Karma Records):")
                lines.append(f"   Status: {'✅ ACTIVE' if status.healthy else '❌ UNHEALTHY'}")
                lines.append(f"   Profiles: {profile_count} components being watched")
                lines.append(f"   Anomalies: {anomaly_count} detected")
                lines.append("")

            # Get anomalies
            if not bottlenecks_only:
                anomalies = []
                if hasattr(chitragupta, 'get_all_anomalies'):
                    anomalies = chitragupta.get_all_anomalies()

                if anomalies:
                    lines.append("   🚨 BEHAVIORAL ANOMALIES:")
                    for a in anomalies[:5]:
                        lines.append(f"      ⚠️  {a.component_id}.{a.metric}")
                        lines.append(f"         Value: {a.current_value:.2f} (>2σ deviation)")
                        if a.expected_range:
                            lines.append(f"         Normal: {a.expected_range[0]:.2f} - {a.expected_range[1]:.2f}")
                    if len(anomalies) > 5:
                        lines.append(f"      ... and {len(anomalies) - 5} more")
                    lines.append("")
                elif not anomalies_only:
                    lines.append("   ✅ No behavioral anomalies")
                    lines.append("")

            # Get timing bottlenecks
            if not anomalies_only:
                timing = {}
                if hasattr(chitragupta, 'get_timing_summary'):
                    timing = chitragupta.get_timing_summary()

                bottlenecks = []
                for component, metrics in timing.items():
                    for metric, stats in metrics.items():
                        mean = stats.get('mean', 0)
                        stddev = stats.get('stddev', 0)
                        samples = stats.get('samples', 0)
                        if samples >= 5 and (mean > 50 or (stddev > mean * 0.5 and mean > 0)):
                            bottlenecks.append({
                                'component': component,
                                'metric': metric,
                                'mean': mean,
                                'stddev': stddev,
                            })

                bottlenecks.sort(key=lambda x: x['mean'], reverse=True)

                if bottlenecks:
                    lines.append("   🐢 TIMING BOTTLENECKS:")
                    for b in bottlenecks[:5]:
                        icon = "🔴" if b['mean'] > 100 else "🟡"
                        lines.append(f"      {icon} {b['component']}.{b['metric']}")
                        lines.append(f"         {b['mean']:.1f}ms avg (±{b['stddev']:.1f}ms)")
                    if len(bottlenecks) > 5:
                        lines.append(f"      ... and {len(bottlenecks) - 5} more")
                    lines.append("")
                elif not bottlenecks_only:
                    lines.append("   ✅ No timing bottlenecks (>50ms)")
                    lines.append("")

        except Exception as e:
            lines.append("📿 CHITRAGUPTA (Karma Records):")
            lines.append(f"   ❌ Error: {e}")
            lines.append("")

        return lines

    def _check_dharma_breaches(self) -> List[str]:
        """Check for dharma breaches (unblessed services)."""
        lines = []
        lines.append("⚖️  DHARMA (Service Registry):")

        try:
            from vibe_core.di import ServiceRegistry

            # Check if blessing is enabled
            blessing_enabled = getattr(ServiceRegistry, '_naga_blessing_enabled', False)

            if blessing_enabled:
                lines.append("   ✅ Naga blessing ENABLED")
                lines.append("   All services wrapped with NagaProxy")
            else:
                lines.append("   ⚠️  Naga blessing DISABLED")
                lines.append("   Services not being observed!")
                lines.append("   💡 Call ServiceRegistry.enable_naga_blessing()")

            lines.append("")

        except Exception as e:
            lines.append(f"   ❌ Error: {e}")
            lines.append("")

        return lines

    def _generate_health_summary(self) -> List[str]:
        """Generate brief health summary."""
        lines = []
        lines.append("📊 HEALTH SUMMARY:")

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import ChitraguptaProtocol

            chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if chitragupta:
                status = chitragupta.get_status()
                anomaly_count = status.details.get('anomalies_detected', 0)

                if anomaly_count == 0:
                    lines.append("   🟢 HEALTHY - No anomalies detected")
                elif anomaly_count < 3:
                    lines.append(f"   🟡 ATTENTION - {anomaly_count} anomalies detected")
                else:
                    lines.append(f"   🔴 WARNING - {anomaly_count} anomalies detected")
            else:
                lines.append("   ⚪ UNKNOWN - Chitragupta not active")

            lines.append("")

        except Exception:
            lines.append("   ⚪ UNKNOWN - Could not determine health")
            lines.append("")

        return lines

    def _generate_recommendations(self, chitragupta_report: List[str]) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        report_text = "\n".join(chitragupta_report)

        if "Not active" in report_text:
            recommendations.append("Enable kernel boot to activate NAGA observation")

        if "ANOMALIES" in report_text:
            recommendations.append("Investigate anomalous components with 'naga intel'")

        if "BOTTLENECKS" in report_text:
            recommendations.append("Profile slow operations with 'naga optimize --perf'")

        if "DISABLED" in report_text:
            recommendations.append("Enable naga blessing for full observation coverage")

        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")

        return recommendations


# Export for direct import
__all__ = ["DiagnoseCommand"]
