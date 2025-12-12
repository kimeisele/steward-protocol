# OPUS-025: PATH LOBOTOMY CRISIS

> **Status:** CRITICAL - System Integrity Compromised
> **Created:** 2025-12-12
> **Last Updated:** 2025-12-12
> **Severity:** P0 - Architectural Foundation Broken

---

## Executive Summary

Das System ist **LOBOTOMIERT**. Die Config-Architektur (PhoenixConfig.paths) existiert und ist vollstaendig, aber:

1. **Code benutzt Pfade OHNE `resolve()`** → erstellt buchstaeblich Ordner namens `{root}`
2. **Code ignoriert PhoenixConfig komplett** → hardcoded `Path("data/...")` ueberall
3. **Inkonsistente Nutzung** → manchmal richtig, manchmal falsch

**Symptom:** Ein Ordner namens `{root}` existiert im Projekt-Root mit `vibe_ledger.db` darin.

---

## Wurzelursache

### Das Template-Variable Problem

`config/paths.yaml` benutzt Template-Variablen:

```yaml
data:
  root: "data"
  vibe_ledger: "{root}/vibe_ledger.db"
  economy_db: "{root}/economy.db"
  registry_citizens: "{root}/registry/citizens.json"
  # ... alle mit {root}
```

Die `resolve()` Methode sollte `{root}` durch `"data"` ersetzen:

```python
# DataPathsConfig.resolve()
def resolve(self, path_key: str) -> Path:
    value = getattr(self, path_key, None)
    resolved = value.replace("{root}", self.root)  # "{root}" → "data"
    return Path(resolved)
```

**ABER:** Der Code ruft oft `.vibe_ledger` direkt auf statt `.resolve("vibe_ledger")`:

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

## Drei Kategorien von Bugs

### Kategorie 1: PhoenixConfig benutzt OHNE resolve()

Diese erstellen buchstaeblich Ordner/Dateien mit `{root}` im Namen:

| Datei | Zeile | Code | Auswirkung |
|-------|-------|------|------------|
| `kernel_impl.py` | 177 | `paths.data.vibe_ledger` | Erstellt `{root}/vibe_ledger.db` |
| `license_tool.py` | 159 | `paths.data.registry` | Erstellt `{root}/registry/...` |
| `memory.py` | 83 | `paths.data.events` | Erstellt `{root}/events/...` |

**Fix:** ALLE muessen `resolve()` benutzen.

### Kategorie 2: PhoenixConfig komplett IGNORIERT

Diese benutzen hardcoded Pfade und ignorieren die Config:

| Datei | Zeile | Hardcoded Path |
|-------|-------|----------------|
| `ledger.py` | 132 | `"data/vibe_ledger.db"` |
| `boot_orchestrator.py` | 77 | `"data/vibe_ledger.db"` |
| `kernel_impl.py` | 179 | `"data/vibe_ledger.db"` (Fallback) |
| `config/schema.py` | 219 | `"data/registry/"` |
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
| `doctor/plugin_main.py` | 42, 48 | `"data/vibe_ledger.db"` |
| `interface/renderers/git.py` | 44 | `"data/registry/citizens.json"` |
| `prakriti.py` | 79 | `"data" / "vibe_ledger.db"` |
| `analyst/architecture_tool.py` | 192, 304 | `"data" / "vibe_ledger.db"` |

**40+ Stellen** die PhoenixConfig ignorieren.

**Fix:** ALLE muessen Config-Injection bekommen und `paths.data.resolve()` benutzen.

### Kategorie 3: UNBEKANNT - Was noch fehlt

Ich habe noch NICHT vollstaendig analysiert:

- [ ] knowledge-Pfade (`{root}` in KnowledgePathsConfig)
- [ ] system-Pfade (`{runtime_root}` in SystemPathsConfig)
- [ ] Pfade in Tests
- [ ] Pfade in Scripts
- [ ] Pfade die zur Laufzeit dynamisch erstellt werden
- [ ] Zirkulaere Abhaengigkeiten beim Config-Loading

**Diese Liste ist NICHT vollstaendig.**

---

## Die RICHTIGE Loesung

### Prinzip: Dependency Injection + resolve()

```python
# VORHER (VERBOTEN):
class SomeTool:
    DB_PATH = Path("data/economy.db")  # HARDCODED - VERBOTEN!

    def __init__(self):
        self.db_path = self.DB_PATH

# NACHHER (RICHTIG):
class SomeTool:
    def __init__(self, config: PhoenixConfig = None):
        self._config = config or get_config()

    @property
    def db_path(self) -> Path:
        return self._config.paths.data.resolve("economy_db")
```

### Keine Fallbacks zu hardcoded Pfaden

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

### Config muss beim Boot validiert werden

```python
# Beim System-Start:
config = PhoenixConfig.from_files()
errors = config.paths.validate()
if errors:
    raise ConfigurationError(f"Invalid paths configuration: {errors}")
```

---

## Migrations-Plan

### Phase 1: Kategorie 1 Bugs (KRITISCH - erstellt {root} Ordner)

| Datei | Zeile | Aenderung |
|-------|-------|-----------|
| `kernel_impl.py` | 177 | `.vibe_ledger` → `.resolve("vibe_ledger")` |
| `license_tool.py` | 159 | `.registry` → `.resolve("registry_citizens")` + Pfad-Anpassung |
| `memory.py` | 83 | `.events` → `.resolve("events_herald")` |

### Phase 2: Core System (P0)

| Datei | Prioritaet |
|-------|------------|
| `ledger.py` | P0 |
| `boot_orchestrator.py` | P0 |
| `kernel_impl.py:179` (Fallback entfernen) | P0 |

### Phase 3: Governance/State (P1)

| Datei | Prioritaet |
|-------|------------|
| `vault_tool.py`, `vault.py` | P1 |
| `economy.py`, `bank_tool.py`, `ledger_tool.py` | P1 |
| `registry_agent.py`, `lifecycle_manager.py` | P1 |

### Phase 4: Features (P2)

| Datei | Prioritaet |
|-------|------------|
| `watchdog_tool.py` | P2 |
| `agency_director.py` | P2 |
| `ledger_visualizer.py` | P2 |
| `scout_tool_legacy.py` | P2 |

### Phase 5: AI/ML (P3)

| Datei | Prioritaet |
|-------|------------|
| `semantic_engine.py` | P3 |
| `local_llama_provider.py` | P3 |

### Phase 6: Plugins/Tools (P4)

| Datei | Prioritaet |
|-------|------------|
| `doctor/plugin_main.py` | P4 |
| `interface/renderers/git.py` | P4 |
| Alle anderen | P4 |

### Phase 7: Vollstaendige Analyse

- [ ] knowledge-Pfade analysieren
- [ ] system-Pfade analysieren
- [ ] Tests analysieren
- [ ] Scripts analysieren
- [ ] Runtime-erstellte Pfade tracen

---

## Enforcement

### Pre-commit Hook erweitern

```python
# .pre-commit-config.yaml - Regel hinzufuegen:
# Blockiert: paths.data.XYZ (ohne resolve)
# Blockiert: Path("data/...")
# Blockiert: "data/" in String-Literals
```

### CI Gate

```bash
# Prueft auf neue Violations
grep -r 'Path("data/' vibe_core/ && exit 1
grep -r 'paths\.data\.[a-z_]+[^(]' vibe_core/ && exit 1
```

### Watchman AST-Visitor aktivieren

Der existiert bereits aber wird nicht enforced:
```python
# watchman/tools/standards_inspection.py:71
class PathDataCallVisitor(ast.NodeVisitor):
    """AST visitor to detect Path("data/...") calls."""
```

---

## Was ich NICHT weiss

1. **Gibt es weitere Template-Variablen?** - Ich habe nur `{root}` und `{runtime_root}` gefunden
2. **Werden Pfade zur Laufzeit dynamisch erstellt?** - Moeglicherweise durch String-Concatenation
3. **Wie verhaelt sich das in Tests?** - Tests koennten andere Pfade benutzen
4. **Gibt es Config-Loading Race Conditions?** - Was passiert wenn Pfade benutzt werden bevor Config geladen ist?
5. **Wie verhaelt sich das bei Binary Distribution?** - PyInstaller aendert Pfade

---

## Architektur-Entscheidung

**ADR-025: Mandatory resolve() for Template Paths**

**Status:** Proposed

**Context:**
- PhoenixConfig.paths benutzt Template-Variablen wie `{root}`
- Code benutzt Pfade inkonsistent - manchmal mit, manchmal ohne resolve()
- Das fuehrt zu buchstaeblichen `{root}` Ordnern im Dateisystem

**Decision:**
1. ALLE Pfad-Zugriffe MUESSEN `resolve()` benutzen
2. Direkte Attribut-Zugriffe wie `.vibe_ledger` sind VERBOTEN
3. Hardcoded Pfade wie `Path("data/...")` sind VERBOTEN
4. Fallbacks zu hardcoded Pfaden sind VERBOTEN
5. Config-Fehler muessen LAUT scheitern, nicht still fallbacken

**Consequences:**
- Alle 40+ Stellen muessen migriert werden
- Dependency Injection muss implementiert werden
- CI muss neue Violations blockieren
- Volle Flexibilitaet fuer verschiedene Deployment-Szenarien

---

## @HARNESS

```yaml
files:
  - path: config/paths.yaml
    required: true
  - path: vibe_core/phoenix/sections/paths/section_main.py
    required: true
tests:
  - tests/unit/test_config_paths.py
wiring:
  - pattern: "paths.data.resolve"
    in: vibe_core/kernel_impl.py
absent:
  - pattern: 'paths\.data\.[a-z_]+[^(]'
    in: vibe_core/kernel_impl.py
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
| Template-Variablen funktionieren | ✅ | resolve() Methode existiert |
| Code benutzt resolve() konsistent | ❌ | 3 Stellen ohne resolve() gefunden |
| Hardcoded Pfade eliminiert | ❌ | 40+ Violations |
| {root} Ordner existiert | ❌ | Benutzer-Report |
| CI Gate | ❌ | Nicht implementiert |
| Migration abgeschlossen | ❌ | 0% |
| Vollstaendige Analyse | ❌ | Unbekannte Bereiche bleiben |

---

## WARNUNG

**Diese Analyse ist NICHT vollstaendig.**

Ich habe nur die offensichtlichsten Violations gefunden. Es gibt wahrscheinlich mehr:
- In Tests
- In Scripts
- In dynamisch generiertem Code
- In String-Concatenations die ich nicht mit grep gefunden habe
- In Bereichen die ich noch nicht analysiert habe

**Der Plan muss erweitert werden sobald weitere Violations gefunden werden.**

---

*Erstellt: 2025-12-12 | Letzte Aktualisierung: 2025-12-12*
