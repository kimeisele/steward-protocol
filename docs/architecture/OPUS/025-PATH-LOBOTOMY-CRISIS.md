# OPUS-025: PATH LOBOTOMY CRISIS

> **Status:** CRITICAL - System Integrity Compromised
> **Created:** 2025-12-12
> **Severity:** P0 - Architectural Foundation Broken

---

## Executive Summary

Das System ist **LOBOTOMIERT**. Die Config-Architektur (PhoenixConfig.paths) existiert und ist vollstaendig, aber der Code ignoriert sie und benutzt hardcodierte Pfade. Das fuehrt zu:

1. **State-Leaks**: Ein `data/` Verzeichnis mit Ledger, Governance-Proposals, Keys, etc.
2. **Broken Verification**: 5 von 7 Ledger-Events haben "malformed_signature"
3. **Uncontrollable State**: Daten werden an Orten geschrieben die niemand kontrolliert

---

## Das Problem

### Symptom: Das `data/` Verzeichnis

```
data/
├── audits/wiring_audit_latest.md
├── census/census_2025-12-04.json
├── dhruva/genesis_block.json
├── diplomatic_bag/invitation_*.json
├── federation/pokedex.json
├── governance/
│   ├── proposals/ (7 proposals)
│   ├── votes/votes.jsonl
│   └── executed/ (2 executed)
├── ledger/audit_trail.jsonl  ← 5/7 FAILED verifications!
├── models/sentence-transformers/
├── registry/
├── reports/
├── vibe_ledger.db.backup
└── vibe_ledger.db.bak
```

### Wurzelursache: Wiring wurde nie durchgefuehrt

**Die Architektur existiert:**
- `config/paths.yaml` - Definiert alle Pfade mit `{root}` Variablen
- `vibe_core/phoenix/sections/paths/section_main.py` - PathsConfig Klasse
- Kommentar: "This section eliminates all 105 hardcoded Path() violations"

**Aber der Code ignoriert sie:**

| PhoenixConfig.paths benutzt | Hardcoded `Path("data/...")` |
|-----------------------------|------------------------------|
| ~10 Stellen | **40+ Stellen** |

---

## Betroffene Dateien (Hardcoded Path Violations)

### Kritisch (Core System)

| Datei | Zeile | Hardcoded Path | Sollte sein |
|-------|-------|----------------|-------------|
| `vibe_core/ledger.py` | 132 | `"data/vibe_ledger.db"` | `config.paths.data.vibe_ledger` |
| `vibe_core/boot_orchestrator.py` | 77 | `"data/vibe_ledger.db"` | `config.paths.data.vibe_ledger` |
| `vibe_core/kernel_impl.py` | 179 | `"data/vibe_ledger.db"` (fallback) | Kein Fallback - Fehler werfen |
| `vibe_core/config/schema.py` | 219 | `"data/registry/"` | `config.paths.data.registry` |

### Hoch (Agent Tools)

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `civic/tools/vault_tool.py` | 91 | `Path("data/security/master.key")` |
| `civic/tools/vault.py` | 113 | `Path("data/security/master.key")` |
| `civic/tools/economy.py` | 52, 65 | `Path("data/economy.db")` |
| `civic/tools/bank_tool.py` | 51 | `Path("data/economy.db")` |
| `civic/tools/ledger_tool.py` | 64 | `Path("data/economy.db")` |
| `civic/tools/lifecycle_manager.py` | 108 | `"data/registry/citizens.json"` |
| `civic/registry_agent.py` | 38 | `Path("data/registry/citizens.json")` |
| `civic/economy_agent.py` | 245 | `"data/registry/licenses.json"` |
| `auditor/tools/watchdog_tool.py` | 37, 40 | `Path("data/ledger/*.jsonl")` |
| `herald/tools/scout_tool_legacy.py` | 26 | `Path("data/federation/pokedex.json")` |
| `herald/core/agency_director.py` | 107 | `Path("data/reports")` |
| `archivist/tools/ledger_visualizer.py` | 32 | `Path("data/ledger/audit_trail.jsonl")` |

### Mittel (Provider/LLM)

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `llm/local_llama_provider.py` | 21 | `Path("data/models")` |
| `cortex/engines/semantic_engine.py` | 76-80 | `"data/models"` |

### Plugins

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `plugins/doctor/plugin_main.py` | 42, 48 | `"data/vibe_ledger.db"` |
| `plugins/interface/renderers/git.py` | 44 | `"data/registry/citizens.json"` |

---

## Warum ist Watchman nicht eingeschritten?

Watchman HAT einen AST-Visitor der `Path("data/...")` Calls erkennt:

```python
# watchman/tools/standards_inspection.py:71
class PathDataCallVisitor(ast.NodeVisitor):
    """AST visitor to detect Path("data/...") calls."""
```

**ABER:** Die Ergebnisse wurden nie in Fixes umgesetzt. Der Visitor wurde gebaut, aber die Migration nie durchgefuehrt.

---

## Impact

### 1. State-Leaks
- Governance Proposals werden in `data/governance/` geschrieben
- Ledger-Events in `data/ledger/`
- Federation-Daten in `data/federation/`
- **Niemand kontrolliert diese Pfade**

### 2. Broken Verification
```json
{"status": "VERIFIED"}  // 1 von 7
{"status": "FAILED", "reason": "malformed_signature"}  // 6 von 7
```

### 3. Container-Inkompatibilitaet
- PhoenixConfig sollte die Single Source of Truth sein
- Aber Container/Deployments wissen nichts von den hardcoded Pfade
- Pfade sind nicht konfigurierbar

### 4. Testing-Chaos
- Tests erstellen Dateien in `data/`
- Diese bleiben zwischen Runs bestehen
- Non-deterministic Test Results

---

## Holistische Loesung

### Phase 1: STOP THE BLEEDING (Sofort)

1. **Kernel-Schutz erweitern**: Alle `Path("data/...")` Calls als Violation markieren
2. **Pre-commit Hook**: Blockiert neue hardcoded Pfade
3. **CI Gate**: Prueft auf Regressions

### Phase 2: INJECT CONFIG (Systematisch)

Jede betroffene Datei muss:

```python
# VORHER (VERBOTEN):
class SomeTool:
    DB_PATH = Path("data/economy.db")

# NACHHER (RICHTIG):
class SomeTool:
    def __init__(self, config: PhoenixConfig = None):
        self._config = config or get_config()

    @property
    def db_path(self) -> Path:
        return self._config.paths.data.resolve("economy_db")
```

### Phase 3: DEPENDENCY INJECTION (Clean Architecture)

1. **Kernel injiziert Config** bei Agent-Initialisierung
2. **Agents nutzen Config** statt hardcoded Pfade
3. **Tools erhalten Config** via Constructor Injection

### Phase 4: CONTAINER FORMAT (Optional)

Wenn PhoenixConfig selbst ein Vibe Container wird:
- `config/paths.yaml` wird Teil des Container-Manifests
- Deployment kann Pfade ueberschreiben
- Isolierte Instanzen moeglich

---

## Migration-Reihenfolge

| Prioritaet | Datei | Grund |
|------------|-------|-------|
| P0 | `ledger.py`, `boot_orchestrator.py`, `kernel_impl.py` | Core System |
| P1 | `civic/tools/*.py` | Governance State |
| P2 | `auditor/tools/*.py`, `archivist/tools/*.py` | Verification |
| P3 | `herald/`, `plugins/` | Features |
| P4 | `semantic_engine.py`, `local_llama_provider.py` | AI/ML |

---

## Verification

Nach der Migration:

```bash
# Sollte 0 Violations zurueckgeben
python -c "
from vibe_core.cartridges.system.watchman.tools.standards_inspection import PathDataCallVisitor
# Run on vibe_core/
"

# data/ Verzeichnis sollte leer oder nicht existent sein
ls data/  # Erwartung: Error oder leerer Output
```

---

## Architektur-Entscheidung

**ADR-025: Path Configuration via PhoenixConfig**

**Status:** Accepted

**Context:**
Der Code hat 40+ hardcoded `Path("data/...")` Calls obwohl PhoenixConfig.paths existiert.

**Decision:**
1. ALLE Pfade MUESSEN via `config.paths.*` abgerufen werden
2. Hardcoded Pfade sind VERBOTEN (CI blockiert)
3. Fallbacks zu "data/" sind VERBOTEN
4. Config wird via Dependency Injection bereitgestellt

**Consequences:**
- Mehr Boilerplate bei Tool-Initialisierung
- Aber: Vollstaendige Kontrolle ueber State-Location
- Container-ready
- Testbar

---

## @HARNESS

```yaml
files:
  - path: config/paths.yaml
    required: true
  - path: vibe_core/phoenix/sections/paths/section_main.py
    required: true
  - path: vibe_core/ledger.py
    required: true
tests:
  - tests/unit/test_config_paths.py
wiring:
  - pattern: "config.paths.data"
    in: vibe_core/kernel_impl.py
absent:
  - pattern: 'Path\("data/'
    in: vibe_core/ledger.py
  - pattern: '"data/vibe_ledger.db"'
    in: vibe_core/boot_orchestrator.py
```

---

## Status

| Aspekt | Status | Evidenz |
|--------|--------|---------|
| PathsConfig definiert | ✅ | config/paths.yaml |
| PathsConfig Section | ✅ | phoenix/sections/paths/section_main.py |
| Wiring durchgefuehrt | ❌ | 40+ hardcoded violations |
| CI Gate | ❌ | Kein Blocker fuer Path("data/") |
| Migration | ❌ | 0% |

---

*Erstellt: 2025-12-12 | Letzte Aktualisierung: 2025-12-12*
