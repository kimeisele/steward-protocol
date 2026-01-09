"""
GUNA PROTOCOL - The Physics of Quality
======================================

Refined Logic (Siddhanta):
- Material Objects: Mix of Sattva, Rajas, Tamas (Sum = 1.0). Visuddha = 0.
- Void/Maya: Sattva=0, Rajas=0, Tamas=0, Visuddha=0. (Existenzlos).
- Mantra/Krishna: Sattva=0, Rajas=0, Tamas=0, Visuddha=1.0 (Transzendental Saguna).
"""

from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable

ZERO = Decimal("0.0")
ONE = Decimal("1.0")

class GunaType(Enum):
    SATTVA = "sattva"           # Material Goodness
    RAJAS = "rajas"             # Material Passion
    TAMAS = "tamas"             # Material Ignorance
    VISUDDHA_SATTVA = "shuddha" # Pure Goodness (Transcendental Form)

@dataclass(frozen=True)
class GunaProfile:
    """
    The Quality Matrix.
    """
    sattva: Decimal
    rajas: Decimal
    tamas: Decimal
    visuddha: Decimal # The "S-Guna" (Spiritual Quality) factor
    
    @property
    def is_material(self) -> bool:
        return self.visuddha == ZERO and (self.sattva + self.rajas + self.tamas > ZERO)

    @property
    def is_transcendental(self) -> bool:
        """
        True if the object consists of Pure Goodness (Krishna Tattva).
        This is NOT 'Nirguna' in the sense of Void. It is 'Gunatita' (Beyond modes).
        """
        return self.visuddha > ZERO

    @property
    def is_void(self) -> bool:
        """The Mayavad Trap: No qualities at all."""
        return self.sattva == ZERO and self.rajas == ZERO and self.tamas == ZERO and self.visuddha == ZERO

    def __repr__(self):
        if self.is_transcendental:
            return f"🌟 VISUDDHA (Spiritually Potent: {self.visuddha:.2f})"
        if self.is_void:
            return "⚫ VOID (Mayavad)"
        return f"S:{self.sattva:.2f} R:{self.rajas:.2f} T:{self.tamas:.2f}"

@runtime_checkable
class GunaProtocol(Protocol):
    def get_guna_profile(self) -> GunaProfile:
        ...
