"""
NAGA Federation - The Invisible Guardians.

"Niemand darf es merken" - they infiltrate invisibly.
"Wie Wasser in jede Ritze" - organic flooding into every crack.
"Der Wächter" - they notice when things go wrong.

Components:
- NagaOrchestrator: Bootstrap and coordinate all NAGAs
- Sesha: Data foundation, gossip sync, Ledger access
- Vasuki: Network bridge, serialization, external boundary
- Takshaka: Security guardian, toxicity detection, rate limiting
- NagaFloodManager: EventBus/SignalBus organic flooding
- NagaCommitWatcher: Commit pattern detection and alerting

Usage:
    from vibe_core.naga import NagaOrchestrator

    # During boot
    naga = NagaOrchestrator.bootstrap(
        ledger=kernel.ledger,
        correction_orchestrator=correction_orchestrator,
    )

    # Access components
    naga.sesha.get_top_hash()
    naga.takshaka.scan_toxicity("content")
    naga.commit_watcher.observe(commit_result)
"""

from vibe_core.naga.orchestrator import NagaOrchestrator

# Lazy imports for optional components
__all__ = [
    "NagaOrchestrator",
    # Services
    "SeshaService",
    "VasukiService",
    "TakshakaService",
    # Flooding
    "NagaFloodManager",
    "NagaFloodController",
    # Watching
    "NagaCommitWatcher",
    "CommitAlert",
]


def __getattr__(name: str):
    """Lazy import for optional components."""
    if name == "SeshaService":
        from vibe_core.naga.services.sesha import SeshaService

        return SeshaService
    elif name == "VasukiService":
        from vibe_core.naga.services.vasuki import VasukiService

        return VasukiService
    elif name == "TakshakaService":
        from vibe_core.naga.services.takshaka import TakshakaService

        return TakshakaService
    elif name == "NagaFloodManager":
        from vibe_core.naga.flood import NagaFloodManager

        return NagaFloodManager
    elif name == "NagaFloodController":
        from vibe_core.naga.flood import NagaFloodController

        return NagaFloodController
    elif name == "NagaCommitWatcher":
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        return NagaCommitWatcher
    elif name == "CommitAlert":
        from vibe_core.naga.commit_watcher import CommitAlert

        return CommitAlert
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
