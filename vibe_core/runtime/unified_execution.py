"""
UNIFIED EXECUTION MODEL (OPUS Architecture)
============================================

OPUS-301: This module now serves as a compatibility layer.
Actual implementation split into:
- unified_execution_core.py (Router - loaded at boot)
- unified_execution_full.py (Executor - loaded on first use)

This reduces boot time by ~265ms by deferring executor imports.

Original components:
1. ExecutionRequest - Unified request tracking object (Moved to vibe_core.state.schema)
2. ExecutionResult - Unified result format (Moved to vibe_core.state.schema)
3. UnifiedRouter - Single router (in core)
4. UnifiedExecutor - Single executor (in full)

OPUS-200/201 INTEGRATION:
- QuantumReactor provides RESONANCE-BASED gating (Breaking the Binary)
- check_gate_resonant() computes continuous energy instead of boolean
- Actions MANIFEST when energy > inertia (not "allowed")
- Entropy chain provides cryptographic audit trail

Refs: docs/architecture/OPUS/OPUS_RUNTIME_SEPARATION.md
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

# OPUS-301: Import router from core (light - loaded at boot)
from vibe_core.runtime.unified_execution_core import UnifiedRouter

# OPUS-301: Import executor from full (heavy - lazy loaded)
from vibe_core.runtime.unified_execution_full import UnifiedExecutor

# Re-export schema types for backward compatibility
from vibe_core.state.schema import (
    ExecutionPath,
    ExecutionRequest,
    ExecutionResult,
    MilkOceanGate,
)

# Re-export for backward compatibility
__all__ = [
    "UnifiedRouter",
    "UnifiedExecutor",
    "create_unified_runtime",
    "ExecutionPath",
    "ExecutionRequest",
    "ExecutionResult",
    "MilkOceanGate",
]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_unified_runtime(kernel: "RealVibeKernel") -> tuple:
    """
    Create unified router and executor for a kernel.

    OPUS-301: Router imported from core (light), Executor from full (heavy).

    Returns:
        (UnifiedRouter, UnifiedExecutor) tuple
    """
    router = UnifiedRouter(kernel)
    executor = UnifiedExecutor(kernel)
    return router, executor
