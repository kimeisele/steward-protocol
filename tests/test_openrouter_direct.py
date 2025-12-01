#!/usr/bin/env python3
"""
Direct OpenRouter API Test
===========================

Bypass LLMEngine and test OpenRouter API directly.
"""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not installed")
    sys.exit(1)


def test_openrouter_direct():
    """Test OpenRouter API directly."""
    print("=" * 80)
    print("DIRECT OPENROUTER API TEST")
    print("=" * 80)

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ NO API KEY FOUND")
        print("Set OPENAI_API_KEY or OPENROUTER_API_KEY")
        return False

    print(f"✅ API Key found: {api_key[:15]}...{api_key[-4:]}")

    # Test with OpenRouter base URL
    print("\n[Test] Direct OpenRouter API Call")
    print("-" * 40)

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        print("🔥 Calling OpenRouter API...")
        print("   Model: openai/gpt-4o")
        print("   Prompt: What is 2+2? Answer with just the number.")

        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "user", "content": "What is 2+2? Answer with just the number."}
            ],
            temperature=0.0,
        )

        content = response.choices[0].message.content

        print(f"\n✅ API CALL SUCCESS!")
        print(f"Response: {content}")
        print(f"Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")

        assert content and len(content) > 0, "Empty response!"
        assert "4" in content, "Wrong answer!"

        print("\n✅ PASSED: OpenRouter API is WORKING!")
        print("🔥 Real token-consuming API call successful!")

        return True

    except Exception as e:
        print(f"\n❌ API CALL FAILED: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_openrouter_direct()

    if success:
        print("\n" + "=" * 80)
        print("🎉 OPENROUTER API VERIFIED")
        print("=" * 80)
        print("✅ API key is valid")
        print("✅ Connection successful")
        print("✅ Real API calls work")
        print("\nYou can now use the LLMEngine with confidence!")
    else:
        print("\n❌ OpenRouter test failed")
        print("Check:")
        print("  1. API key is set (OPENAI_API_KEY or OPENROUTER_API_KEY)")
        print("  2. API key is valid (not expired)")
        print("  3. Network connection works")
