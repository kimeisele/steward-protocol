# Test Suite Protocol Audit (TESTS.md)

**Mandate**: "Protocol instead of Concrete Classes". All tests must use `vibe_core.protocols` types for mocks/stubs.

## Strategy
- **P0**: Universal Protocols & Core (`tests/universal`, `tests/protocols`)
- **P1**: Unit Tests (`tests/unit`)
- **P2**: Naga Services (`tests/naga`)
- **P3**: Manas / Cortex (`tests/manas`)

## Status Ledger

### P0: Universal & Protocols
- [x] `tests/universal/test_sudarshana.py` (Refactored w/ `ServiceProtocol`)
- [x] `tests/universal/test_ramanujan.py` (Checked - No Mocks)
- [x] `tests/universal/test_mantra_loop.py` (Renamed Mock -> Reference)
- [x] `tests/protocols/test_contract_compliance.py` (The Enforcer - Passed)

### P1: Unit Tests (The Atoms)
- [x] `tests/unit/test_task_kernel.py` (Stubbed)
- [x] `tests/unit/test_process_manager.py` (Refactored: MagicMock -> StubMantraKernel)

### P2: Naga Services (The Guardians)
- [x] `tests/naga/test_prahlad.py` (Enforced SysState Enum)
- [x] `tests/naga/test_dwarapala.py` (Connected to NervousSystemProtocol)

### P3: Manas / Cortex (The Mind)
- [x] `tests/manas/test_memory_store.py` (Refactored w/ AkashicProtocol + State Reset)
- [x] `tests/manas/test_documentation_surface.py` (Documentation surface adapter/builder coverage)

## Rules
1. **No Ad-Hoc Mocks**: Use `class MockX(ProtocolX): ...`
2. **Strict Typing**: All test helpers must be typed.
3. **Ontology**: If it acts like a Service, it must BE a ServiceProtocol.
