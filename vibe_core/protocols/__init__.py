"""
VIBE_CORE PROTOCOLS - Layer 1: Interfaces Only

This module contains ONLY abstract base classes (ABCs) that define the interfaces
for all vibe-agency components. No implementations here.

Protocol Modules:
- agent: VibeAgent ABC
- ledger: VibeLedger ABC
- playbook: Playbook and related ABCs
- store: Store ABC
- scheduler: VibeScheduler ABC
- registry: ManifestRegistry ABC
- oath: OathProtocol (Constitutional oath interface)
- config: Configuration protocol (CityConfig)

These are pure interfaces. All implementations belong in Layer 2.
All wiring belongs in Layer 3 (runtime/).

BLOCKER #2: 3-Layer Architecture - Canonical Protocol Layer
"""

from .agent import VibeAgent, AgentManifest, Task
from .ledger import VibeLedger
from .playbook import Playbook
from .store import VibeStore
from .scheduler import VibeScheduler
from .registry import ManifestRegistry

__all__ = [
    "VibeAgent",
    "AgentManifest",
    "Task",
    "VibeLedger",
    "Playbook",
    "VibeStore",
    "VibeScheduler",
    "ManifestRegistry",
]
