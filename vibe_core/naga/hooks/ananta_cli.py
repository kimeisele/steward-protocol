"""
ANANTA CLI HOOK - The Flood (Gene Splicer)

Intercepts CLI commands at PRE_EXECUTE to inject Genes (Mixin Capabilities)
into the Handler Instance.

This is the "Positive Pathogen" mechanism for the CLI.
Ananta (Level -1) floods the Handler (Level 0) with capabilities.

Usage:
    hook = AnantaCLIHook(ananta_service)
    chain.register(hook)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x4b94822f"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Optional

from vibe_core.protocols.cli_execution import (
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
)
from vibe_core.protocols.naga.ananta import AnantaProtocol

logger = logging.getLogger("ANANTA_CLI")


class AnantaCLIHook(CLIHookProtocol):
    """
    Floods CLI Handlers with NAGA genes.
    """

    def __init__(self, ananta: AnantaProtocol):
        self._ananta = ananta

    @property
    def hook_id(self) -> str:
        return "ananta"

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        """
        Inject genes at PRE_EXECUTE phase.
        """
        if phase != CLIExecutionPhase.PRE_EXECUTE:
            return CLIHookResult(allow=True)

        handler = context.handler
        if not handler:
            # No handler to flood (maybe legacy command?)
            return CLIHookResult(allow=True)

        try:
            # Consult Ananta about this handler class
            # (Ananta analyzes service -> proposes flood)
            # But here we flood the INSTANCE directly via flood_instance
            # Wait, AnantaProtocol (interface) only has create_flooded_class.
            # AnantaService (implementation) has flood_instance (I added it).
            # We should assume AnantaService behavior or extend Protocol.

            # The protocol says create_flooded_class.
            # The service has flood_instance.
            # We should use flood_instance if available.

            if hasattr(self._ananta, "flood_instance"):
                # Determine genes based on command domain or metadata?
                # For now, we inject standard genes if they are missing.
                # Or let Ananta decide based on analyze_service logic.

                # We ask Ananta to flood with whatever it thinks is best.
                # flood_instance will call analyze_service internaly.

                # We can also pass specific genes if needed (e.g. from token caps).
                genes = []
                # Check token capabilities?
                if context.capability_token:
                    # Map capabilities to genes? E.g. "cli.ledger" -> "sesha"
                    # This logic should be in Ananta or here?
                    pass

                self._ananta.flood_instance(handler, genes=genes)
                logger.debug(f"🌊 Flooded handler {type(handler).__name__} via Ananta")

            else:
                logger.warning("Ananta service missing flood_instance method")

        except Exception as e:
            logger.error(f"Failed to flood handler: {e}")
            # Do not block execution on flood failure (Graceful Degradation)
            return CLIHookResult(allow=True, reason=f"Flood failed: {e}")

        return CLIHookResult(allow=True, reason="Flooded")
