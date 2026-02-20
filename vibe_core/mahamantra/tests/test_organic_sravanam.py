"""
Tests for the organic Sravanam chain.

The system must be able to:
1. Parse Python files into CSTFragments
2. Register fragments as MahaCellUnified in CellRouter
3. Scan cells per position with guardian-specific remedies
4. Find real violations without any manual scripting

This is MantraOS: the system heals itself.
"""

from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.fragment_parser import (
    parse_file_to_fragments,
    register_fragments_as_cells,
)
from vibe_core.mahamantra.substrate.cell_router import get_router, CellRouter
from vibe_core.mahamantra.dharma.kumaras.sravanam import (
    SravanamScanner,
    SravanamListener,
    GUARDIAN_RULE_MAP,
)
from vibe_core.mahamantra.protocols._seed import WORDS


@pytest.fixture(autouse=True)
def fresh_router():
    """Reset CellRouter between tests to avoid cross-contamination."""
    import vibe_core.mahamantra.substrate.cell_router as cr
    old = cr._router
    cr._router = CellRouter()
    yield cr._router
    cr._router = old


class TestFragmentIngestion:
    """Files must decompose into cells in the CellRouter."""

    def test_parse_single_file(self):
        from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT
        f = SUBSTRATE_ROOT / "lotus_core.py"
        frags = parse_file_to_fragments(f)
        assert len(frags.fragments) > 0

    def test_register_populates_router(self, fresh_router):
        from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT
        f = SUBSTRATE_ROOT / "lotus_core.py"
        frags = parse_file_to_fragments(f)
        addrs = register_fragments_as_cells(frags)
        assert len(addrs) > 0
        assert len(fresh_router) == len(addrs)

    def test_cells_have_positions(self, fresh_router):
        from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT
        f = SUBSTRATE_ROOT / "lotus_core.py"
        frags = parse_file_to_fragments(f)
        register_fragments_as_cells(frags)
        positions = set()
        for cell in fresh_router._cells.values():
            positions.add(cell.header.pada_sevanam)
        assert len(positions) > 1, "Cells should span multiple positions"

    @pytest.mark.timeout(120)
    def test_bulk_ingestion(self, fresh_router):
        root = Path("vibe_core/mahamantra")
        count = 0
        for py in sorted(root.rglob("*.py")):
            if "__pycache__" in str(py) or "/tests/" in str(py):
                continue
            try:
                frags = parse_file_to_fragments(py)
                register_fragments_as_cells(frags)
                count += 1
            except Exception:
                pass
        assert count > 100, f"Should ingest 100+ files, got {count}"
        assert len(fresh_router) > 500, f"Should have 500+ cells, got {len(fresh_router)}"


# Small subset of files for fast scan tests
def _scan_files():
    from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT, MAHAMANTRA_ROOT
    return [
        SUBSTRATE_ROOT / "lotus_core.py",
        SUBSTRATE_ROOT / "vm" / "tattva_registry.py",
        SUBSTRATE_ROOT / "core" / "pancha_tattva.py",
        SUBSTRATE_ROOT / "encoding" / "wordnet_bridge.py",
        SUBSTRATE_ROOT / "vm" / "gate_providers.py",
        SUBSTRATE_ROOT / "cell_system" / "cell_router.py",
        MAHAMANTRA_ROOT / "dharma" / "kumaras" / "engine.py",
        MAHAMANTRA_ROOT / "dharma" / "kumaras" / "sravanam.py",
        MAHAMANTRA_ROOT / "adapters" / "composition.py",
        MAHAMANTRA_ROOT / "kernel" / "singularity.py",
    ]

def _ingest_subset():
    for f in _scan_files():
        if f.exists():
            try:
                frags = parse_file_to_fragments(f)
                register_fragments_as_cells(frags)
            except Exception:
                pass


class TestSravanamScan:
    """Sravanam must find violations organically via CellRouter."""

    def test_scan_position_returns_report(self, fresh_router):
        _ingest_subset()
        scanner = SravanamScanner()
        report = scanner.scan_position(0)
        assert report.position == 0
        assert report.guardian == "vyasa"

    def test_scan_finds_violations(self, fresh_router):
        _ingest_subset()
        scanner = SravanamScanner()
        total = 0
        for pos in range(WORDS):
            report = scanner.scan_position(pos)
            total += report.violations_found
        assert total > 0, "Sravanam should find at least 1 violation in the subset"

    def test_guardian_rule_map_covers_all_positions(self):
        assert len(GUARDIAN_RULE_MAP) == WORDS


class TestSravanamListener:
    """SravanamListener must respond to tick state."""

    def test_listener_responds_to_tick_dict(self, fresh_router):
        _ingest_subset()
        listener = SravanamListener()
        listener({"position": 0, "tick": 1})

    def test_listener_accumulates_reports(self, fresh_router):
        _ingest_subset()
        listener = SravanamListener()
        for pos in range(WORDS):
            listener({"position": pos, "tick": pos})
        assert isinstance(listener.reports, list)

    def test_listener_disable_stops_scanning(self, fresh_router):
        _ingest_subset()
        listener = SravanamListener()
        listener.disable()
        listener({"position": 0, "tick": 1})
        assert listener.total_violations == 0
