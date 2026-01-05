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

Phase 10 - The 7th NAGA:
- Prahlad (Resilience/Hardening)
"""

from vibe_core.naga.services.chitragupta import ChitraguptaService
from vibe_core.naga.services.kaliya import KaliyaService
from vibe_core.naga.services.narada import NaradaService
from vibe_core.naga.services.prahlad import PrahladService
from vibe_core.naga.services.sesha import SeshaService
from vibe_core.naga.services.takshaka import TakshakaService
from vibe_core.naga.services.vasuki import VasukiService

__all__ = [
    # Original 3
    "SeshaService",
    "VasukiService",
    "TakshakaService",
    # NSA Extension (Phase 9)
    "NaradaService",
    "KaliyaService",
    "ChitraguptaService",
    # Phase 10
    "PrahladService",
]
