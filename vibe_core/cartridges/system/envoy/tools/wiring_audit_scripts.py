#!/usr/bin/env python3
"""
🔌 WIRING AUDIT SCRIPTS
========================

Python implementations for the WIRING_AUDIT circuit.
These functions are called by the DeterministicExecutor when running audit phases.

Designed by Opus (Senior Audit Sprint)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x165696e9"  # GenesisByte: parampara % 37 == 0

import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("WIRING_AUDIT")


class WiringAuditor:
    """
    Automated System Integration Auditor.

    Finds:
    - Missing kernel injections
    - Unhandled routing paths
    - Stub code that should be live
    - Missing agent methods
    - Unregistered action handlers
    """

    def __init__(self, kernel=None, project_root: Optional[Path] = None):
        self.kernel = kernel
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent.parent
        self.findings: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.passed_checks: List[str] = []

    def run_full_audit(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all audit checks and generate report."""
        logger.info("🔌 WIRING AUDIT STARTED")
        logger.info("=" * 60)

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "running",
            "phases": {},
        }

        # Phase 1: Kernel Injection
        results["phases"]["kernel_injection"] = self.check_kernel_injection()

        # Phase 2: Routing Paths
        results["phases"]["routing_paths"] = self.check_routing_paths()

        # Phase 3: Stub Detection
        results["phases"]["stubs"] = self.find_stubs(verbose=verbose)

        # Phase 4: Agent Methods
        results["phases"]["agent_methods"] = self.check_agent_methods()

        # Phase 5: Action Handlers
        results["phases"]["action_handlers"] = self.check_action_handlers()

        # Compile summary
        total_issues = sum(len(phase.get("findings", [])) for phase in results["phases"].values())

        critical = sum(
            1
            for phase in results["phases"].values()
            for f in phase.get("findings", [])
            if f.get("severity") == "CRITICAL"
        )

        results["summary"] = {
            "total_issues": total_issues,
            "critical": critical,
            "high": sum(
                1 for p in results["phases"].values() for f in p.get("findings", []) if f.get("severity") == "HIGH"
            ),
            "medium": sum(
                1 for p in results["phases"].values() for f in p.get("findings", []) if f.get("severity") == "MEDIUM"
            ),
            "low": sum(
                1 for p in results["phases"].values() for f in p.get("findings", []) if f.get("severity") == "LOW"
            ),
            "passed_phases": sum(1 for p in results["phases"].values() if p.get("passed", False)),
            "total_phases": len(results["phases"]),
        }

        results["status"] = "PASS" if critical == 0 else "FAIL"

        logger.info("=" * 60)
        logger.info(f"🔌 WIRING AUDIT COMPLETE: {results['status']}")
        logger.info(f"   Total issues: {total_issues} (Critical: {critical})")

        return results

    def check_kernel_injection(self) -> Dict[str, Any]:
        """Phase 1: Verify all agents have kernel reference."""
        logger.info("\n📍 Phase 1: Kernel Injection Audit")
        findings = []

        if not self.kernel:
            logger.warning("   ⚠️ No kernel available - skipping runtime check")
            # Static check instead
            return self._static_kernel_check()

        for agent_id, agent in self.kernel._agent_registry.items():
            # Check kernel reference
            if agent.kernel is None:
                findings.append(
                    {
                        "agent": agent_id,
                        "issue": "agent.kernel is None",
                        "severity": "CRITICAL",
                        "fix": "Ensure agent.set_kernel(kernel) is called in register_agent()",
                        "file": f"vibe_core/cartridges/system/{agent_id}/cartridge_main.py",
                    }
                )

            # Check system interface
            if not hasattr(agent, "system") or agent.system is None:
                findings.append(
                    {
                        "agent": agent_id,
                        "issue": "agent.system is None",
                        "severity": "HIGH",
                        "fix": "Ensure agent.system = AgentSystemInterface() in register_agent()",
                        "file": "vibe_core/kernel_impl.py:740",
                    }
                )

        passed = len(findings) == 0
        logger.info(f"   {'✅ PASS' if passed else '❌ FAIL'}: {len(findings)} issues found")

        return {"findings": findings, "passed": passed, "checked": len(self.kernel._agent_registry)}

    def _static_kernel_check(self) -> Dict[str, Any]:
        """Static analysis when kernel not available."""
        findings = []

        # Check kernel_impl.py has set_kernel call
        kernel_impl = self.project_root / "vibe_core" / "kernel_impl.py"
        if kernel_impl.exists():
            content = kernel_impl.read_text()
            if "agent.set_kernel(self)" not in content:
                findings.append(
                    {
                        "file": "vibe_core/kernel_impl.py",
                        "issue": "Missing agent.set_kernel(self) call",
                        "severity": "CRITICAL",
                        "fix": "Add 'agent.set_kernel(self)' before system interface injection",
                    }
                )

        return {"findings": findings, "passed": len(findings) == 0, "mode": "static"}

    def check_routing_paths(self) -> Dict[str, Any]:
        """Phase 2: Verify all routing paths are handled."""
        logger.info("\n📍 Phase 2: Routing Path Audit")
        findings = []

        expected_paths = ["flash", "science", "lazy", "critical"]
        expected_statuses = ["routing", "queued", "blocked", "delegated", "completed", "critical"]

        files_to_check = [
            ("vibe_core/cartridges/system/envoy/cartridge_main.py", expected_paths + ["routing", "queued", "blocked"]),
            ("scripts/heartbeat.py", expected_statuses),
        ]

        for file_path, paths in files_to_check:
            full_path = self.project_root / file_path
            if not full_path.exists():
                findings.append(
                    {
                        "file": file_path,
                        "issue": "File not found",
                        "severity": "HIGH",
                    }
                )
                continue

            content = full_path.read_text()
            for path in paths:
                patterns = [
                    f'path == "{path}"',
                    f"path == '{path}'",
                    f'status == "{path}"',
                    f"status == '{path}'",
                    f'"{path}"' if path in ["flash", "science"] else None,
                ]
                patterns = [p for p in patterns if p]

                if not any(p in content for p in patterns):
                    findings.append(
                        {
                            "file": file_path,
                            "path": path,
                            "issue": f"Path/status '{path}' not handled",
                            "severity": "HIGH" if path in ["flash", "science", "critical"] else "MEDIUM",
                            "fix": f"Add handler for '{path}' in process() method",
                        }
                    )

        passed = len(findings) == 0
        logger.info(f"   {'✅ PASS' if passed else '❌ FAIL'}: {len(findings)} issues found")

        return {"findings": findings, "passed": passed}

    def find_stubs(self, verbose: bool = False) -> Dict[str, Any]:
        """Phase 3: Find stub code that should be live."""
        logger.info("\n📍 Phase 3: Stub Detection")
        findings = []

        stub_patterns = {
            "NotImplementedError": "CRITICAL",
            "# STUB": "HIGH",
            "# TODO.*implement": "MEDIUM",
            "Would create": "HIGH",
            "Would write": "HIGH",
            "Would init": "HIGH",
            "pass  #": "LOW",
            "# Mock": "MEDIUM",
            "simulate.*=.*True": "MEDIUM",
        }

        exclude_dirs = ["tests/", "scripts/research/", "__pycache__", ".git", "node_modules"]
        exclude_files = ["wiring_audit_scripts.py"]  # Don't audit ourselves

        # Exclusion patterns for known false positives
        exclude_patterns = [
            # Intentional deprecation stubs with helpful error messages
            "vibe_core/specialists/__init__.py",
            # Abstract base classes (NotImplementedError is correct pattern)
            "vibe_core/specialists/base_specialist.py",
            "vibe_core/playbook/executor.py",
            "vibe_core/cartridges/system/scribe/tools/base.py",  # Abstract Tool base class
            # NotImplementedError in strings/pattern lists (not real stubs)
            "vibe_core/cartridges/system/oracle/tools/introspection_tool.py",  # Line 328: string reference
            "vibe_core/cartridges/system/watchman/cartridge_main.py",  # Line 65: pattern list
            # Templates (TODOs expected)
            "starter-packs/",
            "engineer/templates/",
            # Example agents (not core system)
            "vibe_core/cartridges/agent_city/",
            # Audit tool itself
            "wiring_audit_scripts.py",
            # Test files
            "/test_",
            "_test.py",
            # Documentation examples
            "examples/",
            "docs/",
        ]

        search_dirs = ["steward/", "vibe_core/", "scripts/"]

        for pattern, severity in stub_patterns.items():
            try:
                result = subprocess.run(
                    ["grep", "-rn", "-E", pattern]
                    + [str(self.project_root / d) for d in search_dirs if (self.project_root / d).exists()]
                    + ["--include=*.py"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue

                    # Skip excluded paths (both dirs and patterns)
                    if any(ex in line for ex in exclude_dirs + exclude_files + exclude_patterns):
                        continue

                    parts = line.split(":", 2)
                    if len(parts) >= 2:
                        findings.append(
                            {
                                "file": parts[0].replace(str(self.project_root) + "/", ""),
                                "line": parts[1],
                                "pattern": pattern,
                                "severity": severity,
                                "content": parts[2][:80] if len(parts) > 2 else "",
                            }
                        )

            except subprocess.TimeoutExpired:
                logger.warning(f"   ⚠️ Timeout searching for pattern: {pattern}")
            except Exception as e:
                logger.warning(f"   ⚠️ Error searching for pattern {pattern}: {e}")

        # Deduplicate by file:line
        seen = set()
        unique_findings = []
        for f in findings:
            key = f"{f['file']}:{f['line']}"
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)

        findings = unique_findings

        # Count by severity
        by_severity = {}
        for f in findings:
            sev = f["severity"]
            by_severity[sev] = by_severity.get(sev, 0) + 1

        critical_count = by_severity.get("CRITICAL", 0)
        passed = critical_count == 0

        logger.info(f"   {'✅ PASS' if passed else '❌ FAIL'}: {len(findings)} stubs found")
        if verbose:
            for sev, count in sorted(by_severity.items()):
                logger.info(f"      {sev}: {count}")

        return {
            "findings": findings,
            "passed": passed,
            "by_severity": by_severity,
            "total_stubs": len(findings),
        }

    def check_agent_methods(self) -> Dict[str, Any]:
        """Phase 4: Verify agents implement required methods."""
        logger.info("\n📍 Phase 4: Agent Method Audit")
        findings = []

        required_methods = ["process", "get_manifest", "report_status"]
        async_required = ["process"]

        agents_dir = self.project_root / "steward" / "system_agents"

        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            cartridge = agent_dir / "cartridge_main.py"
            if not cartridge.exists():
                continue

            content = cartridge.read_text()
            agent_name = agent_dir.name

            # Also check agent.py for inherited methods
            agent_py = agent_dir / "agent.py"
            inherited_content = agent_py.read_text() if agent_py.exists() else ""

            for method in required_methods:
                # Check if method exists in cartridge OR inherited from agent.py
                sync_pattern = rf"def {method}\s*\("
                async_pattern = rf"async def {method}\s*\("

                has_sync = bool(re.search(sync_pattern, content))
                has_async = bool(re.search(async_pattern, content))

                # Check inherited methods
                inherited_sync = bool(re.search(sync_pattern, inherited_content))
                inherited_async = bool(re.search(async_pattern, inherited_content))

                total_sync = has_sync or inherited_sync
                total_async = has_async or inherited_async

                if not total_sync and not total_async:
                    findings.append(
                        {
                            "agent": agent_name,
                            "method": method,
                            "issue": f"Missing method: {method}()",
                            "severity": "HIGH" if method == "process" else "MEDIUM",
                            "fix": f"Add {method}() method to {agent_name} cartridge",
                        }
                    )
                elif method in async_required and total_sync and not total_async:
                    findings.append(
                        {
                            "agent": agent_name,
                            "method": method,
                            "issue": f"Method {method}() should be async",
                            "severity": "MEDIUM",
                            "fix": f"Change 'def {method}' to 'async def {method}'",
                        }
                    )

        passed = len(findings) == 0
        logger.info(f"   {'✅ PASS' if passed else '❌ FAIL'}: {len(findings)} issues found")

        return {"findings": findings, "passed": passed}

    def check_action_handlers(self) -> Dict[str, Any]:
        """Phase 5: Verify action handlers are registered."""
        logger.info("\n📍 Phase 5: Action Handler Audit")
        findings = []

        required_handlers = [
            "CHECK_STATE",
            "EXECUTE_SCRIPT",
            "EMIT_EVENT",
            "CALL_AGENT",
            "CALL_PLAYBOOK",
        ]

        handler_file = self.project_root / "steward" / "system_agents" / "envoy" / "action_handlers.py"

        if not handler_file.exists():
            findings.append(
                {
                    "file": "action_handlers.py",
                    "issue": "Action handlers file not found",
                    "severity": "CRITICAL",
                }
            )
            return {"findings": findings, "passed": False}

        content = handler_file.read_text()

        for handler_type in required_handlers:
            # Check for handler class or registration
            patterns = [
                f"action_type.*{handler_type}",
                f'"{handler_type}"',
                f"'{handler_type}'",
            ]

            if not any(re.search(p, content) for p in patterns):
                findings.append(
                    {
                        "handler": handler_type,
                        "issue": f"No handler for action type: {handler_type}",
                        "severity": "HIGH",
                        "fix": f"Create handler class for {handler_type} action type",
                    }
                )

        passed = len(findings) == 0
        logger.info(f"   {'✅ PASS' if passed else '❌ FAIL'}: {len(findings)} issues found")

        return {"findings": findings, "passed": passed}

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate a markdown report from audit results."""
        lines = [
            "# 🔌 WIRING AUDIT REPORT",
            "",
            f"> **Timestamp:** {results['timestamp']}",
            f"> **Status:** {'✅ PASS' if results['status'] == 'PASS' else '❌ FAIL'}",
            "",
            "---",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Issues | {results['summary']['total_issues']} |",
            f"| Critical | {results['summary']['critical']} |",
            f"| High | {results['summary']['high']} |",
            f"| Medium | {results['summary']['medium']} |",
            f"| Low | {results['summary']['low']} |",
            f"| Phases Passed | {results['summary']['passed_phases']}/{results['summary']['total_phases']} |",
            "",
            "---",
            "",
        ]

        for phase_name, phase_data in results["phases"].items():
            status = "✅ PASS" if phase_data.get("passed", False) else "❌ ISSUES"
            lines.append(f"## Phase: {phase_name.replace('_', ' ').title()}")
            lines.append(f"**Status:** {status}")
            lines.append("")

            findings = phase_data.get("findings", [])
            if findings:
                lines.append("### Findings")
                lines.append("")
                for f in findings:
                    severity = f.get("severity", "UNKNOWN")
                    emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
                    lines.append(f"- {emoji} **{severity}**: {f.get('issue', 'Unknown issue')}")
                    if f.get("file"):
                        lines.append(f"  - File: `{f['file']}`")
                    if f.get("fix"):
                        lines.append(f"  - Fix: {f['fix']}")
                lines.append("")
            else:
                lines.append("No issues found.")
                lines.append("")

            lines.append("---")
            lines.append("")

        lines.append("")
        lines.append("*Generated by WIRING_AUDIT Circuit*")

        return "\n".join(lines)


# ============================================================
# CLI ENTRY POINT
# ============================================================


def main():
    """Run wiring audit from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Run wiring audit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", type=str, help="Output file for report")
    parser.add_argument("--scope", choices=["full", "kernel", "routing", "stubs"], default="full")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    auditor = WiringAuditor()

    if args.scope == "full":
        results = auditor.run_full_audit(verbose=args.verbose)
    elif args.scope == "kernel":
        results = {"phases": {"kernel_injection": auditor.check_kernel_injection()}}
    elif args.scope == "routing":
        results = {"phases": {"routing_paths": auditor.check_routing_paths()}}
    elif args.scope == "stubs":
        results = {"phases": {"stubs": auditor.find_stubs(verbose=args.verbose)}}

    if args.output:
        report = auditor.generate_markdown_report(results) if "timestamp" in results else str(results)
        Path(args.output).write_text(report)
        print(f"\n📄 Report saved to: {args.output}")

    # Exit with error code if critical issues found
    if results.get("summary", {}).get("critical", 0) > 0:
        exit(1)


if __name__ == "__main__":
    main()
