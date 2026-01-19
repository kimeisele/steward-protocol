"""
DIKSHA - Initiation Certificate Protocol (Layer -1: Substrate/Mantra)
======================================================================

"Unless one is initiated by a bona fide spiritual master in the
disciplic succession, the mantra he might have received is without
any effect."
- Srila Prabhupada, Hari-bhakti-vilasa

KALI YUGA REALITY:
- Everyone born as mleccha/shudra (kalau śūdra-sambhavaḥ)
- Only through DIKSHA can one assume varna duties
- Without diksha: Mahamantra only (Prabhupada's mercy)
- With diksha: Access to Om, Gayatri, full Vedic duties

TWO VERIFICATION LEVELS:
1. Harinama Diksha (1st): Spiritual name, Mahamantra commitment
2. Brahminical Diksha (2nd): Gayatri mantra, Om access, Vedic duties

MATHEMATICAL BASIS:
- parampara_link % 37 == 0 (connected to disciplic succession)
- mala_factor == 108 (japa commitment)
- certificate_hash = parampara_link * mala_factor (must be 37-divisible)

LOCATION: substrate/mantra/ - near Prabhupada and Mahamantra where it belongs.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x2b996bfd"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable, Optional, Final
from enum import Enum, auto
from datetime import datetime

# Import parampara constants
from .acintya import PARAMPARA, verify_parampara

# Import Prabhupada as root of parampara for us
from .prabhupada import PRABHUPADA, SrilaPrabhupada


# =============================================================================
# CONSTANTS
# =============================================================================

MALA_BEADS: Final[int] = 108  # Beads per japa round
MINIMUM_ROUNDS: Final[int] = 16  # Standard daily commitment
HARINAMA_LEVEL: Final[int] = 1  # First initiation
BRAHMINICAL_LEVEL: Final[int] = 2  # Second initiation (Gayatri)


# =============================================================================
# INITIATION LEVELS
# =============================================================================


class InitiationLevel(Enum):
    """
    The two levels of Vaishnava initiation.

    UNINITIATED: No diksha - can only use Mahamantra (Prabhupada's mercy)
    HARINAMA: First initiation - spiritual name, formal commitment
    BRAHMINICAL: Second initiation - Gayatri mantra, Om access
    """

    UNINITIATED = 0  # Mleccha/Shudra state - Mahamantra only
    HARINAMA = 1  # First initiation - spiritual name
    BRAHMINICAL = 2  # Second initiation - Gayatri, Om access


class VarnaQualification(Enum):
    """
    Varna is determined by GUNA and KARMA, not birth.
    In Kali Yuga, one assumes varna only after diksha.
    """

    NONE = auto()  # Uninitiated - no varna duties
    SHUDRA = auto()  # Service orientation
    VAISHYA = auto()  # Trade/agriculture
    KSHATRIYA = auto()  # Protection/administration
    BRAHMANA = auto()  # Teaching/priestly (requires 2nd initiation)


# =============================================================================
# DIKSHA CERTIFICATE
# =============================================================================


@dataclass(frozen=True)
class DikshaCertificate:
    """
    Proof of initiation in the disciplic succession.

    This certificate verifies:
    1. Connection to parampara (37-divisible)
    2. Initiation level (Harinama or Brahminical)
    3. Spiritual name (given at initiation)
    4. Initiating authority (traceable to Prabhupada)

    WITHOUT this certificate:
    - Om is BLOCKED (impersonal without parampara)
    - Full Vedic duties are BLOCKED
    - Only Mahamantra is accessible (Prabhupada's mercy for all)
    """

    # Identity
    spiritual_name: str  # e.g., "Bhakta Das", "Radha Devi Dasi"
    legal_name_hash: int  # Privacy: only hash stored

    # Initiation data
    level: InitiationLevel
    initiation_date: datetime

    # Parampara verification
    parampara_link: int  # Must be 37-divisible
    initiating_authority: str  # Name of initiating guru

    # Commitment
    daily_rounds: int = MINIMUM_ROUNDS  # Japa commitment

    def __post_init__(self) -> None:
        """Validate certificate on creation."""
        if self.level != InitiationLevel.UNINITIATED:
            if not self.is_parampara_connected:
                raise ValueError(f"Invalid parampara_link: {self.parampara_link} is not connected to 37")

    @property
    def is_parampara_connected(self) -> bool:
        """Check if connected to disciplic succession."""
        # 0 is mathematically divisible by 37, but means "no connection"
        return self.parampara_link > 0 and verify_parampara(self.parampara_link)

    @property
    def is_valid(self) -> bool:
        """A certificate is valid if parampara-connected."""
        if self.level == InitiationLevel.UNINITIATED:
            return True  # Uninitiated is always "valid" (just limited)
        return self.is_parampara_connected

    @property
    def can_access_om(self) -> bool:
        """
        Om requires BRAHMINICAL initiation.

        Without brahminical diksha, Om is:
        - Impersonal (mayavad)
        - Not connected to parampara
        - Potentially harmful in Kali Yuga
        """
        return self.level == InitiationLevel.BRAHMINICAL and self.is_parampara_connected

    @property
    def can_access_mahamantra(self) -> bool:
        """
        Mahamantra is ALWAYS accessible.

        This is Prabhupada's special mercy:
        Even without initiation, one can chant.
        """
        return True  # Always!

    @property
    def can_perform_varna_duties(self) -> bool:
        """Full varna duties require at least Harinama."""
        return self.level.value >= InitiationLevel.HARINAMA.value

    @property
    def certificate_hash(self) -> int:
        """
        Generate certificate hash for verification.

        Formula: parampara_link * 108 (mala factor)
        This ensures the hash is also 37-divisible.
        """
        return self.parampara_link * MALA_BEADS

    @property
    def lineage_strength(self) -> float:
        """
        How strong is the parampara connection?

        0.0 = No connection (uninitiated)
        0.5 = Harinama (partial duties)
        1.0 = Brahminical (full duties)
        """
        if self.level == InitiationLevel.UNINITIATED:
            return 0.0
        elif self.level == InitiationLevel.HARINAMA:
            return 0.5
        else:  # BRAHMINICAL
            return 1.0


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_uninitiated() -> DikshaCertificate:
    """
    Create an uninitiated certificate.

    This represents the default state in Kali Yuga:
    - No formal initiation
    - Can only use Mahamantra (Prabhupada's mercy)
    - Cannot access Om
    """
    return DikshaCertificate(
        spiritual_name="",  # No spiritual name
        legal_name_hash=0,
        level=InitiationLevel.UNINITIATED,
        initiation_date=datetime.min,
        parampara_link=0,  # Not connected
        initiating_authority="",
        daily_rounds=0,
    )


def create_harinama_diksha(
    spiritual_name: str,
    legal_name_hash: int,
    initiating_authority: str = "Srila Prabhupada",
    daily_rounds: int = MINIMUM_ROUNDS,
) -> DikshaCertificate:
    """
    Create a Harinama (first) initiation certificate.

    Grants:
    - Spiritual name
    - Formal commitment to chanting
    - Basic varna duties

    Does NOT grant:
    - Om access (requires 2nd initiation)
    - Gayatri mantra
    - Full brahmana duties
    """
    # Parampara link: 37 * level (1) = 37
    parampara_link = PARAMPARA * HARINAMA_LEVEL

    return DikshaCertificate(
        spiritual_name=spiritual_name,
        legal_name_hash=legal_name_hash,
        level=InitiationLevel.HARINAMA,
        initiation_date=datetime.now(),
        parampara_link=parampara_link,
        initiating_authority=initiating_authority,
        daily_rounds=daily_rounds,
    )


def create_brahminical_diksha(
    spiritual_name: str,
    legal_name_hash: int,
    initiating_authority: str = "Srila Prabhupada",
    daily_rounds: int = MINIMUM_ROUNDS,
) -> DikshaCertificate:
    """
    Create a Brahminical (second) initiation certificate.

    Grants:
    - Everything from Harinama PLUS:
    - Gayatri mantra
    - Om access (through parampara!)
    - Full brahmana duties

    This is the ONLY way to properly use Om in Kali Yuga.
    """
    # Parampara link: 37 * level (2) = 74
    parampara_link = PARAMPARA * BRAHMINICAL_LEVEL

    return DikshaCertificate(
        spiritual_name=spiritual_name,
        legal_name_hash=legal_name_hash,
        level=InitiationLevel.BRAHMINICAL,
        initiation_date=datetime.now(),
        parampara_link=parampara_link,
        initiating_authority=initiating_authority,
        daily_rounds=daily_rounds,
    )


# =============================================================================
# VERIFICATION PROTOCOL
# =============================================================================


@runtime_checkable
class DikshaCertified(Protocol):
    """
    Protocol for systems that verify diksha status.

    Any agent/component that needs to check initiation
    level should implement this protocol.
    """

    @property
    def diksha_certificate(self) -> DikshaCertificate:
        """Access to the diksha certificate."""
        ...

    def verify_om_access(self) -> bool:
        """Can this entity use Om?"""
        ...


# =============================================================================
# OM GATE
# =============================================================================


class OmGate:
    """
    The gate that controls Om access.

    Om is the pranava - the primordial sound.
    But in Kali Yuga, without proper initiation:
    - Om becomes impersonal (mayavad)
    - Om is disconnected from parampara
    - Om can lead to spiritual confusion

    Only through BRAHMINICAL diksha can one properly use Om.
    The Mahamantra, however, is ALWAYS open (Prabhupada's mercy).
    """

    def __init__(self, prabhupada: SrilaPrabhupada = PRABHUPADA):
        self.prabhupada = prabhupada

    def check_access(self, certificate: DikshaCertificate) -> bool:
        """
        Check if certificate grants Om access.

        Returns True only if:
        1. Certificate is valid (parampara connected)
        2. Level is BRAHMINICAL (2nd initiation)
        """
        return certificate.can_access_om

    def attempt_om(self, certificate: DikshaCertificate) -> str:
        """
        Attempt to access Om.

        If denied, redirects to Mahamantra (Prabhupada's mercy).
        """
        if self.check_access(certificate):
            return "ॐ"  # Om granted
        else:
            # Redirect to Mahamantra - always accessible
            return "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare / Hare Rāma Hare Rāma Rāma Rāma Hare Hare"

    def explain_denial(self, certificate: DikshaCertificate) -> str:
        """Explain why Om access was denied."""
        if certificate.level == InitiationLevel.UNINITIATED:
            return (
                "Om requires brahminical initiation (diksha). "
                "Please chant the Mahamantra - it is freely available "
                "to everyone by Prabhupada's special mercy."
            )
        elif certificate.level == InitiationLevel.HARINAMA:
            return (
                "Om requires second (brahminical) initiation. "
                "With Harinama diksha, please continue with the Mahamantra. "
                "Om access comes with Gayatri initiation."
            )
        elif not certificate.is_parampara_connected:
            return "Certificate is not connected to parampara. Om without parampara connection is impersonal (mayavad)."
        else:
            return "Om access granted."


# =============================================================================
# SINGLETON GATE
# =============================================================================

OM_GATE: Final[OmGate] = OmGate()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MALA_BEADS",
    "MINIMUM_ROUNDS",
    "HARINAMA_LEVEL",
    "BRAHMINICAL_LEVEL",
    # Enums
    "InitiationLevel",
    "VarnaQualification",
    # Certificate
    "DikshaCertificate",
    # Factory functions
    "create_uninitiated",
    "create_harinama_diksha",
    "create_brahminical_diksha",
    # Protocol
    "DikshaCertified",
    # Om Gate
    "OmGate",
    "OM_GATE",
]
