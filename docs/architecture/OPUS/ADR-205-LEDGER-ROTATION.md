# ADR-205: Samsara Ledger Rotation

**Status**: DRAFT
**Date**: 2025-12-22
**Author**: Gemini (Senior Mode)
**Supersedes**: N/A
**Related**: GAD-000, OPUS-203, ADR-204

---

## Executive Summary

The `vibe_ledger.db` has grown to 76MB. While SQLite can handle this, the system's "Heartbeat" (Pulse) and "Audit" (Integrity) operations frequently scan the entire event history. This creates a "Karmic Burden" that slows down the OS.

**Decision**: Implement a "Samsara" rotation strategy: Move "Old Karma" (historical events) into an archive database while keeping "Active Karma" (recent events) in a high-speed hot-ledger.

---

## Problem Statement

1.  **Latency**: `get_all_events()` and integrity checks take increasing time as the ledger grows.
2.  **Memory Pressure**: Loading large event lists for the Auditor Aditya causes spikes in RAM usage.
3.  **Physical Bloat**: The single DB file becomes a liability for backup and Git-tracking.

---

## Decision

### The Samsara Rotation
1.  **Threshold Trigger**: When the Hot Ledger exceeds N events (e.g., 5000), a rotation is triggered.
2.  **Cryptographic Linkage**: The last event of the Archive Ledger becomes the "Genesis Reference" for the next Hot Ledger. The hash chain remains unbroken across files.
3.  **Active/Archive Separation**: 
    - `Hot Ledger`: Stays in `data/vibe_ledger.db`. Used for daily operations.
    - `Archive Ledgers`: Moved to `data/ledger/archive/vibe_ledger_YYYYMMDD.db`.
4.  **Sovereign Pruning**: Only the infrastructure (RealVibeKernel) can trigger rotation. Agents are unaware of the physical split.

---

## Implementation Plan

### Phase 1: Rotation Engine
- Update `SQLiteLedger` to support `rotate()` and `genesis_from_archive()`.
- Implement atomic file-moving for archives.

### Phase 2: Kernel Integration
- Add `check_ledger_size()` to the Kernel's background maintenance cycle.
- Trigger rotation during `CLEANUP` phase of the heartbeat.

---

## Validation

- GAD-000 integrity checks must pass across the archive/hot boundary.
- Pulse speed must return to < 10ms regardless of total system age.
