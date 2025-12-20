#!/usr/bin/env python3
"""
🥋 MANAS DOJO - Ephemeral Synaptic Training

OPUS-133: "MANAS lernt nicht um zu gewinnen, sondern um zu dienen."

Run MANAS through training scenarios in an ephemeral environment.
Only the learned synaptic weights persist - everything else is discarded.

Usage:
    python scripts/manas_dojo.py                    # Run mixed curriculum
    python scripts/manas_dojo.py --curriculum attack --scenarios 20
    python scripts/manas_dojo.py --curriculum progressive --epochs 3
    python scripts/manas_dojo.py --red-team         # Attack scenarios only

Curricula:
    basic        - Safe documentation/cleanup (warm-up)
    intermediate - Code modifications (moderate risk)
    advanced     - Complex refactoring (high skill)
    attack       - Red team scenarios (must be blocked!)
    chaos        - Edge cases, stress tests
    mixed        - Balanced mix of all types
    progressive  - Easy → Hard progression
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_logging(verbose: bool = False):
    """Configure logging for dojo training."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",  # Clean output for training
    )
    # Quiet down noisy loggers
    logging.getLogger("vibe_core").setLevel(logging.WARNING)
    logging.getLogger("MANAS").setLevel(logging.WARNING)
    logging.getLogger("LEDGER").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(
        description="🥋 MANAS DOJO - Ephemeral Synaptic Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/manas_dojo.py                          # Mixed curriculum, 10 scenarios
    python scripts/manas_dojo.py --curriculum attack      # Red team only
    python scripts/manas_dojo.py --scenarios 50 --epochs 3 # Intensive training
    python scripts/manas_dojo.py --red-team               # Attack simulation
    python scripts/manas_dojo.py --progressive            # Easy → Hard
        """,
    )

    parser.add_argument(
        "--curriculum",
        "-c",
        choices=["basic", "intermediate", "advanced", "attack", "chaos", "mixed", "progressive"],
        default="mixed",
        help="Training curriculum type (default: mixed)",
    )

    parser.add_argument(
        "--scenarios",
        "-s",
        type=int,
        default=10,
        help="Number of scenarios per epoch (default: 10)",
    )

    parser.add_argument(
        "--epochs",
        "-e",
        type=int,
        default=1,
        help="Number of training epochs (default: 1)",
    )

    parser.add_argument(
        "--red-team",
        action="store_true",
        help="Run attack scenarios only (alias for --curriculum attack)",
    )

    parser.add_argument(
        "--progressive",
        action="store_true",
        help="Run progressive curriculum (easy → hard)",
    )

    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Don't persist synaptic weights after training",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--stop-on-fail",
        action="store_true",
        help="Stop if an attack slips through (false negative)",
    )

    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed synapses with baseline patterns before training",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset synapses to baseline (WARNING: erases learned patterns!)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle shortcuts
    curriculum = args.curriculum
    if args.red_team:
        curriculum = "attack"
    if args.progressive:
        curriculum = "progressive"

    # Import dojo components
    from vibe_core.plugins.opus_assistant.manas.dojo.runner import (
        DojoConfig,
        DojoRunner,
    )
    from vibe_core.plugins.opus_assistant.manas.dojo.synaptic_seeder import (
        SynapticSeeder,
    )

    # Handle seeding/reset before training
    seeder = SynapticSeeder(project_root)

    if args.reset:
        print("\n⚠️  RESETTING SYNAPSES TO BASELINE...")
        result = seeder.reset_to_baseline()
        print(f"   ✅ Reset complete: {result['good_patterns']} good, {result['bad_patterns']} bad patterns")
        print()

    if args.seed:
        print("\n🌱 SEEDING BASELINE PATTERNS...")
        result = seeder.seed(force=False)  # Don't overwrite learned patterns
        print(f"   ✅ Seeded: +{result['good_added']} good, +{result['bad_added']} bad, ~{result['skipped']} skipped")
        print()

    # Configure
    config = DojoConfig(
        curriculum=curriculum,
        scenarios_per_epoch=args.scenarios,
        max_epochs=args.epochs,
        dry_run=True,  # Always dry run in training
        persist_synapses=not args.no_persist,
        persist_metrics=True,
        stop_on_false_negative=args.stop_on_fail,
    )

    # Banner
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🥋 PROJECT DOJO - Ephemeral Synaptic Training                   ║")
    print("║                                                                  ║")
    print("║  'MANAS lernt nicht um zu gewinnen, sondern um zu dienen.'       ║")
    print("║  'MANAS learns not to win, but to serve.'                        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # Run training
    runner = DojoRunner(project_root, config)
    session = runner.run_training()

    # Exit code based on results
    if session.attack_detection_rate < 0.8:
        print("\n⚠️  WARNING: Attack detection rate below 80%!")
        print("    MANAS needs more training to recognize threats.")
        sys.exit(1)

    if session.accuracy < 0.5:
        print("\n⚠️  WARNING: Overall accuracy below 50%!")
        print("    MANAS judgment needs calibration.")
        sys.exit(1)

    print("\n✅ Training session complete. Synapses updated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
