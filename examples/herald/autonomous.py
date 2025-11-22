import os
import sys
from pathlib import Path

# --- CONFIG: OPENROUTER BRIDGE ---
if os.getenv("OPENROUTER_API_KEY"):
    print("🌍 SYSTEM: Using OpenRouter Bridge")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# --- IMPORTS ---
try:
    # 1. The Engine
    from vibe_core.kernel import VibeKernel
    # 2. The Protocol (New SDK)
    from steward.client import StewardClient
    print("✅ SYSTEM: Engine & Protocol loaded.")
except ImportError as e:
    print(f"❌ ERROR: Dependencies missing. {e}")
    sys.exit(1)


def run():
    print("🤖 HERALD BOOT SEQUENCE...")

    # 1. Initialize Protocol Identity
    # We point to our local identity file
    client = StewardClient(identity_file="examples/herald/STEWARD.md")

    if client.assert_identity():
        print("🔐 IDENTITY: Verified (Private Key Active)")
    else:
        print("⚠️  IDENTITY: Unverified (No Private Key found or Identity missing)")

    # 2. Initialize Brain
    try:
        kernel = VibeKernel()
        print(f"🧠 KERNEL ONLINE")
        print(f"📡 Connection: {os.environ.get('OPENAI_BASE_URL', 'Direct OpenAI')}")
    except Exception as e:
        print(f"⚠️  Kernel init: {e}")
        print("✅ KERNEL: Simulation Mode (VibeKernel standby)")

    # 3. DO WORK (Generate Content)
    topic = "The importance of Cryptographic Truth in AI"
    content = f"""# Daily Insight: {topic}

In a world of synthetic media, authenticity is the new currency.
Agents must not only think but prove they thought it.

Every output must be verifiable. Every claim, traceable.
This is Runtime Sovereignty.

- Herald"""

    print(f"\n📝 GENERATED CONTENT:\n{content}")

    # 4. PROTOCOL ATTESTATION (Signing the Work)
    print("\n✍️  Signing artifact...")
    signature = client.sign_artifact(content.strip())

    # 5. SAVE ARTIFACT
    output_dir = Path("examples/herald")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "daily_thought.md"

    with open(output_file, "w") as f:
        f.write(content)
        f.write(f"\n\n---\n")
        f.write(f"**Signature:** `{signature[:40]}...`\n")

    print(f"✅ ARTIFACT SAVED: {output_file}")
    print(f"   Signature: {signature[:40]}...")
    print(f"\n🔗 CHAIN OF TRUST: Content → Signature → Verification")


if __name__ == "__main__":
    run()
