"""
PRITHU MAHARAJA - The Infrastructure Orchestrator
==================================================

"Prithu Maharaja is celebrated as a shaktyavesha-avatara because
he was specifically empowered by the Lord to manage the Earth
and extract resources for the welfare of the citizens."
— Srimad Bhagavatam 4.15.6

SHAKTI: Palana-shakti (The Ruling/Maintenance Potency)

STORY (SB 4.15-19):
When Vena (bad king) was killed, there was no qualified ruler.
The sages churned his arms and Prithu appeared.
The Earth, fearing Prithu's arrows, surrendered as a cow.
Prithu milked her for resources - grains, knowledge, etc.
He LEVELED the Earth (made it usable) and ESTABLISHED cities.

ARCHITECTURAL MEANING:

Prithu = Infrastructure Orchestrator

He does NOT write business logic. He:
1. LEVELS the substrate (formats disk, allocates memory)
2. MILKS resources (extracts from substrate for services)
3. ESTABLISHES structure (creates directories, namespaces)
4. GOVERNS access (quota management, rate limiting)

RELATION TO OTHER ROLES:

| Role       | Analogy                    | Function                  |
|------------|----------------------------|---------------------------|
| KRISHNA    | The Owner                  | Owns everything           |
| VISHNU     | The Hardware Vendor        | Provides the hardware     |
| PRITHU     | The Infrastructure Eng     | Configures, provisions    |
| MANU       | The Policy Writer          | Writes the rules          |
| YAMARAJA   | The Auditor                | Checks compliance         |
| JANAKA     | The Application Dev        | Writes the code           |

MILKING PATTERNS (from SB 4.18):

Prithu established different milking parties for different resources:

1. GRAINS (Basic Resources)
   - Kalb: Svayambhuva Manu (dharma stimulation)
   - Melker: Prithu (sovereign extraction)
   - Topf: Hand-cupped (direct allocation)

2. SOMA (Compute Power)
   - Kalb: Indra (performance demand)
   - Melker: Devas (service processes)
   - Topf: Golden vessel (privileged buffer)

3. VEDA (Knowledge/Config)
   - Kalb: Brihaspati (requirement specification)
   - Melker: Rishis (documentation)
   - Topf: Sruti/Smrti (persistent store)

4. FEAR (Error Handling)
   - Kalb: Yamaraja (judgment)
   - Melker: Yakshas/Rakshasas (error handlers)
   - Topf: Skull cup (error log)

PROTOCOL LEVEL:

Prithu operates at Level 0 (AVATARA/EXECUTIVE).
He interfaces with:
- Level -1 (SUBSTRATE): byte.py, substrate/__init__.py
- Level 1 (MAHAJANA): Gets audited by Yamaraja, lawful by Manu
- Level 2 (SERVICES): Provisions for Janaka's applications

FRACTAL SCALABILITY:

Prithu himself can be the KALB for a higher-level operation.
Example: Vishnu milks Prithu for "ruling energy".

This creates the chain:
KRISHNA → VISHNU → PRITHU → SERVICES → JIVAS

Each level can use the Milking Protocol to extract from the level below.
"""

from __future__ import annotations

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
# RESOURCE TYPES (What Prithu extracts)
# =============================================================================


class ResourceType(TypedDict, total=False):
    """
    A resource that can be allocated.
    WATERTIGHT - no Any!
    """

    name: str
    amount_total: float
    amount_used: float
    amount_available: float
    unit: str  # "bytes", "processes", "connections", etc.
    owner_id: str  # Sovereign who owns this allocation


class AllocationRequest(TypedDict, total=False):
    """
    Request to allocate resources.
    WATERTIGHT - no Any!
    """

    resource: str  # What resource
    amount: float  # How much
    requester_id: str  # Who is asking
    purpose: str  # Why they need it
    duration_seconds: float  # How long (0 = permanent)
    lineage_hash: int  # Parampara verification


class AllocationResult(TypedDict, total=False):
    """
    Result of an allocation request.
    WATERTIGHT - no Any!
    """

    granted: bool
    resource: str
    amount_granted: float
    allocation_id: str
    expires_at: str  # ISO format, or empty if permanent
    reason: str  # Why granted/denied
    lineage_verified: bool


# =============================================================================
# STANDARD MILKING SETUPS
# =============================================================================


# The four primary milking parties from SB 4.18
MILKING_GRAINS: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="svayambhuva_manu",
        role_type="kalb",
        description="Stimulates with dharmic demand (lawful request)",
    ),
    melker=MilkingRole(
        identity="prithu",
        role_type="melker",
        description="Performs sovereign extraction",
    ),
    topf=MilkingRole(
        identity="hand_buffer",
        role_type="topf",
        description="Direct allocation to requester",
    ),
    resource="memory",
    source="substrate",
)

MILKING_SOMA: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="indra",
        role_type="kalb",
        description="Stimulates with performance demand",
    ),
    melker=MilkingRole(
        identity="devas",
        role_type="melker",
        description="Service processes extract compute",
    ),
    topf=MilkingRole(
        identity="golden_vessel",
        role_type="topf",
        description="Privileged process buffer",
    ),
    resource="compute",
    source="cpu",
)

MILKING_VEDA: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="brihaspati",
        role_type="kalb",
        description="Stimulates with specification",
    ),
    melker=MilkingRole(
        identity="rishis",
        role_type="melker",
        description="Sages document and compile",
    ),
    topf=MilkingRole(
        identity="sruti",
        role_type="topf",
        description="Persistent knowledge store",
    ),
    resource="config",
    source="knowledge_base",
)

MILKING_FEAR: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="yamaraja",
        role_type="kalb",
        description="Stimulates with judgment/error",
    ),
    melker=MilkingRole(
        identity="rakshasas",
        role_type="melker",
        description="Error handlers extract info",
    ),
    topf=MilkingRole(
        identity="skull_cup",
        role_type="topf",
        description="Error log (retained for analysis)",
    ),
    resource="error_info",
    source="error_stream",
)


# =============================================================================
# PRITHU PROTOCOL
# =============================================================================


@runtime_checkable
class PrithuProtocol(Protocol):
    """
    The Infrastructure Orchestrator Protocol.

    Any system that manages infrastructure MUST implement this.
    Prithu is the PERSON responsible - not abstract "infrastructure".
    """

    def level_earth(self) -> bool:
        """
        Level the substrate (initialize infrastructure).

        Like Prithu leveling the Earth for cities:
        - Format/prepare storage
        - Initialize memory pools
        - Create directory structure
        - Establish quotas

        Returns True if successful.
        """
        ...

    def allocate(self, request: AllocationRequest) -> AllocationResult:
        """
        Allocate resources from the substrate.

        This is the primary MILKING operation.
        Extracts resources according to request.
        """
        ...

    def deallocate(self, allocation_id: str) -> bool:
        """
        Return resources to the substrate.

        Resources flow back to the Earth.
        """
        ...

    def get_resource_status(self, resource: str) -> Optional[ResourceType]:
        """
        Get current status of a resource.

        How much is total, used, available?
        """
        ...

    def list_allocations(self, owner_id: Optional[str] = None) -> List[AllocationResult]:
        """
        List active allocations.

        If owner_id provided, filter by owner.
        """
        ...

    def establish_quota(
        self,
        owner_id: str,
        resource: str,
        max_amount: float,
        lineage_hash: int,
    ) -> bool:
        """
        Establish a quota for an owner.

        Prithu GOVERNS access - this sets limits.
        Requires valid parampara for authorization.
        """
        ...


# =============================================================================
# PRITHU IMPLEMENTATION
# =============================================================================


class Prithu(BaseAvatara):
    """
    Prithu Maharaja - The Infrastructure Orchestrator.

    SHAKTI: Palana (Ruling/Maintenance)

    He levels the earth, extracts resources, establishes structure.
    Without Prithu, no infrastructure. Without infrastructure, no services.

    ANTI-MAYAVAD: This is not abstract "infrastructure".
    PRITHU (the Person) manages it. He is the DevOps Maharaja.
    """

    AVATARA_NAME = "Prithu"
    AVATARA_SHAKTI = Shakti.PALANA
    AVATARA_TYPE = AvatarType.SHAKTYAVESHA
    DOMAIN = "Infrastructure/Resource Management"
    DESCRIPTION = "The Infrastructure Orchestrator - levels earth, milks resources"

    def __init__(self) -> None:
        super().__init__()
        self._resources: Dict[str, ResourceType] = {}
        self._allocations: Dict[str, AllocationResult] = {}
        self._quotas: Dict[str, Dict[str, float]] = {}  # owner_id -> resource -> max
        self._allocation_counter = 0
        self._earth_leveled = False

    # =========================================================================
    # INFRASTRUCTURE OPERATIONS
    # =========================================================================

    def level_earth(self) -> bool:
        """
        Level the substrate (initialize infrastructure).

        From SB 4.18: Prithu made the Earth level and smooth
        so that cities could be established.

        In code: Initialize resource pools, prepare storage.
        """
        if not self._empowered:
            return False

        # Initialize standard resource pools
        self._resources["memory"] = ResourceType(
            name="memory",
            amount_total=1_000_000_000.0,  # 1GB default
            amount_used=0.0,
            amount_available=1_000_000_000.0,
            unit="bytes",
            owner_id="substrate",
        )

        self._resources["compute"] = ResourceType(
            name="compute",
            amount_total=100.0,  # 100 units
            amount_used=0.0,
            amount_available=100.0,
            unit="units",
            owner_id="substrate",
        )

        self._resources["storage"] = ResourceType(
            name="storage",
            amount_total=10_000_000_000.0,  # 10GB default
            amount_used=0.0,
            amount_available=10_000_000_000.0,
            unit="bytes",
            owner_id="substrate",
        )

        self._resources["connections"] = ResourceType(
            name="connections",
            amount_total=1000.0,
            amount_used=0.0,
            amount_available=1000.0,
            unit="connections",
            owner_id="substrate",
        )

        self._earth_leveled = True
        return True

    def allocate(self, request: AllocationRequest) -> AllocationResult:
        """
        Allocate resources from the substrate.

        This is Prithu MILKING the Earth.
        """
        resource_name = request.get("resource", "")
        amount = request.get("amount", 0.0)
        requester_id = request.get("requester_id", "anonymous")
        lineage_hash = request.get("lineage_hash", 0)

        # Must be empowered
        if not self._empowered:
            return AllocationResult(
                granted=False,
                resource=resource_name,
                amount_granted=0.0,
                allocation_id="",
                reason="Prithu not empowered (no valid parampara)",
                lineage_verified=False,
            )

        # Must have leveled earth
        if not self._earth_leveled:
            return AllocationResult(
                granted=False,
                resource=resource_name,
                amount_granted=0.0,
                allocation_id="",
                reason="Earth not leveled (infrastructure not initialized)",
                lineage_verified=False,
            )

        # Resource must exist
        if resource_name not in self._resources:
            return AllocationResult(
                granted=False,
                resource=resource_name,
                amount_granted=0.0,
                allocation_id="",
                reason=f"Resource '{resource_name}' does not exist",
                lineage_verified=False,
            )

        # Check quota if set
        if requester_id in self._quotas:
            max_allowed = self._quotas[requester_id].get(resource_name, float("inf"))
            current_usage = self._get_usage_for_owner(requester_id, resource_name)
            if current_usage + amount > max_allowed:
                return AllocationResult(
                    granted=False,
                    resource=resource_name,
                    amount_granted=0.0,
                    allocation_id="",
                    reason=f"Quota exceeded: {current_usage + amount} > {max_allowed}",
                    lineage_verified=self.verify_parampara(lineage_hash),
                )

        # Check availability
        resource = self._resources[resource_name]
        available = resource.get("amount_available", 0.0)

        if amount > available:
            return AllocationResult(
                granted=False,
                resource=resource_name,
                amount_granted=0.0,
                allocation_id="",
                reason=f"Insufficient resources: {amount} > {available}",
                lineage_verified=self.verify_parampara(lineage_hash),
            )

        # Allocate!
        self._allocation_counter += 1
        allocation_id = f"alloc_{self._allocation_counter}_{requester_id}"

        # Update resource pool
        resource["amount_used"] = resource.get("amount_used", 0.0) + amount
        resource["amount_available"] = resource.get("amount_available", 0.0) - amount

        # Record allocation
        duration = request.get("duration_seconds", 0.0)
        expires = ""
        if duration > 0:
            expires = (
                datetime.now().isoformat()
            )  # Simplified - would add duration in real impl

        result = AllocationResult(
            granted=True,
            resource=resource_name,
            amount_granted=amount,
            allocation_id=allocation_id,
            expires_at=expires,
            reason=f"Allocated by Prithu for {request.get('purpose', 'unspecified')}",
            lineage_verified=self.verify_parampara(lineage_hash),
        )

        self._allocations[allocation_id] = result
        return result

    def deallocate(self, allocation_id: str) -> bool:
        """
        Return resources to the substrate.
        """
        if allocation_id not in self._allocations:
            return False

        allocation = self._allocations[allocation_id]
        resource_name = allocation.get("resource", "")
        amount = allocation.get("amount_granted", 0.0)

        if resource_name in self._resources:
            resource = self._resources[resource_name]
            resource["amount_used"] = resource.get("amount_used", 0.0) - amount
            resource["amount_available"] = resource.get("amount_available", 0.0) + amount

        del self._allocations[allocation_id]
        return True

    def get_resource_status(self, resource: str) -> Optional[ResourceType]:
        """Get current status of a resource."""
        return self._resources.get(resource)

    def list_allocations(self, owner_id: Optional[str] = None) -> List[AllocationResult]:
        """List active allocations."""
        if owner_id is None:
            return list(self._allocations.values())

        return [
            a
            for a in self._allocations.values()
            if owner_id in a.get("allocation_id", "")
        ]

    def establish_quota(
        self,
        owner_id: str,
        resource: str,
        max_amount: float,
        lineage_hash: int,
    ) -> bool:
        """
        Establish a quota for an owner.

        Only valid parampara can set quotas.
        """
        if not self.verify_parampara(lineage_hash):
            return False

        if owner_id not in self._quotas:
            self._quotas[owner_id] = {}

        self._quotas[owner_id][resource] = max_amount
        return True

    def _get_usage_for_owner(self, owner_id: str, resource: str) -> float:
        """Calculate total usage for an owner."""
        total = 0.0
        for allocation in self._allocations.values():
            if owner_id in allocation.get("allocation_id", ""):
                if allocation.get("resource") == resource:
                    total += allocation.get("amount_granted", 0.0)
        return total

    # =========================================================================
    # MILKING PROTOCOL IMPLEMENTATION
    # =========================================================================

    def _do_milk(self, setup: MilkingSetup) -> MilkingResult:
        """
        Execute a milking operation.

        Uses the Milking Protocol pattern from SB 4.18.
        """
        from datetime import datetime

        # Create allocation request from milking setup
        request = AllocationRequest(
            resource=setup.resource,
            amount=1.0,  # Default unit
            requester_id=setup.melker.identity,
            purpose=f"Milking by {setup.melker.identity} for {setup.topf.identity}",
            lineage_hash=37,  # Valid parampara
        )

        allocation = self.allocate(request)

        return MilkingResult(
            resource=setup.resource,
            amount=allocation.get("amount_granted", 0.0),
            quality=1.0 if allocation.get("granted") else 0.0,
            source_id=setup.source,
            operator_id=self.AVATARA_NAME,
            timestamp=datetime.now().isoformat(),
            lineage_verified=allocation.get("lineage_verified", False),
        )


# =============================================================================
# NULL PRITHU (For testing without infrastructure)
# =============================================================================


class NullPrithu:
    """
    The Anarchic State.
    All allocations permitted (for testing without governance).
    """

    AVATARA_NAME = "NullPrithu"

    def level_earth(self) -> bool:
        return True

    def allocate(self, request: AllocationRequest) -> AllocationResult:
        return AllocationResult(
            granted=True,
            resource=request.get("resource", ""),
            amount_granted=request.get("amount", 0.0),
            allocation_id="null_allocation",
            reason="NullPrithu permits all",
            lineage_verified=True,
        )

    def deallocate(self, allocation_id: str) -> bool:
        return True

    def get_resource_status(self, resource: str) -> Optional[ResourceType]:
        return ResourceType(
            name=resource,
            amount_total=float("inf"),
            amount_used=0.0,
            amount_available=float("inf"),
            unit="units",
            owner_id="null",
        )

    def list_allocations(self, owner_id: Optional[str] = None) -> List[AllocationResult]:
        return []

    def establish_quota(
        self,
        owner_id: str,
        resource: str,
        max_amount: float,
        lineage_hash: int,
    ) -> bool:
        return True


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_prithu: Optional[Prithu] = None


def get_prithu() -> Prithu:
    """Get the global Prithu instance."""
    global _prithu
    if _prithu is None:
        _prithu = Prithu()
    return _prithu


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ResourceType",
    "AllocationRequest",
    "AllocationResult",
    # Standard milking setups
    "MILKING_GRAINS",
    "MILKING_SOMA",
    "MILKING_VEDA",
    "MILKING_FEAR",
    # Protocol
    "PrithuProtocol",
    # Implementation
    "Prithu",
    "NullPrithu",
    # Singleton
    "get_prithu",
]
