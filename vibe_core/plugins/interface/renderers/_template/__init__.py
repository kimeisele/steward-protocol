"""Golden Template Renderer - Copy this folder for new renderers."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa2603d68"  # GenesisByte: parampara % 37 == 0

from .renderer import GoldenRenderer, create_renderer

__all__ = ["GoldenRenderer", "create_renderer"]
