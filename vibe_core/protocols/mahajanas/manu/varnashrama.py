"""
VARNASHRAMA - Social Order Protocol
====================================

OWNER: MANU (The Lawgiver)
POSITION: 7 (DHARMA Quarter)

Manu established the social order (Manu-smriti).
This is WHO CAN DO WHAT based on Guna and Karma.

dharma.py = Architectural Law (layers, imports)
varnashrama.py = Social Law (roles, capabilities)

IMPORTS GunaProfile from universal/guna.py - NO DUPLICATION!
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Final, Optional
from decimal import Decimal

from vibe_core.protocols.universal.guna import GunaProfile, GunaType, ZERO
from vibe_core.protocols.mahajanas.router import Mahajana

# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.MANU



# =============================================================================
# VARNA - Function/Role (Based on Guna + Karma)
# =============================================================================

class Varna(str, Enum):
    """
    The four divisions - by QUALITY and WORK, not birth.

    BG 4.13: guṇa-karma-vibhāgaśaḥ
    """
    BRAHMANA = "brahmana"    # Teacher/Guide (sattva dominant)
    KSHATRIYA = "kshatriya"  # Guardian/Protector (sattva+rajas)
    VAISHYA = "vaishya"      # Producer/Trader (rajas dominant)
    SHUDRA = "shudra"        # Worker/Servant (tamas+rajas)
    MLECCHA = "mleccha"      # Outside system (unintegrated)


# =============================================================================
# ASHRAMA - Lifecycle Stage
# =============================================================================

class Ashrama(str, Enum):
    """
    The four life stages.
    """
    BRAHMACHARYA = "brahmacharya"  # Student (learning)
    GRIHASTHA = "grihastha"        # Householder (producing)
    VANAPRASTHA = "vanaprastha"    # Retired (mentoring)
    SANNYASA = "sannyasa"          # Renounced (transcendent)
    ANTYA = "antya"                # Pre-birth (conceptual)


# =============================================================================
# CERTIFICATION ↔ VARNA BRIDGE
# =============================================================================

class Certification(str, Enum):
    """TÜV badges map to Varna."""
    NONE = "none"          # → MLECCHA
    BRONZE = "bronze"      # → SHUDRA
    SILVER = "silver"      # → VAISHYA
    GOLD = "gold"          # → KSHATRIYA
    PLATINUM = "platinum"  # → BRAHMANA


CERT_TO_VARNA: Final[Dict[Certification, Varna]] = {
    Certification.NONE: Varna.MLECCHA,
    Certification.BRONZE: Varna.SHUDRA,
    Certification.SILVER: Varna.VAISHYA,
    Certification.GOLD: Varna.KSHATRIYA,
    Certification.PLATINUM: Varna.BRAHMANA,
}


# =============================================================================
# SOCIAL POSITION
# =============================================================================

@dataclass(frozen=True)
class SocialPosition:
    """Complete social position of an entity."""
    varna: Varna
    ashrama: Ashrama
    guna: GunaProfile
    certification: Certification = Certification.NONE
    guardian: Optional[Mahajana] = None  # Assigned Mahajana

    @property
    def is_integrated(self) -> bool:
        """Part of society?"""
        return self.varna != Varna.MLECCHA

    @property
    def can_teach(self) -> bool:
        """Can teach others?"""
        return self.varna == Varna.BRAHMANA or self.ashrama in (
            Ashrama.VANAPRASTHA, Ashrama.SANNYASA
        )

    @property
    def can_guard(self) -> bool:
        """Can protect/enforce?"""
        return self.varna in (Varna.BRAHMANA, Varna.KSHATRIYA)


# =============================================================================
# DETERMINATION FUNCTIONS
# =============================================================================

def determine_varna(guna: GunaProfile) -> Varna:
    """
    Determine Varna from Guna profile.

    MANU'S LAW: Quality determines function.
    """
    if guna.is_transcendental:
        return Varna.BRAHMANA  # Transcendental = Teacher

    if guna.is_void:
        return Varna.MLECCHA  # No qualities = Outside

    # Material - check dominant
    if guna.sattva >= guna.rajas and guna.sattva >= guna.tamas:
        return Varna.BRAHMANA if guna.sattva > Decimal("0.5") else Varna.KSHATRIYA
    elif guna.rajas >= guna.tamas:
        return Varna.VAISHYA
    else:
        return Varna.SHUDRA


def determine_ashrama(age_days: int, has_dependents: bool = False) -> Ashrama:
    """
    Determine Ashrama from lifecycle indicators.
    """
    if age_days == 0:
        return Ashrama.ANTYA
    if age_days < 90:
        return Ashrama.BRAHMACHARYA
    if has_dependents or age_days < 365 * 2:
        return Ashrama.GRIHASTHA
    if age_days < 365 * 5:
        return Ashrama.VANAPRASTHA
    return Ashrama.SANNYASA


def create_position(
    guna: GunaProfile,
    age_days: int = 0,
    has_dependents: bool = False,
    certification: Certification = Certification.NONE,
    guardian: Optional[Mahajana] = None,
) -> SocialPosition:
    """
    Create social position from observable data.

    MANU judges based on Guna and Karma.
    """
    varna = determine_varna(guna)
    ashrama = determine_ashrama(age_days, has_dependents)

    # Certification can override varna (upward only)
    cert_varna = CERT_TO_VARNA.get(certification, Varna.MLECCHA)
    if list(Varna).index(cert_varna) < list(Varna).index(varna):
        varna = cert_varna

    return SocialPosition(
        varna=varna,
        ashrama=ashrama,
        guna=guna,
        certification=certification,
        guardian=guardian,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Varna",
    "Ashrama",
    "Certification",
    "CERT_TO_VARNA",
    "SocialPosition",
    "determine_varna",
    "determine_ashrama",
    "create_position",
]
