#!/usr/bin/env python3
"""
Ouroboros Violation Ingestion - CI/CD Script

Ingests violations from watchman_report.json into Knowledge Graph.
This closes the feedback loop: CI finds violations → KG learns → System heals.

Pattern: Same as run_watchman_inspection.py
- Direct imports (no kernel overhead)
- Reads existing report
- Writes to Prakriti's Knowledge Graph
"""

import json
import sys
from pathlib import Path

from vibe_core.ouroboros.ingestion import ViolationIngester, ViolationSource

# Boot Prakriti (registers KG in ServiceRegistry)
from vibe_core.state.prakriti import Prakriti

print("🐍 OUROBOROS: Ingesting violations into Knowledge Graph...")

# Check for report
report_path = Path("watchman_report.json")
if not report_path.exists():
    print("⚠️  No watchman_report.json found - nothing to ingest")
    sys.exit(0)

# Boot Prakriti (this registers KG automatically)
prakriti = Prakriti()

# Load violations
report = json.loads(report_path.read_text())
violations = report.get("violations", [])

if not violations:
    print("✅ No violations to ingest")
    sys.exit(0)

print(f"📥 Found {len(violations)} violations to ingest")

# Ingest via ViolationIngester
ingester = ViolationIngester()
count = 0

for v in violations:
    try:
        ingester.kg.add_violation(
            file_path=v.get("file_path", "unknown"),
            line=v.get("line_number", 0),
            rule_id=v.get("rule_id", "UNKNOWN"),
            message=v.get("message", ""),
            has_remedy=v.get("has_remedy", False),
        )
        count += 1
    except Exception as e:
        print(f"⚠️  Failed to ingest: {e}")

# Persist to disk
prakriti.save_knowledge()

print(f"✅ Ingested {count} violations into Knowledge Graph")
print("📁 Persisted to: .prakriti/knowledge.json")
sys.exit(0)
