"""
HERALD CLI - Command Line Interface for the Agency Director.

Implements GAD-000 Operator Inversion: The system can be controlled by
any operator (human, cron job, another AI agent, CI/CD system) via JSON
output and standard exit codes.

Commands:
  status          - Show current agency state (governance-compliant)
  run             - Execute one I-P-V-O cycle
  loop            - Run continuous cycles (daemon mode)
  simulate        - Run dry-run simulation (no real posts)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .core.agency_director import AgencyDirector

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HERALD_CLI")


class HeraldCLI:
    """Command line interface for HERALD Agency Director."""

    def __init__(self):
        """Initialize CLI."""
        self.director = None

    def _init_director(self) -> bool:
        """Initialize the Agency Director. Return True if successful."""
        try:
            self.director = AgencyDirector()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize AgencyDirector: {e}")
            return False

    def cmd_status(self, args) -> int:
        """
        Show current agency state.

        Returns:
            0 if state available, 1 if not
        """
        if not self._init_director():
            return 1

        state = self.director.get_state()

        if state is None:
            output = {
                "status": "no_state",
                "message": "No state file found - agency hasn't run yet",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            output = state

        if args.json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n📊 HERALD Agency Status:")
            print(f"  Cycle ID:    {output.get('cycle_id', 'N/A')}")
            print(f"  Phase:       {output.get('phase', 'IDLE')}")
            print(f"  Status:      {output.get('status', 'UNKNOWN')}")
            print(f"  Timestamp:   {output.get('timestamp', 'N/A')}")

            if "details" in output and output["details"]:
                print(f"  Details:     {json.dumps(output['details'], default=str)}")

        return 0

    def cmd_run(self, args) -> int:
        """
        Execute one complete I-P-V-O cycle.

        Returns:
            0 if SUCCESS, 1 if VALIDATION_FAILED or ERROR
        """
        if not self._init_director():
            return 1

        theme = args.theme or "auto"
        logger.info(f"🚀 Running single cycle (theme: {theme})")

        result = self.director.run_cycle(campaign_theme=theme)

        output = {
            "status": result.status,
            "phase": result.phase,
            "cycle_id": result.cycle_id,
            "draft": result.draft,
            "violations": result.violations,
            "error": result.error,
            "broadcast_result": result.broadcast_result,
        }

        if args.json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print(f"\n✅ Cycle Result: {result.status}")
            print(f"   Phase: {result.phase}")
            if result.draft:
                print(f"   Draft: {result.draft[:80]}...")
            if result.violations:
                print(f"   Violations: {', '.join(result.violations[:2])}")
            if result.error:
                print(f"   Error: {result.error}")

        # Exit code based on result
        if result.status == "SUCCESS":
            return 0
        elif result.status == "VALIDATION_FAILED":
            return 2  # Specific exit code for validation failure
        else:
            return 1

    def cmd_loop(self, args) -> int:
        """
        Run continuous cycles (daemon mode).

        Returns:
            0 if normal exit, 1 if error during initialization
        """
        if not self._init_director():
            return 1

        interval = args.interval or 3600  # Default 1 hour
        max_cycles = args.cycles or None

        logger.info(f"🔄 Starting loop mode (interval: {interval}s, max_cycles: {max_cycles})")

        cycle_count = 0
        try:
            while True:
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"✅ Reached max cycles ({max_cycles}), exiting")
                    break

                cycle_count += 1
                logger.info(f"\n--- Cycle {cycle_count} ---")

                result = self.director.run_retry_loop(
                    campaign_theme=args.theme or "auto",
                    max_retries=3,
                )

                if args.json:
                    print(
                        json.dumps(
                            {
                                "cycle": cycle_count,
                                "status": result.status,
                                "phase": result.phase,
                            },
                            default=str,
                        )
                    )

                if result.status != "SUCCESS":
                    logger.warning(f"⚠️  Cycle {cycle_count} failed: {result.error}")

                if cycle_count < (max_cycles or float("inf")):
                    logger.info(f"💤 Sleeping for {interval}s...")
                    time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n⛔ Loop interrupted by user")
            return 0
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            return 1

        return 0

    def cmd_simulate(self, args) -> int:
        """
        Run simulation (dry-run without real posts).

        Returns:
            0 if simulation succeeds, 1 otherwise
        """
        if not self._init_director():
            return 1

        cycles = args.cycles or 5
        logger.info(f"🧪 Starting simulation ({cycles} cycles, no real posts)")

        results = []
        for i in range(cycles):
            logger.info(f"\n[SIM {i + 1}/{cycles}]")
            result = self.director.run_cycle(campaign_theme=args.theme or "auto")
            results.append(
                {
                    "cycle": i + 1,
                    "status": result.status,
                    "phase": result.phase,
                    "draft": result.draft[:50] + "..." if result.draft else None,
                }
            )

            # In simulation, continue even on validation failure
            if result.status == "SUCCESS":
                logger.info(f"  ✅ Success")
            elif result.status == "VALIDATION_FAILED":
                logger.info(f"  ⚠️  Validation failed (expected in simulation)")
            else:
                logger.info(f"  ❌ Error: {result.error}")

        if args.json:
            print(
                json.dumps(
                    {
                        "simulation": True,
                        "total_cycles": cycles,
                        "results": results,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    indent=2,
                    default=str,
                )
            )
        else:
            successful = sum(1 for r in results if r["status"] == "SUCCESS")
            print(f"\n📊 Simulation Results:")
            print(f"  Total cycles: {cycles}")
            print(f"  Successful: {successful}/{cycles}")
            print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")

        return 0

    def run(self, argv=None) -> int:
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="HERALD Agency Director CLI (GAD-000 Compliant)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  herald status                    - Show current agency state
  herald run --theme campaign      - Execute one cycle with campaign theme
  herald loop --interval 3600      - Run continuous cycles every hour
  herald simulate --cycles 10      - Test 10 cycles without posting

GAD-000 Compliance:
  - All commands support --json for machine readability
  - Exit codes: 0=success, 1=error, 2=validation_failed
  - Safe for CI/CD, cron, and other AI agent orchestration
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Status command
        status_parser = subparsers.add_parser("status", help="Show agency status")
        status_parser.add_argument("--json", action="store_true", help="Output as JSON (for AI operators)")

        # Run command
        run_parser = subparsers.add_parser("run", help="Execute one I-P-V-O cycle")
        run_parser.add_argument(
            "--theme",
            choices=["auto", "tech_deep_dive", "campaign", "agent_city"],
            default="auto",
            help="Content generation theme",
        )
        run_parser.add_argument("--json", action="store_true", help="Output as JSON (for AI operators)")

        # Loop command
        loop_parser = subparsers.add_parser("loop", help="Run continuous cycles (daemon mode)")
        loop_parser.add_argument(
            "--interval",
            type=int,
            default=3600,
            help="Seconds between cycles (default: 3600 = 1 hour)",
        )
        loop_parser.add_argument(
            "--cycles",
            type=int,
            help="Max number of cycles (optional, infinite by default)",
        )
        loop_parser.add_argument(
            "--theme",
            choices=["auto", "tech_deep_dive", "campaign", "agent_city"],
            default="auto",
            help="Content generation theme",
        )
        loop_parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON (for monitoring systems)",
        )

        # Simulate command
        simulate_parser = subparsers.add_parser("simulate", help="Run simulation without real posts")
        simulate_parser.add_argument(
            "--cycles",
            type=int,
            default=5,
            help="Number of simulation cycles (default: 5)",
        )
        simulate_parser.add_argument(
            "--theme",
            choices=["auto", "tech_deep_dive", "campaign", "agent_city"],
            default="auto",
            help="Content generation theme",
        )
        simulate_parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args(argv)

        if not args.command:
            parser.print_help()
            return 0

        # Dispatch to command handler
        if args.command == "status":
            return self.cmd_status(args)
        elif args.command == "run":
            return self.cmd_run(args)
        elif args.command == "loop":
            return self.cmd_loop(args)
        elif args.command == "simulate":
            return self.cmd_simulate(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1


def main():
    """CLI entry point."""
    cli = HeraldCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
