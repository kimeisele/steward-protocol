import os
import sys

# --- CONFIG: OPENROUTER BRIDGE ---
if os.getenv("OPENROUTER_API_KEY"):
    print("🌍 SYSTEM: Using OpenRouter Bridge")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

try:
    # Import Engine from vibe_core (actual module from vibe-agency repo)
    from vibe_core.kernel import VibeKernel
    print("✅ ENGINE: Vibe-Core loaded successfully.")
except ImportError as e:
    print(f"❌ ERROR: Vibe-Core not installed.")
    print(f"Details: {e}")
    print("Run: pip install -r examples/herald/requirements.txt")
    sys.exit(1)

def run():
    print("🤖 HERALD BOOT SEQUENCE...")

    # Init Brain using Vibe-Core Kernel
    try:
        kernel = VibeKernel()
        print(f"🧠 KERNEL ONLINE")
        print(f"📡 Connection: {os.environ.get('OPENAI_BASE_URL', 'Direct OpenAI')}")
        print("✅ HERALD READY FOR COMMANDS")
    except Exception as e:
        print(f"⚠️  Kernel init returned: {e}")
        print("✅ HERALD READY FOR COMMANDS (degraded mode)")

if __name__ == "__main__":
    run()
