#!/usr/bin/env python3
"""
AGENT CITY OS - THE ONE ENTRY POINT

Usage:
    python boot.py              # Boot and run interactively
    python boot.py --check      # Verify system can boot (no operator loop)
    python boot.py --help       # Show this help

This boots the VibeOS Kernel with all agents and starts the operator loop.
The system runs until you press Ctrl+C or type 'exit'.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Verify critical dependencies are available."""
    missing = []

    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")

    try:
        import pydantic
    except ImportError:
        missing.append("pydantic")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False

    return True


def boot_check():
    """Quick boot verification - boots system but doesn't run operator loop."""
    from vibe_core.boot_orchestrator import BootOrchestrator

    print("=" * 60)
    print("AGENT CITY OS - BOOT CHECK")
    print("=" * 60)

    orchestrator = BootOrchestrator()
    try:
        kernel = orchestrator.boot()
        status = kernel.get_status()
        agents = status.get("agents_registered", 0)
        has_ritual = hasattr(kernel, "daily_ritual") and kernel.daily_ritual is not None

        print()
        print(f"Agents registered: {agents}")
        print(f"Daily Ritual:      {'Active' if has_ritual else 'MISSING'}")
        print(f"Kernel Status:     OPERATIONAL")
        print()
        print("=" * 60)
        print("BOOT CHECK: PASSED")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"BOOT CHECK: FAILED - {e}")
        return False


async def boot_and_run():
    """Full boot with interactive operator loop."""
    from vibe_core.boot_orchestrator import boot_and_run as _boot_and_run

    await _boot_and_run()


def main():
    parser = argparse.ArgumentParser(
        description="Agent City OS - Boot the VibeOS Kernel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python boot.py          # Start Agent City (interactive)
    python boot.py --check  # Verify boot works (quick test)
        """
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run boot verification only (no operator loop)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # Run appropriate mode
    if args.check:
        success = boot_check()
        sys.exit(0 if success else 1)
    else:
        print("=" * 60)
        print("AGENT CITY OS - STARTING")
        print("=" * 60)
        print("Press Ctrl+C to shutdown")
        print()
        try:
            asyncio.run(boot_and_run())
        except KeyboardInterrupt:
            print("\nShutdown requested.")
            sys.exit(0)


if __name__ == "__main__":
    main()
