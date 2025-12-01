#!/usr/bin/env python3
"""
Test Ambassador Question Answering
===================================

This test proves that the Ambassador agent can now answer questions
with either LLM-powered responses or helpful static fallbacks.

Success criteria:
1. Ambassador accepts questions and returns helpful answers
2. Fallback mode provides useful welcome information
3. No "not_implemented" errors
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_city.registry.ambassador.cartridge_main import AmbassadorCartridge
from vibe_core import Task


async def test_ambassador_question_answering():
    """Test that Ambassador can answer questions."""
    print("=" * 80)
    print("AMBASSADOR QUESTION ANSWERING TEST")
    print("=" * 80)

    # Initialize Ambassador
    ambassador = AmbassadorCartridge()
    print("✅ Ambassador initialized")

    # Test 1: Basic question
    print("\n[Test 1] Basic Question")
    print("-" * 40)

    question = "What is Agent City?"
    task = Task(
        agent_id="ambassador",
        payload={
            "action": "answer_question",
            "question": question,
            "user_id": "test_user_001",
        },
    )

    result = await ambassador.process(task)

    print(f"Status: {result.get('status')}")
    print(f"Method: {result.get('method')}")
    print(f"\nQuestion: {result.get('question')}")
    print(f"\nAnswer preview:")
    answer = result.get('answer', '')
    print(answer[:300] + "..." if len(answer) > 300 else answer)

    # Verify no error
    assert result.get("status") != "not_implemented", "❌ FAILED: Still returning not_implemented!"
    assert result.get("status") == "answered", f"❌ FAILED: Wrong status: {result.get('status')}"
    assert "answer" in result, "❌ FAILED: No answer field in response!"
    assert len(result["answer"]) > 0, "❌ FAILED: Empty answer!"

    # Verify helpful content in answer
    answer_lower = result["answer"].lower()
    assert "agent city" in answer_lower or "ambassador" in answer_lower, "❌ FAILED: Answer not relevant!"

    print("✅ PASSED: Ambassador answered the question")

    # Test 2: Verify conversation tracking
    print("\n[Test 2] Conversation Tracking")
    print("-" * 40)

    print(f"Active conversations: {len(ambassador.active_conversations)}")
    assert len(ambassador.active_conversations) > 0, "❌ FAILED: No conversation tracked!"
    print("✅ PASSED: Conversations are being tracked")

    # Test 3: Multiple questions
    print("\n[Test 3] Multiple Questions")
    print("-" * 40)

    questions = [
        "How do I get started?",
        "What agents are available?",
        "Tell me about governance",
    ]

    for i, q in enumerate(questions, 2):
        task = Task(
            agent_id="ambassador",
            payload={
                "action": "answer_question",
                "question": q,
                "user_id": f"test_user_{i:03d}",
            },
        )

        result = await ambassador.process(task)
        print(f"  Q{i}: {q[:40]}... → {result.get('status')}")

        assert result.get("status") == "answered", f"❌ FAILED: Question {i} not answered!"

    print("✅ PASSED: Ambassador handled multiple questions")

    # Test 4: Check if fallback mode is working
    print("\n[Test 4] Fallback Mode Check")
    print("-" * 40)

    if result.get("method") == "static_fallback":
        print("🔵 Ambassador is using static fallback (no LLM)")
        # Verify the welcome message contains expected content
        answer = result.get("answer", "")
        assert "Agent City" in answer, "❌ FAILED: Welcome message missing Agent City info!"
        assert "Layer 0" in answer or "Foundation" in answer, "❌ FAILED: Missing architecture info!"
        assert "Quick Start" in answer or "Documentation" in answer, "❌ FAILED: Missing help info!"
        print("✅ Static fallback provides comprehensive welcome message")
    elif result.get("method") == "llm_powered":
        print("🧠 Ambassador is using LLM-powered responses")
        print("✅ LLM integration working")
    else:
        print(f"⚠️  Unknown method: {result.get('method')}")

    # Final summary
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED - AMBASSADOR IS FUNCTIONAL")
    print("=" * 80)
    print("\nSUMMARY:")
    print("✅ Ambassador accepts and answers questions")
    print("✅ No more 'not_implemented' errors")
    print("✅ Conversation tracking works")
    print("✅ Multiple questions handled successfully")
    print(f"✅ Response method: {result.get('method', 'unknown')}")
    print("\n🤝 The Ambassador is now ready for community engagement!")


if __name__ == "__main__":
    asyncio.run(test_ambassador_question_answering())
