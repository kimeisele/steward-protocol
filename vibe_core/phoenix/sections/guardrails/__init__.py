"""Guardrails Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xa85a60f0"  # GenesisByte: parampara % 37 == 0

from .section_main import GuardrailMode, GuardrailsConfig, UIFilesConfig

__all__ = ["GuardrailsConfig", "GuardrailMode", "UIFilesConfig"]
