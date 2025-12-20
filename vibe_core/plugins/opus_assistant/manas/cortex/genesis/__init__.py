"""
OPUS-158: Infrastructure Genesis - The Stadtamt Service

Auto-generates GAD-000 compliant infrastructure for new modules.

The Agent Virus Pattern:
    DETECT (ShrutaSense) -> CLASSIFY -> GENERATE -> WIRE -> REPLICATE

"Jedes Haus bekommt einen Briefkasten. Jede Strase ein Schild."
"""

from .classifier import InfrastructureClassifier, ModuleType
from .generator import InfrastructureGenerator

__all__ = [
    "InfrastructureClassifier",
    "InfrastructureGenerator",
    "ModuleType",
]
