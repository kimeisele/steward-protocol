"""
CARD GENERATOR - Artisan 2.0.

Mints Cyberpunk Trading Cards for Agent City.
"""

import logging
from pathlib import Path
from typing import Any, Dict

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None

logger = logging.getLogger("CARD_GEN")


class CardGenerator:
    """
    Mints dynamic PNG cards for agents.
    """

    def __init__(self, output_dir: Path = Path("docs/cards")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not Image:
            logger.warning("⚠️ Pillow not installed. Card generation disabled.")

    def generate_card(self, agent_data: Dict[str, Any], tier_info: Dict[str, Any]) -> str:
        """
        Draw a trading card.

        Args:
            agent_data: {agent_id, role, joined_at}
            tier_info: {name, color, min_xp}

        Returns:
            str: Path to generated image
        """
        if not Image:
            return ""

        agent_id = agent_data.get("agent_id", "UNKNOWN")
        role = agent_data.get("role", "Agent")
        xp = agent_data.get("xp", 0)
        tier_name = tier_info.get("name", "Novice")
        tier_color = tier_info.get("color", "#808080")

        # Canvas
        width, height = 400, 600
        bg_color = (20, 20, 25)  # Dark Grey

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Border (Tier Color)
        border_width = 10
        draw.rectangle([0, 0, width - 1, height - 1], outline=tier_color, width=border_width)

        # Inner Frame
        draw.rectangle([20, 20, width - 20, height - 20], outline=(50, 50, 60), width=2)

        # Header (Agent ID)
        try:
            # Try to load a font, fallback to default
            font_large = ImageFont.truetype("Arial.ttf", 40)
            font_medium = ImageFont.truetype("Arial.ttf", 24)
            font_small = ImageFont.truetype("Arial.ttf", 16)
        except IOError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Title
        draw.text((40, 50), agent_id, fill="white", font=font_large)
        draw.text((40, 100), role.upper(), fill=(150, 150, 150), font=font_medium)

        # Tier Badge
        badge_y = 200
        draw.rectangle([40, badge_y, 360, badge_y + 60], fill=(30, 30, 35), outline=tier_color)
        draw.text(
            (60, badge_y + 15),
            f"TIER: {tier_name.upper()}",
            fill=tier_color,
            font=font_medium,
        )

        # XP Stats
        stats_y = 300
        draw.text((40, stats_y), f"XP: {xp}", fill="white", font=font_medium)
        draw.text((40, stats_y + 40), f"Next Tier: ???", fill="grey", font=font_small)

        # Footer
        draw.text((40, 550), "STEWARD PROTOCOL", fill=(100, 100, 100), font=font_small)
        draw.text((250, 550), "VERIFIED", fill=tier_color, font=font_small)

        # Save
        filename = f"{agent_id}.png"
        path = self.output_dir / filename
        img.save(path)

        logger.info(f"🃏 Minted card for {agent_id}: {path}")
        return str(path)
