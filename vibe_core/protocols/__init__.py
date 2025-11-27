"""
VIBE_CORE PROTOCOLS - Layer 1: Interfaces Only

This module contains ONLY abstract base classes (ABCs) that define the interfaces
for all vibe-agency components. No implementations here.

Protocol Modules:
- agent: VibeAgent ABC
- ledger: VibeLedger ABC
- scheduler: VibeScheduler ABC
- registry: ManifestRegistry ABC

These are pure interfaces. All implementations belong in Layer 2.
All wiring belongs in Layer 3 (runtime/).

BLOCKER #2: 3-Layer Architecture - Canonical Protocol Layer
"""

from .agent import VibeAgent, AgentManifest, AgentResponse, Capability
from .ledger import VibeLedger, VibeScheduler, VibeKernel, ManifestRegistry, KernelStatus
from .registry import ManifestRegistry as _ManifestRegistry  # Avoid duplicate
from .scheduler import VibeScheduler as _VibeScheduler  # Avoid duplicate

__all__ = [
    "VibeAgent",
    "AgentManifest",
    "AgentResponse",
    "Capability",
    "VibeLedger",
    "VibeScheduler",
    "VibeKernel",
    "ManifestRegistry",
    "KernelStatus",
]
