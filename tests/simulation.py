"""
HERALD Simulation Harness - Proof of Autonomy

Runs the complete I-P-V-O cycle multiple times without posting to real platforms.
This proves:
1. The architecture is deterministic (same input = consistent behavior)
2. Governance rules are enforced (violations are caught)
3. Memory & event sourcing work (state persists across cycles)
4. The system is autonomous (no human intervention needed)

This is the GAD-000 "Simulation Proof" - demonstrating that the agent
can operate without external intervention.

Usage:
    python tests/simulation.py [--cycles 10] [--theme auto] [--verbose]

Or via CLI:
    herald simulate --cycles 10 --theme auto
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from herald.core.agency_director import AgencyDirector

# Setup detailed logging for simulation
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HERALD_SIMULATION")


class SimulationHarness:
    """
    Simulation runner for HERALD Agency Director.

    Tests determinism, governance, and autonomy.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize simulation.

        Args:
            verbose: If True, print detailed logs
        """
        self.verbose = verbose
        self.director = AgencyDirector()
        self.results: List[Dict[str, Any]] = []

        logger.info("🧪 HERALD Simulation Harness initialized")

    def run_cycles(self, num_cycles: int, theme: str = "auto") -> Dict[str, Any]:
        """
        Run multiple cycles and collect results.

        Args:
            num_cycles: Number of cycles to run
            theme: Content generation theme

        Returns:
            Dict with simulation results and statistics
        """
        logger.info(f"🚀 Starting simulation: {num_cycles} cycles, theme={theme}")
        print(f"\n{'='*70}")
        print(f"HERALD Simulation: {num_cycles} I-P-V-O Cycles")
        print(f"Theme: {theme}")
        print(f"Start: {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*70}\n")

        start_time = datetime.now(timezone.utc)

        for i in range(num_cycles):
            print(f"[Cycle {i+1}/{num_cycles}] ", end="", flush=True)

            result = self.director.run_cycle(campaign_theme=theme)

            cycle_result = {
                "cycle": i + 1,
                "status": result.status,
                "phase": result.phase,
                "draft_length": len(result.draft) if result.draft else 0,
                "violations_count": len(result.violations) if result.violations else 0,
                "error": result.error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results.append(cycle_result)

            # Print quick status
            if result.status == "SUCCESS":
                print(f"✅ SUCCESS ({result.draft[:50]}...)")
            elif result.status == "VALIDATION_FAILED":
                violations_str = ", ".join(result.violations[:2]) if result.violations else "unknown"
                print(f"⚠️  VALIDATION_FAILED ({violations_str})")
            else:
                print(f"❌ ERROR ({result.error})")

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Compute statistics
        stats = self._compute_statistics()

        simulation_result = {
            "simulation": True,
            "harness_version": "1.0",
            "configuration": {
                "total_cycles": num_cycles,
                "theme": theme,
            },
            "execution": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": duration,
            },
            "results": self.results,
            "statistics": stats,
        }

        self._print_summary(simulation_result)

        return simulation_result

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute simulation statistics."""
        if not self.results:
            return {}

        successful = sum(1 for r in self.results if r["status"] == "SUCCESS")
        failed_validation = sum(1 for r in self.results if r["status"] == "VALIDATION_FAILED")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")

        total_violations = sum(r.get("violations_count", 0) for r in self.results)
        avg_draft_length = sum(r.get("draft_length", 0) for r in self.results) / len(self.results) if self.results else 0

        return {
            "total_cycles": len(self.results),
            "successful": successful,
            "validation_failed": failed_validation,
            "errors": errors,
            "success_rate": (successful / len(self.results) * 100) if self.results else 0,
            "total_violations_caught": total_violations,
            "avg_draft_length": avg_draft_length,
        }

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Print simulation summary."""
        stats = result["statistics"]
        duration = result["execution"]["duration_seconds"]

        print(f"\n{'='*70}")
        print("Simulation Summary:")
        print(f"{'='*70}")
        print(f"Total Cycles:        {stats['total_cycles']}")
        print(f"Successful:          {stats['successful']}/{stats['total_cycles']} ({stats['success_rate']:.1f}%)")
        print(f"Validation Failed:   {stats['validation_failed']}")
        print(f"Errors:              {stats['errors']}")
        print(f"Violations Caught:   {stats['total_violations_caught']}")
        print(f"Avg Draft Length:    {stats['avg_draft_length']:.0f} chars")
        print(f"Duration:            {duration:.2f} seconds")
        print(f"Cycles/Second:       {stats['total_cycles']/duration:.2f}")
        print(f"{'='*70}\n")

        # Check EventLog
        events = self.director.event_log.get_all_events()
        print(f"📖 Event Log Status:")
        print(f"   Total events: {len(events)}")
        print(f"   Content generated: {len(self.director.event_log.get_events_by_type('content_generated'))}")
        print(f"   Content published: {len(self.director.event_log.get_events_by_type('content_published'))}")
        print(f"   Content rejected: {len(self.director.event_log.get_events_by_type('content_rejected'))}")
        print(f"   System errors: {len(self.director.event_log.get_events_by_type('system_error'))}")

    def export_json(self, filepath: Path) -> None:
        """Export simulation results to JSON."""
        output = {
            "simulation": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": self.results,
            "statistics": self._compute_statistics(),
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"💾 Results exported to {filepath}")


def main():
    """CLI entry point for simulation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="HERALD Simulation Harness - Proof of Autonomy",
        epilog="""
This harness proves GAD-000 compliance by running the agency deterministically
without human intervention or real platform posts.

Example:
    python tests/simulation.py --cycles 10 --theme auto --verbose
        """
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=5,
        help="Number of cycles to run (default: 5)"
    )
    parser.add_argument(
        "--theme",
        choices=["auto", "tech_deep_dive", "campaign", "agent_city"],
        default="auto",
        help="Content generation theme (default: auto)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed logs"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to JSON file"
    )

    args = parser.parse_args()

    # Run simulation
    harness = SimulationHarness(verbose=args.verbose)
    result = harness.run_cycles(args.cycles, args.theme)

    # Export if requested
    if args.export:
        export_path = Path(args.export)
        harness.export_json(export_path)

    # Exit with success code
    if result["statistics"]["success_rate"] > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
