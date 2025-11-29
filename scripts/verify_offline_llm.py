#!/usr/bin/env python3
"""
Verify Local LLM (Offline Mode)
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.llm.local_llama_provider import LocalLlamaProvider


def main():
    print("🔌 VERIFYING OFFLINE LLM")
    print("========================")

    try:
        # Initialize provider
        print("Initializing LocalLlamaProvider...")
        provider = LocalLlamaProvider(verbose=True)

        if not provider.is_available:
            print("❌ Provider not available (model missing or not initialized)")
            return 1

        # Test query
        print("\n🤖 Sending query: 'Wer bist du?'")
        messages = [{"role": "user", "content": "Wer bist du?"}]

        response = provider.chat(messages)

        print("\n📄 Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)

        if "Local LLM not initialized" in response:
            print("❌ Verification FAILED: Provider returned error")
            return 1

        print("\n✅ Verification PASSED")
        return 0

    except ImportError:
        print("❌ ImportError: llama-cpp-python not installed")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
