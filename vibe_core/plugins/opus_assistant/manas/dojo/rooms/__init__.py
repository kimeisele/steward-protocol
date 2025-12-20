"""
Dojo Rooms - Multi-dimensional Training Space

OPUS-133: "Wie eine Pokemon-Arena mit verschiedenen Räumen."

The Dojo is not just a training ground - it's a multi-dimensional
learning space where MANAS can:

    Arena   - Practice decisions against scenarios
    Library - Research and learn from external knowledge
    Mirror  - Inspect itself and find gaps

Each room serves a different purpose in MANAS's growth.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/arena.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py
    required: true
-->
"""

from .arena import Arena
from .library import Library
from .mirror import Mirror

__all__ = [
    "Arena",
    "Library",
    "Mirror",
]
