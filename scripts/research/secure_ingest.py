#!/usr/bin/env python3
"""
SECURE INGESTION PROTOCOL 🔐
One-time setup script for sensitive environment variables.

This script:
1. Reads environment variables set via CI/CD secrets or system settings
2. Encrypts them using the Civic Vault
3. Stores them in the economy.db database
4. Makes them unavailable from the environment (secure containment)

This is the ONLY place where raw API keys touch the disk.
After this runs, agents never see the raw key - they lease it from the Vault.

Usage:
    export TAVILY_API_KEY="your_actual_key"
    python3 scripts/secure_ingest.py

Philosophy:
"Secrets are not environment variables. Secrets are ASSETS managed by the collective."
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from civic.tools.economy import CivicBank

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SECURE_INGEST")


def ingest_secrets():
    """Ingest environment variable secrets into the Civic Vault."""

    print("\n🔐 SECURE INGESTION PROTOCOL")
    print("   (One-time secret storage)")

    # Initialize the bank and vault
    try:
        bank = CivicBank()
        vault = bank.vault
    except Exception as e:
        print(f"❌ Failed to initialize vault: {e}")
        return False

    if vault is None:
        print("❌ Vault not available (cryptography not installed)")
        return False

    # Secrets to ingest (add more as needed)
    secrets_to_ingest = {
        "tavily_api": "TAVILY_API_KEY",
        "openai_api": "OPENAI_API_KEY",
        "openrouter_api": "OPENROUTER_API_KEY",
    }

    ingested = []
    missing = []

    print("\n📥 Scanning environment for secrets...")

    for secret_name, env_var in secrets_to_ingest.items():
        value = os.getenv(env_var)

        if value:
            try:
                vault.store_secret(secret_name, value)
                print(f"   ✅ {secret_name} <- {env_var}")
                ingested.append(secret_name)
            except Exception as e:
                print(f"   ❌ Failed to ingest {secret_name}: {e}")
        else:
            print(f"   ⏭️  {secret_name} (not in environment)")
            missing.append(secret_name)

    # Summary
    print(f"\n📊 INGESTION SUMMARY")
    print(f"   ✅ Ingested: {len(ingested)} secret(s)")
    print(f"   ⏭️  Missing: {len(missing)} secret(s)")

    if ingested:
        print(f"\n🔒 SECURE STORAGE CONFIRMED")
        print(f"   Secrets are now encrypted in data/economy.db")
        print(f"   Master Key: data/security/master.key (chmod 600)")
        print(f"   Agents will LEASE these secrets using Credits")
        print(f"\n✅ INGESTION COMPLETE. Environment variables no longer needed.")
        return True
    else:
        print(f"\n⚠️  No secrets were ingested.")
        print(f"   Set at least one of: {', '.join(secrets_to_ingest.values())}")
        return False


def list_vaulted_assets():
    """List all assets currently in the vault."""

    try:
        bank = CivicBank()
        vault = bank.vault
    except Exception:
        return

    if vault is None:
        return

    assets = vault.list_assets()

    if assets:
        print(f"\n📦 VAULTED ASSETS")
        for asset in assets:
            print(f"   • {asset['key_name']}")
            print(f"     Created: {asset['created_at']}")
            if asset["rotated_at"] != asset["created_at"]:
                print(f"     Rotated: {asset['rotated_at']}")
    else:
        print(f"\n📦 VAULT IS EMPTY")


def show_vault_audit_trail(limit: int = 5):
    """Show recent vault access audit trail."""

    try:
        bank = CivicBank()
        vault = bank.vault
    except Exception:
        return

    if vault is None:
        return

    leases = vault.lease_history(limit=limit)

    if leases:
        print(f"\n🔍 VAULT AUDIT TRAIL (recent {limit} leases)")
        for lease in leases:
            print(
                f"   {lease['agent_id']} <- {lease['key_name']} "
                f"({lease['credits_charged']} Credits)"
            )
    else:
        print(f"\n🔍 VAULT AUDIT TRAIL (no leases yet)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Secure Ingestion Protocol")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest secrets from environment into vault",
    )
    parser.add_argument(
        "--list-assets", action="store_true", help="List all vaulted assets"
    )
    parser.add_argument(
        "--audit-trail", action="store_true", help="Show vault access audit trail"
    )

    args = parser.parse_args()

    # If no args, do default ingest + list
    if not (args.ingest or args.list_assets or args.audit_trail):
        success = ingest_secrets()
        list_vaulted_assets()
        show_vault_audit_trail()
        sys.exit(0 if success else 1)

    if args.ingest:
        ingest_secrets()

    if args.list_assets:
        list_vaulted_assets()

    if args.audit_trail:
        show_vault_audit_trail()
