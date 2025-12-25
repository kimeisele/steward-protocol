"""
TEST GUARDIAN - Who Watches the Watchers

PHILOSOPHY:
"Quis custodiet ipsos custodes?" - Who will guard the guards themselves?

Tests are CONTRACTS. They define expected behavior.
When code changes break a test, the CODE is wrong, not the test.

This module enforces test immutability:
1. Records test hashes at "birth" (first run)
2. Detects mutations before test execution
3. Blocks or alerts on unauthorized changes
4. Logs all mutation attempts to lineage

INTEGRATION:
- Reads policy from TestGovernanceConfig (Phoenix section)
- Records baselines to lineage (immutable)
- Called by TestOrchestrationPlugin before running tests
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TEST_GUARDIAN")


# ============================================================================
# TEST CONTRACT - Immutable record of a test's "birth"
# ============================================================================


@dataclass
class TestContract:
    """
    Immutable record of a test file at its creation.

    Once a test is "born", its hash is recorded.
    Any future mutation triggers governance policy.
    """

    test_path: str
    content_hash: str
    created_at: str
    created_by: str = "unknown"
    frozen: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_path": self.test_path,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "frozen": self.frozen,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestContract":
        return cls(**data)


# ============================================================================
# MUTATION EVENT - Record of an attempted/detected mutation
# ============================================================================


@dataclass
class MutationEvent:
    """Record of a detected test mutation."""

    test_path: str
    old_hash: str
    new_hash: str
    detected_at: str
    action_taken: str  # "blocked", "approved", "warned"
    approved_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_path": self.test_path,
            "old_hash": self.old_hash,
            "new_hash": self.new_hash,
            "detected_at": self.detected_at,
            "action_taken": self.action_taken,
            "approved_by": self.approved_by,
        }


# ============================================================================
# TEST GUARDIAN - The Watchman
# ============================================================================


class Guardian:
    """
    Guardian of test suite integrity.

    Enforces test immutability policy:
    - Records test hashes at first run ("birth")
    - Detects mutations before execution
    - Blocks/warns/requires approval based on policy
    - Logs everything to lineage
    """

    def __init__(self, kernel: Optional["RealVibeKernel"] = None):
        self._kernel = kernel
        self._contracts: Dict[str, TestContract] = {}
        self._mutations: List[MutationEvent] = []
        self._config = None

        # Temporary permits for test updates (expire after one use)
        self._update_permits: Dict[str, str] = {}  # test_path -> reason

        # Load existing baselines
        self._load_baselines()

    def _get_config(self):
        """Get TestGovernanceConfig from Phoenix."""
        if self._config is not None:
            return self._config

        # Try to get from kernel's Phoenix config
        if self._kernel and hasattr(self._kernel, "config"):
            config = getattr(self._kernel.config, "test_governance", None)
            if config:
                self._config = config
                return self._config

        # Fallback to defaults
        from vibe_core.phoenix.sections.test_governance.section_main import (
            TestGovernanceConfig,
        )

        self._config = TestGovernanceConfig()
        return self._config

    def _get_baseline_path(self) -> Path:
        """Get path to baseline storage."""
        config = self._get_config()
        return Path(config.baseline_path)

    def _load_baselines(self) -> None:
        """Load existing test contracts from disk."""
        path = self._get_baseline_path()
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                for test_path, contract_data in data.get("contracts", {}).items():
                    self._contracts[test_path] = TestContract.from_dict(contract_data)
                logger.info(f"Loaded {len(self._contracts)} test contracts")
            except Exception as e:
                logger.warning(f"Failed to load baselines: {e}")

    def _save_baselines(self) -> None:
        """Save test contracts to disk."""
        path = self._get_baseline_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "contracts": {k: v.to_dict() for k, v in self._contracts.items()},
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    # ========================================================================
    # CORE API
    # ========================================================================

    def hash_file(self, path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        if not path.exists():
            return "FILE_NOT_FOUND"

        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def register_test(
        self,
        test_path: str,
        created_by: str = "unknown",
        frozen: bool = False,
    ) -> TestContract:
        """
        Register a new test contract (at "birth").

        This records the test's hash, making it immutable.
        """
        path = Path(test_path)
        content_hash = self.hash_file(path)

        contract = TestContract(
            test_path=test_path,
            content_hash=content_hash,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            frozen=frozen,
        )

        self._contracts[test_path] = contract
        self._save_baselines()

        # Record to lineage
        self._record_to_lineage(
            event_type="TEST_CONTRACT_CREATED",
            details={
                "test_path": test_path,
                "content_hash": content_hash,
                "frozen": frozen,
            },
        )

        logger.info(f"Registered test contract: {test_path} ({content_hash})")
        return contract

    def validate_test(self, test_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate a test file hasn't mutated.

        Returns:
            (is_valid, error_message)
            is_valid: True if test is unchanged or no contract exists
            error_message: Description of mutation if detected
        """
        config = self._get_config()

        # Check if we have a contract for this test
        if test_path not in self._contracts:
            # No contract = first run, register it
            if config.baseline_enforcement:
                self.register_test(test_path)
            return (True, None)

        # Compare current hash with contract
        contract = self._contracts[test_path]
        current_hash = self.hash_file(Path(test_path))

        if current_hash == contract.content_hash:
            return (True, None)

        # MUTATION DETECTED!
        error = f"Test mutation detected: {test_path}"
        error += f"\n  Original: {contract.content_hash}"
        error += f"\n  Current:  {current_hash}"

        # Log the mutation
        mutation = MutationEvent(
            test_path=test_path,
            old_hash=contract.content_hash,
            new_hash=current_hash,
            detected_at=datetime.now().isoformat(),
            action_taken=config.mutation_policy,
        )
        self._mutations.append(mutation)

        # Record to lineage
        self._record_to_lineage(
            event_type="TEST_MUTATION_DETECTED",
            details=mutation.to_dict(),
        )

        # Apply policy
        if config.mutation_policy == "blocked":
            logger.error(f"BLOCKED: {error}")
            return (False, error)
        elif config.mutation_policy == "human_approval":
            logger.warning(f"REQUIRES APPROVAL: {error}")
            return (False, error + "\n\nHuman approval required to proceed.")
        else:  # warn_only
            logger.warning(f"WARNING: {error}")
            return (False, error)

    def validate_all_tests(self, test_dir: str = "tests") -> Dict[str, Any]:
        """
        Validate all test files in a directory.

        Returns summary of validation results.
        """
        results = {
            "total": 0,
            "valid": 0,
            "mutated": 0,
            "new": 0,
            "errors": [],
        }

        test_path = Path(test_dir)
        for py_file in test_path.rglob("test_*.py"):
            results["total"] += 1
            rel_path = str(py_file)

            if rel_path not in self._contracts:
                results["new"] += 1
                self.register_test(rel_path)
            else:
                is_valid, error = self.validate_test(rel_path)
                if is_valid:
                    results["valid"] += 1
                else:
                    results["mutated"] += 1
                    results["errors"].append(error)

        return results

    def is_frozen(self, test_path: str) -> bool:
        """Check if a test is frozen (can never be modified)."""
        config = self._get_config()
        return config.is_frozen(test_path)

    def can_modify(self, test_path: str, modifier: str = "ai") -> tuple[bool, str]:
        """
        Check if a test can be modified.

        Returns:
            (can_modify, reason)
        """
        config = self._get_config()

        # Check if frozen (CONSTITUTIONAL - never modifiable)
        if self.is_frozen(test_path):
            return (False, f"Test is FROZEN and cannot be modified: {test_path}")

        # Check for temporary permit (Feature Evolution Mode)
        if test_path in self._update_permits:
            reason = self._update_permits[test_path]
            # Consume the permit (one-time use)
            del self._update_permits[test_path]
            logger.info(f"Permit consumed for {test_path}: {reason}")
            return (True, f"Modification permitted: {reason}")

        # Check if human review required
        if config.requires_human_review(test_path):
            if modifier == "ai":
                return (False, f"Test requires human review: {test_path}")

        # Check mutation policy
        if config.mutation_policy == "blocked" and modifier == "ai":
            return (False, f"AI modification blocked by policy: {test_path}")

        return (True, "Modification allowed")

    # ========================================================================
    # PERMIT SYSTEM (Feature Evolution Mode)
    # ========================================================================

    def permit_update(self, test_path: str, reason: str, approved_by: str = "human") -> bool:
        """
        Issue a one-time permit to update a test.

        This is for Feature Evolution mode when requirements change
        and tests legitimately need updating.

        The permit is consumed on first use (single-use).

        Args:
            test_path: Path to the test file
            reason: Why the update is needed (logged to lineage)
            approved_by: Who approved this (must be human for frozen tests)

        Returns:
            True if permit issued, False if test is frozen
        """
        # Frozen tests can NEVER be permitted
        if self.is_frozen(test_path):
            logger.error(f"Cannot permit update to FROZEN test: {test_path}")
            return False

        self._update_permits[test_path] = reason

        # Record to lineage
        self._record_to_lineage(
            event_type="TEST_UPDATE_PERMITTED",
            details={
                "test_path": test_path,
                "reason": reason,
                "approved_by": approved_by,
            },
        )

        logger.info(f"Permit issued for {test_path}: {reason}")
        return True

    def revoke_permit(self, test_path: str) -> bool:
        """Revoke a previously issued permit."""
        if test_path in self._update_permits:
            del self._update_permits[test_path]
            logger.info(f"Permit revoked for {test_path}")
            return True
        return False

    def list_permits(self) -> Dict[str, str]:
        """List all active permits."""
        return dict(self._update_permits)

    def accept_update(self, test_path: str, reason: str = "requirements changed") -> bool:
        """
        Accept a test mutation and update the contract.

        Call this AFTER the test has been legitimately updated
        to register the new hash as the baseline.

        Args:
            test_path: Path to the updated test
            reason: Why the update was needed

        Returns:
            True if accepted, False if frozen
        """
        if self.is_frozen(test_path):
            logger.error(f"Cannot accept update to FROZEN test: {test_path}")
            return False

        # Get new hash
        new_hash = self.hash_file(Path(test_path))
        old_hash = self._contracts.get(
            test_path,
            TestContract(
                test_path=test_path,
                content_hash="",
                created_at="",
            ),
        ).content_hash

        # Update contract
        self._contracts[test_path] = TestContract(
            test_path=test_path,
            content_hash=new_hash,
            created_at=datetime.now().isoformat(),
            created_by="human",
            frozen=False,
            notes=reason,
        )
        self._save_baselines()

        # Record to lineage
        self._record_to_lineage(
            event_type="TEST_CONTRACT_UPDATED",
            details={
                "test_path": test_path,
                "old_hash": old_hash,
                "new_hash": new_hash,
                "reason": reason,
            },
        )

        logger.info(f"Contract updated for {test_path}: {old_hash} -> {new_hash}")
        return True

    # ========================================================================
    # LINEAGE INTEGRATION
    # ========================================================================

    def _record_to_lineage(self, event_type: str, details: Dict[str, Any]) -> None:
        """Record event to kernel's lineage/ledger."""
        if not self._kernel:
            return

        # Try lineage first (newer), then ledger (legacy)
        if hasattr(self._kernel, "lineage"):
            try:
                self._kernel.lineage.add_block(
                    {
                        "event_type": event_type,
                        "agent_id": "TEST_GUARDIAN",
                        "details": details,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to record to lineage: {e}")

        elif hasattr(self._kernel, "ledger"):
            try:
                self._kernel.ledger.record_event(
                    event_type=event_type,
                    agent_id="TEST_GUARDIAN",
                    details=details,
                )
            except Exception as e:
                logger.debug(f"Failed to record to ledger: {e}")

    # ========================================================================
    # REPORTING
    # ========================================================================

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of test contracts and mutations."""
        return {
            "total_contracts": len(self._contracts),
            "frozen_tests": sum(1 for c in self._contracts.values() if c.frozen),
            "mutations_detected": len(self._mutations),
            "policy": self._get_config().mutation_policy,
            "regression_mode": self._get_config().regression_mode,
        }

    def print_status(self) -> str:
        """Print human-readable status."""
        summary = self.get_summary()
        lines = [
            "=" * 60,
            "TEST GUARDIAN STATUS",
            "=" * 60,
            f"Test Contracts:     {summary['total_contracts']}",
            f"Frozen Tests:       {summary['frozen_tests']}",
            f"Mutations Detected: {summary['mutations_detected']}",
            "",
            f"Mutation Policy:    {summary['policy']}",
            f"Regression Mode:    {summary['regression_mode']}",
            "=" * 60,
        ]

        if self._mutations:
            lines.append("\nRECENT MUTATIONS:")
            for m in self._mutations[-5:]:
                lines.append(f"  - {m.test_path}: {m.action_taken}")

        return "\n".join(lines)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "TestGuardian",
    "TestContract",
    "MutationEvent",
]
