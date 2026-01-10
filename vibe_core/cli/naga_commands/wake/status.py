"""
STATUS COMMAND - PRITHU's Wake
==============================

MAHAJANA: PRITHU (The Avatara King)
OPCODE: SYS_WAKE (Position 0)
PHASE: WAKE

WHY PRITHU?
- Prithu is the first king, who organized the world
- He made the earth yield her resources
- Status is about SEEING the system's state

MANTRA WORD: HARE (Position 0)
"Hare awakens the dormant consciousness"

Prithu is the HEAD of the WAKE phase - the Avatara who initiates.
Every cycle begins with SYS_WAKE, every status check with PRITHU.

Usage:
    naga status              # Full system status
    naga status --brief      # One-line summary
    naga status --nagas      # NAGA federation status
    naga status --services   # Service health
"""

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import (
    Mahajana,
    NagaCommandBase,
    NagaCommandResult,
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.SYS_WAKE,
    mahajana=Mahajana.PRITHU,
    name="status",
    help_text="System status (PRITHU's wake - first command of every cycle)",
)
class StatusCommand(NagaCommandBase):
    """
    Status command implementation.

    PRITHU awakens the system by reporting its state.
    This is position 0 - the HEAD of WAKE phase.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute status command.

        Args:
            args: Flags for status detail level

        Returns:
            NagaCommandResult with system status
        """
        # Parse flags
        brief = "--brief" in args
        nagas_only = "--nagas" in args
        services_only = "--services" in args

        try:
            if brief:
                status = self._get_brief_status()
            elif nagas_only:
                status = self._get_naga_status()
            elif services_only:
                status = self._get_service_status()
            else:
                status = self._get_full_status()

            return self.success(
                status,
                data=(
                    ("phase", "wake"),
                    ("position", "0"),
                    ("mahajana", "prithu"),
                    ("mode", self._get_mode(args)),
                ),
            )
        except Exception as e:
            return self.failure(
                f"Status check failed: {e}",
                exit_code=1,
            )

    def _get_mode(self, args: List[str]) -> str:
        """Determine status mode from args."""
        if "--brief" in args:
            return "brief"
        if "--nagas" in args:
            return "nagas"
        if "--services" in args:
            return "services"
        return "full"

    def _get_brief_status(self) -> str:
        """Get one-line status summary."""
        # Placeholder: actual implementation would query system
        return "[PRITHU] System AWAKE - All NAGAs operational"

    def _get_naga_status(self) -> str:
        """Get NAGA federation status."""
        # Placeholder: actual implementation would query NagaFederationProtocol
        lines = [
            "[PRITHU] NAGA Federation Status",
            "=" * 40,
            "  SESHA (Ledger)      : ACTIVE",
            "  VASUKI (Network)    : ACTIVE",
            "  TAKSHAKA (Security) : ACTIVE",
            "  KALIYA (Quarantine) : STANDBY",
            "  CHITRAGUPTA (Audit) : ACTIVE",
            "  PRAHLAD (Memory)    : ACTIVE",
            "  PADMA (Cache)       : ACTIVE",
            "  SHANKHA (Broadcast) : ACTIVE",
            "  KARKOTAKA (Crypto)  : ACTIVE",
            "  KULIKA (Schema)     : ACTIVE",
            "  ANANTA (Splicer)    : ACTIVE",
            "  GARUDA (Carrier)    : ACTIVE",
            "=" * 40,
            "Federation: 11/12 ACTIVE, 1/12 STANDBY",
        ]
        return "\n".join(lines)

    def _get_service_status(self) -> str:
        """Get service health status."""
        # Placeholder: actual implementation would query services
        lines = [
            "[PRITHU] Service Health",
            "=" * 40,
            "  Cognitive (MANAS)   : HEALTHY",
            "  Intel Bridge        : HEALTHY",
            "  Flood Protocol      : HEALTHY",
            "  Command Registry    : HEALTHY",
            "=" * 40,
            "Services: 4/4 HEALTHY",
        ]
        return "\n".join(lines)

    def _get_full_status(self) -> str:
        """Get full system status."""
        # Placeholder: actual implementation would aggregate all status
        lines = [
            "[PRITHU] System Status - SYS_WAKE Complete",
            "=" * 50,
            "",
            "PHASE: WAKE (Position 0)",
            "OPCODE: SYS_WAKE",
            "MAHAJANA: PRITHU (The First King)",
            "",
            "SYSTEM STATE:",
            "  Kernel        : RUNNING",
            "  Memory        : 42% used",
            "  Uptime        : 2h 34m",
            "",
            "NAGA FEDERATION:",
            "  Active NAGAs  : 11/12",
            "  Observations  : 1,247 (last hour)",
            "  Alerts        : 0 critical, 2 warnings",
            "",
            "PROTOCOLS:",
            "  Registered    : 47",
            "  Sealed        : 45",
            "  Coverage      : 96%",
            "",
            "=" * 50,
            "\"Prithu made the earth yield - status reveals all.\"",
        ]
        return "\n".join(lines)


# Export for direct import
__all__ = ["StatusCommand"]
