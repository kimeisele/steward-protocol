#!/usr/bin/env python3
"""
HERALD Publisher Phase (Phase 4 of Campaign)

This script:
1. Reads the generated content bundle (dist/content.json)
2. Verifies Twitter credentials
3. Publishes to Twitter (text + optional media)
4. Reports results

Used in: GitHub Actions Job 3 (Execution Stage)
Input: dist/content.json + optional image
Output: Twitter post + log
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HERALD_PUBLISHER")

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.publisher import TwitterPublisher


def main():
    """Publish content from artifact bundle."""
    logger.info("🚀 PHASE 4: EXECUTION PIPELINE")
    logger.info("=" * 70)

    # PHASE 1: READ ARTIFACT
    logger.info("\n[PHASE 1] Reading Content Bundle...")

    dist_dir = Path("dist")
    content_file = dist_dir / "content.json"

    if not content_file.exists():
        logger.error(f"❌ No bundle found: {content_file}")
        logger.error("   (Likely the Generator phase failed or was not approved)")
        sys.exit(1)

    try:
        with open(content_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ BUNDLE READ FAILED: {e}")
        sys.exit(1)

    text = data.get("text")
    image_filename = data.get("image_filename")
    image_path = data.get("image_path")

    if not text:
        logger.error("❌ Bundle missing 'text' field")
        sys.exit(1)

    logger.info(f"✅ Bundle read successfully")
    logger.info(f"   Text: {len(text)} chars")
    logger.info(f"   Image: {image_filename if image_filename else 'None'}")

    # PHASE 2: INITIALIZE PUBLISHER
    logger.info("\n[PHASE 2] Initializing Publisher...")

    try:
        publisher = TwitterPublisher()
        logger.info("✅ Publisher initialized")
    except Exception as e:
        logger.error(f"❌ PUBLISHER INIT FAILED: {e}")
        sys.exit(1)

    # PHASE 3: VERIFY CREDENTIALS
    logger.info("\n[PHASE 3] Verifying OAuth Credentials...")

    if publisher.client is None:
        logger.error("❌ Twitter client not initialized")
        logger.error("   Check: TWITTER_API_KEY, TWITTER_API_SECRET,")
        logger.error("          TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
        sys.exit(1)

    if not publisher.verify_credentials():
        logger.error("❌ OAuth verification failed")
        logger.error("   Check token permissions in Twitter Dev Portal")
        sys.exit(1)

    logger.info("✅ OAuth credentials verified")

    # PHASE 4: PUBLISH
    logger.info("\n[PHASE 4] Publishing Content...")

    success = False

    if image_filename:
        # Publish with media
        img_path = dist_dir / image_filename

        if img_path.exists():
            logger.info(f"📸 Publishing with media: {image_filename}")

            try:
                if hasattr(publisher, "publish_with_media"):
                    success = publisher.publish_with_media(text, str(img_path))
                else:
                    logger.warning("⚠️  publish_with_media() not available")
                    logger.info("📝 Falling back to text-only")
                    success = publisher.publish(text)

            except Exception as e:
                logger.error(f"❌ PUBLISH WITH MEDIA FAILED: {e}")
                logger.info("📝 Retrying as text-only...")
                try:
                    success = publisher.publish(text)
                except Exception as e2:
                    logger.error(f"❌ TEXT FALLBACK ALSO FAILED: {e2}")
                    sys.exit(1)
        else:
            logger.warning(f"⚠️  Image file missing: {img_path}")
            logger.info("📝 Publishing text-only instead...")
            try:
                success = publisher.publish(text)
            except Exception as e:
                logger.error(f"❌ TEXT PUBLISH FAILED: {e}")
                sys.exit(1)

    else:
        # Publish text-only
        logger.info("📝 Publishing text-only content...")

        try:
            success = publisher.publish(text)
        except Exception as e:
            logger.error(f"❌ PUBLISH FAILED: {e}")
            sys.exit(1)

    # PHASE 5: SUMMARY
    logger.info("\n" + "=" * 70)

    if success:
        logger.info("✅ EXECUTION COMPLETE: Published successfully")
        logger.info(f"   Type: {'Media' if image_filename else 'Text'}")
        logger.info(f"   Length: {len(text)} chars")
        logger.info("=" * 70)
        sys.exit(0)
    else:
        logger.warning("⚠️  EXECUTION PARTIAL: Publisher returned False")
        logger.warning("   (May indicate credential or API issues)")
        logger.warning("   Check Twitter API logs for details")
        logger.info("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
