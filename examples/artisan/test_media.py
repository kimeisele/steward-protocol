"""
Test script for Artisan Media Tool.
Generates a dummy image and processes it.
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from artisan.tools.media_tool import MediaTool


def create_dummy_image(path: str):
    """Create a dummy image (square) to test cropping."""
    # 1024x1024 square image
    img = Image.new("RGB", (1024, 1024), color="red")
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Original Image", fill=(255, 255, 0))

    # Simulate a "watermark" at the bottom
    d.rectangle((0, 900, 1024, 1024), fill="black")
    d.text((400, 950), "UGLY WATERMARK", fill="white")

    img.save(path)
    print(f"Created dummy image: {path}")


def test_artisan():
    tool = MediaTool()

    # Setup
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    input_path = test_dir / "test_input.png"

    create_dummy_image(str(input_path))

    # Process
    print("Running Artisan...")
    output_path = tool.process_image(str(input_path))

    if output_path:
        print(f"Success! Output: {output_path}")

        # Verify dimensions
        with Image.open(output_path) as img:
            print(f"Output Size: {img.size}")
            ratio = img.width / img.height
            print(f"Aspect Ratio: {ratio:.3f} (Target: 1.777)")

            if 1.77 < ratio < 1.78:
                print("✅ Aspect Ratio Correct (16:9)")
            else:
                print("❌ Aspect Ratio Incorrect")
    else:
        print("❌ Processing failed")


if __name__ == "__main__":
    test_artisan()
