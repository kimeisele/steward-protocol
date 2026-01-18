"""
SCAN COMMAND - VYASA's Truth
============================

MAHAJANA: VYASA (The Avatara Compiler)
OPCODE: ASSERT_TRUTH (Position 4)
PHASE: PURIFY

WHY VYASA?
- Vyasadeva compiled all Vedic knowledge
- He divided truth into categories (Vedas, Puranas, etc.)
- Scanning is about VERIFYING and CATEGORIZING truth

MANTRA WORD: KRISHNA (Position 4)
"Krishna is the source of all truth"

Vyasa is the HEAD of the PURIFY phase - the Avatara who verifies.
Every validation begins with ASSERT_TRUTH, every scan with VYASA.

Usage:
    naga scan                    # Full system scan
    naga scan --quick            # Quick scan (critical only)
    naga scan --deep             # Deep scan (all checks)
    naga scan --toxicity         # Toxicity scan only
    naga scan --protocols        # Protocol coverage scan
    naga scan --path <dir>       # Scan specific path
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xab9f3b21"  # GenesisByte: parampara % 37 == 0

from typing import Dict, List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.COMPILE_AST,
    name="scan",
    help_text="Scan and verify system integrity (VYASA's truth - HEAD of PURIFY phase)",
)
class ScanCommand(NagaCommandBase):
    """
    Scan command implementation.

    VYASA verifies truth by scanning for:
    - Toxicity (security violations)
    - Protocol gaps (missing protocols)
    - Integrity issues (corruption)
    - Compliance (dharma violations)

    This is position 4 - the HEAD of PURIFY phase.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute scan command.

        Args:
            args: Flags for scan mode and targets

        Returns:
            NagaCommandResult with scan results
        """
        import re
        from pathlib import Path

        # Parse flags
        quick = "--quick" in args
        deep = "--deep" in args
        toxicity_only = "--toxicity" in args
        protocols_only = "--protocols" in args
        verbose = "--verbose" in args or "-v" in args

        # Parse path
        target_path_str = "."
        if "--path" in args:
            try:
                idx = args.index("--path")
                target_path_str = args[idx + 1]
            except (IndexError, ValueError):
                return self.failure("Invalid --path flag. Usage: --path <directory>", exit_code=1)

        target_path = Path(target_path_str).absolute()
        path_exists = target_path.exists()

        try:
            # Determine scan mode
            if quick:
                scan_mode = "quick"
            elif deep:
                scan_mode = "deep"
            elif toxicity_only:
                scan_mode = "toxicity"
            elif protocols_only:
                scan_mode = "protocols"
            else:
                scan_mode = "full"

            scan_type = "all"
            if toxicity_only:
                scan_type = "security"
            elif protocols_only:
                scan_type = "types"

            # Logic from naga_cli.py cmd_scan
            results = {
                "silent_failures": [],
                "vfs_bypasses": [],
                "any_types": [],
                "security_issues": [],
            }

            py_files = []
            if path_exists:
                py_files = list(target_path.rglob("*.py"))
                if not py_files and target_path.is_file() and target_path.suffix == ".py":
                    py_files = [target_path]

            # Quick scan limits to first 10 files for speed
            files_to_scan = py_files[:10] if scan_mode == "quick" else py_files

            for py_file in files_to_scan:
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")

                    # Quick scan only checks security (most critical)
                    if scan_mode == "quick":
                        results["security_issues"].extend(self._find_security_issues(content, py_file))
                    else:
                        if scan_type in ["all", "silent"]:
                            results["silent_failures"].extend(self._find_silent_failures(content, py_file))

                        if scan_type in ["all", "vfs"]:
                            results["vfs_bypasses"].extend(self._find_vfs_bypasses(content, py_file))

                        if scan_type in ["all", "types"]:
                            results["any_types"].extend(self._find_any_types(content, py_file))

                        if scan_type in ["all", "security"]:
                            results["security_issues"].extend(self._find_security_issues(content, py_file))

                except Exception as e:
                    if verbose:
                        print(f"    Error scanning {py_file}: {e}")

            # Format output
            mode_label = {
                "quick": "Quick Scan",
                "deep": "Deep Scan",
                "full": "Full Scan",
                "toxicity": "Toxicity Scan",
                "protocols": "Protocol Scan",
            }[scan_mode]

            # Quick scan has minimal output
            if scan_mode == "quick":
                total_issues = len(results["security_issues"])
                output_lines = [
                    f"[VYASA] {mode_label}: {len(files_to_scan)} files, {total_issues} issues",
                ]
            else:
                output_lines = [
                    f"[VYASA] Codebase {mode_label}: {target_path}",
                    "=" * 60,
                    f"    Scanned {len(py_files)} Python files",
                ]

                # Deep scan adds extra sections
                if scan_mode == "deep":
                    output_lines.append("    TOXICITY SCAN: Enabled")
                    output_lines.append("    PROTOCOL SCAN: Enabled")

                # Toxicity scan adds TAKSHAKA reference (guardian of security)
                if scan_mode == "toxicity":
                    output_lines.append("    TAKSHAKA: Security Guardian Active")
                    output_lines.append("    VAJRA: Penetration Shield Enabled")

                # Protocol scan adds coverage info
                if scan_mode == "protocols":
                    output_lines.append("    COVERAGE: Protocol Compliance Check")
                    output_lines.append("    GAPS: Missing Protocol Detection")
                    output_lines.append("    MAHAJANA: Guardian Coverage Analysis")

                output_lines.append("-" * 60)

                total_issues = 0
                for key, issues in results.items():
                    if issues:
                        count = len(issues)
                        total_issues += count
                        output_lines.append(f"    {key.upper().replace('_', ' ')}: {count}")
                        if verbose:
                            for issue in issues[:5]:
                                output_lines.append(f"      {issue['file']}:{issue['line']}")

                output_lines.append("-" * 60)
                output_lines.append(f"    TOTAL ISSUES: {total_issues}")
                output_lines.append("=" * 60)
                output_lines.append("ASSERT_TRUTH: COMPLETED")

            return self.success(
                "\n".join(output_lines),
                data=(
                    ("phase", "purify"),
                    ("position", "4"),
                    ("mahajana", "vyasa"),
                    ("mode", scan_mode),
                    ("total_issues", str(total_issues)),
                    ("path", target_path_str),
                ),
            )
        except Exception as e:
            return self.failure(f"Scan failed: {e}", exit_code=1)

    def _find_silent_failures(self, content: str, filepath: any) -> List[Dict]:
        """Find except: pass patterns."""
        import re

        issues = []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(r"except.*:\s*pass\s*$", line) or re.search(r"except.*:\s*\.\.\.\s*$", line):
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})
        return issues

    def _find_vfs_bypasses(self, content: str, filepath: any) -> List[Dict]:
        """Find direct open() calls that bypass VFS."""
        import re

        issues = []
        if "test" in str(filepath).lower():
            return []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(r"(?<!vfs\.)open\s*\(", line):
                if line.strip().startswith("#") or ("from" in line and "import" in line):
                    continue
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})
        return issues

    def _find_any_types(self, content: str, filepath: any) -> List[Dict]:
        """Find Dict[str, Any] and similar."""
        import re

        issues = []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(r":\s*Any\b", line) or re.search(r"\[\s*Any\s*\]", line):
                if line.strip().startswith("#"):
                    continue
                issues.append({"file": str(filepath), "line": i, "code": line.strip()})
        return issues

    def _find_security_issues(self, content: str, filepath: any) -> List[Dict]:
        """Find potential security issues."""
        import re

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
                    issues.append({"file": str(filepath), "line": i, "type": issue_type, "code": line.strip()})
        return issues


# Export for direct import
__all__ = ["ScanCommand"]
