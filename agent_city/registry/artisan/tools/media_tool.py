"""
ARTISAN Media Tool - Image processing and branding.

Capabilities:
- Crop to 16:9 (Twitter format)
- Apply 'Verified by Steward' watermark
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

logger = logging.getLogger("ARTISAN_MEDIA")


class MediaTool:
    """
    The Artisan's toolbox for media manipulation.
    """

    def __init__(self):
        """Initialize media tool."""
        if not Image:
            logger.warning("⚠️  Pillow not installed. Media capabilities disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Artisan Media Tool initialized")

    def process_image(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Process an image for publication:
        1. Crop to 16:9 aspect ratio (removing top/bottom bars/watermarks)
        2. Add 'Verified by Steward' overlay

        Args:
            image_path: Path to source image
            output_path: Path to save processed image (default: source_processed.png)

        Returns:
            str: Path to processed image, or None if failed
        """
        if not self.enabled:
            logger.error("❌ MediaTool disabled (Pillow missing)")
            return None

        try:
            img_path = Path(image_path)
            if not img_path.exists():
                logger.error(f"❌ Image not found: {image_path}")
                return None

            # Open image
            with Image.open(img_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                width, height = img.size
                logger.info(f"🎨 Processing image: {width}x{height}")

                # 1. Crop to 16:9
                # Target ratio: 1.777
                target_ratio = 16 / 9
                current_ratio = width / height

                if current_ratio < target_ratio:
                    # Image is too tall - crop top/bottom
                    # We prioritize the CENTER-TOP to keep heads/subjects,
                    # but specifically want to cut the BOTTOM to remove watermarks if present
                    new_height = int(width / target_ratio)

                    # Crop strategy:
                    # If we crop from center, we lose top and bottom equally.
                    # If we crop from top, we keep top and lose bottom.
                    # Let's do a slight offset: Keep top 10%, crop rest from bottom.
                    # Actually, simple center crop is usually safest for composition,
                    # BUT user specifically mentioned removing bottom watermark.
                    # So let's align to TOP (0,0) and cut the bottom.

                    left = 0
                    top = 0
                    right = width
                    bottom = new_height

                    # Safety check
                    if bottom > height:
                        bottom = height

                    logger.info(f"✂️ Cropping to 16:9 ({width}x{new_height}) - Top aligned")
                    img = img.crop((left, top, right, bottom))

                elif current_ratio > target_ratio:
                    # Image is too wide - crop sides (center)
                    new_width = int(height * target_ratio)
                    left = (width - new_width) // 2
                    top = 0
                    right = left + new_width
                    bottom = height

                    logger.info(f"✂️ Cropping to 16:9 ({new_width}x{height}) - Center aligned")
                    img = img.crop((left, top, right, bottom))

                # 2. Add Branding
                draw = ImageDraw.Draw(img)

                # Text settings
                text = "🛡️ Verified by Steward"

                # Dynamic font size (2% of height)
                font_size = int(img.height * 0.03)
                if font_size < 12:
                    font_size = 12

                # Try to load a font, fallback to default
                try:
                    # Try common system fonts
                    font_paths = [
                        "/System/Library/Fonts/Helvetica.ttc",  # Mac
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                        "arial.ttf",  # Windows/Generic
                    ]
                    font = None
                    for fp in font_paths:
                        if os.path.exists(fp):
                            font = ImageFont.truetype(fp, font_size)
                            break
                    if not font:
                        font = ImageFont.load_default()
                except Exception:
                    font = ImageFont.load_default()

                # Calculate text position (Bottom Right with padding)
                # Get text bbox
                left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                text_width = right - left
                text_height = bottom - top

                padding = int(img.height * 0.02)
                x = img.width - text_width - padding - 10
                y = img.height - text_height - padding - 10

                # Draw semi-transparent background for text
                # Pillow doesn't support alpha on draw.rectangle directly on RGB image easily without a separate layer
                # So we'll just draw a dark rectangle
                bg_left = x - 10
                bg_top = y - 5
                bg_right = x + text_width + 10
                bg_bottom = y + text_height + 5

                draw.rectangle((bg_left, bg_top, bg_right, bg_bottom), fill="#0a0e27")  # Steward Dark Blue

                # Draw text
                draw.text((x, y), text, font=font, fill="#64ffda")  # Steward Green

                # Save
                if not output_path:
                    output_path = str(img_path.parent / f"{img_path.stem}_artisan.png")

                img.save(output_path, "PNG")
                logger.info(f"✅ Saved processed image: {output_path}")

                return output_path

        except Exception as e:
            logger.error(f"❌ Image processing failed: {e}")
            return None
