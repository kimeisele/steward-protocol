"""
STEWARD PROTOCOL - Agent Meta-Layer

STEWARD is NOT an Agent. STEWARD is the PROTOCOL that enables Agents to exist.
Like Telegram's BotFather is not a bot - it's the meta-instance managing bots.

This is one of N fractal pillars:
- kernel/    → Execution
- phoenix/   → Configuration
- steward/   → Agent Protocol (this)
- playbook/  → Workflows
- ...        → Extensible

Components:
- protocol.py    → AgentManifest, AgentProtocol (duck-typed)
- loader.py      → AgentLoader (auto-discovery, like SectionLoader)
- constitution.py → Constitutional Oath binding
- oath_mixin.py  → Mixin for agents to swear oaths
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x510d6833"  # GenesisByte: parampara % 37 == 0

from vibe_core.steward.constitution import ConstitutionalOath
from vibe_core.steward.loader import AgentLoader, AgentMeta
from vibe_core.steward.oath_mixin import OathMixin
from vibe_core.steward.protocol import AgentManifest, AgentProtocol, is_valid_agent

__all__ = [
    # Protocol
    "AgentManifest",
    "AgentProtocol",
    "is_valid_agent",
    # Loader
    "AgentLoader",
    "AgentMeta",
    # Constitution
    "ConstitutionalOath",
    "OathMixin",
]
