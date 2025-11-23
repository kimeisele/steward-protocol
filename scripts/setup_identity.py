#!/usr/bin/env python3
"""
HERALD Identity Setup - Generate and register cryptographic keys.

This script sets up HERALD's Steward Protocol identity by:
1. Generating a new ECDSA keypair (NIST P-256, SHA256)
2. Displaying the public key for embedding in STEWARD.md
3. Providing instructions for securing the private key

The private key will be stored in `.steward/keys/private.pem` (user-only access).
You must then add the key to GitHub Secrets as `HERALD_PRIVATE_KEY` for CI/CD pipelines.

Usage:
    python scripts/setup_identity.py
"""

import sys
import os
from pathlib import Path

try:
    from steward import crypto
except ImportError:
    print("❌ ERROR: 'steward' module not found")
    print("   Please ensure you're running this from the project root")
    print("   and that the steward package is installed.")
    sys.exit(1)


def print_banner(title: str):
    """Print a formatted banner."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Main setup flow."""
    print_banner("🦅 HERALD Identity Setup - Steward Protocol v3.1")

    # Step 1: Generate keypair
    print("\n[STEP 1] Generating cryptographic keypair...")
    print("   Algorithm: ECDSA (Elliptic Curve Digital Signature)")
    print("   Curve: NIST P-256")
    print("   Hash: SHA256")

    try:
        newly_created = crypto.ensure_keys_exist()
        if newly_created:
            print("   ✅ New keypair generated")
        else:
            print("   ℹ️  Keypair already exists")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        sys.exit(1)

    # Step 2: Show public key
    print("\n[STEP 2] Retrieving public key...")
    try:
        public_key = crypto.get_public_key_string()
        print(f"   ✅ Public key retrieved ({len(public_key)} characters)")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        sys.exit(1)

    # Step 3: Show private key location
    print("\n[STEP 3] Private key location...")
    private_key_path = Path.home() / ".steward" / "keys" / "private.pem"
    print(f"   📁 Private key stored at: {private_key_path}")
    print(f"   🔐 Permissions: Owner-only (0o600)")
    print(f"   ⚠️  NEVER commit this file to git")

    # Step 4: Instructions for GitHub Secrets
    print_banner("Next Steps: Register Identity in GitHub")
    print("\n1. Add public key to herald/STEWARD.md:")
    print(f"\n   ```yaml\n   - **key:** `{public_key}`\n   ```\n")

    print("2. Register private key in GitHub Secrets:")
    print("   a) Go to: https://github.com/kimeisele/steward-protocol/settings/secrets/actions")
    print("   b) Click 'New repository secret'")
    print("   c) Name: HERALD_PRIVATE_KEY")
    print("   d) Value: (paste the contents of private.pem file below)")

    # Step 5: Show private key (for manual entry)
    print("\n" + "=" * 70)
    print("  ⚠️  PRIVATE KEY - KEEP THIS SECURE")
    print("=" * 70)

    try:
        with open(private_key_path, "r") as f:
            private_key_content = f.read()
            print(private_key_content)
    except FileNotFoundError:
        print("❌ ERROR: Private key file not found")
        print(f"   Expected at: {private_key_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR reading private key: {e}")
        sys.exit(1)

    # Final instructions
    print_banner("✅ Identity Setup Complete")
    print("\n✅ Status: HERALD is now registered as a Steward Protocol Agent")
    print("📋 Action required: Add the public key and private key to GitHub")
    print("🚀 Once done, HERALD can sign all generated content cryptographically")
    print("")


if __name__ == "__main__":
    main()
