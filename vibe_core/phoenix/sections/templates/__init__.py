"""Templates Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x861efbb3"  # GenesisByte: parampara % 37 == 0

from .section_main import TemplateEntry, TemplatesConfig

__all__ = ["TemplatesConfig", "TemplateEntry"]
