"""
Tests for the Shuddhi Self-Healing Engine.
"""

import os
import tempfile
import unittest
from pathlib import Path

from vibe_core.protocols.shuddhi import ShuddhiStatus
from vibe_core.shuddhi.engine import ShuddhiEngine


class TestShuddhiEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ShuddhiEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name) / "test_violation.py"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_purify_unsafe_io_write(self):
        """Test healing of unsafe open().write() pattern."""
        content = """
class MyTool:
    def run(self):
        with open("log.txt", "w") as f:
            f.write("hello world")
"""
        self.test_path.write_text(content)

        result = self.engine.purify(self.test_path, "unsafe_io_write")

        self.assertEqual(result.status, ShuddhiStatus.PURIFIED)
        self.assertIn("self.system.write_file", result.diff)

        # Verify result content (conceptually)
        # Note: In real use, ShuddhiEngine doesn't write back to file automatically
        # unless integrated with Kernel IO. For now, it returns the purified state.

    def test_out_of_scope_heuristic(self):
        """Test that heuristic prevents healing when self.system is missing."""
        content = """
def standalone_func():
    with open("log.txt", "w") as f:
        f.write("danger")
"""
        self.test_path.write_text(content)

        result = self.engine.purify(self.test_path, "unsafe_io_write")

        self.assertEqual(result.status, ShuddhiStatus.OUT_OF_SCOPE)
        self.assertIn("no 'self.system' context", result.message)


if __name__ == "__main__":
    unittest.main()
