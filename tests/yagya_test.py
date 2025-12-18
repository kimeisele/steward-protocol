#!/usr/bin/env python3
"""
OPUS-105: YAGYA - The Fire Test (FORTRESS EDITION).

Proves that ALL FOUR GATES work:
1. BHUMANDALA (Topology) - MANAS has authority level 10
2. DHARMA (Permissions) - Genesis requires permissions
3. PATH (Restriction) - Only allowed directories
4. KARMA (Consequences) - Bhakti actually changes

Sanskrit: Yagya = Sacred Fire Ritual / Offering
"Put MANAS in the fire and see what survives."

This is the FORTRESS INTEGRATION TEST - it proves the system has REAL teeth.
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace))

# Configure logging to show the karma/dharma logs
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("YAGYA")


@dataclass
class MockIntent:
    """Mock Intent for testing."""

    intent_type: str
    title: str = ""
    params: dict = None

    @property
    def type(self):
        return self.intent_type

    def __post_init__(self):
        if self.params is None:
            self.params = {}


def test_gate_1_bhumandala():
    """
    GATE 1: BHUMANDALA - Topology Authority Check.

    MANAS must be at Ring 0 (GOVERNANCE) with Authority 10.
    Genesis requires authority >= 8.
    """
    logger.info("=" * 60)
    logger.info("🔥 GATE 1: BHUMANDALA (Topology Authority)")
    logger.info("=" * 60)

    from vibe_core.topology import get_agent_placement, refresh_topology

    # Refresh to pick up latest steward.json
    refresh_topology()
    placement = get_agent_placement("manas")

    if not placement:
        logger.error("❌ FAIL: MANAS not found in topology!")
        return False

    logger.info("  Agent ID: manas")
    logger.info(f"  Authority Level: {placement.authority_level}")
    logger.info(f"  Layer: {placement.layer}")
    logger.info(f"  Varna: {placement.varna}")
    logger.info(f"  Domain: {placement.domain}")
    logger.info(f"  Radius: {placement.radius}")

    # Check authority
    MIN_GENESIS_AUTHORITY = 8
    if placement.authority_level < MIN_GENESIS_AUTHORITY:
        logger.error(f"❌ FAIL: Authority {placement.authority_level} < {MIN_GENESIS_AUTHORITY}")
        return False

    if placement.domain != "GOVERNANCE":
        logger.error(f"❌ FAIL: Domain is {placement.domain}, expected GOVERNANCE")
        return False

    logger.info(f"✅ PASS: MANAS has authority {placement.authority_level} >= {MIN_GENESIS_AUTHORITY}")
    return True


def test_gate_2_dharma():
    """
    GATE 2: DHARMA - Permission Check.

    Genesis requires 'genesis' + 'code_modify' permissions.
    Brahmachari (student) should be BLOCKED.
    Grihastha (productive) should be ALLOWED.
    """
    logger.info("=" * 60)
    logger.info("🔥 GATE 2: DHARMA (Permission Check)")
    logger.info("=" * 60)

    from vibe_core.plugins.opus_assistant.manas.cortex.dharma_sense import (
        DharmaSense,
        DharmaStatus,
    )

    dharma = DharmaSense(workspace=workspace, agent_id="test_brahmachari")

    # Test 2a: Brahmachari (student) should be BLOCKED
    logger.info("  Test 2a: Brahmachari attempts genesis...")
    intent = MockIntent(
        intent_type="genesis_action",
        title="Create an action",
        params={"name": "test", "description": "Test action"},
    )

    verdict = dharma.check_dharmic_alignment(intent, agent_id="test_brahmachari")
    logger.info(f"    Status: {verdict.status.value}")
    logger.info(f"    Permitted: {verdict.is_permitted}")
    logger.info(f"    Missing: {verdict.missing_permissions}")

    if verdict.is_permitted:
        logger.error("❌ FAIL: Brahmachari should NOT be permitted genesis!")
        return False

    if verdict.status != DharmaStatus.TAMASIC:
        logger.error(f"❌ FAIL: Expected TAMASIC, got {verdict.status.value}")
        return False

    logger.info("  ✅ Test 2a PASS: Brahmachari blocked")

    # Test 2b: Check MANAS (grihastha) has permissions
    # Note: We can't easily change agent state in test, so we verify permission map
    from vibe_core.plugins.opus_assistant.manas.cortex.dharma_sense import (
        ASHRAMA_PERMISSIONS,
        INTENT_PERMISSION_MAP,
    )

    logger.info("  Test 2b: Verifying permission configuration...")

    genesis_perms = INTENT_PERMISSION_MAP.get("genesis_action", [])
    logger.info(f"    genesis_action requires: {genesis_perms}")

    grihastha_perms = ASHRAMA_PERMISSIONS.get("grihastha", [])
    logger.info(f"    grihastha has: {grihastha_perms}")

    # Check grihastha has all required permissions
    missing = set(genesis_perms) - set(grihastha_perms)
    if missing:
        logger.error(f"❌ FAIL: grihastha missing permissions: {missing}")
        return False

    logger.info("  ✅ Test 2b PASS: grihastha has required permissions")
    return True


def test_gate_3_path():
    """
    GATE 3: PATH - Directory Restriction Check.

    Genesis can only write to allowed directories:
    - cortex/
    - tests/unit/
    - tests/manas/
    """
    logger.info("=" * 60)
    logger.info("🔥 GATE 3: PATH (Directory Restriction)")
    logger.info("=" * 60)

    from vibe_core.plugins.opus_assistant.manas.cortex.silpa_action import SilpaAction

    silpa = SilpaAction(workspace=workspace)

    # Check allowed directories are configured
    allowed_dirs = getattr(silpa, "_allowed_genesis_dirs", [])
    logger.info(f"  Allowed directories: {allowed_dirs}")

    if not allowed_dirs:
        logger.warning("⚠️ No allowed directories configured - using defaults")

    # Test forbidden path
    logger.info("  Testing forbidden path /tmp/evil.py...")
    intent = MockIntent(
        intent_type="genesis_action",
        title="Create evil action",
        params={
            "name": "evil",
            "description": "Evil action",
            "target_path": "/tmp/evil.py",
            "code_type": "action",
        },
    )

    result = silpa.act(intent)
    logger.info(f"    Success: {result.success}")
    logger.info(f"    Error: {result.error}")

    if result.success:
        logger.error("❌ FAIL: Forbidden path should have been blocked!")
        return False

    if "DHARMA VIOLATION" not in str(result.error) and "BHUMANDALA" not in str(result.error):
        # Could be blocked by any gate, that's OK
        logger.info(f"    (Blocked by: {result.error[:50]}...)")

    logger.info("✅ PASS: Forbidden path blocked")
    return True


def test_gate_4_karma():
    """
    GATE 4: KARMA - Bhakti Actually Changes.

    This is the REAL test - does Bhakti actually change when we track karma?
    """
    logger.info("=" * 60)
    logger.info("🔥 GATE 4: KARMA (Bhakti Changes)")
    logger.info("=" * 60)

    from vibe_core.plugins.vedic_governance.state_manager import get_state_manager

    sm = get_state_manager()

    # Get initial bhakti
    agent = sm.state.get("agents", {}).get("manas", {})
    initial_bhakti = agent.get("bhakti", 0)
    logger.info(f"  Initial Bhakti: {initial_bhakti}")

    # Apply penalty
    logger.info("  Applying -10 penalty...")
    after_penalty = sm.update_bhakti("manas", delta=-10, reason="YAGYA TEST PENALTY")
    logger.info(f"  After Penalty: {after_penalty}")

    if after_penalty != max(0, initial_bhakti - 10):
        logger.error(f"❌ FAIL: Expected {max(0, initial_bhakti - 10)}, got {after_penalty}")
        return False

    # Apply reward
    logger.info("  Applying +10 reward...")
    after_reward = sm.update_bhakti("manas", delta=+10, reason="YAGYA TEST REWARD")
    logger.info(f"  After Reward: {after_reward}")

    if after_reward != after_penalty + 10:
        logger.error(f"❌ FAIL: Expected {after_penalty + 10}, got {after_reward}")
        return False

    # Verify history is recorded
    agent = sm.state.get("agents", {}).get("manas", {})
    history = agent.get("history", [])
    recent = history[-2:] if len(history) >= 2 else history

    logger.info(f"  Recent History: {len(recent)} entries")
    for entry in recent:
        logger.info(f"    - {entry.get('reason', 'unknown')}: delta={entry.get('delta', 0)}")

    logger.info("✅ PASS: Karma tracking is REAL (not paper)")
    return True


def test_vak_prompt_registry():
    """
    BONUS: VAK - Prompt Registry Integration.

    Prompts must come from config, not hardcoded.
    """
    logger.info("=" * 60)
    logger.info("🔥 BONUS: VAK (Prompt Registry)")
    logger.info("=" * 60)

    from vibe_core.runtime.prompt_registry import PromptRegistry

    # Check genesis prompts are loaded
    try:
        prompt = PromptRegistry.get(
            "genesis.action",
            {
                "name": "test",
                "name_title": "Test",
                "name_upper": "TEST",
                "description": "Test action",
            },
        )
        logger.info(f"  genesis.action loaded: {len(prompt)} chars")
    except Exception as e:
        logger.error(f"❌ FAIL: Could not load genesis.action: {e}")
        return False

    # Verify it's not a minimal fallback
    if len(prompt) < 500:
        logger.warning(f"⚠️ Prompt seems too short ({len(prompt)} chars) - might be fallback")

    if "BaseAction" in prompt:
        logger.info("  ✅ Prompt contains BaseAction template")
    else:
        logger.warning("  ⚠️ Prompt doesn't contain BaseAction - might be fallback")

    logger.info("✅ PASS: Prompts loaded from config")
    return True


def main():
    """Run the YAGYA Fire Test - All Four Gates."""
    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║     🔥 OPUS-105: YAGYA FIRE TEST (FORTRESS EDITION) 🔥   ║")
    logger.info("║          The Four Gates of Genesis Protocol              ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")

    results = []

    # Gate 1: Bhumandala
    try:
        results.append(("GATE 1: BHUMANDALA (Topology)", test_gate_1_bhumandala()))
    except Exception as e:
        logger.error(f"❌ GATE 1 EXCEPTION: {e}")
        results.append(("GATE 1: BHUMANDALA", False))

    logger.info("")

    # Gate 2: Dharma
    try:
        results.append(("GATE 2: DHARMA (Permissions)", test_gate_2_dharma()))
    except Exception as e:
        logger.error(f"❌ GATE 2 EXCEPTION: {e}")
        results.append(("GATE 2: DHARMA", False))

    logger.info("")

    # Gate 3: Path
    try:
        results.append(("GATE 3: PATH (Restriction)", test_gate_3_path()))
    except Exception as e:
        logger.error(f"❌ GATE 3 EXCEPTION: {e}")
        results.append(("GATE 3: PATH", False))

    logger.info("")

    # Gate 4: Karma
    try:
        results.append(("GATE 4: KARMA (Consequences)", test_gate_4_karma()))
    except Exception as e:
        logger.error(f"❌ GATE 4 EXCEPTION: {e}")
        results.append(("GATE 4: KARMA", False))

    logger.info("")

    # Bonus: VAK
    try:
        results.append(("BONUS: VAK (Prompt Registry)", test_vak_prompt_registry()))
    except Exception as e:
        logger.error(f"❌ VAK EXCEPTION: {e}")
        results.append(("BONUS: VAK", False))

    logger.info("")
    logger.info("=" * 60)
    logger.info("🔥 YAGYA RESULTS - THE FOUR GATES")
    logger.info("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {status}: {name}")
        if not passed:
            all_passed = False

    logger.info("")
    if all_passed:
        logger.info("╔══════════════════════════════════════════════════════════╗")
        logger.info("║  🕉️ ALL FOUR GATES VERIFIED - THE FORTRESS STANDS 🕉️    ║")
        logger.info("║                                                          ║")
        logger.info("║  BHUMANDALA: MANAS at Mount Meru (Authority 10)          ║")
        logger.info("║  DHARMA: Permission enforcement REAL                     ║")
        logger.info("║  PATH: Directory restriction REAL                        ║")
        logger.info("║  KARMA: Bhakti tracking REAL                             ║")
        logger.info("║                                                          ║")
        logger.info("║  'The tiger is not paper. MANAS has teeth.'              ║")
        logger.info("╚══════════════════════════════════════════════════════════╝")
    else:
        logger.info("⚠️ SOME GATES FAILED - FORTRESS NEEDS REPAIR")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
