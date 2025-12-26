"""
OPUS-307 Phase 4: Audit CLI

Self-awareness for the Steward system.

Usage:
    steward audit databases      Find all DBs and their status
    steward audit usage          Check tool usage from ledger
    steward audit full           Complete system audit
    steward audit split-brain    Check for database inconsistencies
"""

import json
import logging
import sys
from pathlib import Path
from typing import List

from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("AUDIT_CLI")


@register_cli
class AuditCLI:
    """
    System Audit CLI.

    Self-aware diagnostics for finding dead code, split databases, and orphaned components.
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="audit",
            description="System Audit - Self-aware diagnostics",
            domain="system",
            subcommands=["databases", "usage", "full", "split-brain"],
            tags=["audit", "diagnostics", "dead-code"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry point."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_usage()
            return 0

        cmd = args[0]
        remaining = args[1:]
        as_json = "--json" in remaining

        if cmd == "databases":
            return self.cmd_databases(as_json)
        elif cmd == "usage":
            return self.cmd_usage(as_json)
        elif cmd == "full":
            return self.cmd_full(as_json)
        elif cmd == "split-brain":
            return self.cmd_split_brain(as_json)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print(__doc__)

    def _get_audit(self):
        """Get SystemAudit instance."""
        from vibe_core.tools.system_audit import SystemAudit

        return SystemAudit()

    def cmd_databases(self, as_json: bool) -> int:
        """List all databases."""
        audit = self._get_audit()
        dbs = audit.run_database_audit()

        if as_json:
            print(
                json.dumps(
                    [
                        {
                            "path": str(db.path),
                            "size_kb": round(db.size_bytes / 1024, 1),
                            "category": db.category,
                            "is_empty": db.is_empty,
                            "tables": db.tables,
                            "row_count": sum(db.row_counts.values()),
                        }
                        for db in dbs
                    ],
                    indent=2,
                )
            )
        else:
            print(f"\n{'=' * 60}")
            print(f"DATABASE INVENTORY ({len(dbs)} found)")
            print(f"{'=' * 60}\n")

            # Group by category
            by_cat = {}
            for db in dbs:
                if db.category not in by_cat:
                    by_cat[db.category] = []
                by_cat[db.category].append(db)

            for cat, cat_dbs in sorted(by_cat.items()):
                print(f"[{cat.upper()}]")
                for db in cat_dbs:
                    size = db.size_bytes / 1024
                    rows = sum(db.row_counts.values())
                    status = "EMPTY" if db.is_empty else f"{rows} rows"
                    print(f"  {db.path.name:<35} {size:>8.1f}KB  {status}")
                print()

        return 0

    def cmd_usage(self, as_json: bool) -> int:
        """Show tool usage from ledger."""
        audit = self._get_audit()
        usage = audit.run_usage_audit()

        if as_json:
            print(
                json.dumps(
                    [
                        {
                            "tool": t.tool_name,
                            "calls": t.call_count,
                            "success_rate": round(t.success_rate, 2),
                        }
                        for t in usage
                    ],
                    indent=2,
                )
            )
        else:
            print(f"\n{'=' * 60}")
            print("TOOL USAGE (from ledger)")
            print(f"{'=' * 60}\n")

            if usage:
                for t in usage:
                    print(f"  {t.tool_name:<40} {t.call_count:>5} calls")

                # Show unused tools
                from vibe_core.cli.cartridge_bridge import LazyCartridgeRegistry

                registry = LazyCartridgeRegistry.get_instance()
                registry.scan_manifests()

                all_tools = set()
                for cart in registry.list_cartridges():
                    for tool in cart.tool_stubs.values():
                        all_tools.add(tool.tool_id)

                used_tools = {t.tool_name for t in usage}
                unused = all_tools - used_tools

                print(f"\n  Discovered: {len(all_tools)} tools")
                print(f"  Used:       {len(used_tools)} tools")
                print(f"  Unused:     {len(unused)} tools ({round(len(unused) / len(all_tools) * 100)}%)")
            else:
                print("  No tool calls recorded in ledger")

        return 0

    def cmd_full(self, as_json: bool) -> int:
        """Run full system audit."""
        audit = self._get_audit()
        report = audit.run_full_audit()

        if as_json:
            print(audit.format_json(report))
        else:
            print(audit.format_report(report))

        return 0

    def cmd_split_brain(self, as_json: bool) -> int:
        """Check for database split-brain condition."""
        audit = self._get_audit()
        dbs = audit.run_database_audit()

        # Check .vibe vs data
        vibe_dbs = [db for db in dbs if ".vibe" in str(db.path)]
        data_dbs = [db for db in dbs if "data/" in str(db.path) and db.category == "production"]

        vibe_empty = all(db.is_empty for db in vibe_dbs)
        data_has_content = any(not db.is_empty for db in data_dbs)

        is_split = vibe_empty and data_has_content

        if as_json:
            print(
                json.dumps(
                    {
                        "split_brain": is_split,
                        "vibe_databases": [
                            {
                                "path": str(db.path),
                                "is_empty": db.is_empty,
                            }
                            for db in vibe_dbs
                        ],
                        "data_databases": [
                            {
                                "path": str(db.path),
                                "is_empty": db.is_empty,
                                "rows": sum(db.row_counts.values()),
                            }
                            for db in data_dbs
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(f"\n{'=' * 60}")
            print("SPLIT-BRAIN ANALYSIS")
            print(f"{'=' * 60}\n")

            if is_split:
                print("  STATUS: SPLIT-BRAIN DETECTED\n")
                print("  Problem:")
                print("    .vibe/ databases are EMPTY")
                print("    data/ databases have CONTENT")
                print()
                print("  This means the system has two 'brains':")
                print("    - Components reading .vibe/ see empty state")
                print("    - Components reading data/ see real state")
                print()
                print("  Fix: Consolidate to single source of truth")
                print("  Option A: Move data/vibe_ledger.db -> .vibe/vibe.db")
                print("  Option B: Update all paths to use data/")
            else:
                print("  STATUS: OK - No split-brain detected")

            print(f"\n{'=' * 60}")

        return 1 if is_split else 0


def main():
    """Entry point."""
    cli = AuditCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
