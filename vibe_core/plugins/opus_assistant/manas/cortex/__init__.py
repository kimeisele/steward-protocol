"""
MANAS Cortex - The Sensory-Motor Interface.

OPUS-041: VAK (The Voice)

The cortex modules provide MANAS with interfaces to the external world:
- ShellCortex: Safe CLI command execution
- (Future) GitCortex: Git operations
- (Future) FileCortex: File operations

"The brain alone is not enough - it needs hands to act."
"""

from vibe_core.plugins.opus_assistant.manas.cortex.shell import (
    CommandRisk,
    ShellCortex,
    ShellResult,
)

__all__ = ["ShellCortex", "ShellResult", "CommandRisk"]
