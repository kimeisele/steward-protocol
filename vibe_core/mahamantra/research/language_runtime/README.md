# Language Runtime (Research)

## Purpose
This folder is a **structured research track** for moving the language engine
from prototype mode toward production readiness, without touching core
production orchestration prematurely.

## Design Rule
Do **not** rebuild timing/orchestration.

We reuse existing runtime infrastructure:
- `VenuService` (heartbeat loop)
- `VenuOrchestratorProtocol` (shared flute dispatcher)
- `DIWSubscriberProtocol` (tick event interface)

## Modules
- `contracts.py`: typed runtime envelopes and tick payloads
- `venu_bridge.py`: adapter from shared DIW events to runtime tick snapshots
- `session.py`: thin session wrapper that combines generation output + tick context

## Why this structure
1. Keeps research isolated from production modules.
2. Avoids orchestration duplication (no second clock, no parallel scheduler).
3. Creates clean seams for progressive hardening and eventual migration.

## Planned path to production
1. Prove stable contracts (`RuntimeTick`, `RuntimeEnvelope`) in research tests.
2. Integrate session wrapper behind feature flag in one non-critical entry path.
3. Promote modules from `research/language_runtime` to production package when
   observability + determinism + compatibility gates are green.
