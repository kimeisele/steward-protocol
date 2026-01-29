"""
SAMSKARA PROTOCOL - The Transformation Ritual
==============================================

Owner: YAMARAJA (Judgment/Audit)
OpCode: RESET_IP (Transformation gate)

"Every wild protocol must face Yamaraja before entering the Kingdom."

Samskara = The 16 Hindu rituals of transformation (birth to death).
16 Samskaras = 16-bit Mahamantra. Not coincidence.

MIGRATION IS JUDGMENT:
- The wild protocol "dies" (leaves unowned state)
- Yamaraja judges: Is it GAD-000 compliant?
- If MERCY (chants) → enters Mahajana folder
- If DENY → must be purified first

THE AJAMIL EXCEPTION APPLIES:
Even if a protocol fails GAD-000, if it chants the Holy Name,
Yamaraja grants MERCY. The protocol can be migrated with
a purification TODO marker.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xcab0452c"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol, ProtocolState


# =============================================================================
# CONSTANTS
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.YAMARAJA

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.AUDIT_SEAL,  # Transformation gate
]


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================


class SamskaraType(str, Enum):
    """
    The 16 Samskaras mapped to protocol lifecycle.
    Each corresponds to a Mahamantra bit.
    """

    # QUARTER 1: GENESIS (Before Birth)
    GARBHADHANA = "garbhadhana"  # 1. Conception - Protocol idea
    PUMSAVANA = "pumsavana"  # 2. Fetus protection - Initial design
    SIMANTONNAYANA = "simantonnayana"  # 3. Hair parting - API definition
    JATAKARMA = "jatakarma"  # 4. Birth - First implementation

    # QUARTER 2: DHARMA (Childhood)
    NAMAKARANA = "namakarana"  # 5. Naming - Protocol naming
    NISHKRAMANA = "nishkramana"  # 6. First outing - First test
    ANNAPRASHANA = "annaprashana"  # 7. First food - First integration
    CHUDAKARANA = "chudakarana"  # 8. Head shaving - Cleanup

    # QUARTER 3: KARMA (Youth)
    KARNAVEDHA = "karnavedha"  # 9. Ear piercing - Listen to feedback
    VIDYARAMBHA = "vidyarambha"  # 10. Learning begins - Documentation
    UPANAYANA = "upanayana"  # 11. Sacred thread - GAD-000 audit
    VEDARAMBHA = "vedarambha"  # 12. Veda study - Deep review

    # QUARTER 4: MOKSHA (Maturity)
    KESHANTA = "keshanta"  # 13. First shave - Production ready
    SAMAVARTANA = "samavartana"  # 14. Graduation - Migration complete
    VIVAHA = "vivaha"  # 15. Marriage - Mahajana binding
    ANTYESHTI = "antyeshti"  # 16. Last rites - Wild protocol death


class MigrationStatus(str, Enum):
    """Status of a protocol migration."""

    WILD = "wild"  # Not yet migrated
    JUDGING = "judging"  # Under Yamaraja's review
    PURIFYING = "purifying"  # Needs cleanup (ATONE verdict)
    MIGRATING = "migrating"  # In transit
    BLESSED = "blessed"  # NAGA blessed, in folder
    REJECTED = "rejected"  # Failed, needs major work
    MERCY = "mercy"  # Failed but chants - gets in anyway


class WildProtocol(TypedDict, total=False):
    """
    A wild protocol awaiting migration.
    WATERTIGHT - no Any!
    """

    path: str  # File path
    name: str  # Protocol name
    target_mahajana: str  # Mahajana.value
    status: str  # MigrationStatus.value
    gad_score: float  # 0.0 to 1.0
    has_chanting: bool  # Does it call chant()?
    has_owner: bool  # Does it have OWNER constant?
    has_watertight: bool  # No Any types?
    samskara_stage: str  # SamskaraType.value
    discovered_at: str  # ISO timestamp
    judged_at: str  # ISO timestamp (empty if not judged)
    migrated_at: str  # ISO timestamp (empty if not migrated)


class MigrationVerdict(TypedDict, total=False):
    """
    Yamaraja's verdict on a protocol migration.
    WATERTIGHT - no Any!
    """

    protocol_path: str
    verdict: str  # "allow", "deny", "atone", "mercy"
    reason: str
    required_samskaras: List[str]  # SamskaraType values needed
    target_path: str  # Where it should go
    chanting_detected: bool
    gad_compliant: bool


class SamskaraState(TypedDict, total=False):
    """
    Full state of the Samskara system.
    WATERTIGHT - no Any!
    """

    protocol_name: str
    owner: str
    is_chanting: bool
    wild_count: int
    judging_count: int
    purifying_count: int
    migrating_count: int
    blessed_count: int
    rejected_count: int
    mercy_count: int
    total_migrated: int
    health: str


class MigrationManifest(TypedDict, total=False):
    """
    Complete migration manifest.
    WATERTIGHT - no Any!
    """

    version: str
    created_at: str
    updated_at: str
    wild_protocols: List[WildProtocol]
    completed_migrations: List[str]  # Paths of migrated protocols
    pending_verdicts: List[MigrationVerdict]


# =============================================================================
# SAMSKARA PROTOCOL
# =============================================================================


@runtime_checkable
class SamskaraProtocol(Protocol):
    """
    Protocol for managing wild protocol transformation/migration.

    Owner: YAMARAJA
    OpCode: RESET_IP (transformation gate)

    Every wild protocol must face Yamaraja's judgment before
    entering a Mahajana folder.

    WATERTIGHT - no Any types in interface!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.YAMARAJA."""
        ...

    # =========================================================================
    # Discovery (Find Wild Protocols)
    # =========================================================================

    def discover_wild(self, search_paths: List[str]) -> List[WildProtocol]:
        """
        Discover wild protocols in given paths.
        Returns list of WildProtocol entries.
        """
        ...

    def get_wild_protocols(self) -> List[WildProtocol]:
        """Get all known wild protocols."""
        ...

    def get_wild_by_status(self, status: MigrationStatus) -> List[WildProtocol]:
        """Get wild protocols by status."""
        ...

    # =========================================================================
    # Judgment (Yamaraja's Domain)
    # =========================================================================

    def judge(self, protocol_path: str) -> MigrationVerdict:
        """
        Judge a wild protocol.
        Returns Yamaraja's verdict.

        THE AJAMIL EXCEPTION: If protocol chants, verdict is MERCY
        even if GAD-000 fails.
        """
        ...

    def check_gad_compliance(self, protocol_path: str) -> float:
        """
        Check GAD-000 compliance score.
        Returns 0.0 to 1.0.
        """
        ...

    def check_chanting(self, protocol_path: str) -> bool:
        """
        Check if protocol calls chant() or has Mahamantra heartbeat.
        THE AJAMIL EXCEPTION applies here.
        """
        ...

    def identify_mahajana(self, protocol_path: str) -> Optional[Mahajana]:
        """
        Semantically identify which Mahajana should own this protocol.
        Returns None if unclear.
        """
        ...

    # =========================================================================
    # Transformation (The Samskaras)
    # =========================================================================

    def begin_samskara(
        self,
        protocol_path: str,
        samskara_type: SamskaraType,
    ) -> bool:
        """
        Begin a specific samskara for a protocol.
        Returns True if samskara started.
        """
        ...

    def complete_samskara(
        self,
        protocol_path: str,
        samskara_type: SamskaraType,
    ) -> bool:
        """
        Complete a samskara.
        Returns True if completed successfully.
        """
        ...

    def get_required_samskaras(self, protocol_path: str) -> List[SamskaraType]:
        """
        Get list of samskaras needed before migration.
        """
        ...

    # =========================================================================
    # Migration (The Actual Move)
    # =========================================================================

    def migrate(
        self,
        protocol_path: str,
        target_mahajana: Mahajana,
        target_name: str,
    ) -> bool:
        """
        Migrate a wild protocol to a Mahajana folder.
        Returns True if migration successful.

        REQUIRES: Verdict of ALLOW or MERCY.
        """
        ...

    def rollback(self, protocol_path: str) -> bool:
        """
        Rollback a failed migration.
        Returns True if rollback successful.
        """
        ...

    # =========================================================================
    # Manifest Management
    # =========================================================================

    def get_manifest(self) -> MigrationManifest:
        """Get the full migration manifest."""
        ...

    def save_manifest(self) -> bool:
        """Save manifest to disk."""
        ...

    def get_state(self) -> SamskaraState:
        """Get current state. WATERTIGHT."""
        ...


# =============================================================================
# OWNED PROTOCOL WRAPPER
# =============================================================================


class SamskaraOwnedProtocol(OwnedProtocol):
    """
    OwnedProtocol wrapper for Samskara.

    Allows Samskara to:
    - Be owned by YAMARAJA
    - Chant the Mahamantra
    - Pass GAD-000 audits
    - Be traceable to source
    """

    OWNER = Mahajana.YAMARAJA
    OPCODES = list(OWNED_OPCODES)
    PROTOCOL_NAME = "samskara"
    DESCRIPTION = "Protocol Migration - The 16 Transformations"

    def __init__(self, samskara: SamskaraProtocol) -> None:
        super().__init__()
        self._samskara = samskara

    def get_state(self) -> ProtocolState:
        """Return current state. WATERTIGHT - no Any!"""
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
        )

    @property
    def samskara(self) -> SamskaraProtocol:
        """Access the underlying samskara protocol."""
        return self._samskara


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullSamskara:
    """
    Null implementation for testing.
    No actual migration - just tracking.
    """

    def __init__(self) -> None:
        self._wild: List[WildProtocol] = []
        self._verdicts: List[MigrationVerdict] = []
        self._migrated: List[str] = []

    @property
    def owner(self) -> Mahajana:
        return Mahajana.YAMARAJA

    def discover_wild(self, search_paths: List[str] = None) -> List[WildProtocol]:
        return []

    def get_wild_protocols(self) -> List[WildProtocol]:
        return self._wild

    def get_wild_by_status(self, status: MigrationStatus = None) -> List[WildProtocol]:
        return [w for w in self._wild if w.get("status") == status.value]

    def judge(self, protocol_path: str = "") -> MigrationVerdict:
        # Null always grants MERCY (Ajamil Exception in full force)
        return MigrationVerdict(
            protocol_path=protocol_path,
            verdict="mercy",
            reason="NullSamskara grants mercy to all",
            required_samskaras=[],
            target_path="",
            chanting_detected=True,
            gad_compliant=True,
        )

    def check_gad_compliance(self, protocol_path: str = "") -> float:
        return 1.0  # Perfect compliance in null mode

    def check_chanting(self, protocol_path: str = "") -> bool:
        return True  # Assume chanting

    def identify_mahajana(self, protocol_path: str = "") -> Optional[Mahajana]:
        return None  # Unknown

    def begin_samskara(
        self,
        protocol_path: str = "",
        samskara_type: SamskaraType = None,
    ) -> bool:
        return True

    def complete_samskara(
        self,
        protocol_path: str = "",
        samskara_type: SamskaraType = None,
    ) -> bool:
        return True

    def get_required_samskaras(self, protocol_path: str = "") -> List[SamskaraType]:
        return []

    def migrate(
        self,
        protocol_path: str = "",
        target_mahajana: Mahajana = None,
        target_name: str = "",
    ) -> bool:
        self._migrated.append(protocol_path)
        return True

    def rollback(self, protocol_path: str = "") -> bool:
        if protocol_path in self._migrated:
            self._migrated.remove(protocol_path)
            return True
        return False

    def get_manifest(self) -> MigrationManifest:
        return MigrationManifest(
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            wild_protocols=self._wild,
            completed_migrations=self._migrated,
            pending_verdicts=self._verdicts,
        )

    def save_manifest(self) -> bool:
        return True

    def get_state(self) -> SamskaraState:
        return SamskaraState(
            protocol_name="samskara",
            owner="yamaraja",
            is_chanting=False,
            wild_count=len(self._wild),
            judging_count=0,
            purifying_count=0,
            migrating_count=0,
            blessed_count=len(self._migrated),
            rejected_count=0,
            mercy_count=0,
            total_migrated=len(self._migrated),
            health="pristine",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OWNER",
    "OWNED_OPCODES",
    # Enums
    "SamskaraType",
    "MigrationStatus",
    # Types (WATERTIGHT)
    "WildProtocol",
    "MigrationVerdict",
    "SamskaraState",
    "MigrationManifest",
    # Protocol
    "SamskaraProtocol",
    # Owned wrapper
    "SamskaraOwnedProtocol",
    # Null implementation
    "NullSamskara",
]
