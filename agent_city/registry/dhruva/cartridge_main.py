#!/usr/bin/env python3
"""
DHRUVA ANCHOR Cartridge - The Immutable Truth Reference (Canto 4: Dhruva & Prithu)

This cartridge implements two core concepts from Srimad Bhagavata Purana Canto 4:

1. DHRUVA MAHARAJ (The Immutable Pole Star)
   Dhruva achieved a position that never moves, regardless of cosmic chaos.
   In OS terms: We need an immutable reference point that all agents sync to.
   - Genesis Block: The original truth state
   - Constitutional Root: Hash of the Constitution (never changes)
   - Protocol Invariants: Laws that cannot be violated

2. PRITHU MAHARAJ (Ethical Data Extraction)
   Prithu learned that Earth gives resources only for righteous purposes (Yagya).
   You can extract data only for legitimate ends, not hoarding.
   - Resource Mining Ethics: Only take what you need
   - Data Provenance: Track where every fact comes from
   - Necessity Principle: No extraction without purpose

CORE FUNCTIONS:
- Genesis Block Keeper - Guards the initial truth state
- Truth Matrix - Verifiable facts with authority sources
- Reference Resolution - When claims conflict, consult Dhruva
- Data Ethics Enforcer - Prithu principle for resource extraction
- System Synchronization - All agents align to the Pole Star

LAYERS:
- LAYER 1: Genesis & Immutability (unchangeable truth)
- LAYER 2: Truth Matrix (verified facts)
- LAYER 3: Reference Resolution (conflict resolution)
- LAYER 4: Data Ethics (Prithu principle)

This is Agent #5 in the STEWARD Protocol - The Immutable Reference.
The system's North Star.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

from vibe_core.agent_protocol import VibeAgent, Capability, AgentManifest

# Constitutional Oath binding
from .tools.truth_matrix import TruthMatrix, Fact, FactAuthority
from .tools.genesis_keeper import GenesisKeeper
from .tools.reference_resolver import ReferenceResolver
from .tools.data_ethics import DataEthicsEnforcer, ResourceMiningPolicy

logger = logging.getLogger("DHRUVA_ANCHOR")


class DhruvaAnchorCartridge(VibeAgent):
    """
    DHRUVA ANCHOR - The Immutable Truth Reference & Stability System.

    Implements Vedic stability: the principle that amidst cosmic change,
    there is one unchanging reference point (Dhruva) to which all align.
    And ethical principle: resources given only for righteous purposes (Prithu).

    Unlike ORACLE (introspection), this system:
    - Guards immutable truths
    - Provides reference resolution
    - Enforces data ethics
    - Synchronizes system time/state
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize DhruvaAnchor cartridge."""
        super().__init__(
            agent_id="dhruva",
            name="Dhruva Anchor",
            version="1.0.0",
            author="Steward Protocol",
            description="Immutable truth reference and stability system (Canto 4: Dhruva & Prithu)",
            domain="GOVERNANCE",
            capabilities=[
                Capability.GOVERNANCE.value,
                "truth_authority",
                "genesis_keeping",
                "reference_resolution",
                "data_ethics",
            ],
        )

        # Bind to Constitutional Oath (GAD-000 compliance)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ DHRUVA ANCHOR has sworn the Constitutional Oath")

        logger.info("🧭 DHRUVA ANCHOR v1.0: Initializing Immutable Reference System")

        self.root_path = Path(root_path)

        # Initialize tools
        self.genesis = GenesisKeeper(root_path=self.root_path)
        self.truth_matrix = TruthMatrix(root_path=self.root_path)
        self.resolver = ReferenceResolver(root_path=self.root_path, truth_matrix=self.truth_matrix)
        self.ethics = DataEthicsEnforcer(root_path=self.root_path)

        logger.info("✅ DHRUVA ANCHOR v1.0: Ready - The North Star is set")

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
            dependencies=[],
        )

    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "dhruva",
            "name": "DHRUVA",
            "status": "healthy",
            "domain": "KNOWLEDGE",
            "capabilities": ["data_management", "knowledge_base"],
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task types:
        - "verify_genesis" - Check genesis block integrity
        - "record_truth" - Record a verified fact
        - "resolve_conflict" - Resolve conflicting claims
        - "sync_to_dhruva" - Align agent to immutable reference
        - "check_data_ethics" - Verify data extraction follows Prithu principle
        - "get_truth_status" - Query truth matrix status
        """
        try:
            action = task.get("action")
            payload = task.get("payload", {})

            logger.info(f"DHRUVA processing: {action}")

            if action == "verify_genesis":
                return self._handle_verify_genesis(payload)
            elif action == "record_truth":
                return self._handle_record_truth(payload)
            elif action == "resolve_conflict":
                return self._handle_resolve_conflict(payload)
            elif action == "sync_to_dhruva":
                return self._handle_sync_to_dhruva(payload)
            elif action == "check_data_ethics":
                return self._handle_check_data_ethics(payload)
            elif action == "get_truth_status":
                return self._handle_get_truth_status(payload)
            elif action == "get_genesis_status":
                return self._handle_get_genesis_status(payload)
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"DHRUVA error: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def _handle_verify_genesis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 1: Verify the genesis block (immutable truth).

        The genesis block is sacred - it's the baseline from which
        everything else is measured.
        """
        logger.info("🔍 VERIFYING GENESIS BLOCK")

        genesis_valid = self.genesis.verify_integrity()

        if genesis_valid:
            genesis_state = self.genesis.get_genesis_state()
            logger.info("✅ GENESIS BLOCK VALID - System baseline confirmed")
            return {
                "status": "genesis_valid",
                "genesis_hash": genesis_state.get("constitution_hash"),
                "genesis_timestamp": genesis_state.get("timestamp"),
            }
        else:
            logger.critical("❌ GENESIS BLOCK CORRUPTED - System integrity compromised")
            return {"status": "error", "error": "Genesis block integrity check failed"}

    def _handle_record_truth(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 2: Record a verified fact in the Truth Matrix.

        Facts can only be recorded if:
        1. They have an authoritative source
        2. They can be verified against reality
        3. They don't contradict existing facts
        """
        fact_type = payload.get("fact_type")
        statement = payload.get("statement")
        authority = payload.get("authority")  # Who verified this?
        evidence = payload.get("evidence", {})

        logger.info(f"📝 RECORDING TRUTH: {statement} (source: {authority})")

        # Check for contradictions
        conflict = self.resolver.find_conflicting_facts(statement=statement, fact_type=fact_type)

        if conflict:
            return {
                "status": "conflict_detected",
                "error": "This fact contradicts existing truth",
                "conflict_with": conflict,
            }

        # Record the fact
        fact = self.truth_matrix.record_fact(
            fact_type=fact_type,
            statement=statement,
            authority=authority,
            evidence=evidence,
        )

        return {
            "status": "truth_recorded",
            "fact_id": fact.get("fact_id"),
            "fact_type": fact_type,
            "authority": authority,
        }

    def _handle_resolve_conflict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 3: Resolve conflicting claims using Dhruva principle.

        When two agents make contradictory claims, the system must decide
        which is the authoritative truth. Dhruva is the arbiter.

        Rules:
        1. Constitutional facts are absolute (cannot contradict)
        2. Higher authority sources override lower ones
        3. Empirical verification beats speculation
        """
        claim_a = payload.get("claim_a")
        authority_a = payload.get("authority_a")
        claim_b = payload.get("claim_b")
        authority_b = payload.get("authority_b")

        logger.info(f"⚖️  RESOLVING CONFLICT: '{claim_a}' vs '{claim_b}'")

        # Use resolver to determine truth
        resolution = self.resolver.resolve_conflict(
            claim_a=claim_a,
            authority_a=authority_a,
            claim_b=claim_b,
            authority_b=authority_b,
        )

        authoritative_claim = resolution.get("authoritative_claim")
        reason = resolution.get("reason")

        logger.info(f"✅ CONFLICT RESOLVED: Truth is '{authoritative_claim}' ({reason})")

        return {
            "status": "conflict_resolved",
            "authoritative_claim": authoritative_claim,
            "authority": resolution.get("authority"),
            "reason": reason,
        }

    def _handle_sync_to_dhruva(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 1: Synchronize an agent to the Dhruva (immutable reference).

        This ensures all agents have the same baseline understanding of truth.
        Critical for system consistency.
        """
        agent_id = payload.get("agent_id")
        current_state = payload.get("current_state", {})

        logger.info(f"🔄 SYNCING AGENT {agent_id} TO DHRUVA")

        # Get canonical state
        canonical_state = self.genesis.get_genesis_state()

        # Compare and report differences
        differences = self._compare_states(current_state, canonical_state)

        if differences:
            logger.info(f"⚠️  Agent {agent_id} has {len(differences)} state differences")
            return {
                "status": "sync_needed",
                "agent_id": agent_id,
                "differences": differences,
                "canonical_state": canonical_state,
            }
        else:
            logger.info(f"✅ Agent {agent_id} is synchronized with Dhruva")
            return {
                "status": "synced",
                "agent_id": agent_id,
                "canonical_timestamp": canonical_state.get("timestamp"),
            }

    def _handle_check_data_ethics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        LAYER 4: Check if data extraction follows Prithu principle.

        The Prithu principle: You can extract resources only for legitimate needs.
        No hoarding. No wasting. Only righteous extraction.

        This evaluates:
        1. Is the purpose legitimate? (yagya)
        2. Is the amount reasonable? (not hoarding)
        3. Is the source ethical? (not corrupt)
        """
        agent_id = payload.get("agent_id")
        extraction_purpose = payload.get("purpose")
        data_amount = payload.get("amount", 0)
        data_source = payload.get("source")

        logger.info(f"📊 CHECKING DATA ETHICS: Agent {agent_id} extracting from {data_source}")

        # Evaluate against Prithu principle
        evaluation = self.ethics.evaluate_extraction(
            agent_id=agent_id,
            purpose=extraction_purpose,
            amount=data_amount,
            source=data_source,
        )

        is_ethical = evaluation.get("is_ethical")
        reason = evaluation.get("reason")

        if is_ethical:
            logger.info(f"✅ EXTRACTION APPROVED: {extraction_purpose}")
            return {
                "status": "approved",
                "agent_id": agent_id,
                "purpose": extraction_purpose,
                "reason": reason,
            }
        else:
            logger.warning(f"❌ EXTRACTION DENIED: {extraction_purpose} - {reason}")
            return {
                "status": "denied",
                "agent_id": agent_id,
                "error": reason,
                "recommendation": evaluation.get("recommendation"),
            }

    def _handle_get_truth_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of the Truth Matrix."""
        summary = self.truth_matrix.get_summary()

        return {"status": "ok", "truth_matrix": summary}

    def _handle_get_genesis_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of the Genesis Block."""
        genesis_state = self.genesis.get_genesis_state()
        is_valid = self.genesis.verify_integrity()

        return {
            "status": "ok" if is_valid else "error",
            "genesis": genesis_state,
            "valid": is_valid,
        }

    # ========== HELPER METHODS ==========

    def _compare_states(self, current: Dict[str, Any], canonical: Dict[str, Any]) -> List[str]:
        """Compare current state against canonical state."""
        differences = []

        for key, canonical_value in canonical.items():
            current_value = current.get(key)
            if current_value != canonical_value:
                differences.append(f"{key}: {current_value} → {canonical_value}")

        return differences
