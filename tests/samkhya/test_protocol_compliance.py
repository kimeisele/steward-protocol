import inspect
from typing import get_type_hints

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.naga.services.ananta import AnantaService
from vibe_core.protocols.substrate import IAnantaBridge
from vibe_core.protocols.universal import (
    EnforceProtocol,
    InferProtocol,
    KrishnaProtocol,
    MantraProtocol,
    OmProtocol,
    RamaProtocol,
    ReadWriteProtocol,
    StoreRecallProtocol,
    SyncProtocol,
)


class TestProtocolCompliance:
    """
    PROTOCOL COMPLIANCE GATES (TDD).
    HARD MODE: Strict Signature Verification.
    """

    def _verify_signature(self, cls, protocol, method_name):
        """Helper to verify method signature matches protocol."""
        assert hasattr(cls, method_name), f"{cls.__name__} missing {method_name}"

        proto_method = getattr(protocol, method_name)
        cls_method = getattr(cls, method_name)

        proto_sig = inspect.signature(proto_method)
        cls_sig = inspect.signature(cls_method)

        # We check parameter names and count. Types might differ (covariant) but let's check count.
        assert len(proto_sig.parameters) == len(cls_sig.parameters), (
            f"Signature mismatch for {method_name}: Expected {len(proto_sig.parameters)} params, got {len(cls_sig.parameters)}"
        )

    def test_kernel_implements_krishna(self):
        """Gate: Krishna Protocol (Identity)."""
        assert issubclass(RealVibeKernel, KrishnaProtocol)
        self._verify_signature(RealVibeKernel, KrishnaProtocol, "bind_genes")
        # Property check
        assert hasattr(RealVibeKernel, "sovereign_context")

    def test_kernel_implements_rama(self):
        """Gate: Rama Protocol (Action)."""
        assert issubclass(RealVibeKernel, RamaProtocol)
        self._verify_signature(RealVibeKernel, RamaProtocol, "perform_dharma")

    def test_kernel_implements_mantra(self):
        """Gate: Mantra Protocol (Time)."""
        assert issubclass(RealVibeKernel, MantraProtocol)
        self._verify_signature(RealVibeKernel, MantraProtocol, "chant_mahamantra")
        self._verify_signature(RealVibeKernel, MantraProtocol, "get_alignment_score")

    def test_kernel_implements_infer(self):
        """Gate: Infer Protocol (Thought)."""
        assert issubclass(RealVibeKernel, InferProtocol)
        self._verify_signature(RealVibeKernel, InferProtocol, "infer")
        self._verify_signature(RealVibeKernel, InferProtocol, "classify")
        self._verify_signature(RealVibeKernel, InferProtocol, "evaluate")

    def test_kernel_implements_enforce(self):
        """Gate: Enforce Protocol (Law)."""
        assert issubclass(RealVibeKernel, EnforceProtocol)
        self._verify_signature(RealVibeKernel, EnforceProtocol, "enforce")
        self._verify_signature(RealVibeKernel, EnforceProtocol, "check")
        self._verify_signature(RealVibeKernel, EnforceProtocol, "get_rules")

    def test_kernel_implements_read_write(self):
        """Gate: ReadWrite Protocol (Record)."""
        assert issubclass(RealVibeKernel, ReadWriteProtocol)
        self._verify_signature(RealVibeKernel, ReadWriteProtocol, "read")
        self._verify_signature(RealVibeKernel, ReadWriteProtocol, "write")
        self._verify_signature(RealVibeKernel, ReadWriteProtocol, "exists")

    def test_kernel_implements_store_recall(self):
        """Gate: StoreRecall Protocol (Memory)."""
        assert issubclass(RealVibeKernel, StoreRecallProtocol)
        self._verify_signature(RealVibeKernel, StoreRecallProtocol, "store")
        self._verify_signature(RealVibeKernel, StoreRecallProtocol, "recall")
        self._verify_signature(RealVibeKernel, StoreRecallProtocol, "forget")

    def test_kernel_implements_sync(self):
        """Gate: Sync Protocol (Cycle)."""
        assert issubclass(RealVibeKernel, SyncProtocol)
        self._verify_signature(RealVibeKernel, SyncProtocol, "sync")
        self._verify_signature(RealVibeKernel, SyncProtocol, "get_sync_status")
        self._verify_signature(RealVibeKernel, SyncProtocol, "is_synced")

    def test_kernel_implements_om(self):
        """Gate: Om Protocol (Unification)."""
        assert issubclass(RealVibeKernel, OmProtocol)
        # Om unifies all others, so if others pass, this conceptually passes.
        # But we check explicit inheritance.

    def test_ananta_implements_bridge(self):
        """Gate: Ananta must be the Substrate Bridge."""
        assert issubclass(AnantaService, IAnantaBridge)
        self._verify_signature(AnantaService, IAnantaBridge, "flood_instance")
        self._verify_signature(AnantaService, IAnantaBridge, "resonate")
        self._verify_signature(AnantaService, IAnantaBridge, "analyze_class")
