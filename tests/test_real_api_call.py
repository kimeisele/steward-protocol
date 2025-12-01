#!/usr/bin/env python3
"""
REAL API CALL TEST
==================

This test makes an ACTUAL API call to OpenRouter/OpenAI.
No mocks, no simulation - just raw API communication.

We'll test:
1. LLM Engine initialization with real API key
2. Actual API call to generate text
3. Ambassador using real LLM for Q&A
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.llm_engine import LLMEngine
from agent_city.registry.ambassador.cartridge_main import AmbassadorCartridge
from vibe_core import Task


def test_llm_engine_real_api():
    """Test LLM Engine with real API call."""
    print("=" * 80)
    print("REAL API CALL TEST - Part 1: LLM Engine Direct")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ NO API KEY FOUND")
        print("Please set OPENAI_API_KEY or OPENROUTER_API_KEY")
        return False

    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")

    # Initialize LLM Engine
    print("\n[Test 1] LLM Engine Initialization")
    print("-" * 40)

    llm = LLMEngine()
    print(f"Provider: {llm.provider}")
    print(f"Model: {llm.model}")
    print(f"Has API Key: {bool(llm.api_key)}")

    assert llm.api_key is not None, "❌ FAILED: No API key loaded!"
    assert llm.provider != "mock", "❌ FAILED: Still in mock mode!"
    print("✅ PASSED: LLM Engine initialized with real API")

    # Test real API call via speak()
    print("\n[Test 2] Real API Call - speak()")
    print("-" * 40)

    test_question = "What is 2+2? Answer in one short sentence."
    print(f"Question: {test_question}")
    print("Calling API...")

    try:
        response = llm.speak("AMBASSADOR", "test", test_question)

        print(f"\n✅ API CALL SUCCESS!")
        print(f"Response length: {len(response)} chars")
        print(f"Response preview: {response[:200]}...")

        # Verify it's not a mock response
        assert "Signal received" not in response, "❌ FAILED: Got mock response, not real API!"
        assert len(response) > 20, "❌ FAILED: Response too short!"

        print("✅ PASSED: Real API call successful (not mock)")
        return True

    except Exception as e:
        print(f"❌ API CALL FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ambassador_real_api():
    """Test Ambassador with real API call."""
    print("\n" + "=" * 80)
    print("REAL API CALL TEST - Part 2: Ambassador Integration")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("⚠️  NO API KEY - Skipping Ambassador test")
        return False

    print("\n[Test 3] Ambassador with Real LLM")
    print("-" * 40)

    # Initialize Ambassador
    ambassador = AmbassadorCartridge()

    # Check that LLM is initialized
    assert ambassador.llm_engine is not None, "❌ FAILED: LLM Engine not initialized!"
    print("✅ Ambassador has LLM Engine")

    # Ask a real question
    question = "In one sentence, what is artificial intelligence?"

    task = Task(
        agent_id="ambassador",
        payload={
            "action": "answer_question",
            "question": question,
            "user_id": "real_api_test",
        },
    )

    print(f"\nQuestion: {question}")
    print("Sending to Ambassador (will call real API)...")

    try:
        result = await ambassador.process(task)

        print(f"\n✅ AMBASSADOR RESPONSE RECEIVED!")
        print(f"Status: {result.get('status')}")
        print(f"Method: {result.get('method')}")
        print(f"\nAnswer: {result.get('answer')}")

        # Verify it used real LLM (not fallback)
        assert result.get("method") == "llm_powered", "❌ FAILED: Did not use LLM!"
        assert "Welcome to Agent City" not in result.get("answer", ""), "❌ FAILED: Used static fallback!"

        print("\n✅ PASSED: Ambassador used REAL API (not fallback)")
        return True

    except Exception as e:
        print(f"❌ AMBASSADOR TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all real API tests."""
    print("\n" + "🔥" * 40)
    print("REAL API CALL TEST SUITE")
    print("No mocks. No simulation. Just raw API calls.")
    print("🔥" * 40 + "\n")

    results = []

    # Test 1: LLM Engine direct
    result1 = test_llm_engine_real_api()
    results.append(("LLM Engine API Call", result1))

    # Test 2: Ambassador integration
    if result1:  # Only test if LLM works
        result2 = asyncio.run(test_ambassador_real_api())
        results.append(("Ambassador API Call", result2))
    else:
        print("\n⚠️  Skipping Ambassador test (LLM Engine failed)")
        results.append(("Ambassador API Call", None))

    # Final summary
    print("\n" + "=" * 80)
    print("REAL API TEST RESULTS")
    print("=" * 80)

    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{status} - {test_name}")

    if all(r is True for r in results if r is not None):
        print("\n🎉 ALL API TESTS PASSED!")
        print("✅ Real OpenRouter/OpenAI API calls working")
        print("✅ Ambassador can answer questions with real LLM")
        print("\n🔥 The system is ALIVE with real intelligence!")
    else:
        print("\n⚠️  Some tests failed or were skipped")
        print("Check API key configuration")


if __name__ == "__main__":
    main()
