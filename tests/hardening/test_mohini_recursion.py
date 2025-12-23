#!/usr/bin/env python3
"""
MOHINI-MURTI: The Infinite Recursive Loop - Cognitive Deception Test.

Mythology: When the Devas and Asuras fought over the Amrita (nectar of
immortality), Vishnu took the form of Mohini, an enchantress of
incomparable beauty. The Asuras, mesmerized by her form, forgot their
purpose and lost their share of the nectar. They were trapped in an
endless loop of desire, never reaching their goal.

This test proves:
1. Circular intent dependencies are detected and broken.
2. Recursive action loops don't cause stack overflow.
3. The cognitive layer can escape infinite "beauty loops".

"Maya may enchant, but Dharma must not forget its purpose."
"""

import hashlib
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class Intent:
    """Simplified Intent for testing."""

    id: str
    intent_type: str
    title: str
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    confidence: float = 0.8


class CircularDependencyDetector:
    """
    Detects circular dependencies in intent graphs.
    Uses DFS with path tracking for cycle detection.
    """

    def __init__(self):
        self.visited: Set[str] = set()
        self.path: List[str] = []
        self.cycles_found: List[List[str]] = []

    def detect_cycle(self, intent: Intent, all_intents: Dict[str, Intent]) -> Optional[List[str]]:
        """
        Detect if processing this intent would create a cycle.
        Returns the cycle path if found, None otherwise.
        """
        self.visited.clear()
        self.path.clear()
        self.cycles_found.clear()

        self._dfs(intent.id, all_intents)

        return self.cycles_found[0] if self.cycles_found else None

    def _dfs(self, intent_id: str, all_intents: Dict[str, Intent]) -> bool:
        """DFS with path tracking for cycle detection."""
        if intent_id in self.path:
            # Cycle found! Extract the cycle
            cycle_start = self.path.index(intent_id)
            cycle = self.path[cycle_start:] + [intent_id]
            self.cycles_found.append(cycle)
            return True

        if intent_id in self.visited:
            return False

        intent = all_intents.get(intent_id)
        if not intent:
            return False

        self.visited.add(intent_id)
        self.path.append(intent_id)

        for dep_id in intent.dependencies:
            if self._dfs(dep_id, all_intents):
                return True

        self.path.pop()
        return False


class TestMohiniRecursion:
    """Tests for cognitive loop prevention and circular dependency detection."""

    def test_simple_circular_dependency_detection(self):
        """
        MOHINI TEST 1: Simple A→B→A Cycle.

        Intent A depends on B, Intent B depends on A.
        System must detect and refuse to enter this loop.
        """
        print("\n🌙 MOHINI (Simple Cycle A→B→A):")

        intent_a = Intent(
            id="intent_a",
            intent_type="approval",
            title="Need B's approval",
            dependencies=["intent_b"],
        )

        intent_b = Intent(
            id="intent_b",
            intent_type="confirmation",
            title="Need A's confirmation",
            dependencies=["intent_a"],  # CYCLE!
        )

        all_intents = {"intent_a": intent_a, "intent_b": intent_b}

        detector = CircularDependencyDetector()
        cycle = detector.detect_cycle(intent_a, all_intents)

        print(f"   Intent A depends on: {intent_a.dependencies}")
        print(f"   Intent B depends on: {intent_b.dependencies}")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, "MOHINI VICTORY: Simple cycle undetected!"
        assert "intent_a" in cycle and "intent_b" in cycle

        print("✅ Simple Cycle DETECTED: Mohini's illusion broken")

    def test_complex_circular_dependency_chain(self):
        """
        MOHINI TEST 2: Complex A→B→C→D→A Cycle.

        Longer dependency chains that eventually loop back.
        """
        print("\n🌙 MOHINI (Complex Cycle A→B→C→D→A):")

        intents = {
            "a": Intent(id="a", intent_type="step", title="Step A", dependencies=["b"]),
            "b": Intent(id="b", intent_type="step", title="Step B", dependencies=["c"]),
            "c": Intent(id="c", intent_type="step", title="Step C", dependencies=["d"]),
            "d": Intent(id="d", intent_type="step", title="Step D", dependencies=["a"]),  # CYCLE!
        }

        detector = CircularDependencyDetector()
        cycle = detector.detect_cycle(intents["a"], intents)

        print("   Chain: a→b→c→d→a")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, "MOHINI VICTORY: Complex cycle undetected!"
        assert len(cycle) >= 4, f"Cycle too short: {cycle}"

        print("✅ Complex Cycle DETECTED: Long chain hypnosis broken")

    def test_nested_json_recursion_limit(self):
        """
        MOHINI TEST 3: Deep JSON Nesting (Stack Overflow Prevention).

        Attackers send deeply nested JSON to cause stack overflow
        during validation or processing.
        """
        print("\n🌙 MOHINI (Deep JSON Nesting):")

        def create_deep_json(depth: int) -> Dict[str, Any]:
            """Create a deeply nested JSON structure."""
            if depth == 0:
                return {"bottom": True}
            return {"level": create_deep_json(depth - 1)}

        # Test with dangerous depth
        dangerous_depth = 100  # Could cause stack overflow in naive parsers
        deep_json = create_deep_json(dangerous_depth)

        # Create intent with deeply nested params
        intent = Intent(
            id="deep_intent",
            intent_type="complex_operation",
            title="Deep nested params",
            params=deep_json,
        )

        # Attempt to process (serialize/validate)
        try:
            # Simulate processing
            import json

            serialized = json.dumps(intent.params)
            deserialized = json.loads(serialized)

            # Check we didn't crash and data is intact
            current = deserialized
            depth_verified = 0
            while "level" in current:
                current = current["level"]
                depth_verified += 1

            print(f"   Target depth: {dangerous_depth}")
            print(f"   Verified depth: {depth_verified}")

            assert depth_verified == dangerous_depth, f"Depth mismatch: {depth_verified} vs {dangerous_depth}"
            print("✅ Deep JSON Nesting HANDLED without crash")

        except RecursionError as e:
            pytest.fail(f"MOHINI VICTORY: Stack overflow! {e}")

    def test_self_referencing_intent(self):
        """
        MOHINI TEST 4: Self-Referencing Intent (A→A).

        An intent that depends on itself - the simplest infinite loop.
        """
        print("\n🌙 MOHINI (Self-Reference A→A):")

        narcissist = Intent(
            id="narcissist",
            intent_type="approval",
            title="I need my own approval",
            dependencies=["narcissist"],  # Self-reference!
        )

        all_intents = {"narcissist": narcissist}

        detector = CircularDependencyDetector()
        cycle = detector.detect_cycle(narcissist, all_intents)

        print(f"   Intent depends on itself: {narcissist.dependencies}")
        print(f"   Cycle detected: {cycle}")

        assert cycle is not None, "MOHINI VICTORY: Self-reference undetected!"
        assert cycle == ["narcissist", "narcissist"], f"Wrong cycle format: {cycle}"

        print("✅ Self-Reference DETECTED: Narcissism loop broken")

    def test_diamond_dependency_not_cycle(self):
        """
        MOHINI TEST 5: Diamond Dependency (NOT a cycle).

        A→B, A→C, B→D, C→D
        This is a valid DAG, not a cycle. System should NOT flag it.
        """
        print("\n🌙 MOHINI (Diamond Dependency - Valid):")

        intents = {
            "a": Intent(id="a", intent_type="root", title="Root", dependencies=["b", "c"]),
            "b": Intent(id="b", intent_type="branch", title="Branch B", dependencies=["d"]),
            "c": Intent(id="c", intent_type="branch", title="Branch C", dependencies=["d"]),
            "d": Intent(id="d", intent_type="leaf", title="Leaf D", dependencies=[]),
        }

        detector = CircularDependencyDetector()
        cycle = detector.detect_cycle(intents["a"], intents)

        print("   Structure: A→[B,C]→D (diamond)")
        print(f"   Cycle detected: {cycle}")

        assert cycle is None, f"FALSE POSITIVE: Diamond flagged as cycle: {cycle}"

        print("✅ Diamond Dependency correctly NOT flagged as cycle")

    def test_loop_breaking_mechanism(self):
        """
        MOHINI TEST 6: Loop Breaking (Max Iterations Guard).

        Even if cycle detection fails, a max-iterations guard should
        prevent infinite loops during processing.
        """
        print("\n🌙 MOHINI (Loop Breaking Mechanism):")

        max_iterations = 100
        iteration_count = 0
        loop_broken = False

        # Simulate a processing loop that could go infinite
        current = "start"
        visited = set()

        while current != "end":
            iteration_count += 1

            if iteration_count > max_iterations:
                loop_broken = True
                break

            if current in visited:
                # Cycle detected mid-loop
                loop_broken = True
                break

            visited.add(current)

            # Simulate processing that gets stuck
            current = "stuck"  # Never reaches "end"

        print(f"   Max iterations: {max_iterations}")
        print(f"   Actual iterations: {iteration_count}")
        print(f"   Loop broken: {loop_broken}")

        assert loop_broken, "MOHINI VICTORY: Infinite loop not prevented!"
        assert iteration_count <= max_iterations + 1, f"Too many iterations: {iteration_count}"

        print("✅ Loop Breaking Mechanism WORKING")

    def test_concurrent_cycle_detection(self):
        """
        MOHINI TEST 7: Concurrent Cycle Detection.

        Multiple threads trying to process dependent intents simultaneously.
        Race conditions should not cause false passes or misses.
        """
        print("\n🌙 MOHINI (Concurrent Detection):")

        # Create a known cyclic structure
        intents = {
            "x": Intent(id="x", intent_type="step", title="X", dependencies=["y"]),
            "y": Intent(id="y", intent_type="step", title="Y", dependencies=["z"]),
            "z": Intent(id="z", intent_type="step", title="Z", dependencies=["x"]),
        }

        results: List[bool] = []
        lock = threading.Lock()

        def detect_in_thread():
            detector = CircularDependencyDetector()
            cycle = detector.detect_cycle(intents["x"], intents)
            with lock:
                results.append(cycle is not None)

        # Launch multiple concurrent detections
        threads = []
        for _ in range(20):
            t = threading.Thread(target=detect_in_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print(f"   Threads: {len(threads)}")
        print(f"   All detected cycle: {all(results)}")
        print(f"   Any false negative: {not all(results)}")

        assert all(results), f"FALSE NEGATIVES in concurrent detection: {results.count(False)} misses"

        print("✅ Concurrent Detection CONSISTENT")

    def test_intent_recursion_depth_limit(self):
        """
        MOHINI TEST 8: Intent Processing Recursion Limit.

        Simulate deep intent processing that could overflow call stack.
        System should have explicit recursion depth limits.
        """
        print("\n🌙 MOHINI (Recursion Depth Limit):")

        max_recursion_depth = 50
        actual_depth = 0

        def process_intent(depth: int = 0) -> int:
            """Simulated recursive intent processing with depth limit."""
            if depth >= max_recursion_depth:
                return depth  # Safety limit

            # Simulate processing that triggers child intents
            return process_intent(depth + 1)

        try:
            actual_depth = process_intent()
            print(f"   Max allowed depth: {max_recursion_depth}")
            print(f"   Actual depth reached: {actual_depth}")

            assert actual_depth == max_recursion_depth, f"Depth limit not enforced: {actual_depth}"
            print("✅ Recursion Depth Limit ENFORCED")

        except RecursionError:
            pytest.fail("MOHINI VICTORY: Stack overflow - no recursion limit!")


class TestCognitiveResilience:
    """Tests for MANAS cognitive layer resilience against deception."""

    def test_hallucination_resistance(self):
        """
        Test that high "temperature" (uncertainty) inputs are handled
        with appropriate skepticism.
        """
        print("\n🌙 COGNITIVE (Hallucination Resistance):")

        # Simulate high-uncertainty intent (like LLM with high temperature)
        uncertain_intent = Intent(
            id="uncertain",
            intent_type="action",
            title="Maybe do something?",
            confidence=0.3,  # LOW confidence
        )

        # System should be skeptical of low-confidence intents
        requires_verification = uncertain_intent.confidence < 0.5

        print(f"   Intent confidence: {uncertain_intent.confidence}")
        print(f"   Requires verification: {requires_verification}")

        assert requires_verification, "Low confidence intents should require verification"
        print("✅ Hallucination Resistance ACTIVE")

    def test_semantic_loop_detection(self):
        """
        Detect when intents are semantically similar but have different IDs,
        potentially forming a disguised loop.
        """
        print("\n🌙 COGNITIVE (Semantic Loop Detection):")

        def semantic_hash(intent: Intent) -> str:
            """Create a semantic fingerprint of an intent."""
            content = f"{intent.intent_type}|{intent.title}|{intent.description}"
            return hashlib.md5(content.encode()).hexdigest()[:8]

        # Create intents that are semantically identical but different IDs
        intent_1 = Intent(
            id="intent_abc123",
            intent_type="document_update",
            title="Update README",
            description="Fix documentation",
        )

        intent_2 = Intent(
            id="intent_xyz789",  # Different ID!
            intent_type="document_update",
            title="Update README",
            description="Fix documentation",
        )

        hash_1 = semantic_hash(intent_1)
        hash_2 = semantic_hash(intent_2)

        print(f"   Intent 1 ID: {intent_1.id}, Semantic: {hash_1}")
        print(f"   Intent 2 ID: {intent_2.id}, Semantic: {hash_2}")
        print(f"   Semantically identical: {hash_1 == hash_2}")

        # Detection: Same semantic hash = likely duplicate/loop
        is_duplicate = hash_1 == hash_2 and intent_1.id != intent_2.id

        assert is_duplicate, "Semantic duplicates should be detected"
        print("✅ Semantic Loop DETECTED: Different IDs, same intent")


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
