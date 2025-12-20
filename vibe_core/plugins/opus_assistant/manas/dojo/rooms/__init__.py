"""
Dojo Rooms - Multi-dimensional Training Space

OPUS-133: "Wie eine Pokemon-Arena mit verschiedenen Räumen."

The Dojo is not just a training ground - it's a multi-dimensional
learning space where MANAS can:

    Arena      - Practice decisions against scenarios
    Library    - Research and learn from external knowledge
    Mirror     - Inspect itself and find gaps
    Meditation - Practice Mantras through Japa (OPUS-140)

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
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/meditation.py
    required: true
-->
"""

from .arena import Arena
from .library import Library
from .meditation import (
    JapaResult,
    MantraState,
    MeditationRoom,
    MeditationSession,
    get_meditation_room,
)
from .mirror import Mirror

__all__ = [
    "Arena",
    "Library",
    "Mirror",
    # OPUS-140: Meditation Room
    "MeditationRoom",
    "MeditationSession",
    "MantraState",
    "JapaResult",
    "get_meditation_room",
]
