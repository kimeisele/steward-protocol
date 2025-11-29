#!/usr/bin/env python3
"""
HERALD Visual Artist (v1.0)
The Creative Visuals Department via Pollinations.ai

Role: Takes tweet text and generates thematic cyberpunk/technical visuals.
API: Pollinations.ai (Free, Fast, No Auth Required)
Output: High-quality images in JPEG format

Strategy:
- Generate images that match the tweet's theme
- Style: Cyberpunk blueprint / technical schematic / neon look
- Keep dimensions 16:9 (800x450) for Twitter/social media
- No watermark removal (we embrace "Free & Open Source" branding)
"""

import os
import time
import logging
import requests
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger("HERALD_ARTIST")


class HeraldArtist:
    """Visual Artist: Generates images via Pollinations.ai"""

    def __init__(self):
        """Initialize the Visual Artist."""
        self.output_dir = Path("examples/herald/assets")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Pollinations.ai config
        self.base_url = "https://image.pollinations.ai/prompt"
        self.timeout = 15

        logger.info("✅ ARTIST: Initialized (Pollinations.ai backend)")

    def generate_visual(self, prompt_text, style="cyberpunk"):
        """
        Generate a visual for a tweet.

        Args:
            prompt_text (str): The tweet/content to visualize
            style (str): Visual style preset ("cyberpunk" or "abstract")

        Returns:
            str: Path to generated image file, or None if failed
        """

        # 1. Extract key words from the prompt (first 6 words as "subject")
        words = prompt_text.split()[:6]
        subject = " ".join(words).replace("#", "").strip()

        # 2. Build the full prompt with style
        if style == "cyberpunk":
            full_prompt = (
                f"cyberpunk blueprint technical schematic neon green lines "
                f"dark background digital circuit board {subject} "
                f"abstract AI agent network graph highly detailed 4k"
            )
        else:  # abstract fallback
            full_prompt = (
                f"abstract digital art network visualization {subject} "
                f"neon glowing lines dark background technical illustration"
            )

        # 3. URL-encode the prompt safely
        encoded = quote(full_prompt)

        # 4. Build final URL (add parameters for size and quality)
        # Note: Removed nologo param - Pollinations API changed
        url = f"{self.base_url}/{encoded}"

        # 5. Generate filename with timestamp
        timestamp = int(time.time())
        filename = self.output_dir / f"visual_{timestamp}.jpg"

        try:
            logger.info(f"🎨 ARTIST: Generating visual for '{subject}'...")
            logger.debug(f"   Prompt: {full_prompt[:80]}...")
            logger.debug(f"   URL: {url[:100]}...")

            # Add proper HTTP headers to mimic browser request
            headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

            # Request image from Pollinations with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=self.timeout, headers=headers)

                    if response.status_code == 200:
                        # Save to disk
                        with open(filename, "wb") as f:
                            f.write(response.content)

                        file_size_kb = filename.stat().st_size / 1024
                        logger.info(f"✅ ARTIST: Image saved ({file_size_kb:.1f} KB)")
                        logger.info(f"   Path: {filename}")

                        return str(filename)
                    elif response.status_code == 403:
                        logger.warning(f"⚠️  ARTIST: HTTP {response.status_code} (Rate limit/Auth issue)")
                        if attempt < max_retries - 1:
                            logger.info("   Retrying in 2 seconds...")
                            time.sleep(2)
                        else:
                            return None
                    else:
                        logger.warning(f"⚠️  ARTIST: Pollinations returned {response.status_code}")
                        logger.debug(f"   Response: {response.text[:200]}")
                        return None

                except requests.exceptions.Timeout:
                    logger.error("❌ ARTIST: Request timeout (Pollinations taking too long)")
                    return None

        except Exception as e:
            logger.error(f"❌ ARTIST ERROR: {type(e).__name__}: {e}")
            return None

    def generate_visual_batch(self, prompt_texts, style="cyberpunk"):
        """
        Generate multiple visuals (for future batch campaigns).

        Args:
            prompt_texts (list): List of text prompts
            style (str): Visual style

        Returns:
            list: Paths to generated images
        """
        results = []
        for i, text in enumerate(prompt_texts):
            logger.info(f"🎨 ARTIST: Batch generation {i + 1}/{len(prompt_texts)}")
            image_path = self.generate_visual(text, style=style)
            if image_path:
                results.append(image_path)
            # Small delay to respect API rate limits
            if i < len(prompt_texts) - 1:
                time.sleep(1)

        logger.info(f"✅ ARTIST: Batch complete ({len(results)}/{len(prompt_texts)} images)")
        return results


# --- Demo/Test Mode ---
if __name__ == "__main__":
    logger.info("🧪 HERALD VISUAL ARTIST - Test Mode")
    logger.info("=" * 60)

    artist = HeraldArtist()

    # Test prompt
    test_prompt = "Agent identity is the missing layer in the AI stack cryptographic verification"
    logger.info(f"\nGenerating visual for:\n  '{test_prompt}'")

    image_path = artist.generate_visual(test_prompt)

    if image_path:
        logger.info(f"✅ SUCCESS: Image generated at {image_path}")
    else:
        logger.warning("⚠️  FAILED: Could not generate image (check internet connection)")

    logger.info("=" * 60)
