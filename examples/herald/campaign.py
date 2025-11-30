#!/usr/bin/env python3
"""
HERALD Campaign Launcher (LLM-Powered Insight Agent)

This script:
1. Initializes TwitterPublisher with OAuth 1.0a credentials
2. Verifies Twitter connection using verify_credentials()
3. Generates intelligent content via HERALD Brain (LLM-based)
4. Publishes content with graceful fallback
5. Reports results
"""

import logging
import sys
from pathlib import Path

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HERALD_CAMPAIGN")

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.artist import HeraldArtist
from examples.herald.brain import HeraldBrain
from examples.herald.publisher import TwitterPublisher


def run_campaign():
    """Main campaign execution with HERALD Brain."""
    logger.info("🦅 PHOENIX: Igniting HERALD Brain...")
    logger.info("=" * 70)

    # PHASE 1: INITIALIZE INFRASTRUCTURE
    logger.info("PHASE 1: Initializing Publisher, Brain & Artist...")
    try:
        publisher = TwitterPublisher()
        brain = HeraldBrain()
        artist = HeraldArtist()
        logger.info("✅ Infrastructure initialized (Publisher + Brain + Artist)")
    except Exception as e:
        logger.error(f"❌ CRITICAL: {e}")
        sys.exit(1)

    # PHASE 2: VERIFY PUBLISHER
    logger.info("\nPHASE 2: OAuth 1.0a Diagnostic...")

    if publisher.client is None:
        logger.error("❌ DIAGNOSTIC FAIL: Missing Twitter OAuth credentials")
        logger.error("   Required: TWITTER_API_KEY, TWITTER_API_SECRET,")
        logger.error("             TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
        sys.exit(1)

    if publisher.verify_credentials():
        logger.info("✅ DIAGNOSTIC PASS: OAuth 1.0a verified")
    else:
        logger.error("❌ DIAGNOSTIC FAIL: OAuth 1.0a failed")
        logger.error("   Check permissions & User Context in Dev Portal")
        sys.exit(1)

    # PHASE 3: GENERATE INTELLIGENT CONTENT
    logger.info("\nPHASE 3: Brain Generating Insight...")

    content = brain.generate_insight()

    # Validate content
    if not content or len(content) < 10:
        logger.error("❌ BRAIN FART: Generated content too short or empty")
        sys.exit(1)

    logger.info(f"📝 Generated Insight:\n{content}")

    # PHASE 3B: GENERATE VISUAL CONTENT
    logger.info("\nPHASE 3B: Artist Generating Visual...")

    image_path = artist.generate_visual(content, style="cyberpunk")

    if image_path:
        logger.info("🎨 Visual generated successfully")
    else:
        logger.warning("⚠️  PHASE 3B: Artist failed (will fall back to text-only)")
        image_path = None

    # PHASE 4: PUBLISH (WITH MEDIA IF AVAILABLE)
    logger.info("\nPHASE 4: Publishing to Twitter...")

    if image_path:
        logger.info("📸 Publishing with media...")
        success = publisher.publish_with_media(content, image_path)
    else:
        logger.info("📝 Publishing text-only...")
        success = publisher.publish(content)

    if success:
        logger.info("✅ PHASE 4 COMPLETE: Published successfully")
        if image_path:
            logger.info("   ✅ With visual media attached")
    else:
        logger.warning("⚠️  PHASE 4 PARTIAL: Publisher returned False")
        logger.warning("   (May happen if credentials invalid)")

    # SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("🎯 HERALD Campaign Complete")
    logger.info("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    run_campaign()
