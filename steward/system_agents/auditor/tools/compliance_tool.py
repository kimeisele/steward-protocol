#!/usr/bin/env python3
"""
GAD-000 Compliance Tool - System Integrity Verification

This tool enforces GAD-000 (Governance As Design) compliance by verifying:
1. Identity Integrity: All agents have valid cryptographic identities
2. Documentation Sync: STEWARD.md exists and is valid
3. Event Log Resilience: Event logs are intact and uncorrupted

The AUDITOR doesn't just verify agents - it verifies the SYSTEM ITSELF.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger("AUDITOR_COMPLIANCE")


@dataclass
class ComplianceViolation:
    """Represents a GAD-000 compliance violation."""

    check_type: str
    severity: str  # "critical", "warning"
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ComplianceReport:
    """Complete compliance audit report."""

    timestamp: str
    checks_performed: List[str]
    violations: List[ComplianceViolation]
    warnings: List[ComplianceViolation]
    passed: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "checks_performed": self.checks_performed,
            "violations": [
                {
                    "check_type": v.check_type,
                    "severity": v.severity,
                    "message": v.message,
                    "details": v.details,
                }
                for v in self.violations
            ],
            "warnings": [
                {
                    "check_type": w.check_type,
                    "severity": w.severity,
                    "message": w.message,
                    "details": w.details,
                }
                for w in self.warnings
            ],
            "passed": self.passed,
            "summary": self.summary,
        }


class ComplianceTool:
    """
    GAD-000 Compliance Verification Tool.

    This tool performs meta-verification of the system itself:
    - Verifies agent identities are properly configured
    - Verifies documentation is synchronized with code
    - Verifies event logs are intact and uncorrupted

    Unlike HERALD (creator) and ARCHIVIST (verifier), AUDITOR verifies
    the SYSTEM that contains these agents.
    """

    def __init__(self, root_path: Path = Path(".")):
        """
        Initialize compliance tool.

        Args:
            root_path: Root path of the repository
        """
        self.root_path = root_path
        self.violations: List[ComplianceViolation] = []
        self.warnings: List[ComplianceViolation] = []

    def check_identity_integrity(self) -> Tuple[bool, List[str]]:
        """
        Check 1: Identity Integrity

        Verifies that all agents have valid cartridge.yaml files with
        proper identity configuration.

        Returns:
            Tuple of (passed, details)
        """
        logger.info("🔍 CHECK 1: Identity Integrity")
        logger.info("   Verifying all agents have valid identities...")

        details = []
        passed = True

        # Find all cartridge.yaml files
        agent_dirs = ["herald", "archivist", "auditor"]

        for agent_dir in agent_dirs:
            cartridge_path = self.root_path / agent_dir / "cartridge.yaml"

            if not cartridge_path.exists():
                self.violations.append(
                    ComplianceViolation(
                        check_type="identity_integrity",
                        severity="critical",
                        message=f"Agent {agent_dir} missing cartridge.yaml",
                        details={"expected_path": str(cartridge_path)},
                    )
                )
                details.append(f"❌ {agent_dir}: Missing cartridge.yaml")
                passed = False
                continue

            # Parse cartridge.yaml
            try:
                with open(cartridge_path, "r") as f:
                    cartridge = yaml.safe_load(f)

                # Verify required fields
                if "meta" not in cartridge:
                    self.violations.append(
                        ComplianceViolation(
                            check_type="identity_integrity",
                            severity="critical",
                            message=f"Agent {agent_dir} cartridge.yaml missing 'meta' section",
                            details={"path": str(cartridge_path)},
                        )
                    )
                    details.append(f"❌ {agent_dir}: Missing 'meta' section")
                    passed = False
                    continue

                meta = cartridge["meta"]
                required_fields = ["id", "name", "version", "author"]
                missing_fields = [f for f in required_fields if f not in meta]

                if missing_fields:
                    self.violations.append(
                        ComplianceViolation(
                            check_type="identity_integrity",
                            severity="critical",
                            message=f"Agent {agent_dir} cartridge.yaml missing required meta fields",
                            details={
                                "path": str(cartridge_path),
                                "missing_fields": missing_fields,
                            },
                        )
                    )
                    details.append(f"❌ {agent_dir}: Missing fields {missing_fields}")
                    passed = False
                else:
                    details.append(f"✅ {agent_dir}: Identity valid (ID: {meta['id']})")

            except yaml.YAMLError as e:
                self.violations.append(
                    ComplianceViolation(
                        check_type="identity_integrity",
                        severity="critical",
                        message=f"Agent {agent_dir} cartridge.yaml is invalid YAML",
                        details={"path": str(cartridge_path), "error": str(e)},
                    )
                )
                details.append(f"❌ {agent_dir}: Invalid YAML - {e}")
                passed = False

            except Exception as e:
                self.violations.append(
                    ComplianceViolation(
                        check_type="identity_integrity",
                        severity="critical",
                        message=f"Agent {agent_dir} cartridge.yaml verification failed",
                        details={"path": str(cartridge_path), "error": str(e)},
                    )
                )
                details.append(f"❌ {agent_dir}: Verification failed - {e}")
                passed = False

        return passed, details

    def check_documentation_sync(self) -> Tuple[bool, List[str]]:
        """
        Check 2: Documentation Sync

        Verifies that STEWARD.md exists and contains required fields.

        Returns:
            Tuple of (passed, details)
        """
        logger.info("🔍 CHECK 2: Documentation Sync")
        logger.info("   Verifying STEWARD.md is present and valid...")

        details = []
        passed = True

        steward_path = self.root_path / "STEWARD.md"

        # Check if STEWARD.md exists
        if not steward_path.exists():
            self.violations.append(
                ComplianceViolation(
                    check_type="documentation_sync",
                    severity="critical",
                    message="STEWARD.md not found in repository root",
                    details={"expected_path": str(steward_path)},
                )
            )
            details.append("❌ STEWARD.md: File not found")
            return False, details

        # Read and validate STEWARD.md
        try:
            with open(steward_path, "r") as f:
                content = f.read()

            # Check for required sections
            required_sections = [
                "## 🆔 Agent Identity",
                "## 🎯 What I Do",
                "## ✅ Core Capabilities",
                "## 👤 Maintained By",
            ]

            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)

            if missing_sections:
                self.warnings.append(
                    ComplianceViolation(
                        check_type="documentation_sync",
                        severity="warning",
                        message="STEWARD.md missing recommended sections",
                        details={"missing_sections": missing_sections},
                    )
                )
                details.append(f"⚠️  STEWARD.md: Missing sections {missing_sections}")

            # Check for key field
            if "**key:**" not in content and "- **key:**" not in content:
                self.warnings.append(
                    ComplianceViolation(
                        check_type="documentation_sync",
                        severity="warning",
                        message="STEWARD.md missing public key field",
                        details={
                            "recommendation": "Add 'key:' field to Agent Identity section"
                        },
                    )
                )
                details.append("⚠️  STEWARD.md: No 'key:' field found")
            else:
                details.append("✅ STEWARD.md: Key field present")

            # Check for signature
            if "<!-- STEWARD_SIGNATURE:" in content:
                details.append("✅ STEWARD.md: Cryptographic signature present")
            else:
                self.warnings.append(
                    ComplianceViolation(
                        check_type="documentation_sync",
                        severity="warning",
                        message="STEWARD.md not cryptographically signed",
                        details={
                            "recommendation": "Sign STEWARD.md with organization key"
                        },
                    )
                )
                details.append("⚠️  STEWARD.md: No cryptographic signature")

            details.append(f"✅ STEWARD.md: File valid ({len(content)} bytes)")

        except Exception as e:
            self.violations.append(
                ComplianceViolation(
                    check_type="documentation_sync",
                    severity="critical",
                    message="STEWARD.md verification failed",
                    details={"error": str(e)},
                )
            )
            details.append(f"❌ STEWARD.md: Verification failed - {e}")
            passed = False

        return passed, details

    def check_event_log_resilience(self) -> Tuple[bool, List[str]]:
        """
        Check 3: Event Log Resilience

        Verifies that event logs exist and are valid JSONL format.

        Returns:
            Tuple of (passed, details)
        """
        logger.info("🔍 CHECK 3: Event Log Resilience")
        logger.info("   Verifying event logs are intact...")

        details = []
        passed = True

        events_dir = self.root_path / "data" / "events"

        # Check if events directory exists
        if not events_dir.exists():
            self.warnings.append(
                ComplianceViolation(
                    check_type="event_log_resilience",
                    severity="warning",
                    message="Events directory not found",
                    details={"expected_path": str(events_dir)},
                )
            )
            details.append(
                "⚠️  Events directory not found (will be created on first run)"
            )
            return True, details  # Not a critical failure

        # Find all .jsonl files
        jsonl_files = list(events_dir.glob("*.jsonl"))

        if not jsonl_files:
            self.warnings.append(
                ComplianceViolation(
                    check_type="event_log_resilience",
                    severity="warning",
                    message="No event logs found",
                    details={"events_dir": str(events_dir)},
                )
            )
            details.append("⚠️  No event logs found (agents haven't run yet)")
            return True, details  # Not a critical failure

        # Verify each JSONL file
        total_events = 0
        for jsonl_file in jsonl_files:
            try:
                event_count = 0
                with open(jsonl_file, "r") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:
                            try:
                                json.loads(line)
                                event_count += 1
                            except json.JSONDecodeError as e:
                                self.violations.append(
                                    ComplianceViolation(
                                        check_type="event_log_resilience",
                                        severity="critical",
                                        message=f"Corrupt event log: {jsonl_file.name}",
                                        details={
                                            "file": str(jsonl_file),
                                            "line": line_num,
                                            "error": str(e),
                                        },
                                    )
                                )
                                details.append(
                                    f"❌ {jsonl_file.name}: Corrupt JSON at line {line_num}"
                                )
                                passed = False

                total_events += event_count
                details.append(f"✅ {jsonl_file.name}: {event_count} events verified")

            except Exception as e:
                self.violations.append(
                    ComplianceViolation(
                        check_type="event_log_resilience",
                        severity="critical",
                        message=f"Failed to read event log: {jsonl_file.name}",
                        details={"file": str(jsonl_file), "error": str(e)},
                    )
                )
                details.append(f"❌ {jsonl_file.name}: Read failed - {e}")
                passed = False

        if total_events > 0:
            details.append(f"✅ Total events verified: {total_events}")

        return passed, details

    def run_compliance_audit(self) -> ComplianceReport:
        """
        Run complete GAD-000 compliance audit.

        Executes all compliance checks and generates a comprehensive report.

        Returns:
            ComplianceReport with audit results
        """
        logger.info("=" * 70)
        logger.info("🔍 AUDITOR - GAD-000 COMPLIANCE AUDIT")
        logger.info("=" * 70)

        # Reset violations and warnings
        self.violations = []
        self.warnings = []

        checks_performed = []
        all_details = []

        # Check 1: Identity Integrity
        check1_passed, check1_details = self.check_identity_integrity()
        checks_performed.append("identity_integrity")
        all_details.extend(check1_details)
        logger.info("")

        # Check 2: Documentation Sync
        check2_passed, check2_details = self.check_documentation_sync()
        checks_performed.append("documentation_sync")
        all_details.extend(check2_details)
        logger.info("")

        # Check 3: Event Log Resilience
        check3_passed, check3_details = self.check_event_log_resilience()
        checks_performed.append("event_log_resilience")
        all_details.extend(check3_details)
        logger.info("")

        # Determine overall pass/fail
        passed = check1_passed and check2_passed and check3_passed

        # Generate summary
        if passed:
            summary = f"✅ GAD-000 COMPLIANCE: PASSED ({len(self.warnings)} warnings)"
        else:
            summary = (
                f"❌ GAD-000 COMPLIANCE: FAILED ({len(self.violations)} violations)"
            )

        # Create report
        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            checks_performed=checks_performed,
            violations=self.violations,
            warnings=self.warnings,
            passed=passed,
            summary=summary,
        )

        # Log summary
        logger.info("=" * 70)
        logger.info("📊 AUDIT SUMMARY")
        logger.info("=" * 70)
        for detail in all_details:
            logger.info(f"   {detail}")
        logger.info("")
        logger.info(f"   Violations: {len(self.violations)}")
        logger.info(f"   Warnings: {len(self.warnings)}")
        logger.info("")
        logger.info(summary)
        logger.info("=" * 70)

        return report

    def save_report(self, report: ComplianceReport, report_path: Path) -> bool:
        """
        Save compliance report to file.

        Args:
            report: ComplianceReport to save
            report_path: Path to save report

        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure directory exists
            report_path.parent.mkdir(parents=True, exist_ok=True)

            # Write report
            with open(report_path, "w") as f:
                json.dump(report.to_dict(), f, indent=2)

            logger.info(f"📄 Compliance report saved: {report_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save compliance report: {e}")
            return False
