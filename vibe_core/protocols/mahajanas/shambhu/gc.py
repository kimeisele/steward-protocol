"""
GC - Garbage Collection Protocol
================================

OWNER: SHAMBHU (Lord Shiva)
POSITION: 3 (GENESIS Quarter)
OPCODE: GARBAGE_COLLECT

Shambhu destroys to make room for new creation.
This is garbage collection: reclaim unused resources.

SHASTRA BASIS:
    Shiva (Shambhu) is the destroyer in the trinity.
    But destruction is not evil - it's SEVA (service).
    Without destruction, there's no space for new creation.

    "Destruction is necessary for regeneration."

COLLECTION STRATEGIES:
    - MANUAL: Explicit cleanup calls
    - REFERENCE_COUNT: Track references, free when zero
    - MARK_SWEEP: Mark reachable, sweep unreachable
    - GENERATIONAL: Young/old generations

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x5e4e3909"  # GenesisByte: parampara % 37 == 0

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Protocol, Set, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.shambhu import (
    DestructionType,
    DestructionResult,
    DestructionState,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.SHAMBHU
LOTUS_POSITION: Final[int] = 3
LOTUS_QUARTER: Final[str] = "genesis"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.INIT_THREAD,  # GARBAGE_COLLECT
]


# =============================================================================
# GC STRATEGY
# =============================================================================


class GCStrategy(str, Enum):
    """Garbage collection strategies."""

    MANUAL = "manual"  # Explicit cleanup
    REFERENCE_COUNT = "ref_count"  # Reference counting
    MARK_SWEEP = "mark_sweep"  # Mark and sweep
    GENERATIONAL = "generational"  # Young/old generations


# =============================================================================
# MANAGED OBJECT
# =============================================================================


@dataclass
class ManagedObject:
    """An object tracked by the garbage collector."""

    object_id: str
    size_bytes: int
    created_at: datetime = field(default_factory=datetime.now)
    ref_count: int = 1
    generation: int = 0  # 0 = young, 1 = old
    marked: bool = False
    destructor: Optional[Callable[[], None]] = None


@dataclass(frozen=True)
class GCResult:
    """Result of a garbage collection cycle."""

    objects_collected: int
    bytes_freed: int
    duration_ms: int
    strategy: GCStrategy
    message: str


@dataclass
class GCStats:
    """GC statistics."""

    total_collections: int = 0
    total_objects_collected: int = 0
    total_bytes_freed: int = 0
    last_collection_time: Optional[str] = None
    managed_objects: int = 0
    managed_bytes: int = 0


# =============================================================================
# GC PROTOCOL
# =============================================================================


@runtime_checkable
class GCProtocol(Protocol):
    """
    The Garbage Collection Protocol - Shambhu's Cleanup.

    OWNER: Mahajana.SHAMBHU

    Reclaims unused resources:
    - Track managed objects
    - Detect unreachable objects
    - Free resources
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.SHAMBHU."""
        ...

    @property
    def strategy(self) -> GCStrategy:
        """Current GC strategy."""
        ...

    # Object Management
    def track(self, object_id: str, size_bytes: int, destructor: Optional[Callable[[], None]] = None) -> bool:
        """Start tracking an object."""
        ...

    def untrack(self, object_id: str) -> bool:
        """Stop tracking an object."""
        ...

    def add_reference(self, object_id: str) -> bool:
        """Increment reference count."""
        ...

    def release_reference(self, object_id: str) -> bool:
        """Decrement reference count."""
        ...

    # Collection
    def collect(self) -> GCResult:
        """Run garbage collection."""
        ...

    def collect_generation(self, generation: int) -> GCResult:
        """Collect specific generation."""
        ...

    # Stats
    def get_stats(self) -> GCStats:
        """Get GC statistics."""
        ...


# =============================================================================
# GC IMPLEMENTATION
# =============================================================================


class GarbageCollector:
    """
    Shambhu's Garbage Collector.

    OWNER: Mahajana.SHAMBHU

    Features:
    - Multiple collection strategies
    - Reference counting
    - Generational collection
    - Destructor callbacks
    """

    def __init__(self, strategy: GCStrategy = GCStrategy.REFERENCE_COUNT) -> None:
        """Initialize garbage collector."""
        self._strategy = strategy
        self._objects: Dict[str, ManagedObject] = {}
        self._roots: Set[str] = set()  # Root objects (always reachable)
        self._stats = GCStats()

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHAMBHU

    @property
    def strategy(self) -> GCStrategy:
        return self._strategy

    def track(
        self,
        object_id: str,
        size_bytes: int,
        destructor: Optional[Callable[[], None]] = None,
    ) -> bool:
        """Start tracking an object."""
        if object_id in self._objects:
            return False
        self._objects[object_id] = ManagedObject(
            object_id=object_id,
            size_bytes=size_bytes,
            destructor=destructor,
        )
        self._stats.managed_objects += 1
        self._stats.managed_bytes += size_bytes
        return True

    def untrack(self, object_id: str) -> bool:
        """Stop tracking an object (manual free)."""
        obj = self._objects.get(object_id)
        if obj is None:
            return False
        self._free_object(obj)
        return True

    def add_reference(self, object_id: str) -> bool:
        """Increment reference count."""
        obj = self._objects.get(object_id)
        if obj is None:
            return False
        obj.ref_count += 1
        return True

    def release_reference(self, object_id: str) -> bool:
        """Decrement reference count."""
        obj = self._objects.get(object_id)
        if obj is None:
            return False
        obj.ref_count -= 1

        # Auto-collect if ref count hits zero and using ref counting
        if self._strategy == GCStrategy.REFERENCE_COUNT and obj.ref_count <= 0:
            self._free_object(obj)

        return True

    def mark_root(self, object_id: str) -> bool:
        """Mark an object as a GC root."""
        if object_id not in self._objects:
            return False
        self._roots.add(object_id)
        return True

    def unmark_root(self, object_id: str) -> bool:
        """Unmark a GC root."""
        if object_id in self._roots:
            self._roots.remove(object_id)
            return True
        return False

    def collect(self) -> GCResult:
        """Run garbage collection based on strategy."""
        start_time = time.time()
        collected = 0
        freed = 0

        if self._strategy == GCStrategy.MANUAL:
            # Manual mode - do nothing
            pass

        elif self._strategy == GCStrategy.REFERENCE_COUNT:
            # Collect objects with zero references
            for obj_id in list(self._objects.keys()):
                obj = self._objects.get(obj_id)
                if obj and obj.ref_count <= 0 and obj_id not in self._roots:
                    freed += obj.size_bytes
                    self._free_object(obj)
                    collected += 1

        elif self._strategy == GCStrategy.MARK_SWEEP:
            # Mark phase
            for obj in self._objects.values():
                obj.marked = False
            for root_id in self._roots:
                self._mark(root_id)

            # Sweep phase
            for obj_id in list(self._objects.keys()):
                obj = self._objects.get(obj_id)
                if obj and not obj.marked:
                    freed += obj.size_bytes
                    self._free_object(obj)
                    collected += 1

        elif self._strategy == GCStrategy.GENERATIONAL:
            # Collect young generation first
            result = self.collect_generation(0)
            collected = result.objects_collected
            freed = result.bytes_freed

        duration_ms = int((time.time() - start_time) * 1000)

        self._stats.total_collections += 1
        self._stats.total_objects_collected += collected
        self._stats.total_bytes_freed += freed
        self._stats.last_collection_time = datetime.now().isoformat()

        return GCResult(
            objects_collected=collected,
            bytes_freed=freed,
            duration_ms=duration_ms,
            strategy=self._strategy,
            message=f"Collected {collected} objects, freed {freed} bytes",
        )

    def collect_generation(self, generation: int) -> GCResult:
        """Collect specific generation."""
        start_time = time.time()
        collected = 0
        freed = 0

        for obj_id in list(self._objects.keys()):
            obj = self._objects.get(obj_id)
            if obj and obj.generation == generation and obj.ref_count <= 0 and obj_id not in self._roots:
                freed += obj.size_bytes
                self._free_object(obj)
                collected += 1

        # Promote survivors
        for obj in self._objects.values():
            if obj.generation == generation:
                obj.generation = min(obj.generation + 1, 1)  # Max generation = 1

        return GCResult(
            objects_collected=collected,
            bytes_freed=freed,
            duration_ms=int((time.time() - start_time) * 1000),
            strategy=GCStrategy.GENERATIONAL,
            message=f"Gen {generation}: collected {collected} objects",
        )

    def _mark(self, object_id: str) -> None:
        """Mark an object and its references as reachable."""
        obj = self._objects.get(object_id)
        if obj is None or obj.marked:
            return
        obj.marked = True
        # In a real implementation, we'd trace references here

    def _free_object(self, obj: ManagedObject) -> None:
        """Free a managed object."""
        if obj.destructor:
            try:
                obj.destructor()
            except Exception:
                pass
        self._stats.managed_objects -= 1
        self._stats.managed_bytes -= obj.size_bytes
        self._objects.pop(obj.object_id, None)
        self._roots.discard(obj.object_id)

    def get_stats(self) -> GCStats:
        """Get GC statistics."""
        return GCStats(
            total_collections=self._stats.total_collections,
            total_objects_collected=self._stats.total_objects_collected,
            total_bytes_freed=self._stats.total_bytes_freed,
            last_collection_time=self._stats.last_collection_time,
            managed_objects=self._stats.managed_objects,
            managed_bytes=self._stats.managed_bytes,
        )

    def get_state(self) -> DestructionState:
        """Get destruction state."""
        return DestructionState(
            last_collection=self._stats.last_collection_time or "",
            items_pending=len([o for o in self._objects.values() if o.ref_count <= 0]),
            total_destroyed=self._stats.total_objects_collected,
            total_bytes_freed=self._stats.total_bytes_freed,
            is_destroyed=False,
            health="healthy",
        )


# =============================================================================
# NULL GC
# =============================================================================


class NullGC:
    """Null garbage collector - no collection."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHAMBHU

    @property
    def strategy(self) -> GCStrategy:
        return GCStrategy.MANUAL

    def track(self, object_id: str = "", size_bytes: int = 0, destructor: Optional[Callable[[], None]] = None) -> bool:
        return True

    def untrack(self, object_id: str = "") -> bool:
        return True

    def add_reference(self, object_id: str = "") -> bool:
        return True

    def release_reference(self, object_id: str = "") -> bool:
        return True

    def collect(self) -> GCResult:
        return GCResult(objects_collected=0, bytes_freed=0, duration_ms=0, strategy=GCStrategy.MANUAL, message="NullGC")

    def collect_generation(self, generation: int = 0) -> GCResult:
        return self.collect()

    def get_stats(self) -> GCStats:
        return GCStats()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    "GCStrategy",
    "ManagedObject",
    "GCResult",
    "GCStats",
    "GCProtocol",
    "GarbageCollector",
    "NullGC",
]
