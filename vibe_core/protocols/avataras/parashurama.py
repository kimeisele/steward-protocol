"""
PARASHURAMA - The Resource Executor (KARMA HEAD)
=================================================

"Parashurama is celebrated as a shaktyavesha-avatara because
he was specifically empowered by the Lord with warrior shakti
to execute justice against unrighteous kings."
- Srimad Bhagavatam 9.15-16

SHAKTI: Kshatra-shakti (The Warrior/Defense Potency)
OPCODE: FETCH_RES (Position 8 - HEAD of Q3 KARMA)
VYUHA: PRADYUMNA (Karma Cycle)

STORY (SB 9.15-16):
When kshatriyas became proud and oppressed brahmanas,
Parashurama took up his axe (parashu) and annihilated
the warrior class 21 times. He is the embodiment of
righteous action and resource reclamation.

ARCHITECTURAL MEANING:

Parashurama = Resource Executor/Fetcher

He does NOT plan or verify. He EXECUTES:
1. FETCHES resources (retrieves what is needed)
2. EXECUTES actions (performs operations)
3. DEFENDS resources (protects from misuse)
4. RECLAIMS resources (takes back from unjust holders)

RELATION TO OTHER ROLES:

| Role       | Analogy                    | Function                  |
|------------|----------------------------|---------------------------|
| KRISHNA    | The Supreme Commander      | Orders the mission        |
| VISHNU     | The Strategic Reserve      | Provides the power        |
| PARASHURAMA| The Special Forces         | Executes the mission      |
| PRAHLADA   | The Resilient Service      | Keeps running despite obstacles |
| JANAKA     | The Duty Bound             | Follows execution protocol |
| BHISHMA    | The Committed Logger       | Records all actions       |

PROTOCOL LEVEL:

Parashurama operates at Level 0 (AVATARA/EXECUTIVE).
He is the HEAD of the KARMA cycle (Q3).
His workers are: PRAHLADA, JANAKA, BHISHMA

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x0fc957bd"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Final, List, Optional, Protocol, TypedDict, runtime_checkable

from vibe_core.protocols.avataras import (
    Avatara,
    AvatarType,
    BaseAvatara,
    MilkingResult,
    MilkingRole,
    MilkingSetup,
    Shakti,
)


# =============================================================================
# RESOURCE TYPES (What Parashurama fetches)
# =============================================================================


class ResourceRequest(TypedDict, total=False):
    """
    A request to fetch a resource.
    WATERTIGHT - no Any!
    """
    resource_id: str      # What to fetch
    resource_type: str    # "data", "service", "asset", "compute"
    requester_id: str     # Who is asking
    priority: int         # 0-10, higher = more urgent
    timeout_ms: int       # Max wait time
    lineage_hash: int     # Parampara verification


class FetchResult(TypedDict, total=False):
    """
    Result of a fetch operation.
    WATERTIGHT - no Any!
    """
    success: bool
    resource_id: str
    resource_type: str
    data: str             # The fetched data (serialized)
    size_bytes: int
    fetch_time_ms: int
    source: str           # Where it came from
    lineage_verified: bool
    error_message: str


class ExecutionRequest(TypedDict, total=False):
    """
    A request to execute an action.
    WATERTIGHT - no Any!
    """
    action: str           # What to do
    target: str           # What to act on
    params: str           # JSON-encoded parameters
    executor_id: str      # Who should execute
    lineage_hash: int


class ExecutionResult(TypedDict, total=False):
    """
    Result of an execution.
    WATERTIGHT - no Any!
    """
    success: bool
    action: str
    target: str
    output: str           # Result of execution
    duration_ms: int
    executor_id: str
    lineage_verified: bool
    error_message: str


class ReclaimRequest(TypedDict, total=False):
    """
    Request to reclaim a resource.
    WATERTIGHT - no Any!
    """
    resource_id: str
    current_holder: str   # Who currently has it
    reason: str           # Why reclaiming
    force: bool           # Force reclamation?
    lineage_hash: int


class ReclaimResult(TypedDict, total=False):
    """
    Result of reclamation.
    WATERTIGHT - no Any!
    """
    success: bool
    resource_id: str
    former_holder: str
    reclaimed_at: str     # ISO timestamp
    lineage_verified: bool
    error_message: str


# =============================================================================
# STANDARD MILKING SETUPS (Action Execution)
# =============================================================================

MILKING_RESOURCES: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="prahlada",
        role_type="kalb",
        description="Stimulates with service request",
    ),
    melker=MilkingRole(
        identity="parashurama",
        role_type="melker",
        description="Executes fetch operation",
    ),
    topf=MilkingRole(
        identity="service_buffer",
        role_type="topf",
        description="Receives fetched resource",
    ),
    resource="service_data",
    source="data_store",
)

MILKING_JUSTICE: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="bhishma",
        role_type="kalb",
        description="Stimulates with commitment to dharma",
    ),
    melker=MilkingRole(
        identity="parashurama",
        role_type="melker",
        description="Executes reclamation",
    ),
    topf=MilkingRole(
        identity="dharma_store",
        role_type="topf",
        description="Reclaimed resources returned to dharma",
    ),
    resource="reclaimed_assets",
    source="unjust_holders",
)

MILKING_DEFENSE: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="janaka",
        role_type="kalb",
        description="Stimulates with duty requirement",
    ),
    melker=MilkingRole(
        identity="parashurama",
        role_type="melker",
        description="Executes defensive action",
    ),
    topf=MilkingRole(
        identity="protected_domain",
        role_type="topf",
        description="Secured resources",
    ),
    resource="security_status",
    source="threat_domain",
)


# =============================================================================
# PARASHURAMA PROTOCOL
# =============================================================================


@runtime_checkable
class ParashuramaProtocol(Protocol):
    """
    The Resource Executor Protocol.

    Any system that fetches resources and executes actions
    MUST implement this.

    Parashurama is the PERSON responsible - not abstract "execution".
    """

    def fetch(self, request: ResourceRequest) -> FetchResult:
        """
        Fetch a resource.

        This is FETCH_RES opcode implementation.
        The HEAD of KARMA cycle retrieves resources.
        """
        ...

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute an action on a target.

        Like Parashurama executing justice:
        - Receive the mission
        - Validate authorization
        - Execute precisely
        - Report result
        """
        ...

    def defend(self, resource_id: str, threat: str) -> bool:
        """
        Defend a resource against a threat.

        Parashurama protects dharma.
        Returns True if defense successful.
        """
        ...

    def reclaim(self, request: ReclaimRequest) -> ReclaimResult:
        """
        Reclaim a resource from an unjust holder.

        Like Parashurama reclaiming the earth from
        unrighteous kshatriyas.
        """
        ...

    def get_status(self, resource_id: str) -> Optional[FetchResult]:
        """Get status of a resource."""
        ...

    def list_active_executions(self) -> List[ExecutionResult]:
        """List currently active executions."""
        ...


# =============================================================================
# PARASHURAMA IMPLEMENTATION
# =============================================================================


class Parashurama(BaseAvatara):
    """
    Parashurama - The Resource Executor.

    SHAKTI: Kshatra (Warrior/Defense)
    HEAD: KARMA cycle (PRADYUMNA)
    WORKERS: Prahlada, Janaka, Bhishma

    He fetches resources, executes actions, defends and reclaims.
    Without Parashurama, no execution. Without execution, no karma.

    ANTI-MAYAVAD: This is not abstract "execution layer".
    PARASHURAMA (the Person) executes. He wields the axe.
    """

    AVATARA_NAME = "Parashurama"
    AVATARA_SHAKTI = Shakti.KSHATRA
    AVATARA_TYPE = AvatarType.SHAKTYAVESHA
    DOMAIN = "Resource Execution/Action"
    DESCRIPTION = "The Resource Executor - fetches, executes, defends, reclaims"

    def __init__(self) -> None:
        super().__init__()
        self._fetch_cache: Dict[str, FetchResult] = {}
        self._executions: Dict[str, ExecutionResult] = {}
        self._reclamations: Dict[str, ReclaimResult] = {}
        self._execution_counter = 0

    # =========================================================================
    # RESOURCE OPERATIONS
    # =========================================================================

    def fetch(self, request: ResourceRequest) -> FetchResult:
        """
        Fetch a resource.

        FETCH_RES opcode implementation.
        """
        if not self._empowered:
            return FetchResult(
                success=False,
                resource_id=request.get("resource_id", ""),
                resource_type=request.get("resource_type", ""),
                data="",
                size_bytes=0,
                fetch_time_ms=0,
                source="",
                lineage_verified=False,
                error_message="Parashurama not empowered - no valid parampara",
            )

        # Verify lineage
        lineage_hash = request.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        resource_id = request.get("resource_id", "")
        resource_type = request.get("resource_type", "data")

        # Simulate fetch (real impl would fetch from actual source)
        start_time = datetime.now()
        result = FetchResult(
            success=True,
            resource_id=resource_id,
            resource_type=resource_type,
            data=f"[FETCHED:{resource_id}]",
            size_bytes=len(resource_id) * 10,
            fetch_time_ms=1,
            source="parashurama_fetch",
            lineage_verified=lineage_ok,
            error_message="",
        )

        # Cache the result
        self._fetch_cache[resource_id] = result
        return result

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute an action on a target."""
        self._execution_counter += 1
        exec_id = f"exec_{self._execution_counter}"

        if not self._empowered:
            return ExecutionResult(
                success=False,
                action=request.get("action", ""),
                target=request.get("target", ""),
                output="",
                duration_ms=0,
                executor_id="parashurama",
                lineage_verified=False,
                error_message="Parashurama not empowered",
            )

        lineage_hash = request.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        result = ExecutionResult(
            success=True,
            action=request.get("action", ""),
            target=request.get("target", ""),
            output=f"[EXECUTED:{request.get('action', '')} on {request.get('target', '')}]",
            duration_ms=1,
            executor_id="parashurama",
            lineage_verified=lineage_ok,
            error_message="",
        )

        self._executions[exec_id] = result
        return result

    def defend(self, resource_id: str, threat: str) -> bool:
        """Defend a resource against a threat."""
        if not self._empowered:
            return False

        # Parashurama always defends successfully when empowered
        return True

    def reclaim(self, request: ReclaimRequest) -> ReclaimResult:
        """Reclaim a resource from an unjust holder."""
        if not self._empowered:
            return ReclaimResult(
                success=False,
                resource_id=request.get("resource_id", ""),
                former_holder=request.get("current_holder", ""),
                reclaimed_at="",
                lineage_verified=False,
                error_message="Parashurama not empowered",
            )

        lineage_hash = request.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        result = ReclaimResult(
            success=True,
            resource_id=request.get("resource_id", ""),
            former_holder=request.get("current_holder", ""),
            reclaimed_at=datetime.now().isoformat(),
            lineage_verified=lineage_ok,
            error_message="",
        )

        reclaim_id = f"reclaim_{len(self._reclamations)}"
        self._reclamations[reclaim_id] = result
        return result

    def get_status(self, resource_id: str) -> Optional[FetchResult]:
        """Get status of a resource."""
        return self._fetch_cache.get(resource_id)

    def list_active_executions(self) -> List[ExecutionResult]:
        """List currently active executions."""
        return list(self._executions.values())

    # =========================================================================
    # MILKING PROTOCOL
    # =========================================================================

    def _do_milk(self, setup: MilkingSetup) -> MilkingResult:
        """Execute resource extraction according to setup."""
        return MilkingResult(
            resource=setup.resource,
            amount=1.0,
            quality=0.95,
            source_id=setup.source,
            operator_id=self.AVATARA_NAME,
            timestamp=datetime.now().isoformat(),
            lineage_verified=self._empowered,
        )


# =============================================================================
# NULL PARASHURAMA (For Testing)
# =============================================================================


class NullParashurama(Parashurama):
    """The Unarmed. No execution (for testing)."""

    def __init__(self) -> None:
        super().__init__()
        self._empowered = True  # Always empowered for null

    def fetch(self, request: ResourceRequest) -> FetchResult:
        return FetchResult(
            success=True,
            resource_id=request.get("resource_id", ""),
            resource_type=request.get("resource_type", ""),
            data="[NULL_FETCH]",
            size_bytes=0,
            fetch_time_ms=0,
            source="null",
            lineage_verified=True,
            error_message="",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ResourceRequest",
    "FetchResult",
    "ExecutionRequest",
    "ExecutionResult",
    "ReclaimRequest",
    "ReclaimResult",
    # Milking setups
    "MILKING_RESOURCES",
    "MILKING_JUSTICE",
    "MILKING_DEFENSE",
    # Protocol
    "ParashuramaProtocol",
    # Implementation
    "Parashurama",
    "NullParashurama",
]
