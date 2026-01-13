"""Prompts Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7bd190f4"  # GenesisByte: parampara % 37 == 0

from .section_main import PromptEntry, PromptsConfig

__all__ = ["PromptsConfig", "PromptEntry"]
