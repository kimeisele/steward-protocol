# OPUS-025: PATH LOBOTOMY CRISIS

> **Status:** CRITICAL - System Integrity Compromised
> **Created:** 2025-12-12
> **Last Updated:** 2025-12-12
> **Severity:** P0 - Architectural Foundation Broken
> **Scope:** Audit all path handling against PhoenixConfig.paths

<!-- @HARNESS
files:
  - path: config/paths.yaml
    required: true
  - path: vibe_core/phoenix/sections/paths/section_main.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/runtime/boot_sequence.py
    required: true
  - path: vibe_core/ledger.py
    required: true
  - path: vibe_core/boot_orchestrator.py
    required: true
tests:
  - tests/unit/test_config_paths.py
  - tests/integration/test_kernel_boot.py
wiring:
  - pattern: "paths.data.resolve"
    in: vibe_core/kernel_impl.py
  - pattern: "paths.system.resolve"
    in: vibe_core/kernel_impl.py
absent:
  - pattern: 'paths\.data\.[a-z_]+[^(]'
    in: vibe_core/kernel_impl.py
  - pattern: 'Path\("data/'
    in: vibe_core/ledger.py
  - pattern: '"data/vibe_ledger.db"'
    in: vibe_core/boot_orchestrator.py
  - pattern: '"/tmp/vibe_os'
    in: vibe_core/kernel_impl.py
  - pattern: '\.vibe.*vibe\.db'
    in: vibe_core/runtime/boot_sequence.py
config:
  - section: paths
-->

## Status

| Aspekt | Status | Evidenz |
|--------|--------|---------|
| PathsConfig definiert | ✅ | `config/paths.yaml` |
| Template-Variablen funktionieren | ✅ | `resolve()` Methode existiert |
| Code benutzt resolve() konsistent | ❌ | 3+ Stellen ohne resolve() |
| Hardcoded `data/` Pfade eliminiert | ❌ | 40+ Violations |
| Hardcoded `/tmp/vibe_os` eliminiert | ❌ | 15+ Violations |
| `.vibe` Schatten-Pfade in Config | ❌ | 6+ Violations |
| Python Defaults = YAML Defaults | ❌ | Inkonsistente Defaults |
| CI Gate aktiv | ❌ | Nicht implementiert |
| Migration abgeschlossen | ❌ | 0% |

---

## Executive Summary

Das System ist **LOBOTOMIERT**. Die Config-Architektur (PhoenixConfig.paths) existiert, aber:

1. **Code benutzt Pfade OHNE `resolve()`** → erstellt buchstaeblich Ordner namens `{root}`
2. **Code ignoriert PhoenixConfig komplett** → hardcoded Pfade ueberall
3. **Drei Schatten-Dateisysteme** existieren parallel:
   - `data/` - Governance, Ledger, Registry
   - `/tmp/vibe_os/` - Runtime, Agents, Lineage
   - `.vibe/` - Boot State, Memory, Tasks
4. **Python Defaults untergraben YAML** → False Safety

---

## GAD-000 Compliance

Dieses Problem verletzt GAD-000 "Operator Inversion":

| Test | Status | Problem |
|------|--------|---------|
| **Discoverability** | ❌ | Pfade sind nicht ueber Config entdeckbar - hardcoded im Code |
| **Observability** | ❌ | Drei Schatten-Dateisysteme - AI kann nicht alle State-Locations finden |
| **Parseability** | ⚠️ | Wenn `{root}` als Literal erscheint, ist Fehler schwer zu parsen |
| **Composability** | ❌ | Pfade koennen nicht via Config komponiert werden |
| **Idempotency** | ⚠️ | Daten an falschen Orten = unvorhersehbares Verhalten bei Retry |

**Ein AI Operator kann dieses System nicht zuverlaessig steuern wenn Daten an unbekannten Orten landen.**

---

## Wurzelursache

### Das Template-Variable Problem

`config/paths.yaml` benutzt Template-Variablen:

```yaml
data:
  root: "data"
  vibe_ledger: "{root}/vibe_ledger.db"
  economy_db: "{root}/economy.db"
```

Die `resolve()` Methode sollte `{root}` durch `"data"` ersetzen. **ABER:** Der Code ruft oft direkt auf statt `resolve()`:

```python
# FALSCH - kernel_impl.py:177
ledger_path = str(phoenix_config.paths.data.vibe_ledger)
# Gibt zurueck: "{root}/vibe_ledger.db" (LITERAL!)

# RICHTIG - kernel_impl.py:253
prakriti_db_path = phoenix_config.paths.data.resolve("vibe_ledger")
# Gibt zurueck: "data/vibe_ledger.db" (AUFGELOEST!)
```

Wenn Code dann `Path("{root}/vibe_ledger.db").parent.mkdir()` macht, wird ein Ordner namens `{root}` erstellt!

---

## Vier Kategorien von Bugs

### Kategorie 1: PhoenixConfig benutzt OHNE resolve()

Diese erstellen buchstaeblich Ordner/Dateien mit `{root}` im Namen:

| Datei | Zeile | Code | Auswirkung |
|-------|-------|------|------------|
| `kernel_impl.py` | 177 | `paths.data.vibe_ledger` | Erstellt `{root}/vibe_ledger.db` |
| `license_tool.py` | 159 | `paths.data.registry` | Erstellt `{root}/registry/...` |
| `memory.py` | 83 | `paths.data.events` | Erstellt `{root}/events/...` |

### Kategorie 2: Hardcoded `data/` Pfade (40+ Stellen)

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `ledger.py` | 132 | `"data/vibe_ledger.db"` |
| `boot_orchestrator.py` | 77 | `"data/vibe_ledger.db"` |
| `kernel_impl.py` | 179 | `"data/vibe_ledger.db"` (Fallback) |
| `vault_tool.py` | 91 | `Path("data/security/master.key")` |
| `vault.py` | 113 | `Path("data/security/master.key")` |
| `economy.py` | 52, 65 | `Path("data/economy.db")` |
| `bank_tool.py` | 51 | `Path("data/economy.db")` |
| `ledger_tool.py` | 64 | `Path("data/economy.db")` |
| `lifecycle_manager.py` | 108 | `"data/registry/citizens.json"` |
| `registry_agent.py` | 38 | `Path("data/registry/citizens.json")` |
| `economy_agent.py` | 245 | `"data/registry/licenses.json"` |
| `watchdog_tool.py` | 37, 40 | `Path("data/ledger/*.jsonl")` |
| `scout_tool_legacy.py` | 26 | `Path("data/federation/pokedex.json")` |
| `agency_director.py` | 107 | `Path("data/reports")` |
| `ledger_visualizer.py` | 32 | `Path("data/ledger/audit_trail.jsonl")` |
| `local_llama_provider.py` | 21 | `Path("data/models")` |
| `semantic_engine.py` | 76-80 | `"data/models"` |
| `prakriti.py` | 79 | `"data/vibe_ledger.db"` |
| `analyst/architecture_tool.py` | 192, 304 | `"data/vibe_ledger.db"` |
| `doctor/plugin_main.py` | 42, 48 | `"data/vibe_ledger.db"` |

### Kategorie 3: Hardcoded `/tmp/vibe_os` Pfade (15+ Stellen)

Obwohl `SystemPathsConfig.runtime_root` existiert, wird es ignoriert:

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `vfs.py` | 39 | `Path("/tmp/vibe_os/agents")` |
| `kernel_impl.py` | 221 | `"/tmp/vibe_os/kernel/lineage.db"` (Fallback) |
| `kernel_impl.py` | 488 | `Path("/tmp/vibe_os/kernel/economy.db")` |
| `lineage.py` | 64 | `"/tmp/vibe_os/kernel/lineage.db"` (Default) |
| `legacy.py` | 55 | `Path("/tmp/vibe_os/kernel/lineage.db")` |
| `legacy.py` | 57 | `Path("/tmp/vibe_os/kernel/kernel.pid")` |
| `legacy.py` | 507 | `Path("/tmp/vibe_os/logs")` |
| `legacy.py` | 511 | `Path("/tmp/vibe_os/kernel/kernel.pid")` |
| `legacy.py` | 573 | `Path("/tmp/vibe_os/kernel/kernel.pid")` |
| `legacy.py` | 805 | `Path("/tmp/vibe_os/logs/kernel.log")` |
| `legacy.py` | 1093 | `Path("/tmp/vibe_os/tasks")` |
| `local_llama_provider.py` | 28 | `Path("/tmp/vibe_os/models")` |
| `protocols/agent.py` | 363 | `Path("/tmp/vibe_os/agents/{agent_id}")` |
| `kernel_spawn.py` | 54 | `Path("/tmp/vibe_os/agents")` |
| `agent_interface.py` | 317 | `/tmp/vibe_os/agents/{agent_id}` |

### Kategorie 4: `.vibe` Schatten-Dateisystem (NICHT in PathsConfig)

Diese Pfade existieren NICHT in `config/paths.yaml`:

| Datei | Zeile | Schatten-Pfad | Zweck |
|-------|-------|---------------|-------|
| `boot_sequence.py` | 33 | `.vibe/vibe.db` | Boot State DB |
| `boot_sequence.py` | 506 | `.vibe/state/active_mission.json` | Legacy Migration |
| `project_memory.py` | 28 | `.vibe/project_memory.json` | Semantic Memory |
| `task_manager.py` | 44 | `.vibe/state` | Task State |
| `task_manager.py` | 45 | `.vibe/config` | Task Config |
| `task_manager.py` | 46 | `.vibe/history/mission_logs` | History |

**Problem:** Das sind Produktions-Daten die komplett an PhoenixConfig vorbeigehen!

---

## Kategorie 5: False Safety Defaults (Senior Audit Finding)

Die `from_dict` Methoden in `section_main.py` haben inkonsistente Defaults:

```python
# section_main.py:134
economy_db=data.get("economy_db", "data/economy.db"),  # AUFGELOEST
vibe_ledger=data.get("vibe_ledger", "data/vibe_ledger.db"),  # AUFGELOEST
```

**ABER** `config/paths.yaml` benutzt:
```yaml
economy_db: "{root}/economy.db"  # TEMPLATE
vibe_ledger: "{root}/vibe_ledger.db"  # TEMPLATE
```

**Das Problem:**
- Wenn YAML da: Bekommt `"{root}/economy.db"` → braucht resolve()
- Wenn YAML fehlt: Bekommt `"data/economy.db"` → kein resolve() noetig

**Das verdeckt Bugs!** Das System scheint zu funktionieren, aber benutzt unterschiedliche Pfad-Strategien je nach Config-Zustand.

---

## Die RICHTIGE Loesung

### Prinzip 1: Dependency Injection + resolve()

```python
# VORHER (VERBOTEN):
class SomeTool:
    DB_PATH = Path("data/economy.db")  # HARDCODED - VERBOTEN!

# NACHHER (RICHTIG):
class SomeTool:
    def __init__(self, config: PhoenixConfig = None):
        self._config = config or get_config()

    @property
    def db_path(self) -> Path:
        return self._config.paths.data.resolve("economy_db")
```

### Prinzip 2: Keine Fallbacks

```python
# VORHER (VERBOTEN):
try:
    ledger_path = str(phoenix_config.paths.data.vibe_ledger)
except:
    ledger_path = "data/vibe_ledger.db"  # FALLBACK - VERBOTEN!

# NACHHER (RICHTIG):
ledger_path = str(phoenix_config.paths.data.resolve("vibe_ledger"))
# Kein Fallback. Wenn Config kaputt ist, soll es LAUT SCHEITERN.
```

### Prinzip 3: Single Source of Truth

```python
# section_main.py - Defaults MUESSEN Template-Form haben:
economy_db=data.get("economy_db", "{root}/economy.db"),  # Konsistent mit YAML!

# ODER: Keine Defaults - wenn YAML fehlt, Exception werfen
```

### Prinzip 4: Alle Schatten-Pfade in PathsConfig

`config/paths.yaml` muss erweitert werden:

```yaml
# NEU: Project-lokale State-Pfade
project:
  vibe_root: ".vibe"
  state_db: "{vibe_root}/vibe.db"
  memory_file: "{vibe_root}/project_memory.json"
  tasks_dir: "{vibe_root}/state"
  config_dir: "{vibe_root}/config"
  history_dir: "{vibe_root}/history/mission_logs"
```

---

## Migrations-Plan

### Phase 1: Kategorie 1 Bugs (KRITISCH - erstellt {root} Ordner)

| Datei | Zeile | Aenderung |
|-------|-------|-----------|
| `kernel_impl.py` | 177 | `.vibe_ledger` → `.resolve("vibe_ledger")` |
| `license_tool.py` | 159 | `.registry` → `.resolve("registry_citizens")` |
| `memory.py` | 83 | `.events` → `.resolve("events_herald")` |

### Phase 2: Core System (P0)

| Datei | Aenderung |
|-------|-----------|
| `ledger.py:132` | Config Injection statt Default |
| `boot_orchestrator.py:77` | Config Injection, Fallback entfernen |
| `kernel_impl.py:179` | Fallback entfernen |
| `kernel_impl.py:221` | Fallback entfernen |

### Phase 3: Schatten-Dateisysteme in Config (P0)

| Aenderung |
|-----------|
| `.vibe/*` Pfade zu `config/paths.yaml` hinzufuegen |
| `/tmp/vibe_os/*` durch `config.paths.system.resolve()` ersetzen |
| `boot_sequence.py` auf Config umstellen |
| `task_manager.py` auf Config umstellen |

### Phase 4: False Safety Defaults (P1)

| Datei | Aenderung |
|-------|-----------|
| `section_main.py` | Alle Defaults zu Template-Form aendern ODER entfernen |

### Phase 5: Governance/State Tools (P1)

| Datei |
|-------|
| `vault_tool.py`, `vault.py` |
| `economy.py`, `bank_tool.py`, `ledger_tool.py` |
| `registry_agent.py`, `lifecycle_manager.py` |

### Phase 6: Runtime/Legacy (P2)

| Datei |
|-------|
| `legacy.py` (alle 8+ Stellen) |
| `vfs.py` |
| `lineage.py` |
| `kernel_spawn.py` |
| `agent_interface.py` |

### Phase 7: Features/Plugins (P3)

| Datei |
|-------|
| `watchdog_tool.py` |
| `agency_director.py` |
| `ledger_visualizer.py` |
| `semantic_engine.py` |
| `local_llama_provider.py` |

### Phase 8: Vollstaendige Analyse

- [ ] Tests auf hardcoded Pfade pruefen
- [ ] Scripts auf hardcoded Pfade pruefen
- [ ] Runtime-generierte Pfade tracen
- [ ] Config-Loading Race Conditions analysieren

---

## Enforcement

### Pre-commit Hook

```bash
# .githooks/pre-commit muss erweitert werden:
# 1. Blockiert: Path("data/...)
# 2. Blockiert: paths.data.XYZ (ohne resolve)
# 3. Blockiert: /tmp/vibe_os
# 4. Blockiert: .vibe/ (ohne Config)
```

### CI Gate

```bash
grep -rE 'Path\("data/' vibe_core/ && exit 1
grep -rE 'paths\.(data|system|knowledge)\.[a-z_]+[^(]' vibe_core/ && exit 1
grep -rE '"/tmp/vibe_os' vibe_core/ && exit 1
```

### Watchman AST-Visitor aktivieren

Der existiert bereits in `watchman/tools/standards_inspection.py:71` aber wird nicht enforced.

---

## Was noch NICHT analysiert wurde

1. **Tests** - Hardcoded Pfade in test fixtures?
2. **Scripts** - Build/CI Scripts mit falschen Pfaden?
3. **String-Concatenation** - `f"data/{something}"` nicht mit grep findbar
4. **Config-Loading Order** - Race Conditions beim Boot?
5. **Binary Distribution** - PyInstaller aendert Pfade
6. **Docker/Container** - Volume Mounts vs. Config?

**Diese Analyse ist NICHT vollstaendig. Der Plan muss erweitert werden sobald weitere Violations gefunden werden.**

---

## Architektur-Entscheidung

**ADR-025: Mandatory resolve() and Config Injection for All Paths**

**Status:** Proposed

**Context:**
- PhoenixConfig.paths benutzt Template-Variablen wie `{root}`, `{runtime_root}`
- Code benutzt Pfade inkonsistent - manchmal mit, manchmal ohne resolve()
- Drei Schatten-Dateisysteme (`data/`, `/tmp/vibe_os/`, `.vibe/`) existieren parallel
- Python Defaults in `from_dict()` sind inkonsistent mit YAML Templates

**Decision:**
1. ALLE Pfad-Zugriffe MUESSEN `resolve()` benutzen
2. Direkte Attribut-Zugriffe wie `.vibe_ledger` sind VERBOTEN
3. Hardcoded Pfade sind VERBOTEN
4. Fallbacks zu hardcoded Pfaden sind VERBOTEN
5. Config-Fehler muessen LAUT scheitern
6. ALLE Schatten-Pfade muessen in `config/paths.yaml` definiert werden
7. Python Defaults muessen Template-Form haben oder entfernt werden

**Consequences:**
- 60+ Stellen muessen migriert werden
- Dependency Injection muss durchgaengig implementiert werden
- CI muss neue Violations blockieren
- Volle Flexibilitaet fuer verschiedene Deployment-Szenarien
- Single Source of Truth fuer alle Pfade

---

*Erstellt: 2025-12-12 | Letzte Aktualisierung: 2025-12-12*
*Senior Audit Contributions: Gemini (2025-12-12)*
