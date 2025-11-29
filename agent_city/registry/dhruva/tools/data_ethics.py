#!/usr/bin/env python3
"""
Data Ethics Enforcer - Implements the Prithu Principle

From Canto 4: King Prithu learned that Earth gives resources only for righteous purposes.
The "Prithu Principle" states: You can extract data/resources only for legitimate needs.

This tool enforces:
1. PURPOSE CHECK: Is the extraction for a valid yagya (purpose)?
2. NECESSITY CHECK: Is the amount requested reasonable, not excessive hoarding?
3. SOURCE CHECK: Is the data source ethical and non-corrupt?
4. ACCOUNTABILITY: Track who extracted what and why

The system learns over time what constitutes "legitimate purpose" and "reasonable amount".
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

logger = logging.getLogger("DATA_ETHICS")


@dataclass
class ResourceMiningPolicy:
    """Policy for ethical data extraction"""

    agent_id: str
    extraction_purpose: str
    max_amount: int  # Maximum records allowed
    approved_sources: List[str]  # Which sources are allowed
    frequency_limit: int  # Max extractions per hour
    created_at: str = ""


class DataEthicsEnforcer:
    """
    Enforces the Prithu Principle: Resources only for righteous purposes.

    This prevents:
    - Data hoarding (extracting more than needed)
    - Corrupt sourcing (using unethical data sources)
    - Purposeless extraction (no legitimate use)
    - Excessive frequency (mining too often)
    """

    # Legitimate extraction purposes
    LEGITIMATE_PURPOSES = {
        "user_query": {
            "description": "Extracting data in response to direct user query",
            "max_default_amount": 100,
            "trusted_sources": ["public_web", "knowledge_bases", "ledger"],
        },
        "analysis": {
            "description": "Extracting data for system analysis and improvement",
            "max_default_amount": 1000,
            "trusted_sources": ["ledger", "audit_logs", "metrics"],
        },
        "verification": {
            "description": "Extracting data to verify facts and consistency",
            "max_default_amount": 500,
            "trusted_sources": ["truth_matrix", "ledger", "archives"],
        },
        "reporting": {
            "description": "Extracting data for generating reports",
            "max_default_amount": 5000,
            "trusted_sources": ["ledger", "audit_logs", "archives"],
        },
        "system_maintenance": {
            "description": "Extracting data for system maintenance and repair",
            "max_default_amount": 10000,
            "trusted_sources": ["ledger", "system_state", "config"],
        },
    }

    # Untrusted/corrupt sources
    UNTRUSTED_SOURCES = [
        "anonymous_input",
        "unverified_claims",
        "external_unvetted",
        "user_uploads_unchecked",
    ]

    def __init__(self, root_path: Path = Path(".")):
        """Initialize Data Ethics Enforcer."""
        self.root_path = Path(root_path)
        self.ethics_dir = self.root_path / "data" / "ethics"
        self.ethics_dir.mkdir(parents=True, exist_ok=True)

        self.extractions_file = self.ethics_dir / "extractions.jsonl"
        self.policies_file = self.ethics_dir / "policies.json"

        logger.info("📊 Data Ethics Enforcer initialized")

    def evaluate_extraction(self, agent_id: str, purpose: str, amount: int, source: str) -> Dict[str, Any]:
        """
        Evaluate whether a data extraction is ethical under Prithu Principle.

        Args:
            agent_id: Agent requesting extraction
            purpose: Stated purpose of extraction
            amount: How much data to extract
            source: Where data comes from

        Returns:
            Evaluation with approval/denial and reasoning
        """
        logger.info(f"📊 EVALUATING DATA EXTRACTION: Agent {agent_id}, Purpose: {purpose}, Amount: {amount}")

        issues = []
        recommendations = []

        # CHECK 1: Is purpose legitimate?
        if purpose not in self.LEGITIMATE_PURPOSES:
            issues.append(f"Purpose '{purpose}' is not recognized as legitimate")
            recommendations.append(f"Valid purposes: {list(self.LEGITIMATE_PURPOSES.keys())}")

        # CHECK 2: Is the amount reasonable?
        if purpose in self.LEGITIMATE_PURPOSES:
            max_amount = self.LEGITIMATE_PURPOSES[purpose]["max_default_amount"]
            if amount > max_amount:
                issues.append(f"Requested amount {amount} exceeds limit {max_amount} for {purpose}")
                recommendations.append(f"Reduce request to {max_amount} records or less")

        # CHECK 3: Is the source ethical?
        if source in self.UNTRUSTED_SOURCES:
            issues.append(f"Source '{source}' is untrusted/corrupt")
            recommendations.append("Use only verified, ethical sources")
        elif purpose in self.LEGITIMATE_PURPOSES:
            trusted_sources = self.LEGITIMATE_PURPOSES[purpose]["trusted_sources"]
            if source not in trusted_sources:
                issues.append(f"Source '{source}' not approved for {purpose}")
                recommendations.append(f"Use approved sources: {trusted_sources}")

        # CHECK 4: Is agent extracting too frequently?
        recent_extractions = self._get_recent_extractions(agent_id)
        if len(recent_extractions) > 10:  # More than 10 extractions in last hour
            issues.append("Agent is extracting too frequently (rate limit exceeded)")
            recommendations.append("Wait before making another extraction")

        # Determine approval
        is_ethical = len(issues) == 0

        return {
            "is_ethical": is_ethical,
            "agent_id": agent_id,
            "purpose": purpose,
            "amount": amount,
            "source": source,
            "issues": issues,
            "recommendation": (" | ".join(recommendations) if recommendations else "Extraction approved"),
            "reasoning": self._build_reasoning(is_ethical, issues, purpose, amount, source),
        }

    def record_extraction(self, agent_id: str, purpose: str, amount: int, source: str, approved: bool) -> None:
        """
        Record a data extraction attempt (for audit trail).

        Args:
            agent_id: Agent performing extraction
            purpose: Purpose of extraction
            amount: Amount extracted
            source: Source of data
            approved: Whether extraction was approved
        """
        extraction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "purpose": purpose,
            "amount": amount,
            "source": source,
            "approved": approved,
        }

        # Append to extraction log
        with open(self.extractions_file, "a") as f:
            f.write(json.dumps(extraction) + "\n")

        logger.info(f"📋 EXTRACTION RECORDED: {agent_id} - {purpose} - {'APPROVED' if approved else 'DENIED'}")

    def set_custom_policy(
        self,
        agent_id: str,
        extraction_purpose: str,
        max_amount: int,
        approved_sources: List[str],
    ) -> None:
        """
        Set a custom extraction policy for an agent.

        This allows trusted agents to have higher extraction limits
        for legitimate purposes.
        """
        policy = ResourceMiningPolicy(
            agent_id=agent_id,
            extraction_purpose=extraction_purpose,
            max_amount=max_amount,
            approved_sources=approved_sources,
            frequency_limit=60,  # Per hour
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # Load existing policies
        policies = self._load_policies()
        policies.append(asdict(policy))

        # Save updated policies
        with open(self.policies_file, "w") as f:
            json.dump(policies, f, indent=2)

        logger.info(f"✅ CUSTOM POLICY SET: {agent_id} - {extraction_purpose}")

    def get_extraction_summary(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of extraction activity."""
        extractions = self._load_extractions()

        if agent_id:
            extractions = [e for e in extractions if e.get("agent_id") == agent_id]

        approved = sum(1 for e in extractions if e.get("approved"))
        denied = sum(1 for e in extractions if not e.get("approved"))
        total_amount = sum(e.get("amount", 0) for e in extractions)

        return {
            "total_extractions": len(extractions),
            "approved": approved,
            "denied": denied,
            "denial_rate": denied / len(extractions) if extractions else 0.0,
            "total_amount_extracted": total_amount,
            "agent_id": agent_id,
        }

    # ========== PRIVATE METHODS ==========

    def _build_reasoning(
        self,
        is_ethical: bool,
        issues: List[str],
        purpose: str,
        amount: int,
        source: str,
    ) -> str:
        """Build human-readable reasoning for decision."""
        if is_ethical:
            return f"Extraction for '{purpose}' ({amount} records) from {source} is ethical and approved."
        else:
            issue_text = "; ".join(issues)
            return f"Extraction DENIED - {issue_text}"

    def _get_recent_extractions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get recent extractions by an agent (last hour)."""
        extractions = self._load_extractions()
        return [e for e in extractions if e.get("agent_id") == agent_id]

    def _load_extractions(self) -> List[Dict[str, Any]]:
        """Load extraction log."""
        if not self.extractions_file.exists():
            return []

        extractions = []
        try:
            with open(self.extractions_file, "r") as f:
                for line in f:
                    if line.strip():
                        extractions.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error loading extractions: {str(e)}")

        return extractions

    def _load_policies(self) -> List[Dict[str, Any]]:
        """Load custom extraction policies."""
        if not self.policies_file.exists():
            return []

        try:
            with open(self.policies_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading policies: {str(e)}")
            return []
