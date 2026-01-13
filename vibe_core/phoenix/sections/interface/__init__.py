"""Interface Configuration Section.

UI rendering configuration - which files to render, intervals, document types.
Section ownership (LIVE/AI/HUMAN), layouts, view types, dependencies.
Fractal: Custom agents can add their own renderers via config.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xe413bcb9"  # GenesisByte: parampara % 37 == 0

from .section_main import (
    DependencyConfig,
    ElementTypeConfig,
    FooterConfig,
    FormattingConfig,
    HeaderConfig,
    InterfaceConfig,
    LayoutConfig,
    OwnershipTypeConfig,
    RendererConfig,
    SectionConfig,
    ViewTypeConfig,
    get_default_interface_config,
)

__all__ = [
    "InterfaceConfig",
    "RendererConfig",
    "SectionConfig",
    "HeaderConfig",
    "FooterConfig",
    "FormattingConfig",
    "ElementTypeConfig",
    "LayoutConfig",
    "OwnershipTypeConfig",
    "ViewTypeConfig",
    "DependencyConfig",
    "get_default_interface_config",
]
