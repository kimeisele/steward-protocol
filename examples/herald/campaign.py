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

import os
import sys
import logging
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HERALD_CAMPAIGN")

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.publisher import TwitterPublisher, RedditPublisher, MultiChannelPublisher
from examples.herald.brain import HeraldBrain


def run_campaign():
    """Main campaign execution with HERALD Brain (Multi-Channel Edition)."""
    logger.info("🦅 HERALD: Igniting Multi-Channel Campaign...")
    logger.info("=" * 70)

    # PHASE 0: DETERMINE MODE
    mode = os.getenv("HERALD_MODE", "twitter").lower()
    logger.info(f"🎯 Campaign Mode: {mode.upper()}")

    if mode not in ["twitter", "reddit_deepdive"]:
        logger.error(f"❌ Invalid HERALD_MODE: {mode}")
        logger.error("   Valid options: 'twitter', 'reddit_deepdive'")
        sys.exit(1)

    # PHASE 1: INITIALIZE INFRASTRUCTURE
    logger.info("\nPHASE 1: Initializing Brain & Publishers...")
    try:
        brain = HeraldBrain()
        if mode == "twitter":
            publisher = TwitterPublisher()
        else:  # reddit_deepdive
            publisher = RedditPublisher()
        logger.info("✅ Infrastructure initialized")
    except Exception as e:
        logger.error(f"❌ CRITICAL: {e}")
        sys.exit(1)

    # PHASE 2: VERIFY CREDENTIALS
    logger.info("\nPHASE 2: Credential Diagnostic...")

    if not publisher.verify_credentials():
        logger.error("❌ DIAGNOSTIC FAIL: Publisher credentials invalid")
        sys.exit(1)

    logger.info("✅ DIAGNOSTIC PASS: Credentials verified")

    # PHASE 3: GENERATE INTELLIGENT CONTENT
    logger.info(f"\nPHASE 3: Brain Generating {mode.upper()} Content...")

    if mode == "twitter":
        content = brain.generate_insight()
        if not content or len(content) < 10:
            logger.error("❌ BRAIN FART: Generated content too short or empty")
            sys.exit(1)
        logger.info(f"📝 Generated Insight:\n{content}")
    else:  # reddit_deepdive
        subreddit = os.getenv("REDDIT_TARGET_SUBREDDIT", "r/LocalLLaMA")
        logger.info(f"   Target: {subreddit}")
        post = brain.generate_reddit_deepdive(subreddit=subreddit)
        if not post:
            logger.error("❌ BRAIN FART: No Reddit post generated")
            sys.exit(1)
        logger.info(f"📝 Generated Reddit Post:")
        logger.info(f"   Title: {post['title']}")
        logger.info(f"   Body: {post['body'][:100]}...")

    # PHASE 4: PUBLISH
    logger.info(f"\nPHASE 4: Publishing to {mode.upper()}...")

    if mode == "twitter":
        success = publisher.publish(content)
    else:  # reddit_deepdive
        subreddit_name = os.getenv("REDDIT_TARGET_SUBREDDIT", "r/LocalLLaMA").replace("r/", "")
        success = publisher.publish(post['title'], post['body'], subreddit_name=subreddit_name)

    if success:
        logger.info("✅ PHASE 4 COMPLETE: Published successfully")
    else:
        logger.warning("⚠️  PHASE 4 PARTIAL: Publisher returned False")

    # SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info(f"🎯 HERALD {mode.upper()} Campaign Complete")
    logger.info("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    run_campaign()
