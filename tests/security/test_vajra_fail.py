
import os
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.steward.constitution import ConstitutionalOath


class TestVajraFailure:
    def test_dev_mode_bypass_vulnerability(self):
        """
        PROOF OF DEFECT: The Vajra Failure.
        
        Security Requirement: The Constitutional Oath must verification the hash matches reality.
        Vulnerability: If STEWARD_DEV_MODE=true, it accepts ANY hash (or specifically 'genesis_hash' check bypass).
        
        We simulate an attack where:
        1. We are in Dev Mode (Env Var set).
        2. We provide a 'genesis_hash' stored value but the file is missing/different.
        3. The system should REJECT this (Safe default), but currently ACCEPTS it.
        """

        # 1. Simulate Dev Mode
        with patch.dict(os.environ, {"STEWARD_DEV_MODE": "true"}):

            # 2. Instantiate Oath
            oath = ConstitutionalOath()

            # 3. Call verification with a "bypass" condition
            # The vulnerability code:
            # if stored_hash == "genesis_hash": return True (inside dev mode check)

            # We mock the internal hash computation to be "REALITY"
            # And we pass "genesis_hash" as the argument (what is stored/claimed).

            # verify_oath(self, stored_hash)
            # stored_hash = "genesis_hash"

            with patch.object(oath, 'compute_constitution_hash', return_value="REALITY_HASH_123"):
                # verify_oath expects an EVENT DICT, not stored_hash arg
                fake_event = {"constitution_hash": "genesis_hash", "agent": "attacker"}
                is_valid, reason = oath.verify_oath(fake_event)

                print(f"DEBUG: Dev Mode=True. Stored='genesis_hash'. Reality='REALITY_HASH_123'. Result={is_valid}")

                # ASSERTION OF TRUTH
                # A secure system should return FALSE because "genesis_hash" != "REALITY_HASH_123".
                # The Bug: It returns TRUE.

                assert is_valid is False, "SECURITY BREACH: Vajra broken. System accepted 'genesis_hash' bypass in Dev Mode."
