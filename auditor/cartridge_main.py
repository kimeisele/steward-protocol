#!/usr/bin/env python3
"""
AUDITOR Cartridge - The GAD-000 Enforcement Agent

This cartridge demonstrates meta-level verification in the Steward Protocol:
1. Verifies agent identity integrity (all agents have valid cartridge.yaml)
2. Verifies documentation sync (STEWARD.md exists and is valid)
3. Verifies event log resilience (event logs are intact)
4. Enforces GAD-000 compliance at the system level

This is Agent #3 in the STEWARD Protocol ecosystem - The Watcher of Watchers.

"Who watches the watchers?" - The AUDITOR does.

Usage:
    Standalone: python auditor/shim.py --action audit
    VibeOS:     kernel.load_cartridge("auditor").run_compliance_audit()
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path

from auditor.tools.compliance_tool import ComplianceTool

logger = logging.getLogger("AUDITOR_CARTRIDGE")


class AuditorCartridge:
    """
    AUDITOR - The GAD-000 Enforcement Agent for STEWARD Protocol.

    This cartridge encapsulates the system integrity workflow:
    1. Identity Check: Verify all agents have valid identities
    2. Documentation Check: Verify STEWARD.md is synchronized
    3. Resilience Check: Verify event logs are intact
    4. Report: Generate compliance report and FAIL BUILD if violations found

    Architecture:
    - Vibe-OS compatible (ARCH-050 CartridgeBase)
    - Meta-verification (verifies the system, not just agents)
    - Enforcement-first (fails builds on violations)
    - Zero-tolerance (GAD-000 compliance is non-negotiable)

    Unlike HERALD (creator) and ARCHIVIST (verifier), AUDITOR verifies
    the SYSTEM ITSELF. It is the meta-level guardian.
    """

    # Cartridge Metadata (ARCH-050 required fields)
    name = "auditor"
    version = "1.0.0"
    description = "System integrity and GAD-000 compliance enforcement agent"
    author = "Steward Protocol"

    def __init__(self, root_path: Path = Path(".")):
        """
        Initialize AUDITOR cartridge.

        Args:
            root_path: Root path of the repository
        """
        logger.info("🔍 AUDITOR v1.0: Cartridge initialization")

        # Initialize compliance tool
        self.compliance = ComplianceTool(root_path=root_path)
        self.root_path = root_path

        logger.info("✅ AUDITOR: Ready for compliance enforcement")

    def get_config(self) -> Dict[str, Any]:
        """Get cartridge configuration (ARCH-050 interface)."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
        }

    def report_status(self) -> Dict[str, Any]:
        """Report cartridge status (ARCH-050 interface) - Deep Introspection."""
        # Try to get compliance statistics
        compliance_stats = {}
        try:
            # Count report files if they exist
            reports_dir = self.root_path / "data" / "reports"
            reports_count = len(list(reports_dir.glob("*.json"))) if reports_dir.exists() else 0
            compliance_stats["reports_generated"] = reports_count
            compliance_stats["reports_dir"] = str(reports_dir)
        except:
            compliance_stats["reports_generated"] = 0

        return {
            "agent_id": "auditor",
            "name": self.name,
            "version": self.version,
            "status": "RUNNING",
            "domain": "SECURITY",
            "enforcement_mode": "fail_build",
            "compliance_metrics": {
                "root_path": str(self.root_path),
                "reports_generated": compliance_stats.get("reports_generated", 0),
                "reports_dir": compliance_stats.get("reports_dir", str(self.root_path / "data" / "reports")),
                "enforcement_enabled": True,
            }
        }

    def run_compliance_audit(
        self,
        save_report: bool = True,
        fail_on_violation: bool = True
    ) -> Dict[str, Any]:
        """
        Execute GAD-000 compliance audit.

        This is the main workflow:
        1. Run all compliance checks (identity, docs, events)
        2. Generate comprehensive compliance report
        3. Save report to data/reports/
        4. FAIL BUILD if violations found (unless fail_on_violation=False)

        Args:
            save_report: If True, save report to file
            fail_on_violation: If True, fail build on violations

        Returns:
            dict: Audit result with status and report
        """
        try:
            logger.info("🔍 PHASE 1: COMPLIANCE AUDIT")
            logger.info("=" * 70)

            # Run compliance audit
            report = self.compliance.run_compliance_audit()

            # Save report if requested
            if save_report:
                logger.info("\n🔍 PHASE 2: REPORT GENERATION")
                logger.info("=" * 70)

                report_path = self.root_path / "data" / "reports" / "audit_compliance.json"
                if self.compliance.save_report(report, report_path):
                    logger.info(f"✅ Compliance report saved: {report_path}")
                else:
                    logger.warning("⚠️  Failed to save compliance report")

            # Build result
            result = {
                "status": "passed" if report.passed else "failed",
                "report": report.to_dict(),
                "violations_count": len(report.violations),
                "warnings_count": len(report.warnings),
                "summary": report.summary,
            }

            # Enforcement: Fail build if violations found
            if not report.passed and fail_on_violation:
                logger.error("\n" + "=" * 70)
                logger.error("❌ GAD-000 COMPLIANCE VIOLATION DETECTED")
                logger.error("=" * 70)
                logger.error(f"   Violations: {len(report.violations)}")
                logger.error("")

                for idx, violation in enumerate(report.violations, 1):
                    logger.error(f"   [{idx}] {violation.check_type.upper()}")
                    logger.error(f"       Severity: {violation.severity}")
                    logger.error(f"       Message: {violation.message}")
                    if violation.details:
                        logger.error(f"       Details: {violation.details}")
                    logger.error("")

                logger.error("=" * 70)
                logger.error("❌ BUILD FAILED: Fix violations and retry")
                logger.error("=" * 70)

                # Exit with error code to fail CI/CD pipeline
                sys.exit(1)

            # Success path
            logger.info("\n" + "=" * 70)
            logger.info("✅ COMPLIANCE AUDIT COMPLETE")
            logger.info("=" * 70)
            logger.info(f"   Status: {result['status'].upper()}")
            logger.info(f"   Violations: {result['violations_count']}")
            logger.info(f"   Warnings: {result['warnings_count']}")
            logger.info("=" * 70)

            if result['warnings_count'] > 0:
                logger.info("\n⚠️  WARNINGS:")
                for idx, warning in enumerate(report.warnings, 1):
                    logger.info(f"   [{idx}] {warning.message}")
                logger.info("")

            return result

        except Exception as e:
            logger.error(f"❌ Compliance audit error: {e}")
            import traceback
            tb = traceback.format_exc()
            logger.error(f"   Traceback: {tb}")

            # On error, fail build if enforcement is enabled
            if fail_on_violation:
                logger.error("\n❌ BUILD FAILED: Audit execution error")
                sys.exit(1)

            return {
                "status": "error",
                "reason": "audit_execution_error",
                "error": str(e),
            }

    def verify_single_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Verify a single agent's compliance (for testing or API use).

        Args:
            agent_name: Name of agent to verify (e.g., "herald")

        Returns:
            dict: Verification result
        """
        logger.info(f"🔍 Verifying agent: {agent_name}")

        cartridge_path = self.root_path / agent_name / "cartridge.yaml"

        if not cartridge_path.exists():
            return {
                "agent": agent_name,
                "status": "failed",
                "reason": "cartridge_not_found",
                "path": str(cartridge_path),
            }

        # Basic validation could be added here
        return {
            "agent": agent_name,
            "status": "passed",
            "path": str(cartridge_path),
        }


# Export for VibeOS cartridge loading
__all__ = ["AuditorCartridge"]
