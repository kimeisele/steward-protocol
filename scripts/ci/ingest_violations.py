#!/usr/bin/env python3
"""
Ouroboros Violation Ingestion - CI/CD Script

Ingests violations from watchman_report.json into persistent storage.
This closes the feedback loop: CI finds violations → persisted → System heals.

Pattern: Direct file persistence (no kernel overhead)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

print("🐍 OUROBOROS: Ingesting violations...")

# Check for report
report_path = Path("watchman_report.json")
if not report_path.exists():
    print("⚠️  No watchman_report.json found - nothing to ingest")
    sys.exit(0)

# Load violations
report = json.loads(report_path.read_text())
violations = report.get("violations", [])

if not violations:
    print("✅ No violations to ingest")
    sys.exit(0)

print(f"📥 Found {len(violations)} violations to ingest")

# Persistence path (OUROBOROS state)
state_dir = Path(".vibe/state/ouroboros")
state_dir.mkdir(parents=True, exist_ok=True)
violations_file = state_dir / "violations.jsonl"

# Append violations to JSONL (append-only log)
ingested = 0
with open(violations_file, "a") as f:
    for v in violations:
        record = {
            "ingested_at": datetime.utcnow().isoformat(),
            "file_path": v.get("file_path", "unknown"),
            "line": v.get("line_number"),
            "rule_id": v.get("rule_id", "UNKNOWN"),
            "message": v.get("message", ""),
            "severity": v.get("severity", "MEDIUM"),
            "has_remedy": v.get("has_remedy", False),
            "agent": v.get("agent", "watchman"),
        }
        f.write(json.dumps(record) + "\n")
        ingested += 1

print(f"✅ Ingested {ingested} violations")
print(f"📁 Persisted to: {violations_file}")

# Summary stats
total_lines = sum(1 for _ in open(violations_file)) if violations_file.exists() else 0
print(f"📊 Total violations in log: {total_lines}")

sys.exit(0)
