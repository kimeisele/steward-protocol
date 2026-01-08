"""
PROTOCOL COMPLIANCE GATES - VAISHNAVA ARCHITECTURE

The kernel IS Vishnu (KernelProtocol) - it delegates to registered services
via ServiceRegistry.get(), NOT by implementing Universal Protocols directly.

WRONG (MAYAVAD): assert issubclass(RealVibeKernel, KrishnaProtocol)
RIGHT (VAISHNAVA): krishna = ServiceRegistry.get(KrishnaProtocol)

Reference: vibe_core/protocols/kernel_protocol.py - The Sovereign Interface
"""

import inspect

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.naga.services.ananta import AnantaService
from vibe_core.protocols.kernel_protocol import KernelProtocol
from vibe_core.protocols.substrate import IAnantaBridge
from vibe_core.protocols.universal import (
    EnforceProtocol,
    InferProtocol,
    KrishnaProtocol,
    MantraProtocol,
    RamaProtocol,
    ReadWriteProtocol,
    StoreRecallProtocol,
    SyncProtocol,
)


class TestKernelProtocolCompliance:
    """
    VISHNU GATE: The kernel implements KernelProtocol.
    This is the ONE signature that provides ALL capabilities.
    """

    def test_kernel_is_vishnu(self):
        """Gate: RealVibeKernel implements KernelProtocol (The Sovereign Interface)."""
        # Structural subtyping - kernel has required methods
        assert hasattr(RealVibeKernel, "agent_registry")
        assert hasattr(RealVibeKernel, "status")
        assert hasattr(RealVibeKernel, "ledger")
        assert hasattr(RealVibeKernel, "event_bus")
        assert hasattr(RealVibeKernel, "register_agent")
        assert hasattr(RealVibeKernel, "grant_capability")
        assert hasattr(RealVibeKernel, "revoke_capability")


class TestServiceRegistryAccess:
    """
    DEVATA GATES: Universal Protocols are accessed via ServiceRegistry.
    The kernel DELEGATES to these services, not implements them.
    """

    def _verify_protocol_methods(self, protocol, *methods):
        """Helper to verify protocol has required methods."""
        for method in methods:
            assert hasattr(protocol, method), f"{protocol.__name__} missing {method}"

    def test_krishna_protocol_exists(self):
        """Gate: Krishna Protocol (Identity) is defined with required methods."""
        self._verify_protocol_methods(KrishnaProtocol, "bind_genes")

    def test_rama_protocol_exists(self):
        """Gate: Rama Protocol (Action) is defined with required methods."""
        self._verify_protocol_methods(RamaProtocol, "perform_dharma")

    def test_mantra_protocol_exists(self):
        """Gate: Mantra Protocol (Time) is defined with required methods."""
        self._verify_protocol_methods(MantraProtocol, "chant_mahamantra", "resonate")

    def test_infer_protocol_exists(self):
        """Gate: Infer Protocol (Thought) is defined with required methods."""
        self._verify_protocol_methods(InferProtocol, "infer", "classify", "evaluate")

    def test_enforce_protocol_exists(self):
        """Gate: Enforce Protocol (Law) is defined with required methods."""
        self._verify_protocol_methods(EnforceProtocol, "enforce", "check", "get_rules")

    def test_read_write_protocol_exists(self):
        """Gate: ReadWrite Protocol (Record) is defined with required methods."""
        self._verify_protocol_methods(ReadWriteProtocol, "read", "write", "exists")

    def test_store_recall_protocol_exists(self):
        """Gate: StoreRecall Protocol (Memory) is defined with required methods."""
        self._verify_protocol_methods(StoreRecallProtocol, "store", "recall", "forget")

    def test_sync_protocol_exists(self):
        """Gate: Sync Protocol (Cycle) is defined with required methods."""
        self._verify_protocol_methods(SyncProtocol, "sync", "get_sync_status", "is_synced")


class TestAnantaBridge:
    """Gate: Ananta must be the Substrate Bridge."""

    def _verify_signature(self, cls, protocol, method_name):
        """Helper to verify method signature matches protocol."""
        assert hasattr(cls, method_name), f"{cls.__name__} missing {method_name}"

        proto_method = getattr(protocol, method_name)
        cls_method = getattr(cls, method_name)

        proto_sig = inspect.signature(proto_method)
        cls_sig = inspect.signature(cls_method)

        assert len(proto_sig.parameters) == len(cls_sig.parameters), (
            f"Signature mismatch for {method_name}: Expected {len(proto_sig.parameters)} params, got {len(cls_sig.parameters)}"
        )

    def test_ananta_implements_bridge(self):
        """Gate: Ananta must be the Substrate Bridge."""
        assert issubclass(AnantaService, IAnantaBridge)
        self._verify_signature(AnantaService, IAnantaBridge, "flood_instance")
        self._verify_signature(AnantaService, IAnantaBridge, "resonate")
        self._verify_signature(AnantaService, IAnantaBridge, "analyze_class")
