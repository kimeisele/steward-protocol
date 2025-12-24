"""
Lightweight integration test for Shuddhi Service DI registration.
"""

import tempfile
import unittest
from pathlib import Path

from vibe_core.shuddhi.engine import ShuddhiEngine
from vibe_core.protocols.shuddhi import ShuddhiProtocol, ShuddhiStatus
from vibe_core.protocols.task import TaskProtocol
from vibe_core.di import ServiceRegistry


class TestShuddhiDIIntegration(unittest.TestCase):
    def setUp(self):
        ServiceRegistry.reset()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name) / "test_violation.py"

    def tearDown(self):
        self.temp_dir.cleanup()
        ServiceRegistry.reset()

        def test_di_registration_and_usage(self):

            """Test that ShuddhiProtocol can be registered and retrieved via DI."""

            # Registration (mimics BootOrchestrator)

            engine = ShuddhiEngine()

            ServiceRegistry.register(ShuddhiProtocol, engine)

            

            # Retrieval (mimics kernel.shuddhi)

            service = ServiceRegistry.require(ShuddhiProtocol)

    
        self.assertIsInstance(service, ShuddhiEngine)

        # Usage
        content = """
class Test:
    def method(self, x):
        with open("log", "w") as f:
            f.write(x)
"""
        self.test_path.write_text(content)
        result = service.purify(self.test_path, "unsafe_io_write")
        self.assertEqual(result.status, ShuddhiStatus.PURIFIED)


if __name__ == "__main__":
    unittest.main()
