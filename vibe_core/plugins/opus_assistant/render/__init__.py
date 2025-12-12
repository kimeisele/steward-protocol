"""
OPUS Render Module - Standalone OPUS.md generation.

OPUS-029 Migration: Replaced interface/renderers/opus/ with this module.
"""

from vibe_core.plugins.opus_assistant.render.opus_md_writer import (
    OpusMdWriter,
    write_opus_md,
)

__all__ = [
    "OpusMdWriter",
    "write_opus_md",
]
