# 📊 Steward Protocol Ledger Viewer

**Live verification dashboard for the immutable audit trail.**

## Overview

The Ledger Viewer provides real-time visualization of the Steward Protocol's immutable audit trail. Every action taken by HERALD, ARCHIVIST, and AUDITOR is cryptographically recorded and verified.

This viewer displays:
- **Total Events**: Count of all recorded actions
- **Verified Events**: Actions successfully cryptographically verified
- **Failed Verifications**: Actions that failed integrity checks
- **Verification Rate**: Overall trust percentage
- **Event Timeline**: Reverse-chronological list of all attestations

## Access the Viewer

**[📈 Open Live Ledger Viewer](ledger-viewer.html)**

## Trust Signal

The verification rate is your "Trust Signal":

| Rate | Trust Level | Meaning |
|------|-----------|---------|
| ≥95% | 🟢 HIGH | System operating normally |
| 80-94% | 🟡 MEDIUM | Minor issues detected |
| <80% | 🔴 LOW | Significant issues present |

## Technical Details

### Data Source

The viewer reads from the immutable JSONL ledger:

```
data/ledger/audit_trail.jsonl
```

Each line is a complete attestation:

```json
{
  "attestation_type": "event_verification",
  "auditor": "agent.vibe.archivist",
  "timestamp": "2025-11-23T12:13:38.954234+00:00",
  "target_event": {
    "event_type": "content_generated",
    "sequence_number": 1,
    "agent_id": "agent.steward.herald",
    "timestamp": "2025-11-23T10:15:30.123456+00:00"
  },
  "verification": {
    "verified": true,
    "signature": "MEUCIQDxK8X9vR4p2Z5n8K9q7C6b5A4m3L2k1J0i..."
  },
  "status": "VERIFIED"
}
```

### Event Types

| Type | Agent | Meaning |
|------|-------|---------|
| `content_generated` | HERALD | Content drafted and governance-checked |
| `content_published` | HERALD | Content published to social media |
| `content_rejected` | HERALD | Content failed governance checks |
| `strategy_planned` | HERALD | Campaign strategy generated |
| `system_error` | Any | System error occurred |

### Verification Status

| Status | Meaning |
|--------|---------|
| `VERIFIED` | ✅ Event cryptographically verified |
| `FAILED` | ❌ Event failed verification |
| `PENDING` | ⏳ Awaiting verification |

## Python API

Use the `LedgerVisualizer` tool to analyze the ledger programmatically:

```python
from archivist.tools.ledger_visualizer import LedgerVisualizer

# Initialize
viz = LedgerVisualizer()

# Get statistics
stats = viz.get_summary_statistics()
print(f"Verified: {stats['verified_count']}/{stats['total_events']}")

# Get trust score
trust = viz.get_trust_score()
print(f"Trust Level: {trust['trust_level']}")

# Get recent events
recent = viz.get_recent_events(limit=10)

# Generate report
report = viz.generate_json_report(output_path="dist/ledger_report.json")

# Validate integrity
validation = viz.validate_ledger_integrity()
print(validation["message"])
```

## Auto-Refresh

The viewer automatically refreshes every 30 seconds. No manual reload needed.

## Integration with CI/CD

The ledger viewer can be published to GitHub Pages or any static site:

```bash
# Generate current report
python -c "from archivist.tools.ledger_visualizer import generate_ledger_report; generate_ledger_report()"

# Publish to docs/
cp dist/ledger_report.json docs/
```

## Security

- The ledger file itself is **immutable** and cryptographically signed
- This viewer **reads but never modifies** the ledger
- All verification logic uses the same cryptographic functions as ARCHIVIST
- The viewer runs client-side in the browser (no server-side processing)

## What Does This Prove?

✅ **Transparency**: All actions are logged publicly
✅ **Accountability**: Every action is signed and verifiable
✅ **Immutability**: The ledger cannot be modified retroactively
✅ **Governance**: The system enforces its own rules
✅ **Trust**: You can verify the system's integrity yourself

---

**Steward Protocol** - Artificial Governed Intelligence
