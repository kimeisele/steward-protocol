#!/usr/bin/env python3
"""
Reference Resolver - Resolves Conflicting Claims using Dhruva Authority

When two agents make contradictory claims, who is right?
The Dhruva system uses a hierarchy of authority to determine truth:

1. Constitutional facts (absolute - cannot be contradicted)
2. Ledger facts (immutable - highest empirical truth)
3. Auditor facts (verified - high trust)
4. Oracle facts (self-verified - medium trust)
5. Herald facts (published - medium trust)
6. Science facts (researched - medium trust)
7. Witness facts (reported - lowest trust)

This system ensures consistent truth resolution across the entire OS.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from .tools.truth_matrix import TruthMatrix, FactAuthority

logger = logging.getLogger("REFERENCE_RESOLVER")


class ReferenceResolver:
    """
    Resolves conflicting claims using the Dhruva hierarchy of authorities.

    The resolver acts as an arbiter when two sources disagree.
    Higher authority always wins (unless constitutional precedent applies).
    """

    # Authority hierarchy (higher number = higher authority)
    AUTHORITY_HIERARCHY = {
        FactAuthority.CONSTITUTIONAL.value: 7,
        FactAuthority.LEDGER.value: 6,
        FactAuthority.AUDITOR.value: 5,
        FactAuthority.ORACLE.value: 4,
        FactAuthority.HERALD.value: 3,
        FactAuthority.SCIENCE.value: 2,
        FactAuthority.WITNESS.value: 1,
    }

    def __init__(self, root_path: Path = Path("."), truth_matrix: Optional[TruthMatrix] = None):
        """Initialize Reference Resolver."""
        self.root_path = Path(root_path)
        self.truth_matrix = truth_matrix or TruthMatrix(root_path)

        logger.info("⚖️  Reference Resolver initialized")

    def resolve_conflict(self, claim_a: str, authority_a: str, claim_b: str, authority_b: str) -> Dict[str, Any]:
        """
        Resolve a conflict between two claims.

        Args:
            claim_a: First claim statement
            authority_a: Authority source of claim A
            claim_b: Second claim statement
            authority_b: Authority source of claim B

        Returns:
            Resolution with authoritative claim and reasoning
        """
        logger.info(f"⚖️  RESOLVING: '{claim_a}' vs '{claim_b}'")

        # Get authority levels
        level_a = self.AUTHORITY_HIERARCHY.get(authority_a, 0)
        level_b = self.AUTHORITY_HIERARCHY.get(authority_b, 0)

        # Determine winner by authority
        if level_a > level_b:
            authoritative_claim = claim_a
            authoritative_authority = authority_a
            reason = f"{authority_a} has higher authority than {authority_b}"
        elif level_b > level_a:
            authoritative_claim = claim_b
            authoritative_authority = authority_b
            reason = f"{authority_b} has higher authority than {authority_a}"
        else:
            # Same authority level - tie-breaker needed
            # In this case, check if any fact is already recorded
            recorded_a = self._is_fact_recorded(claim_a)
            recorded_b = self._is_fact_recorded(claim_b)

            if recorded_a and not recorded_b:
                authoritative_claim = claim_a
                authoritative_authority = authority_a
                reason = f"{claim_a} is already recorded in Truth Matrix"
            elif recorded_b and not recorded_a:
                authoritative_claim = claim_b
                authoritative_authority = authority_b
                reason = f"{claim_b} is already recorded in Truth Matrix"
            else:
                # Both recorded or neither recorded - use lexicographic order as tiebreaker
                if claim_a < claim_b:
                    authoritative_claim = claim_a
                    authoritative_authority = authority_a
                    reason = "Same authority; using lexicographic ordering (tie-breaker)"
                else:
                    authoritative_claim = claim_b
                    authoritative_authority = authority_b
                    reason = "Same authority; using lexicographic ordering (tie-breaker)"

        logger.info(f"✅ CONFLICT RESOLVED: '{authoritative_claim}'")

        return {
            "authoritative_claim": authoritative_claim,
            "authority": authoritative_authority,
            "reason": reason,
            "authority_level_winner": max(level_a, level_b),
            "claims_compared": 2,
        }

    def find_conflicting_facts(self, statement: str, fact_type: Optional[str] = None) -> Optional[str]:
        """
        Check if a statement contradicts any existing facts.

        Args:
            statement: The proposed statement
            fact_type: Optional fact type to limit search

        Returns:
            Conflicting fact if found, None if no conflicts
        """
        facts = self.truth_matrix.get_all_facts()

        # Simple negation check (very basic for this prototype)
        # In production, this would use semantic analysis
        statement_lower = statement.lower()

        for fact in facts:
            existing_statement = fact.get("statement", "").lower()

            # Check for explicit contradiction
            if self._statements_contradict(statement_lower, existing_statement):
                logger.warning(f"⚠️  CONFLICT DETECTED: '{statement}' contradicts existing fact")
                return existing_statement

        return None

    def get_authority_ranking(self) -> Dict[str, int]:
        """Get the authority hierarchy for inspection."""
        return self.AUTHORITY_HIERARCHY

    # ========== PRIVATE METHODS ==========

    def _is_fact_recorded(self, statement: str) -> bool:
        """Check if a fact is already recorded in Truth Matrix."""
        facts = self.truth_matrix.find_facts_like(statement)
        return len(facts) > 0

    def _statements_contradict(self, statement_a: str, statement_b: str) -> bool:
        """
        Check if two statements directly contradict each other.

        This is a very simple implementation. Real version would use semantic analysis.
        For now, we check for explicit negation patterns.
        """
        # Check for explicit "not" contradictions
        if statement_a.startswith("not ") and statement_b == statement_a[4:]:
            return True
        if statement_b.startswith("not ") and statement_a == statement_b[4:]:
            return True

        # Check for opposite claims
        opposite_pairs = [
            ("true", "false"),
            ("valid", "invalid"),
            ("enabled", "disabled"),
            ("active", "inactive"),
        ]

        for positive, negative in opposite_pairs:
            if (positive in statement_a and negative in statement_b) or (
                negative in statement_a and positive in statement_b
            ):
                return True

        return False
