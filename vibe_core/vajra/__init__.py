"""
⚡ VAJRA - The Diamond Wiring System
=====================================

OPUS-070: Kernel topology enforcement for the Steward Protocol.

VAJRA ensures all components are properly wired to the kernel.
Components without kernel injection operate in "shadow mode" (limited capability).

Three Laws of VAJRA:
1. No component shall access ledger without kernel injection
2. All wirable components must implement inject_kernel()
3. Shadow mode is permissive but logged - production must be WIRED

Usage:
    from vibe_core.vajra import WiringProtocol, assert_wired, auto_wire

    class MyComponent:
        def __init__(self):
            self._vibe_kernel = None

        def inject_kernel(self, kernel):
            self._vibe_kernel = kernel

    # Assert wired before use
    @assert_wired
    def execute(self):
        return self._vibe_kernel.ledger.get_all_events()

    # Auto-wire from kernel
    component = MyComponent()
    auto_wire(kernel, component)

CANONICAL LOCATION: vibe_core/vajra/__init__.py
"""

from vibe_core.vajra.auto_wire import auto_wire, wire_all
from vibe_core.vajra.enforcement import (
    VajraEnforcer,
    WiringError,
    assert_wired,
    check_wired,
    require_wiring,
)
from vibe_core.vajra.protocol import WiringProtocol
from vibe_core.vajra.scanner import VAJRAScanner, scan_for_orphans

__all__ = [
    # Protocol
    "WiringProtocol",
    # Enforcement
    "assert_wired",
    "require_wiring",
    "WiringError",
    "check_wired",
    "VajraEnforcer",
    # Auto-wiring
    "auto_wire",
    "wire_all",
    # Scanning
    "VAJRAScanner",
    "scan_for_orphans",
]
