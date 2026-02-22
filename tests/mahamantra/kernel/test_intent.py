"""
TESTS: kernel/intent.py - Mantra Intent System
===============================================

REAL TESTS for:
1. IntentType enum
2. IntentPriority enum
3. IntentStatus enum
4. MantraIntent dataclass
5. IntentResult dataclass
6. IntentQueue class
7. MantraKernel class
8. get_kernel, resolve, surrender functions
"""

import pytest
from vibe_core.mahamantra.kernel.intent import (
    IntentType,
    IntentPriority,
    IntentStatus,
    MantraIntent,
    IntentResult,
    IntentQueue,
    IntentResolver,
    MantraKernel,
    get_kernel,
    resolve,
    surrender,
)
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# IntentType Enum Tests
# =============================================================================


class TestIntentType:
    """Test IntentType enum."""

    def test_intent_type_read(self):
        """IntentType has READ."""
        assert IntentType.READ.value == "read"

    def test_intent_type_write(self):
        """IntentType has WRITE."""
        assert IntentType.WRITE.value == "write"

    def test_intent_type_transform(self):
        """IntentType has TRANSFORM."""
        assert IntentType.TRANSFORM.value == "transform"

    def test_intent_type_resolve(self):
        """IntentType has RESOLVE."""
        assert IntentType.RESOLVE.value == "resolve"

    def test_intent_type_bind(self):
        """IntentType has BIND."""
        assert IntentType.BIND.value == "bind"

    def test_intent_type_migrate(self):
        """IntentType has MIGRATE."""
        assert IntentType.MIGRATE.value == "migrate"

    def test_intent_type_wake(self):
        """IntentType has WAKE."""
        assert IntentType.WAKE.value == "wake"

    def test_intent_type_sync(self):
        """IntentType has SYNC."""
        assert IntentType.SYNC.value == "sync"

    def test_intent_type_heal(self):
        """IntentType has HEAL."""
        assert IntentType.HEAL.value == "heal"

    def test_intent_type_observe(self):
        """IntentType has OBSERVE."""
        assert IntentType.OBSERVE.value == "observe"

    def test_intent_type_surrender(self):
        """IntentType has SURRENDER."""
        assert IntentType.SURRENDER.value == "surrender"

    def test_intent_type_is_string_enum(self):
        """IntentType is a string enum."""
        assert isinstance(IntentType.READ.value, str)


# =============================================================================
# IntentPriority Enum Tests
# =============================================================================


class TestIntentPriority:
    """Test IntentPriority enum."""

    def test_intent_priority_critical(self):
        """IntentPriority has CRITICAL."""
        assert IntentPriority.CRITICAL is not None
        assert IntentPriority.CRITICAL.value == 1

    def test_intent_priority_high(self):
        """IntentPriority has HIGH."""
        assert IntentPriority.HIGH is not None
        assert IntentPriority.HIGH.value == 2

    def test_intent_priority_normal(self):
        """IntentPriority has NORMAL."""
        assert IntentPriority.NORMAL is not None
        assert IntentPriority.NORMAL.value == 3

    def test_intent_priority_low(self):
        """IntentPriority has LOW."""
        assert IntentPriority.LOW is not None
        assert IntentPriority.LOW.value == 4

    def test_intent_priority_background(self):
        """IntentPriority has BACKGROUND."""
        assert IntentPriority.BACKGROUND is not None
        assert IntentPriority.BACKGROUND.value == 5

    def test_intent_priority_ordering(self):
        """Priority values are ordered correctly."""
        assert IntentPriority.CRITICAL.value < IntentPriority.HIGH.value
        assert IntentPriority.HIGH.value < IntentPriority.NORMAL.value
        assert IntentPriority.NORMAL.value < IntentPriority.LOW.value
        assert IntentPriority.LOW.value < IntentPriority.BACKGROUND.value


# =============================================================================
# IntentStatus Enum Tests
# =============================================================================


class TestIntentStatus:
    """Test IntentStatus enum."""

    def test_intent_status_pending(self):
        """IntentStatus has PENDING."""
        assert IntentStatus.PENDING.value == "pending"

    def test_intent_status_resolving(self):
        """IntentStatus has RESOLVING."""
        assert IntentStatus.RESOLVING.value == "resolving"

    def test_intent_status_resolved(self):
        """IntentStatus has RESOLVED."""
        assert IntentStatus.RESOLVED.value == "resolved"

    def test_intent_status_failed(self):
        """IntentStatus has FAILED."""
        assert IntentStatus.FAILED.value == "failed"

    def test_intent_status_surrendered(self):
        """IntentStatus has SURRENDERED."""
        assert IntentStatus.SURRENDERED.value == "surrendered"


# =============================================================================
# MantraIntent Dataclass Tests
# =============================================================================


class TestMantraIntent:
    """Test MantraIntent dataclass."""

    def test_mantra_intent_creation(self):
        """MantraIntent can be created."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={"key": "value"},
        )
        assert intent.type == IntentType.READ
        assert intent.target == "some.module"
        assert intent.params == {"key": "value"}

    def test_mantra_intent_default_priority(self):
        """MantraIntent has default NORMAL priority."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        assert intent.priority == IntentPriority.NORMAL

    def test_mantra_intent_default_requester(self):
        """MantraIntent has default requester 'anonymous'."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        assert intent.requester == "anonymous"

    def test_mantra_intent_default_parampara_vector(self):
        """MantraIntent has default parampara_vector 0."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        assert intent.parampara_vector == 0

    def test_mantra_intent_custom_priority(self):
        """MantraIntent accepts custom priority."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            priority=IntentPriority.CRITICAL,
        )
        assert intent.priority == IntentPriority.CRITICAL

    def test_mantra_intent_is_connected_false(self):
        """is_connected returns False for non-multiple of 37."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            parampara_vector=10,  # 10 % 37 != 0
        )
        assert intent.is_connected is False

    def test_mantra_intent_is_connected_true(self):
        """is_connected returns True for connected intent."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            parampara_vector=PARAMPARA * 12,  # 444
        )
        assert intent.is_connected is True

    def test_mantra_intent_opcode_read(self):
        """opcode returns correct OpCode for READ."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.EXEC_OP

    def test_mantra_intent_opcode_write(self):
        """opcode returns correct OpCode for WRITE."""
        intent = MantraIntent(
            type=IntentType.WRITE,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.LEDGER_SIGN

    def test_mantra_intent_opcode_transform(self):
        """opcode returns correct OpCode for TRANSFORM."""
        intent = MantraIntent(
            type=IntentType.TRANSFORM,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.EXTEND_CAP

    def test_mantra_intent_opcode_resolve(self):
        """opcode returns correct OpCode for RESOLVE."""
        intent = MantraIntent(
            type=IntentType.RESOLVE,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.BIND_SYMBOL

    def test_mantra_intent_opcode_bind(self):
        """opcode returns correct OpCode for BIND."""
        intent = MantraIntent(
            type=IntentType.BIND,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.INIT_THREAD

    def test_mantra_intent_opcode_migrate(self):
        """opcode returns correct OpCode for MIGRATE."""
        intent = MantraIntent(
            type=IntentType.MIGRATE,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.LOAD_ROOT

    def test_mantra_intent_opcode_wake(self):
        """opcode returns correct OpCode for WAKE."""
        intent = MantraIntent(
            type=IntentType.WAKE,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.SYS_WAKE

    def test_mantra_intent_opcode_sync(self):
        """opcode returns correct OpCode for SYNC."""
        intent = MantraIntent(
            type=IntentType.SYNC,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.DHARMA_TEST

    def test_mantra_intent_opcode_heal(self):
        """opcode returns correct OpCode for HEAL."""
        intent = MantraIntent(
            type=IntentType.HEAL,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.TYPE_CHECK

    def test_mantra_intent_opcode_observe(self):
        """opcode returns correct OpCode for OBSERVE."""
        intent = MantraIntent(
            type=IntentType.OBSERVE,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.STATE_SYNC

    def test_mantra_intent_opcode_surrender(self):
        """opcode returns correct OpCode for SURRENDER."""
        intent = MantraIntent(
            type=IntentType.SURRENDER,
            target="some.module",
            params={},
        )
        assert intent.opcode == MantraOpCode.YIELD_CPU

    def test_mantra_intent_guardian_read(self):
        """guardian returns correct Mahajana for READ."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.PRAHLADA

    def test_mantra_intent_guardian_write(self):
        """guardian returns correct Mahajana for WRITE."""
        intent = MantraIntent(
            type=IntentType.WRITE,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.BHISHMA

    def test_mantra_intent_guardian_transform(self):
        """guardian returns correct Mahajana for TRANSFORM."""
        intent = MantraIntent(
            type=IntentType.TRANSFORM,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.JANAKA

    def test_mantra_intent_guardian_resolve(self):
        """guardian returns correct Mahajana for RESOLVE."""
        intent = MantraIntent(
            type=IntentType.RESOLVE,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.KAPILA

    def test_mantra_intent_guardian_bind(self):
        """guardian returns correct Mahajana for BIND."""
        intent = MantraIntent(
            type=IntentType.BIND,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.MANU

    def test_mantra_intent_guardian_migrate(self):
        """guardian returns correct Mahajana for MIGRATE."""
        intent = MantraIntent(
            type=IntentType.MIGRATE,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.BRAHMA

    def test_mantra_intent_guardian_wake(self):
        """guardian returns correct Mahajana for WAKE."""
        intent = MantraIntent(
            type=IntentType.WAKE,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.BRAHMA

    def test_mantra_intent_guardian_sync(self):
        """guardian returns correct Mahajana for SYNC."""
        intent = MantraIntent(
            type=IntentType.SYNC,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.NARADA

    def test_mantra_intent_guardian_heal(self):
        """guardian returns correct Mahajana for HEAL."""
        intent = MantraIntent(
            type=IntentType.HEAL,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.SHAMBHU

    def test_mantra_intent_guardian_observe(self):
        """guardian returns correct Mahajana for OBSERVE."""
        intent = MantraIntent(
            type=IntentType.OBSERVE,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.SHUKA

    def test_mantra_intent_guardian_surrender(self):
        """guardian returns correct Mahajana for SURRENDER."""
        intent = MantraIntent(
            type=IntentType.SURRENDER,
            target="some.module",
            params={},
        )
        assert intent.guardian == Mahajana.BALI

    def test_mantra_intent_is_frozen(self):
        """MantraIntent is frozen (immutable)."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        with pytest.raises(AttributeError):
            intent.target = "other.module"  # type: ignore

    def test_mantra_intent_params_types(self):
        """MantraIntent params accept various types."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={
                "string": "value",
                "int": 42,
                "bool": True,
                "none": None,
            },
        )
        assert intent.params["string"] == "value"
        assert intent.params["int"] == 42
        assert intent.params["bool"] is True
        assert intent.params["none"] is None


# =============================================================================
# IntentResult Dataclass Tests
# =============================================================================


class TestIntentResult:
    """Test IntentResult dataclass."""

    def test_intent_result_creation(self):
        """IntentResult can be created."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.intent == intent
        assert result.status == IntentStatus.RESOLVED

    def test_intent_result_default_value(self):
        """IntentResult has default value None."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.value is None

    def test_intent_result_default_error(self):
        """IntentResult has default error None."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.error is None

    def test_intent_result_with_value(self):
        """IntentResult can have a value."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
            value="data",
        )
        assert result.value == "data"

    def test_intent_result_with_error(self):
        """IntentResult can have an error."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.FAILED,
            error="Something went wrong",
        )
        assert result.error == "Something went wrong"

    def test_intent_result_is_success_resolved(self):
        """is_success returns True for RESOLVED."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.is_success is True

    def test_intent_result_is_success_surrendered(self):
        """is_success returns True for SURRENDERED."""
        intent = MantraIntent(
            type=IntentType.SURRENDER,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.SURRENDERED,
        )
        assert result.is_success is True

    def test_intent_result_is_success_false_pending(self):
        """is_success returns False for PENDING."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.PENDING,
        )
        assert result.is_success is False

    def test_intent_result_is_success_false_failed(self):
        """is_success returns False for FAILED."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.FAILED,
        )
        assert result.is_success is False

    def test_intent_result_remainder_no_vector(self):
        """remainder returns 37 for parampara_vector 0."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            parampara_vector=0,
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.remainder == 37

    def test_intent_result_remainder_connected(self):
        """remainder returns 0 for connected intent."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            parampara_vector=PARAMPARA * 12,  # 444
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.remainder == 0

    def test_intent_result_remainder_partial(self):
        """remainder returns non-zero for partial connection."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
            parampara_vector=38,  # 38 % 37 = 1
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
        )
        assert result.remainder == 1

    def test_intent_result_resolved_by(self):
        """IntentResult can track resolved_by Mahajana."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
            resolved_by=Mahajana.PRAHLADA,
        )
        assert result.resolved_by == Mahajana.PRAHLADA

    def test_intent_result_parampara_verified(self):
        """IntentResult tracks parampara_verified."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = IntentResult(
            intent=intent,
            status=IntentStatus.RESOLVED,
            parampara_verified=True,
        )
        assert result.parampara_verified is True


# =============================================================================
# IntentQueue Tests
# =============================================================================


class TestIntentQueue:
    """Test IntentQueue class."""

    def test_intent_queue_creation(self):
        """IntentQueue can be created."""
        queue = IntentQueue()
        assert queue is not None

    def test_intent_queue_starts_empty(self):
        """IntentQueue starts empty."""
        queue = IntentQueue()
        assert len(queue) == 0
        assert queue.is_empty is True

    def test_intent_queue_push(self):
        """IntentQueue can push intents."""
        queue = IntentQueue()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        queue.push(intent)
        assert len(queue) == 1
        assert queue.is_empty is False

    def test_intent_queue_pop(self):
        """IntentQueue can pop intents."""
        queue = IntentQueue()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        queue.push(intent)
        popped = queue.pop()
        assert popped == intent
        assert len(queue) == 0

    def test_intent_queue_pop_empty(self):
        """IntentQueue returns None when popping empty queue."""
        queue = IntentQueue()
        popped = queue.pop()
        assert popped is None

    def test_intent_queue_priority_ordering(self):
        """IntentQueue orders by priority."""
        queue = IntentQueue()

        low = MantraIntent(
            type=IntentType.READ,
            target="low",
            params={},
            priority=IntentPriority.LOW,
        )
        critical = MantraIntent(
            type=IntentType.READ,
            target="critical",
            params={},
            priority=IntentPriority.CRITICAL,
        )
        normal = MantraIntent(
            type=IntentType.READ,
            target="normal",
            params={},
            priority=IntentPriority.NORMAL,
        )

        queue.push(low)
        queue.push(critical)
        queue.push(normal)

        # CRITICAL should come first
        assert queue.pop().target == "critical"
        assert queue.pop().target == "normal"
        assert queue.pop().target == "low"

    def test_intent_queue_multiple_same_priority(self):
        """IntentQueue handles multiple intents with same priority."""
        queue = IntentQueue()

        intent1 = MantraIntent(
            type=IntentType.READ,
            target="first",
            params={},
            priority=IntentPriority.NORMAL,
        )
        intent2 = MantraIntent(
            type=IntentType.READ,
            target="second",
            params={},
            priority=IntentPriority.NORMAL,
        )

        queue.push(intent1)
        queue.push(intent2)

        # Both should be retrievable
        assert len(queue) == 2


# =============================================================================
# MantraKernel Tests
# =============================================================================


class TestMantraKernel:
    """Test MantraKernel class."""

    def test_mantra_kernel_creation(self):
        """MantraKernel can be created."""
        kernel = MantraKernel()
        assert kernel is not None

    def test_mantra_kernel_is_connected(self):
        """MantraKernel reports connection status."""
        kernel = MantraKernel()
        # Should be connected via ParamparaConnection.from_guru()
        assert isinstance(kernel.is_connected, bool)

    def test_mantra_kernel_resolve_no_resolver(self):
        """MantraKernel surrenders when no resolver available."""
        kernel = MantraKernel()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = kernel.resolve(intent)
        assert result.status == IntentStatus.SURRENDERED

    def test_mantra_kernel_resolve_with_guardian(self):
        """MantraKernel sets resolved_by to guardian."""
        kernel = MantraKernel()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = kernel.resolve(intent)
        assert result.resolved_by == intent.guardian

    def test_mantra_kernel_queue_intent(self):
        """MantraKernel can queue intents."""
        kernel = MantraKernel()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        kernel.queue(intent)
        # Queue should have one item (internal check)
        assert not kernel._queue.is_empty

    def test_mantra_kernel_process_queue(self):
        """MantraKernel can process queued intents."""
        kernel = MantraKernel()
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        kernel.queue(intent)
        results = kernel.process_queue()
        assert len(results) == 1
        assert results[0].status == IntentStatus.SURRENDERED

    def test_mantra_kernel_process_empty_queue(self):
        """MantraKernel returns empty list for empty queue."""
        kernel = MantraKernel()
        results = kernel.process_queue()
        assert results == []

    def test_mantra_kernel_register_resolver(self):
        """MantraKernel can register resolvers."""

        class MockResolver:
            def can_resolve(self, intent):
                return True

            def resolve(self, intent):
                return IntentResult(
                    intent=intent,
                    status=IntentStatus.RESOLVED,
                    value="resolved!",
                )

        kernel = MantraKernel()
        kernel.register_resolver(IntentType.READ, MockResolver())

        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = kernel.resolve(intent)
        assert result.status == IntentStatus.RESOLVED
        assert result.value == "resolved!"

    def test_mantra_kernel_resolver_can_reject(self):
        """MantraKernel falls back when resolver can't handle."""

        class RejectingResolver:
            def can_resolve(self, intent):
                return False

            def resolve(self, intent):
                return IntentResult(
                    intent=intent,
                    status=IntentStatus.RESOLVED,
                )

        kernel = MantraKernel()
        kernel.register_resolver(IntentType.READ, RejectingResolver())

        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = kernel.resolve(intent)
        # Falls back to surrender
        assert result.status == IntentStatus.SURRENDERED


# =============================================================================
# get_kernel Function Tests
# =============================================================================


class TestGetKernel:
    """Test get_kernel function."""

    def test_get_kernel_returns_instance(self):
        """get_kernel returns MantraKernel."""
        kernel = get_kernel()
        assert isinstance(kernel, MantraKernel)

    def test_get_kernel_singleton(self):
        """get_kernel returns same instance."""
        kernel1 = get_kernel()
        kernel2 = get_kernel()
        assert kernel1 is kernel2


# =============================================================================
# resolve Function Tests
# =============================================================================


class TestResolveFunction:
    """Test resolve function."""

    def test_resolve_function_returns_result(self):
        """resolve returns IntentResult."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = resolve(intent)
        assert isinstance(result, IntentResult)

    def test_resolve_function_uses_global_kernel(self):
        """resolve uses global kernel."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="some.module",
            params={},
        )
        result = resolve(intent)
        # Should get surrendered result from global kernel
        assert result.status == IntentStatus.SURRENDERED


# =============================================================================
# surrender Function Tests
# =============================================================================


class TestSurrenderFunction:
    """Test surrender function."""

    def test_surrender_returns_result(self):
        """surrender returns IntentResult."""
        result = surrender("some.module")
        assert isinstance(result, IntentResult)

    def test_surrender_intent_type(self):
        """surrender creates SURRENDER intent."""
        result = surrender("some.module")
        assert result.intent.type == IntentType.SURRENDER

    def test_surrender_target(self):
        """surrender sets target correctly."""
        result = surrender("some.module")
        assert result.intent.target == "some.module"

    def test_surrender_with_params(self):
        """surrender accepts params."""
        result = surrender("some.module", {"key": "value"})
        assert result.intent.params == {"key": "value"}

    def test_surrender_is_connected(self):
        """surrender creates connected intent."""
        result = surrender("some.module")
        assert result.intent.is_connected is True

    def test_surrender_parampara_vector(self):
        """surrender sets parampara_vector to 444."""
        result = surrender("some.module")
        assert result.intent.parampara_vector == PARAMPARA * 12  # 444

    def test_surrender_remainder_is_zero(self):
        """surrender has remainder 0 (pure resolution)."""
        result = surrender("some.module")
        assert result.remainder == 0


# =============================================================================
# IntentResolver Protocol Tests
# =============================================================================


class TestIntentResolverProtocol:
    """Test IntentResolver protocol."""

    def test_intent_resolver_is_runtime_checkable(self):
        """IntentResolver is runtime checkable."""

        class ValidResolver:
            def can_resolve(self, intent):
                return True

            def resolve(self, intent):
                return IntentResult(
                    intent=intent,
                    status=IntentStatus.RESOLVED,
                )

        resolver = ValidResolver()
        assert isinstance(resolver, IntentResolver)

    def test_intent_resolver_missing_method(self):
        """IntentResolver rejects incomplete implementations."""

        class IncompleteResolver:
            def can_resolve(self, intent):
                return True

            # Missing resolve method

        resolver = IncompleteResolver()
        assert not isinstance(resolver, IntentResolver)


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.kernel import intent

        expected = [
            "IntentType",
            "IntentPriority",
            "IntentStatus",
            "MantraIntent",
            "IntentResult",
            "IntentQueue",
            "IntentResolver",
            "MantraKernel",
            "get_kernel",
            "resolve",
            "surrender",
        ]
        for item in expected:
            assert item in intent.__all__, f"{item} should be in __all__"
