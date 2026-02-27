"""
MAHA PHONETICS - Substrate Sound Vibration Layer
"""

from .shabda import (
    SANSKRIT_PHONEME_MAP,
    ArticulationPoint,
    VibrationSignature,
    VoicingType,
    text_to_vibration,
    translate_via_vibration,
    vibration_to_sanskrit,
)

__all__ = [
    "ArticulationPoint",
    "VoicingType",
    "VibrationSignature",
    "SANSKRIT_PHONEME_MAP",
    "text_to_vibration",
    "vibration_to_sanskrit",
    "translate_via_vibration",
]
