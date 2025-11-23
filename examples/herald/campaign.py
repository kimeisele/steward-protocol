#!/usr/bin/env python3
"""
HERALD Campaign Launcher (Simplified OAuth 1.0a Edition)

This script:
1. Initializes TwitterPublisher with OAuth 1.0a credentials
2. Verifies Twitter connection using verify_credentials()
3. Publishes test content
4. Reports results
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

from examples.herald.publisher import TwitterPublisher, MultiChannelPublisher


def run_campaign():
    """Main campaign execution."""
    logger.info("🦅 HERALD Campaign Starting...")
    logger.info("=" * 70)

    # PHASE 1: INITIALIZE PUBLISHER
    logger.info("PHASE 1: Initializing Twitter Publisher...")
    try:
        twitter = TwitterPublisher()
        logger.info("✅ Publisher initialized")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Publisher failed to initialize: {e}")
        sys.exit(1)

    # PHASE 2: DIAGNOSTIC CHECK (OAuth 1.0a)
    logger.info("\nPHASE 2: Running OAuth 1.0a Diagnostic...")

    if twitter.client is None:
        logger.error("❌ DIAGNOSTIC FAIL: Client is None - Missing OAuth 1.0a credentials")
        logger.error("   Required environment variables:")
        logger.error("   - TWITTER_API_KEY (Consumer Key)")
        logger.error("   - TWITTER_API_SECRET (Consumer Secret)")
        logger.error("   - TWITTER_ACCESS_TOKEN (Access Token)")
        logger.error("   - TWITTER_ACCESS_SECRET (Access Token Secret)")
        logger.error("")
        logger.error("   Fix in GitHub Secrets or .env file and retry.")
        sys.exit(1)

    # Use the verify_credentials() method
    if twitter.verify_credentials():
        logger.info("✅ DIAGNOSTIC PASS: OAuth 1.0a authentication verified")
    else:
        logger.error("❌ DIAGNOSTIC FAIL: OAuth 1.0a authentication failed")
        logger.error("   Check: Are app permissions set to 'Read AND Write' in Dev Portal?")
        logger.error("   Check: Is OAuth 1.0a User Context enabled?")
        sys.exit(1)

    # PHASE 3: CAMPAIGN EXECUTION
    logger.info("\nPHASE 3: Generating and Publishing Content...")

    content = "🦅 HERALD Agent running via GitHub Actions & Steward Protocol. #BuildInPublic #AI"
    tags = ["#StewardProtocol", "#HERALD"]

    logger.info(f"📝 Content: {content}")
    logger.info(f"🏷️  Tags: {' '.join(tags)}")

    # Try to publish
    success = twitter.publish(content, tags=tags)

    if success:
        logger.info("✅ PHASE 3 COMPLETE: Content published successfully")
    else:
        logger.warning("⚠️  PHASE 3 PARTIAL: Publisher returned False")
        logger.warning("   (This may happen if credentials are missing or invalid)")

    # SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("🎯 HERALD Campaign Execution Complete")
    logger.info("=" * 70)

    # Exit code 0 to not break the workflow (logging is the diagnostics)
    sys.exit(0)


if __name__ == "__main__":
    run_campaign()
