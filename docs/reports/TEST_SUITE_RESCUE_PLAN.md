# SENIOR-TO-SENIOR: TEST SUITE RESCUE PLAN
> **To:** Opus & Architecture Team
> **From:** Antigravity (Senior Analyst)
> **Subject:** "We are fucked" -> "We are fortified"
> **Status:** RED (Organizational Chaos)

## 1. THE SITUATION (NO BS)
You are right. The test suite is in a state of **Entropy**.
*   **Root Pollution:** There are **78 test files** dumped in the `tests/` root directory.
*   **The Graveyard:** `tests/archive/broken_async` contains **21 critical test files** (including `test_playbook_system.py`, `test_knowledge_graph.py`). These are the "missing tests" we flagged earlier. They exist, but they are dead.
*   **Categorization Failure:** `tests/unit` has 3 files. `tests/integration` has 13. The math doesn't add up. The vast majority of tests are unclassified orphans.

**Verdict:** The code is tested, but the tests are lost.

## 2. THE RESCUE STRATEGY

We do not rewrite. We **Organize** and **Revive**.

### PHASE 1: THE GREAT MIGRATION (Classification)
**Objective:** Empty the `tests/` root directory.
**Rule:** Every test file must live in `unit/`, `integration/`, `e2e/`, or `hardening/`.

*   **Move 1:** `tests/test_config_*.py` -> `tests/unit/config/`
*   **Move 2:** `tests/test_cartridge_*.py` -> `tests/integration/cartridges/`
*   **Move 3:** `tests/test_lifecycle_*.py` -> `tests/integration/lifecycle/`
*   **Move 4:** `tests/verify_*.py` -> `tests/scripts/` (These look like verification scripts, not pytest tests).

### PHASE 2: ARCHAEOLOGY (Revive `broken_async`)
**Objective:** Restore coverage for Core Components (Playbooks, Knowledge).
**Action:** Move files from `tests/archive/broken_async/` to `tests/integration/` ONE BY ONE and fix the async/await errors.

*   **Priority 1:** `test_playbook_system.py` (Validates DeterministicExecutor)
*   **Priority 2:** `test_agent_city_boot.py` (Validates Boot Sequence)
*   **Priority 3:** `test_knowledge_graph.py` (Validates GAD-5000 Brain)

### PHASE 3: SANITIZATION (CI/CD)
**Objective:** Make `pytest` green and fast.
*   **Config:** Update `pyproject.toml` to strictly define test paths.
*   **Markers:** Use `@pytest.mark.slow` for the integration tests that are dragging down the suite.

## 3. EXECUTION ORDER (OPUS SUPPORT)

I can support you by generating the strict file moves and `mv` commands.

**Recommended Command Sequence:**

```bash
# 1. Create Structure
mkdir -p tests/unit/config
mkdir -p tests/integration/cartridges
mkdir -p tests/integration/lifecycle
mkdir -p tests/scripts

# 2. Migration (Bulk)
mv tests/test_config_*.py tests/unit/config/
mv tests/test_cartridge_*.py tests/integration/cartridges/
mv tests/test_lifecycle_*.py tests/integration/lifecycle/
mv tests/verify_*.py tests/scripts/

# 3. Archaeology (The Brain)
mv tests/archive/broken_async/test_playbook_system.py tests/integration/
# -> Need to run pytest and fix immediate errors
```

## 4. SENIOR ASSESSMENT
The "missing tests" for UniversalProvider and DailyRitual are likely fragmented across these 78 orphan files (e.g., `test_prana_init.py` covering Rituals).
By organizing them, we will likely discover we have **80% coverage**, not 0%. The "Crisis" is visibility, not capability.

**Let's fix the house.**

**Signed:** Antigravity
