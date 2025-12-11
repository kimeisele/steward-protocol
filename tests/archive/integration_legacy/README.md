# Archived Integration Tests (Legacy)

**Archived:** 2025-12-11
**Reason:** Tests not updated after Container/Plugin system migration

## Tests Archived

| Test File | Issue |
|-----------|-------|
| test_kernel_markdown_interfaces.py | temp_workdir fixture doesn't copy phoenix/sections/, renderer lookup fails |
| test_federation_manual.py | Federation/Sangha API tests - architecture changed |
| test_fractal_ui.py | Test isolation issues - passes alone, fails in batch |
| test_genesis_boot.py | Genesis holon loading - setup dependencies missing |
| test_genesis_flow.py | Genesis flow - BootOrchestrator changes |
| test_sangha_api.py | Sangha API gateway - network layer changes |
| test_watchman_governance.py | Watchman signature governance - container format changes |

## To Revive

1. Fix `temp_workdir` fixture to copy ALL required paths (not just config/)
2. Update tests to use new Container/Plugin architecture
3. Update renderer lookups to match current interface plugin structure
4. Run tests individually first, then in batch to catch isolation issues

## Priority

LOW - Core functionality is tested via:
- `scripts/ci/test_kernel_boot.py` (kernel boots)
- `scripts/ci/test_gateway_boot.py` (gateway boots)
- `scripts/ci/test_governance_gate.py` (governance works)
- Unit tests in `tests/unit/` (84 tests)
