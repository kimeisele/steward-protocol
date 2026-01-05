"""
NAGA Services - The Invisible Guardians (NSA - NAGA Service Agency).

Original 3 (PROMPT.md Level 2):
- Sesha (Data/Truth)
- Vasuki (Network/Boundary)
- Takshaka (Security/Guard)

NSA Extension (Phase 9):
- Narada (Spy/Observer)
- Kaliya (Quarantine/Isolation)
- Chitragupta (Profiler/Behavioral)
"""

from vibe_core.naga.services.chitragupta import ChitraguptaService
from vibe_core.naga.services.kaliya import KaliyaService

# NSA Extension
from vibe_core.naga.services.narada import NaradaService
from vibe_core.naga.services.sesha import SeshaService
from vibe_core.naga.services.takshaka import TakshakaService
from vibe_core.naga.services.vasuki import VasukiService

__all__ = [
    # Original 3
    "SeshaService",
    "VasukiService",
    "TakshakaService",
    # NSA Extension
    "NaradaService",
    "KaliyaService",
    "ChitraguptaService",
]
