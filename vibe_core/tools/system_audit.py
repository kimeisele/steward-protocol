"""
OPUS-307 Phase 4: System Audit Tool

Self-aware diagnostics for the Steward system.
Finds dead code, duplicate databases, and orphaned components.

Usage:
    steward audit databases      # Find all DBs and their status
    steward audit imports        # Check what code is actually imported
    steward audit usage          # Check tool usage from ledger
    steward audit full           # Complete system audit
    steward audit consolidate    # Generate consolidation plan

This tool exists because:
    "You cannot maintain what you cannot see."
    "Blind deletion in a 99% system is suicide."
"""

import ast
import importlib.util
import json
import logging
import os
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("SYSTEM_AUDIT")


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class DatabaseInfo:
    """Information about a discovered database."""

    path: Path
    size_bytes: int
    tables: List[str]
    row_counts: Dict[str, int]
    last_modified: datetime
    created_by: List[str]  # Files that reference this path
    is_empty: bool
    category: str  # production, test, archive, unknown


@dataclass
class ImportInfo:
    """Information about module imports."""

    module_path: Path
    imports: Set[str]
    imported_by: Set[str]
    is_orphan: bool  # Not imported by anything


@dataclass
class ToolUsage:
    """Tool usage statistics from ledger."""

    tool_name: str
    call_count: int
    last_called: Optional[datetime]
    success_rate: float


@dataclass
class AuditReport:
    """Complete system audit report."""

    timestamp: datetime
    databases: List[DatabaseInfo]
    tool_usage: List[ToolUsage]
    import_orphans: List[str]
    recommendations: List[str]
    kill_list: List[str]  # Files/DBs safe to delete


# =============================================================================
# DATABASE AUDIT
# =============================================================================


class DatabaseAuditor:
    """Finds and analyzes all databases in the project."""

    def __init__(self, root: Path):
        self.root = root
        self.db_files: List[DatabaseInfo] = []

    def scan_all(self) -> List[DatabaseInfo]:
        """Find all .db files and analyze them."""
        db_paths = list(self.root.rglob("*.db"))

        for db_path in db_paths:
            if self._should_skip(db_path):
                continue

            info = self._analyze_db(db_path)
            if info:
                self.db_files.append(info)

        return self.db_files

    def _should_skip(self, path: Path) -> bool:
        """Skip certain directories."""
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
        ]
        return any(p in str(path) for p in skip_patterns)

    def _analyze_db(self, db_path: Path) -> Optional[DatabaseInfo]:
        """Analyze a single database file."""
        try:
            stat = db_path.stat()

            # Get tables and row counts
            tables = []
            row_counts = {}

            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Get row counts
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        row_counts[table] = cursor.fetchone()[0]
                    except Exception as e:
                        # SECURITY FIX B-P0-2: Log instead of silent failure
                        logger.warning(f"Failed to count rows in {table}: {e}")
                        row_counts[table] = -1

                conn.close()
            except Exception as e:
                logger.debug(f"Could not read {db_path}: {e}")

            # Find who creates/uses this DB
            created_by = self._find_references(db_path)

            # Categorize
            category = self._categorize_db(db_path, tables)

            # Check if empty
            total_rows = sum(v for v in row_counts.values() if v > 0)
            is_empty = total_rows == 0

            return DatabaseInfo(
                path=db_path,
                size_bytes=stat.st_size,
                tables=tables,
                row_counts=row_counts,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                created_by=created_by,
                is_empty=is_empty,
                category=category,
            )
        except Exception as e:
            logger.error(f"Failed to analyze {db_path}: {e}")
            return None

    def _find_references(self, db_path: Path) -> List[str]:
        """Find Python files that reference this database path."""
        references = []
        db_name = db_path.name

        # Search in vibe_core for references
        vibe_core = self.root / "vibe_core"
        if vibe_core.exists():
            for py_file in vibe_core.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    if db_name in content:
                        references.append(str(py_file.relative_to(self.root)))
                except Exception as e:
                    # SECURITY FIX B-P0-2: Log instead of silent failure
                    logger.debug(f"Failed to read {py_file} for reference search: {e}")

        return references[:10]  # Limit to 10

    def _categorize_db(self, path: Path, tables: List[str]) -> str:
        """Categorize database by path and content."""
        path_str = str(path)

        if "MagicMock" in path_str or "mock" in path_str.lower():
            return "mock"
        if "test" in path_str.lower():
            return "test"
        if "archive" in path_str:
            return "archive"
        if "phase" in path_str.lower():
            return "experiment"
        if ".vibe" in path_str:
            return "state"
        if "data/" in path_str:
            if "ledger" in path_str:
                return "production"
            if "economy" in path_str:
                return "production"

        return "unknown"


# =============================================================================
# LEDGER AUDIT (Tool Usage)
# =============================================================================


class LedgerAuditor:
    """Analyzes tool usage from the production ledger."""

    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.tool_usage: Dict[str, ToolUsage] = {}

    def analyze(self) -> List[ToolUsage]:
        """Analyze tool usage from ledger events."""
        if not self.ledger_path.exists():
            logger.warning(f"Ledger not found: {self.ledger_path}")
            return []

        try:
            conn = sqlite3.connect(str(self.ledger_path))
            cursor = conn.cursor()

            # Get tool call events
            cursor.execute("""
                SELECT payload, timestamp
                FROM ledger_events
                WHERE event_type IN ('TOOL_CALL_INITIATED', 'TOOL_CALL_COMPLETED')
                ORDER BY timestamp
            """)

            tool_calls = defaultdict(lambda: {"count": 0, "successes": 0, "last": None})

            for row in cursor.fetchall():
                try:
                    payload = json.loads(row[0])
                    tool_name = payload.get("tool_name", "unknown")
                    timestamp = row[1]
                    success = payload.get("success", True)

                    tool_calls[tool_name]["count"] += 1
                    if success:
                        tool_calls[tool_name]["successes"] += 1
                    tool_calls[tool_name]["last"] = timestamp
                except Exception as e:
                    # SECURITY FIX B-P0-2: Log instead of silent failure
                    logger.debug(f"Failed to parse tool call event: {e}")

            conn.close()

            # Convert to ToolUsage objects
            results = []
            for tool_name, stats in tool_calls.items():
                count = stats["count"]
                successes = stats["successes"]

                results.append(
                    ToolUsage(
                        tool_name=tool_name,
                        call_count=count,
                        last_called=datetime.fromisoformat(stats["last"]) if stats["last"] else None,
                        success_rate=successes / count if count > 0 else 0.0,
                    )
                )

            return sorted(results, key=lambda x: x.call_count, reverse=True)

        except Exception as e:
            logger.error(f"Failed to analyze ledger: {e}")
            return []


# =============================================================================
# IMPORT AUDIT
# =============================================================================


class ImportAuditor:
    """Analyzes Python imports to find orphaned code."""

    def __init__(self, root: Path):
        self.root = root
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.imported_by: Dict[str, Set[str]] = defaultdict(set)

    def scan_imports(self) -> Dict[str, ImportInfo]:
        """Scan all Python files for imports."""
        vibe_core = self.root / "vibe_core"
        if not vibe_core.exists():
            return {}

        for py_file in vibe_core.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            self._analyze_file(py_file)

        # Build ImportInfo objects
        results = {}
        for module_path, imports in self.imports.items():
            is_orphan = len(self.imported_by.get(module_path, set())) == 0

            # Skip __init__.py and main entry points
            if module_path.endswith("__init__.py"):
                is_orphan = False
            if "cli" in module_path or "main" in module_path:
                is_orphan = False

            results[module_path] = ImportInfo(
                module_path=Path(module_path),
                imports=imports,
                imported_by=self.imported_by.get(module_path, set()),
                is_orphan=is_orphan,
            )

        return results

    def _analyze_file(self, py_file: Path) -> None:
        """Analyze imports in a single Python file."""
        try:
            content = py_file.read_text()
            tree = ast.parse(content)

            rel_path = str(py_file.relative_to(self.root))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[rel_path].add(alias.name)
                        if alias.name.startswith("vibe_core"):
                            # Track internal imports
                            imported = alias.name.replace(".", "/") + ".py"
                            self.imported_by[imported].add(rel_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[rel_path].add(node.module)
                        if node.module.startswith("vibe_core"):
                            imported = node.module.replace(".", "/") + ".py"
                            self.imported_by[imported].add(rel_path)
        except SyntaxError:
            pass
        except Exception as e:
            logger.debug(f"Could not parse {py_file}: {e}")


# =============================================================================
# MAIN AUDIT TOOL
# =============================================================================


class SystemAudit:
    """
    Complete system audit tool.

    Usage:
        audit = SystemAudit(Path("."))
        report = audit.run_full_audit()
        print(audit.format_report(report))
    """

    def __init__(self, root: Path = None):
        self.root = (root or Path.cwd()).resolve()

    def run_database_audit(self) -> List[DatabaseInfo]:
        """Audit all databases."""
        auditor = DatabaseAuditor(self.root)
        return auditor.scan_all()

    def run_usage_audit(self) -> List[ToolUsage]:
        """Audit tool usage from ledger."""
        ledger_path = self.root / "data" / "vibe_ledger.db"
        auditor = LedgerAuditor(ledger_path)
        return auditor.analyze()

    def run_import_audit(self) -> Dict[str, ImportInfo]:
        """Audit Python imports."""
        auditor = ImportAuditor(self.root)
        return auditor.scan_imports()

    def run_full_audit(self) -> AuditReport:
        """Run complete system audit."""
        databases = self.run_database_audit()
        tool_usage = self.run_usage_audit()
        imports = self.run_import_audit()

        # Find orphans
        orphans = [path for path, info in imports.items() if info.is_orphan]

        # Generate recommendations
        recommendations = self._generate_recommendations(databases, tool_usage, orphans)

        # Generate kill list
        kill_list = self._generate_kill_list(databases)

        return AuditReport(
            timestamp=datetime.now(),
            databases=databases,
            tool_usage=tool_usage,
            import_orphans=orphans,
            recommendations=recommendations,
            kill_list=kill_list,
        )

    def _generate_recommendations(
        self, databases: List[DatabaseInfo], tool_usage: List[ToolUsage], orphans: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        # Database recommendations
        empty_dbs = [db for db in databases if db.is_empty and db.category != "mock"]
        if empty_dbs:
            recs.append(f"CONSOLIDATE: {len(empty_dbs)} empty databases found")

        prod_dbs = [db for db in databases if db.category == "production"]
        if len(prod_dbs) > 1:
            recs.append(f"WARNING: Multiple production databases ({len(prod_dbs)})")

        # Check for the specific .vibe vs data split
        vibe_dbs = [db for db in databases if ".vibe" in str(db.path)]
        data_dbs = [db for db in databases if "data/" in str(db.path) and db.category == "production"]

        if vibe_dbs and data_dbs:
            vibe_empty = all(db.is_empty for db in vibe_dbs)
            data_has_content = any(not db.is_empty for db in data_dbs)

            if vibe_empty and data_has_content:
                recs.append(
                    "CRITICAL: .vibe/ databases are empty but data/ has content. "
                    "System has split brain. Consolidate to single source of truth."
                )

        # Tool usage recommendations
        used_tools = {t.tool_name for t in tool_usage}
        if len(used_tools) < 5:
            recs.append(f"LOW USAGE: Only {len(used_tools)} tools have been called via ledger")

        return recs

    def _generate_kill_list(self, databases: List[DatabaseInfo]) -> List[str]:
        """Generate list of files safe to delete."""
        kill_list = []

        for db in databases:
            if db.category == "mock":
                kill_list.append(f"MOCK: {db.path}")
            elif db.category == "test" and db.is_empty:
                kill_list.append(f"EMPTY TEST: {db.path}")
            elif db.category == "experiment":
                kill_list.append(f"EXPERIMENT: {db.path}")

        return kill_list

    def format_report(self, report: AuditReport) -> str:
        """Format audit report for human reading."""
        lines = []

        lines.append("=" * 70)
        lines.append("SYSTEM AUDIT REPORT")
        lines.append(f"Generated: {report.timestamp}")
        lines.append("=" * 70)

        # Databases
        lines.append("\n## DATABASES\n")

        by_category = defaultdict(list)
        for db in report.databases:
            by_category[db.category].append(db)

        for category, dbs in sorted(by_category.items()):
            lines.append(f"### {category.upper()} ({len(dbs)})")
            for db in dbs:
                size_kb = db.size_bytes / 1024
                status = "EMPTY" if db.is_empty else f"{sum(db.row_counts.values())} rows"
                lines.append(f"  {db.path.name:<30} {size_kb:>8.1f}KB  {status}")
            lines.append("")

        # Tool Usage
        lines.append("\n## TOOL USAGE (from ledger)\n")
        if report.tool_usage:
            for tool in report.tool_usage[:20]:
                lines.append(f"  {tool.tool_name:<40} {tool.call_count:>5} calls")
        else:
            lines.append("  No tool calls recorded in ledger")

        # Recommendations
        lines.append("\n## RECOMMENDATIONS\n")
        for rec in report.recommendations:
            lines.append(f"  - {rec}")

        # Kill List
        if report.kill_list:
            lines.append("\n## SAFE TO DELETE\n")
            for item in report.kill_list:
                lines.append(f"  - {item}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def format_json(self, report: AuditReport) -> str:
        """Format audit report as JSON."""
        return json.dumps(
            {
                "timestamp": report.timestamp.isoformat(),
                "databases": [
                    {
                        "path": str(db.path),
                        "size_bytes": db.size_bytes,
                        "tables": db.tables,
                        "row_counts": db.row_counts,
                        "category": db.category,
                        "is_empty": db.is_empty,
                        "created_by": db.created_by,
                    }
                    for db in report.databases
                ],
                "tool_usage": [
                    {
                        "tool_name": t.tool_name,
                        "call_count": t.call_count,
                        "success_rate": t.success_rate,
                    }
                    for t in report.tool_usage
                ],
                "recommendations": report.recommendations,
                "kill_list": report.kill_list,
            },
            indent=2,
        )


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """CLI entry point."""
    import sys

    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h", "help"):
        print(__doc__)
        return 0

    audit = SystemAudit()
    cmd = args[0]
    as_json = "--json" in args

    if cmd == "databases":
        dbs = audit.run_database_audit()
        if as_json:
            print(
                json.dumps(
                    [
                        {
                            "path": str(db.path),
                            "size_kb": db.size_bytes / 1024,
                            "category": db.category,
                            "is_empty": db.is_empty,
                            "tables": db.tables,
                        }
                        for db in dbs
                    ],
                    indent=2,
                )
            )
        else:
            print(f"\nFound {len(dbs)} databases:\n")
            for db in sorted(dbs, key=lambda x: x.category):
                size_kb = db.size_bytes / 1024
                status = "EMPTY" if db.is_empty else f"{sum(db.row_counts.values())} rows"
                print(f"  [{db.category:<10}] {db.path.name:<35} {size_kb:>8.1f}KB  {status}")
        return 0

    elif cmd == "usage":
        usage = audit.run_usage_audit()
        if as_json:
            print(
                json.dumps(
                    [
                        {
                            "tool": t.tool_name,
                            "calls": t.call_count,
                        }
                        for t in usage
                    ],
                    indent=2,
                )
            )
        else:
            print("\nTool usage from ledger:\n")
            if usage:
                for t in usage:
                    print(f"  {t.tool_name:<40} {t.call_count:>5} calls")
            else:
                print("  No tool calls recorded")
        return 0

    elif cmd == "full":
        report = audit.run_full_audit()
        if as_json:
            print(audit.format_json(report))
        else:
            print(audit.format_report(report))
        return 0

    else:
        print(f"Unknown command: {cmd}")
        print("Use: databases, usage, full")
        return 1


if __name__ == "__main__":
    sys.exit(main())
