"""
MAHA PHONETICS - Substrate Sound Vibration Layer
"""

from .shabda import (
    ArticulationPoint,
    VoicingType,
    VibrationSignature,
    SANSKRIT_PHONEME_MAP,
    text_to_vibration,
    vibration_to_sanskrit,
    translate_via_vibration,
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
