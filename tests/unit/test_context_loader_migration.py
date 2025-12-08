"""
Verification Test: Context Loader Migration (OPUS-005 Phase 3)
============================================================

Verifies:
1. ContextLoader follows UnifiedLoader pattern
2. ContextLoader discovers project context (singleton)
3. ContextManager functions correctly
4. BootSequence integration works (instantiation)
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.loaders import UnifiedLoader
from vibe_core.runtime.boot_sequence import BootSequence
from vibe_core.runtime.context_loader import ContextLoader, ContextManager


class TestContextLoaderMigration(unittest.TestCase):
    def test_loader_inheritance(self):
        """Verify ContextLoader inherits from UnifiedLoader"""
        assert issubclass(ContextLoader, UnifiedLoader)
        assert ContextLoader.item_type == "context"

    def test_discovery(self):
        """Verify loader can discover project context"""
        items, metadata = ContextLoader.discover_and_load(force_refresh=True)

        assert "project" in items
        assert isinstance(items["project"], ContextManager)

        # Verify metadata
        assert "project" in metadata
        meta = metadata["project"]
        assert meta.item_type == "context"
        assert meta.loaded_successfully

    def test_manager_functionality(self):
        """Verify ContextManager still works as expected"""
        items, _ = ContextLoader.discover_and_load(force_refresh=False)
        manager = items["project"]

        # Test usage
        context = manager.load()
        assert isinstance(context, dict)
        assert "git" in context
        assert "environment" in context

    def test_boot_sequence_instantiation(self):
        """Verify BootSequence can be instantiated with new loader"""
        try:
            boot = BootSequence()
            assert isinstance(boot.context_loader, ContextManager)
            print("✅ BootSequence instantiated successfully")
        except Exception as e:
            # Check if failure is due to missing dependencies (e.g. LLM engine)
            # or due to our change
            print(f"BootSequence instantiation failed: {e}")
            raise e


if __name__ == "__main__":
    unittest.main()
