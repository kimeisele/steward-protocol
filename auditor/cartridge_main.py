#!/usr/bin/env python3
"""
AUDITOR Cartridge - The GAD-000 Enforcement Agent & Semantic Verifier

This cartridge encompasses THREE layers of verification:

LAYER 1: GAD-000 Compliance (Static Analysis)
- Verifies agent identity integrity (all agents have valid cartridge.yaml)
- Verifies documentation sync (STEWARD.md exists and is valid)
- Verifies event log resilience (event logs are intact)

LAYER 2: Semantic Verification (The JUDGE)
- Runs invariant rules against the event ledger
- Detects logical violations (not just syntax errors)
- Example: "BROADCAST without LICENSE_VALID" = violation

LAYER 3: Runtime Monitoring (The WATCHDOG)
- Continuous daemon that monitors ledger stream
- Records VIOLATION events when invariants break
- Can halt system on CRITICAL violations

This is Agent #3 in the STEWARD Protocol ecosystem - The Watcher of Watchers.

"Who watches the watchers?" - The AUDITOR does.

Usage:
    Standalone: python auditor/shim.py --action audit
    VibeOS:     kernel.load_cartridge("auditor").run_compliance_audit()
"""

import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from auditor.tools.compliance_tool import ComplianceTool
from auditor.tools.invariant_tool import get_judge
from auditor.tools.watchdog_tool import Watchdog, WatchdogConfig, WatchdogIntegration

logger = logging.getLogger("AUDITOR_CARTRIDGE")


class AuditorCartridge:
    """
    AUDITOR - The GAD-000 Enforcement & Semantic Verification Agent for STEWARD Protocol.

    This cartridge encapsulates THREE verification layers:
    
    LAYER 1: Static Compliance (ComplianceTool)
    - Identity Check: Verify all agents have valid identities
    - Documentation Check: Verify STEWARD.md is synchronized
    - Resilience Check: Verify event logs are intact
    
    LAYER 2: Semantic Verification (The JUDGE)
    - Runs invariant checks on the ledger
    - Detects logical violations in event sequences
    - Example: "BROADCAST without LICENSE_VALID" = CRITICAL violation
    
    LAYER 3: Runtime Monitoring (The WATCHDOG)
    - Continuous monitoring daemon
    - Records VIOLATION events
    - Can halt system on CRITICAL violations

    Unlike HERALD (creator) and ARCHIVIST (verifier), AUDITOR verifies
    the SYSTEM ITSELF at multiple levels. It is the meta-level guardian.
    """

    # Cartridge Metadata (ARCH-050 required fields)
    name = "auditor"
    version = "2.0.0"  # Now includes semantic verification
    description = "System integrity, GAD-000 compliance, and semantic verification enforcement agent"
    author = "Steward Protocol"

    def __init__(self, root_path: Path = Path(".")):
        """
        Initialize AUDITOR cartridge.

        Args:
            root_path: Root path of the repository
        """
        logger.info("🔍 AUDITOR v2.0: Cartridge initialization")

        # LAYER 1: Static compliance tool
        self.compliance = ComplianceTool(root_path=root_path)
        self.root_path = root_path
        
        # LAYER 2: The JUDGE (semantic verification)
        self.judge = get_judge()
        
        # LAYER 3: The WATCHDOG (runtime monitoring)
        self.watchdog_integration = WatchdogIntegration()

        logger.info("✅ AUDITOR v2.0: Ready for multi-layer verification")

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

        # Get watchdog status
        watchdog_status = self.watchdog_integration.get_status()

        return {
            "agent_id": "auditor",
            "name": self.name,
            "version": self.version,
            "status": "RUNNING",
            "domain": "SECURITY",
            "enforcement_mode": "fail_build_and_halt_on_critical",
            "compliance_metrics": {
                "root_path": str(self.root_path),
                "reports_generated": compliance_stats.get("reports_generated", 0),
                "reports_dir": compliance_stats.get("reports_dir", str(self.root_path / "data" / "reports")),
                "enforcement_enabled": True,
            },
            "verification_layers": {
                "layer_1_static_compliance": "enabled",
                "layer_2_semantic_judge": "enabled",
                "layer_3_watchdog_monitoring": "enabled"
            },
            "watchdog": watchdog_status
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

    # ========== LAYER 2: SEMANTIC VERIFICATION (THE JUDGE) ==========

    def run_semantic_verification(self) -> Dict[str, Any]:
        """
        Run semantic verification on the kernel ledger.
        
        This checks for LOGICAL violations, not just syntax errors.
        For example: "Is BROADCAST preceded by LICENSE_VALID?"
        
        Returns:
            dict: Semantic verification report
        """
        try:
            logger.info("⚖️  JUDGE: Running semantic verification")
            logger.info("=" * 70)
            
            # Read kernel ledger
            ledger_path = self.root_path / "data" / "ledger" / "kernel.jsonl"
            events = []
            
            if ledger_path.exists():
                import json
                with open(ledger_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            
            logger.info(f"⚖️  Loaded {len(events)} events from ledger")
            
            # Run the Judge
            report = self.judge.verify_ledger(events)
            
            # Save report
            report_path = self.root_path / "data" / "reports" / "semantic_verification.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(report_path, "w") as f:
                json.dump(report.to_dict(), f, indent=2)
            
            logger.info(f"✅ Semantic verification report saved: {report_path}")
            
            return {
                "status": "completed",
                "passed": report.passed,
                "violations": len(report.violations),
                "events_checked": report.checked_events,
                "report": report.to_dict()
            }
        
        except Exception as e:
            logger.error(f"⚖️  Semantic verification error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    # ========== LAYER 3: RUNTIME MONITORING (THE WATCHDOG) ==========

    def start_watchdog(self) -> Dict[str, Any]:
        """
        Start the Watchdog runtime verification daemon.
        
        This should be called early in kernel initialization.
        The watchdog then monitors the ledger continuously.
        
        Returns:
            dict: Watchdog initialization status
        """
        try:
            logger.info("👁️  WATCHDOG: Starting runtime verification daemon")
            
            # Configure watchdog for this system
            config = WatchdogConfig(
                ledger_path=self.root_path / "data" / "ledger" / "kernel.jsonl",
                violations_path=self.root_path / "data" / "ledger" / "violations.jsonl",
                halt_on_critical=True,
                notify_envoy=True
            )
            
            self.watchdog_integration.watchdog = Watchdog(config)
            
            logger.info("✅ WATCHDOG: Daemon started and ready for kernel attachment")
            
            return {
                "status": "started",
                "config": {
                    "check_interval": config.check_interval,
                    "halt_on_critical": config.halt_on_critical,
                    "notify_envoy": config.notify_envoy
                }
            }
        
        except Exception as e:
            logger.error(f"👁️  WATCHDOG startup error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def run_watchdog_check(self) -> Dict[str, Any]:
        """
        Run a single watchdog check cycle (for testing or manual invocation).
        
        Normally this would be called by the kernel on each tick.
        
        Returns:
            dict: Check results including any violations found
        """
        try:
            logger.info("👁️  WATCHDOG: Running verification check")
            result = self.watchdog_integration.watchdog.run_once()
            
            if result.get("status") == "error":
                logger.error(f"👁️  Check failed: {result.get('error')}")
            else:
                logger.info(f"👁️  Check complete: {len(result.get('violations', []))} violations")
            
            return result
        
        except Exception as e:
            logger.error(f"👁️  Watchdog check error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_watchdog_status(self) -> Dict[str, Any]:
        """Get current watchdog status"""
        return self.watchdog_integration.get_status()


# Export for VibeOS cartridge loading
__all__ = ["AuditorCartridge"]
