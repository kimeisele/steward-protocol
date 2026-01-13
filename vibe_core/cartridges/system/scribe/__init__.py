"""SCRIBE Cartridge - Documentation Agent"""


# Lazy import to avoid circular dependencies when loading tools directly
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x192bfa27"  # GenesisByte: parampara % 37 == 0

def __getattr__(name):
    if name == "ScribeCartridge":
        from .cartridge_main import ScribeCartridge

        return ScribeCartridge
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["ScribeCartridge"]
