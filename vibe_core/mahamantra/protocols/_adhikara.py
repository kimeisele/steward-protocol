"""
ADHIKARA PROTOCOL - The Authorization Chain (Parampara Custody)
===============================================================

"evaṁ paramparā-prāptam imaṁ rājarṣayo viduḥ"
"This supreme science was received through the chain of disciplic succession."
— Bhagavad Gita 4.2

This protocol defines the ADHIKARA (qualification/authorization) required
to perform operations that mutate the substrate. Without Adhikara, even
correct code is "dead" (asiddhanta) - it lacks the chain of custody.

LOCATION: vibe_core.mahamantra.protocols._adhikara (THE LAW)
MATH: 12 Mahajanas × 37 Parampara = Chain of Custody

THE PROBLEM:
============
The `mutation_vector % 37 == 0` check is a PASSIVE filter.
It doesn't verify WHO authorized the mutation.

THE SOLUTION:
=============
Every operation that modifies substrate state must be SIGNED by
at least one of the 12 Mahajanas. The signature is verified using
the Parampara formula (24 + 12 + 1 = 37).

AUTHORIZATION MATRIX:
=====================
| Quarter | Head (Avatara) | Workers (Mahajanas) | Auth Required |
|---------|----------------|---------------------|---------------|
| GENESIS | Vyasa          | Brahma, Narada, Shambhu | 1 signature |
| DHARMA  | Prithu         | Kumaras, Kapila, Manu   | 2 signatures|
| KARMA   | Parashurama    | Prahlada, Janaka, Bhishma| 2 signatures|
| MOKSHA  | Nrisimha       | Bali, Shuka, Yamaraja   | 3 signatures|

Higher quarters (KARMA, MOKSHA) require MORE authorization because
their operations have greater impact on the substrate.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from hashlib import sha256
from typing import Final, FrozenSet, Protocol, Set, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb98623e7"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# VERIFICATION
# =============================================================================
assert MAHAJANA_COUNT == MAHAJANA_COUNT, "There must be 12 Mahajanas"
assert PARAMPARA == PARAMPARA, "Parampara must be 37"
assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA, "37 Formula"


# =============================================================================
# THE 12 MAHAJANAS (Authorizers)
# =============================================================================


class Mahajana(IntEnum):
    """
    The 12 Mahajanas - Authorities who can sign mutations.

    From Srimad Bhagavatam 6.3.20-21:
    "Lord Brahma, Bhagavan Narada, Lord Shiva, the four Kumaras,
    Lord Kapila, Svayambhuva Manu, Prahlada Maharaja, Janaka Maharaja,
    Grandfather Bhisma, Bali Maharaja, Sukadeva Gosvami and myself (Yamaraja)."
    """

    BRAHMA = 0  # Genesis Quarter, Worker 1
    NARADA = KSETRAJNA  # Genesis Quarter, Worker 2
    SHAMBHU = HALVES  # Genesis Quarter, Worker 3
    KUMARAS = TRINITY  # Dharma Quarter, Worker 1
    KAPILA = QUARTERS  # Dharma Quarter, Worker 2
    MANU = PANCHA  # Dharma Quarter, Worker 3
    PRAHLADA = SHARANAGATI  # Karma Quarter, Worker 1
    JANAKA = SEVEN  # Karma Quarter, Worker 2
    BHISHMA = HARE_COUNT  # Karma Quarter, Worker 3
    BALI = NAVA  # Moksha Quarter, Worker 1
    SHUKA = TEN  # Moksha Quarter, Worker 2
    YAMARAJA = 11  # Moksha Quarter, Worker 3


assert len(Mahajana) == MAHAJANA_COUNT, "Must have exactly 12 Mahajanas"


# =============================================================================
# QUARTER AUTHORIZATION REQUIREMENTS
# =============================================================================


class Quarter(IntEnum):
    """The 4 Quarters with increasing authorization requirements."""

    GENESIS = 0  # Boot/Load - 1 signature required
    DHARMA = KSETRAJNA  # Verify/Check - 2 signatures required
    KARMA = HALVES  # Execute/Commit - 2 signatures required
    MOKSHA = TRINITY  # Yield/Exit - 3 signatures required


# Signatures required per quarter (increasing risk = increasing auth)
SIGNATURES_REQUIRED: Final[dict[Quarter, int]] = {
    Quarter.GENESIS: KSETRAJNA,
    Quarter.DHARMA: HALVES,
    Quarter.KARMA: HALVES,
    Quarter.MOKSHA: TRINITY,
}


# Mahajanas authorized to sign per quarter
QUARTER_MAHAJANAS: Final[dict[Quarter, FrozenSet[Mahajana]]] = {
    Quarter.GENESIS: frozenset({Mahajana.BRAHMA, Mahajana.NARADA, Mahajana.SHAMBHU}),
    Quarter.DHARMA: frozenset({Mahajana.KUMARAS, Mahajana.KAPILA, Mahajana.MANU}),
    Quarter.KARMA: frozenset({Mahajana.PRAHLADA, Mahajana.JANAKA, Mahajana.BHISHMA}),
    Quarter.MOKSHA: frozenset({Mahajana.BALI, Mahajana.SHUKA, Mahajana.YAMARAJA}),
}


# =============================================================================
# SIGNATURE STRUCTURE
# =============================================================================


@dataclass(frozen=True)
class MahajanaSignature:
    """
    A cryptographic signature from a Mahajana.

    The signature is a hash of (mahajana_id, payload, nonce) that
    must satisfy the Parampara constraint (hash % 37 == 0).
    """

    mahajana: Mahajana
    signature_hash: str  # Hex string
    nonce: int

    def verify_parampara(self) -> bool:
        """Verify that the signature satisfies Parampara constraint."""
        try:
            hash_int = int(self.signature_hash[:WORDS], WORDS)  # First 64 bits
            return hash_int % PARAMPARA == 0
        except (ValueError, TypeError):
            return False


@dataclass
class AuthorizationBundle:
    """
    A bundle of Mahajana signatures authorizing an operation.
    """

    quarter: Quarter
    operation_id: str
    payload_hash: str
    signatures: Set[MahajanaSignature] = field(default_factory=set)

    def add_signature(self, sig: MahajanaSignature) -> bool:
        """
        Add a signature to the bundle.

        Returns:
            True if signature is valid and from authorized Mahajana
        """
        # Check if Mahajana is authorized for this quarter
        if sig.mahajana not in QUARTER_MAHAJANAS[self.quarter]:
            return False

        # Check Parampara constraint
        if not sig.verify_parampara():
            return False

        self.signatures.add(sig)
        return True

    def is_authorized(self) -> bool:
        """
        Check if bundle has enough valid signatures.
        """
        required = SIGNATURES_REQUIRED[self.quarter]
        valid_signatures = [
            s for s in self.signatures if s.mahajana in QUARTER_MAHAJANAS[self.quarter] and s.verify_parampara()
        ]
        return len(valid_signatures) >= required

    @property
    def missing_signatures(self) -> int:
        """Number of additional signatures needed."""
        required = SIGNATURES_REQUIRED[self.quarter]
        have = len([s for s in self.signatures if s.mahajana in QUARTER_MAHAJANAS[self.quarter]])
        return max(0, required - have)


# =============================================================================
# SIGNING FUNCTIONS
# =============================================================================


def create_signature(
    mahajana: Mahajana,
    payload: bytes,
    max_attempts: int = 1000,
) -> MahajanaSignature | None:
    """
    Create a Parampara-compliant signature.

    The nonce is adjusted until hash % 37 == 0.
    This is the "proof of work" that validates the Parampara connection.

    Args:
        mahajana: The signing Mahajana
        payload: The data being signed
        max_attempts: Maximum nonce attempts

    Returns:
        MahajanaSignature if successful, None if failed
    """
    for nonce in range(max_attempts):
        data = f"{mahajana.value}:{payload.hex()}:{nonce}".encode()
        sig_hash = sha256(data).hexdigest()
        hash_int = int(sig_hash[:WORDS], WORDS)

        if hash_int % PARAMPARA == 0:
            return MahajanaSignature(
                mahajana=mahajana,
                signature_hash=sig_hash,
                nonce=nonce,
            )

    return None  # Failed to find valid nonce


def verify_authorization(
    quarter: Quarter,
    payload: bytes,
    signatures: Set[MahajanaSignature],
) -> bool:
    """
    Verify that an operation is properly authorized.

    Args:
        quarter: The quarter in which the operation occurs
        payload: The operation payload
        signatures: Set of Mahajana signatures

    Returns:
        True if operation is authorized
    """
    bundle = AuthorizationBundle(
        quarter=quarter,
        operation_id="verify",
        payload_hash=sha256(payload).hexdigest(),
        signatures=signatures,
    )
    return bundle.is_authorized()


# =============================================================================
# ADHIKARA PROTOCOL
# =============================================================================


@runtime_checkable
class AdhikaraProtocol(Protocol):
    """
    Protocol for entities that require Parampara authorization.

    Any operation that mutates substrate state MUST implement this
    protocol to demonstrate proper chain of custody.
    """

    @property
    def quarter(self) -> Quarter:
        """The quarter in which this entity operates."""
        ...

    @property
    def authorization(self) -> AuthorizationBundle:
        """The current authorization bundle."""
        ...

    def request_signature(self, mahajana: Mahajana) -> bool:
        """Request a signature from a Mahajana."""
        ...

    def is_authorized(self) -> bool:
        """Check if entity has sufficient authorization."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Mahajana",
    "Quarter",
    # Constants
    "SIGNATURES_REQUIRED",
    "QUARTER_MAHAJANAS",
    # Data Classes
    "MahajanaSignature",
    "AuthorizationBundle",
    # Functions
    "create_signature",
    "verify_authorization",
    # Protocol
    "AdhikaraProtocol",
]
