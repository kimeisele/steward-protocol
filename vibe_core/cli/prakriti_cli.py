"""
OPUS-307: Prakriti CLI - The Soul Made Visible

GAD-000 COMPLIANT: The state engine is now observable.

"You cannot maintain what you cannot see."

Usage:
    steward prakriti status              Show current state across all layers
    steward prakriti guna                Show Guna distribution (Sattva/Rajas/Tamas)
    steward prakriti snapshot            Take complete state snapshot
    steward prakriti verify              Verify workspace consistency
    steward prakriti diff [ref]          Show changes from ref (default: HEAD~1)
    steward prakriti layers              Show layer capabilities
    steward prakriti session             Show current session info
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("PRAKRITI_CLI")


@register_cli
class PrakritiCLI:
    """
    Prakriti CLI - Window into the State Engine.

    Makes the invisible visible. GAD-000 compliance for state observability.
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="prakriti",
            description="State Engine CLI - The Soul Made Visible",
            domain="state",
            subcommands=["status", "guna", "snapshot", "verify", "diff", "layers", "session"],
            tags=["prakriti", "state", "guna", "observability"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry point."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_usage()
            return 0

        cmd = args[0]
        remaining = args[1:]

        if cmd == "status":
            return self.cmd_status(remaining)
        elif cmd == "guna":
            return self.cmd_guna(remaining)
        elif cmd == "snapshot":
            return self.cmd_snapshot(remaining)
        elif cmd == "verify":
            return self.cmd_verify(remaining)
        elif cmd == "diff":
            return self.cmd_diff(remaining)
        elif cmd == "layers":
            return self.cmd_layers(remaining)
        elif cmd == "session":
            return self.cmd_session(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print(__doc__)

    def _get_prakriti(self):
        """Get or create Prakriti instance."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols import PrakritiProtocol

        prakriti = ServiceRegistry.get(PrakritiProtocol)
        if prakriti is None:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti()
        return prakriti

    def _get_guna_classifier(self):
        """Get GunaClassifier for state diagnosis."""
        from vibe_core.state.guna_classifier import GunaClassifier

        return GunaClassifier()

    # =========================================================================
    # Commands
    # =========================================================================

    def cmd_status(self, args: List[str]) -> int:
        """Show current state across all layers."""
        as_json = "--json" in args

        prakriti = self._get_prakriti()

        status = {
            "workspace": str(prakriti.workspace),
            "branch": prakriti.branch,
            "is_dirty": prakriti.is_dirty,
            "layers": {
                "sthula": {
                    "git": "active",
                    "files": "active",
                    "ledger": "active",
                },
                "prana": {
                    "kernel": prakriti.kernel.status() if prakriti.kernel else "not injected",
                    "ephemeral": "active",
                },
                "purusha": {
                    "personas": "active",
                },
            },
        }

        # Add session info if available
        if prakriti.session:
            status["session"] = {
                "id": prakriti.session.session_id,
                "commits": prakriti.session.commit_count,
                "crash_recovery": prakriti.session.crash_recovery,
            }

        if as_json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("🕉️  PRAKRITI STATUS - The State Engine")
            print("=" * 60)
            print(f"\n📁 Workspace: {status['workspace']}")
            print(f"🌿 Branch:    {status['branch']}")
            print(f"💫 Dirty:     {'Yes (Rajas)' if status['is_dirty'] else 'No (Sattva)'}")

            print("\n📊 LAYERS:")
            print("  STHULA (Physical):")
            print("    ├── git:    ✅ active")
            print("    ├── files:  ✅ active")
            print("    └── ledger: ✅ active")

            print("  PRANA (Runtime):")
            kernel_status = status["layers"]["prana"]["kernel"]
            if isinstance(kernel_status, dict):
                print("    ├── kernel: ✅ injected")
            else:
                print(f"    ├── kernel: ⚠️  {kernel_status}")
            print("    └── ephemeral: ✅ active")

            print("  PURUSHA (Identity):")
            print("    └── personas: ✅ active")

            if "session" in status:
                print("\n🔐 SESSION:")
                print(f"    ID:      {status['session']['id'][:8]}...")
                print(f"    Commits: {status['session']['commits']}")

            print("\n" + "=" * 60)

        return 0

    def cmd_guna(self, args: List[str]) -> int:
        """Show Guna distribution across state paths."""
        as_json = "--json" in args
        deep = "--deep" in args

        classifier = self._get_guna_classifier()

        # Scan key state paths
        state_paths = [
            Path(".vibe/state"),
            Path(".prakriti"),
            Path("data"),
            Path("config"),
        ]

        classifications = []
        guna_counts = {"sattva": 0, "rajas": 0, "tamas": 0}

        for base_path in state_paths:
            if not base_path.exists():
                continue

            if deep:
                # Scan all files
                for path in base_path.rglob("*"):
                    if path.is_file():
                        result = classifier.classify(path)
                        classifications.append(result.to_dict())
                        guna_counts[result.guna.value] += 1
            else:
                # Just classify the directory
                result = classifier.classify(base_path)
                classifications.append(result.to_dict())
                guna_counts[result.guna.value] += 1

        total = sum(guna_counts.values())
        percentages = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in guna_counts.items()}

        output = {
            "total_paths": total,
            "distribution": guna_counts,
            "percentages": percentages,
            "health": "healthy" if guna_counts["tamas"] == 0 else "needs_attention",
        }

        if deep:
            output["classifications"] = classifications

        if as_json:
            print(json.dumps(output, indent=2))
        else:
            print("\n" + "=" * 60)
            print("🕉️  GUNA DISTRIBUTION - State Health")
            print("=" * 60)

            # Visual bar
            bar_width = 40
            sattva_bar = int(percentages["sattva"] / 100 * bar_width)
            rajas_bar = int(percentages["rajas"] / 100 * bar_width)
            tamas_bar = bar_width - sattva_bar - rajas_bar

            print(f"\n{'🟢' * sattva_bar}{'🟡' * rajas_bar}{'🔴' * tamas_bar}")

            print(f"\n  SATTVA (Balance):   {guna_counts['sattva']:>3} ({percentages['sattva']}%)")
            print(f"  RAJAS (Activity):   {guna_counts['rajas']:>3} ({percentages['rajas']}%)")
            print(f"  TAMAS (Inertia):    {guna_counts['tamas']:>3} ({percentages['tamas']}%)")

            print(f"\n  Total Paths: {total}")
            print(f"  Health: {'✅ Healthy' if output['health'] == 'healthy' else '⚠️  Needs Attention'}")

            if guna_counts["tamas"] > 0:
                print("\n  ⚠️  Tamas paths detected. Run 'prakriti guna --deep --json' for details.")

            print("\n" + "=" * 60)

        return 0

    def cmd_snapshot(self, args: List[str]) -> int:
        """Take complete state snapshot."""
        as_json = "--json" in args

        prakriti = self._get_prakriti()
        snapshot = prakriti.snapshot()

        output = {
            "timestamp": snapshot.timestamp,
            "git": snapshot.git,
            "files": snapshot.files,
            "kernel": snapshot.kernel,
            "ephemeral": snapshot.ephemeral,
            "personas": snapshot.personas,
        }

        if as_json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("📸 STATE SNAPSHOT")
            print("=" * 60)
            print(f"\nTimestamp: {snapshot.timestamp}")

            print("\n🗂️  GIT:")
            if snapshot.git:
                for k, v in snapshot.git.items():
                    print(f"    {k}: {v}")

            print("\n📁 FILES:")
            if snapshot.files:
                dirty = snapshot.files.get("dirty_count", 0)
                print(f"    Dirty files: {dirty}")

            print("\n⚡ KERNEL:")
            if snapshot.kernel:
                for k, v in list(snapshot.kernel.items())[:5]:
                    print(f"    {k}: {v}")

            print("\n" + "=" * 60)

        return 0

    def cmd_verify(self, args: List[str]) -> int:
        """Verify workspace consistency."""
        as_json = "--json" in args

        prakriti = self._get_prakriti()
        result = prakriti.verify()

        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("🔍 WORKSPACE VERIFICATION")
            print("=" * 60)

            status_icon = "✅" if result["status"] == "ok" else "⚠️"
            print(f"\nStatus: {status_icon} {result['status'].upper()}")
            print(f"Branch: {result.get('git_branch', 'N/A')}")
            print(f"SHA:    {result.get('git_sha', 'N/A')}")

            if result.get("issues"):
                print(f"\nIssues ({len(result['issues'])}):")
                for issue in result["issues"]:
                    severity_icon = {"warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(issue.get("severity"), "•")
                    print(f"  {severity_icon} [{issue['layer']}] {issue['issue']}")

            print("\n" + "=" * 60)

        return 0 if result["status"] == "ok" else 1

    def cmd_diff(self, args: List[str]) -> int:
        """Show changes from ref."""
        as_json = "--json" in args
        ref = "HEAD~1"

        for arg in args:
            if not arg.startswith("--"):
                ref = arg
                break

        prakriti = self._get_prakriti()

        if ref == "main":
            diff = prakriti.diff_main()
        else:
            diff = prakriti.diff(ref)

        output = {
            "base_ref": ref,
            "files_changed": diff.files_changed,
            "insertions": diff.insertions,
            "deletions": diff.deletions,
            "files": diff.files if hasattr(diff, "files") else [],
        }

        if as_json:
            print(json.dumps(output, indent=2))
        else:
            print("\n" + "=" * 60)
            print(f"📊 DIFF: {ref} → HEAD")
            print("=" * 60)
            print(f"\n  Files changed: {diff.files_changed}")
            print(f"  Insertions:    +{diff.insertions}")
            print(f"  Deletions:     -{diff.deletions}")

            if hasattr(diff, "files") and diff.files:
                print("\n  Changed files:")
                for f in diff.files[:10]:
                    print(f"    • {f}")
                if len(diff.files) > 10:
                    print(f"    ... and {len(diff.files) - 10} more")

            print("\n" + "=" * 60)

        return 0

    def cmd_layers(self, args: List[str]) -> int:
        """Show layer capabilities."""
        as_json = "--json" in args

        prakriti = self._get_prakriti()
        capabilities = prakriti.get_capabilities()

        if as_json:
            print(json.dumps(capabilities, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("🏛️  PRAKRITI LAYER ARCHITECTURE")
            print("=" * 60)

            print(f"\nVersion: {capabilities.get('version', 'N/A')}")
            print(f"Workspace: {capabilities.get('workspace', 'N/A')}")

            print("\n📋 OPERATIONS:")
            for op in capabilities.get("operations", []):
                print(f"    • {op}")

            print("\n🏗️  LAYERS:")
            layers = capabilities.get("layers", {})
            for layer_name, layer_info in layers.items():
                status = layer_info.get("status", "unknown")
                status_icon = "✅" if status == "active" else "⚠️"
                print(f"\n  {layer_name.upper()} ({status_icon} {status}):")
                for comp in layer_info.get("components", []):
                    print(f"    └── {comp}")

            print("\n" + "=" * 60)

        return 0

    def cmd_session(self, args: List[str]) -> int:
        """Show current session info."""
        as_json = "--json" in args

        prakriti = self._get_prakriti()

        if prakriti.session is None:
            if as_json:
                print(json.dumps({"session": None, "message": "No active session"}))
            else:
                print("\n⚠️  No active session. Kernel not booted?")
            return 1

        session = prakriti.session
        output = {
            "session_id": session.session_id,
            "boot_time": session.boot_time,
            "boot_commit": session.boot_commit,
            "pid": session.pid,
            "last_commit": session.last_commit,
            "commit_count": session.commit_count,
            "crash_recovery": session.crash_recovery,
        }

        if as_json:
            print(json.dumps(output, indent=2))
        else:
            print("\n" + "=" * 60)
            print("🔐 SESSION INFO")
            print("=" * 60)
            print(f"\n  Session ID:     {session.session_id}")
            print(f"  PID:            {session.pid}")
            print(f"  Boot Commit:    {session.boot_commit[:8]}...")
            print(f"  Commits Made:   {session.commit_count}")
            print(f"  Last Commit:    {session.last_commit[:8] if session.last_commit else 'None'}...")
            print(f"  Crash Recovery: {'Yes' if session.crash_recovery else 'No'}")
            print("\n" + "=" * 60)

        return 0


def main():
    """Entry point for direct execution."""
    cli = PrakritiCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
