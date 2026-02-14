"""
E2E CLOSED LOOP TEST — Proof that the Self-Healing Pipeline Works
==================================================================

This test proves the ENTIRE closed loop fires end-to-end:

    1. INJECT: Create a broken file (unused Any import) on disk
    2. INGEST: ViolationIngester pushes it into Knowledge Graph
    3. HEAL:   ShuddhiEngine.heal_and_record() reads KG, applies CST remedy
    4. VERIFY: File on disk is healed, KG violation marked as healed

No boot. No VenuService. No async. Pure component wiring.
This is the proof that the organism's immune system works.
"""

import tempfile
import textwrap
from pathlib import Path

import pytest

from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.knowledge.schema import NodeType
from vibe_core.ouroboros.ingestion import (
    ViolationIngester,
    ViolationRecord,
    ViolationSource,
)
from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def kg():
    """Fresh Knowledge Graph per test."""
    return UnifiedKnowledgeGraph()


@pytest.fixture
def ingester(kg):
    """ViolationIngester wired to the test KG."""
    return ViolationIngester(kg=kg)


@pytest.fixture
def engine():
    """ShuddhiEngine with all 14 remedies loaded."""
    return ShuddhiEngine()


@pytest.fixture
def broken_file(tmp_path):
    """Create a Python file with an unused Any import (any_type_usage violation)."""
    code = textwrap.dedent("""\
        from typing import Any, Dict, List

        def process(data: Dict[str, List[int]]) -> None:
            for key, values in data.items():
                print(key, sum(values))
    """)
    f = tmp_path / "broken_module.py"
    f.write_text(code)
    return f


@pytest.fixture
def broken_file_silent_fail(tmp_path):
    """Create a Python file with a bare except (silent_failure violation)."""
    code = textwrap.dedent("""\
        import logging

        logger = logging.getLogger(__name__)

        def risky_operation():
            try:
                result = 1 / 0
            except:
                pass
    """)
    f = tmp_path / "silent_module.py"
    f.write_text(code)
    return f


# =============================================================================
# E2E: FULL CLOSED LOOP
# =============================================================================

class TestClosedLoopE2E:
    """End-to-end proof of the self-healing pipeline."""

    def test_inject_heal_verify_any_type(self, kg, ingester, engine, broken_file):
        """
        FULL LOOP: unused Any import → KG → heal → file fixed → KG updated.

        This is THE proof. If this passes, the immune system works.
        """
        # --- STEP 1: INJECT violation into KG ---
        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="any_type_usage",
                file_path=str(broken_file),
                line=1,
                message="Unused Any import",
                severity="MEDIUM",
                has_remedy=True,
                verification_status="verified",
                origin="live_scan",
            )
        ]
        ingested = ingester.ingest(violations)
        assert ingested == 1, "Violation must be ingested"

        # --- STEP 2: Verify KG has the violation ---
        unhealed = kg.get_violations(healed=False)
        assert len(unhealed) == 1, f"Expected 1 unhealed violation, got {len(unhealed)}"
        violation_node = unhealed[0]
        assert violation_node.properties["rule_id"] == "any_type_usage"
        assert violation_node.properties["file"] == str(broken_file)
        assert violation_node.properties["healed"] is False

        # --- STEP 3: HEAL via ShuddhiEngine ---
        result = engine.heal_and_record(
            file_path=broken_file,
            rule_id="any_type_usage",
            violation_id=violation_node.id,
            write_file=True,
        )

        # --- STEP 4: VERIFY healing succeeded ---
        assert result.status == ShuddhiStatus.PURIFIED, (
            f"Expected PURIFIED, got {result.status}: {result.message}"
        )

        # --- STEP 5: VERIFY file on disk is healed ---
        healed_code = broken_file.read_text()
        assert "Any" not in healed_code, (
            f"Any should be removed from healed file.\nHealed code:\n{healed_code}"
        )
        assert "Dict" in healed_code, "Dict import should remain"
        assert "List" in healed_code, "List import should remain"

        # Verify healed code compiles
        compile(healed_code, str(broken_file), "exec")

    def test_inject_heal_verify_with_kg_marking(self, kg, ingester, engine, broken_file):
        """
        Verify that KG violation is marked as healed after successful healing.

        This tests the KG feedback loop — not just the file fix.
        """
        # Inject
        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="any_type_usage",
                file_path=str(broken_file),
                line=1,
                message="Unused Any import",
                has_remedy=True,
                verification_status="verified",
                origin="live_scan",
            )
        ]
        ingester.ingest(violations)
        violation_node = kg.get_violations(healed=False)[0]

        # Heal with KG recording
        # We need to wire KG into ServiceRegistry for heal_and_record to find it
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol

        # Register our test KG
        original = ServiceRegistry.get(KnowledgeGraphProtocol)
        ServiceRegistry.register(KnowledgeGraphProtocol, kg)

        try:
            result = engine.heal_and_record(
                file_path=broken_file,
                rule_id="any_type_usage",
                violation_id=violation_node.id,
                write_file=True,
            )
            assert result.status == ShuddhiStatus.PURIFIED

            # Verify KG is updated
            healed_violations = kg.get_violations(healed=True)
            assert len(healed_violations) == 1, (
                f"Expected 1 healed violation, got {len(healed_violations)}"
            )
            assert healed_violations[0].properties["healed"] is True
            assert healed_violations[0].properties["healed_by"] == "any_type_usage"

            # Verify no unhealed violations remain
            unhealed = kg.get_violations(healed=False)
            assert len(unhealed) == 0, (
                f"Expected 0 unhealed violations, got {len(unhealed)}"
            )
        finally:
            # Restore original KG registration
            if original:
                ServiceRegistry.register(KnowledgeGraphProtocol, original)


# =============================================================================
# COMPONENT TESTS — Each link in the chain
# =============================================================================

class TestChainLinks:
    """Test each individual link in the closed loop."""

    def test_ingester_to_kg(self, kg, ingester):
        """Link 1: ViolationIngester → KG."""
        violations = [
            ViolationRecord(
                source=ViolationSource.WATCHMAN,
                rule_id="test_rule",
                file_path="/tmp/test.py",
                line=42,
                message="Test violation",
                has_remedy=True,
            )
        ]
        count = ingester.ingest(violations)
        assert count == 1

        nodes = kg.get_violations(healed=False)
        assert len(nodes) == 1
        assert nodes[0].properties["rule_id"] == "test_rule"
        assert nodes[0].properties["file"] == "/tmp/test.py"
        assert nodes[0].properties["healed"] is False

    def test_kg_violation_lifecycle(self, kg):
        """Link 2: KG violation → healed lifecycle."""
        # Add violation
        node = kg.add_violation(
            file_path="/tmp/test.py",
            line=10,
            rule_id="any_type_usage",
            message="Unused Any",
            has_remedy=True,
        )

        # Verify unhealed
        assert len(kg.get_violations(healed=False)) == 1
        assert len(kg.get_violations(healed=True)) == 0

        # Mark healed
        kg.mark_violation_healed(node.id, "any_type_usage")

        # Verify healed
        assert len(kg.get_violations(healed=False)) == 0
        assert len(kg.get_violations(healed=True)) == 1

    def test_engine_purify_any_type(self, engine, broken_file):
        """Link 3: ShuddhiEngine.purify() heals a file."""
        result = engine.purify(broken_file, "any_type_usage")
        assert result.status == ShuddhiStatus.PURIFIED
        assert result.purified_code is not None
        assert "Any" not in result.purified_code
        assert "Dict" in result.purified_code

    def test_engine_purify_clean_file_skips(self, engine, tmp_path):
        """ShuddhiEngine skips files that have no violations."""
        clean = tmp_path / "clean.py"
        clean.write_text("from typing import Dict\n\ndef f(x: Dict) -> None:\n    pass\n")
        result = engine.purify(clean, "any_type_usage")
        assert result.status == ShuddhiStatus.SKIPPED

    def test_engine_scan_cell_no_io(self, engine):
        """Link 4: scan_cell() works in pure RAM (no file I/O)."""
        source = "from typing import Any, Dict\n\ndef f(x: Dict) -> None:\n    pass\n"
        result = engine.scan_cell(source, "any_type_usage")
        assert result is not None
        assert result.status == ShuddhiStatus.PURIFIED
        assert "Any" not in result.purified_code

    def test_engine_scan_cell_clean_returns_none(self, engine):
        """scan_cell() returns None for clean code."""
        source = "from typing import Dict\n\ndef f(x: Dict) -> None:\n    pass\n"
        result = engine.scan_cell(source, "any_type_usage")
        assert result is None

    def test_engine_has_all_remedies(self, engine):
        """Verify all 14 remedies are loaded."""
        remedies = engine.list_remedies()
        assert len(remedies) >= 14, f"Expected >=14 remedies, got {len(remedies)}: {remedies}"

        # Verify key remedies exist
        expected = [
            "any_type_usage",
            "broken_genesis",
            "silent_failure",
            "unsafe_io_write",
            "missing_mahajana",
        ]
        for rule_id in expected:
            assert engine.can_heal(rule_id), f"Missing remedy: {rule_id}"


# =============================================================================
# MULTI-VIOLATION TEST
# =============================================================================

class TestMultiViolation:
    """Test healing multiple violations in sequence."""

    def test_multiple_files_multiple_rules(self, kg, ingester, engine, tmp_path):
        """Heal multiple violations across multiple files."""
        # Create two broken files
        file1 = tmp_path / "mod1.py"
        file1.write_text(
            "from typing import Any, Dict\n\ndef f(x: Dict) -> None:\n    pass\n"
        )

        file2 = tmp_path / "mod2.py"
        file2.write_text(
            "from typing import Any, List, Optional\n\ndef g(items: List[Optional[int]]) -> None:\n    pass\n"
        )

        # Inject both
        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="any_type_usage",
                file_path=str(file1),
                line=1,
                message="Unused Any in mod1",
                has_remedy=True,
                verification_status="verified",
                origin="live_scan",
            ),
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="any_type_usage",
                file_path=str(file2),
                line=1,
                message="Unused Any in mod2",
                has_remedy=True,
                verification_status="verified",
                origin="live_scan",
            ),
        ]
        assert ingester.ingest(violations) == 2
        assert len(kg.get_violations(healed=False)) == 2

        # Heal both
        for node in kg.get_violations(healed=False):
            file_path = Path(node.properties["file"])
            rule_id = node.properties["rule_id"]
            result = engine.heal_and_record(
                file_path=file_path,
                rule_id=rule_id,
                violation_id=node.id,
                write_file=True,
            )
            assert result.status == ShuddhiStatus.PURIFIED, (
                f"Failed to heal {file_path}: {result.message}"
            )

        # Verify both files healed
        assert "Any" not in file1.read_text()
        assert "Any" not in file2.read_text()
        assert "Dict" in file1.read_text()
        assert "List" in file2.read_text()

        # Both compile
        compile(file1.read_text(), str(file1), "exec")
        compile(file2.read_text(), str(file2), "exec")
