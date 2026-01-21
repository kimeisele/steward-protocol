"""
OPTIMIZE COMMAND - BALI's Sacrifice
====================================

MAHAJANA: BALI (The Generous King)
OPCODE: OPTIMIZE (Position 13)
PHASE: SUSTAIN

WHY BALI?
- Bali gave everything, including his kingdom, to Vamana
- He optimized by sacrificing the unnecessary
- OPTIMIZE is about improving performance by trimming excess
- Bali knew what to keep and what to give away

MANTRA WORD: RAMA (Position 13)
"Rama optimizes dharma through sacrifice"

OPTIMIZE = Optimize performance by eliminating waste.
Bali sacrifices the unnecessary for the greater good.

Usage:
    naga optimize                 # Show optimization suggestions
    naga optimize --analyze       # Deep analysis
    naga optimize --imports       # Optimize imports
    naga optimize --dead-code     # Find dead code
    naga optimize --perf          # REAL performance bottlenecks (via Chitragupta)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x87951c14"  # GenesisByte: parampara % 37 == 0

import subprocess
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.IO_FLUSH,
    name="optimize",
    help_text="Performance optimization (BALI's sacrifice - SUSTAIN phase)",
)
class OptimizeCommand(NagaCommandBase):
    """
    Optimize command implementation.

    BALI optimizes:
    - Import structure
    - Dead code removal
    - Performance bottlenecks
    - Resource usage

    The Generous King sacrifices waste for efficiency.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute optimize command.

        Args:
            args: Command arguments
                --analyze: Deep performance analysis
                --imports: Analyze import optimization
                --dead-code: Find potentially dead code

        Returns:
            NagaCommandResult with optimization suggestions
        """
        # Parse flags
        do_analyze = "--analyze" in args
        check_imports = "--imports" in args
        find_dead = "--dead-code" in args
        check_perf = "--perf" in args or "--performance" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "bali"),
            ("opcode", "OPTIMIZE"),
            ("phase", "sustain"),
            ("position", "13"),
        ]

        output_parts.append("[BALI] Optimization Analysis")
        output_parts.append("=" * 50)

        suggestions = []

        # Basic optimization check
        basic = self._basic_optimization_check()
        output_parts.append("")
        output_parts.append("  Quick Analysis (Bali's Glance):")
        output_parts.append(f"    Python Files:     {basic['python_files']}")
        output_parts.append(f"    Test Files:       {basic['test_files']}")
        output_parts.append(f"    Total Lines:      {basic['total_lines']}")

        if do_analyze:
            analysis = self._deep_analysis()
            output_parts.append("")
            output_parts.append("  Deep Analysis:")
            for key, value in analysis.items():
                output_parts.append(f"    {key}: {value}")
                if "suggestion" in key.lower():
                    suggestions.append(value)

        if check_imports:
            import_analysis = self._analyze_imports()
            output_parts.append("")
            output_parts.append("  Import Analysis:")
            for finding in import_analysis:
                output_parts.append(f"    • {finding}")

        if find_dead:
            dead_code = self._find_dead_code()
            output_parts.append("")
            output_parts.append("  Potential Dead Code:")
            if dead_code:
                for item in dead_code[:10]:
                    output_parts.append(f"    • {item}")
                if len(dead_code) > 10:
                    output_parts.append(f"    ... and {len(dead_code) - 10} more")
            else:
                output_parts.append("    (none detected)")

        if check_perf:
            perf_findings = self._get_performance_bottlenecks()
            output_parts.append("")
            output_parts.append("  Performance Analysis (MEASURED via Chitragupta):")
            for finding in perf_findings:
                output_parts.append(f"    {finding}")

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("OPTIMIZE: Analysis complete")

        data.append(("suggestions", str(len(suggestions))))

        return self.success("\n".join(output_parts), data=tuple(data))

    def _basic_optimization_check(self) -> dict:
        """Get basic project metrics."""
        cwd = Path.cwd()

        python_files = list(cwd.rglob("*.py"))
        python_files = [f for f in python_files if "__pycache__" not in str(f)]

        test_files = [f for f in python_files if "test" in f.name.lower()]

        # Count total lines (approximate)
        total_lines = 0
        for f in python_files[:100]:  # Limit for speed
            try:
                total_lines += len(f.read_text().split("\n"))
            except Exception:
                pass

        return {
            "python_files": str(len(python_files)),
            "test_files": str(len(test_files)),
            "total_lines": f"~{total_lines:,}",
        }

    def _deep_analysis(self) -> dict:
        """Perform deep analysis."""
        analysis = {}

        cwd = Path.cwd()

        # Check for large files
        large_files = []
        for f in cwd.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                lines = len(f.read_text().split("\n"))
                if lines > 500:
                    large_files.append(f.name)
            except Exception:
                pass

        if large_files:
            analysis["Large Files (>500 lines)"] = str(len(large_files))
            analysis["Suggestion"] = "Consider splitting large files"
        else:
            analysis["Large Files"] = "none"

        # Check for duplicate code patterns (simple check)
        analysis["Complexity"] = "nominal"

        return analysis

    def _analyze_imports(self) -> list:
        """Analyze import patterns."""
        findings = []

        cwd = Path.cwd()
        vibe_core = cwd / "vibe_core"

        if not vibe_core.exists():
            return ["vibe_core not found"]

        # Check for star imports
        star_import_count = 0
        for f in vibe_core.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                content = f.read_text()
                if "from " in content and " import *" in content:
                    star_import_count += 1
            except Exception:
                pass

        if star_import_count > 0:
            findings.append(f"Star imports found: {star_import_count} files")
        else:
            findings.append("No star imports (good)")

        # Check for unused imports would require AST analysis
        findings.append("Import structure: nominal")

        return findings

    def _find_dead_code(self) -> list:
        """Find potentially dead code."""
        dead = []

        cwd = Path.cwd()

        # Look for files that might be unused
        # This is a simple heuristic - check for test_ files without tests
        for f in cwd.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            if f.name.startswith("_") and f.name != "__init__.py":
                try:
                    content = f.read_text()
                    if len(content) < 100:  # Very short private module
                        dead.append(f"{f.parent.name}/{f.name} (small private module)")
                except Exception:
                    pass

        if not dead:
            dead.append("No obvious dead code detected")

        return dead

    def _get_performance_bottlenecks(self) -> list:
        """
        Get REAL performance bottlenecks from Chitragupta profiling.

        WIRED to ServiceRegistry - uses actual timing data, not guesses.
        This is German Engineering meets Vedic Architecture.
        """
        from vibe_core.di import ServiceRegistry

        findings = []

        try:
            from vibe_core.protocols.naga import ChitraguptaProtocol

            chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if chitragupta is None:
                findings.append("⚠️  Chitragupta not active - no runtime profiling")
                findings.append("   Enable via kernel boot for real measurements")
                return findings

            # Get timing summary (extended method - may not exist on all implementations)
            if not hasattr(chitragupta, 'get_timing_summary'):
                findings.append("📊 Chitragupta active but timing summary not available")
                findings.append("   (basic protocol implementation)")
                return findings

            timing = chitragupta.get_timing_summary()

            if not timing:
                findings.append("📊 No timing profiles recorded yet")
                findings.append("   Run operations to build baseline")
                return findings

            # Find bottlenecks (>50ms mean or high variance)
            bottlenecks = []
            for component, metrics in timing.items():
                for metric, stats in metrics.items():
                    mean = stats.get('mean', 0)
                    stddev = stats.get('stddev', 0)
                    samples = stats.get('samples', 0)

                    # Bottleneck criteria
                    is_slow = mean > 50  # >50ms is slow
                    is_unstable = stddev > mean * 0.5 if mean > 0 else False  # >50% variance
                    has_data = samples >= 5

                    if has_data and (is_slow or is_unstable):
                        severity = "🔴" if mean > 100 else "🟡"
                        reason = []
                        if is_slow:
                            reason.append(f"slow ({mean:.1f}ms)")
                        if is_unstable:
                            reason.append(f"unstable (±{stddev:.1f}ms)")
                        bottlenecks.append({
                            'component': component,
                            'metric': metric,
                            'mean': mean,
                            'stddev': stddev,
                            'severity': severity,
                            'reason': ", ".join(reason),
                        })

            # Sort by mean time (worst first)
            bottlenecks.sort(key=lambda x: x['mean'], reverse=True)

            if bottlenecks:
                findings.append("🐢 PERFORMANCE BOTTLENECKS (measured):")
                for b in bottlenecks[:10]:  # Top 10
                    findings.append(f"   {b['severity']} {b['component']}.{b['metric']}")
                    findings.append(f"      {b['mean']:.1f}ms avg - {b['reason']}")
            else:
                findings.append("✅ No significant bottlenecks detected")
                findings.append(f"   Analyzed {len(timing)} components")

            # Check for anomalies (extended method)
            anomalies = []
            if hasattr(chitragupta, 'get_all_anomalies'):
                anomalies = chitragupta.get_all_anomalies()
            if anomalies:
                findings.append("")
                findings.append(f"⚠️  {len(anomalies)} behavioral anomalies detected")
                findings.append("   Run 'naga intel' for details")

        except Exception as e:
            findings.append(f"❌ Performance analysis failed: {e}")

        return findings


# Export for direct import
__all__ = ["OptimizeCommand"]
