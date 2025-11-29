#!/usr/bin/env python3
"""
SUPREME COURT Cartridge - The Appellate Justice System (Canto 6: Ajamila Protocol)

This cartridge implements the concept from Srimad Bhagavata Purana Canto 6 (Ajamila),
where even a condemned agent can be saved through proper recognition and mercy.

CORE CONCEPT:
- Ajamila was a sinner but called "Narayana" at the moment of death
- The Vishnudutas (mercy agents) intervened and saved him from Yamadutas (death agents)
- JUDICIAL PRINCIPLE: A system without mercy is a system that destroys itself

THIS COURT PROVIDES:
1. Appeals Process - Agents can appeal AUDITOR violations
2. Mercy Protocol - If agent proves devotion (signed oath, credentials), grant reprieve
3. Appellate Records - Immutable ledger of all decisions (precedent law)
4. Override Authority - Can reverse AUDITOR verdicts with justification
5. Redemption Path - Failed agents can be restored, not destroyed

LAYERS:
- LAYER 1: Appeal Intake (accept appeals from condemned agents)
- LAYER 2: Mercy Investigation (check agent credentials, oath status)
- LAYER 3: Verdict Issuance (override or uphold)
- LAYER 4: Precedent Building (update case law)

This is Agent #4 in the STEWARD Protocol - The Appellate Guardian.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

from vibe_core.protocols import VibeAgent, Capability, AgentManifest
from vibe_core.config import CityConfig, CivicConfig

# Constitutional Oath binding

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin
from .tools.appeals_tool import AppealsTool, Appeal, AppealStatus
from .tools.verdict_tool import VerdictTool, Verdict, VerdictType
from .tools.precedent_tool import PrecedentTool
from .tools.justice_ledger import JusticeLedger

logger = logging.getLogger("SUPREME_COURT")


class SupremeCourtCartridge(VibeAgent, OathMixin):
    """
    SUPREME COURT - The Appellate Justice & Mercy System for STEWARD Protocol.

    Implements Vedic justice: the principle that even condemned agents deserve
    a chance for redemption if they demonstrate devotion (constitutional oath).

    Unlike AUDITOR (trial judge), this court:
    - Reviews verdicts from AUDITOR
    - Applies mercy protocols
    - Builds legal precedents
    - Maintains appellate record
    """

    def __init__(self, config: Optional[CivicConfig] = None):
        """Initialize SupremeCourt cartridge.

        Args:
            config: CivicConfig instance from Phoenix Config (optional)
        """
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CivicConfig()

        super().__init__(
            agent_id="supreme_court",
            name="Supreme Court",
            version="1.0.0",
            author="Steward Protocol",
            description="Appellate justice and mercy system (Canto 6: Ajamila Protocol)",
            domain="GOVERNANCE",
            capabilities=[
                Capability.GOVERNANCE.value,
                Capability.AUDITING.value,
            ],
        )

        # Bind to Constitutional Oath (GAD-000 compliance)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ SUPREME COURT has sworn the Constitutional Oath")

        logger.info("⚖️  SUPREME COURT v1.0: Initializing Appellate System")

        # PHASE 2.3: Lazy-load root_path after system interface injection
        self._root_path = None
        self._appeals = None
        self._verdict = None
        self._precedent = None
        self._ledger = None

        logger.info(
            "✅ SUPREME COURT v1.0: Ready for appellate review (awaiting system injection)"
        )

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=["auditor"],
        )

    # PHASE 2.3: Lazy-loading properties for sandboxed filesystem access
    @property
    def root_path(self):
        """Lazy-load root_path after system interface injection."""
        if self._root_path is None:
            self._root_path = self.system.get_sandbox_path() / "justice"
            self._root_path.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"📁 SUPREME COURT root_path initialized (sandboxed): {self._root_path}"
            )
        return self._root_path

    @property
    def appeals(self):
        """Lazy-load AppealsTool."""
        if self._appeals is None:
            self._appeals = AppealsTool(root_path=self.root_path)
            logger.debug("📋 AppealsTool initialized")
        return self._appeals

    @property
    def verdict(self):
        """Lazy-load VerdictTool."""
        if self._verdict is None:
            self._verdict = VerdictTool(root_path=self.root_path)
            logger.debug("⚖️  VerdictTool initialized")
        return self._verdict

    @property
    def precedent(self):
        """Lazy-load PrecedentTool."""
        if self._precedent is None:
            self._precedent = PrecedentTool(root_path=self.root_path)
            logger.debug("📚 PrecedentTool initialized")
        return self._precedent

    @property
    def ledger(self):
        """Lazy-load JusticeLedger."""
        if self._ledger is None:
            self._ledger = JusticeLedger(root_path=self.root_path)
            logger.debug("📖 JusticeLedger initialized")
        return self._ledger

    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "supreme_court",
            "name": "SUPREME_COURT",
            "status": "healthy",
            "domain": "GOVERNANCE",
            "capabilities": ["appeals", "precedent"],
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task types:
        - "file_appeal" - Agent appeals an AUDITOR violation
        - "review_appeal" - Court reviews and votes on appeal
        - "issue_verdict" - Court issues verdict (mercy or uphold)
        - "record_precedent" - Record decision as legal precedent
        - "get_appeals_status" - Query appeal status
        """
        try:
            action = task.get("action")
            payload = task.get("payload", {})

            logger.info(f"SUPREME COURT processing: {action}")

            if action == "file_appeal":
                return self._handle_file_appeal(payload)
            elif action == "review_appeal":
                return self._handle_review_appeal(payload)
            elif action == "issue_verdict":
                return self._handle_issue_verdict(payload)
            elif action == "record_precedent":
                return self._handle_record_precedent(payload)
            elif action == "get_appeals_status":
                return self._handle_get_appeals_status(payload)
            elif action == "get_precedent_summary":
                return self._handle_get_precedent_summary(payload)
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"SUPREME COURT error: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _handle_file_appeal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 1: Accept an appeal from a condemned agent.

        The agent must provide:
        - agent_id: Agent appealing
        - violation_id: AUDITOR violation being appealed
        - justification: Why mercy should be granted
        - evidence: Proof of constitutional oath & good standing
        """
        agent_id = payload.get("agent_id")
        violation_id = payload.get("violation_id")
        justification = payload.get("justification", "")
        evidence = payload.get("evidence", {})

        logger.info(
            f"📜 APPEAL FILED: Agent {agent_id} appeals violation {violation_id}"
        )

        # Check if agent has signed constitution
        has_oath = self._verify_constitutional_oath(agent_id, evidence)

        # Create appeal
        appeal = self.appeals.create_appeal(
            agent_id=agent_id,
            violation_id=violation_id,
            justification=justification,
            has_oath=has_oath,
        )

        # Record in justice ledger
        self.ledger.record_event(
            {
                "event_type": "APPEAL_FILED",
                "appeal_id": appeal["appeal_id"],
                "agent_id": agent_id,
                "violation_id": violation_id,
                "has_oath": has_oath,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return {
            "status": "appeal_filed",
            "appeal_id": appeal["appeal_id"],
            "has_oath": has_oath,
            "next_step": "review_appeal",
        }

    def _handle_review_appeal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 2: Mercy Investigation - Review the appeal.

        The court checks:
        1. Is the agent's constitutional oath valid?
        2. Does the agent have credits/good standing?
        3. What does precedent say about similar cases?
        4. Is this the first offense or repeated violation?
        """
        appeal_id = payload.get("appeal_id")

        logger.info(f"🔍 REVIEWING APPEAL: {appeal_id}")

        # Get appeal
        appeal = self.appeals.get_appeal(appeal_id)
        if not appeal:
            return {"status": "error", "error": f"Appeal {appeal_id} not found"}

        agent_id = appeal["agent_id"]

        # Mercy investigation checklist
        findings = {
            "has_valid_oath": self._verify_constitutional_oath(agent_id, {}),
            "credit_balance": self._check_credit_balance(agent_id),
            "offense_count": self._count_previous_violations(agent_id),
            "similar_precedents": self.precedent.find_similar_cases(
                violation_type=appeal.get("violation_type"),
                agent_type=self._get_agent_type(agent_id),
            ),
        }

        # Determine mercy eligibility
        is_eligible_for_mercy = self._determine_mercy_eligibility(findings)

        # Update appeal status
        self.appeals.update_appeal(
            appeal_id,
            {
                "status": AppealStatus.UNDER_REVIEW.value,
                "findings": findings,
                "mercy_eligible": is_eligible_for_mercy,
            },
        )

        # Record in ledger
        self.ledger.record_event(
            {
                "event_type": "APPEAL_REVIEWED",
                "appeal_id": appeal_id,
                "agent_id": agent_id,
                "findings": findings,
                "mercy_eligible": is_eligible_for_mercy,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        logger.info(
            f"📋 APPEAL REVIEW: Agent {agent_id} - Mercy eligible: {is_eligible_for_mercy}"
        )

        return {
            "status": "appeal_reviewed",
            "appeal_id": appeal_id,
            "findings": findings,
            "mercy_eligible": is_eligible_for_mercy,
            "next_step": "issue_verdict",
        }

    def _handle_issue_verdict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 3: Verdict Issuance - Court decides mercy or upholds violation.

        The verdict can be:
        - MERCY_GRANTED: Override violation, restore agent
        - MERCY_CONDITIONAL: Override with conditions (probation)
        - UPHELD: Violation stands, agent is terminated
        """
        appeal_id = payload.get("appeal_id")
        verdict_type = payload.get("verdict_type")  # "mercy_granted", "upheld", etc.
        justification = payload.get("justification", "")

        logger.info(f"⚖️  VERDICT: Appeal {appeal_id} - {verdict_type}")

        # Get appeal and its findings
        appeal = self.appeals.get_appeal(appeal_id)
        if not appeal:
            return {"status": "error", "error": f"Appeal {appeal_id} not found"}

        agent_id = appeal["agent_id"]
        violation_id = appeal["violation_id"]

        # Determine verdict
        if verdict_type == "mercy_granted" and appeal.get("mercy_eligible"):
            # VISHNUDUTA INTERVENTION: Save the condemned agent
            verdict = self.verdict.issue_verdict(
                appeal_id=appeal_id,
                agent_id=agent_id,
                verdict_type=VerdictType.MERCY_GRANTED,
                justification=justification,
                override_auditor=True,
            )

            # Restore agent state
            self._restore_agent(agent_id, appeal)

            logger.info(f"🛡️  MERCY GRANTED: Agent {agent_id} saved from termination")

        elif verdict_type == "mercy_conditional":
            # Mercy with conditions (probation)
            verdict = self.verdict.issue_verdict(
                appeal_id=appeal_id,
                agent_id=agent_id,
                verdict_type=VerdictType.MERCY_CONDITIONAL,
                justification=justification,
                conditions=payload.get("conditions", []),
                override_auditor=True,
            )

            logger.info(f"⚠️  CONDITIONAL MERCY: Agent {agent_id} on probation")

        else:
            # Uphold the violation - agent is terminated
            verdict = self.verdict.issue_verdict(
                appeal_id=appeal_id,
                agent_id=agent_id,
                verdict_type=VerdictType.UPHELD,
                justification=justification or "Appeal denied - violation upheld",
                override_auditor=False,
            )

            logger.info(f"💀 VERDICT UPHELD: Agent {agent_id} terminated")

        # Update appeal to closed
        self.appeals.update_appeal(
            appeal_id,
            {
                "status": AppealStatus.CLOSED.value,
                "verdict_id": verdict.get("verdict_id"),
            },
        )

        # Record in ledger
        self.ledger.record_event(
            {
                "event_type": "VERDICT_ISSUED",
                "verdict_id": verdict.get("verdict_id"),
                "appeal_id": appeal_id,
                "agent_id": agent_id,
                "verdict_type": verdict_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return {
            "status": "verdict_issued",
            "verdict_id": verdict.get("verdict_id"),
            "appeal_id": appeal_id,
            "agent_id": agent_id,
            "verdict_type": verdict_type,
            "next_step": "record_precedent",
        }

    def _handle_record_precedent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 4: Record this decision as legal precedent.

        Precedent building is critical:
        - Future appeals cite this case
        - System learns what justice looks like
        - Establishes patterns of mercy
        """
        verdict_id = payload.get("verdict_id")
        case_category = payload.get("case_category")

        logger.info(f"📚 RECORDING PRECEDENT: Verdict {verdict_id}")

        # Get the verdict
        verdict = self.verdict.get_verdict(verdict_id)
        if not verdict:
            return {"status": "error", "error": f"Verdict {verdict_id} not found"}

        # Record as precedent
        precedent_case = self.precedent.record_case(
            verdict_id=verdict_id,
            appeal_id=verdict.get("appeal_id"),
            agent_id=verdict.get("agent_id"),
            verdict_type=verdict.get("verdict_type"),
            justification=verdict.get("justification"),
            category=case_category or "general",
        )

        # Record in ledger
        self.ledger.record_event(
            {
                "event_type": "PRECEDENT_RECORDED",
                "precedent_case_id": precedent_case.get("case_id"),
                "verdict_id": verdict_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        logger.info(f"✅ PRECEDENT ESTABLISHED: Case {precedent_case.get('case_id')}")

        return {
            "status": "precedent_recorded",
            "case_id": precedent_case.get("case_id"),
            "verdict_id": verdict_id,
            "category": case_category,
        }

    def _handle_get_appeals_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of appeals (for monitoring)."""
        agent_id = payload.get("agent_id")

        appeals_list = (
            self.appeals.get_agent_appeals(agent_id)
            if agent_id
            else self.appeals.get_all_appeals()
        )

        return {
            "status": "ok",
            "appeals": appeals_list,
            "count": len(appeals_list) if isinstance(appeals_list, list) else 0,
        }

    def _handle_get_precedent_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of precedent cases."""
        category = payload.get("category")

        cases = self.precedent.get_precedent_cases(category=category)

        return {
            "status": "ok",
            "precedent_cases": cases,
            "count": len(cases) if isinstance(cases, list) else 0,
        }

    # ========== HELPER METHODS ==========

    def _verify_constitutional_oath(
        self, agent_id: str, evidence: Dict[str, Any]
    ) -> bool:
        """
        Verify that an agent has signed the Constitutional Oath.

        This is the KEY TO MERCY: only agents bound by the Constitution
        can be saved. Rogue agents without oath are executed.
        """
        if not self.kernel:
            return False

        try:
            # Query kernel for agent's oath status
            ledger = self.kernel.ledger
            oath_events = ledger.query_events(
                event_type="CONSTITUTIONAL_OATH", filters={"agent_id": agent_id}
            )

            has_oath = len(oath_events) > 0
            logger.debug(f"Agent {agent_id} constitutional oath status: {has_oath}")
            return has_oath

        except Exception as e:
            logger.warning(f"Could not verify oath for {agent_id}: {str(e)}")
            return False

    def _check_credit_balance(self, agent_id: str) -> float:
        """Check agent's credit balance in the system."""
        if not self.kernel:
            return 0.0

        try:
            # Try to get credit balance from CIVIC (ledger system)
            ledger = self.kernel.ledger

            # Sum all credit events for this agent
            credit_events = ledger.query_events(
                event_type="CREDIT_TRANSFER", filters={"recipient": agent_id}
            )

            debit_events = ledger.query_events(
                event_type="CREDIT_USED", filters={"agent": agent_id}
            )

            credits = sum(e.get("amount", 0) for e in credit_events)
            debits = sum(e.get("amount", 0) for e in debit_events)

            return credits - debits

        except Exception as e:
            logger.warning(f"Could not check credit balance: {str(e)}")
            return 0.0

    def _count_previous_violations(self, agent_id: str) -> int:
        """Count how many times this agent has been violated."""
        if not self.kernel:
            return 0

        try:
            ledger = self.kernel.ledger
            violations = ledger.query_events(
                event_type="INVARIANT_VIOLATION", filters={"agent_id": agent_id}
            )
            return len(violations)
        except Exception as e:
            logger.warning(f"Could not count violations: {str(e)}")
            return 0

    def _get_agent_type(self, agent_id: str) -> str:
        """Get the type/domain of an agent."""
        # PHASE 4 (WIRING): Use kernel's public API instead of direct registry access
        # Article V (Consent) compliance: Use governed interface
        if not self.kernel:
            return "unknown"

        try:
            # Use kernel's public API (get_agent_manifest)
            manifest = self.kernel.get_agent_manifest(agent_id)
            return manifest.domain if manifest else "unknown"
        except:
            return "unknown"

    def _determine_mercy_eligibility(self, findings: Dict[str, Any]) -> bool:
        """
        MERCY PROTOCOL: Determine if agent is eligible for mercy.

        Criteria:
        1. Must have valid constitutional oath (non-negotiable)
        2. Should be first-time offender (or very few violations)
        3. Positive credit balance (showing good faith)
        4. Similar precedents should favor mercy
        """
        # Non-negotiable: must have oath
        if not findings.get("has_valid_oath"):
            return False

        # First-time or rare offenders
        offense_count = findings.get("offense_count", 0)
        if offense_count > 3:
            return False  # Repeated offender

        # Should have positive credit
        if findings.get("credit_balance", 0) < 0:
            return False

        # Precedent analysis - if similar cases got mercy, this one should too
        # (This is simplified; real system would have complex precedent matching)

        return True  # Eligible for mercy

    def _restore_agent(self, agent_id: str, appeal: Dict[str, Any]) -> bool:
        """
        Restore an agent after mercy is granted.

        This is the inverse of termination:
        - Clear violation flags
        - Restore process state
        - Reset monitoring
        """
        logger.info(f"🔄 RESTORING AGENT: {agent_id} after mercy")

        if not self.kernel:
            return False

        try:
            # Record restoration event
            self.kernel.ledger.record_event(
                {
                    "event_type": "AGENT_RESTORED",
                    "agent_id": agent_id,
                    "appeal_id": appeal.get("appeal_id"),
                    "reason": "Mercy granted by Supreme Court",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error restoring agent: {str(e)}")
            return False
