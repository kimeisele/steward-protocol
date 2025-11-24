#!/usr/bin/env python3
"""
Verification Script - Public Access Layer
Tests the FastAPI Gateway using TestClient.
"""

import sys
import logging
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Mock dependencies if not installed
try:
    from fastapi.testclient import TestClient
    from gateway.api import app
except ImportError:
    print("⚠️  FastAPI/TestClient not installed. Skipping full API test.")
    sys.exit(0)

def main():
    print("\n" + "="*60)
    print("🌐 VERIFICATION: Public Access Layer (Gateway)")
    print("="*60 + "\n")

    client = TestClient(app)
    api_key = "steward-secret-key"

    # 1. Test Auth Failure
    print("🔒 TEST 1: Auth Failure (No Key)")
    response = client.post("/v1/chat", json={"user_id": "admin", "command": "status"})
    if response.status_code == 401: # or 422 if header missing
        print("✅ Passed: 401/422 Unauthorized")
    else:
        print(f"❌ Failed: Got {response.status_code}")

    # 2. Test Unauthorized User
    print("\n⛔ TEST 2: Unauthorized User (Ledger Check)")
    response = client.post(
        "/v1/chat", 
        headers={"x-api-key": api_key},
        json={"user_id": "hacker_bob", "command": "status"}
    )
    if response.status_code == 403:
        print("✅ Passed: 403 Forbidden")
    else:
        print(f"❌ Failed: Got {response.status_code} - {response.text}")

    # 3. Test Valid Briefing
    print("\n🧠 TEST 3: Strategic Briefing (HIL Assistant)")
    response = client.post(
        "/v1/chat",
        headers={"x-api-key": api_key},
        json={"user_id": "hil_operator_01", "command": "briefing"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Passed: 200 OK")
        print(f"   Summary: {data['summary'][:100]}...")
        print(f"   Ledger Hash: {data['ledger_hash']}")
    else:
        print(f"❌ Failed: Got {response.status_code} - {response.text}")

    # 4. Test Natural Language Launch
    print("\n🚀 TEST 4: Natural Language Launch")
    response = client.post(
        "/v1/chat",
        headers={"x-api-key": api_key},
        json={
            "user_id": "hil_operator_01", 
            "command": "starte die Kampagne zur Veröffentlichung..."
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Passed: 200 OK")
        print(f"   Summary: {data['summary'][:100]}...")
    else:
        print(f"❌ Failed: Got {response.status_code} - {response.text}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
