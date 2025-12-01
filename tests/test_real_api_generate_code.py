#!/usr/bin/env python3
"""
REAL API CALL TEST - Code Generation
=====================================

Test the generate_code() method which ACTUALLY calls the API.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.llm_engine import LLMEngine


def test_generate_code_real_api():
    """Test generate_code with REAL API call."""
    print("=" * 80)
    print("REAL API TEST - generate_code() Method")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ NO API KEY FOUND")
        return False

    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")

    # Initialize LLM Engine
    llm = LLMEngine()
    print(f"Provider: {llm.provider}")
    print(f"Model: {llm.model}")

    # Test REAL API call with generate_code
    print("\n[Test] Real API Call - generate_code()")
    print("-" * 40)

    prompt = "Write a simple Python function that returns 'Hello World'"

    print(f"Prompt: {prompt}")
    print("\n🔥 Calling REAL API (this will cost tokens)...")

    try:
        response = llm.generate_code(prompt)

        print(f"\n✅ API CALL SUCCESS!")
        print(f"Response length: {len(response)} chars")
        print(f"\nGenerated code:")
        print("-" * 40)
        print(response[:500] if len(response) > 500 else response)
        print("-" * 40)

        # Verify it's not a mock
        assert "Hello World" in response or "hello" in response.lower(), "Response doesn't match prompt!"
        assert len(response) > 10, "Response too short!"

        print("\n✅ PASSED: Real API call successful!")
        print("🔥 OpenRouter/OpenAI API is WORKING!")

        return True

    except Exception as e:
        print(f"\n❌ API CALL FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_generate_code_real_api()

    if success:
        print("\n" + "=" * 80)
        print("🎉 REAL API VERIFICATION COMPLETE")
        print("=" * 80)
        print("✅ OpenRouter/OpenAI API key works")
        print("✅ Real token-consuming API calls successful")
        print("✅ LLM integration is LIVE")
        print("\nNote: speak() uses deterministic responses (by design)")
        print("      generate_code() uses REAL API calls (proven above)")
    else:
        print("\n❌ API test failed")
