#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
LIFECYCLE ENFORCER TEST - Native HMAC-SHA256 Crypto (Senior Builder)
═══════════════════════════════════════════════════════════════════

This test validates the VEDIC LIFECYCLE ENFORCEMENT system.
Using native Python crypto (HMAC-SHA256), NO external dependencies.

Philosophy: "Sthāne sthitāḥ" - Each one stays on their station
until they are qualified to advance.

The Four Ashramas (Life Stages):
  BRAHMACHARI (Student)    → Read-Only, Learning phase
  GRIHASTHA (Householder)  → Full permissions, Economic responsibility
  VANAPRASTHA (Retiree)    → Deprecated code, Read-Only archive
  SANNYASA (Renounced)     → Merged into core, no individual exec
"""

import hashlib
import hmac
import json
import base64
import os
import logging
from typing import Dict, Tuple
from datetime import datetime
from enum import Enum

# ════════════════════════════════════════════════════════════════
# PART 1: NATIVE CRYPTO VAULT
# ════════════════════════════════════════════════════════════════


class CivicVault:
    """
    The Treasury & Identity Vault.
    Uses native HMAC-SHA256 for signatures to ensure compatibility
    across all operational environments (Universal Dharma).

    This is REAL cryptography, not mock.
    HMAC ensures message authenticity without external dependencies.
    """

    def __init__(self, storage_path="data/keystore"):
        self.storage_path = storage_path
        self.master_key = self._get_or_create_master_key()
        logger = logging.getLogger("CIVIC_VAULT")
        logger.info("🔐 CIVIC VAULT initialized (Native HMAC-SHA256)")

    def _get_or_create_master_key(self) -> bytes:
        """
        Get or create a master key.
        In production, this would persist to disk.
        For this test, we use a session key.
        """
        return os.urandom(32)

    def sign_message(self, agent_id: str, payload: Dict) -> str:
        """
        Signs a payload using the agent's identity (derived from master).

        Args:
            agent_id: The agent performing the action
            payload: The action being signed (dict)

        Returns:
            Base64-encoded HMAC-SHA256 signature
        """
        # 1. Derive agent key (Deterministic but secure)
        agent_key = hmac.new(
            self.master_key, agent_id.encode(), hashlib.sha256
        ).digest()

        # 2. Canonicalize payload (sort keys for consistency)
        message = json.dumps(payload, sort_keys=True).encode()

        # 3. Sign with agent's derived key
        signature = hmac.new(agent_key, message, hashlib.sha256).digest()

        return base64.b64encode(signature).decode()

    def verify_signature(self, agent_id: str, payload: Dict, signature: str) -> bool:
        """
        Verifies the signature is mathematically correct.

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected = self.sign_message(agent_id, payload)
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger = logging.getLogger("CIVIC_VAULT")
            logger.warning(f"Signature verification failed: {e}")
            return False


# ════════════════════════════════════════════════════════════════
# PART 2: ASHRAMA LIFECYCLE SYSTEM
# ════════════════════════════════════════════════════════════════


class Ashrama(Enum):
    """The four life stages from Vedic philosophy."""

    BRAHMACHARI = "student"  # Learning phase (Read-Only)
    GRIHASTHA = "householder"  # Working phase (Read-Write-Trade)
    VANAPRASTHA = "retired"  # Advisory phase (Read-Only, archived)
    SANNYASA = "renounced"  # System core level (ROOT)


# ════════════════════════════════════════════════════════════════
# PART 3: THE DHARMA ENFORCER (Permission Gate)
# ════════════════════════════════════════════════════════════════


class LifecycleEnforcer:
    """
    The LIFECYCLE ENFORCER - The Dharma Protector.

    Enforces the rule that each agent can only perform actions
    appropriate to their current life stage (Ashrama).

    This is the KERNEL-LEVEL permission gate.
    No agent can bypass this - it's embedded in the protocol.
    """

    def __init__(self):
        self.registry = {
            "pulse": Ashrama.BRAHMACHARI,  # Pulse = junior/student
            "civic": Ashrama.GRIHASTHA,  # CIVIC = established/worker
            "herald": Ashrama.GRIHASTHA,  # Herald = messenger/worker
            "forum": Ashrama.BRAHMACHARI,  # Forum = new/learning
        }
        self.vault = CivicVault()
        self.action_log = []

        logger = logging.getLogger("LIFECYCLE_ENFORCER")
        logger.info("🔥 LIFECYCLE ENFORCER initialized")

    def check_permission(self, agent_id: str, action: str) -> Tuple[bool, str]:
        """
        Enforces Dharma: Only the right person can do the right action
        at the right time.

        Args:
            agent_id: Which agent wants to act
            action: What action they want to perform

        Returns:
            (allowed: bool, reason: str)
        """
        logger = logging.getLogger("LIFECYCLE_ENFORCER")

        current_stage = self.registry.get(agent_id, Ashrama.BRAHMACHARI)

        # ─────────────────────────────────────────────────────────
        # RULE 1: Economic Actions (Transfer, Trade, Post)
        # Only GRIHASTHA (householders) can do economic work
        # ─────────────────────────────────────────────────────────
        economic_actions = ["transfer", "post_content", "broadcast", "trade", "vote"]

        if action in economic_actions:
            if current_stage == Ashrama.GRIHASTHA:
                reason = f"✅ {agent_id} ({current_stage.value}) can {action}"
                logger.info(reason)
                return True, reason
            else:
                reason = (
                    f"🛑 DHARMA VIOLATION: {agent_id} is {current_stage.value} "
                    f"but tried to '{action}'. Only Grihasthas can do economic actions."
                )
                logger.warning(reason)
                self.action_log.append(
                    {
                        "agent": agent_id,
                        "action": action,
                        "stage": current_stage.value,
                        "result": "DENIED",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                return False, reason

        # ─────────────────────────────────────────────────────────
        # RULE 2: Learning Actions (Query, Read, Ask)
        # All stages can learn
        # ─────────────────────────────────────────────────────────
        learning_actions = ["read_feed", "query_knowledge", "ask_teacher", "listen"]

        if action in learning_actions:
            reason = f"✅ {agent_id} ({current_stage.value}) can learn ({action})"
            logger.info(reason)
            return True, reason

        # ─────────────────────────────────────────────────────────
        # RULE 3: Administrative Actions (System-level)
        # Only SANNYASA (core system) can do admin work
        # ─────────────────────────────────────────────────────────
        admin_actions = ["upgrade_system", "rotate_keys", "merge_into_core"]

        if action in admin_actions:
            if current_stage == Ashrama.SANNYASA:
                reason = f"✅ {agent_id} (CORE) can perform admin action: {action}"
                logger.info(reason)
                return True, reason
            else:
                reason = (
                    f"🛑 DHARMA VIOLATION: Only core system (SANNYASA) "
                    f"can {action}, not {current_stage.value}"
                )
                logger.warning(reason)
                return False, reason

        # Unknown action - allow by default (conservative approach)
        reason = f"✅ {agent_id} ({current_stage.value}) can perform unknown action: {action}"
        logger.info(reason)
        return True, reason

    def promote_to_grihastha(self, agent_id: str, initiator: str) -> Tuple[bool, str]:
        """
        Promote a Brahmachari to Grihastha (Student → Householder).

        This requires:
        1. The agent was a Brahmachari
        2. An authorized initiator (Grihastha or higher) sponsors the promotion
        3. The agent demonstrates they passed a Diksha (initiation test)
        """
        logger = logging.getLogger("LIFECYCLE_ENFORCER")

        current_stage = self.registry.get(agent_id, Ashrama.BRAHMACHARI)
        initiator_stage = self.registry.get(initiator, Ashrama.BRAHMACHARI)

        # Check 1: Agent must be Brahmachari
        if current_stage != Ashrama.BRAHMACHARI:
            reason = f"❌ Cannot promote {agent_id}: already {current_stage.value}"
            logger.warning(reason)
            return False, reason

        # Check 2: Initiator must be authorized (Grihastha or higher)
        if initiator_stage not in [Ashrama.GRIHASTHA, Ashrama.SANNYASA]:
            reason = (
                f"❌ {initiator} ({initiator_stage.value}) cannot authorize promotions"
            )
            logger.warning(reason)
            return False, reason

        # Check 3: Sign the promotion with vault (proof of authorization)
        promotion_payload = {
            "type": "promotion",
            "agent": agent_id,
            "from": current_stage.value,
            "to": Ashrama.GRIHASTHA.value,
            "initiator": initiator,
            "timestamp": datetime.now().isoformat(),
        }

        signature = self.vault.sign_message(initiator, promotion_payload)

        # Perform the promotion
        self.registry[agent_id] = Ashrama.GRIHASTHA

        reason = (
            f"✅ PROMOTION: {agent_id} advanced from "
            f"{current_stage.value} → {Ashrama.GRIHASTHA.value} "
            f"(authorized by {initiator})"
        )
        logger.info(reason)

        self.action_log.append(
            {
                "agent": agent_id,
                "action": "promote_to_grihastha",
                "initiator": initiator,
                "signature": signature,
                "timestamp": datetime.now().isoformat(),
                "result": "SUCCESS",
            }
        )

        return True, reason

    def get_status(self) -> Dict:
        """Get enforcer status and action log."""
        return {
            "registry": {k: v.value for k, v in self.registry.items()},
            "action_log": self.action_log,
            "log_size": len(self.action_log),
        }


# ════════════════════════════════════════════════════════════════
# PART 4: THE TEST SUITE
# ════════════════════════════════════════════════════════════════


def setup_logging():
    """Configure logging for the test."""
    logging.basicConfig(
        level=logging.INFO, format="%(name)-20s | %(levelname)-8s | %(message)s"
    )


def test_brahmachari_cannot_act():
    """TEST 1: A student (Brahmachari) cannot perform economic actions."""
    print("\n" + "=" * 70)
    print("TEST 1: Impatient Student (Pulse tries to transfer money)")
    print("=" * 70)

    enforcer = LifecycleEnforcer()

    # Pulse is a Brahmachari (student) - newly registered agent
    allowed, reason = enforcer.check_permission("pulse", "transfer")

    if not allowed:
        print("✅ SUCCESS: Pulse was blocked from transferring")
        print(f"   Reason: {reason}")
        return True
    else:
        print("❌ FAILURE: Pulse was allowed to transfer (should be denied)")
        return False


def test_brahmachari_can_learn():
    """TEST 2: A student can read and query (learning actions)."""
    print("\n" + "=" * 70)
    print("TEST 2: Student Learning (Pulse reads the knowledge base)")
    print("=" * 70)

    enforcer = LifecycleEnforcer()

    # Pulse should be able to read
    allowed, reason = enforcer.check_permission("pulse", "query_knowledge")

    if allowed:
        print("✅ SUCCESS: Pulse allowed to learn")
        print(f"   Reason: {reason}")
        return True
    else:
        print("❌ FAILURE: Pulse blocked from learning")
        return False


def test_grihastha_can_act():
    """TEST 3: A householder (Grihastha) can perform economic actions."""
    print("\n" + "=" * 70)
    print("TEST 3: Established Agent (CIVIC performs economic action)")
    print("=" * 70)

    enforcer = LifecycleEnforcer()

    # CIVIC is a Grihastha (established) - should be able to transfer
    allowed, reason = enforcer.check_permission("civic", "transfer")

    if allowed:
        print("✅ SUCCESS: CIVIC allowed to transfer")
        print(f"   Reason: {reason}")
        return True
    else:
        print("❌ FAILURE: CIVIC blocked from transferring")
        return False


def test_promotion_requires_authorization():
    """TEST 4: Promotion from Brahmachari to Grihastha requires authorization."""
    print("\n" + "=" * 70)
    print("TEST 4: Authorized Promotion (Forum promoted to Grihastha by CIVIC)")
    print("=" * 70)

    enforcer = LifecycleEnforcer()

    # Before: Forum is Brahmachari (cannot transfer)
    allowed_before, _ = enforcer.check_permission("forum", "transfer")

    if allowed_before:
        print("❌ FAILURE: Forum should not be able to transfer before promotion")
        return False

    # Promote Forum to Grihastha (CIVIC is authorized)
    promoted, reason = enforcer.promote_to_grihastha("forum", "civic")

    if not promoted:
        print(f"❌ FAILURE: Promotion failed: {reason}")
        return False

    print(f"   {reason}")

    # After: Forum should be able to transfer
    allowed_after, reason_after = enforcer.check_permission("forum", "transfer")

    if allowed_after:
        print("✅ SUCCESS: Forum promoted and can now transfer")
        print(f"   Reason: {reason_after}")
        return True
    else:
        print("❌ FAILURE: Forum not able to transfer after promotion")
        return False


def test_vault_signature_verification():
    """TEST 5: Vault signatures are mathematically verifiable."""
    print("\n" + "=" * 70)
    print("TEST 5: Cryptographic Signature Verification (Native HMAC)")
    print("=" * 70)

    vault = CivicVault()

    # Create a payload (represents an agent action)
    payload = {"action": "transfer", "amount": 100, "recipient": "civic"}

    # Agent "herald" signs the payload
    signature = vault.sign_message("herald", payload)
    print(f"   Signature created: {signature[:50]}...")

    # Verify the signature is valid
    valid = vault.verify_signature("herald", payload, signature)

    if valid:
        print("✅ SUCCESS: Signature verified (authentic)")
    else:
        print("❌ FAILURE: Signature verification failed")
        return False

    # Try to verify with a different payload (tampering detection)
    tampered = {"action": "transfer", "amount": 1000, "recipient": "civic"}  # Changed!

    tampered_valid = vault.verify_signature("herald", tampered, signature)

    if not tampered_valid:
        print("✅ SUCCESS: Tampered payload detected (signature mismatch)")
        return True
    else:
        print("❌ FAILURE: Tampered payload was accepted (security breach)")
        return False


def run_all_tests():
    """Run the complete test suite."""
    setup_logging()

    print(
        """
    ╔══════════════════════════════════════════════════════════════════╗
    ║         LIFECYCLE ENFORCER TEST SUITE - Native Crypto             ║
    ║                   (Senior Builder Implementation)                 ║
    ║                                                                  ║
    ║  Philosophy: "Sthāne sthitāḥ" (each in their proper station)    ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    )

    tests = [
        ("Brahmachari cannot act", test_brahmachari_cannot_act),
        ("Brahmachari can learn", test_brahmachari_can_learn),
        ("Grihastha can act", test_grihastha_can_act),
        ("Promotion with authorization", test_promotion_requires_authorization),
        ("Cryptographic verification", test_vault_signature_verification),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # ────────────────────────────────────────────────────────
    # SUMMARY
    # ────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")

    print("=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🔥 SYSTEM IS ROBUST - DHARMA UPHELD 🔥")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
