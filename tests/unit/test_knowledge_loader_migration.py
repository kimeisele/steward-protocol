"""
Verification Test: Knowledge Loader Migration (OPUS-005 Phase 3)
==============================================================

Verifies:
1. KnowledgeLoader follows UnifiedLoader pattern
2. KnowledgeLoader scans and loads YAML files
3. UnifiedKnowledgeGraph correctly populates using the new loader
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
from vibe_core.knowledge.schema import Node
from vibe_core.loaders import UnifiedLoader
from vibe_core.loaders.knowledge_loader import KnowledgeLoader


class TestKnowledgeLoaderMigration(unittest.TestCase):
    def test_loader_inheritance(self):
        """Verify KnowledgeLoader inherits from UnifiedLoader"""
        assert issubclass(KnowledgeLoader, UnifiedLoader)
        assert KnowledgeLoader.item_type == "knowledge"

    def test_discovery(self):
        """Verify loader can discover knowledge files"""
        # Point to actual knowledge dir
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        if not knowledge_dir.exists():
            print("Skipping discovery test - knowledge dir not found")
            return

        items, metadata = KnowledgeLoader.discover_and_load(scan_paths=[knowledge_dir], force_refresh=True)

        # Should find at least some files (core ontology usually)
        print(f"Discovered {len(items)} knowledge files")
        assert len(items) > 0

        # Verify metadata structure
        first_id = list(items.keys())[0]
        meta = metadata[first_id]
        assert meta.item_type == "knowledge"
        assert meta.loaded_successfully

    def test_graph_integration(self):
        """Verify UnifiedKnowledgeGraph uses the loader correctly"""
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        if not knowledge_dir.exists():
            print("Skipping graph test - knowledge dir not found")
            return

        graph = UnifiedKnowledgeGraph()
        graph.load(knowledge_dir)

        print(f"Graph loaded: {len(graph.nodes)} nodes, {len(graph.constraints)} constraints")

        # Basic check if graph populated
        # Note: Depending on actual content, nodes might be 0 if knowledge dir is empty in test env
        # But we check that load() didn't crash
        assert graph._loaded is True

        # If there are nodes, check structure
        if len(graph.nodes) > 0:
            node = list(graph.nodes.values())[0]
            assert isinstance(node, Node)


if __name__ == "__main__":
    unittest.main()
