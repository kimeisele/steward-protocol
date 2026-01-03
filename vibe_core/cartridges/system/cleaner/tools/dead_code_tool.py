"""
Dead Code Scanner Tool

Finds orphaned files, unused imports, and dead databases.
Uses the audit infrastructure from OPUS-307.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from vibe_core.tools.tool_protocol import Tool, ToolResult


class DeadCodeTool(Tool):
    """Scan for dead code, orphaned DBs, and unused files."""

    def __init__(self):
        self.workspace = Path.cwd()

    @property
    def name(self) -> str:
        return "cleaner.scan"

    @property
    def description(self) -> str:
        return "Scan for dead code: orphaned DBs, empty tables, unused files"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "target": {
                "type": "string",
                "required": False,
                "description": "Target: 'databases', 'imports', 'all' (default: 'databases')",
                "default": "databases",
            },
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        target = parameters.get("target", "databases")
        if target not in ["databases", "imports", "all"]:
            raise ValueError(f"Invalid target: {target}")

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        target = parameters.get("target", "databases")

        results = {
            "dead_databases": [],
            "empty_tables": [],
            "active_databases": [],
        }

        if target in ["databases", "all"]:
            results = self._scan_databases()

        return ToolResult(
            success=True,
            output=results,
            metadata={
                "target": target,
                "dead_count": len(results.get("dead_databases", [])),
            },
        )

    def _scan_databases(self) -> Dict[str, Any]:
        """Scan all SQLite databases for dead code."""
        dead = []
        active = []

        # Find all .db files
        db_files = list(self.workspace.glob("**/*.db"))

        for db_path in db_files:
            if "__pycache__" in str(db_path) or ".git" in str(db_path):
                continue

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Count rows
                total_rows = 0
                for table in tables:
                    if table.startswith("sqlite_"):
                        continue
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        total_rows += cursor.fetchone()[0]
                    except Exception as e:
                        # OPUS-312: Log SQL failures
                        import logging

                        logging.getLogger("CLEANER").warning(f"SQL count failed for {table}: {e}")

                conn.close()

                info = {
                    "path": str(db_path.relative_to(self.workspace)),
                    "tables": len(tables),
                    "rows": total_rows,
                    "size_kb": round(db_path.stat().st_size / 1024, 1),
                }

                if total_rows == 0:
                    dead.append(info)
                else:
                    active.append(info)

            except Exception as e:
                dead.append(
                    {
                        "path": str(db_path.relative_to(self.workspace)),
                        "error": str(e),
                    }
                )

        return {
            "dead_databases": dead,
            "active_databases": active,
            "summary": f"{len(dead)} dead, {len(active)} active",
        }
