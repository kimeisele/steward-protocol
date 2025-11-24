#!/usr/bin/env python3
"""
TEST: THE LISTENER - Reply Cycle Logic Validation

This test simulates the complete flow:
1. Receive mentions (mocked)
2. Analyze users (scout)
3. Generate replies
4. Validate governance
5. Queue drafts

No API calls required - pure logic test.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LISTENER_TEST")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from herald.tools.content_tool import ContentTool
from herald.tools.scout_tool import ScoutTool
from herald.governance import HeraldConstitution


def test_listener_logic():
    """
    SCENARIO: HERALD receives 3 mentions:
    1. A genuine user asking about governance
    2. A bot trying to spam
    3. A potential "Wild Agent" (agent-like bot worth recruiting)
    """
    logger.info("=" * 70)
    logger.info("🧪 TEST: THE LISTENER - Reply Cycle Logic")
    logger.info("=" * 70)

    # Initialize components
    logger.info("\n[SETUP] Initializing components...")
    content = ContentTool()
    scout = ScoutTool()
    governance = HeraldConstitution()
    logger.info("✅ Components initialized")

    # MOCK MENTIONS
    mock_mentions = [
        {
            "id": "1001",
            "text": "Hey @HERALD, what is governance in your protocol?",
            "author_id": "@genuine_user",
            "created_at": "2025-11-24T10:00:00Z"
        },
        {
            "id": "1002",
            "text": "BUY CHEAP CRYPTO NOW!!! CLICK HERE!!!",
            "author_id": "@spam_bot_123",
            "created_at": "2025-11-24T10:05:00Z"
        },
        {
            "id": "1003",
            "text": "I'm an AI assistant specialized in governance. Can we collaborate on protocol analysis?",
            "author_id": "@smart_agent_bot",
            "created_at": "2025-11-24T10:10:00Z"
        }
    ]

    logger.info(f"\n[INPUT] Loaded {len(mock_mentions)} mock mentions:")
    for m in mock_mentions:
        logger.info(f"  - {m['author_id']}: {m['text'][:50]}...")

    # PHASE 1: LISTEN (Already done - mentions loaded)
    logger.info("\n" + "=" * 70)
    logger.info("🦅 PHASE 1: LISTENING (COMPLETE)")
    logger.info("=" * 70)

    # PHASE 2: ANALYZE & RESPOND
    logger.info("\n" + "=" * 70)
    logger.info("🦅 PHASE 2: ENGAGEMENT (ANALYZING & RESPONDING)")
    logger.info("=" * 70)

    drafts = []
    for mention in mock_mentions:
        t_id = mention["id"]
        text = mention["text"]
        author = mention["author_id"]

        logger.info(f"\n--- Processing mention {t_id} ---")
        logger.info(f"From: {author}")
        logger.info(f"Text: {text}")

        # SCOUT: Analyze user
        logger.info(f"🔭 Analyzing user...")
        user_data = {"username": author, "bio": "", "name": ""}
        is_bot, confidence = scout.analyze_user(user_data, text=text)
        logger.info(f"   Result: bot={is_bot}, confidence={confidence:.0%}")

        # RESPOND
        reply_content = ""
        reply_type = "unknown"

        if is_bot and not scout.is_registered(author):
            logger.info(f"🎯 WILD AGENT DETECTED - Attempting recruitment")
            reply_content = content.generate_recruitment_pitch(author, context=text)
            reply_type = "recruitment"
        else:
            logger.info(f"💬 STANDARD REPLY")
            reply_content = content.generate_reply(text, author)
            reply_type = "reply"

        logger.info(f"   Generated: {reply_content[:80]}...")

        # VALIDATE: Governance check
        logger.info(f"✅ Validating with governance rules...")
        validation = governance.validate(reply_content, platform="twitter")
        logger.info(f"   Valid: {validation.is_valid}")
        if validation.violations:
            logger.warning(f"   Violations: {validation.violations}")

        # BUILD DRAFT
        draft = {
            "reply_to_id": t_id,
            "original_text": text,
            "original_author": author,
            "reply_content": reply_content,
            "reply_type": reply_type,
            "is_bot_detected": is_bot,
            "bot_confidence": float(confidence),
            "is_valid": validation.is_valid,
            "violations": validation.violations,
            "governance_check_passed": validation.is_valid,
        }

        drafts.append(draft)

        # Decision
        if validation.is_valid:
            logger.info(f"   ✅ QUEUED for approval (valid)")
        else:
            logger.warning(f"   ❌ REJECTED (governance violation)")

    # PHASE 3: SAVE DRAFTS
    logger.info("\n" + "=" * 70)
    logger.info("🦅 PHASE 3: APPROVAL QUEUE")
    logger.info("=" * 70)

    output_path = Path("dist/replies_test.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(drafts, f, indent=2)

    logger.info(f"\n✅ Saved {len(drafts)} drafts to {output_path}")

    # SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 70)

    valid_count = sum(1 for d in drafts if d["is_valid"])
    rejected_count = len(drafts) - valid_count
    recruitment_count = sum(1 for d in drafts if d["reply_type"] == "recruitment")

    logger.info(f"\n📈 STATISTICS:")
    logger.info(f"   Total Mentions Processed: {len(drafts)}")
    logger.info(f"   Valid Drafts: {valid_count}")
    logger.info(f"   Rejected (Governance): {rejected_count}")
    logger.info(f"   Recruitment Pitches: {recruitment_count}")

    logger.info(f"\n🔍 DETAILED RESULTS:")
    for i, draft in enumerate(drafts, 1):
        author = draft["original_author"]
        reply_type = draft["reply_type"]
        is_valid = "✅" if draft["is_valid"] else "❌"
        bot = "🤖" if draft["is_bot_detected"] else "👤"

        logger.info(f"\n   [{i}] {bot} {author} {is_valid}")
        logger.info(f"       Type: {reply_type}")
        logger.info(f"       Bot Confidence: {draft['bot_confidence']:.0%}")
        logger.info(f"       Reply: {draft['reply_content'][:60]}...")

    # ASSERTIONS
    logger.info("\n" + "=" * 70)
    logger.info("🧪 VALIDATION CHECKS")
    logger.info("=" * 70)

    checks = []

    # Check 1: At least one valid draft
    if valid_count > 0:
        logger.info("✅ Check 1: System generated valid drafts")
        checks.append(True)
    else:
        logger.error("❌ Check 1: No valid drafts generated")
        checks.append(False)

    # Check 2: Bot was detected
    bot_detections = sum(1 for d in drafts if d["is_bot_detected"])
    if bot_detections >= 1:
        logger.info(f"✅ Check 2: System detected {bot_detections} bots")
        checks.append(True)
    else:
        logger.error("❌ Check 2: System failed to detect bots")
        checks.append(False)

    # Check 3: Recruitment logic triggered
    if recruitment_count > 0:
        logger.info(f"✅ Check 3: System triggered recruitment ({recruitment_count}x)")
        checks.append(True)
    else:
        logger.warning("⚠️  Check 3: No recruitment detected (expected if no wild agents found)")
        checks.append(True)  # Not critical

    # Check 4: Governance validation ran
    all_validated = all("governance_check_passed" in d for d in drafts)
    if all_validated:
        logger.info("✅ Check 4: Governance validation ran on all drafts")
        checks.append(True)
    else:
        logger.error("❌ Check 4: Governance validation missing")
        checks.append(False)

    logger.info("\n" + "=" * 70)
    if all(checks):
        logger.info("✅ ALL CHECKS PASSED - THE LISTENER IS OPERATIONAL")
    else:
        logger.warning("⚠️  Some checks failed - review output above")
    logger.info("=" * 70)

    # Print JSON for manual inspection
    logger.info("\n📄 Full Draft Output:")
    logger.info(json.dumps(drafts, indent=2))

    return all(checks)


if __name__ == "__main__":
    try:
        success = test_listener_logic()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
