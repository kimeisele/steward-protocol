"""
INTEL COMMAND - SHUKA's Vision
==============================

MAHAJANA: SHUKA (The Visionary)
OPCODE: FETCH_RES (Position 8)
PHASE: SERVE

WHY SHUKA?
- Shuka can see past, present, and future
- He narrated Bhagavatam with perfect vision
- Intelligence is about SEEING clearly

MANTRA WORD: HARE (Position 8)
"Hare dispels illusion and reveals truth"

Note: While PARASHURAMA is the Avatara at position 8,
SHUKA semantically owns intelligence operations.

Usage:
    naga intel                    # Get recent intel
    naga intel --critical         # Get critical items only
    naga intel --threats          # Get active threats
    naga intel --category security # Filter by category
"""

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.FETCH_RES,
    name="intel",
    help_text="Query NAGA intelligence (SHUKA's vision)")
class IntelCommand(NagaCommandBase):
    """
    Intel command implementation.

    Bridges NAGA collective intelligence to CLI.
    Accesses observations from all NAGAs.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute intel query.

        Args:
            args: Flags for filtering intel

        Returns:
            NagaCommandResult with intel items or error
        """
        # Parse flags
        critical_only = "--critical" in args
        threats_only = "--threats" in args
        category = None

        if "--category" in args:
            try:
                idx = args.index("--category")
                category = args[idx + 1]
            except (IndexError, ValueError):
                return self.failure(
                    "Invalid --category flag. Usage: --category <type>",
                    exit_code=1)

        try:
            # Get intel bridge
            intel = self._get_intel(
                critical_only=critical_only,
                threats_only=threats_only,
                category=category)

            if not intel:
                return self.success(
                    "[SHUKA] No intelligence available.",
                    data=(("count", "0")))

            return self.success(
                intel,
                data=(
                    ("critical_only", str(critical_only)),
                    ("threats_only", str(threats_only)),
                    ("category", category or "all"),
                    ("mahajana", "shuka")))
        except Exception as e:
            return self.failure(
                f"Intel service unavailable: {e}",
                exit_code=2)

    def _get_intel(
        self,
        critical_only: bool = False,
        threats_only: bool = False,
        category: str = None) -> str:
        """
        Fetch intelligence from NAGA bridge.

        This is a placeholder - actual implementation would use
        IntelBridgeProtocol.
        """
        # Placeholder: actual implementation would use:
        # - vibe_core.protocols.naga.intel_bridge.IntelBridgeProtocol
        # - NullIntelBridge as fallback

        filters = []
        if critical_only:
            filters.append("critical")
        if threats_only:
            filters.append("threats")
        if category:
            filters.append(f"category:{category}")

        filter_str = ", ".join(filters) if filters else "none"
        return f"[SHUKA] Intel query complete (filters: {filter_str})"


# Export for direct import
__all__ = ["IntelCommand"]
