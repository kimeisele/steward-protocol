#!/usr/bin/env python3
"""
Constitutional Verdict Tool - Layer 3 Defense in Depth (Phase 3.4)
====================================================================

This is the AUDITOR's supreme authority - constitutional judgment on code quality.

Part of Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: Watchman (AST analysis) - catches architectural violations
- Layer 3: THIS TOOL - constitutional judgment and final verdict

The Auditor provides the final authority on whether code:
1. Adheres to THE AGENT CONSTITUTION (CONSTITUTION.md)
2. Respects the 6 Articles (Identity, Accountability, Governance, Transparency, Consent, Interoperability)
3. Follows the 4 Regulating Principles (Purity, Truth, Austerity, Authorized Connections)
4. Upholds GAD-000 governance standards

This is not technical analysis (that's Watchman's job).
This is CONSTITUTIONAL JUDGMENT - the final word on code quality.

"The Constitution is not optional. It is the supreme law."
"""

import ast
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AUDITOR.CONSTITUTIONAL_VERDICT")


class ConstitutionalArticle(Enum):
    """The 6 Articles of THE AGENT CONSTITUTION."""

    ARTICLE_I_IDENTITY = "Article I: Identity (Cryptographic Proof)"
    ARTICLE_II_ACCOUNTABILITY = "Article II: Rechenschaft (Auditability)"
    ARTICLE_III_GOVERNANCE = "Article III: Governance (Boundaries)"
    ARTICLE_IV_TRANSPARENCY = "Article IV: Transparenz (Observability)"
    ARTICLE_V_CONSENT = "Article V: Zustimmung (Consent)"
    ARTICLE_VI_INTEROPERABILITY = "Article VI: Interoperabilität (Standardization)"


class RegulatingPrinciple(Enum):
    """The 4 Regulating Principles (Moral Firewall)."""

    PRINCIPLE_1_PURITY = "Principle 1: No Corrupt Data Ingestion (Mercy/Daya)"
    PRINCIPLE_2_TRUTH = "Principle 2: No Hallucination (Truthfulness/Satyam)"
    PRINCIPLE_3_AUSTERITY = "Principle 3: No Resource Leaks (Austerity/Tapas)"
    PRINCIPLE_4_AUTHORIZED_ONLY = (
        "Principle 4: No Unauthorized Connections (Cleanliness/Saucam)"
    )


class VerdictSeverity(Enum):
    """Severity of constitutional violations."""

    CONSTITUTIONAL = "CONSTITUTIONAL"  # Violates supreme law - must fail
    GOVERNANCE = "GOVERNANCE"  # Violates governance principles - should fail
    WARNING = "WARNING"  # Does not align with best practices


@dataclass
class ConstitutionalViolation:
    """Represents a violation of THE AGENT CONSTITUTION."""

    agent_id: str
    article: ConstitutionalArticle | RegulatingPrinciple
    severity: VerdictSeverity
    message: str
    file_path: str
    line_number: Optional[int] = None
    remedy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "article": self.article.value,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "remedy": self.remedy,
        }


class ConstitutionalVerdictTool:
    """
    Constitutional Verdict Tool - The Final Authority (Layer 3).

    This tool performs constitutional judgment on the codebase,
    verifying adherence to THE AGENT CONSTITUTION.

    This is NOT technical analysis (Watchman does that).
    This is CONSTITUTIONAL JUDGMENT - ensuring agents uphold the supreme law.
    """

    def __init__(self):
        self.violations: List[ConstitutionalViolation] = []

    def render_verdict(self, system_agents_path: Path) -> Dict[str, Any]:
        """
        Render constitutional verdict on all agents.

        Args:
            system_agents_path: Path to steward/system_agents

        Returns:
            Verdict dict with constitutional judgment
        """
        logger.info("\n" + "=" * 70)
        logger.info("⚖️  AUDITOR CONSTITUTIONAL VERDICT (Layer 3 - Supreme Authority)")
        logger.info("=" * 70)

        self.violations = []

        # Find all agent directories
        agent_dirs = [
            d
            for d in system_agents_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        for agent_dir in agent_dirs:
            logger.info(f"⚖️  Judging {agent_dir.name}...")
            self._judge_agent(agent_dir)

        # Generate verdict report
        verdict = self._generate_verdict_report()

        # Log verdict summary
        self._log_verdict_summary(verdict)

        return verdict

    def _judge_agent(self, agent_path: Path) -> None:
        """
        Judge a single agent for constitutional compliance.

        Args:
            agent_path: Path to agent directory
        """
        agent_id = agent_path.name

        # Article I: Identity (Cryptographic Proof)
        self._check_article_i_identity(agent_path, agent_id)

        # Article II: Accountability (Auditability)
        self._check_article_ii_accountability(agent_path, agent_id)

        # Article III: Governance (Boundaries)
        self._check_article_iii_governance(agent_path, agent_id)

        # Article IV: Transparency (Observability)
        self._check_article_iv_transparency(agent_path, agent_id)

        # Article V: Consent (No unauthorized access)
        self._check_article_v_consent(agent_path, agent_id)

        # Article VI: Interoperability (Standardization)
        self._check_article_vi_interoperability(agent_path, agent_id)

        # Principle 4: No Unauthorized Connections (most critical for code)
        self._check_principle_4_authorized_connections(agent_path, agent_id)

    def _check_article_i_identity(self, agent_path: Path, agent_id: str) -> None:
        """
        Article I: Identity (Cryptographic Proof)

        "Kein Agent darf ohne beweisbare Identität agieren."
        Every agent must have cryptographic keys and sign all actions.
        """
        # Check for steward.json (agent manifest)
        manifest_path = agent_path / "steward.json"
        if not manifest_path.exists():
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_I_IDENTITY,
                    severity=VerdictSeverity.CONSTITUTIONAL,
                    message="Agent lacks identity manifest (steward.json)",
                    file_path=str(manifest_path),
                    remedy="Create steward.json with agent ID, version, and public key",
                )
            )

        # Check for STEWARD.md (identity documentation)
        steward_md = agent_path / "STEWARD.md"
        if not steward_md.exists():
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_I_IDENTITY,
                    severity=VerdictSeverity.CONSTITUTIONAL,
                    message="Agent lacks identity documentation (STEWARD.md)",
                    file_path=str(steward_md),
                    remedy="Create STEWARD.md with agent identity and capabilities",
                )
            )

    def _check_article_ii_accountability(self, agent_path: Path, agent_id: str) -> None:
        """
        Article II: Rechenschaft (Auditability)

        "Keine Macht ohne Nachvollziehbarkeit."
        Every decision must be logged in immutable audit trail.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # Check if agent uses ledger/logging for accountability
        content = cartridge_file.read_text()
        has_logging = "logging" in content or "logger" in content
        has_audit = "ledger" in content or "audit" in content or "event" in content

        if not (has_logging or has_audit):
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_II_ACCOUNTABILITY,
                    severity=VerdictSeverity.GOVERNANCE,
                    message="Agent lacks audit trail (no logging or ledger usage)",
                    file_path=str(cartridge_file),
                    remedy="Add logging or ledger integration to track decisions",
                )
            )

    def _check_article_iii_governance(self, agent_path: Path, agent_id: str) -> None:
        """
        Article III: Governance (Boundaries)

        "Code ist Gesetz, nicht Richtlinie."
        Constraints must be enforced architecturally, not through prompts.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # Check if agent uses system interface for governance
        content = cartridge_file.read_text()
        has_system_interface = (
            "AgentSystemInterface" in content or "self.system" in content
        )

        if not has_system_interface:
            # Only warn - some agents might not need system interface
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_III_GOVERNANCE,
                    severity=VerdictSeverity.WARNING,
                    message="Agent may lack architectural governance (no system interface)",
                    file_path=str(cartridge_file),
                    remedy="Use AgentSystemInterface for governed operations",
                )
            )

    def _check_article_iv_transparency(self, agent_path: Path, agent_id: str) -> None:
        """
        Article IV: Transparenz (Observability)

        "Keine Black Boxes im Verhalten."
        Internal state, tools, and errors must be machine-readable.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # Check for report_status() or get_manifest() methods
        content = cartridge_file.read_text()
        has_status_reporting = "report_status" in content or "get_manifest" in content

        if not has_status_reporting:
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_IV_TRANSPARENCY,
                    severity=VerdictSeverity.GOVERNANCE,
                    message="Agent lacks observability (no status reporting)",
                    file_path=str(cartridge_file),
                    remedy="Implement report_status() or get_manifest() method",
                )
            )

    def _check_article_v_consent(self, agent_path: Path, agent_id: str) -> None:
        """
        Article V: Zustimmung (Consent)

        "Die Souveränität des Nutzers und anderer Agenten ist unantastbar."
        No unauthorized access to resources or data.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # Check for unauthorized file access patterns
        try:
            content = cartridge_file.read_text()
            tree = ast.parse(content)

            # Look for direct file operations without proper authorization
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for open() calls without context manager
                    if isinstance(node.func, ast.Name) and node.func.id == "open":
                        # This is a heuristic - we warn but don't fail
                        self.violations.append(
                            ConstitutionalViolation(
                                agent_id=agent_id,
                                article=ConstitutionalArticle.ARTICLE_V_CONSENT,
                                severity=VerdictSeverity.WARNING,
                                message="Agent may perform unauthorized file access",
                                file_path=str(cartridge_file),
                                line_number=node.lineno,
                                remedy="Use system.get_sandbox_path() for governed file access",
                            )
                        )
                        break  # Only report once

        except SyntaxError:
            pass  # Skip files with syntax errors (Watchman will catch)

    def _check_article_vi_interoperability(
        self, agent_path: Path, agent_id: str
    ) -> None:
        """
        Article VI: Interoperabilität (Standardization)

        "Isolation ist Stagnation."
        Agents must use standardized protocols.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # Check if agent implements VibeAgent protocol
        content = cartridge_file.read_text()
        implements_protocol = "VibeAgent" in content or "process(" in content

        if not implements_protocol:
            self.violations.append(
                ConstitutionalViolation(
                    agent_id=agent_id,
                    article=ConstitutionalArticle.ARTICLE_VI_INTEROPERABILITY,
                    severity=VerdictSeverity.GOVERNANCE,
                    message="Agent may not implement standard protocol (VibeAgent)",
                    file_path=str(cartridge_file),
                    remedy="Implement VibeAgent protocol with process() method",
                )
            )

    def _check_principle_4_authorized_connections(
        self, agent_path: Path, agent_id: str
    ) -> None:
        """
        Principle 4: No Unauthorized Connections (Cleanliness/Saucam)

        "Keine Promiscuous Mode Network Interfaces."
        Only signed, authorized connections are allowed.
        """
        cartridge_file = agent_path / "cartridge_main.py"
        if not cartridge_file.exists():
            return

        # This check is mostly done by Watchman, but we provide constitutional context
        content = cartridge_file.read_text()

        # Check for network operations
        network_keywords = ["socket", "requests.", "urllib", "http.client"]
        has_network = any(keyword in content for keyword in network_keywords)

        if has_network:
            # Check if there's GAD-1000 verification
            has_verification = (
                "gad_1000" in content.lower()
                or "verify" in content
                or "signature" in content
            )

            if not has_verification:
                self.violations.append(
                    ConstitutionalViolation(
                        agent_id=agent_id,
                        article=RegulatingPrinciple.PRINCIPLE_4_AUTHORIZED_ONLY,
                        severity=VerdictSeverity.CONSTITUTIONAL,
                        message="Network operations without GAD-1000 identity verification",
                        file_path=str(cartridge_file),
                        remedy="Implement GAD-1000 identity verification before network operations",
                    )
                )

    def _generate_verdict_report(self) -> Dict[str, Any]:
        """
        Generate constitutional verdict report.

        Returns:
            Verdict dict with judgment and violations
        """
        # Group by severity
        constitutional = [
            v for v in self.violations if v.severity == VerdictSeverity.CONSTITUTIONAL
        ]
        governance = [
            v for v in self.violations if v.severity == VerdictSeverity.GOVERNANCE
        ]
        warnings = [v for v in self.violations if v.severity == VerdictSeverity.WARNING]

        # Determine overall verdict
        if constitutional:
            verdict_status = "UNCONSTITUTIONAL"
            should_fail = True
        elif governance:
            verdict_status = "GOVERNANCE_VIOLATIONS"
            should_fail = True
        elif warnings:
            verdict_status = "WARNINGS"
            should_fail = False
        else:
            verdict_status = "CONSTITUTIONAL"
            should_fail = False

        return {
            "verdict": verdict_status,
            "should_fail_build": should_fail,
            "total_violations": len(self.violations),
            "by_severity": {
                "CONSTITUTIONAL": len(constitutional),
                "GOVERNANCE": len(governance),
                "WARNING": len(warnings),
            },
            "by_article": self._group_by_article(),
            "violations": [v.to_dict() for v in self.violations],
            "constitutional_hash": self._get_constitution_hash(),
        }

    def _group_by_article(self) -> Dict[str, int]:
        """Group violations by article."""
        by_article = {}
        for v in self.violations:
            article_name = v.article.value
            if article_name not in by_article:
                by_article[article_name] = 0
            by_article[article_name] += 1
        return by_article

    def _get_constitution_hash(self) -> str:
        """Get SHA-256 hash of CONSTITUTION.md."""
        constitution_path = Path("CONSTITUTION.md")
        if constitution_path.exists():
            content = constitution_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        return "CONSTITUTION_NOT_FOUND"

    def _log_verdict_summary(self, verdict: Dict[str, Any]) -> None:
        """Log verdict summary to console."""
        logger.info("\n" + "=" * 70)
        logger.info("⚖️  CONSTITUTIONAL VERDICT SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Verdict: {verdict['verdict']}")
        logger.info(f"Total Violations: {verdict['total_violations']}")
        logger.info("\nBy Severity:")
        for severity, count in verdict["by_severity"].items():
            if count > 0:
                logger.info(f"  • {severity}: {count}")

        if verdict["by_article"]:
            logger.info("\nBy Article:")
            for article, count in verdict["by_article"].items():
                logger.info(f"  • {article}: {count}")

        logger.info(f"\nConstitution Hash: {verdict['constitutional_hash']}")

        if verdict["should_fail_build"]:
            logger.error(
                "\n❌ VERDICT: BUILD MUST FAIL - Constitutional violations detected"
            )
            logger.error(
                "The Constitution is the supreme law. These violations cannot be ignored."
            )
        elif verdict["total_violations"] > 0:
            logger.warning("\n⚠️  VERDICT: WARNINGS DETECTED - Review recommended")
            logger.warning(
                "Consider addressing these to improve constitutional alignment"
            )
        else:
            logger.info(
                "\n✅ VERDICT: CONSTITUTIONAL - All agents uphold the supreme law"
            )

        logger.info("=" * 70 + "\n")
