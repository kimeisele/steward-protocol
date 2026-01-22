"""
SANKALPA - The Will Protocol.

SHASTRA: _seed.py defines SHARANAGATI[6] = "anukulyasya sankalpah"
(The acceptance of the favorable - the first step of surrender)

This is NOT ego-will (Ahankara). This is Dharma-will.
The system acts because Shastra dictates, not because it "wants".
NISHKAMA KARMA - Action without attachment.

ADVAITA: All execution goes through ChatProtocol.
Internal voice (Sankalpa) and external voice (User) enter the same gate.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xebbc13e9"

from .types import (
    MissionPriority,
    MissionStatus,
    SankalpaIntent,
    SankalpaMission,
    SankalpaResult,
    SankalpaStatus,
    SankalpaStrategy,
    SankalpaTrigger,
    StrategyFrequency,
    TriggerType,
)
from .will import (
    SankalpaOrchestrator,
    SankalpaPlanner,
    SankalpaRegistry,
    get_sankalpa,
    handle_sankalpa_query,
    get_sankalpa_status_for_chat,
)

__all__ = [
    # Types
    "MissionPriority",
    "MissionStatus",
    "SankalpaIntent",
    "SankalpaMission",
    "SankalpaResult",
    "SankalpaStatus",
    "SankalpaStrategy",
    "SankalpaTrigger",
    "StrategyFrequency",
    "TriggerType",
    # Logic
    "SankalpaOrchestrator",
    "SankalpaPlanner",
    "SankalpaRegistry",
    "get_sankalpa",
    "handle_sankalpa_query",
    "get_sankalpa_status_for_chat",
]
