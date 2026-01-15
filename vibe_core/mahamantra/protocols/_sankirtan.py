"""
SANKIRTAN PROTOCOL - The Mass Injection (Virus of Order)
========================================================

"sankirtana-pravartaka sri-krsna-caitanya"
"Lord Chaitanya is the initiator of the congregational chanting."

POSITION: Hare Krishna (Genesis Quarter) / Shuka (Log/Emission)?
Actually: It is the FLOOD. It transcends positions.

FUNCTION: DNA Injection, Header Stamping, Mass Awakening.

This protocol defines HOW the Mahamantra spreads itself into files.
It replaces ad-hoc regex substitution with a Sacred Rite.

LOCATION: vibe_core.mahamantra.protocols._sankirtan (THE LAW)
"""

from typing import Protocol, TypedDict, runtime_checkable, Optional
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.protocols._seed import PARAMPARA

class GenesisByte(TypedDict):
    """The Seal of Validity."""
    hash: str       # "0x..."
    vector: int     # Numeric value
    is_valid: bool  # vector % 37 == 0

class InjectionRequest(TypedDict):
    """Request to inject DNA into a host."""
    path: str
    mahajana: str
    position: int

@runtime_checkable
class SankirtanProtocol(PanchaTattvaProtocol, Protocol):
    """
    The Injection Protocol.
    Defines how the Holy Name enters a file.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Sankirtan Protocol",
            "nityananda": "Seed Protocol",
            "advaita": "Injection Logic",
            "gadadhara": "File Flow",
            "srivasa": "Permission Governance",
        }

    def calculate_genesis_byte(self, path: str, position: int) -> GenesisByte:
        """
        Calculate the GenesisByte (Seal).
        Must satisfy: hash % PARAMPARA == 0.
        """
        ...

    def inject(self, request: InjectionRequest) -> bool:
        """
        Inject the DNA header into the target.
        Must be idempotent.
        """
        ...

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GenesisByte",
    "InjectionRequest",
    "SankirtanProtocol",
]
