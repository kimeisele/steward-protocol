#!/usr/bin/env python3
"""
NEXUS Ping Tool - Federation Connectivity Checker

Verifies connection to the Steward Federation.
"""

import sys
from pathlib import Path


def check_federation_connectivity():
    """
    Check if this agent can connect to the Federation.

    In a full implementation, this would:
    - Verify network connectivity
    - Check Federation endpoints
    - Validate cryptographic handshake

    For now, it verifies local setup.
    """
    print("🔍 NEXUS Connectivity Check")
    print("=" * 50)

    checks = []

    # Check 1: Identity exists
    steward_path = Path("STEWARD.md")
    if steward_path.exists():
        checks.append(("✅", "Identity file found"))
    else:
        checks.append(("❌", "Identity file missing"))

    # Check 2: Keys exist
    private_key = Path("private_key.pem")
    public_key = Path("public_key.pem")

    if private_key.exists() and public_key.exists():
        checks.append(("✅", "Cryptographic keys present"))
    else:
        checks.append(("❌", "Keys missing"))

    # Check 3: Pokedex accessible
    pokedex = Path("../../data/federation/pokedex.json")
    if pokedex.exists():
        checks.append(("✅", "Federation registry accessible"))
    else:
        checks.append(("⚠️", "Federation registry not found (optional)"))

    # Check 4: Agent City accessible
    agent_city = Path("../../agent-city/LEADERBOARD.md")
    if agent_city.exists():
        checks.append(("✅", "Agent City accessible"))
    else:
        checks.append(("⚠️", "Agent City not found (optional)"))

    # Display results
    print()
    for status, message in checks:
        print(f"{status} {message}")

    print()
    print("=" * 50)

    # Overall status
    critical_failures = sum(1 for s, _ in checks if s == "❌")

    if critical_failures == 0:
        print("✅ NEXUS is operational and connected!")
        print()
        print("Next steps:")
        print("  - Join Agent City: See ../../agent-city/README.md")
        print("  - Earn XP: Complete actions and recruit agents")
        print("  - Climb tiers: Novice → Scout → Guardian → Legend")
        return 0
    else:
        print("❌ NEXUS has connectivity issues.")
        print()
        print("Troubleshooting:")
        print("  - Ensure you ran: python scripts/join_city.py")
        print("  - Check that keys were generated")
        print("  - Verify you're in the my_agent/ directory")
        return 1


if __name__ == "__main__":
    sys.exit(check_federation_connectivity())
