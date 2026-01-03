from pathlib import Path

import pytest

from vibe_core.cartridges.system.watchman.cartridge_main import WatchmanCartridge
from vibe_core.di import ServiceRegistry
from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.state.prakriti import Prakriti


@pytest.fixture
def clean_workspace(tmp_path):
    """Provide a clean workspace for the test."""
    # Ensure .prakriti dir exists
    (tmp_path / ".prakriti").mkdir()
    return tmp_path


def test_ouroboros_persistence(clean_workspace):
    """
    Verify that Watchman violations persist across Prakriti sessions.

    Diamond Protocol:
    1. Boot Prakriti (Session A)
    2. Watchman records violation
    3. Shutdown Prakriti
    4. Boot Prakriti (Session B)
    5. Verify violation exists in Session B
    """

    # --- SESSION A ---
    print("\n--- SESSION A ---")
    prakriti_a = Prakriti(workspace_path=clean_workspace)

    # Ensure KG is wired
    kg_a = ServiceRegistry.get(UnifiedKnowledgeGraph)
    assert kg_a is not None, "KnowledgeGraph not registered in Session A"

    # Watchman finds a violation
    watchman = WatchmanCartridge()
    # Mock system injection for watchman (usually done by kernel)
    # But _record_violations_to_knowledge_graph uses ServiceRegistry directly

    violation = {
        "file_path": "test_violation.py",
        "line_number": 1,
        "rule_id": "TEST_RULE",
        "message": "This should persist",
        "has_remedy": True,
    }

    # Record violation
    count = watchman._record_violations_to_knowledge_graph([violation])
    assert count == 1

    # Verify it exists in Session A memory
    violations_a = kg_a.get_violations(rule_id="TEST_RULE")
    assert len(violations_a) == 1

    # Trigger persistence (simulate end of session or explicit save)
    # Currently Prakriti doesn't auto-save knowledge on every change,
    # so we need to rely on what we implement.
    # If we assume 'end_session' or similar saves it.
    if hasattr(prakriti_a, "save_knowledge"):
        prakriti_a.save_knowledge()
    else:
        # If not implemented yet, this test EXPECTS failure or manual save logic
        pass

    # --- SESSION B (Restart) ---
    print("\n--- SESSION B ---")
    # Reset registry for new session simulation
    ServiceRegistry._services.clear()

    prakriti_b = Prakriti(workspace_path=clean_workspace)
    kg_b = ServiceRegistry.get(UnifiedKnowledgeGraph)
    assert kg_b is not None, "KnowledgeGraph not registered in Session B"
    assert kg_b is not kg_a, "Should be a new instance"

    # Verify persistence
    violations_b = kg_b.get_violations(rule_id="TEST_RULE")

    # THIS ASSERTION SHOULD FAIL until we implement persistence
    assert len(violations_b) == 1, "Violation did not persist to Session B"
    # Message is stored in description, not properties
    assert violations_b[0].description == "This should persist"
