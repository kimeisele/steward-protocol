"""
NAGA CLI - The Invisible Guardian's Command Interface.

"Niemand darf es merken" - but YOU can command them.

FRACTAL NAGA CLI:
    steward naga status      - Federation health
    steward naga scan        - Scan codebase for issues (REPORT.md style)
    steward naga detect      - Detect drifts and violations
    steward naga flood       - FloodManager status
    steward naga bite        - Record a violation
    steward naga remediate   - Actually FIX issues (not just detect!)
    steward naga audit       - Query ledger audit trail

THIS IS NOT DOCUMENTATION. THIS IS ACTION.
NAGAs flood the system with what is LACKING.
"""

import ast
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("NAGA_CLI")


@register_cli
class NagaCLI:
    """
    NAGA Command Line Interface.

    THE EXECUTIVE LAYER IN YOUR TERMINAL.
    NAGAs don't just observe - they ACT.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="naga",
            description="NAGA Federation CLI - The Invisible Guardians",
            domain="security",
            subcommands=["status", "scan", "detect", "flood", "bite", "remediate", "audit"],
            tags=["naga", "security", "guardian", "fractal", "executive"],
        )

    def __init__(self):
        self._federation = None
        self._repo_root = Path.cwd()

    def _get_federation(self):
        """Lazy-load NagaOrchestrator."""
        if self._federation is None:
            try:
                from vibe_core.naga import NagaOrchestrator

                try:
                    self._federation = ServiceRegistry.get("NagaOrchestrator")
                except Exception:
                    self._federation = ServiceRegistry.get(NagaOrchestrator)
            except Exception:
                pass
        return self._federation

    def run(self, args: List[str]) -> int:
        """
        Main entry point.

        Routes to subcommands.
        """
        if not args:
            self._print_usage()
            return 0

        cmd = args[0]

        if cmd == "status":
            return self.cmd_status(args[1:])
        elif cmd == "scan":
            return self.cmd_scan(args[1:])
        elif cmd == "detect":
            return self.cmd_detect(args[1:])
        elif cmd == "flood":
            return self.cmd_flood(args[1:])
        elif cmd == "bite":
            return self.cmd_bite(args[1:])
        elif cmd == "remediate":
            return self.cmd_remediate(args[1:])
        elif cmd == "audit":
            return self.cmd_audit(args[1:])
        elif cmd == "help" or cmd == "--help":
            self._print_usage()
            return 0
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        """Print NAGA CLI usage."""
        print("""
    NAGA FEDERATION CLI
    ===================
    "Wir sind selbst NAGAs - Hüter des Schatzes dieses AOS."

    COMMANDS:
        steward naga status     Federation health status
        steward naga scan       Scan codebase for issues (REAL scanning!)
        steward naga detect     Detect drifts from CommitWatcher
        steward naga flood      FloodManager observation status
        steward naga bite       Record a violation to Ledger
        steward naga remediate  Actually FIX detected issues
        steward naga audit      Query Ledger audit trail

    OPTIONS:
        --path <path>    Target path for scanning
        --type <type>    Issue type to scan for
        --fix            Auto-fix issues (remediate)
        --verbose        Show detailed output

    NAGAs don't just observe. NAGAs ACT.
        """)

    # =========================================================================
    # STATUS - Federation Health
    # =========================================================================

    def cmd_status(self, args: List[str]) -> int:
        """Show federation status."""
        print("\n    NAGA FEDERATION STATUS")
        print("=" * 60)

        federation = self._get_federation()

        if not federation:
            print("\n    Federation not initialized.")
            print("    Boot the kernel first: steward boot")
            print("\n    Standalone scan available: steward naga scan")
            print("=" * 60)
            return 0

        try:
            status = federation.get_status()
            ready = federation.is_ready()

            print(f"\n    Overall: {'HEALTHY' if ready else 'DEGRADED'}")

            # Components
            print("\n    Components:")
            if federation.sesha:
                s = federation.sesha.get_status()
                print(f"      SESHA (Foundation):  {'OK' if s.healthy else 'DEGRADED'}")

            if federation.vasuki:
                v = federation.vasuki.get_status()
                print(f"      VASUKI (Bridge):     {'OK' if v.healthy else 'DEGRADED'}")

            if federation.takshaka:
                t = federation.takshaka.get_status()
                print(f"      TAKSHAKA (Guardian): {'OK' if t.healthy else 'DEGRADED'} [trust={t.trust_mode}]")

            if federation.flood_manager:
                f = federation.flood_manager.get_status()
                print(
                    f"      FLOOD MANAGER:       {'ACTIVE' if f.get('active') else 'INACTIVE'} [{f.get('total_observations', 0)} obs]"
                )

            if federation.commit_watcher:
                c = federation.commit_watcher.get_stats()
                print(
                    f"      COMMIT WATCHER:      {c.get('total_observed', 0)} observed, {c.get('alerts_generated', 0)} alerts"
                )

        except Exception as e:
            print(f"\n    Error getting status: {e}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # SCAN - Actually scan the codebase for issues
    # =========================================================================

    def cmd_scan(self, args: List[str]) -> int:
        """
        Scan codebase for issues.

        THIS IS REAL SCANNING - not just status.
        NAGAs flood with what is LACKING.
        """
        print("\n    NAGA CODEBASE SCAN")
        print("=" * 60)

        # Parse args
        target_path = self._repo_root / "vibe_core"
        scan_type = "all"
        verbose = "--verbose" in args or "-v" in args

        for i, arg in enumerate(args):
            if arg == "--path" and i + 1 < len(args):
                target_path = Path(args[i + 1])
            elif arg == "--type" and i + 1 < len(args):
                scan_type = args[i + 1]

        if not target_path.exists():
            print(f"    Path not found: {target_path}")
            return 1

        print(f"\n    Target: {target_path}")
        print(f"    Type: {scan_type}")
        print()

        results = {
            "silent_failures": [],
            "vfs_bypasses": [],
            "any_types": [],
            "global_singletons": [],
            "security_issues": [],
        }

        # Count files
        py_files = list(target_path.rglob("*.py"))
        print(f"    Scanning {len(py_files)} Python files...")
        print()

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")

                # Silent Failures (except: pass)
                if scan_type in ["all", "silent"]:
                    silent = self._find_silent_failures(content, py_file)
                    results["silent_failures"].extend(silent)

                # VFS Bypasses (direct open())
                if scan_type in ["all", "vfs"]:
                    vfs = self._find_vfs_bypasses(content, py_file)
                    results["vfs_bypasses"].extend(vfs)

                # Any Types
                if scan_type in ["all", "types"]:
                    anys = self._find_any_types(content, py_file)
                    results["any_types"].extend(anys)

                # Security Issues
                if scan_type in ["all", "security"]:
                    sec = self._find_security_issues(content, py_file)
                    results["security_issues"].extend(sec)

            except Exception as e:
                if verbose:
                    print(f"    Error scanning {py_file}: {e}")

        # Report
        print("    SCAN RESULTS")
        print("-" * 60)

        total_issues = 0

        if results["silent_failures"]:
            count = len(results["silent_failures"])
            total_issues += count
            print(f"\n    SILENT FAILURES (except: pass): {count}")
            if verbose:
                for issue in results["silent_failures"][:10]:
                    print(f"      {issue['file']}:{issue['line']}")

        if results["vfs_bypasses"]:
            count = len(results["vfs_bypasses"])
            total_issues += count
            print(f"\n    VFS BYPASSES (direct open): {count}")
            if verbose:
                for issue in results["vfs_bypasses"][:10]:
                    print(f"      {issue['file']}:{issue['line']}")

        if results["any_types"]:
            count = len(results["any_types"])
            total_issues += count
            print(f"\n    ANY-TYPE VIOLATIONS: {count}")
            if verbose:
                for issue in results["any_types"][:10]:
                    print(f"      {issue['file']}:{issue['line']}")

        if results["security_issues"]:
            count = len(results["security_issues"])
            total_issues += count
            print(f"\n    SECURITY ISSUES: {count}")
            if verbose:
                for issue in results["security_issues"][:10]:
                    print(f"      [{issue['type']}] {issue['file']}:{issue['line']}")

        print()
        print("-" * 60)
        print(f"    TOTAL ISSUES: {total_issues}")

        # Record to Ledger if federation available
        federation = self._get_federation()
        if federation and federation.sesha and hasattr(federation.sesha, "_ledger"):
            try:
                federation.sesha._ledger.record_event(
                    event_type="NAGA_SCAN_COMPLETE",
                    agent_id="naga_cli",
                    details={
                        "path": str(target_path),
                        "files_scanned": len(py_files),
                        "total_issues": total_issues,
                        "breakdown": {k: len(v) for k, v in results.items()},
                    },
                )
                print("    (Recorded to Ledger)")
            except Exception:
                pass

        print("=" * 60)
        return 0 if total_issues == 0 else 1

    def _find_silent_failures(self, content: str, filepath: Path) -> List[Dict]:
        """Find except: pass patterns."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Match various silent failure patterns
            if re.search(r"except.*:\s*pass\s*$", line):
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})
            elif re.search(r"except.*:\s*\.\.\.\s*$", line):
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})

        return issues

    def _find_vfs_bypasses(self, content: str, filepath: Path) -> List[Dict]:
        """Find direct open() calls that bypass VFS."""
        issues = []
        lines = content.split("\n")

        # Skip test files and known exceptions
        if "test" in str(filepath).lower():
            return []

        for i, line in enumerate(lines, 1):
            # Look for open() not in VFS context
            if re.search(r"(?<!vfs\.)open\s*\(", line):
                # Skip if it's in a comment
                if line.strip().startswith("#"):
                    continue
                # Skip if it's importing open
                if "from" in line and "import" in line:
                    continue
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})

        return issues

    def _find_any_types(self, content: str, filepath: Path) -> List[Dict]:
        """Find Dict[str, Any] and similar."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Match Any type hints
            if re.search(r":\s*Any\b", line) or re.search(r"\[\s*Any\s*\]", line):
                # Skip if it's a comment
                if line.strip().startswith("#"):
                    continue
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})

        return issues

    def _find_security_issues(self, content: str, filepath: Path) -> List[Dict]:
        """Find potential security issues."""
        issues = []
        lines = content.split("\n")

        patterns = [
            (r"eval\s*\(", "EVAL"),
            (r"exec\s*\(", "EXEC"),
            (r"subprocess\.call\s*\(.*shell\s*=\s*True", "SHELL_INJECTION"),
            (r"yaml\.load\s*\((?!.*Loader)", "UNSAFE_YAML"),
            (r"pickle\.load", "PICKLE"),
            (r"__import__\s*\(", "DYNAMIC_IMPORT"),
        ]

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue

            for pattern, issue_type in patterns:
                if re.search(pattern, line):
                    issues.append(
                        {
                            "file": str(filepath),
                            "line": i,
                            "type": issue_type,
                            "code": line.strip(),
                        }
                    )

        return issues

    # =========================================================================
    # DETECT - Drift Detection
    # =========================================================================

    def cmd_detect(self, args: List[str]) -> int:
        """Detect drifts from CommitWatcher."""
        print("\n    NAGA DRIFT DETECTION")
        print("=" * 60)

        federation = self._get_federation()

        if not federation:
            print("\n    Federation not initialized.")
            print("    Using standalone detection...")
            # Fallback to file-based detection
            return self._detect_file_drift()

        if not federation.commit_watcher:
            print("\n    CommitWatcher not available.")
            return 1

        stats = federation.commit_watcher.get_stats()

        print(f"\n    Total Observed:    {stats.get('total_observed', 0)}")
        print(f"    Success Count:     {stats.get('success_count', 0)}")
        print(f"    Panic Count:       {stats.get('panic_count', 0)}")
        print(f"    Deferred Count:    {stats.get('deferred_count', 0)}")
        print(f"    Healed Count:      {stats.get('healed_count', 0)}")
        print(f"    Alerts Generated:  {stats.get('alerts_generated', 0)}")

        # Detect patterns
        print("\n    Pattern Analysis:")

        if stats.get("panic_count", 0) >= 3:
            print("      PANIC PATTERN DETECTED - Data loss risk!")

        if stats.get("consecutive_deferrals", 0) >= 5:
            print("      DEFERRAL LOOP DETECTED - Decision paralysis!")

        total = stats.get("total_observed", 0)
        healed = stats.get("healed_count", 0)
        if total > 10 and healed / total > 0.5:
            print(f"      CONFLICT DRIFT DETECTED - {healed / total:.1%} require healing!")

        if not any(
            [
                stats.get("panic_count", 0) >= 3,
                stats.get("consecutive_deferrals", 0) >= 5,
                total > 10 and healed / total > 0.5,
            ]
        ):
            print("      No concerning patterns detected.")

        print("\n" + "=" * 60)
        return 0

    def _detect_file_drift(self) -> int:
        """Standalone file-based drift detection."""
        # Check for uncommitted changes
        import subprocess

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self._repo_root,
            )

            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                print(f"\n    Uncommitted Changes: {len(lines)}")
                for line in lines[:10]:
                    print(f"      {line}")
                if len(lines) > 10:
                    print(f"      ... and {len(lines) - 10} more")
            else:
                print("\n    No uncommitted changes.")

        except Exception as e:
            print(f"\n    Git check failed: {e}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # FLOOD - FloodManager Status
    # =========================================================================

    def cmd_flood(self, args: List[str]) -> int:
        """Show FloodManager status."""
        print("\n    NAGA FLOOD MANAGER STATUS")
        print("=" * 60)

        federation = self._get_federation()

        if not federation or not federation.flood_manager:
            print("\n    FloodManager not available.")
            print("    Boot the kernel first: steward boot")
            return 1

        status = federation.flood_manager.get_status()

        print(f"\n    Active:           {status.get('active', False)}")
        print(f"    Observations:     {status.get('total_observations', 0)}")
        print(f"    Subscribers:      {status.get('subscriber_count', 0)}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # BITE - Record Violation
    # =========================================================================

    def cmd_bite(self, args: List[str]) -> int:
        """Record a violation to Ledger."""
        if not args:
            print("Usage: steward naga bite <violation_type> [--details <json>]")
            return 1

        violation_type = args[0]
        details = {}

        for i, arg in enumerate(args):
            if arg == "--details" and i + 1 < len(args):
                import json

                details = json.loads(args[i + 1])

        print(f"\n    TAKSHAKA BITE: {violation_type}")
        print("=" * 60)

        federation = self._get_federation()

        if federation and federation.takshaka:
            try:
                from vibe_core.protocols.naga import VajraViolation

                violation = VajraViolation(
                    violation_type=violation_type,
                    source="naga_cli",
                    details=details,
                )
                event_id = federation.takshaka.bite(violation)
                print(f"\n    Recorded: {event_id}")
            except Exception as e:
                print(f"\n    Bite failed: {e}")
                return 1
        else:
            print("\n    Takshaka not available. Recording locally...")
            print(f"    Type: {violation_type}")
            print(f"    Details: {details}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # REMEDIATE - Actually FIX issues
    # =========================================================================

    def cmd_remediate(self, args: List[str]) -> int:
        """
        Actually FIX detected issues.

        THIS IS WHERE NAGAs ACT, NOT JUST OBSERVE.
        """
        print("\n    NAGA REMEDIATION")
        print("=" * 60)

        dry_run = "--dry-run" in args
        auto_fix = "--fix" in args

        if not auto_fix and not dry_run:
            print("\n    Available remediations:")
            print("      --fix            Actually apply fixes")
            print("      --dry-run        Show what would be fixed")
            print()
            print("    Remediation types:")
            print("      steward naga remediate silent --fix    Fix silent failures")
            print("      steward naga remediate imports --fix   Remove unused imports")
            print()
            return 0

        remedy_type = None
        for arg in args:
            if arg not in ["--fix", "--dry-run", "-v", "--verbose"]:
                remedy_type = arg
                break

        if remedy_type == "silent":
            return self._remediate_silent_failures(dry_run)
        elif remedy_type == "imports":
            print("    Import remediation not yet implemented.")
            print("    Use: ruff check --fix")
            return 0
        else:
            print(f"    Unknown remediation type: {remedy_type}")
            return 1

    def _remediate_silent_failures(self, dry_run: bool) -> int:
        """Replace except: pass with proper logging."""
        target_path = self._repo_root / "vibe_core"
        fixed_count = 0

        print(f"\n    Scanning for silent failures in {target_path}...")

        for py_file in target_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                original = content

                # Replace except: pass with logging
                # Pattern: except SomeError: pass
                new_content = re.sub(
                    r"(except\s+\w+.*?):\s*pass(\s*$)",
                    r'\1:\n                logger.debug("Suppressed exception")',
                    content,
                    flags=re.MULTILINE,
                )

                # Pattern: except: pass
                new_content = re.sub(
                    r"(except):\s*pass(\s*$)",
                    r'\1:\n                logger.debug("Suppressed exception")',
                    new_content,
                    flags=re.MULTILINE,
                )

                if new_content != original:
                    if dry_run:
                        print(f"    Would fix: {py_file}")
                    else:
                        py_file.write_text(new_content, encoding="utf-8")
                        print(f"    Fixed: {py_file}")
                    fixed_count += 1

            except Exception as e:
                print(f"    Error processing {py_file}: {e}")

        print(f"\n    {'Would fix' if dry_run else 'Fixed'}: {fixed_count} files")
        print("=" * 60)
        return 0

    # =========================================================================
    # AUDIT - Query Ledger
    # =========================================================================

    def cmd_audit(self, args: List[str]) -> int:
        """Query Ledger audit trail."""
        print("\n    NAGA AUDIT TRAIL")
        print("=" * 60)

        federation = self._get_federation()

        if not federation or not federation.sesha:
            print("\n    Sesha not available.")
            print("    Boot the kernel first: steward boot")
            return 1

        limit = 10
        event_type = None

        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
            elif arg == "--type" and i + 1 < len(args):
                event_type = args[i + 1]

        try:
            if hasattr(federation.sesha, "_ledger"):
                ledger = federation.sesha._ledger

                if event_type:
                    events = ledger.get_events_by_type(event_type, limit=limit)
                else:
                    events = ledger.get_recent_events(limit=limit)

                print(f"\n    Recent Events (limit={limit}):")
                for event in events:
                    e = event.to_dict() if hasattr(event, "to_dict") else event
                    print(f"      [{e.get('event_type', 'UNKNOWN')}] {e.get('timestamp', '')}")
                    print(f"        Agent: {e.get('agent_id', 'unknown')}")

        except Exception as e:
            print(f"\n    Audit query failed: {e}")

        print("\n" + "=" * 60)
        return 0
