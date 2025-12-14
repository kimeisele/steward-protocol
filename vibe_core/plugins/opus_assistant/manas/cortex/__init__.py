"""
MANAS Cortex - The Sensory-Motor Interface.

OPUS-041: VAK (The Voice)
OPUS-042: SAMVADA (The Dialogue)
OPUS-043: JNANA (The Conversation)

The cortex modules provide MANAS with interfaces to the external world:
- ShellCortex: Safe CLI command execution
- SamvadaListener/Client: Real-time human-MANAS dialogue
- JnanaHandler: Intelligent LLM-powered responses

"The brain alone is not enough - it needs hands to act and ears to hear."
"""

from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler
from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
    SamvadaClient,
    SamvadaListener,
    SamvadaMessage,
    SamvadaResponse,
    chat,
    chat_sync,
)
from vibe_core.plugins.opus_assistant.manas.cortex.samvada_handler import (
    SamvadaHandler,
    create_manas_handler,
)
from vibe_core.plugins.opus_assistant.manas.cortex.shell import (
    CommandRisk,
    ShellCortex,
    ShellResult,
)

__all__ = [
    # OPUS-041: VAK (The Voice)
    "ShellCortex",
    "ShellResult",
    "CommandRisk",
    # OPUS-042: SAMVADA (The Dialogue)
    "SamvadaListener",
    "SamvadaClient",
    "SamvadaMessage",
    "SamvadaResponse",
    "SamvadaHandler",
    "chat",
    "chat_sync",
    "create_manas_handler",
    # OPUS-043: JNANA (The Conversation)
    "JnanaHandler",
]
