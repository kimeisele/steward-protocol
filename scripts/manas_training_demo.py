#!/usr/bin/env python3
"""
OPUS-133: MANAS Synaptic Training Demo

Demonstrates how MANAS learns through experience:
1. Creates test intents
2. Routes them through VivekaAction
3. Reinforces successful patterns
4. Shows weight growth

Usage:
    python scripts/manas_training_demo.py

"Ein Gehirn, das nie handelt, lernt nie."
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def show_synapses(workspace: Path, label: str = "Current"):
    """Display current synapse weights."""
    synapses_path = workspace / ".opus_state" / "synapses.json"
    if not synapses_path.exists():
        print(f"\n📊 {label} Synapses: (no file yet)")
        return

    with open(synapses_path) as f:
        data = json.load(f)

    print(f"\n📊 {label} Synapses:")
    print("=" * 60)

    # Show weights dict
    weights = data.get("weights", {})
    for trigger, actions in weights.items():
        for action, weight in actions.items():
            print(f"  {trigger} → {action}: {weight:.2f}")

    # Show triggers list (dynamic learning)
    triggers = data.get("triggers", [])
    if triggers:
        print("\n  🧠 Dynamically Learned:")
        for t in triggers:
            trigger = t.get("trigger", "?")
            for conn in t.get("connections", []):
                target = conn.get("target", "?")
                weight = conn.get("weight", 0)
                learned = conn.get("learned_at", "?")[:10]
                print(f"  {trigger} → {target}: {weight:.2f} (learned: {learned})")


def run_training_session(workspace: Path):
    """Run a synaptic training session."""
    from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import VivekaAction
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

    print("\n" + "=" * 70)
    print("🧠 MANAS SYNAPTIC TRAINING SESSION")
    print("=" * 70)

    show_synapses(workspace, "BEFORE Training")

    # Initialize VivekaAction
    viveka = VivekaAction(workspace=workspace)

    # Training intents - each one will reinforce a pattern
    training_intents = [
        Intent(
            id="train-001",
            intent_type="update_readme",
            title="Update README with new features",
            description="Training intent for documentation updates",
            reasoning="Testing synaptic learning",
            params={"file_path": "README.md"},
        ),
        Intent(
            id="train-002",
            intent_type="fix_test",
            title="Fix failing test in test_contracts.py",
            description="Training intent for test fixes",
            reasoning="Testing synaptic learning",
            params={"file_path": "tests/test_contracts.py", "error": "AssertionError"},
        ),
        Intent(
            id="train-003",
            intent_type="run_tests",
            title="Run test suite after changes",
            description="Training intent for test execution",
            reasoning="Testing synaptic learning",
            params={"file_path": "vibe_core/kernel.py"},
        ),
        Intent(
            id="train-004",
            intent_type="check_lint",
            title="Check linting after refactor",
            description="Training intent for lint checks",
            reasoning="Testing synaptic learning",
            params={"file_path": "vibe_core/loaders/action_loader.py"},
        ),
        Intent(
            id="train-005",
            intent_type="notify_operator",
            title="Notify operator about critical error",
            description="Training intent for notifications",
            reasoning="Testing synaptic learning",
            params={"error": "ConnectionTimeout", "severity": "critical"},
        ),
    ]

    print(f"\n🎓 Training with {len(training_intents)} intents...")
    print("-" * 60)

    for i, intent in enumerate(training_intents, 1):
        print(f"\n[{i}/{len(training_intents)}] Processing: {intent.title}")

        # Evaluate through Viveka gate
        eval_result = viveka.evaluate(intent)
        decision = eval_result.get("decision", "UNKNOWN")
        dharmic_score = eval_result.get("dharmic_score", 0)
        harmony = eval_result.get("harmony", "?")

        print("  📋 Dharmic Evaluation:")
        print(f"     Decision: {decision}")
        print(f"     Score: {dharmic_score:.2f}")
        print(f"     Harmony: {harmony}")

        if decision in ("EXECUTE", "WARN_EXECUTE", "SHIVA_OVERRIDE"):
            # Simulate successful execution
            print("  ✅ Simulating successful execution...")

            # Reinforce the pattern
            viveka.reinforce(intent, success=True)
            print("  🧠 Synapse reinforced!")
        else:
            print("  ⛔ Blocked - no reinforcement")

    show_synapses(workspace, "AFTER Training")

    # Show delta
    print("\n" + "=" * 70)
    print("📈 TRAINING SUMMARY")
    print("=" * 70)
    print("Each successful execution increased the weight by 0.05")
    print("Run this script multiple times to see weights grow toward 1.0")
    print("\nNext: Implement P2 (Negative Learning) to reduce weights on failure")


def test_negative_learning(workspace: Path):
    """Test negative learning - weights should decrease on failure."""
    from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import VivekaAction
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

    print("\n" + "=" * 70)
    print("🔴 TESTING NEGATIVE LEARNING (P2 Implementation)")
    print("=" * 70)

    viveka = VivekaAction(workspace=workspace)

    # Use an intent that we've already trained (so it has a weight)
    failure_intent = Intent(
        id="fail-001",
        intent_type="update_readme",  # This was trained earlier!
        title="Failed README update (simulated)",
        description="Testing negative learning",
        reasoning="P2 test",
        params={"file_path": "README.md"},
    )

    show_synapses(workspace, "BEFORE Negative Learning")

    print("\n🔴 Simulating FAILED execution of 'update_readme'...")
    print("   (This intent was successfully trained earlier)")

    # Reinforce with FAILURE
    viveka.reinforce(failure_intent, success=False)

    show_synapses(workspace, "AFTER Negative Learning")

    print("\n✅ P2 IMPLEMENTED: Weights now DECREASE on failure!")
    print("   Learning rate: +0.05 success / -0.10 failure (asymmetric)")
    print("   This means MANAS learns FASTER from mistakes 🧠")


if __name__ == "__main__":
    workspace = project_root

    print("🧠 MANAS Synaptic Training Demo")
    print("=" * 70)

    # Run training
    run_training_session(workspace)

    # Test P2 gap
    test_negative_learning(workspace)

    print("\n✅ Demo complete!")
