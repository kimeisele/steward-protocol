
"""
VERIFY EXECUTION - The King's Scepter
=====================================

Tests the Unified Execution Pipeline (Phase 10).
Ensures that Natural Language maps to Mahajana Actions.
"""

import unittest
import logging
from vibe_core.mahamantra.kernel.singularity import mahamantra
from vibe_core.gateway import execute as gateway_execute

# Setup Logging
logging.basicConfig(level=logging.INFO)

class TestRoyalAlignment(unittest.TestCase):
    
    def test_execution_scan_disk(self):
        """Test 'scan disk' -> Prithu."""
        print("\n\n💾 EXECUTE: SCAN DISK")
        print("======================")
        
        # Using Gateway Execute (simulating CLI)
        response = gateway_execute("scan disk")
        
        print(f"Response:\n{response['output']}")
        
        self.assertTrue(response['success'])
        self.assertIn("PRITHU", response['output']) # Should be mapped to Prithu
        # response['guardian'] might be lower or upper case pending implementation, check loosely or strictly
        self.assertEqual(response['guardian'], "prithu")

    def test_execution_time(self):
        """Test 'what time is it' -> Yamaraja."""
        print("\n\n🕒 EXECUTE: TIME")
        print("====================")
        
        # Using Gateway Execute
        response = gateway_execute("what time is it")
        
        print(f"Response:\n{response['output']}")
        
        self.assertTrue(response['success'])
        self.assertIn("YAMARAJA", response['output'])
        self.assertEqual(response['guardian'], "yamaraja")

    def test_execution_legacy_chat(self):
        """Test fallback to chat/Narada."""
        print("\n\n🗣️ EXECUTE: CHAT (UNKNOWN)")
        print("=========================")
        
        # Using Gateway Execute
        response = gateway_execute("hello world")
        
        print(f"Response:\n{response['output']}")
        
        self.assertTrue(response['success'])
        self.assertIn("NARADA", response['output']) # Fallback

if __name__ == '__main__':
    unittest.main()
