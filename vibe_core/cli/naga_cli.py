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
            subcommands=[
                "status",
                "scan",
                "detect",
                "flood",
                "bite",
                "remediate",
                "audit",
                "prahlad",
                "chaos",
                "chat",
                "intel",
            ],
            tags=["naga", "security", "guardian", "fractal", "executive", "intelligence"],
        )

    def __init__(self):
        self._federation = None
        self._repo_root = Path.cwd()

    def _get_federation(self):
        """Lazy-load NagaFederation from ServiceRegistry."""
        if self._federation is None:
            try:
                from vibe_core.protocols.naga import NagaFederationProtocol

                self._federation = ServiceRegistry.get(NagaFederationProtocol)
            except Exception:
                pass
        return self._federation

    def run(self, args: List[str]) -> int:
        """
        Main entry point.

        PROTOCOL-FIRST ROUTING:
        1. First try NagaCommandRegistry (protocol-based commands)
        2. Fall back to legacy cmd_* methods for unimplemented commands

        This enables gradual migration from legacy to protocol-based commands.
        """
        if not args:
            self._print_usage()
            return 0

        cmd = args[0]

        if cmd == "help" or cmd == "--help":
            self._print_usage()
            return 0

        # =================================================================
        # PROTOCOL-FIRST: Try NagaCommandRegistry
        # =================================================================
        result = self._try_protocol_command(cmd, args[1:])
        if result is not None:
            return result

        # =================================================================
        # LEGACY FALLBACK: Route to cmd_* methods
        # =================================================================
        legacy_handlers = {
            "status": self.cmd_status,
            "scan": self.cmd_scan,
            "detect": self.cmd_detect,
            "flood": self.cmd_flood,
            "bite": self.cmd_bite,
            "remediate": self.cmd_remediate,
            "audit": self.cmd_audit,
            "prahlad": self.cmd_prahlad,
            "chaos": self.cmd_chaos,
            "chat": self.cmd_chat,
            "intel": self.cmd_intel,
        }

        handler = legacy_handlers.get(cmd)
        if handler:
            return handler(args[1:])

        print(f"Unknown command: {cmd}")
        self._print_usage()
        return 1

    def _try_protocol_command(self, cmd: str, args: List[str]) -> Optional[int]:
        """
        Try to execute a command via NagaCommandRegistry.

        Returns:
            Exit code if protocol command exists and executed, None otherwise.

        PROTOCOL ROUTING:
        Uses the fractal CLI architecture from protocols/naga/cli_command.py.
        Commands route through MahajanaRouter to their owning Mahajana.
        """
        try:
            # Import protocol infrastructure
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            # Ensure commands are discovered (Balarama pattern)
            discover_commands()

            # Try to get protocol command
            protocol_cmd = NAGA_COMMAND_REGISTRY.get(cmd)
            if protocol_cmd is None:
                return None  # No protocol command, fall back to legacy

            # Execute protocol command
            result = protocol_cmd.execute(args)

            # Print output
            if result.output:
                print(result.output)
            if result.error:
                print(f"Error: {result.error}")

            return result.exit_code

        except ImportError as e:
            # Protocol infrastructure not available, fall back to legacy
            logger.debug(f"Protocol infrastructure unavailable: {e}")
            return None
        except Exception as e:
            # Log error but fall back to legacy
            logger.warning(f"Protocol command failed, falling back to legacy: {e}")
            return None

    def _print_usage(self):
        """Print NAGA CLI usage."""
        print("""
    NAGA FEDERATION CLI
    ===================

    COMMANDS:
        steward naga status     Federation health status
        steward naga scan       Scan codebase for issues
        steward naga detect     Detect drifts from CommitWatcher
        steward naga flood      FloodManager observation status
        steward naga bite       Record a violation to Ledger
        steward naga remediate  Actually FIX detected issues
        steward naga audit      Query Ledger audit trail
        steward naga prahlad    Prahlad resilience agent
        steward naga chaos      Run Hiranyakashipu chaos attacks
        steward naga chat       Chat with NAGA intelligence
        steward naga intel      Query intelligence bridge

    OPTIONS:
        --path <path>    Target path for scanning
        --type <type>    Issue type to scan for
        --fix            Auto-fix issues (remediate)
        --verbose        Show detailed output

    PRAHLAD COMMANDS:
        steward naga prahlad dharma     Run Dharma audit
        steward naga prahlad coverage   Get coverage intelligence
        steward naga prahlad verify     Run NAGA self-verification

    CHAOS COMMANDS:
        steward naga chaos list         List available attack seeds
        steward naga chaos run <type>   Run attack seeds by type
        steward naga chaos probe <mod>  Chaos probe a module

    CHAT COMMANDS:
        steward naga chat <message>     Send message with Naga intel
        steward naga chat --threats     Show active threats
        steward naga chat --critical    Show critical alerts

    INTEL COMMANDS:
        steward naga intel recent       Recent intelligence items
        steward naga intel threats      Active threat intelligence
        steward naga intel nagas        List active NAGAs
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

        # Record to Ledger if federation available (via PUBLIC API)
        federation = self._get_federation()
        if federation and federation.sesha:
            try:
                from vibe_core.protocols.naga import EventRecord

                event: EventRecord = {
                    "event_type": "NAGA_SCAN_COMPLETE",
                    "agent_id": "naga_cli",
                    "details": {
                        "path": str(target_path),
                        "files_scanned": len(py_files),
                        "total_issues": total_issues,
                        "breakdown": {k: len(v) for k, v in results.items()},
                    },
                }
                federation.sesha.record_event(event)
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
            # YAMARAJA: Use PUBLIC Sesha API, not _ledger directly
            sesha = federation.sesha
            if event_type:
                events = sesha.get_events_by_type(event_type, limit=limit)
            else:
                events = sesha.get_recent_events(limit=limit)

            print(f"\n    Recent Events (limit={limit}):")
            for event in events:
                e = event.to_dict() if hasattr(event, "to_dict") else event
                print(f"      [{e.get('event_type', 'UNKNOWN')}] {e.get('timestamp', '')}")
                print(f"        Agent: {e.get('agent_id', 'unknown')}")

        except Exception as e:
            print(f"\n    Audit query failed: {e}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # PRAHLAD - Resilience Agent
    # =========================================================================

    def cmd_prahlad(self, args: List[str]) -> int:
        """
        Access Prahlad Resilience Agent.

        Subcommands:
            dharma   - Run Dharma audit (integrity check)
            coverage - Get coverage intelligence
            verify   - Run NAGA self-verification (Ouroboros)
        """
        if not args:
            print("\n    PRAHLAD - The Resilience Agent")
            print("=" * 60)
            print("\n    Subcommands:")
            print("        dharma   - Run Dharma audit (integrity check)")
            print("        coverage - Get coverage intelligence")
            print("        verify   - Run NAGA self-verification")
            print("\n    Usage: steward naga prahlad <subcommand>")
            print("=" * 60)
            return 0

        subcmd = args[0]

        if subcmd == "dharma":
            return self._prahlad_dharma()
        elif subcmd == "coverage":
            return self._prahlad_coverage()
        elif subcmd == "verify":
            return self._prahlad_verify()
        else:
            print(f"    Unknown prahlad command: {subcmd}")
            return 1

    def _prahlad_dharma(self) -> int:
        """Run Dharma audit."""
        from vibe_core.protocols.naga import PrahladProtocol

        print("\n    PRAHLAD DHARMA AUDIT")
        print("=" * 60)

        prahlad = ServiceRegistry.get(PrahladProtocol)
        score = prahlad.dharma_audit()

        print(f"\n    Total Score:          {score.total_score:.1f}%")
        print(f"    Signature Compliance: {score.signature_compliance:.1f}%")
        print(f"    Identity Coverage:    {score.identity_coverage:.1f}%")
        print(f"    Ledger Intact:        {'YES' if score.ledger_intact else 'NO'}")
        print(f"    Unsigned Decisions:   {score.unsigned_decisions}")

        if score.total_score >= 80:
            status = "DHARMIC"
        elif score.total_score >= 50:
            status = "MONITORING"
        else:
            status = "ADHARMIC"

        print(f"\n    Status: {status}")
        print("=" * 60)
        return 0 if score.total_score >= 50 else 1

    def _prahlad_coverage(self) -> int:
        """Get coverage intelligence."""
        from vibe_core.protocols.naga import PrahladProtocol

        print("\n    PRAHLAD COVERAGE INTELLIGENCE")
        print("=" * 60)

        prahlad = ServiceRegistry.get(PrahladProtocol)
        intel = prahlad.get_coverage_intelligence()

        if "error" in intel:
            print(f"\n    Error: {intel['error']}")
        else:
            print(f"\n    Total Testables:  {intel.get('total_testables', 0)}")
            print(f"    Total Tests:      {intel.get('total_tests', 0)}")

            by_type = intel.get("by_type", {})
            if by_type:
                print("\n    By Type:")
                for t, count in by_type.items():
                    print(f"        {t}: {count}")

            naga = intel.get("naga_coverage", {})
            if naga:
                print("\n    NAGA Coverage:")
                print(f"        Testables: {naga.get('testables_covered', 0)}")
                print(f"        Tests:     {naga.get('tests_available', 0)}")

        stats = intel.get("prahlad_stats", {})
        print("\n    Prahlad Stats:")
        print(f"        Tests Generated:  {stats.get('tests_generated', 0)}")
        print(f"        Chaos Probes:     {stats.get('chaos_probes', 0)}")
        print(f"        Dharma Audits:    {stats.get('dharma_audits', 0)}")

        print("=" * 60)
        return 0

    def _prahlad_verify(self) -> int:
        """Run NAGA self-verification (Ouroboros)."""
        from vibe_core.protocols.naga import PrahladProtocol

        print("\n    PRAHLAD SELF-VERIFICATION (OUROBOROS)")
        print("=" * 60)
        print("\n    Running NAGA test suite...")

        prahlad = ServiceRegistry.get(PrahladProtocol)
        passed = prahlad.verify_self_integrity(quiet=False)

        if passed:
            print("\n    NAGA IS WATERTIGHT")
        else:
            print("\n    NAGA COMPROMISED - Tests failed!")

        print("=" * 60)
        return 0 if passed else 1

    # =========================================================================
    # CHAOS - Hiranyakashipu Attack Framework
    # =========================================================================

    def cmd_chaos(self, args: List[str]) -> int:
        """
        Run Hiranyakashipu chaos attacks.

        Subcommands:
            list        - List available attack seeds
            run <type>  - Run attacks by type (trivial, real, narasimha_paradox)
            probe <mod> - Chaos probe a module with attack seeds
        """
        if not args:
            print("\n    HIRANYAKASHIPU - The Attack Framework")
            print("=" * 60)
            print("\n    Subcommands:")
            print("        list         - List available attack seeds")
            print("        run <type>   - Run attacks by type")
            print("        probe <mod>  - Chaos probe a module")
            print("\n    Usage: steward naga chaos <subcommand>")
            print("=" * 60)
            return 0

        subcmd = args[0]

        if subcmd == "list":
            return self._chaos_list()
        elif subcmd == "run":
            attack_type = args[1] if len(args) > 1 else None
            return self._chaos_run(attack_type)
        elif subcmd == "probe":
            target = args[1] if len(args) > 1 else "vibe_core"
            return self._chaos_probe(target, args[2:])
        else:
            print(f"    Unknown chaos command: {subcmd}")
            return 1

    def _chaos_list(self) -> int:
        """List available attack seeds."""
        from vibe_core.protocols.naga import PrahladProtocol

        print("\n    HIRANYAKASHIPU ATTACK SEEDS")
        print("=" * 60)

        prahlad = ServiceRegistry.get(PrahladProtocol)
        count = prahlad.load_attack_seeds()

        print(f"\n    Loaded: {count} attack seeds")

        # Group by type
        for attack_type in ["trivial", "real", "narasimha_paradox"]:
            seeds = prahlad.get_attack_seeds(attack_type=attack_type)
            if seeds:
                print(f"\n    {attack_type.upper()} ({len(seeds)}):")
                for seed in seeds[:5]:
                    print(f"        - {seed.name} (difficulty: {seed.difficulty})")
                if len(seeds) > 5:
                    print(f"        ... and {len(seeds) - 5} more")

        print("=" * 60)
        return 0

    def _chaos_run(self, attack_type: Optional[str]) -> int:
        """Run attacks by type."""
        import asyncio

        from vibe_core.naga.hiranyakashipu import LivingTestFramework

        print("\n    HIRANYAKASHIPU ATTACK RUN")
        print("=" * 60)

        fw = LivingTestFramework()
        seed_dir = Path(__file__).parent.parent / "naga" / "hiranyakashipu" / "seeds"
        if seed_dir.exists():
            fw.add_seed_dir(seed_dir)
        count = fw.load_seeds()

        print(f"\n    Seeds loaded: {count}")

        if attack_type:
            seeds = fw.get_seeds(attack_type=attack_type)
            print(f"    Running {len(seeds)} {attack_type} attacks...")
        else:
            seeds = fw.get_seeds()
            print(f"    Running all {len(seeds)} attacks...")

        # Run attacks
        bypassed = 0
        held = 0

        for seed in seeds:
            try:
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(fw.run_attack(seed, "test_target"))
                finally:
                    loop.close()

                if result.bypassed:
                    bypassed += 1
                    print(f"      BYPASSED: {seed.name}")
                else:
                    held += 1

            except Exception as e:
                print(f"      ERROR: {seed.name}: {e}")

        print("\n    Results:")
        print(f"        Attacks held:    {held}")
        print(f"        Attacks bypassed: {bypassed}")

        if bypassed > 0:
            print(f"\n    WARNING: {bypassed} attacks bypassed defenses!")

        print("=" * 60)
        return 0 if bypassed == 0 else 1

    def _chaos_probe(self, target: str, extra_args: List[str]) -> int:
        """Chaos probe a module with Hiranyakashipu seeds."""
        from vibe_core.protocols.naga import PrahladProtocol

        print("\n    CHAOS PROBE")
        print("=" * 60)
        print(f"\n    Target: {target}")

        prahlad = ServiceRegistry.get(PrahladProtocol)
        count = prahlad.load_attack_seeds()
        print(f"    Attack seeds loaded: {count}")

        # Get attack type filter
        attack_type = None
        for i, arg in enumerate(extra_args):
            if arg == "--type" and i + 1 < len(extra_args):
                attack_type = extra_args[i + 1]

        seeds = prahlad.get_attack_seeds(attack_type=attack_type)
        if not seeds:
            print("    No attack seeds available.")
            return 1

        print(f"    Running {len(seeds)} attacks...")

        result = prahlad.chaos_probe(target, attack_seeds=seeds)

        print(f"\n    Scenarios tested: {result.scenarios_tested}")
        print(f"    Failures (bypasses): {result.failures}")

        if result.failure_details:
            print("\n    Bypass Details:")
            for failure in result.failure_details[:10]:
                print(f"        - {failure.scenario}: {failure.message[:60]}")

        status = "VULNERABLE" if result.failures > 0 else "RESILIENT"
        print(f"\n    Status: {status}")

        print("=" * 60)
        return 0 if result.failures == 0 else 1

    # =========================================================================
    # CHAT - Intelligence-Enhanced Chat
    # =========================================================================

    def cmd_chat(self, args: List[str]) -> int:
        """
        Chat with NAGA intelligence.

        Uses IntelBridgeProtocol to enhance responses with Naga insights.

        MAHAJANA: SHUKA (The Visionary)
        OPCODE: FETCH_RES
        """
        print("\n    NAGA INTELLIGENCE CHAT")
        print("=" * 60)

        # Check for special flags
        show_threats = "--threats" in args
        show_critical = "--critical" in args

        # Get Intel Bridge
        try:
            from vibe_core.protocols.naga import (
                IntelBridgeProtocol,
                NullIntelBridge,
                IntelCategory,
                IntelPriority,
            )

            intel_bridge = ServiceRegistry.get(IntelBridgeProtocol)
        except Exception:
            intel_bridge = NullIntelBridge()

        if show_threats:
            # Show active threats
            threats = intel_bridge.get_threats()
            if threats:
                print("\n    ACTIVE THREATS:")
                for item in threats:
                    print(f"      {item.to_chat_message()}")
            else:
                print("\n    No active threats detected.")
            print("=" * 60)
            return 0

        if show_critical:
            # Show critical alerts
            critical = intel_bridge.get_critical()
            if critical:
                print("\n    CRITICAL ALERTS:")
                for item in critical:
                    print(f"      {item.to_chat_message()}")
            else:
                print("\n    No critical alerts.")
            print("=" * 60)
            return 0

        # Regular chat with intel context
        message = " ".join(arg for arg in args if not arg.startswith("--"))

        if not message:
            print("\n    Usage: steward naga chat <message>")
            print("           steward naga chat --threats")
            print("           steward naga chat --critical")
            print("=" * 60)
            return 0

        print(f"\n    Message: {message}")

        # Query for relevant intelligence
        response = intel_bridge.query_for_chat(message, "naga_cli", limit=3)

        if response.items:
            print("\n    NAGA INSIGHTS:")
            for item in response.items:
                print(f"      {item.to_chat_message()}")

        if response.has_critical:
            print("\n    ⚠️  CRITICAL INTELLIGENCE AVAILABLE")

        if response.has_threats:
            print("\n    ⚠️  ACTIVE THREATS DETECTED")

        # Show active NAGAs
        active_nagas = intel_bridge.get_active_nagas()
        if active_nagas:
            print(f"\n    Active NAGAs: {', '.join(active_nagas)}")

        print("\n" + "=" * 60)
        return 0

    # =========================================================================
    # INTEL - Intelligence Bridge Query
    # =========================================================================

    def cmd_intel(self, args: List[str]) -> int:
        """
        Query NAGA intelligence bridge directly.

        Subcommands:
            recent    - Recent intelligence items
            threats   - Active threat intelligence
            nagas     - List active NAGAs
            query     - Custom query with context
        """
        if not args:
            print("\n    NAGA INTELLIGENCE BRIDGE")
            print("=" * 60)
            print("\n    Subcommands:")
            print("        recent    - Recent intelligence items")
            print("        threats   - Active threat intelligence")
            print("        critical  - Critical alerts")
            print("        nagas     - List active NAGAs")
            print("\n    Usage: steward naga intel <subcommand>")
            print("=" * 60)
            return 0

        subcmd = args[0]

        # Get Intel Bridge
        try:
            from vibe_core.protocols.naga import (
                IntelBridgeProtocol,
                NullIntelBridge,
            )

            intel_bridge = ServiceRegistry.get(IntelBridgeProtocol)
        except Exception:
            intel_bridge = NullIntelBridge()

        if subcmd == "recent":
            return self._intel_recent(intel_bridge, args[1:])
        elif subcmd == "threats":
            return self._intel_threats(intel_bridge)
        elif subcmd == "critical":
            return self._intel_critical(intel_bridge)
        elif subcmd == "nagas":
            return self._intel_nagas(intel_bridge)
        else:
            print(f"    Unknown intel command: {subcmd}")
            return 1

    def _intel_recent(self, intel_bridge, args: List[str]) -> int:
        """Show recent intelligence items."""
        limit = 10
        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])

        print("\n    RECENT INTELLIGENCE")
        print("=" * 60)

        items = intel_bridge.get_recent(limit=limit)

        if items:
            for item in items:
                print(f"\n    [{item.category.value.upper()}] {item.summary}")
                print(f"      Priority: {item.priority.value}")
                print(f"      Source: {item.source_naga}")
                print(f"      Time: {item.timestamp}")
        else:
            print("\n    No recent intelligence items.")
            print("    (Boot the kernel to enable NAGA federation)")

        print("\n" + "=" * 60)
        return 0

    def _intel_threats(self, intel_bridge) -> int:
        """Show active threat intelligence."""
        print("\n    ACTIVE THREATS")
        print("=" * 60)

        threats = intel_bridge.get_threats()

        if threats:
            for item in threats:
                print(f"\n    ⚠️  {item.summary}")
                print(f"      Details: {item.details}")
                print(f"      Source: {item.source_naga}")
        else:
            print("\n    No active threats detected.")

        print("\n" + "=" * 60)
        return 0

    def _intel_critical(self, intel_bridge) -> int:
        """Show critical alerts."""
        print("\n    CRITICAL ALERTS")
        print("=" * 60)

        critical = intel_bridge.get_critical()

        if critical:
            for item in critical:
                print(f"\n    🚨 {item.summary}")
                print(f"      Details: {item.details}")
                print(f"      Source: {item.source_naga}")
        else:
            print("\n    No critical alerts.")

        print("\n" + "=" * 60)
        return 0

    def _intel_nagas(self, intel_bridge) -> int:
        """List active NAGAs."""
        print("\n    ACTIVE NAGAS")
        print("=" * 60)

        nagas = intel_bridge.get_active_nagas()
        categories = intel_bridge.get_available_categories()

        print("\n    Available Categories:")
        for cat in categories:
            print(f"      - {cat.value}")

        if nagas:
            print("\n    Active NAGA Services:")
            for naga in nagas:
                print(f"      - {naga}")
        else:
            print("\n    No active NAGA services.")
            print("    (Boot the kernel to enable NAGA federation)")

        print("\n" + "=" * 60)
        return 0
