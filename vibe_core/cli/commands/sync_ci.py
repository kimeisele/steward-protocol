"""
OUROBOROS: Sync CI Command

Syncs CI/CD failures from GitHub Actions into the local Knowledge Graph.
This enables the self-healing loop to learn from remote failures.

Usage:
    steward sync-ci              # Sync latest CI results
    steward sync-ci --workflow steward-ci.yml
    steward sync-ci --status     # Show sync status
"""

from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class SyncCICommand(BaseCommand):
    """Sync CI/CD violations to local Knowledge Graph."""

    name = "sync-ci"
    description = "Sync CI/CD failures to Knowledge Graph (Ouroboros)"
    source = "ouroboros"
    tags = ["ci", "sync", "ouroboros", "self-healing"]

    _parameters = [
        ParameterSpec(
            name="--workflow",
            param_type=ParameterType.STRING,
            required=False,
            default="steward-ci.yml",
            description="GitHub Actions workflow file to sync",
        ),
        ParameterSpec(
            name="--status",
            param_type=ParameterType.BOOLEAN,
            required=False,
            default=False,
            description="Show sync status instead of syncing",
        ),
        ParameterSpec(
            name="--json",
            param_type=ParameterType.BOOLEAN,
            required=False,
            default=False,
            description="Output as JSON",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute CI sync."""
        import json as json_lib
        from dataclasses import asdict

        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.universal import SyncProtocol

        # Parse args
        workflow = "steward-ci.yml"
        show_status = "--status" in args
        as_json = "--json" in args

        for i, arg in enumerate(args):
            if arg == "--workflow" and i + 1 < len(args):
                workflow = args[i + 1]

        # Use Registry (The Bond) - Get the active Sync implementation
        sync = ServiceRegistry.get(SyncProtocol)
        if not sync:
            return CommandResult.error("SyncProtocol service not available")

        if show_status:
            status = sync.get_sync_status()

            # Access details from legacy dict if present
            details = getattr(status, "details", {})
            repo = details.get("repo", "unknown")
            last_sync = status.last_sync
            gh_cli_available = details.get("gh_cli_available", False)

            if as_json:
                return CommandResult.success(json_lib.dumps(asdict(status), indent=2, default=str))

            lines = [
                "🐍 OUROBOROS CI Sync Status",
                "=" * 40,
                f"Repository: {repo}",
                f"Last sync: {last_sync or 'Never'}",
                f"GitHub CLI: {'✅ Available' if gh_cli_available else '❌ Not available'}",
            ]

            if not gh_cli_available:
                lines.append("")
                lines.append("⚠️  Install gh CLI: brew install gh && gh auth login")

            return CommandResult.success("\n".join(lines))

        # Perform sync
        # Note: Protocol uses sync(), not sync_latest()
        result = sync.sync()

        if as_json:
            return CommandResult.success(json_lib.dumps(asdict(result), indent=2, default=str))

        # Format human-readable output
        lines = [
            "🐍 OUROBOROS CI Sync",
            "=" * 40,
            f"Result: {'Success' if result.success else 'Failed'}",
            f"Items Synced: {result.items_synced}",
            "",
        ]

        if result.items_synced > 0:
            lines.append(f"✅ Ingested {result.items_synced} violations to Knowledge Graph")
            lines.append("   The system will learn from these failures.")
        elif result.success:
            lines.append("✅ CI sync completed - no new violations to ingest")
        else:
            lines.append("⚠️  Sync failed")

        if result.errors:
            lines.append("")
            lines.append("Errors:")
            for err in result.errors:
                lines.append(f"  ❌ {err}")

        return CommandResult.success("\n".join(lines))
