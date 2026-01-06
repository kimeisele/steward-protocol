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
- NagaProxy: Universal wrapper (Balarama Pattern)

Usage:
    from vibe_core.naga import NagaOrchestrator, NagaProxy

    # During boot
    naga = NagaOrchestrator.bootstrap(
        ledger=kernel.ledger,
        correction_orchestrator=correction_orchestrator,
    )

    # Wrap any service with observation (Balarama Pattern)
    wrapped = NagaProxy(real_service)
    wrapped.tick()  # Observed by Narada, timed by Chitragupta

    # Access components
    naga.sesha.get_top_hash()
    naga.takshaka.scan_toxicity("content")
    naga.commit_watcher.observe(commit_result)
"""

# HOLON UPGRADE: ALL imports are lazy to prevent import cycles
# NagaOrchestrator is loaded on first access via __getattr__

# Lazy imports for optional components
__all__ = [
    "NagaOrchestrator",
    # Services (Infrastructure Layer - 8)
    "SeshaService",
    "VasukiService",
    "TakshakaService",
    "KaliyaService",
    "KarkotakaService",
    "KulikaService",
    "PadmaService",
    "ShankhaService",
    # Services (Governance Layer - 3)
    "NaradaService",
    "ChitraguptaService",
    "PrahladService",
    # State Proxy (Der Kommissar)
    "NagaStateProxy",
    # Balarama Pattern (Universal Wrapper)
    "NagaProxy",
    "wrap_service",
    # Flooding
    "NagaFloodManager",
    "NagaFloodController",
    # Watching
    "NagaCommitWatcher",
    "CommitAlert",
]


def __getattr__(name: str):
    """Lazy import for all components - HOLON PATTERN."""
    if name == "NagaOrchestrator":
        from vibe_core.naga.orchestrator import NagaOrchestrator

        return NagaOrchestrator
    elif name == "NagaStateProxy":
        from vibe_core.services.naga.state_proxy import NagaStateProxy

        return NagaStateProxy
    elif name == "SeshaService":
        from vibe_core.naga.services.sesha import SeshaService

        return SeshaService
    elif name == "VasukiService":
        from vibe_core.naga.services.vasuki import VasukiService

        return VasukiService
    elif name == "TakshakaService":
        from vibe_core.naga.services.takshaka import TakshakaService

        return TakshakaService
    elif name == "KulikaService":
        from vibe_core.naga.services.kulika import KulikaService

        return KulikaService
    elif name == "KarkotakaService":
        from vibe_core.naga.services.karkotaka import KarkotakaService

        return KarkotakaService
    elif name == "PadmaService":
        from vibe_core.naga.services.padma import PadmaService

        return PadmaService
    elif name == "ShankhaService":
        from vibe_core.naga.services.shankha import ShankhaService

        return ShankhaService
    elif name == "KaliyaService":
        from vibe_core.naga.services.kaliya import KaliyaService

        return KaliyaService
    elif name == "NaradaService":
        from vibe_core.naga.services.narada import NaradaService

        return NaradaService
    elif name == "ChitraguptaService":
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        return ChitraguptaService
    elif name == "PrahladService":
        from vibe_core.naga.services.prahlad import PrahladService

        return PrahladService
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
    elif name == "NagaProxy":
        from vibe_core.naga.proxy import NagaProxy

        return NagaProxy
    elif name == "wrap_service":
        from vibe_core.naga.proxy import wrap_service

        return wrap_service
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
