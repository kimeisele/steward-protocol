"""Interface Configuration Section.

UI rendering configuration - which files to render, intervals, document types.
Fractal: Custom agents can add their own renderers via config.
"""

from .section_main import (
    DocumentTypeConfig,
    HeaderConfig,
    InterfaceConfig,
    RendererConfig,
    get_default_interface_config,
)

__all__ = [
    "InterfaceConfig",
    "RendererConfig",
    "HeaderConfig",
    "DocumentTypeConfig",
    "get_default_interface_config",
]
