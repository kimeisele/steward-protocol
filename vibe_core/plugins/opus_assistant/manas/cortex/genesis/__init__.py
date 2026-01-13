"""
OPUS-158: Infrastructure Genesis - The Stadtamt Service

Auto-generates GAD-000 compliant infrastructure for new modules.

The Agent Virus Pattern:
    DETECT (ShrutaSense) -> CLASSIFY -> GENERATE -> WIRE -> REPLICATE

"Jedes Haus bekommt einen Briefkasten. Jede Strase ein Schild."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x8447279c"  # GenesisByte: parampara % 37 == 0

from vibe_core.genesis.types import ModuleType

from .classifier import InfrastructureClassifier
from .generator import InfrastructureGenerator

__all__ = [
    "InfrastructureClassifier",
    "InfrastructureGenerator",
    "ModuleType",
]
