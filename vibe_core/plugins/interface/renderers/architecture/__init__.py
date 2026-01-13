"""Architecture Renderer - Dynamic Mermaid diagrams from code."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xb0546732"  # GenesisByte: parampara % 37 == 0

from .renderer import ArchitectureRenderer, create_renderer

__all__ = ["ArchitectureRenderer", "create_renderer"]
