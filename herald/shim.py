#!/usr/bin/env python3
"""
HERALD Shim - Vibe-OS Adapter for Standalone Execution

This shim allows HERALD to run in two modes:
1. Native VibeOS Cartridge (when imported by vibe-agency kernel)
2. Standalone Application (via this script)

The shim adapts the cartridge to work without a full Vibe-OS environment,
making it portable and testable.

Usage:
    python herald/shim.py --action run            # Generate content
    python herald/shim.py --action publish        # Publish prepared content
    python herald/shim.py --action plan_campaign  # Plan campaign strategy
    python herald/shim.py --action reply_cycle    # Run engagement loop
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HERALD_SHIM")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from herald.cartridge_main import HeraldCartridge


def main():
    """Main shim entry point."""
    parser = argparse.ArgumentParser(
        description="HERALD Autonomous Agent - Shim for standalone execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python herald/shim.py --action run            Generate content draft
  python herald/shim.py --action publish        Publish prepared content
  python herald/shim.py --action run --dry-run  Test without publishing
  python herald/shim.py --action reply_cycle    Run engagement loop
        """
    )
    parser.add_argument(
        "--action",
        choices=["run", "publish", "plan_campaign", "reply_cycle"],
        required=True,
        help="Action to execute"
    )
    parser.add_argument(
        "--content",
        help="Content for publish action (or loads from dist/content.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without publishing (for testing)"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=2,
        help="Campaign duration in weeks (for plan_campaign action)"
    )

    args = parser.parse_args()

    # Create output directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    # Initialize cartridge
    try:
        logger.info("🔌 Booting HERALD Cartridge...")
        cartridge = HeraldCartridge()
        logger.info("✅ Cartridge initialized")
    except Exception as e:
        logger.error(f"❌ Cartridge boot failed: {e}")
        sys.exit(1)

    # Execute action
    if args.action == "run":
        _execute_run(cartridge, dist_dir, args.dry_run)
    elif args.action == "publish":
        _execute_publish(cartridge, dist_dir, args.content)
    elif args.action == "plan_campaign":
        _execute_plan_campaign(cartridge, dist_dir, args.weeks, args.dry_run)
    elif args.action == "reply_cycle":
        _execute_reply_cycle(cartridge, dist_dir, args.dry_run)


def _execute_run(cartridge: HeraldCartridge, dist_dir: Path, dry_run: bool = False):
    """Execute the run action (campaign generation)."""
    logger.info("=" * 70)
    logger.info("EXECUTING: CAMPAIGN GENERATION")
    logger.info("=" * 70)

    try:
        # Run campaign
        result = cartridge.run_campaign(dry_run=dry_run)

        # Output result
        if result["status"] == "failed":
            logger.error(f"❌ Campaign failed: {result.get('reason')}")
            sys.exit(1)

        # Log preview
        content = result.get("content", "")
        logger.info(f"\n📄 Generated Content Preview:")
        logger.info(f"   {content[:80]}...")
        logger.info(f"   Length: {len(content)} chars")

        # Save artifact (for GitHub Actions workflow)
        artifact = {
            "text": content,
            "image_filename": None,
            "image_path": None,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "platform": "twitter",
            "dry_run": dry_run,
        }

        content_file = dist_dir / "content.json"
        with open(content_file, "w") as f:
            json.dump(artifact, f, indent=2)

        logger.info(f"\n✅ Artifact saved: {content_file}")

        # GitHub Actions output (if running in workflow)
        if "GITHUB_OUTPUT" in os.environ:
            output_file = os.environ["GITHUB_OUTPUT"]
            clean_text = content.replace('\n', ' ').replace('"', '\\"')
            with open(output_file, "a") as gh_out:
                gh_out.write(f"preview_text={clean_text}\n")
                gh_out.write(f"has_image=false\n")
                gh_out.write(f"platform=twitter\n")
            logger.info("✅ GitHub Actions output written")

        logger.info("\n" + "=" * 70)
        logger.info("✅ RUN PHASE COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Run action failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _execute_publish(cartridge: HeraldCartridge, dist_dir: Path, content: str = None):
    """Execute the publish action (content distribution)."""
    logger.info("=" * 70)
    logger.info("EXECUTING: PUBLICATION")
    logger.info("=" * 70)

    try:
        # Load content if not provided
        if not content:
            content_file = dist_dir / "content.json"
            if not content_file.exists():
                logger.error(f"❌ No content file found: {content_file}")
                sys.exit(1)

            with open(content_file) as f:
                data = json.load(f)
                content = data.get("text")

            if not content:
                logger.error("❌ Content file missing 'text' field")
                sys.exit(1)

            logger.info(f"✅ Loaded content from artifact: {len(content)} chars")

        # Verify content
        logger.info("\n[STEP 1] Verifying content...")
        if not content or len(content) < 10:
            logger.error("❌ Invalid content")
            sys.exit(1)

        logger.info(f"✅ Content verified: {len(content)} chars")
        logger.info(f"   Preview: {content[:80]}...")

        # Publish
        logger.info("\n[STEP 2] Publishing...")
        result = cartridge.execute_publish(content)

        if result.get("status") == "failed":
            logger.error(f"❌ Publish failed: {result.get('reason')}")
            sys.exit(1)

        logger.info(f"✅ Published: {result.get('platform')}")

        logger.info("\n" + "=" * 70)
        logger.info("✅ PUBLISH PHASE COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Publish action failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _execute_plan_campaign(cartridge: HeraldCartridge, dist_dir: Path, weeks: int = 2, dry_run: bool = False):
    """Execute the plan_campaign action (strategic roadmap generation)."""
    logger.info("=" * 70)
    logger.info("EXECUTING: CAMPAIGN STRATEGY PLANNING")
    logger.info("=" * 70)

    try:
        # Run planning
        result = cartridge.plan_campaign(duration_weeks=weeks, dry_run=dry_run)

        # Output result
        if result["status"] == "error" or result["status"] == "failed":
            logger.error(f"❌ Planning failed: {result.get('reason')}")
            sys.exit(1)

        # Log preview
        alignment = result.get("alignment", {})
        logger.info(f"\n📋 Strategy Generated:")
        logger.info(f"   Duration: {result.get('duration_weeks')} weeks")
        logger.info(f"   Governance-aligned: {alignment.get('governance_aligned')}")
        logger.info(f"   Status: {result.get('status')}")

        # Save artifact
        artifact = {
            "roadmap_path": result.get("roadmap_path"),
            "roadmap_preview": result.get("roadmap_preview"),
            "alignment": alignment,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "message": result.get("message"),
        }

        roadmap_file = dist_dir / "roadmap.json"
        with open(roadmap_file, "w") as f:
            json.dump(artifact, f, indent=2)

        logger.info(f"\n✅ Strategy artifact saved: {roadmap_file}")

        # GitHub Actions output (if running in workflow)
        if "GITHUB_OUTPUT" in os.environ:
            output_file = os.environ["GITHUB_OUTPUT"]
            with open(output_file, "a") as gh_out:
                gh_out.write(f"strategy_status={result.get('status')}\n")
                gh_out.write(f"governance_aligned={alignment.get('governance_aligned')}\n")
            logger.info("✅ GitHub Actions output written")

        logger.info("\n" + "=" * 70)
        logger.info("✅ PLANNING PHASE COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Planning action failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _execute_reply_cycle(cartridge: HeraldCartridge, dist_dir: Path, dry_run: bool = False):
    """Execute the reply cycle (engagement loop)."""
    logger.info("=" * 70)
    logger.info("EXECUTING: REPLY CYCLE")
    logger.info("=" * 70)

    try:
        result = cartridge.run_reply_cycle(dry_run=dry_run)
        
        logger.info("\n📊 Cycle Results:")
        logger.info(f"   Processed: {result.get('processed')}")
        logger.info(f"   Drafted: {result.get('drafted')}")
        logger.info(f"   Drafts File: {result.get('drafts_file')}")
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ REPLY CYCLE COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Reply cycle failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
