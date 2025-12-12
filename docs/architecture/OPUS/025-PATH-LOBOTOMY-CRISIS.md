# OPUS-025: PATH LOBOTOMY CRISIS

> **Status:** CRITICAL - System Integrity Compromised
> **Created:** 2025-12-12
> **Last Updated:** 2025-12-12
> **Severity:** P0 - Architectural Foundation Broken
> **Scope:** Audit all path handling against PhoenixConfig.paths
> **Violation Count:** 100+ (verified)

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
  - path: vibe_core/phoenix/sections/test_governance/section_main.py
    required: true
  - path: vibe_core/runtime_extensions.py
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
  - pattern: 'Path\.home\(\).*\.steward'
    in: vibe_core/runtime_extensions.py
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
| Hardcoded `/tmp/vibe_os` eliminiert | ❌ | **99 Occurrences in 28 Files** |
| `.vibe` Schatten-Pfade in Config | ❌ | **12+ Violations** |
| `~/.steward` User-Home Pfade | ❌ | **NEUES Schatten-Dateisystem** |
| Python Defaults = YAML Defaults | ❌ | Inkonsistente Defaults |
| XDG Compliance | ❌ | Inkonsistent (3 Stellen) |
| Path.cwd() Injection | ❌ | **36 Stellen ohne Injection** |
| CI Gate aktiv | ❌ | Nicht implementiert |
| Migration abgeschlossen | ❌ | 0% |

---

## Executive Summary

Das System ist **LOBOTOMIERT**. Die Config-Architektur (PhoenixConfig.paths) existiert, aber:

1. **Code benutzt Pfade OHNE `resolve()`** → erstellt buchstaeblich Ordner namens `{root}`
2. **Code ignoriert PhoenixConfig komplett** → hardcoded Pfade ueberall
3. **VIER Schatten-Dateisysteme** existieren parallel:
   - `data/` - Governance, Ledger, Registry
   - `/tmp/vibe_os/` - Runtime, Agents, Lineage (99 Occurrences!)
   - `.vibe/` - Boot State, Memory, Tasks (12+ Stellen)
   - `~/.steward/` - User Extensions, Keys, Models (**NEU ENTDECKT**)
4. **Python Defaults untergraben YAML** → False Safety
5. **Bootstrap Paradox** → SQLiteStore initialisiert VOR Config-Load
6. **XDG Inkonsistenz** → Manchmal XDG, manchmal nicht

---

## GAD-000 Compliance

Dieses Problem verletzt GAD-000 "Operator Inversion":

| Test | Status | Problem |
|------|--------|---------|
| **Discoverability** | ❌ | Pfade sind nicht ueber Config entdeckbar - hardcoded im Code |
| **Observability** | ❌ | VIER Schatten-Dateisysteme - AI kann nicht alle State-Locations finden |
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

### Das Bootstrap Paradox (Henne-Ei-Problem)

`boot_sequence.py:33` initialisiert den SQLiteStore **VOR** Config-Load:

```python
class BootSequence:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        # PROBLEM: SQLiteStore wird initialisiert BEVOR PhoenixConfig geladen wird!
        self.sqlite_store = SQLiteStore(self.project_root / ".vibe" / "vibe.db")
        # Config wird erst DANACH geladen...
```

**Loesung fuer Phase 2:** Store muss **Lazy-Loaded** werden oder Config muss als ERSTES geladen werden.

---

## 11 Kategorien von Bugs

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

### Kategorie 3: Hardcoded `/tmp/vibe_os` Pfade (99 Occurrences in 28 Files!)

Obwohl `SystemPathsConfig.runtime_root` existiert, wird es ignoriert:

**vibe_core/ (Hauptcode):**

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

**scripts/ (NICHT analysiert im Original-Plan):**

| Datei | Occurrences |
|-------|-------------|
| `stress_test_city.py` | 2 |
| `test_parampara.py` | 2 |
| `verify_database_isolation.py` | 5 |
| `verify_lineage_chain.py` | 1 |
| `smoke_test_kernel.py` | 2 |
| `issue_passports.py` | 1 |
| `boot_kernel.py` | 1 |

### Kategorie 4: `.vibe` Schatten-Dateisystem (12+ Stellen, NICHT alle in PathsConfig)

**Im Code gefunden:**

| Datei | Zeile | Schatten-Pfad | In Config? |
|-------|-------|---------------|------------|
| `boot_sequence.py` | 33 | `.vibe/vibe.db` | ❌ |
| `boot_sequence.py` | 506 | `.vibe/state/active_mission.json` | ❌ |
| `project_memory.py` | 28 | `.vibe/project_memory.json` | ❌ |
| `task_manager.py` | 44 | `.vibe/state` | ❌ |
| `task_manager.py` | 45 | `.vibe/config` | ❌ |
| `task_manager.py` | 46 | `.vibe/history/mission_logs` | ❌ |
| `sqlite_store.py` | 37,53,67 | `.vibe/state/vibe_agency.db` | ❌ |
| `base_agent.py` | 111,153,154 | `.vibe/runtime/context.json` | ❌ |
| `base_agent.py` | 153 | `.vibe/config/roadmap.yaml` | ❌ |
| `heartbeat.py` | 16 | `.vibe/state/.lock` | ❌ |
| `section_main.py` | 40,59 | `.vibe/state/archive` | ✅ |
| `section_main.py` | 41,60 | `.vibe/migrations` | ✅ |

### Kategorie 5: False Safety Defaults (Python vs YAML)

Die `from_dict` Methoden haben inkonsistente Defaults:

**section_main.py (paths):**
```python
economy_db=data.get("economy_db", "data/economy.db"),  # AUFGELOEST
vibe_ledger=data.get("vibe_ledger", "data/vibe_ledger.db"),  # AUFGELOEST
```

**YAML:**
```yaml
economy_db: "{root}/economy.db"  # TEMPLATE
vibe_ledger: "{root}/vibe_ledger.db"  # TEMPLATE
```

**Das verdeckt Bugs!** Das System scheint zu funktionieren, aber benutzt unterschiedliche Pfad-Strategien je nach Config-Zustand.

### Kategorie 6: `~/.steward` und `~/.vibe` User-Home Pfade (NEU!)

**VIERTES Schatten-Dateisystem entdeckt!**

| Datei | Zeile | User-Home Pfad |
|-------|-------|----------------|
| `runtime_extensions.py` | 25 | `Path.home() / ".steward"` |
| `build_release.py` | 115 | `~/.vibe/data` |
| `build_release.py` | 225-226 | `~/.vibe/library`, `~/.vibe/` |
| `local_llama_provider.py` | 27 | `Path.home() / ".cache" / "steward" / "models"` |

**NICHT in `config/paths.yaml`!** Diese Pfade sind komplett unmanaged.

**Empfehlung:** `config/paths.yaml` muss erweitert werden:

```yaml
user:
  steward_home: "~/.steward"
  steward_lib: "{steward_home}/lib"
  vibe_library: "~/.vibe/library"
  vibe_config: "~/.vibe/config"
  cache_models: "~/.cache/steward/models"
```

### Kategorie 7: Phoenix Test Governance Section (NEU!)

Eine ganze Phoenix-Section benutzt hardcoded Pfade:

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `test_governance/section_main.py` | 58 | `baseline_path: str = "data/test_baselines.json"` |
| `test_governance/section_main.py` | 104 | `mutation_log_path: str = "data/logs/test_mutations.log"` |
| `test_governance/section_main.py` | 120 | Default in `from_dict()`: `"data/test_baselines.json"` |
| `test_governance/section_main.py` | 132 | Default in `from_dict()`: `"data/logs/test_mutations.log"` |

**IRONIE:** Diese Pfade sind INNERHALB des Phoenix Config Systems aber benutzen dennoch hardcoded Defaults statt Template-Variablen!

### Kategorie 8: f-String Path Concatenation (NEU!)

Schwer zu greppen, aber gefunden:

| Datei | Zeile | f-String Path |
|-------|-------|---------------|
| `gap_report_tool.py` | 464 | `f"data/reports/GAP_Report_{timestamp}.{output_format}"` |

**CI Gate muss erweitert werden um f-Strings zu finden!**

### Kategorie 9: Doctor Plugin Hardcoded Checks (NEU!)

| Datei | Zeile | Problem |
|-------|-------|---------|
| `doctor/plugin_main.py` | 42 | `required_paths = ["data/vibe_ledger.db", ...]` |
| `doctor/plugin_main.py` | 48 | Spezial-Handling fuer diesen Pfad |

Das Doctor Plugin prueft Pfade OHNE Config → kann nicht angepasst werden!

### Kategorie 10: Interface Renderer Git Patterns (NEU!)

| Datei | Zeile | Problem |
|-------|-------|---------|
| `renderers/git.py` | 44 | `"data/registry/citizens.json"` |

Das ist ein Git-Ignore Pattern - muss dynamisch aus Config kommen!

### Kategorie 11: XDG Inkonsistenz (ARCHITEKTUR-ENTSCHEIDUNG NOETIG!)

Der Code benutzt XDG **MANCHMAL**:

```python
# container_loader.py:53
xdg_cache = os.environ.get("XDG_CACHE_HOME")

# memory.py:88, license_tool.py:164
data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))
```

**ABER:** `config/paths.yaml` kennt XDG NICHT.

**Entscheidung noetig:**
- Falls JA zu XDG-Compliance: `paths.yaml` braucht `xdg_cache_home`, `xdg_data_home` mit Fallbacks
- Falls NEIN: Die XDG-Checks im Code muessen entfernt werden

---

## Architektur-Blinde Flecken

### 1. Path.cwd() Explosion (36 Stellen!)

Gefunden: **36 Stellen** mit `Path.cwd()` im `vibe_core/` Verzeichnis.

**Problem:** Manche Komponenten bekommen `project_root` injiziert, andere fallen auf `Path.cwd()` zurueck.

**Empfehlung:** `Path.cwd()` sollte NUR in Entry-Points erlaubt sein:

| Datei | Erlaubt? |
|-------|----------|
| `boot_sequence.py` | ✅ Entry-Point |
| `io_service.py` | ✅ Entry-Point |
| `plugins/**/plugin_main.py` | ✅ Plugin Entry |
| Alle anderen | ❌ Muessen `project_root` injiziert bekommen |

### 2. Makefile/Scripts nicht analysiert

Der Plan erwähnt "Scripts" als nicht analysiert. Die Makefile ist ebenfalls ein Risiko:

```bash
grep -rE 'data/' Makefile
grep -rE '/tmp/vibe_os' Makefile
```

### 3. Tests mit hardcoded Pfaden

Bereits gefunden:
- `tests/integration/test_persistence_prakriti.py:29` → `Path("data/test_persistence.db")`

**Tests muessen in Phase 1-2 geprueft werden** weil sie:
- Die falschen Annahmen validieren
- Nach Migration fehlschlagen koennten
- Self-fulfilling prophecies sind

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
  agency_db: "{vibe_root}/state/vibe_agency.db"
  context_json: "{vibe_root}/runtime/context.json"
  roadmap_yaml: "{vibe_root}/config/roadmap.yaml"
  lock_file: "{vibe_root}/state/.lock"

# NEU: User-Home Pfade
user:
  steward_home: "~/.steward"
  steward_lib: "{steward_home}/lib"
  vibe_library: "~/.vibe/library"
  cache_models: "~/.cache/steward/models"
```

### Prinzip 5: Bootstrap Order korrigieren

```python
class BootSequence:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()

        # 1. ERST Config laden
        self._config = PhoenixConfig.load(self.project_root)

        # 2. DANN Store mit Config-Pfad initialisieren
        state_db_path = self._config.paths.project.resolve("state_db")
        self.sqlite_store = SQLiteStore(self.project_root / state_db_path)
```

---

## Migrations-Plan (REVIDIERT)

### Phase 0: Pre-Audit Cleanup (NEU!)

| Aktion |
|--------|
| Alle 11 Kategorien in Plan dokumentiert ✅ |
| Violation Count aktualisiert (100+) ✅ |
| XDG-Architektur-Entscheidung treffen |
| `~/.steward` Entscheidung treffen (behalten oder entfernen?) |
| Tests auf hardcoded Pfade pruefen |

### Phase 1: Kategorie 1 Bugs (KRITISCH - erstellt {root} Ordner)

| Datei | Zeile | Aenderung |
|-------|-------|-----------|
| `kernel_impl.py` | 177 | `.vibe_ledger` → `.resolve("vibe_ledger")` |
| `license_tool.py` | 159 | `.registry` → `.resolve("registry_citizens")` |
| `memory.py` | 83 | `.events` → `.resolve("events_herald")` |

### Phase 2: Schatten-Dateisysteme definieren (VORGEZOGEN!)

| Aenderung |
|-----------|
| `.vibe/*` Pfade zu `config/paths.yaml` hinzufuegen |
| `~/.steward/*` Pfade zu `config/paths.yaml` hinzufuegen |
| Bootstrap-Order in `boot_sequence.py` korrigieren |

### Phase 3: Core System (P0)

| Datei | Aenderung |
|-------|-----------|
| `ledger.py:132` | Config Injection statt Default |
| `boot_orchestrator.py:77` | Config Injection, Fallback entfernen |
| `kernel_impl.py:179` | Fallback entfernen |
| `kernel_impl.py:221` | Fallback entfernen |

### Phase 4: False Safety Defaults (P1)

| Datei | Aenderung |
|-------|-----------|
| `section_main.py` (paths) | Alle Defaults zu Template-Form aendern ODER entfernen |
| `section_main.py` (test_governance) | Alle Defaults zu Template-Form aendern |

### Phase 5: /tmp/vibe_os Migration (P1)

| Datei |
|-------|
| `vfs.py` |
| `legacy.py` (alle 8+ Stellen) |
| `lineage.py` |
| `kernel_spawn.py` |
| `agent_interface.py` |
| `protocols/agent.py` |
| `local_llama_provider.py` |

### Phase 6: Governance/State Tools (P1)

| Datei |
|-------|
| `vault_tool.py`, `vault.py` |
| `economy.py`, `bank_tool.py`, `ledger_tool.py` |
| `registry_agent.py`, `lifecycle_manager.py` |

### Phase 7: Features/Plugins (P2)

| Datei |
|-------|
| `watchdog_tool.py` |
| `agency_director.py` |
| `ledger_visualizer.py` |
| `semantic_engine.py` |
| `doctor/plugin_main.py` |
| `renderers/git.py` |
| `gap_report_tool.py` |

### Phase 8: Scripts Migration (P2)

| Datei |
|-------|
| `scripts/stress_test_city.py` |
| `scripts/test_parampara.py` |
| `scripts/verify_database_isolation.py` |
| `scripts/verify_lineage_chain.py` |
| `scripts/smoke_test_kernel.py` |
| `scripts/issue_passports.py` |
| `scripts/boot_kernel.py` |
| `Makefile` |

### Phase 9: Path.cwd() Cleanup (P2)

| Aktion |
|--------|
| Audit alle 36 Stellen |
| Nur Entry-Points behalten |
| Alle anderen: `project_root` Injection |

### Phase 10: Test Suite Migration (P3)

| Aktion |
|--------|
| Alle Tests auf hardcoded Pfade pruefen |
| Test-Fixtures auf Config umstellen |
| Integration Tests anpassen |

---

## Enforcement

### Pre-commit Hook (ERWEITERT)

```bash
# .githooks/pre-commit muss erweitert werden:

# Original Checks
grep -rE 'Path\("data/' vibe_core/ && exit 1
grep -rE 'paths\.(data|system|knowledge)\.[a-z_]+[^(]' vibe_core/ && exit 1
grep -rE '"/tmp/vibe_os' vibe_core/ && exit 1

# NEU: Erweiterte Checks
grep -rE '"data/' vibe_core/ && exit 1                    # String literals
grep -rE "f['\"]data/" vibe_core/ && exit 1               # f-strings
grep -rE '\.vibe/' vibe_core/ && exit 1                   # .vibe in Code (ohne Config)
grep -rE '~/.vibe' . && exit 1                            # User home .vibe
grep -rE '~/.steward' . && exit 1                         # User home steward
grep -rE 'Path\.home\(\)' vibe_core/ | grep -v container_loader && exit 1  # Unmanaged home
```

### CI Gate (ERWEITERT)

```bash
# VOLLSTAENDIGER CI GATE:

# Hardcoded data/ paths
grep -rE 'Path\("data/' vibe_core/ && exit 1
grep -rE '"data/' vibe_core/ && exit 1
grep -rE "f['\"]data/" vibe_core/ && exit 1

# resolve() bypass
grep -rE 'paths\.(data|system|knowledge)\.[a-z_]+[^(]' vibe_core/ && exit 1

# Runtime paths
grep -rE '"/tmp/vibe_os' vibe_core/ && exit 1

# Shadow filesystems
grep -rE '\.vibe/' vibe_core/ | grep -v paths.yaml | grep -v section_main && exit 1
grep -rE '~/.vibe' . && exit 1
grep -rE '~/.steward' . | grep -v docs/ && exit 1

# Unmanaged Path.home()
grep -rE 'Path\.home\(\)' vibe_core/ | grep -v container_loader && exit 1
```

### Watchman AST-Visitor aktivieren

Der existiert bereits in `watchman/tools/standards_inspection.py:71` aber wird nicht enforced.

---

## Risiko-Matrix

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| `{root}` Ordner wird erstellt | HOCH | KRITISCH | Phase 1 SOFORT |
| Daten an falschen Orten | HOCH | HOCH | Full Migration |
| Bootstrap Paradox | HOCH | HOCH | Phase 2 (vorgezogen) |
| Tests validieren falsche Pfade | MITTEL | HOCH | Tests frueh pruefen |
| XDG-Inkonsistenz | MITTEL | MITTEL | Architektur-Entscheidung |
| `~/.steward` vergessen | NIEDRIG | MITTEL | In Plan aufgenommen |
| Scripts nicht migriert | MITTEL | MITTEL | Phase 8 |
| Path.cwd() nicht injiziert | MITTEL | MITTEL | Phase 9 |

---

## Offene Architektur-Entscheidungen

### ADR-025a: XDG Compliance

**Status:** OFFEN - Entscheidung noetig

**Optionen:**
1. **XDG-compliant**: `paths.yaml` bekommt `xdg_cache_home`, `xdg_data_home` mit Fallbacks
2. **Eigenes Schema**: XDG-Checks im Code entfernen, nur `~/.steward` und `~/.vibe` nutzen
3. **Hybrid**: XDG fuer Cache, eigenes Schema fuer Config/Data

### ADR-025b: ~/.steward vs ~/.vibe

**Status:** OFFEN - Entscheidung noetig

**Frage:** Warum existieren BEIDE? Konsolidieren zu einem?

---

## Architektur-Entscheidung

**ADR-025: Mandatory resolve() and Config Injection for All Paths**

**Status:** Proposed

**Context:**
- PhoenixConfig.paths benutzt Template-Variablen wie `{root}`, `{runtime_root}`
- Code benutzt Pfade inkonsistent - manchmal mit, manchmal ohne resolve()
- VIER Schatten-Dateisysteme (`data/`, `/tmp/vibe_os/`, `.vibe/`, `~/.steward/`) existieren parallel
- Python Defaults in `from_dict()` sind inkonsistent mit YAML Templates
- Bootstrap initialisiert Store VOR Config-Load

**Decision:**
1. ALLE Pfad-Zugriffe MUESSEN `resolve()` benutzen
2. Direkte Attribut-Zugriffe wie `.vibe_ledger` sind VERBOTEN
3. Hardcoded Pfade sind VERBOTEN
4. Fallbacks zu hardcoded Pfaden sind VERBOTEN
5. Config-Fehler muessen LAUT scheitern
6. ALLE Schatten-Pfade muessen in `config/paths.yaml` definiert werden
7. Python Defaults muessen Template-Form haben oder entfernt werden
8. Bootstrap-Order: Config ERST, dann State-Stores
9. Path.cwd() nur in Entry-Points erlaubt

**Consequences:**
- 100+ Stellen muessen migriert werden
- Dependency Injection muss durchgaengig implementiert werden
- CI muss neue Violations blockieren
- Volle Flexibilitaet fuer verschiedene Deployment-Szenarien
- Single Source of Truth fuer alle Pfade

---

*Erstellt: 2025-12-12 | Letzte Aktualisierung: 2025-12-12*
*Senior Audit Contributions: Gemini (2025-12-12), Opus (2025-12-12)*
*Verification: All 11 categories verified against codebase*
