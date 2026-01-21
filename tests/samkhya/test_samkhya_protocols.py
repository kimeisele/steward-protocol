import dataclasses
from datetime import datetime
from typing import Any, List, Protocol, runtime_checkable, Dict, Optional

import pytest

# Import strict types and protocols
from vibe_core.protocols.universal import (
    Classification,
    ClassifyInput,
    EnforceContext,
    EnforceProtocol,
    Evaluation,
    Inference,
    InferenceInput,
    InferProtocol,
    MemoryValue,
    ReadWriteProtocol,
    Rule,
    StoreRecallProtocol,
    SyncProtocol,
    SyncResult,
    SyncStatus,
    Verdict,
    SovereignContext,
    ProtectedMemory,
)
from vibe_core.protocols.substrate.byte import HolyName, MantraByte

# =============================================================================
# MOCK IMPLEMENTATIONS (The "Varieties" of species)
# =============================================================================


class MockCityConfig:
    """Implements ReadWriteProtocol."""

    def __init__(self):
        self.data = {}

    def read(self, key: str, context: Optional[SovereignContext] = None) -> Any:
        return self.data.get(key)

    def write(self, key: str, value: Any, context: Optional[SovereignContext] = None) -> None:
        self.data[key] = value

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        return key in self.data


class MockCivicConfig:
    """Also implements ReadWriteProtocol (Demonstrates Polymorphism)."""

    def read(self, key: str, context: Optional[SovereignContext] = None) -> Any:
        return "civic"

    def write(self, key: str, value: Any, context: Optional[SovereignContext] = None) -> None:
        pass

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        return True


class MockCISync:
    """Implements SyncProtocol."""

    def sync(self, context: Optional[SovereignContext] = None) -> SyncResult:
        return SyncResult(True, 1)

    def get_sync_status(self, context: Optional[SovereignContext] = None) -> SyncStatus:
        return SyncStatus(True, datetime.now(), 0)

    def is_synced(self, context: Optional[SovereignContext] = None) -> bool:
        return True


class MockGuardian:
    """Implements EnforceProtocol."""

    def verify_action(self, action: str, ctx: SovereignContext) -> HolyName:
        return HolyName.KRISHNA

    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        return Verdict.ALLOW

    def check(self, action: str, context: EnforceContext) -> bool:
        return True

    def calculate_merkle_root(self, ctx: SovereignContext, action: str) -> str:
        return "root"

    def get_rules(self) -> List[Rule]:
        return []


class MockBrain:
    """Implements InferProtocol."""

    def infer(self, input: InferenceInput) -> Inference:
        return Inference("AB", 0.9, [])

    def classify(self, input: ClassifyInput) -> Classification:
        return Classification("A", 0.9, [])

    def evaluate(self, claim: str, context: Optional[SovereignContext] = None) -> Evaluation:
        return Evaluation(True, 1.0, [])


class MockMemory:
    """Implements StoreRecallProtocol."""

    def remember(self, key: str, memory: ProtectedMemory, mantra: MantraByte, context: SovereignContext) -> bool:
        return True

    def store(self, key: str, value: object, context: SovereignContext) -> bool:
        pass

    def recall(self, key: str, mantra: MantraByte, context: SovereignContext) -> Optional[ProtectedMemory]:
        return None

    def forget(self, key: str, context: SovereignContext) -> bool:
        return True

    def list_keys(self, pattern: str = "*", context: SovereignContext = None) -> List[str]:
        return []

    def get_memory_stats(self, context: SovereignContext = None) -> Dict[str, object]:
        return {}


# =============================================================================
# FRACTAL COMPLIANCE TESTS (The "Gene" Checks)
# =============================================================================


@pytest.mark.unit
class TestSamkhyaGenetics:
    """
    Verifies the Genetic Integrity of the SAMKHYA Atomic Protocols.
    'Genes' must be pure (Interface) and strong (Runtime Checkable).
    """

    def test_dna_integrity_read_write(self):
        """Verify ReadWriteProtocol structure and polymorphism."""
        # 1. Structural Typing
        assert isinstance(MockCityConfig(), ReadWriteProtocol)
        assert isinstance(MockCivicConfig(), ReadWriteProtocol)

        # 2. Rejection of Mutation
        class Mutant:
            def read(self, key: str) -> Any:
                pass

            # Missing write/exists

        assert not isinstance(Mutant(), ReadWriteProtocol)

    def test_dna_integrity_sync(self):
        """Verify SyncProtocol."""
        assert isinstance(MockCISync(), SyncProtocol)

        class BrokenSync:
            def sync(self):
                pass

            # Missing others

        assert not isinstance(BrokenSync(), SyncProtocol)

    def test_dna_integrity_enforce(self):
        """Verify EnforceProtocol."""
        assert isinstance(MockGuardian(), EnforceProtocol)

    def test_dna_integrity_infer(self):
        """Verify InferProtocol."""
        assert isinstance(MockBrain(), InferProtocol)

    def test_dna_integrity_store_recall(self):
        """Verify StoreRecallProtocol."""
        assert isinstance(MockMemory(), StoreRecallProtocol)


@pytest.mark.unit
class TestSamkhyaTypes:
    """
    Verifies the Data Structures (Types) used by the protocols.
    Ensures Dataclasses are immutable-ish and structurally sound.
    """

    def test_verdict_enum(self):
        """Verdict must be standard."""
        assert Verdict.ALLOW == "allow"
        assert Verdict.DENY == "deny"
        assert Verdict.ESCALATE == "escalate"
        assert Verdict.AUDIT == "audit"

    def test_sync_result_integrity(self):
        """SyncResult defaults."""
        res = SyncResult(success=True, items_synced=10)
        assert res.errors == []
        assert isinstance(res.timestamp, datetime)

    def test_enforce_context_integrity(self):
        """EnforceContext defaults."""
        from vibe_core.protocols.universal.types import SovereignContext

        sov = SovereignContext(identity_id="test", signature="sig")
        ctx = EnforceContext("agent1", "db", "write", sovereign=sov)
        assert ctx.caller_id == "agent1"


@pytest.mark.unit
class TestRegistrySimulation:
    """
    Simulates the FUTURE capability of ServiceRegistry (Phase 2).
    This proves that the Protocols are ready for 'get_all()'.
    """

    def test_get_all_simulation(self):
        """
        Simulate getting all services that implement a protocol.
        This represents the core logic of the future ServiceRegistry.get_all().
        """
        # The Pool of all services
        registry_pool = [
            MockCityConfig(),
            MockCivicConfig(),
            MockCISync(),
            MockGuardian(),
            "RandomString",  # Noise
            None,
        ]

        # The Filter (What ServiceRegistry.get_all will do)
        read_write_services = [s for s in registry_pool if isinstance(s, ReadWriteProtocol)]

        # Assertion: Should find exactly 2 (City and Civic)
        assert len(read_write_services) == 2
        assert any(isinstance(s, MockCityConfig) for s in read_write_services)
        assert any(isinstance(s, MockCivicConfig) for s in read_write_services)

        # Assertion: Noise should be filtered
        assert "RandomString" not in read_write_services

    def test_strict_typing_enforcement(self):
        """
        Verify that even if methods exist, signature mismatch *might* pass runtime checks
        (Python limitation), but we verify structural existence strictly.
        """

        class ShadowOfReading:
            def read(self, key):
                pass

            def write(self, key, val):
                pass

            def exists(self, key):
                pass

        # Python's runtime_checkable only checks existence, not signatures.
        # This confirms the *limit* of our genetics.
        assert isinstance(ShadowOfReading(), ReadWriteProtocol)
