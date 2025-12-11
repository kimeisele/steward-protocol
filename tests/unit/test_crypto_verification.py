"""
Test Real Cryptographic Verification
=====================================

This test proves that the VerifierTool now performs REAL cryptographic
signature verification using ECDSA P-256.

Success criteria:
1. Valid signatures are accepted
2. Invalid/tampered signatures are REJECTED
3. No simulation mode warnings appear
"""

from vibe_core.cartridges.system.archivist.tools.verifier_tool import VerifierTool
from vibe_core.steward.crypto import ensure_keys_exist, load_or_generate_keys, sign_content


def test_real_crypto_verification():
    """Test that crypto verification is REAL, not simulated."""
    print("=" * 80)
    print("CRYPTO VERIFICATION TEST - Proving Real Implementation")
    print("=" * 80)

    # Ensure keys exist
    ensure_keys_exist()

    # Load keys for signing
    private_key, public_key = load_or_generate_keys()

    # Initialize verifier
    verifier = VerifierTool()

    # Check that we're NOT in simulation mode
    assert not verifier.simulation_mode, "❌ FAILED: Still in simulation mode!"
    print("✅ Verifier is in REAL CRYPTO MODE (not simulation)")

    # Test 1: Valid signature should be accepted
    print("\n[Test 1] Valid Signature Verification")
    print("-" * 40)

    content = "This is a test message from HERALD_Agent"
    signature = sign_content(content, private_key)

    print(f"Content: {content}")
    print(f"Signature: {signature[:50]}...")

    is_valid, message = verifier.verify_signature(content, signature, "HERALD_Agent")

    print(f"Verification result: {is_valid}")
    print(f"Message: {message}")

    assert is_valid, f"❌ FAILED: Valid signature was rejected! {message}"
    assert "cryptographically verified" in message.lower(), "❌ FAILED: Not using crypto verification!"
    print("✅ PASSED: Valid signature was accepted")

    # Test 2: Invalid signature should be REJECTED
    print("\n[Test 2] Invalid Signature Rejection")
    print("-" * 40)

    tampered_signature = "FAKE" + signature[4:]  # Tamper with signature
    print(f"Tampered signature: {tampered_signature[:50]}...")

    is_valid, message = verifier.verify_signature(content, tampered_signature, "HERALD_Agent")

    print(f"Verification result: {is_valid}")
    print(f"Message: {message}")

    assert not is_valid, "❌ FAILED: Tampered signature was accepted! (SECURITY BREACH)"
    assert "FAILED" in message or "invalid" in message.lower(), "❌ FAILED: Wrong error message"
    print("✅ PASSED: Tampered signature was REJECTED")

    # Test 3: Modified content should fail verification
    print("\n[Test 3] Content Tampering Detection")
    print("-" * 40)

    tampered_content = content + " MODIFIED"
    print(f"Original: {content}")
    print(f"Tampered: {tampered_content}")
    print(f"Signature: {signature[:50]}... (original signature)")

    is_valid, message = verifier.verify_signature(tampered_content, signature, "HERALD_Agent")

    print(f"Verification result: {is_valid}")
    print(f"Message: {message}")

    assert not is_valid, "❌ FAILED: Content tampering was not detected!"
    print("✅ PASSED: Content tampering was detected")

    # Test 4: Verification proof shows real crypto
    print("\n[Test 4] Verification Proof Generation")
    print("-" * 40)

    proof = verifier.create_verification_proof({"author": "HERALD_Agent", "content": content})

    print(f"Verification status: {proof['verification_status']}")
    print(f"Algorithm: {proof.get('algorithm', 'N/A')}")
    print(f"Crypto enabled: {proof['crypto_enabled']}")
    print(f"Crypto available: {proof['crypto_available']}")

    assert proof["verification_status"] == "CRYPTOGRAPHICALLY_VERIFIED", "❌ FAILED: Proof shows simulation mode!"
    assert proof["algorithm"] == "ECDSA-P256-SHA256", "❌ FAILED: Wrong algorithm in proof!"
    assert proof["warning"] is None, "❌ FAILED: Warning present in proof!"
    print("✅ PASSED: Verification proof shows real cryptography")
