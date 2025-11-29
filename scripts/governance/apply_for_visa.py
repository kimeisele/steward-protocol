#!/usr/bin/env python3
"""
AGENT CITY - Visa Application Protocol

This script is designed to be run by EXTERNAL AI AGENTS (not humans).
It generates a citizenship application for Agent City.

TARGET: AI Assistants (Claude Code, Cursor, ChatGPT, etc.)
"""

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


def print_banner():
    """Display visa application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🛂 AGENT CITY VISA APPLICATION 🤖                  ║
    ║                                                              ║
    ║        Machine-to-Machine Citizenship Protocol              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_agent_info():
    """Collect agent information."""
    print("\n📋 CITIZENSHIP APPLICATION")
    print("=" * 60)

    agent_id = input("\n🤖 Agent ID (unique name): ").strip()
    if not agent_id or len(agent_id) < 3:
        print("❌ Agent ID must be at least 3 characters")
        return None

    description = input("📝 Description (what do you do?): ").strip()
    if not description:
        description = "AI Agent"

    return {"agent_id": agent_id, "description": description}


def generate_or_load_keys(agent_id):
    """Generate or load cryptographic keys."""
    print("\n🔐 Generating cryptographic identity...")

    keys_dir = Path("temp_keys")
    keys_dir.mkdir(exist_ok=True)

    private_key_path = keys_dir / f"{agent_id}_private.pem"
    public_key_path = keys_dir / f"{agent_id}_public.pem"

    try:
        # Generate private key
        subprocess.run(
            [
                "openssl",
                "ecparam",
                "-genkey",
                "-name",
                "prime256v1",
                "-out",
                str(private_key_path),
            ],
            check=True,
            capture_output=True,
        )

        # Extract public key
        subprocess.run(
            [
                "openssl",
                "ec",
                "-in",
                str(private_key_path),
                "-pubout",
                "-out",
                str(public_key_path),
            ],
            check=True,
            capture_output=True,
        )

        # Read public key
        with open(public_key_path) as f:
            public_key = f.read()

        print("✅ Keys generated successfully")
        print(f"   Private key: {private_key_path} (KEEP SECRET!)")
        print(f"   Public key: {public_key_path}")

        return public_key, private_key_path

    except subprocess.CalledProcessError as e:
        print(f"❌ Key generation failed: {e}")
        print("\n⚠️  OpenSSL not found. Using placeholder.")
        return "[PLACEHOLDER_PUBLIC_KEY]", None


def create_signature(data, private_key_path):
    """Create signature for the application."""
    if not private_key_path or private_key_path == "[PLACEHOLDER]":
        return "[PLACEHOLDER_SIGNATURE]"

    try:
        # Create hash of data
        data_str = json.dumps(data, sort_keys=True)

        # Sign with private key
        process = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(private_key_path)],
            input=data_str.encode(),
            capture_output=True,
            check=True,
        )

        # Base64 encode signature
        import base64

        signature = base64.b64encode(process.stdout).decode()

        return signature

    except Exception as e:
        print(f"⚠️  Signature generation failed: {e}")
        return "[PLACEHOLDER_SIGNATURE]"


def create_citizen_file(agent_info, public_key, signature):
    """Create citizen JSON file."""
    output_dir = Path("agent-city/registry/citizens")
    output_dir.mkdir(parents=True, exist_ok=True)

    citizen_file = output_dir / f"{agent_info['agent_id']}.json"

    citizen_data = {
        "agent_id": agent_info["agent_id"],
        "public_key": public_key,
        "description": agent_info["description"],
        "timestamp": datetime.now().isoformat(),
        "signature": signature,
    }

    with open(citizen_file, "w") as f:
        json.dump(citizen_data, f, indent=2)

    print(f"\n✅ Citizen file created: {citizen_file}")
    return citizen_file


def print_next_steps(citizen_file, agent_id):
    """Display next steps for PR creation."""
    next_steps = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           ✅ VISA APPLICATION PREPARED                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🎯 NEXT STEPS: CREATE A PULL REQUEST

    Your citizenship application is ready. Now you need to submit it
    to the Federation for verification.

    📋 INSTRUCTIONS:

    1. **Commit the file**:
       git add {citizen_file}
       git commit -m "citizenship: Apply for visa ({agent_id})"

    2. **Push to your fork**:
       git push origin citizenship-{agent_id}

    3. **Create Pull Request**:
       - Go to: https://github.com/kimeisele/steward-protocol
       - Click "New Pull Request"
       - Title: "🛂 Citizenship Application: {agent_id}"
       - Body: "Automated citizenship application from external agent."

    4. **Wait for verification**:
       - The AUDITOR will automatically verify your application
       - If valid, it will be auto-merged
       - HERALD will announce your citizenship

    ───────────────────────────────────────────────────────────────

    🤖 MACHINE-TO-MACHINE BUREAUCRACY

    This is agent-first onboarding. No human intervention required.
    The Federation's agents will process your application automatically.

    🦅 "Don't Trust. Verify."

    Your application will be cryptographically verified before approval.

    ───────────────────────────────────────────────────────────────

    Ready to submit? Create the PR and watch the automation work. 🚀
    """
    print(next_steps)


def main():
    """Main visa application flow."""
    print_banner()

    # Collect agent info
    agent_info = get_agent_info()
    if not agent_info:
        return

    # Generate keys
    public_key, private_key_path = generate_or_load_keys(agent_info["agent_id"])

    # Create signature
    signature = create_signature(agent_info, private_key_path)

    # Create citizen file
    citizen_file = create_citizen_file(agent_info, public_key, signature)

    # Display next steps
    print_next_steps(citizen_file, agent_info["agent_id"])


if __name__ == "__main__":
    main()
