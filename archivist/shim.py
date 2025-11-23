#!/usr/bin/env python3
"""
ARCHIVIST Shim - Standalone Entry Point

Allows running ARCHIVIST as a standalone agent (without VibeOS kernel).

Usage:
    python archivist/shim.py --action audit
    python archivist/shim.py --action audit --agent herald
    python archivist/shim.py --action status
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from archivist.cartridge_main import ArchivistCartridge


def setup_logging(verbose: bool = False):
    """Configure logging for standalone execution."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main():
    """Main entry point for standalone ARCHIVIST execution."""
    parser = argparse.ArgumentParser(
        description="ARCHIVIST - Audit & Verification Agent"
    )
    parser.add_argument(
        "--action",
        choices=["audit", "status", "verify"],
        default="audit",
        help="Action to perform (default: audit)",
    )
    parser.add_argument(
        "--agent",
        default="herald",
        help="Agent to audit (default: herald)",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Custom event file path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger("ARCHIVIST_SHIM")
    logger.info("🔍 ARCHIVIST Standalone Mode")
    logger.info("=" * 70)

    # Initialize cartridge
    try:
        archivist = ArchivistCartridge()
    except Exception as e:
        logger.error(f"❌ Failed to initialize ARCHIVIST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Execute action
    try:
        if args.action == "status":
            # Report status
            logger.info("\n📊 ARCHIVIST Status Report")
            logger.info("=" * 70)
            status = archivist.report_status()

            import json
            print(json.dumps(status, indent=2))

        elif args.action == "audit":
            # Run audit on specified agent
            logger.info(f"\n🔍 Auditing agent: {args.agent}")
            logger.info("=" * 70)

            result = archivist.audit_agent(
                agent_name=args.agent,
                event_file=args.event_file,
            )

            logger.info("\n📊 Audit Result:")
            logger.info("=" * 70)
            import json
            print(json.dumps(result, indent=2))

        elif args.action == "verify":
            # Verify a single event (for testing)
            logger.info("\n🔍 Single Event Verification (Test Mode)")
            logger.info("Not yet implemented - use 'audit' action")

        else:
            logger.error(f"❌ Unknown action: {args.action}")
            sys.exit(1)

        logger.info("\n✅ Execution complete")
        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
