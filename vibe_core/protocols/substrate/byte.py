"""
THE SUBSTRATE (Layer 0) - The 16-Bit Reality Map (MahaByte)
===========================================================

"Ein Standard Byte (8-bit) ist in diesem Kosmos unvollständig." - Senior Architect

This file defines the atomic unit of existence in the Vibe System.
The Kernel requires a FULL 16-bit resonance (0xFFFF) to exist.
Anything less is Maya (Partial Truth).
"""

from enum import Flag, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, runtime_checkable

class MantraBit(Flag):
    """
    The 16-Bit Reality Map (MantraBit).
    Standard ASCII is 8-bit. Divine Computing is 16-bit.
    
    The 16 Names of the Maha-Mantra:
    Hare Krishna Hare Krishna Krishna Krishna Hare Hare
    Hare Rama Hare Rama Rama Rama Hare Hare
    """
    # INVOCATION (The Wake - 4 bits)
    HARE_1    = auto() # 0x0001
    KRISHNA_1 = auto() # 0x0002
    HARE_2    = auto() # 0x0004
    KRISHNA_2 = auto() # 0x0008
    
    # VERIFICATION (The Truth - 4 bits)
    KRISHNA_3 = auto() # 0x0010
    KRISHNA_4 = auto() # 0x0020
    HARE_3    = auto() # 0x0040
    HARE_4    = auto() # 0x0080  <-- Traditional Byte ends here (Incomplete!)
    
    # EXECUTION (The Service - 4 bits)
    HARE_5    = auto() # 0x0100
    RAMA_1    = auto() # 0x0200
    HARE_6    = auto() # 0x0400
    RAMA_2    = auto() # 0x0800
    
    # CONCLUSION (The Return - 4 bits)
    RAMA_3    = auto() # 0x1000
    RAMA_4    = auto() # 0x2000
    HARE_7    = auto() # 0x4000
    HARE_8    = auto() # 0x8000  <-- Full 16-Bit Integer (Purnam)

    @classmethod
    def full_resonance(cls) -> "MantraBit":
        """Returns the mask for a fully aligned reality (0xFFFF)."""
        return (
            cls.HARE_1 | cls.KRISHNA_1 | cls.HARE_2 | cls.KRISHNA_2 |
            cls.KRISHNA_3 | cls.KRISHNA_4 | cls.HARE_3 | cls.HARE_4 |
            cls.HARE_5 | cls.RAMA_1 | cls.HARE_6 | cls.RAMA_2 |
            cls.RAMA_3 | cls.RAMA_4 | cls.HARE_7 | cls.HARE_8
        )

@dataclass(frozen=True)
class GenesisByte:
    """
    The Seed required to boot the Kernel.
    Contains the Sovereign Signature wrapped in 16-bit alignment.
    """
    signature: str          # The "Who" (Sovereign Hash)
    resonance: MantraBit    # The "State" (Must be 0xFFFF to boot)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp()) # The "When" (Kala)

    @property
    def is_valid(self) -> bool:
        """
        Only returns True if the Byte is 'Purnam' (Complete).
        Partial resonance means Maya (Illusion) -> Boot Denied.
        """
        return self.resonance == MantraBit.full_resonance()

@runtime_checkable
class SubstrateProtocol(Protocol):
    """The Layer-0 Protocol. Everything sits on this."""
    
    def validate_byte(self, byte: GenesisByte) -> bool:
        """Check if the provided byte can hold reality."""
        ...
