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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x504e2862"  # GenesisByte: parampara % 37 == 0

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.SYS_WAKE,
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
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if not federation:
                return self.failure("NAGA Federation not initialized. Boot the kernel first: steward boot", exit_code=1)

            if brief:
                status = self._get_brief_status(federation)
            elif nagas_only:
                status = self._get_naga_status(federation)
            elif services_only:
                status = self._get_service_status(federation)
            else:
                status = self._get_full_status(federation)

            return self.success(
                status,
                data=(("phase", "wake"), ("position", "0"), ("mahajana", "prithu"), ("mode", self._get_mode(args))),
            )
        except Exception as e:
            return self.failure(f"Status check failed: {e}", exit_code=1)

    def _get_mode(self, args: List[str]) -> str:
        """Determine status mode from args."""
        if "--brief" in args:
            return "brief"
        if "--nagas" in args:
            return "nagas"
        if "--services" in args:
            return "services"
        return "full"

    def _get_brief_status(self, federation: any) -> str:
        """Get one-line status summary."""
        ready = federation.is_ready()
        status_str = "HEALTHY" if ready else "DEGRADED"
        return f"[PRITHU] NAGA Federation: {status_str}"

    def _get_naga_status(self, federation: any) -> str:
        """Get NAGA federation status."""
        lines = [
            "[PRITHU] NAGA Federation Status",
            "=" * 60,
        ]

        try:
            if federation.sesha:
                s = federation.sesha.get_status()
                lines.append(f"  SESHA (Foundation):  {'OK' if s.healthy else 'DEGRADED'}")

            if federation.vasuki:
                v = federation.vasuki.get_status()
                lines.append(f"  VASUKI (Bridge):     {'OK' if v.healthy else 'DEGRADED'}")

            if federation.takshaka:
                t = federation.takshaka.get_status()
                lines.append(f"  TAKSHAKA (Guardian): {'OK' if t.healthy else 'DEGRADED'} [trust={t.trust_mode}]")

            if federation.flood_manager:
                f = federation.flood_manager.get_status()
                lines.append(
                    f"  FLOOD MANAGER:       {'ACTIVE' if f.get('active') else 'INACTIVE'} [{f.get('total_observations', 0)} obs]"
                )

            if federation.commit_watcher:
                c = federation.commit_watcher.get_stats()
                lines.append(
                    f"  COMMIT WATCHER:      {c.get('total_observed', 0)} observed, {c.get('alerts_generated', 0)} alerts"
                )
        except Exception as e:
            lines.append(f"  Error querying NAGAs: {e}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _get_service_status(self, federation: any) -> str:
        """Get service health status."""
        lines = [
            "[PRITHU] Service Health",
            "=" * 60,
        ]

        # Query ServiceRegistry for key protocols
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.naga import IntelBridgeProtocol
        from vibe_core.protocols.universal import SyncProtocol

        intel = ServiceRegistry.get(IntelBridgeProtocol)
        sync = ServiceRegistry.get(SyncProtocol)

        lines.append(f"  Intel Bridge        : {'HEALTHY' if intel else 'NOT FOUND'}")
        lines.append(f"  Sync Protocol       : {'HEALTHY' if sync else 'NOT FOUND'}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _get_full_status(self, federation: any) -> str:
        """Get full system status."""
        ready = federation.is_ready()
        lines = [
            "[PRITHU] System Status - SYS_WAKE",
            "=" * 60,
            f"\n  Overall: {'HEALTHY' if ready else 'DEGRADED'}",
        ]

        lines.append("\n  NAGA Federation Components:")
        lines.append(self._get_naga_status(federation))

        lines.append("\n  MANTRA STATE:")
        lines.append("    Phase: WAKE (Position 0)")
        lines.append("    OpCode: SYS_WAKE")
        lines.append("    Mahajana: PRITHU (The Avatara King)")

        lines.append("\n" + "=" * 60)
        lines.append('"Prithu made the earth yield - status reveals all."')
        return "\n".join(lines)


# Export for direct import
__all__ = ["StatusCommand"]
