# OPUS-021: Test Architecture & Quality Assurance

> **Status**: 📋 DOCUMENTATION
> **Date**: 2025-12-10
> **Author**: Antigravity
> **Depends On**: Phoenix Config (quality.yaml)

<!-- @HARNESS
files:
  - path: tests/conftest.py
    required: true
  - path: config/quality.yaml
    required: true
  - path: vibe_core/plugins/test_orchestration/fixtures.py
    required: true
tests:
  - tests/unit
  - tests/integration
wiring:
  - pattern: "_load_quality_config"
    in: tests/conftest.py
  - pattern: "TestKernel"
    in: tests/conftest.py
  - pattern: "profiles:"
    in: config/quality.yaml
absent:
  - pattern: "hardcoded"
    in: tests/conftest.py
-->

---

## Executive Summary

Die Test Suite ist **config-driven** via `config/quality.yaml`. Keine hardcoded Werte in Python. Alles kommt aus Phoenix Config.

---

## Test Directory Structure

```
tests/
├── conftest.py          ← Zentrale Config, Fixtures, Hooks
├── unit/                ← Isolierte Unit Tests (<1s)
├── integration/         ← Kernel + Plugins Tests
├── fractal/             ← Fraktale Pattern Tests
└── hardening/           ← Stress/Security/Chaos Tests
```

---

## Config-Driven Testing (quality.yaml)

### Test Profiles

```yaml
# config/quality.yaml
test:
  profiles:
    fast:           # Default für Dev
      exclude_markers: [slow, integration, e2e]
      timeout: 30
      fail_fast: true

    full:           # Alles mit Coverage
      timeout: 300
      coverage: true

    ci:             # CI-optimiert
      fail_fast: true
      timeout: 300

    unit:           # Nur Unit Tests
      markers: [unit]
      exclude_markers: [integration, e2e, slow]

    integration:    # Nur Integration
      markers: [integration]
      workers: 1    # Sequential für Stabilität
```

### Usage

```bash
# Development (schnell)
pytest

# Mit spezifischem Profil
pytest --test-profile=full
pytest --test-profile=ci
pytest --test-profile=integration
```

---

## Fixtures (conftest.py)

### Kernel Fixtures

| Fixture | Beschreibung | Use Case |
|---------|--------------|----------|
| `test_kernel` | Minimal, keine Plugins | Unit Tests |
| `permissive_kernel` | Alle Ops erlaubt | Feature Tests |
| `governance_kernel` | Mit Governance Stack | Steward Tests |
| `recording_kernel` | Zeichnet Hooks auf | Verification |
| `cached_kernel` | Shared im Modul | Performance |
| `fresh_kernel` | Frische Instanz | State Tests |

### Agent Fixtures

| Fixture | Beschreibung | oath_sworn |
|---------|--------------|------------|
| `compliant_agent` | Vollständig konform | `True` |
| `no_oath_agent` | Kein Oath Attribut | `None` |
| `false_oath_agent` | Oath = False | `False` |

### Usage in Tests

```python
def test_governance_blocks_no_oath(governance_kernel, no_oath_agent):
    """Agent without oath should be rejected."""
    with pytest.raises(ValueError):
        governance_kernel.register_agent(no_oath_agent)

def test_compliant_agent_accepted(governance_kernel, compliant_agent):
    """Compliant agent should register successfully."""
    governance_kernel.register_agent(compliant_agent)
    assert compliant_agent.agent_id in governance_kernel.agent_registry
```

---

## Auto-Markers (pytest_collection_modifyitems)

Tests werden automatisch gemarkert basierend auf Location:

```python
# tests/conftest.py:91-105
if "hardening" in str(item.fspath):
    item.add_marker(pytest.mark.hardening)
    item.add_marker(pytest.mark.slow)

if "integration" in str(item.fspath):
    item.add_marker(pytest.mark.integration)
```

| Directory | Auto-Markers |
|-----------|--------------|
| `tests/unit/` | (none - use explicit) |
| `tests/integration/` | `@pytest.mark.integration` |
| `tests/hardening/` | `@pytest.mark.hardening`, `@pytest.mark.slow` |

---

## Kernel Presets (quality.yaml)

```yaml
test:
  fixtures:
    kernel_presets:
      minimal:
        description: "Bare kernel, no plugins, memory ledger"
        plugins: []

      permissive:
        description: "All operations allowed, no governance"
        plugins: ["test_mode"]

      governance:
        description: "Full governance stack enabled"
        plugins: ["steward_protocol", "vedic_governance"]

      recording:
        description: "Records all hook calls for assertions"
        plugins: ["test_orchestration"]
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

```python
# Isoliert, schnell, keine externen Dependencies
def test_hash_determinism():
    """SHA256 hash should be deterministic."""
    content = b"test content"
    assert hashlib.sha256(content).hexdigest() == hashlib.sha256(content).hexdigest()
```

### Integration Tests (`tests/integration/`)

```python
# Brauchen Kernel, Plugins, oder externe Systeme
def test_kernel_boot(fresh_kernel):
    """Kernel should boot with plugins."""
    fresh_kernel.boot()
    assert fresh_kernel.status == KernelStatus.RUNNING
```

### Hardening Tests (`tests/hardening/`)

```python
# Stress, Chaos, Security
@pytest.mark.slow
def test_stress_1000_tasks(governance_kernel):
    """Kernel should handle 1000 concurrent tasks."""
    for i in range(1000):
        governance_kernel.submit_task(SimpleTask(f"task_{i}"))
```

---

## CI Integration

### Workflows (quality.yaml)

```yaml
ci:
  workflows:
    - name: Lint & Format Check
      file: steward-ci.yml
      required: true

    - name: Integration Tests
      file: integration-tests.yml
      required: true
```

### Pre-Commit Guards

```yaml
guards:
  block_requirements_txt: true      # Keine requirements.txt in Agents
  block_hardcoded_data_paths: true  # Keine Path("data/...")
  ruff_autoformat: true             # Auto-Format
  ruff_critical_check: true         # Critical Errors blocken
```

---

## Test Orchestration Plugin

```
vibe_core/plugins/test_orchestration/
├── plugin_main.py     ← TestOrchestrationPlugin
└── fixtures.py        ← TestKernel, TestAgents, TestContext
```

### TestKernel Factory

```python
# fixtures.py
class TestKernel:
    @staticmethod
    def minimal() -> RealVibeKernel:
        """Minimal kernel without plugins."""
        return RealVibeKernel(ledger_path=":memory:", load_plugins=False)

    @staticmethod
    def with_governance() -> RealVibeKernel:
        """Kernel with governance stack."""
        kernel = RealVibeKernel(ledger_path=":memory:")
        # Load steward_protocol, vedic_governance
        return kernel
```

---

## Running Tests

```bash
# Quick Feedback (default)
pytest

# Full Suite + Coverage
pytest --test-profile=full

# CI Mode
pytest --test-profile=ci

# Nur Unit Tests
pytest --test-profile=unit

# Nur Integration
pytest --test-profile=integration

# Spezifische Tests
pytest tests/unit/test_container_loader.py -v
pytest tests/integration/test_container_integrity.py -v

# Mit bestimmten Markers
pytest -m "security"
pytest -m "not slow"
```

---

## Summary

| Frage | Antwort |
|-------|---------|
| Wo ist die Config? | `config/quality.yaml` |
| Wo sind Fixtures? | `tests/conftest.py` + `test_orchestration/fixtures.py` |
| Wie wähle ich Profile? | `pytest --test-profile=<name>` |
| Welche Kernel Presets? | minimal, permissive, governance, recording |
| Welche Agent Fixtures? | compliant, no_oath, false_oath |
| Wie werden Tests gemarkert? | Auto (directory) oder explizit (`@pytest.mark.X`) |

**Die Test Suite ist kein Black Box - alles ist config-driven via Phoenix.**
