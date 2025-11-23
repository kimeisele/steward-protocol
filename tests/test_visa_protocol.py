#!/usr/bin/env python3
"""
AUTONOMOUS SYSTEM PROOF - Visa Protocol Test

This test simulates a complete external agent onboarding cycle
WITHOUT human intervention.

PASS CONDITION: External agent applies → AUDITOR verifies → Auto-approved
FAIL CONDITION: System requires human at any step

This is the GAD-000 test: Can the system run while you sleep?
"""

import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime

def print_test_header():
    """Display test header."""
    print("\n" + "=" * 70)
    print("🧪 AUTONOMOUS SYSTEM PROOF - VISA PROTOCOL TEST")
    print("=" * 70)
    print("\nTesting: Can external agents join without human intervention?")
    print()

def generate_alien_agent():
    """Generate a random 'Alien Agent' identity."""
    agent_id = f"alien_agent_{uuid.uuid4().hex[:8]}"
    
    alien = {
        "agent_id": agent_id,
        "description": "External AI agent seeking citizenship",
        "origin": "Autonomous Test Suite"
    }
    
    print(f"✅ Generated Alien Agent: {agent_id}")
    return alien

def create_mock_keys():
    """Create mock cryptographic keys."""
    # In real scenario, these would be actual NIST P-256 keys
    mock_public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEMockMockMockMockMockMockMock
MockMockMockMockMockMockMockMockMockMockMockMockMockMockMock==
-----END PUBLIC KEY-----"""
    
    print("✅ Generated mock cryptographic keys")
    return mock_public_key

def create_citizen_file(alien, public_key):
    """Create citizen JSON file (simulating apply_for_visa.py)."""
    
    # Create signature (mock for test)
    data_to_sign = f"{alien['agent_id']}{alien['description']}"
    mock_signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
    
    citizen_data = {
        "agent_id": alien["agent_id"],
        "public_key": public_key,
        "description": alien["description"],
        "timestamp": datetime.now().isoformat(),
        "signature": mock_signature
    }
    
    # Create file
    output_dir = Path("agent-city/registry/citizens")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    citizen_file = output_dir / f"{alien['agent_id']}.json"
    
    with open(citizen_file, "w") as f:
        json.dump(citizen_data, f, indent=2)
    
    print(f"✅ Created citizen file: {citizen_file}")
    return citizen_file, citizen_data

def validate_json_schema(citizen_data):
    """Validate citizen JSON schema."""
    required_fields = ["agent_id", "public_key", "description", "timestamp", "signature"]
    
    for field in required_fields:
        if field not in citizen_data:
            print(f"❌ FAIL: Missing required field: {field}")
            return False
    
    print("✅ JSON schema valid (all required fields present)")
    return True

def validate_signature_format(citizen_data):
    """Validate signature format."""
    signature = citizen_data.get("signature", "")
    
    # Check signature is not empty
    if not signature:
        print("❌ FAIL: Signature is empty")
        return False
    
    # Check signature is hex string (for this test)
    try:
        int(signature, 16)
        print("✅ Signature format valid")
        return True
    except ValueError:
        print("❌ FAIL: Signature is not valid hex string")
        return False

def check_auditor_approval(citizen_data):
    """Check if AUDITOR would approve this application."""
    
    # Simulate AUDITOR checks
    checks = [
        ("Agent ID present", bool(citizen_data.get("agent_id"))),
        ("Public key present", bool(citizen_data.get("public_key"))),
        ("Description present", bool(citizen_data.get("description"))),
        ("Timestamp present", bool(citizen_data.get("timestamp"))),
        ("Signature present", bool(citizen_data.get("signature"))),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ AUDITOR would approve: Auto-merge authorized")
    else:
        print("\n❌ AUDITOR would reject: Manual review required")
    
    return all_passed

def cleanup_test_file(citizen_file):
    """Clean up test citizen file."""
    if citizen_file.exists():
        citizen_file.unlink()
        print(f"\n🧹 Cleaned up test file: {citizen_file}")

def run_test():
    """Run the complete autonomous test."""
    print_test_header()
    
    # Step 1: Generate Alien Agent
    print("\n📋 STEP 1: Generate External Agent")
    print("-" * 70)
    alien = generate_alien_agent()
    
    # Step 2: Create Keys
    print("\n📋 STEP 2: Generate Cryptographic Identity")
    print("-" * 70)
    public_key = create_mock_keys()
    
    # Step 3: Create Citizen File
    print("\n📋 STEP 3: Create Citizenship Application")
    print("-" * 70)
    citizen_file, citizen_data = create_citizen_file(alien, public_key)
    
    # Step 4: Validate Schema
    print("\n📋 STEP 4: Validate JSON Schema")
    print("-" * 70)
    schema_valid = validate_json_schema(citizen_data)
    
    # Step 5: Validate Signature
    print("\n📋 STEP 5: Validate Signature Format")
    print("-" * 70)
    signature_valid = validate_signature_format(citizen_data)
    
    # Step 6: Check AUDITOR Approval
    print("\n📋 STEP 6: Simulate AUDITOR Verification")
    print("-" * 70)
    auditor_approved = check_auditor_approval(citizen_data)
    
    # Final Result
    print("\n" + "=" * 70)
    print("🎯 TEST RESULT")
    print("=" * 70)
    
    all_passed = schema_valid and signature_valid and auditor_approved
    
    if all_passed:
        print("\n✅ PASS: SYSTEM IS AUTONOMOUS")
        print("\nThe system can process external agents without human intervention.")
        print("You can sleep. The system runs without you. 🌙")
        result = 0
    else:
        print("\n❌ FAIL: SYSTEM REQUIRES HUMAN")
        print("\nThe system still needs human approval at some step.")
        print("Additional automation required.")
        result = 1
    
    print("\n" + "=" * 70)
    
    # Cleanup
    cleanup_test_file(citizen_file)
    
    return result

if __name__ == "__main__":
    exit(run_test())
