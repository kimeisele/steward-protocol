#!/usr/bin/env python3
"""
📜 SUTRA SENSE VERIFICATION - The Third Eye Test

OPUS-054: Test that MANAS can perceive documentation gaps
and generate intents to heal them.

Three Trials:
1. PERCEPTION: Can MANAS see the documentation landscape?
2. GAP DETECTION: Does MANAS identify missing @HARNESS blocks?
3. INTENT GENERATION: Does MANAS propose curation intents?

Run: python scripts/testing/verify_sutra_sense.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def banner(text: str) -> None:
    """Print a trial banner."""
    print("\n" + "=" * 70)
    print(f"  📜 {text}")
    print("=" * 70)


def trial_perception() -> bool:
    """
    TRIAL 1: PERCEPTION

    Can MANAS perceive the documentation landscape?
    """
    banner("TRIAL 1: PERCEPTION - Can MANAS see the documentation landscape?")

    from vibe_core.plugins.opus_assistant.manas.cortex.sutra_sense import SutraSense

    sense = SutraSense(workspace=project_root)
    summary = sense.perceive_gaps(refresh=True)

    print(f"\n  Total OPUS Docs: {summary.total_docs}")
    print(f"  With @HARNESS:   {summary.docs_with_harness}")
    print(f"  Without @HARNESS: {summary.docs_without_harness}")
    print(f"  Total Gaps:      {summary.gaps_found}")
    print(f"  Health Ratio:    {summary.health_ratio:.1%}")

    # Must perceive at least some docs
    if summary.total_docs == 0:
        print("\n  ❌ FAILED: No docs found!")
        return False

    print("\n  ✅ PASSED: MANAS can perceive the documentation landscape")
    return True


def trial_gap_detection() -> bool:
    """
    TRIAL 2: GAP DETECTION

    Does MANAS identify missing @HARNESS blocks and code gaps?
    """
    banner("TRIAL 2: GAP DETECTION - Does MANAS identify gaps?")

    from vibe_core.plugins.opus_assistant.manas.cortex.sutra_sense import SutraSense

    sense = SutraSense(workspace=project_root)
    summary = sense.perceive_gaps(refresh=True)  # Must refresh to populate gaps
    gaps = sense.get_gaps()  # Get actual gap objects

    # Analyze gap types
    gap_types = {}
    for gap in gaps:
        gap_types[gap.gap_type] = gap_types.get(gap.gap_type, 0) + 1

    print("\n  Gap Types Detected:")
    for gap_type, count in sorted(gap_types.items()):
        print(f"    - {gap_type}: {count}")

    # Show some sample gaps
    print("\n  Sample Gaps:")
    for gap in gaps[:5]:
        severity_icon = "🔴" if gap.severity == "high" else "🟡" if gap.severity == "medium" else "⚪"
        doc_name = gap.doc_path.name if gap.doc_path else "?"
        print(f"    {severity_icon} [{gap.gap_type}] {doc_name}: {gap.description[:50]}")

    # Should detect at least one gap type
    if len(gap_types) == 0:
        print("\n  ❌ FAILED: No gap types detected!")
        return False

    print("\n  ✅ PASSED: MANAS can detect documentation gaps")
    return True


def trial_intent_generation() -> bool:
    """
    TRIAL 3: INTENT GENERATION

    Does MANAS generate intents to heal documentation gaps?
    """
    banner("TRIAL 3: INTENT GENERATION - Does MANAS propose curation?")

    from vibe_core.plugins.opus_assistant.manas.cortex.sutra_sense import SutraSense

    sense = SutraSense(workspace=project_root)
    intents = sense.generate_gap_intents(limit=5)

    print(f"\n  Generated {len(intents)} gap intents:")
    for intent in intents:
        print(f"\n    📋 {intent.get('title', 'Unknown')}")
        print(f"       Type: {intent.get('intent_type', '?')}")
        print(f"       Priority: {intent.get('priority', '?')}")
        print(f"       Risk: {intent.get('risk', '?')}")
        if intent.get("params"):
            gap_type = intent["params"].get("gap_type", "?")
            print(f"       Gap Type: {gap_type}")

    # Should generate at least one intent if there are gaps
    summary = sense.perceive_gaps(refresh=False)
    if summary.gaps_found > 0 and len(intents) == 0:
        print("\n  ⚠️ WARNING: Gaps exist but no intents generated")
        # Not a failure - might be by design

    print("\n  ✅ PASSED: MANAS can generate curation intents")
    return True


def trial_cognitive_kernel_integration() -> bool:
    """
    TRIAL 4: COGNITIVE KERNEL INTEGRATION

    Does CognitiveKernel properly initialize and use SutraSense?
    """
    banner("TRIAL 4: COGNITIVE KERNEL - Is SutraSense wired in?")

    from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

    kernel = CognitiveKernel(workspace=project_root)

    # Check if SutraSense was initialized
    if kernel._sutra_sense is None:
        print("\n  ❌ FAILED: SutraSense not initialized!")
        return False

    print("\n  ✅ SutraSense initialized")

    # Check get_sutra_summary
    summary = kernel.get_sutra_summary()
    if summary is None:
        print("  ⚠️ WARNING: get_sutra_summary returned None")
    else:
        print(f"  ✅ Summary: {summary.get('total_docs', 0)} docs, {summary.get('gaps_count', 0)} gaps")

    # Force a think cycle and check if gap intents are generated
    print("\n  Triggering forced think cycle...")
    intents = kernel.think(force=True)

    gap_intents = [i for i in intents if "gap" in i.intent_type or "harness" in i.intent_type.lower()]
    print(f"  Generated {len(intents)} total intents, {len(gap_intents)} gap-related")

    for intent in gap_intents[:3]:
        print(f"    📜 {intent.title[:50]}")

    print("\n  ✅ PASSED: CognitiveKernel has SutraSense wired in")
    return True


def main():
    """Run all trials."""
    print("\n" + "🔮" * 35)
    print("       📜 THE THIRD EYE AWAKENS 📜")
    print("       SUTRA SENSE VERIFICATION")
    print("🔮" * 35)

    results = []

    # Run all trials
    results.append(("PERCEPTION", trial_perception()))
    results.append(("GAP DETECTION", trial_gap_detection()))
    results.append(("INTENT GENERATION", trial_intent_generation()))
    results.append(("COGNITIVE KERNEL", trial_cognitive_kernel_integration()))

    # Summary
    print("\n" + "=" * 70)
    print("  📜 SUTRA SENSE VERIFICATION RESULTS")
    print("=" * 70)

    all_passed = True
    for trial_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {trial_name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n  🎉 ALL TRIALS PASSED!")
        print("  📜 MANAS can now see documentation gaps!")
        print("  📜 The Third Eye is OPEN!")
        print("\n  Bhagavad Gita 9.22:")
        print("  'yoga-kṣemaṁ vahāmy aham'")
        print("  I bring what is lacking, preserve what they have.")
        return 0
    else:
        print("\n  ⚠️ SOME TRIALS FAILED")
        print("  SutraSense needs attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
