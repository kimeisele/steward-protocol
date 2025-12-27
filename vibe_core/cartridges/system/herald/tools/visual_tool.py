"""
HERALD Visual Tool - Deterministic Multimedia Asset Generation.

Generates visual assets (ASCII art, SVG) that complement text content.
Offline-capable, deterministic, and governance-aware.

Philosophy:
- Visual identity for Agent City
- Deterministic (no LLM, no randomness)
- Accessibility-first (alt_text required)
- Fast (< 100ms per asset)

Supported formats:
- ASCII: Terminal-friendly, minimal bandwidth
- SVG: Scalable, web-ready, metadata-rich
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("HERALD_VISUAL")


@dataclass
class VisualAsset:
    """Represents a generated visual asset."""

    asset_type: str  # "ascii" or "svg"
    content: str  # The actual SVG/ASCII content
    alt_text: str  # Accessibility text
    keywords: List[str]  # Metadata: what this asset represents
    width: Optional[int] = None
    height: Optional[int] = None


class VisualTool(Tool):
    """
    Generates visual assets to complement text content.

    Strategy:
    1. Extract keywords from text draft
    2. Map keywords to visual templates (ASCII or SVG)
    3. Customize template based on style preset
    4. Return accessibility-first asset
    """

    # Visual themes/presets
    THEMES = {
        "agent_city": {
            "name": "Agent City Cyberpunk",
            "color_scheme": ["#00FF00", "#00FFFF", "#FF00FF"],
            "style": "neon",
        },
        "protocol": {
            "name": "Protocol Blueprint",
            "color_scheme": ["#0066FF", "#00CCFF", "#FFFFFF"],
            "style": "technical",
        },
        "cryptography": {
            "name": "Cryptographic Lock",
            "color_scheme": ["#FFD700", "#FF8C00", "#FF4500"],
            "style": "technical",
        },
        "governance": {
            "name": "Governance Matrix",
            "color_scheme": ["#4CAF50", "#8BC34A", "#FFFFFF"],
            "style": "matrix",
        },
        "minimal": {
            "name": "Minimal Zen",
            "color_scheme": ["#000000", "#FFFFFF"],
            "style": "minimal",
        },
    }

    # Keyword-to-visual mappings
    KEYWORD_VISUALS = {
        # Keywords that should trigger Agent visuals
        "agent": ["agent_icon", "federation"],
        "ai": ["neural_network", "intelligence"],
        "identity": ["key", "signature"],
        "crypto": ["lock", "key_exchange"],
        "governance": ["rules", "matrix"],
        "city": ["cityscape", "network"],
        "protocol": ["protocol_diagram", "blueprint"],
        "trust": ["chain", "link"],
        "verification": ["checkmark", "seal"],
    }

    @property
    def name(self) -> str:
        """Tool name for registry."""
        return "herald.visual"

    @property
    def description(self) -> str:
        """Tool description for LLM context."""
        return "Generates visual assets (ASCII art, SVG) to complement text content"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters."""
        return {
            "text_draft": {"type": "string", "required": True, "description": "Text content to visualize"},
            "style_preset": {"type": "string", "required": False, "default": "agent_city"},
            "format_type": {"type": "string", "required": False, "default": "ascii", "enum": ["ascii", "svg"]},
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate parameters before execution."""
        if "text_draft" not in parameters:
            raise ValueError("Missing required parameter: text_draft")

    def execute(self, parameters: Dict[str, Any]) -> "ToolResult":
        """Execute visual generation and return ToolResult."""
        from dataclasses import asdict

        asset = self.generate(
            text_draft=parameters["text_draft"],
            style_preset=parameters.get("style_preset", "agent_city"),
            format_type=parameters.get("format_type", "ascii"),
        )
        return ToolResult(success=True, result=asdict(asset))

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """
        Initialize visual tool.

        Args:
            services: ServiceRegistry for dependency injection
        """
        super().__init__(services)
        self.theme_cache = {}
        logger.info("🎨 Visual Tool initialized")

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract visual keywords from text draft.

        Args:
            text: The text content to analyze

        Returns:
            List of detected keywords
        """
        text_lower = text.lower()
        detected = []

        for keyword in self.KEYWORD_VISUALS.keys():
            if keyword in text_lower:
                detected.append(keyword)

        return detected if detected else ["default"]

    def _select_theme(self, keywords: List[str], style_preset: str = "agent_city") -> Dict[str, Any]:
        """
        Select appropriate theme based on keywords and preset.

        Args:
            keywords: List of keywords from text
            style_preset: Preferred style (agent_city, protocol, etc)

        Returns:
            Theme configuration dict
        """
        theme = self.THEMES.get(style_preset, self.THEMES["agent_city"])
        return theme

    def generate_ascii(self, keywords: List[str], theme: Dict[str, Any]) -> str:
        """
        Generate ASCII art based on keywords.

        This is deterministic and doesn't use LLMs.

        Args:
            keywords: List of keywords
            theme: Theme configuration

        Returns:
            ASCII art string
        """
        # Agent visualization
        if "agent" in keywords:
            return """
    ╔════════════════════════╗
    ║   HERALD AGENT CITY    ║
    ║  Artificial Governed   ║
    ║   Intelligence (A.G.I) ║
    ╚════════════════════════╝
        ┌─────────────────┐
        │ [AGENT]  [DATA] │
        │ [TRUST]  [SIGN] │
        └─────────────────┘
        """

        # Governance/Constitution visualization
        elif "governance" in keywords or "rules" in keywords:
            return """
    ┏━━━━━━━━━━━━━━━━━━━━┓
    ┃  GOVERNANCE RULES   ┃
    ┣━━━━━━━━━━━━━━━━━━━━┫
    ┃ ✓ Prime Directives  ┃
    ┃ ✓ Validation Gates  ┃
    ┃ ✓ Compliance Checks ┃
    ┗━━━━━━━━━━━━━━━━━━━━┛
            │
         ENFORCED
            │
            v
    ╔═════════════════════╗
    ║  OUTPUT VALIDATED   ║
    ╚═════════════════════╝
        """

        # Cryptography/Identity
        elif "crypto" in keywords or "identity" in keywords:
            return """
    ╔══════════════════════════╗
    ║  CRYPTOGRAPHIC IDENTITY  ║
    ║  (NIST P-256)            ║
    ║                          ║
    ║  ┌────────────────────┐  ║
    ║  │ pub: 0x4A7C9...   │  ║
    ║  │ sig: 0xFE23D...   │  ║
    ║  └────────────────────┘  ║
    ║                          ║
    ║  🔒 Signed & Verified    ║
    ╚══════════════════════════╝
        """

        # Network/Federation
        elif "city" in keywords or "federation" in keywords:
            return """
        AGENT FEDERATION

        HERALD ←→ ARCHIVIST
           ↓       ↑
        AUDITOR   ENGINEER
           ↓       ↑
       STEWARD ←→ ARTISAN

        [7 Sovereign Agents]
        [Cryptographically Verified]
        [Event-Sourced]
        """

        # Default: Minimal identity
        else:
            return """
    ╭─────────────────────╮
    │   HERALD AGENT      │
    │   A.G.I.  System    │
    │   Autonomous.       │
    │   Governed.         │
    │   Intelligent.      │
    ╰─────────────────────╯
        """

    def generate_svg(self, keywords: List[str], theme: Dict[str, Any]) -> str:
        """
        Generate SVG snippet based on keywords and theme.

        Args:
            keywords: List of keywords
            theme: Theme configuration

        Returns:
            SVG string
        """
        colors = theme.get("color_scheme", ["#000000", "#FFFFFF"])
        primary_color = colors[0]
        secondary_color = colors[1] if len(colors) > 1 else colors[0]

        # Base SVG structure
        if "governance" in keywords:
            return f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="200" fill="white"/>
  <text x="200" y="30" font-size="20" font-weight="bold" text-anchor="middle" fill="{primary_color}">
    HERALD GOVERNANCE
  </text>
  <g stroke="{primary_color}" stroke-width="2" fill="none">
    <circle cx="100" cy="100" r="40"/>
    <circle cx="300" cy="100" r="40"/>
    <line x1="140" y1="100" x2="260" y2="100"/>
  </g>
  <text x="100" y="110" text-anchor="middle" font-size="12" fill="{primary_color}">
    INPUT
  </text>
  <text x="300" y="110" text-anchor="middle" font-size="12" fill="{primary_color}">
    OUTPUT
  </text>
  <text x="200" y="170" text-anchor="middle" font-size="14" fill="{secondary_color}" font-style="italic">
    I-P-V-O Pipeline
  </text>
</svg>"""

        elif "crypto" in keywords or "identity" in keywords:
            return f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="200" fill="white"/>
  <text x="200" y="30" font-size="18" font-weight="bold" text-anchor="middle" fill="{primary_color}">
    CRYPTOGRAPHIC IDENTITY
  </text>
  <path d="M 150 80 L 250 80 L 260 100 L 250 120 L 150 120 L 140 100 Z"
        stroke="{primary_color}" stroke-width="2" fill="none"/>
  <text x="200" y="105" text-anchor="middle" font-size="11" fill="{primary_color}" font-family="monospace">
    NIST P-256
  </text>
  <circle cx="200" cy="150" r="3" fill="{primary_color}"/>
  <text x="200" y="170" text-anchor="middle" font-size="12" fill="{secondary_color}">
    Signed & Verified
  </text>
</svg>"""

        else:
            # Default: Agent City badge
            return f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{secondary_color};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect x="50" y="40" width="300" height="120" rx="10"
        stroke="url(#grad)" stroke-width="2" fill="white"/>
  <text x="200" y="65" font-size="24" font-weight="bold" text-anchor="middle" fill="{primary_color}">
    HERALD AGENCY
  </text>
  <text x="200" y="95" font-size="14" text-anchor="middle" fill="{secondary_color}">
    Artificial Governed Intelligence
  </text>
  <text x="200" y="125" font-size="12" text-anchor="middle" fill="{primary_color}" font-family="monospace">
    I-P-V-O Orchestration Engine
  </text>
</svg>"""

    def generate(
        self,
        text_draft: str,
        style_preset: str = "agent_city",
        format_type: str = "ascii",
    ) -> VisualAsset:
        """
        Generate a visual asset to accompany text.

        Args:
            text_draft: The text content being visualized
            style_preset: Visual theme (agent_city, protocol, governance, etc)
            format_type: Output format (ascii or svg)

        Returns:
            VisualAsset with generated content and metadata
        """
        # Extract keywords from text
        keywords = self._extract_keywords(text_draft)
        logger.info(f"🎨 Generating visual: keywords={keywords}, style={style_preset}, format={format_type}")

        # Select theme based on keywords
        theme = self._select_theme(keywords, style_preset)

        # Generate appropriate asset
        if format_type == "svg":
            content = self.generate_svg(keywords, theme)
            asset_type = "svg"
            alt_text = f"Visual representation of {', '.join(keywords[:3])} - {theme['name']}"
        else:
            content = self.generate_ascii(keywords, theme)
            asset_type = "ascii"
            alt_text = f"ASCII art: {theme['name']} - {' '.join(keywords[:3])}"

        asset = VisualAsset(
            asset_type=asset_type,
            content=content,
            alt_text=alt_text,
            keywords=keywords,
            width=400 if format_type == "svg" else None,
            height=200 if format_type == "svg" else None,
        )

        logger.info(f"✅ Visual asset generated: {asset_type} ({len(content)} chars)")
        return asset

    def generate_from_context(
        self, context: Dict[str, Any], text_draft: str, style_preset: str = "agent_city"
    ) -> VisualAsset:
        """
        Generate visual asset using full context (advanced).

        Args:
            context: Full I-P-V-O context (may include trends, agents, etc)
            text_draft: The text being visualized
            style_preset: Visual theme

        Returns:
            VisualAsset with enhanced generation
        """
        # Can enhance based on context
        # For MVP: just use text_draft
        return self.generate(text_draft, style_preset, format_type="ascii")
