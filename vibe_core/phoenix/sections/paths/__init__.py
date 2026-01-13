"""Paths Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xf64f25e9"  # GenesisByte: parampara % 37 == 0

from .section_main import (
    CartridgePathsConfig,
    DataPathsConfig,
    DocPathsConfig,
    KnowledgePathsConfig,
    PathsConfig,
    SystemPathsConfig,
)

__all__ = [
    "PathsConfig",
    "DataPathsConfig",
    "CartridgePathsConfig",
    "KnowledgePathsConfig",
    "SystemPathsConfig",
    "DocPathsConfig",
]
