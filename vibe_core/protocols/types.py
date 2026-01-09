from dataclasses import dataclass
from enum import IntEnum

class TranscendentalQuality(IntEnum):
    UNCONSCIOUS = 0
    MATERIAL = 10
    SPIRITUAL = 50
    INCONCEIVABLE_POTENCY = 56 # Acintya

@dataclass
class SovereignContext:
    identity: str
    tattva_level: TranscendentalQuality
