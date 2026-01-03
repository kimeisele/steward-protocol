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

        from vibe_core.ouroboros.sync import CISyncService

        # Parse args
        workflow = "steward-ci.yml"
        show_status = "--status" in args
        as_json = "--json" in args

        for i, arg in enumerate(args):
            if arg == "--workflow" and i + 1 < len(args):
                workflow = args[i + 1]

        sync = CISyncService()

        if show_status:
            status = sync.get_sync_status()
            if as_json:
                return CommandResult.success(json_lib.dumps(status, indent=2))

            lines = [
                "🐍 OUROBOROS CI Sync Status",
                "=" * 40,
                f"Repository: {status['repo']}",
                f"Last sync: {status['last_sync'] or 'Never'}",
                f"GitHub CLI: {'✅ Available' if status['gh_cli_available'] else '❌ Not available'}",
            ]

            if not status["gh_cli_available"]:
                lines.append("")
                lines.append("⚠️  Install gh CLI: brew install gh && gh auth login")

            return CommandResult.success("\n".join(lines))

        # Perform sync
        result = sync.sync_latest(workflow=workflow)

        if as_json:
            return CommandResult.success(json_lib.dumps(result, indent=2))

        # Format human-readable output
        lines = [
            "🐍 OUROBOROS CI Sync",
            "=" * 40,
            f"Workflow: {result['workflow']}",
            f"Run ID: {result.get('run_id', 'N/A')}",
            f"Status: {result.get('run_conclusion', 'N/A')}",
            "",
        ]

        if result["violations_ingested"] > 0:
            lines.append(f"✅ Ingested {result['violations_ingested']} violations to Knowledge Graph")
            lines.append("   The system will learn from these failures.")
        elif result.get("run_conclusion") == "success":
            lines.append("✅ CI passed - no violations to ingest")
        else:
            lines.append("⚠️  No violations extracted")

        if result["errors"]:
            lines.append("")
            lines.append("Errors:")
            for err in result["errors"]:
                lines.append(f"  ❌ {err}")

        return CommandResult.success("\n".join(lines))
