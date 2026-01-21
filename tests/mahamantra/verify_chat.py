"""
VERIFY SANKIRTAN - The Universal Chat Bridge
============================================

Tests the chat capabilities (Phase 9).
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import logging

# Setup Logging to see Bridge activity
logging.basicConfig(level=logging.INFO)

from vibe_core.mahamantra.lila.chat import universal_chat
from vibe_core.mahamantra.kernel.singularity import mahamantra
from vibe_core.mahamantra.substrate.proxy import BalaramaProxy

# Dummy Service that SPEAKS
TALKING_PY = """
def on_chat(message):
    return f"I heard you say: {message}"

__mahajana__ = "narada"
__position__ = 2
"""

# Dummy Service that is SILENT (Fallback)
SILENT_PY = """
def do_work():
    pass
"""


class TestSankirtan(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        # Create test files
        self.talker_path = self.base_path / "talker.py"
        self.talker_path.write_text(TALKING_PY)

        self.silent_path = self.base_path / "silent.py"
        self.silent_path.write_text(SILENT_PY)

        # Ensure we can import them by adding temp dir to sys.path
        import sys

        if str(self.base_path) not in sys.path:
            sys.path.append(str(self.base_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_chat_mahajana(self):
        """Test chatting with a canonical Mahajana (Brahma)."""
        print("\n\n🕉️  CHATTING WITH BRAHMA")
        print("========================")

        # Brahma is auto-loaded by Singularity
        response = universal_chat.message("brahma", "Hello Creator")
        print(f"Response:\n{response}")

        self.assertIn("PROXY RESPONSE", response)
        self.assertIn("BRAHMA", response)
        self.assertIn("Pos 1", response)

    def test_chat_dynamic_talker(self):
        """Test chatting with a dynamically wrapped service that speaks."""
        print("\n\n🗣️  CHATTING WITH TALKER")
        print("========================")

        # Dynamic wrap via module name
        response = universal_chat.message("talker", "Hare Krishna")
        print(f"Response:\n{response}")

        self.assertEqual(response, "I heard you say: Hare Krishna")

    def test_chat_dynamic_silent(self):
        """Test chatting with a silent service (fallback)."""
        print("\n\njh  CHATTING WITH SILENT")
        print("========================")

        response = universal_chat.message("silent", "Wake up")
        print(f"Response:\n{response}")

        self.assertIn("PROXY RESPONSE", response)
        self.assertIn("Unknown Service", response)  # Because silent.py has no declarations?
        # Actually it depends on if Balarama extracts unknowns. Yes.


if __name__ == "__main__":
    unittest.main()
