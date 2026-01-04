"""
NAGA Federation - The Invisible Guardians.

Sesha (Data), Vasuki (Network), Takshaka (Security)

"Niemand darf es merken" - they infiltrate invisibly.

Usage:
    from vibe_core.naga import NagaOrchestrator

    # During boot
    naga = NagaOrchestrator.bootstrap(
        ledger=kernel.ledger,
        correction_orchestrator=correction_orchestrator,
    )
"""

from vibe_core.naga.orchestrator import NagaOrchestrator

__all__ = ["NagaOrchestrator"]
