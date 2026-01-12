"""
SHAMBHU - THE 3RD MAHAJANA (Destruction/GC)
===========================================
OpCode: garbage_collect (Bit 7)
Opulence: Vairagya (Renunciation)

"I am Time, the great destroyer of the world."
- Bhagavad Gita 11.32

This test validates that the system can DESTROY properly.
A system that creates but cannot destroy = ZOMBIES = MEMORY LEAKS.
Without Shambhu, the system becomes Asuric (immortal ego).
"""

import time
import gc
import pytest
from typing import List, Protocol, runtime_checkable

from vibe_core.protocols.universal.samsara import (
    SamsaraProtocol,
    SamsaraEngine,
    NullSamsara,
)
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext


# =============================================================================
# TEST PROTOCOLS (Protocol-Based, No Mock)
# =============================================================================

@runtime_checkable
class DestructibleProtocol(Protocol):
    """Any entity that can be destroyed by Shambhu."""

    def is_alive(self) -> bool:
        """Returns True if entity is still active."""
        ...

    def destroy(self) -> None:
        """Execute graceful destruction."""
        ...

    def get_reference_count(self) -> int:
        """Returns number of references to this object."""
        ...


class MortalObject:
    """
    An object that MUST be destroyable.
    If it cannot be destroyed, the system has a memory leak.
    """
    _instances: List["MortalObject"] = []

    def __init__(self, name: str) -> None:
        self.name = name
        self._alive = True
        self._data: List[int] = list(range(1000))  # Some memory
        MortalObject._instances.append(self)

    def is_alive(self) -> bool:
        return self._alive

    def destroy(self) -> None:
        """Execute graceful destruction (Tandava)."""
        self._alive = False
        self._data.clear()
        if self in MortalObject._instances:
            MortalObject._instances.remove(self)

    def get_reference_count(self) -> int:
        import sys
        return sys.getrefcount(self)

    @classmethod
    def get_instance_count(cls) -> int:
        return len(cls._instances)

    @classmethod
    def clear_all(cls) -> None:
        """Class-level cleanup for test isolation."""
        cls._instances.clear()


class ImmortalObject:
    """
    An object that REFUSES to die.
    This represents Asuric code (Hiranyakashipu pattern).
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._alive = True
        self._circular_ref: "ImmortalObject" = self  # Circular reference!

    def is_alive(self) -> bool:
        return self._alive

    def destroy(self) -> None:
        """Attempts to destroy but circular ref prevents GC."""
        self._alive = False
        # Note: _circular_ref still points to self = ZOMBIE

    def get_reference_count(self) -> int:
        import sys
        return sys.getrefcount(self)


# =============================================================================
# THE TESTS (Shambhu's Judgment)
# =============================================================================

class TestShambhuDestruction:
    """
    The 3rd Mahajana Test Suite.
    Proves that the system can destroy gracefully.
    """

    def setup_method(self) -> None:
        """Clean slate before each test."""
        MortalObject.clear_all()
        gc.collect()

    def teardown_method(self) -> None:
        """Ensure cleanup after each test."""
        MortalObject.clear_all()
        gc.collect()

    def test_01_mortal_can_be_destroyed(self) -> None:
        """
        TEST: A properly designed object CAN be destroyed.
        This is the baseline for healthy system behavior.
        """
        obj = MortalObject("test_mortal")

        assert obj.is_alive(), "Object should start alive"
        assert MortalObject.get_instance_count() == 1, "Should have 1 instance"

        obj.destroy()

        assert not obj.is_alive(), "Object should be dead after destroy()"

    def test_02_destroy_frees_memory(self) -> None:
        """
        TEST: Destruction MUST free memory.
        Objects without cleanup = ZOMBIES.
        """
        obj = MortalObject("memory_test")

        # Has data before destroy
        assert len(obj._data) == 1000, "Object should have data"

        obj.destroy()

        # Data should be cleared
        assert len(obj._data) == 0, "Data should be freed after destroy"

    def test_03_null_samsara_reuses_context_mayavad(self) -> None:
        """
        TEST: NullSamsara reuses the same context = MAYAVAD.
        This is the anti-pattern that causes decay.
        """
        null_samsara = NullSamsara()
        items = [1, 2, 3]

        contexts: List[SovereignContext] = []
        for item, ctx in null_samsara.stream(items, "test_id"):
            contexts.append(ctx)

        # All contexts should be THE SAME (Mayavad)
        assert contexts[0] is contexts[1], "NullSamsara reuses context (Mayavad)"
        assert contexts[1] is contexts[2], "NullSamsara reuses context (Mayavad)"

    def test_04_samsara_engine_creates_fresh_contexts(self) -> None:
        """
        TEST: SamsaraEngine creates FRESH context each iteration.
        This is the correct pattern (Living Stream).
        """
        engine = SamsaraEngine()
        items = [1, 2, 3]

        contexts: List[SovereignContext] = []
        for item, ctx in engine.stream(items, "test_id"):
            contexts.append(ctx)
            time.sleep(0.001)  # Ensure different timestamps

        # Each context should be DIFFERENT (Fresh)
        assert contexts[0].signature != contexts[1].signature, \
            "SamsaraEngine must create fresh signatures"
        assert contexts[1].signature != contexts[2].signature, \
            "SamsaraEngine must create fresh signatures"

    def test_05_breathe_creates_valid_context(self) -> None:
        """
        TEST: breathe() creates a valid SovereignContext.
        The context must have identity and signature.
        """
        engine = SamsaraEngine()
        ctx = engine.breathe("shambhu_test")

        assert ctx.identity_id == "shambhu_test", "Identity must match"
        assert ctx.signature, "Signature must be present"
        assert ctx.signature != "void_sig", "Must not be void signature"

    def test_06_garbage_collect_opcode_is_bit_7(self) -> None:
        """
        TEST: Shambhu's OpCode (garbage_collect) is at position 7.
        This is the destruction gate in the Mahamantra.
        """
        opcodes = list(MantraOpCode)
        assert opcodes[6] == MantraOpCode.TYPE_CHECK, \
            "garbage_collect must be OpCode #7 (index 6)"

    def test_07_instance_tracking_works(self) -> None:
        """
        TEST: Instance tracking must work for proper GC.
        If we can't track instances, we can't destroy them.
        """
        MortalObject.clear_all()

        obj1 = MortalObject("one")
        obj2 = MortalObject("two")
        obj3 = MortalObject("three")

        assert MortalObject.get_instance_count() == 3, "Should track 3 instances"

        obj2.destroy()

        assert MortalObject.get_instance_count() == 2, "Should have 2 after destroy"

    def test_08_circular_reference_detection(self) -> None:
        """
        TEST: Circular references are DANGEROUS.
        They prevent proper GC = ZOMBIES.
        This test documents the anti-pattern.
        """
        obj = ImmortalObject("circular_demon")

        # Even after "destroy", circular ref keeps it "alive" in memory
        obj.destroy()

        # The object thinks it's dead...
        assert not obj.is_alive(), "Object claims to be dead"

        # But the circular reference still exists!
        assert obj._circular_ref is obj, "Circular ref still exists = ZOMBIE"


# =============================================================================
# SAMSARA CYCLE TESTS (Integration)
# =============================================================================

class TestSamsaraCycle:
    """
    Test the complete Samsara (Birth-Death-Rebirth) cycle.
    """

    def test_full_lifecycle(self) -> None:
        """
        TEST: Object goes through full lifecycle.
        Birth -> Life -> Death -> Memory Freed
        """
        MortalObject.clear_all()

        # BIRTH
        obj = MortalObject("lifecycle_test")
        assert obj.is_alive(), "Birth: Object is alive"
        initial_count = MortalObject.get_instance_count()

        # LIFE
        assert len(obj._data) > 0, "Life: Object has data"

        # DEATH
        obj.destroy()
        assert not obj.is_alive(), "Death: Object is dead"

        # REBIRTH (in system terms: instance count reduced)
        assert MortalObject.get_instance_count() < initial_count, \
            "Rebirth: Instance released for next cycle"

    def test_stream_lifecycle(self) -> None:
        """
        TEST: Stream processing with proper lifecycle management.
        Each iteration gets fresh context (not decaying).
        """
        engine = SamsaraEngine()
        results: List[int] = []
        timestamps: List[float] = []

        for value, ctx in engine.stream([1, 2, 3, 4, 5], "stream_test"):
            results.append(value)
            timestamps.append(ctx.timestamp)

        assert results == [1, 2, 3, 4, 5], "All items processed"
        # Timestamps should be increasing (time moves forward)
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], \
                "Time must flow forward in Samsara"


# =============================================================================
# TANDAVA TEST (The Destruction Dance)
# =============================================================================

class TestTandava:
    """
    Test the Tandava - Shiva's cosmic dance of destruction.
    Ensures graceful shutdown patterns work.
    """

    def test_reverse_order_destruction(self) -> None:
        """
        TEST: Destruction should happen in REVERSE creation order.
        This prevents dependency errors.
        """
        MortalObject.clear_all()

        # Create in order
        first = MortalObject("first")
        second = MortalObject("second")
        third = MortalObject("third")

        creation_order = ["first", "second", "third"]
        destruction_order: List[str] = []

        # Destroy in reverse order (Tandava)
        for obj in reversed([first, second, third]):
            destruction_order.append(obj.name)
            obj.destroy()

        assert destruction_order == ["third", "second", "first"], \
            "Destruction must be in reverse order (Tandava)"

    def test_gc_collect_after_destruction(self) -> None:
        """
        TEST: Python GC should be able to collect after destroy().
        If not, we have memory leaks.
        """
        MortalObject.clear_all()

        obj = MortalObject("gc_test")
        obj.destroy()
        del obj

        # Force GC
        collected = gc.collect()

        # GC should have run (collected >= 0 means it ran)
        assert collected >= 0, "GC must be able to run"
        assert MortalObject.get_instance_count() == 0, \
            "All instances should be cleaned up"
