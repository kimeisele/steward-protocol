"""
OPUS-171 Phase 5.2: Cortex Adapters

This module contains adapters that wrap existing cortex implementations
in the BaseCortex interface for VEDA-4 auto-discovery.

ADAPTER PATTERN:
    Instead of modifying existing cortex modules (which could break things),
    we create adapters that delegate to the original implementations.

    Original: ShellCortex.execute_safe(cmd)
    Adapter:  ShellCortexAdapter.execute(intent) → calls ShellCortex internally

AVAILABLE ADAPTERS:
    - ShellCortexAdapter: Git/CLI operations
    - SutraCortexAdapter: Documentation weaving
    - TestCortexAdapter: Test execution
    - SilpaCortexAdapter: Code refactoring

USAGE:
    from vibe_core.loaders import get_cortex

    shell = get_cortex("shell", workspace=Path.cwd())
    result = shell.execute(intent)
"""

from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import (
    BaseCortex,
    cortex_error,
    cortex_success,
)

__all__ = [
    "BaseCortex",
    "cortex_success",
    "cortex_error",
]
