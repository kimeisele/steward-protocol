"""Integrity Guard Plugin - Enforces the Law of the Land at boot."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x5e4a2bbc"  # GenesisByte: parampara % 37 == 0

from .plugin_main import IntegrityGuardPlugin

__all__ = ["IntegrityGuardPlugin"]
