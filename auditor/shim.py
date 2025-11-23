#!/usr/bin/env python3
"""
AUDITOR Shim - Standalone execution wrapper

This shim allows AUDITOR to run as a standalone script or CLI tool,
while maintaining compatibility with Vibe-OS cartridge loading.

Usage:
    python auditor/shim.py --action audit
    python auditor/shim.py --action audit --no-fail   # Don't fail build on violations
    python auditor/shim.py --action verify-agent herald
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auditor.cartridge_main import AuditorCartridge


def setup_logging(verbose: bool = False):
    """Configure logging for standalone execution."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description="AUDITOR - GAD-000 Compliance Enforcement Agent"
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["audit", "verify-agent"],
        help="Action to perform",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="herald",
        help="Agent name to verify (for verify-agent action)",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Don't fail build on violations (warnings only)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Don't save compliance report to file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    # Initialize AUDITOR cartridge
    auditor = AuditorCartridge(root_path=Path("."))

    # Execute requested action
    if args.action == "audit":
        result = auditor.run_compliance_audit(
            save_report=not args.no_report,
            fail_on_violation=not args.no_fail,
        )

        # If we get here, audit passed (or no-fail mode is enabled)
        if result["status"] == "passed":
            print("\n✅ GAD-000 COMPLIANCE: PASSED")
            sys.exit(0)
        elif result["status"] == "failed" and args.no_fail:
            print("\n⚠️  GAD-000 COMPLIANCE: FAILED (warnings only)")
            sys.exit(0)
        else:
            # This shouldn't happen (fail_on_violation would have exited in cartridge)
            print("\n❌ GAD-000 COMPLIANCE: FAILED")
            sys.exit(1)

    elif args.action == "verify-agent":
        result = auditor.verify_single_agent(args.agent)
        print(f"\n🔍 Agent verification: {result['status']}")
        sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
