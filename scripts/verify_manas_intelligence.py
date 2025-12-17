import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestIntelligence")


class TestManasIntelligence(unittest.TestCase):
    def setUp(self):
        # Mock dependencies usually provided by kernel/plugins
        self.mock_workspace = Path("/tmp/manas_test")
        self.mock_workspace.mkdir(parents=True, exist_ok=True)

    def test_slim_mode(self):
        """Test MANAS initialization WITHOUT sentence-transformers."""
        logger.info("🧪 Testing SLIM MODE (No Brain)...")

        # Ensure modules are fresh
        if "vibe_core.plugins.opus_assistant.manas.cognitive_kernel" in sys.modules:
            del sys.modules["vibe_core.plugins.opus_assistant.manas.cognitive_kernel"]

        with patch.dict(sys.modules, {"sentence_transformers": None}):
            from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel, ManasConfig

            # Initialize Kernel
            kernel = CognitiveKernel(workspace=self.mock_workspace, config=ManasConfig())

            # Assertions
            self.assertFalse(kernel.has_intelligence, "MANAS should NOT have intelligence in Slim Mode")
            self.assertIsNone(kernel._semantic_engine, "Semantic Engine should be None")
            logger.info("✅ SLIM MODE Passed")

    def test_smart_mode(self):
        """Test MANAS initialization WITH sentence-transformers."""
        logger.info("🧪 Testing SMART MODE (With Brain)...")

        # Determine if we have real lib
        try:
            import sentence_transformers

            has_real_lib = True
        except ImportError:
            has_real_lib = False
            logger.warning("⚠️ sentence-transformers not installed, using mock for Smart Mode test")

        # Mock keys
        modules_to_patch = {}
        if not has_real_lib:
            mock_runtime = MagicMock()
            modules_to_patch = {
                "sentence_transformers": MagicMock(),
                "vibe_core.runtime_extensions": mock_runtime,
                "vibe_core.cortex.engines.semantic_engine": MagicMock(),
            }

        # Clean import
        if "vibe_core.plugins.opus_assistant.manas.cognitive_kernel" in sys.modules:
            del sys.modules["vibe_core.plugins.opus_assistant.manas.cognitive_kernel"]

        with patch.dict(sys.modules, modules_to_patch):
            from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel, ManasConfig

            kernel = CognitiveKernel(workspace=self.mock_workspace, config=ManasConfig())

            if not has_real_lib:
                # Verify extend_runtime was called!
                modules_to_patch["vibe_core.runtime_extensions"].extend_runtime.assert_called()
                logger.info("✅ Runtime Grafting Verified (extend_runtime called)")

            # Assertions
            # In mock mode, we assume success if no error.
            # In real mode, we check properties.
            if has_real_lib:
                self.assertTrue(kernel.has_intelligence, "MANAS SHOULD have intelligence in Smart Mode")
                self.assertIsNotNone(kernel._semantic_engine, "Semantic Engine should be active")

            logger.info("✅ SMART MODE Passed")

    def test_container_env(self):
        """Test MANAS compatibility with container paths (different HOME)."""
        logger.info("🧪 Testing CONTAINER COMPLIANCE (Custom HOME)...")

        # Simulate a container home dir
        container_home = Path("/tmp/container_home/steward")
        container_home.mkdir(parents=True, exist_ok=True)

        with patch.dict("os.environ", {"HOME": str(container_home)}):
            # Re-import runtime extensions to pick up new HOME
            if "vibe_core.runtime_extensions" in sys.modules:
                del sys.modules["vibe_core.runtime_extensions"]

            import vibe_core.runtime_extensions as re

            # Check if STEWARD_LIB is correct relative to mocked HOME
            expected_lib = container_home / ".steward" / "lib"
            expected_str = str(expected_lib)
            actual_str = str(re.STEWARD_LIB)

            # Note: On some systems /tmp might involve symlinks resolving differently
            # So we check if the suffix match or simple string match
            self.assertEqual(
                actual_str,
                expected_str,
                f"Runtime Extensions did NOT respect container HOME path. Expected {expected_str}, got {actual_str}",
            )

            logger.info(f"✅ Container Path Verified: {re.STEWARD_LIB}")


if __name__ == "__main__":
    unittest.main()
