
"""
VERIFY CENSUS - The Great Census Verification
=============================================

Tests the heuristic scanning capabilities (Phase 8).
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from vibe_core.mahamantra.substrate.scanner import get_scanner, FileStatus
from vibe_core.protocols.substrate.scanner import ScanConfig

# Dummy Orphan Content (Prithu-like)
PRITHU_PY = """
def save_data(data, path):
    # This looks like Prithu (Infrastructure)
    with open(path, "w") as f:
        f.write(data)
    print(f"Written to disk at {path}")
"""

# Dummy Orphan Content (Kapila-like)
KAPILA_PY = """
def analyze_metrics(metrics):
    # This looks like Kapila (Analysis)
    total = 0
    for m in metrics:
        total += m
    avg = total / len(metrics)
    return {"avg": avg, "count": len(metrics)}
"""

class TestCensus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Create test files
        self.prithu_path = self.base_path / "prithu_orphan.py"
        self.prithu_path.write_text(PRITHU_PY)
        
        self.kapila_path = self.base_path / "kapila_orphan.py"
        self.kapila_path.write_text(KAPILA_PY)
        
        # Configure scanner
        self.scanner = get_scanner()
        # Ensure we scan our temp dir
        self.scanner.set_config({
            "base_path": str(self.base_path),
            "include_dirs": ["."],
            "exclude_patterns": [],
            "detect_declarations": ["mahajana", "position"],
            "max_depth": 1
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_census_inference(self):
        """Test that scanner infers identity from OpCodes."""
        print("\n\n🕉️  CENSUS VERIFICATION")
        print("=======================")
        
        # 1. Scan Prithu Orphan
        print(f"Scanning {self.prithu_path}...")
        scanned_prithu = self.scanner.scan_file(str(self.prithu_path))
        
        print(f"Result: {scanned_prithu['status']}")
        inference = scanned_prithu.get('inference', {})
        print(f"Inference: {inference}")
        
        self.assertEqual(scanned_prithu['status'], FileStatus.INFERRED.value)
        self.assertEqual(inference.get('identity'), 'prithu')
        self.assertGreater(inference.get('score'), 0.3)
        print("✅ Prithu Identified correctly (Infrastructure Keywords)")

        # 2. Scan Kapila Orphan
        print(f"Scanning {self.kapila_path}...")
        scanned_kapila = self.scanner.scan_file(str(self.kapila_path))
        
        print(f"Result: {scanned_kapila['status']}")
        inference = scanned_kapila.get('inference', {})
        print(f"Inference: {inference}")
        
        self.assertEqual(scanned_kapila['status'], FileStatus.INFERRED.value)
        self.assertEqual(inference.get('identity'), 'kapila')
        print("✅ Kapila Identified correctly (Analysis Keywords)")
        
        print("\n✨ CENSUS VERIFIED!")

if __name__ == '__main__':
    unittest.main()
