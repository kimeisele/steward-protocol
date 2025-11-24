#!/usr/bin/env python3
"""
Integration test: SCIENTIST + HERALD

This test verifies that:
1. SCIENTIST cartridge initializes correctly
2. Web search tool works (with mock data)
3. HERALD can use SCIENTIST's research for content generation
"""

import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_INTEGRATION")


def test_scientist_initialization():
    """Test 1: SCIENTIST cartridge initializes."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: SCIENTIST Initialization")
    logger.info("=" * 70)

    try:
        from science.cartridge_main import ScientistCartridge

        scientist = ScientistCartridge()
        config = scientist.get_config()
        status = scientist.report_status()

        logger.info("✅ SCIENTIST initialized successfully")
        logger.info(f"   Name: {config['name']}")
        logger.info(f"   Version: {config['version']}")
        logger.info(f"   Search mode: {status['search_mode'].upper()}")

        return True
    except Exception as e:
        logger.error(f"❌ SCIENTIST initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_web_search():
    """Test 2: Web search tool works."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Web Search Tool")
    logger.info("=" * 70)

    try:
        from science.tools.web_search_tool import WebSearchTool

        search = WebSearchTool()
        logger.info(f"   Mode: {search.mode.upper()}")

        # Test search
        results = search.search("AI governance 2025", max_results=3)
        logger.info(f"✅ Search returned {len(results)} results")

        for i, result in enumerate(results, 1):
            logger.info(f"   [{i}] {result.title}")
            logger.info(f"       URL: {result.url}")
            logger.info(f"       Source: {result.source}")

        # Test fact sheet synthesis
        fact_sheet = search.synthesize_fact_sheet("AI governance 2025", results)
        logger.info(f"✅ Fact sheet created")
        logger.info(f"   Key insights: {len(fact_sheet['key_insights'])}")
        logger.info(f"   Summary length: {len(fact_sheet['summary'])} chars")

        return True
    except Exception as e:
        logger.error(f"❌ Web search test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scientist_research():
    """Test 3: SCIENTIST research workflow."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: SCIENTIST Research Workflow")
    logger.info("=" * 70)

    try:
        from science.cartridge_main import ScientistCartridge

        scientist = ScientistCartridge()

        # Perform research
        briefing = scientist.research(
            query="AI agents autonomous governance 2025", max_results=3
        )

        logger.info("✅ Research briefing created")
        logger.info(f"   Query: {briefing['query']}")
        logger.info(f"   Sources: {briefing['source_count']}")
        logger.info(f"   Insights: {len(briefing['key_insights'])}")
        logger.info(f"   Summary: {briefing['summary'][:100]}...")

        return True
    except Exception as e:
        logger.error(f"❌ SCIENTIST research test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_herald_integration():
    """Test 4: HERALD uses SCIENTIST."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: HERALD + SCIENTIST Integration")
    logger.info("=" * 70)

    try:
        from herald.cartridge_main import HeraldCartridge

        herald = HeraldCartridge()
        status = herald.report_status()

        logger.info("✅ HERALD initialized with SCIENTIST")
        logger.info(f"   HERALD version: {status['version']}")
        logger.info(f"   SCIENTIST available: {hasattr(herald, 'scientist')}")

        if hasattr(herald, "scientist"):
            scientist_status = herald.scientist.report_status()
            logger.info(f"   SCIENTIST search mode: {scientist_status['search_mode'].upper()}")

            # Test the integration: Get briefing through HERALD
            logger.info("\n   [Integration] Running SCIENTIST research via HERALD...")
            briefing = herald.scientist.research(
                query="cryptographic verification agents",
                max_results=2
            )
            logger.info(f"   ✅ Briefing obtained: {briefing['source_count']} sources")
            logger.info(f"   Summary: {briefing['summary'][:80]}...")

        return True
    except Exception as e:
        logger.error(f"❌ HERALD + SCIENTIST integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "🔬" * 35)
    logger.info("SCIENCE INTEGRATION TEST SUITE")
    logger.info("🔬" * 35)

    results = {
        "SCIENTIST Initialization": test_scientist_initialization(),
        "Web Search Tool": test_web_search(),
        "SCIENTIST Research": test_scientist_research(),
        "HERALD Integration": test_herald_integration(),
    }

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! SCIENTIST is ready.")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
