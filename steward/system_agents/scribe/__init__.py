"""SCRIBE Cartridge - Documentation Agent"""

# Lazy import to avoid circular dependencies when loading tools directly
def __getattr__(name):
    if name == 'ScribeCartridge':
        from .cartridge_main import ScribeCartridge
        return ScribeCartridge
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['ScribeCartridge']
