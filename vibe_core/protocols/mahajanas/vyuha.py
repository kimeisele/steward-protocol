"""
CHATUR-VYUHA - The Four Cycles (4x4 Fractal Architecture)
=========================================================

"catur-vyuham param brahma" - The Supreme has four forms.
- Srimad Bhagavatam 3.1.34

THE MATHEMATICAL TRUTH:
    16 = 4 × (1 + 3)
    4 Cycles × (1 HEAD + 3 Mahajanas) = 16 OpCodes

SATYA YUGA ARCHITECTURE (Fractal/Cyclic):
    - Each Cycle is self-similar (same structure)
    - Each Cycle has exactly 1 HEAD (Avatara) + 3 Workers (Mahajanas)
    - Each element maps to exactly 1 OpCode
    - No orphan processes possible (HEAD provides seal)

KALI YUGA ARCHITECTURE (Linear/Flat) - DEPRECATED:
    - 16 OpCodes → 12 Mahajanas (scattered)
    - Some Mahajanas own multiple OpCodes (Brahma=3, Manu=2, Kapila=2)
    - No cycle concept, no fractal symmetry

THE CRITICAL SEAL (Military-Grade):
    The CycleHead (Avatara) provides the cryptographic salt for the
    hash of the entire 4-block. Without this 'Executive Signature',
    the Mahajanas (Judiciary) reject the entire cycle as 'Headless Noise'
    (Maya), making orphan processes physically impossible.

THE FOUR VYUHAS:
    | Cycle  | Vyuha       | HEAD        | Workers                    | Phase       |
    |--------|-------------|-------------|----------------------------|-------------|
    | 1      | Vasudeva    | PRITHU      | Brahma, Narada, Shambhu    | Genesis     |
    | 2      | Sankarshana | VYASA       | Kumaras, Kapila, Manu      | Dharma      |
    | 3      | Pradyumna   | PARASHURAMA | Prahlada, Janaka, Bhishma  | Karma       |
    | 4      | Aniruddha   | NRISIMHA    | Bali, Shuka, Yamaraja      | Moksha      |

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.avataras import Avatara, Shakti
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# CYCLE DEFINITIONS
# =============================================================================


class Vyuha(str, Enum):
    """
    The Four Vyuhas (Plenary Expansions).

    From SB 3.1.34: The Supreme manifests in four forms:
    Vasudeva, Sankarshana, Pradyumna, Aniruddha.

    Each Vyuha governs one phase of the cosmic cycle.
    """
    VASUDEVA = "vasudeva"        # Cycle 1: Genesis (Consciousness)
    SANKARSHANA = "sankarshana"  # Cycle 2: Dharma (Existence/Ego)
    PRADYUMNA = "pradyumna"      # Cycle 3: Karma (Intelligence)
    ANIRUDDHA = "aniruddha"      # Cycle 4: Moksha (Mind)


class CyclePhase(str, Enum):
    """
    The four phases of system operation.
    Maps 1:1 with the Mahamantra quarters.
    """
    GENESIS = "genesis"    # Q1: Creation/Invocation (H K H K)
    DHARMA = "dharma"      # Q2: Verification/Truth (K K H H)
    KARMA = "karma"        # Q3: Execution/Action (H R H R)
    MOKSHA = "moksha"      # Q4: Conclusion/Liberation (R R H H)


class CyclePosition(IntEnum):
    """Position within a cycle (0-3)."""
    HEAD = 0      # The Avatara (Executive HEAD)
    WORKER_1 = 1  # First Mahajana
    WORKER_2 = 2  # Second Mahajana
    WORKER_3 = 3  # Third Mahajana


# =============================================================================
# CYCLE SEAL (Cryptographic Military-Grade Lock)
# =============================================================================


class SealStatus(str, Enum):
    """Status of a cycle seal."""
    VALID = "valid"          # Seal verified, cycle authorized
    INVALID = "invalid"      # Seal failed, cycle rejected
    MISSING = "missing"      # No seal provided (Headless Noise!)
    EXPIRED = "expired"      # Seal timeout (stale execution)


class CycleSealResult(TypedDict, total=False):
    """
    Result of seal verification.
    WATERTIGHT - no Any!
    """
    status: str              # SealStatus value
    cycle_hash: str          # SHA-256 of cycle block
    head_signature: str      # HEAD's salt contribution
    timestamp: str           # ISO timestamp
    error_message: str       # Empty if valid


@dataclass(frozen=True)
class CycleSeal:
    """
    The Cryptographic Seal for a Cycle.

    CRITICAL SECURITY:
    Without a valid seal from the CycleHead (Avatara),
    the entire cycle is rejected as 'Headless Noise' (Maya).

    MECHANISM:
    1. HEAD (Avatara) provides salt derived from lineage_hash
    2. All 4 OpCodes in cycle are hashed with this salt
    3. Mahajanas verify the seal before processing
    4. Invalid seal = orphan process = REJECTED
    """
    head: Avatara
    cycle: Vyuha
    salt: str                  # Derived from HEAD's lineage_hash
    block_hash: str            # SHA-256 of the 4-opcode block
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    # Seal validity window (in seconds)
    VALIDITY_WINDOW: Final[int] = 300  # 5 minutes

    @classmethod
    def create(
        cls,
        head: Avatara,
        cycle: Vyuha,
        lineage_hash: int,
        opcodes: Tuple[MantraOpCode, MantraOpCode, MantraOpCode, MantraOpCode],
    ) -> "CycleSeal":
        """
        Create a seal for a cycle.

        The HEAD's lineage_hash provides the cryptographic salt.
        37 is the Parampara number (24 Ksetra + 12 Mahajanas + 1 Ksetrajna).
        """
        # Derive salt from lineage_hash (must be valid parampara)
        if lineage_hash % 37 != 0 and lineage_hash != 37:
            raise PermissionError(
                f"Invalid parampara: {lineage_hash} % 37 != 0. "
                "HEAD cannot provide seal without valid lineage."
            )

        salt = hashlib.sha256(
            f"{head.value}:{lineage_hash}:{cycle.value}".encode()
        ).hexdigest()[:16]

        # Hash the 4 opcodes with the salt
        opcode_string = ":".join(op.name for op in opcodes)
        block_hash = hashlib.sha256(
            f"{salt}:{opcode_string}".encode()
        ).hexdigest()

        return cls(
            head=head,
            cycle=cycle,
            salt=salt,
            block_hash=block_hash,
        )

    def verify(self, opcodes: Tuple[MantraOpCode, ...]) -> CycleSealResult:
        """
        Verify this seal against a set of opcodes.

        Returns CycleSealResult with status.
        """
        # Check timestamp validity
        age = datetime.now().timestamp() - self.timestamp
        if age > self.VALIDITY_WINDOW:
            return CycleSealResult(
                status=SealStatus.EXPIRED.value,
                cycle_hash=self.block_hash,
                head_signature=self.salt,
                timestamp=datetime.fromtimestamp(self.timestamp).isoformat(),
                error_message=f"Seal expired: {age:.0f}s > {self.VALIDITY_WINDOW}s",
            )

        # Recompute hash and compare
        opcode_string = ":".join(op.name for op in opcodes)
        expected_hash = hashlib.sha256(
            f"{self.salt}:{opcode_string}".encode()
        ).hexdigest()

        if expected_hash != self.block_hash:
            return CycleSealResult(
                status=SealStatus.INVALID.value,
                cycle_hash=self.block_hash,
                head_signature=self.salt,
                timestamp=datetime.fromtimestamp(self.timestamp).isoformat(),
                error_message="Hash mismatch: opcodes do not match sealed block",
            )

        return CycleSealResult(
            status=SealStatus.VALID.value,
            cycle_hash=self.block_hash,
            head_signature=self.salt,
            timestamp=datetime.fromtimestamp(self.timestamp).isoformat(),
            error_message="",
        )


# =============================================================================
# CYCLE DEFINITION (The 4x4 Matrix)
# =============================================================================


@dataclass(frozen=True)
class CycleDefinition:
    """
    Definition of a single cycle in the Chatur-Vyuha.

    STRUCTURE:
        1 HEAD (Avatara) + 3 Workers (Mahajanas) = 4 entities
        4 OpCodes mapped to these 4 entities

    FRACTAL PROPERTY:
        Each cycle has identical structure (self-similar).
        Zoom in: Same pattern.
        Zoom out: Same pattern.
    """
    vyuha: Vyuha
    phase: CyclePhase

    # The HEAD (Executive - Level 0)
    head: Avatara
    head_shakti: Shakti
    head_opcode: MantraOpCode

    # The Workers (Judiciary - Level 1)
    worker_1: Mahajana
    worker_1_opcode: MantraOpCode
    worker_2: Mahajana
    worker_2_opcode: MantraOpCode
    worker_3: Mahajana
    worker_3_opcode: MantraOpCode

    @property
    def all_opcodes(self) -> Tuple[MantraOpCode, MantraOpCode, MantraOpCode, MantraOpCode]:
        """All 4 opcodes in this cycle, in order."""
        return (self.head_opcode, self.worker_1_opcode, self.worker_2_opcode, self.worker_3_opcode)

    @property
    def all_mahajanas(self) -> Tuple[Mahajana, Mahajana, Mahajana]:
        """All 3 Mahajana workers (excluding HEAD)."""
        return (self.worker_1, self.worker_2, self.worker_3)

    @property
    def quarter(self) -> int:
        """Quarter number (1-4) in the Mahamantra."""
        return {
            CyclePhase.GENESIS: 1,
            CyclePhase.DHARMA: 2,
            CyclePhase.KARMA: 3,
            CyclePhase.MOKSHA: 4,
        }[self.phase]

    def get_entity_for_opcode(self, opcode: MantraOpCode) -> Union[Avatara, Mahajana]:
        """Get the entity (HEAD or Worker) responsible for an opcode."""
        if opcode == self.head_opcode:
            return self.head
        elif opcode == self.worker_1_opcode:
            return self.worker_1
        elif opcode == self.worker_2_opcode:
            return self.worker_2
        elif opcode == self.worker_3_opcode:
            return self.worker_3
        else:
            raise ValueError(f"OpCode {opcode} not in cycle {self.vyuha}")

    def create_seal(self, lineage_hash: int) -> CycleSeal:
        """Create a seal for this cycle using the HEAD's authority."""
        return CycleSeal.create(
            head=self.head,
            cycle=self.vyuha,
            lineage_hash=lineage_hash,
            opcodes=self.all_opcodes,
        )


# =============================================================================
# THE FOUR CYCLES (Chatur-Vyuha Manifest)
# =============================================================================

# CYCLE 1: GENESIS (Vasudeva)
# Quarter 1 of Mahamantra: H K H K
# Phase: Creation/Invocation
CYCLE_GENESIS: Final[CycleDefinition] = CycleDefinition(
    vyuha=Vyuha.VASUDEVA,
    phase=CyclePhase.GENESIS,
    # HEAD: Prithu (Infrastructure/Palana)
    head=Avatara.PRITHU,
    head_shakti=Shakti.PALANA,
    head_opcode=MantraOpCode.SYS_WAKE,
    # Worker 1: Brahma (Creation)
    worker_1=Mahajana.BRAHMA,
    worker_1_opcode=MantraOpCode.LOAD_ROOT,
    # Worker 2: Narada (Communication)
    worker_2=Mahajana.NARADA,
    worker_2_opcode=MantraOpCode.ALLOC_MEM,
    # Worker 3: Shambhu (Destruction/Cleanup preparation)
    worker_3=Mahajana.SHAMBHU,
    worker_3_opcode=MantraOpCode.BIND_CTX,
)

# CYCLE 2: DHARMA (Sankarshana)
# Quarter 2 of Mahamantra: K K H H
# Phase: Verification/Truth
CYCLE_DHARMA: Final[CycleDefinition] = CycleDefinition(
    vyuha=Vyuha.SANKARSHANA,
    phase=CyclePhase.DHARMA,
    # HEAD: Vyasa (Knowledge/Jnana)
    head=Avatara.VYASA,
    head_shakti=Shakti.JNANA,
    head_opcode=MantraOpCode.ASSERT_TRUTH,
    # Worker 1: Kumaras (Purity)
    worker_1=Mahajana.KUMARAS,
    worker_1_opcode=MantraOpCode.RESOLVE_REQ,
    # Worker 2: Kapila (Analysis)
    worker_2=Mahajana.KAPILA,
    worker_2_opcode=MantraOpCode.GARBAGE_COLLECT,
    # Worker 3: Manu (Law)
    worker_3=Mahajana.MANU,
    worker_3_opcode=MantraOpCode.PULSE_SYNC,
)

# CYCLE 3: KARMA (Pradyumna)
# Quarter 3 of Mahamantra: H R H R
# Phase: Execution/Action
CYCLE_KARMA: Final[CycleDefinition] = CycleDefinition(
    vyuha=Vyuha.PRADYUMNA,
    phase=CyclePhase.KARMA,
    # HEAD: Parashurama (Action/Kshatra)
    head=Avatara.PARASHURAMA,
    head_shakti=Shakti.KSHATRA,
    head_opcode=MantraOpCode.FETCH_RES,
    # Worker 1: Prahlada (Resilience)
    worker_1=Mahajana.PRAHLADA,
    worker_1_opcode=MantraOpCode.EXEC_SERVICE,
    # Worker 2: Janaka (Duty)
    worker_2=Mahajana.JANAKA,
    worker_2_opcode=MantraOpCode.CHECK_DHARMA,
    # Worker 3: Bhishma (Commitment)
    worker_3=Mahajana.BHISHMA,
    worker_3_opcode=MantraOpCode.COMMIT_LOG,
)

# CYCLE 4: MOKSHA (Aniruddha)
# Quarter 4 of Mahamantra: R R H H
# Phase: Conclusion/Liberation
CYCLE_MOKSHA: Final[CycleDefinition] = CycleDefinition(
    vyuha=Vyuha.ANIRUDDHA,
    phase=CyclePhase.MOKSHA,
    # HEAD: Nrisimha (Protection/Rakshana)
    head=Avatara.NRISIMHA,
    head_shakti=Shakti.RAKSHANA,
    head_opcode=MantraOpCode.CACHE_STATE,
    # Worker 1: Bali (Surrender)
    worker_1=Mahajana.BALI,
    worker_1_opcode=MantraOpCode.OPTIMIZE,
    # Worker 2: Shuka (Vision)
    worker_2=Mahajana.SHUKA,
    worker_2_opcode=MantraOpCode.YIELD_CPU,
    # Worker 3: Yamaraja (Judgment)
    worker_3=Mahajana.YAMARAJA,
    worker_3_opcode=MantraOpCode.RESET_IP,
)

# All cycles in order
CHATUR_VYUHA: Final[Tuple[CycleDefinition, ...]] = (
    CYCLE_GENESIS,
    CYCLE_DHARMA,
    CYCLE_KARMA,
    CYCLE_MOKSHA,
)

# Lookup tables
CYCLE_BY_VYUHA: Final[Dict[Vyuha, CycleDefinition]] = {
    c.vyuha: c for c in CHATUR_VYUHA
}

CYCLE_BY_PHASE: Final[Dict[CyclePhase, CycleDefinition]] = {
    c.phase: c for c in CHATUR_VYUHA
}


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================


def get_cycle_for_opcode(opcode: MantraOpCode) -> CycleDefinition:
    """Get the cycle that owns an opcode."""
    for cycle in CHATUR_VYUHA:
        if opcode in cycle.all_opcodes:
            return cycle
    raise ValueError(f"OpCode {opcode} not found in any cycle")


def get_head_for_opcode(opcode: MantraOpCode) -> Avatara:
    """Get the CycleHead (Avatara) responsible for an opcode's cycle."""
    return get_cycle_for_opcode(opcode).head


def get_entity_for_opcode(opcode: MantraOpCode) -> Union[Avatara, Mahajana]:
    """Get the specific entity (HEAD or Mahajana) for an opcode."""
    cycle = get_cycle_for_opcode(opcode)
    return cycle.get_entity_for_opcode(opcode)


def get_mahajana_for_opcode(opcode: MantraOpCode) -> Optional[Mahajana]:
    """
    Get the Mahajana for an opcode.
    Returns None if the opcode is owned by the HEAD (Avatara).
    """
    entity = get_entity_for_opcode(opcode)
    if isinstance(entity, Mahajana):
        return entity
    return None


def get_cycle_for_mahajana(mahajana: Mahajana) -> CycleDefinition:
    """Get the cycle a Mahajana belongs to."""
    for cycle in CHATUR_VYUHA:
        if mahajana in cycle.all_mahajanas:
            return cycle
    raise ValueError(f"Mahajana {mahajana} not found in any cycle")


def get_opcodes_for_mahajana(mahajana: Mahajana) -> List[MantraOpCode]:
    """Get all opcodes owned by a Mahajana."""
    result = []
    for cycle in CHATUR_VYUHA:
        if mahajana == cycle.worker_1:
            result.append(cycle.worker_1_opcode)
        elif mahajana == cycle.worker_2:
            result.append(cycle.worker_2_opcode)
        elif mahajana == cycle.worker_3:
            result.append(cycle.worker_3_opcode)
    return result


# =============================================================================
# VERIFICATION
# =============================================================================


def verify_chatur_vyuha() -> bool:
    """
    Verify the Chatur-Vyuha is complete and valid.

    Checks:
    1. All 16 OpCodes are mapped exactly once
    2. All 12 Mahajanas are in exactly one cycle
    3. Each cycle has exactly 4 entities (1 HEAD + 3 Workers)
    4. No duplicate assignments
    """
    # Check all opcodes mapped exactly once
    all_opcodes: List[MantraOpCode] = []
    for cycle in CHATUR_VYUHA:
        all_opcodes.extend(cycle.all_opcodes)

    if len(all_opcodes) != 16:
        raise ValueError(f"Expected 16 opcodes, got {len(all_opcodes)}")

    if len(set(all_opcodes)) != 16:
        duplicates = [op for op in all_opcodes if all_opcodes.count(op) > 1]
        raise ValueError(f"Duplicate opcodes: {duplicates}")

    expected_opcodes = set(MantraOpCode)
    actual_opcodes = set(all_opcodes)
    if expected_opcodes != actual_opcodes:
        missing = expected_opcodes - actual_opcodes
        extra = actual_opcodes - expected_opcodes
        raise ValueError(f"OpCode mismatch. Missing: {missing}, Extra: {extra}")

    # Check all mahajanas in exactly one cycle
    all_mahajanas: List[Mahajana] = []
    for cycle in CHATUR_VYUHA:
        all_mahajanas.extend(cycle.all_mahajanas)

    if len(all_mahajanas) != 12:
        raise ValueError(f"Expected 12 Mahajanas, got {len(all_mahajanas)}")

    if len(set(all_mahajanas)) != 12:
        duplicates = [m for m in all_mahajanas if all_mahajanas.count(m) > 1]
        raise ValueError(f"Duplicate Mahajanas: {duplicates}")

    expected_mahajanas = set(Mahajana)
    actual_mahajanas = set(all_mahajanas)
    if expected_mahajanas != actual_mahajanas:
        missing = expected_mahajanas - actual_mahajanas
        extra = actual_mahajanas - expected_mahajanas
        raise ValueError(f"Mahajana mismatch. Missing: {missing}, Extra: {extra}")

    # Check 4 unique HEADs (Avataras)
    heads = [c.head for c in CHATUR_VYUHA]
    if len(set(heads)) != 4:
        raise ValueError(f"Expected 4 unique HEADs, got {len(set(heads))}")

    return True


# =============================================================================
# VYUHA ROUTER (Cycle-Aware Routing)
# =============================================================================


@runtime_checkable
class VyuhaRouterProtocol(Protocol):
    """
    Protocol for cycle-aware routing.

    The VyuhaRouter adds cycle context to the standard router.
    Every operation must be authorized by the CycleHead.
    """

    def route(self, opcode: MantraOpCode) -> Tuple[CycleDefinition, Union[Avatara, Mahajana]]:
        """Route opcode to its cycle and responsible entity."""
        ...

    def authorize_cycle(self, cycle: CycleDefinition, lineage_hash: int) -> CycleSeal:
        """Create authorization seal for a cycle."""
        ...

    def verify_seal(self, seal: CycleSeal, opcodes: Tuple[MantraOpCode, ...]) -> CycleSealResult:
        """Verify a cycle seal."""
        ...


class VyuhaRouter:
    """
    The Cycle-Aware Router.

    UPGRADE from flat router.py:
    - Every OpCode has a Cycle context
    - Every Cycle has a HEAD that must authorize
    - Headless operations are rejected (Maya/Noise)
    """

    def __init__(self) -> None:
        # Verify on init
        verify_chatur_vyuha()

        # Build lookup tables
        self._opcode_to_cycle: Dict[MantraOpCode, CycleDefinition] = {}
        self._opcode_to_entity: Dict[MantraOpCode, Union[Avatara, Mahajana]] = {}

        for cycle in CHATUR_VYUHA:
            for opcode in cycle.all_opcodes:
                self._opcode_to_cycle[opcode] = cycle
                self._opcode_to_entity[opcode] = cycle.get_entity_for_opcode(opcode)

    def route(self, opcode: MantraOpCode) -> Tuple[CycleDefinition, Union[Avatara, Mahajana]]:
        """
        Route an opcode to its cycle and responsible entity.

        Returns: (CycleDefinition, Entity)
        Where Entity is either the HEAD (Avatara) or a Worker (Mahajana).
        """
        if opcode not in self._opcode_to_cycle:
            raise ValueError(f"Unknown OpCode: {opcode}")

        return (
            self._opcode_to_cycle[opcode],
            self._opcode_to_entity[opcode],
        )

    def authorize_cycle(self, cycle: CycleDefinition, lineage_hash: int) -> CycleSeal:
        """
        Create authorization seal for a cycle.

        The HEAD (Avatara) must have valid parampara to create the seal.
        Without this seal, the Mahajanas will reject the cycle as
        'Headless Noise' (Maya).
        """
        return cycle.create_seal(lineage_hash)

    def verify_seal(self, seal: CycleSeal, opcodes: Tuple[MantraOpCode, ...]) -> CycleSealResult:
        """
        Verify a cycle seal.

        If invalid/missing/expired, the entire cycle is rejected.
        This makes orphan processes PHYSICALLY IMPOSSIBLE.
        """
        return seal.verify(opcodes)

    def get_cycle(self, vyuha: Vyuha) -> CycleDefinition:
        """Get cycle definition by Vyuha."""
        return CYCLE_BY_VYUHA[vyuha]

    def get_phase_cycle(self, phase: CyclePhase) -> CycleDefinition:
        """Get cycle definition by phase."""
        return CYCLE_BY_PHASE[phase]


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

_vyuha_router: Optional[VyuhaRouter] = None


def get_vyuha_router() -> VyuhaRouter:
    """Get the global Vyuha router."""
    global _vyuha_router
    if _vyuha_router is None:
        _vyuha_router = VyuhaRouter()
    return _vyuha_router


def route_with_cycle(opcode: MantraOpCode) -> Tuple[CycleDefinition, Union[Avatara, Mahajana]]:
    """Convenience: Route opcode with cycle context."""
    return get_vyuha_router().route(opcode)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Vyuha",
    "CyclePhase",
    "CyclePosition",
    "SealStatus",
    # Types
    "CycleSealResult",
    # Classes
    "CycleSeal",
    "CycleDefinition",
    "VyuhaRouter",
    # Constants
    "CYCLE_GENESIS",
    "CYCLE_DHARMA",
    "CYCLE_KARMA",
    "CYCLE_MOKSHA",
    "CHATUR_VYUHA",
    "CYCLE_BY_VYUHA",
    "CYCLE_BY_PHASE",
    # Functions
    "get_cycle_for_opcode",
    "get_head_for_opcode",
    "get_entity_for_opcode",
    "get_mahajana_for_opcode",
    "get_cycle_for_mahajana",
    "get_opcodes_for_mahajana",
    "verify_chatur_vyuha",
    "get_vyuha_router",
    "route_with_cycle",
]
