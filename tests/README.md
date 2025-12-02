# Test Suite Documentation

> **Status:** Reorganization in progress
> **Last Audit:** 2025-12-02

---

## Current Structure (As-Is)

```
tests/
├── *.py                 # 29 files - NEEDS REORGANIZATION
├── hardening/           # 6 files - Security-focused (OK)
├── integration/         # 9 files - System integration (OK)
└── archive/             # Legacy tests (deprecated)
```

**Problem:** Root `tests/` directory contains mixed concerns - lifecycle, knowledge, agents, playbooks all in one folder.

---

## Target Structure (To-Be)

```
tests/
├── conftest.py                    # Shared fixtures
├── README.md                      # This file
│
├── unit/                          # Fast, isolated tests
│   ├── kernel/                    # Kernel core logic
│   ├── agents/                    # Individual agent tests
│   └── utils/                     # Utility function tests
│
├── integration/                   # Cross-component tests (EXISTS)
│   ├── test_kernel_boot.py
│   ├── test_kernel_markdown_interfaces.py
│   ├── test_event_bus_integration.py
│   └── ...
│
├── hardening/                     # Security tests (EXISTS)
│   ├── test_constitutional_enforcement.py
│   ├── test_governance_security.py
│   ├── test_ledger_acid.py
│   └── test_red_team_attacks.py
│
├── e2e/                           # End-to-end scenarios
│   ├── test_ambassador_end_to_end.py
│   └── test_live_fire.py
│
└── archive/                       # Deprecated (EXISTS)
    └── legacy_*/
```

---

## Test Categories

### By Domain

| Domain | Files | Target Location |
|--------|-------|-----------------|
| **Kernel** | kernel_boot, kernel_markdown_interfaces, lifecycle_* | `integration/` or `unit/kernel/` |
| **Security** | constitutional_enforcement, governance_security, ledger_acid, red_team_attacks, crypto_verification, visa_protocol | `hardening/` |
| **Knowledge** | knowledge_graph, knowledge_integration, knowledge_resolver, semantic_auditor | `unit/knowledge/` or `integration/` |
| **Agents** | gajendra_*, ambassador_*, herald_*, scribe_*, cartridge_* | `unit/agents/` |
| **Playbook** | playbook_execution, playbook_system | `integration/` |
| **E2E** | live_fire, ambassador_end_to_end | `e2e/` |

### By Test Type

| Type | Description | Location |
|------|-------------|----------|
| **Unit** | Single component, no I/O, mocked dependencies | `unit/` |
| **Integration** | Multiple components, real dependencies | `integration/` |
| **Hardening** | Security, attack simulation, constitutional compliance | `hardening/` |
| **E2E** | Full system scenarios, real kernel | `e2e/` |

---

## Migration Checklist

Files to move from `tests/` root:

- [ ] `test_lifecycle_*.py` (3 files) → `unit/kernel/` or `integration/`
- [ ] `test_knowledge_*.py` (3 files) → `unit/knowledge/`
- [ ] `test_gajendra_*.py` (2 files) → `unit/agents/`
- [ ] `test_playbook_*.py` (2 files) → `integration/`
- [ ] `test_scribe_generation.py` → `unit/agents/`
- [ ] `test_ambassador_end_to_end.py` → `e2e/`
- [ ] `test_live_fire.py` → `e2e/`
- [ ] `test_*_integration.py` → `integration/`

Files to evaluate for archival:
- [ ] `test_roadmap.py` - May be outdated
- [ ] `test_phase3_integration.py` - Phase-specific?

---

## Writing New Tests

### Naming Convention

```
test_<component>_<behavior>.py
```

Examples:
- `test_kernel_boot.py` - Kernel boot behavior
- `test_scribe_render_agents.py` - SCRIBE agent rendering

### Test Structure

```python
"""
<Component> Tests: <What is being tested>
============================================
Brief description of test scope.
"""

import pytest
from <module> import <component>

class Test<Component><Behavior>:
    """Tests for <specific behavior>."""

    def test_<scenario>_<expected_outcome>(self):
        """<Action> should <result>."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...
```

### Fixtures

Shared fixtures are in `conftest.py`:
- `temp_workdir` - Temporary working directory
- `kernel` - Unbooted kernel instance
- `booted_kernel` - Fully booted kernel

---

## Running Tests

```bash
# All tests
python -m pytest tests/

# By category
python -m pytest tests/integration/
python -m pytest tests/hardening/

# Specific test
python -m pytest tests/integration/test_kernel_boot.py

# With coverage
python -m pytest --cov=vibe_core tests/
```

---

## Notes

- **NO MOCKS** for integration tests - use real components
- **Hardening tests** may be slow - run separately in CI
- **Archive** folder contains deprecated tests - do not run
