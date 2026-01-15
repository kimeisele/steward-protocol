
"""
VERIFY INTELLIGENT SANKIRTAN - The Chat Bridge V2
=================================================

Tests the "Intelligent Routing" capabilities (Phase 9 Revised).
Does NOT rely on manual target specification.
"""

import unittest
import logging
from vibe_core.mahamantra.kernel.singularity import mahamantra
from vibe_core.gateway import chat as gateway_chat

# Setup Logging
logging.basicConfig(level=logging.INFO)

class TestIntelligentSankirtan(unittest.TestCase):
    
    def test_routing_time(self):
        """Test routing 'time' keyword to Yamaraja."""
        print("\n\n🕒 CHATTING ABOUT TIME")
        print("========================")
        
        # Using Gateway Interface
        response = gateway_chat("What is the current time?")
        
        print(f"Response:\n{response.output}")
        
        self.assertTrue(response.success)
        self.assertIn("YAMARAJA RESPONDS", response.output)
        self.assertIn("via Universal Bridge", response.output)

    def test_routing_storage(self):
        """Test routing 'scan/disk' keyword to Prithu."""
        print("\n\n💾 CHATTING ABOUT STORAGE")
        print("========================")
        
        # Using Gateway Interface
        response = gateway_chat("Scan the disk for files")
        
        print(f"Response:\n{response.output}")
        
        self.assertTrue(response.success)
        self.assertIn("PRITHU RESPONDS", response.output) # Keyword: "scan" -> Prithu

    def test_routing_fallback(self):
        """Test routing unknown keyword to Narada (Messenger)."""
        print("\n\n🗣️ CHATTING UNKNOWN")
        print("========================")
        
        # Using Gateway Interface
        response = gateway_chat("Hello universe!")
        
        print(f"Response:\n{response.output}")
        
        self.assertTrue(response.success)
        self.assertIn("NARADA RESPONDS", response.output) # Fallback

if __name__ == '__main__':
    unittest.main()
