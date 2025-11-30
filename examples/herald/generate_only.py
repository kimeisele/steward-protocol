#!/usr/bin/env python3
"""
HERALD Generator Phase (Phase 1-3 of Campaign)

This script:
1. Initializes HeraldBrain (with Research + Editor + Aligner)
2. Generates content (text insight + visual)
3. Bundles output to dist/ directory for GitHub Artifacts
4. Writes GitHub Output for workflow visibility

Used in: GitHub Actions Job 1 (Draft Stage)
Output: dist/content.json + optional image
"""

import json
import logging
import os
import shutil
import sys
from pathlib import Path

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("HERALD_GENERATOR")

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.artist import HeraldArtist
from examples.herald.brain import HeraldBrain


def main():
    """Generate content bundle for approval workflow."""
    logger.info("🧠 PHASE 1-3: GENERATION PIPELINE")
    logger.info("=" * 70)

    # Prepare artifact directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    logger.info(f"📁 Artifact directory: {dist_dir}")

    # PHASE 1: INITIALIZE BRAIN
    logger.info("\n[PHASE 1] Initializing Brain...")
    try:
        brain = HeraldBrain()
        logger.info("✅ Brain initialized (Research + Editor + Aligner)")
    except Exception as e:
        logger.error(f"❌ BRAIN INIT FAILED: {e}")
        sys.exit(1)

    # PHASE 2: GENERATE TEXT INSIGHT
    logger.info("\n[PHASE 2] Generating Text Content...")
    try:
        content = brain.generate_insight()

        if not content or len(content) < 10:
            logger.error("❌ Brain generated empty or too-short content")
            sys.exit(1)

        logger.info(f"✅ Text generated ({len(content)} chars)")
        logger.info(f"📝 Content preview: {content[:100]}...")

    except Exception as e:
        logger.error(f"❌ GENERATION FAILED: {e}")
        sys.exit(1)

    # PHASE 3: GENERATE VISUAL
    logger.info("\n[PHASE 3] Generating Visual Content...")
    image_path = None
    image_filename = None

    try:
        artist = HeraldArtist()
        image_path = artist.generate_visual(content, style="cyberpunk")

        if image_path:
            logger.info(f"✅ Visual generated: {image_path}")

            # Move image to dist/ for artifact bundling
            img_name = Path(image_path).name
            final_img_path = dist_dir / img_name
            shutil.copy(image_path, final_img_path)
            image_filename = img_name
            logger.info(f"📦 Bundled to dist/{img_name}")
        else:
            logger.warning("⚠️  Artist unavailable (will publish text-only)")

    except Exception as e:
        logger.error(f"❌ ARTIST ERROR: {e}")
        logger.warning("⚠️  Continuing with text-only content")

    # PHASE 4: BUNDLE ARTIFACT
    logger.info("\n[PHASE 4] Bundling Artifact...")

    payload = {
        "text": content,
        "image_filename": image_filename,
        "image_path": str(image_path) if image_path else None,
    }

    content_file = dist_dir / "content.json"
    with open(content_file, "w") as f:
        json.dump(payload, f, indent=2)

    logger.info(f"✅ Bundle saved: {content_file}")

    # PHASE 5: GITHUB OUTPUT (for workflow visibility)
    logger.info("\n[PHASE 5] Exporting GitHub Output...")

    if "GITHUB_OUTPUT" in os.environ:
        output_file = os.environ["GITHUB_OUTPUT"]
        with open(output_file, "a") as gh_out:
            # Escape newlines for GitHub Actions
            clean_text = content.replace("\n", " ").replace('"', '\\"')
            gh_out.write(f"preview_text={clean_text}\n")
            gh_out.write(f"has_image={'true' if image_filename else 'false'}\n")
        logger.info("✅ GitHub Output written")
    else:
        logger.debug("⚠️  GITHUB_OUTPUT not set (local mode)")

    # SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("✅ GENERATION COMPLETE")
    logger.info(f"   Content: {len(content)} chars")
    logger.info(f"   Visual: {'Yes' if image_filename else 'No'}")
    logger.info("   Artifact: dist/content.json")
    logger.info("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    main()
