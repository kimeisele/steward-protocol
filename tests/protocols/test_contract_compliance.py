"""
PHASE 0: PROTOCOL CONTRACT COMPLIANCE TESTS

Der TÜV für das System - beweist dass konkrete Klassen ihre Protocols erfüllen.

DHARMA: Ein Protocol ohne Test ist ein Vertrag ohne Anwalt.
        Der Test IST der Anwalt, der den Vertrag durchsetzt.

This uses `isinstance(concrete, Protocol)` for runtime verification.
Protocols MUST be decorated with @runtime_checkable for this to work.
"""

import pytest
from typing import TYPE_CHECKING

# =============================================================================
# TEST 1: EventBus implements EventBusProtocol
# =============================================================================


def test_eventbus_implements_protocol():
    """
    VAJRA TEST: EventBus must satisfy EventBusProtocol contract.
    
    This test proves that the concrete EventBus class can be used
    anywhere that expects an EventBusProtocol.
    """
    from vibe_core.event_bus import EventBus
    from vibe_core.protocols.event import EventBusProtocol
    
    # The essence: isinstance check at runtime
    bus = EventBus()
    assert isinstance(bus, EventBusProtocol), (
        "MAYAVAD DETECTED: EventBus does not implement EventBusProtocol! "
        "The Protocol is a lie."
    )


def test_eventbus_has_all_protocol_methods():
    """
    Belt-and-suspenders: verify each method signature exists.
    
    Even if isinstance passes, we want to verify the actual signatures.
    """
    from vibe_core.event_bus import EventBus
    import asyncio
    
    bus = EventBus()
    
    # emit (async)
    assert hasattr(bus, 'emit'), "Missing: emit"
    assert asyncio.iscoroutinefunction(bus.emit), "emit must be async"
    
    # subscribe (sync, returns str)
    assert hasattr(bus, 'subscribe'), "Missing: subscribe"
    assert callable(bus.subscribe), "subscribe must be callable"
    
    # unsubscribe (sync)
    assert hasattr(bus, 'unsubscribe'), "Missing: unsubscribe"
    assert callable(bus.unsubscribe), "unsubscribe must be callable"
    
    # get_history (sync, returns List[Event])
    assert hasattr(bus, 'get_history'), "Missing: get_history"
    result = bus.get_history()
    assert isinstance(result, list), "get_history must return a list"
    
    # get_status (sync, returns Dict)
    assert hasattr(bus, 'get_status'), "Missing: get_status"
    result = bus.get_status()
    assert isinstance(result, dict), "get_status must return a dict"


# =============================================================================
# TEST 2: RealVibeKernel implements KernelProtocol
# =============================================================================


def test_kernel_implements_protocol():
    """
    VAJRA TEST: RealVibeKernel must satisfy KernelProtocol contract.
    
    This is the CRITICAL test - if this fails, the entire Protocol
    migration is blocked.
    """
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    
    # Create minimal kernel for test (in-memory, no plugins)
    kernel = RealVibeKernel(
        ledger_path=":memory:",
        load_plugins=False,
        test_mode=True,
    )
    
    assert isinstance(kernel, KernelProtocol), (
        "MAYAVAD DETECTED: RealVibeKernel does not implement KernelProtocol! "
        "This blocks the entire Protocol migration."
    )


def test_kernel_has_core_properties():
    """
    Verify RealVibeKernel has the core properties defined in KernelProtocol.
    """
    from vibe_core.kernel_impl import RealVibeKernel
    
    kernel = RealVibeKernel(
        ledger_path=":memory:",
        load_plugins=False,
        test_mode=True,
    )
    
    # Properties that MUST exist
    assert hasattr(kernel, 'agent_registry'), "Missing: agent_registry"
    assert hasattr(kernel, 'status'), "Missing: status"
    assert hasattr(kernel, 'config'), "Missing: config"
    assert hasattr(kernel, 'ledger'), "Missing: ledger"
    assert hasattr(kernel, 'event_bus'), "Missing: event_bus"
    assert hasattr(kernel, 'io'), "Missing: io"


def test_kernel_has_core_methods():
    """
    Verify RealVibeKernel has the core methods defined in KernelProtocol.
    """
    from vibe_core.kernel_impl import RealVibeKernel
    
    kernel = RealVibeKernel(
        ledger_path=":memory:",
        load_plugins=False,
        test_mode=True,
    )
    
    # Methods that MUST exist
    assert callable(getattr(kernel, 'register_agent', None)), "Missing: register_agent"
    assert callable(getattr(kernel, 'terminate_agent', None)), "Missing: terminate_agent"
    assert callable(getattr(kernel, 'submit_task', None)), "Missing: submit_task"
    assert callable(getattr(kernel, 'get_status', None)), "Missing: get_status"
    assert callable(getattr(kernel, 'get_system_status', None)), "Missing: get_system_status"


# =============================================================================
# TEST 3: SQLiteLedger implements VibeLedger
# =============================================================================


def test_ledger_implements_protocol():
    """
    VAJRA TEST: SQLiteLedger must satisfy VibeLedger protocol.
    """
    from vibe_core.ledger import SQLiteLedger
    from vibe_core.protocols.ledger import VibeLedger
    
    ledger = SQLiteLedger(":memory:")
    
    assert isinstance(ledger, VibeLedger), (
        "MAYAVAD DETECTED: SQLiteLedger does not implement VibeLedger! "
        "Ledger Protocol migration blocked."
    )


def test_inmemory_ledger_implements_protocol():
    """
    VAJRA TEST: InMemoryLedger must also satisfy VibeLedger protocol.
    """
    from vibe_core.ledger import InMemoryLedger
    from vibe_core.protocols.ledger import VibeLedger
    
    ledger = InMemoryLedger()
    
    assert isinstance(ledger, VibeLedger), (
        "MAYAVAD DETECTED: InMemoryLedger does not implement VibeLedger!"
    )


# =============================================================================
# TEST 4: NullEventBus implements EventBusProtocol
# =============================================================================


def test_null_eventbus_implements_protocol():
    """
    VAJRA TEST: NullEventBus (fallback) must also satisfy the contract.
    
    This is critical for the Arjuna Pattern - the fallback MUST
    be a valid substitute.
    """
    from vibe_core.protocols.event import EventBusProtocol, NullEventBus
    
    null_bus = NullEventBus()
    
    assert isinstance(null_bus, EventBusProtocol), (
        "MAYAVAD DETECTED: NullEventBus does not implement EventBusProtocol! "
        "The Arjuna Pattern is broken."
    )


# =============================================================================
# SUMMARY TEST: The Full Protocol Matrix
# =============================================================================


def test_protocol_compliance_matrix():
    """
    THE FULL TÜV: Run all compliance checks and report.
    
    This is the definitive test that the Protocol layer is complete.
    """
    results = {}
    
    # EventBus
    try:
        from vibe_core.event_bus import EventBus
        from vibe_core.protocols.event import EventBusProtocol
        results["EventBus -> EventBusProtocol"] = isinstance(EventBus(), EventBusProtocol)
    except Exception as e:
        results["EventBus -> EventBusProtocol"] = f"ERROR: {e}"
    
    # NullEventBus
    try:
        from vibe_core.protocols.event import EventBusProtocol, NullEventBus
        results["NullEventBus -> EventBusProtocol"] = isinstance(NullEventBus(), EventBusProtocol)
    except Exception as e:
        results["NullEventBus -> EventBusProtocol"] = f"ERROR: {e}"
    
    # Kernel
    try:
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.protocols.kernel_protocol import KernelProtocol
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False, test_mode=True)
        results["RealVibeKernel -> KernelProtocol"] = isinstance(kernel, KernelProtocol)
    except Exception as e:
        results["RealVibeKernel -> KernelProtocol"] = f"ERROR: {e}"
    
    # Ledgers
    try:
        from vibe_core.ledger import SQLiteLedger, InMemoryLedger
        from vibe_core.protocols.ledger import VibeLedger
        results["SQLiteLedger -> VibeLedger"] = isinstance(SQLiteLedger(":memory:"), VibeLedger)
        results["InMemoryLedger -> VibeLedger"] = isinstance(InMemoryLedger(), VibeLedger)
    except Exception as e:
        results["Ledgers -> VibeLedger"] = f"ERROR: {e}"
    
    # Print matrix
    print("\n" + "=" * 60)
    print("PROTOCOL COMPLIANCE MATRIX (VAJRA TÜV)")
    print("=" * 60)
    for check, result in results.items():
        status = "✓" if result is True else "✗"
        print(f"  {status} {check}: {result}")
    print("=" * 60 + "\n")
    
    # Assert all pass
    failures = [k for k, v in results.items() if v is not True]
    assert not failures, f"Protocol compliance failures: {failures}"
