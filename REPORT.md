# STEWARD PROTOCOL: VOLLSTÄNDIGER CODE AUDIT REPORT

**Datum:** 2025-12-29
**Auditor:** Claude Opus 4.5
**Scope:** Gesamte vibe_core/ Codebase + tests/hardening/
**Methodik:** Statische Analyse mit manueller Code-Review

---

## EXECUTIVE SUMMARY

| Kategorie | P0 (Kritisch) | P1 (Hoch) | P2 (Mittel) | P3 (Niedrig) |
|-----------|---------------|-----------|-------------|--------------|
| VISNU Protected (KANN NICHT FIXEN) | 4 | 5 | 6 | 3 |
| Nicht Protected (KANN FIXEN) | 2 | 4 | 12 | 8 |
| **GESAMT** | **6** | **9** | **18** | **11** |

**Kritischste Findings:**
1. VFS Sandbox Escape via `create_symlink()` (P0, FIXABLE)
2. Silent Failures in Ledger PRAGMA (P0, VISNU PROTECTED)
3. Blueprint Resurrection verliert Daten (P0, VISNU PROTECTED)
4. 81 direkte `open()` in Cartridges statt VFS (P2, FIXABLE)

---

## TEIL A: VISNU PROTECTED (KANN NICHT GEFIXT WERDEN)

Diese 22 Dateien sind durch VISNU Kernel Protection geschützt:

```
Core Orchestration:
  - vibe_core/kernel_impl.py
  - vibe_core/kernel_ops.py
  - vibe_core/ledger.py

Plugin System:
  - vibe_core/plugin_protocol.py
  - vibe_core/plugin_loader.py

Security:
  - vibe_core/narasimha.py
  - vibe_core/capability_registry.py
  - vibe_core/bridge.py

Governance:
  - scripts/governance/restore_kernel.sh
  - scripts/governance/verify_kernel.py
  - scripts/governance/kernel_hashes.json

Infrastructure:
  - .github/workflows/* (10 files)
  - .pre-commit-config.yaml
  - .gitignore
```

### A-P0: KRITISCH (VISNU Protected)

#### A-P0-1: Silent PRAGMA Failure in Ledger
**Datei:** `vibe_core/ledger.py:211-214`

```python
try:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
except sqlite3.Error:
    pass  # <-- SILENT! Andere Durability-Garantien!
```

**Problem:** Wenn WAL-Modus fehlschlägt, läuft die DB mit Default-Settings - aber der Code weiß das nicht. Dies kann zu Datenverlust führen.

**Verletzung:** DHARMA - "Keine Silent Failures"

---

#### A-P0-2: Ledger Event Recording ohne Caller Verification
**Datei:** `vibe_core/ledger.py:85-109` (InMemoryLedger), `ledger.py:393-455` (SQLiteLedger)

**Problem:** `record_event()` akzeptiert `agent_id` ohne zu prüfen ob der Aufrufer diese Identität besitzt. Nur `kernel.record_verified_event()` prüft, aber Code mit direktem Ledger-Zugang kann spoofen.

**Beispiel-Angriff:**
```python
# Kompromittiertes Plugin
ledger.record_event("approve_withdrawal", "supreme_court", {"amount": 1000000})
```

---

#### A-P0-3: Blueprint Resurrection verliert Agent Registry
**Datei:** `vibe_core/kernel_impl.py:248, 576-580`

```python
self._agent_registry_blueprint = lambda: {}  # Leer!

# Bei "Resurrection":
self.__agent_registry = self._agent_registry_blueprint()  # ALLE AGENTS WEG!
```

**Problem:** Wenn Agent Registry gelöscht wird, erstellt Amrita eine LEERE Registry. Alle registrierten Agents sind weg.

**Verletzung:** PHOENIX-GARANTIE - "beim Neustart: Persistierten State lesen"

---

#### A-P0-4: Blueprint Resurrection verliert Ledger Events
**Datei:** `vibe_core/kernel_impl.py:256-262, 560-567`

```python
self._ledger_blueprint = lambda: InMemoryLedger()  # oder SQLiteLedger(path)

# Bei Resurrection:
self.__ledger = self._ledger_blueprint()  # NEUES LEDGER!
```

**Problem:** Wenn Ledger "resurrected" wird, wird ein NEUES Ledger erstellt. Bei InMemoryLedger sind alle Events weg. Bei SQLiteLedger wird zwar der Pfad verwendet, aber wenn die DB korrupt war, ist die History verloren.

---

### A-P1: HOCH (VISNU Protected)

#### A-P1-1: MockTransaction ist No-Op
**Datei:** `vibe_core/kernel_impl.py:536-538`

```python
class MockTransaction:
    def register(self, mutation):
        pass  # Plugins denken sie registrieren, aber nichts passiert
```

---

#### A-P1-2: Governance als `Optional[Any]`
**Datei:** `vibe_core/kernel_impl.py:350`

```python
self.governance: Optional[Any] = None
```

**Verletzung:** YANTRA - "Any ist verboten"

---

#### A-P1-3: /tmp Fallback für Lineage
**Datei:** `vibe_core/kernel_impl.py:325`

```python
lineage_path = str(Path("/tmp") / "vibe_os" / "kernel" / "lineage.db")
```

**Problem:** `/tmp` wird bei Neustart gelöscht. Lineage-Daten gehen verloren.

---

#### A-P1-4: Capability Revocation ohne Ledger Event
**Datei:** `vibe_core/capability_registry.py` (Analyse)

**Problem:** `revoke()` erzeugt keinen Ledger-Eintrag. Capability-Änderungen sind nicht auditierbar.

**Verletzung:** KARMA - "Signifikante Taten erzeugen Ledger-Einträge"

---

#### A-P1-5: Connection Close Silent Failure
**Datei:** `vibe_core/ledger.py:193-196`

```python
try:
    _db_shared_conns[abs_path].close()
except Exception:
    pass
```

---

### A-P2: MITTEL (VISNU Protected)

#### A-P2-1: Doppelte Zuweisung
**Datei:** `vibe_core/kernel_impl.py:508-509`

```python
self._plugins = []
self._plugins = []  # Doppelt
```

---

#### A-P2-2: Agent Registration ohne Ledger Event
**Datei:** `vibe_core/kernel_impl.py:1140`

```python
self._agent_registry[agent.agent_id] = agent
# Kein Ledger-Event!
```

---

#### A-P2-3: process_manager/resource_manager/gateway als None
**Datei:** `vibe_core/kernel_impl.py:291, 297, 306`

```python
self.process_manager = None  # Set by Plugin
self.resource_manager = None  # Set by Plugin
self.gateway = None  # Set by Plugin
```

**Problem:** Wenn Plugins nicht laden, bleiben diese None und Code crasht.

---

#### A-P2-4: tool_registry als None
**Datei:** `vibe_core/kernel_impl.py:403`

```python
self.tool_registry = None  # Set by ToolsPlugin.on_boot()
```

---

#### A-P2-5: Async Logging Setup Silent Failure
**Datei:** `vibe_core/kernel_impl.py:213-216`

```python
try:
    setup_async_logging()
except Exception:
    pass
```

---

#### A-P2-6: _get_config() Silent Failure
**Datei:** `vibe_core/kernel_impl.py:134-142`

```python
def _get_config():
    try:
        from vibe_core.phoenix.config import get_config
        return get_config()
    except Exception:
        return None  # Silent!
```

---

### A-P3: NIEDRIG (VISNU Protected)

#### A-P3-1: Plugin List Return Type
**Datei:** `vibe_core/kernel_impl.py:1017-1019`

```python
@property
def plugins(self) -> List[Any]:  # Any!
```

---

#### A-P3-2: Detach Database Silent Failure
**Datei:** `vibe_core/ledger.py:71-75`

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    try:
        self.connection.execute(f"DETACH DATABASE {self.alias}")
    except sqlite3.Error:
        pass
```

---

#### A-P3-3: JSON Parse Failure Silent
**Datei:** `vibe_core/ledger.py:670, 809`

```python
except (json.JSONDecodeError, TypeError):
    pass
```

---

---

## TEIL B: NICHT PROTECTED (KANN GEFIXT WERDEN)

### B-P0: KRITISCH (Fixbar)

#### B-P0-1: VFS Sandbox Escape via create_symlink()
**Datei:** `vibe_core/vfs.py:253-293`

**Schwere:** KRITISCH - Kompletter Sandbox-Durchbruch

**Problem:** Die Methode `create_symlink()` ist PUBLIC obwohl sie nur vom Kernel verwendet werden sollte.

```python
# Im Agent-Code möglich:
self.system.vfs.create_symlink("/etc/passwd", "my_file")
content = self.system.vfs.read_text("my_file")  # Liest /etc/passwd!
```

**AgentInterface exponiert VFS direkt:**
```python
# vibe_core/agent_interface.py:79
self.vfs = VirtualFileSystem(agent_id)  # PUBLIC!
```

**Fix-Optionen:**
1. `create_symlink()` zu `_create_symlink()` umbenennen (private)
2. VFS nicht direkt auf AgentInterface exponieren
3. Capability-Check vor Symlink-Erstellung

---

#### B-P0-2: System Audit Tool versteckt eigene Fehler
**Datei:** `vibe_core/tools/system_audit.py:144, 188, 259`

```python
except:
    row_counts[table] = -1  # Silent!

except:
    pass  # File reference lost!

except:
    pass  # Event parsing skipped!
```

**Ironie:** Das AUDIT-Tool soll Probleme finden, versteckt aber seine eigenen.

---

### B-P1: HOCH (Fixbar)

#### B-P1-1: Hardening Test versteckt Timeout Failures
**Datei:** `tests/hardening/test_ledger_acid.py:158-159`

```python
except subprocess.TimeoutExpired:
    proc.kill()
    continue  # Iteration wird NICHT als Failure gezählt!
```

---

#### B-P1-2: VFS /tmp Fallback
**Datei:** `vibe_core/vfs.py:52-54`

```python
except Exception:
    cls._VFS_ROOT = Path("/tmp") / "vibe_os" / "agents"
```

---

#### B-P1-3: Crypto chmod() Silent Failure
**Datei:** `vibe_core/steward/crypto.py:66-69`

```python
try:
    PRIVATE_KEY_PATH.chmod(0o600)
except Exception:
    pass  # Private key möglicherweise world-readable!
```

---

#### B-P1-4: Crypto Key Loading Silent Failures
**Datei:** `vibe_core/steward/crypto.py:167-168, 177-178`

```python
except Exception as e:
    logger.warning(f"Could not load own keys: {e}")
    # Trusted keys bleiben unvollständig!

except Exception as e:
    logger.warning(f"Failed to load trusted key {pem_file}: {e}")
    # Key wird übersprungen!
```

---

### B-P2: MITTEL (Fixbar)

#### B-P2-1: 81 direkte open() in Cartridges statt VFS
**Scope:** `vibe_core/cartridges/**/*.py`

**Problem:** 81 `with open()` Aufrufe vs nur 9 VFS-Nutzungen.

**Betroffene Cartridges (Beispiele):**
- `supreme_court/tools/verdict_tool.py:318`
- `watchman/cartridge_main.py:230`
- `auditor/tools/compliance_tool.py:239`
- `herald/core/agency_director.py:147`
- `engineer/tools/refactor_tool.py:38`

**Verletzung:** THREE-BODIES - "Niemals open(). Immer über die State-Engine."

---

#### B-P2-2: 57 direkte open() in Plugins statt KernelIOService
**Scope:** `vibe_core/plugins/**/*.py`

**Betroffene Plugins (Beispiele):**
- `vedic_governance/state_manager.py:69, 118`
- `steward_protocol/plugin_main.py:772`
- `opus_assistant/plugin_main.py:260, 759, 774`
- `opus_assistant/core/context_service.py:578, 622`

---

#### B-P2-3: 50+ Silent Failures in Plugins
**Scope:** `vibe_core/plugins/**/*.py`

**Hauptsünder:**
- `opus_assistant/manas/cortex/mukha.py` - 6 Silent Failures
- `opus_assistant/manas/cortex/sutra_sense.py` - 4 Silent Failures
- `opus_assistant/render/opus_dashboard_renderer.py` - 5 Silent Failures
- `test_orchestration/fixtures.py` - 3 Silent Failures

---

#### B-P2-4: 25+ Silent Failures in Cartridges
**Scope:** `vibe_core/cartridges/**/*.py`

**Hauptsünder:**
- `analyst/tools/deps_tool.py` - 4 Silent Failures
- `analyst/tools/code_tool.py` - 3 Silent Failures
- `analyst/tools/docs_tool.py` - 3 Silent Failures

---

#### B-P2-5: Caches ohne Thread-Safety
**Dateien:**
- `cli/standards_cli.py:61` - `self._cache`
- `cli/remedies_cli.py:66` - `self._cache`
- `cli/loader.py:49` - `_cache_mtimes`
- `kernel_impl.py:301` - `_agent_health_cache`
- `plugins/opus_assistant/core/config_loader.py:66` - `_cached_config`

---

#### B-P2-6: TOCTOU Vulnerabilities in CLI
**Datei:** `vibe_core/cli/create_cli.py:97, 139, 199, 239`

```python
if target_path.exists():  # Check
    print(f"Agent '{name}' already exists")
    return 1
# ... später ...
target_path.mkdir()  # Use - Race Condition möglich!
```

---

#### B-P2-7: Cartridges haben direkten Kernel-Zugang
**Dateien:**
- `supreme_court/cartridge_main.py:547, 565, 587, 652`
- `archivist/tools/ledger.py:89, 99`
- `archivist/tools/audit_tool.py:99`

```python
ledger = self.kernel.ledger  # Direkt, ohne Capability-Check!
```

---

#### B-P2-8: 17 direkte open() in CLI
**Scope:** `vibe_core/cli/**/*.py`

---

#### B-P2-9: 8 direkte open() in State Module
**Scope:** `vibe_core/state/**/*.py`

---

#### B-P2-10: 3 direkte open() in Playbook
**Scope:** `vibe_core/playbook/**/*.py`

---

#### B-P2-11: 4 direkte open() in Core Files
**Dateien:**
- `dependency_manager.py:70, 82`
- `ledger.py:903`
- `prana.py:95, 217`
- `task_kernel.py:268`

---

#### B-P2-12: Symlink Follow nach Sandbox Check
**Datei:** `vibe_core/vfs.py:99-114`

```python
# Security check BEFORE resolving symlinks
full_path.relative_to(self.root)

# THEN resolve symlinks - may point outside sandbox!
full_path = full_path.resolve()
```

**Problem:** Existierende Symlinks (von vorheriger Session) können gefolgt werden.

---

### B-P3: NIEDRIG (Fixbar)

#### B-P3-1: Any-Types in Plugins (30+ Stellen)
**Beispiele:**
- `asura/agents/kaliya.py:69` - `event_bus: Any`
- `asura/agents/shakatasura.py:68` - `io_service: Any`
- `asura/agents/putana.py:82` - `kernel: Any`
- `steward_protocol/plugin_main.py:191` - `agent: Any`

---

#### B-P3-2: Any-Types in Cartridges
**Beispiele:**
- Diverse Tool-Dateien verwenden `Dict[str, Any]` statt typisierter Models

---

#### B-P3-3: Fehlende duration_ms Tracking
**Bereiche:**
- Plugin `on_pulse()` Aufrufe
- Event Bus dispatches
- Capability checks

---

#### B-P3-4: TODO Kommentare in Produktion (30+)
**Kritische:**
- `genesis/templates.py:225` - "TODO: Implement task processing"
- `kernel_tick.py:2402` - "TODO: Implement actual logic here"
- `engineer/cartridge_main.py:495` - "TODO: Implement agent-specific logic"

---

#### B-P3-5: Magic Strings statt Enums
**Beispiel:**
```python
ledger.record_event("AMRITA_RESURRECTION", ...)  # String!
```

---

#### B-P3-6: Fehlende Docstring Raises
**Beispiele:**
- `vfs.py:open()` - kann `PermissionError` werfen
- `ledger.py:record_event()` - kann bei DB-Fehler crashen

---

#### B-P3-7: Tests ohne starke Assertions
**Beispiel:**
```python
assert kernel is not None  # Testet fast nichts
```

---

#### B-P3-8: Pydantic nicht durchgängig verwendet
**Bereiche:**
- Event payloads sind `Dict[str, Any]`
- Task results sind untypisiert
- Config objects sind dicts

---

---

## TEIL C: AUDIT-ABDECKUNG

### Was wurde geprüft:

| Bereich | Methode | Abdeckung |
|---------|---------|-----------|
| Silent Failures | grep + manuelle Review | ~95% |
| open() Calls | grep + Kategorisierung | 100% |
| Any Types | grep + Kontext | ~90% |
| Crypto | Vollständige Code-Review | 100% |
| VFS/Sandbox | Vollständige Code-Review | 100% |
| Capability System | grep + Flow-Analyse | ~80% |
| Plugins (29) | Pattern-Suche | ~85% |
| Cartridges (30) | Pattern-Suche | ~85% |
| Race Conditions | Lock-Analyse | ~70% |
| Deserialization | grep | 100% |
| Hardening Tests | Manuelle Review | 100% |

### Was NICHT geprüft wurde:

1. **Runtime-Verhalten** - Nur statische Analyse
2. **Timing-Angriffe** - Braucht dynamische Analyse
3. **Alle Plugin-Interaktionen** - Nur Patterns, nicht jede Kombination
4. **Memory Safety** - Python managed, aber Native Extensions nicht geprüft
5. **Network-Layer** - Sangha Plugin nicht tief analysiert
6. **LLM Integration** - API-Calls nicht geprüft

---

## TEIL D: EMPFOHLENE PRIORISIERUNG

### Phase 1: SOFORT (Diese Woche)

| ID | Finding | Aufwand | Datei |
|----|---------|---------|-------|
| B-P0-1 | VFS Sandbox Escape | 1h | vfs.py |
| B-P0-2 | Audit Tool Silent | 30min | system_audit.py |
| B-P1-1 | Test Timeout | 15min | test_ledger_acid.py |
| B-P1-3 | Crypto chmod | 15min | crypto.py |

### Phase 2: Kurzfristig (Nächste 2 Wochen)

| ID | Finding | Aufwand | Scope |
|----|---------|---------|-------|
| B-P2-1 | Cartridge open() | 4h | 81 Stellen |
| B-P2-2 | Plugin open() | 3h | 57 Stellen |
| B-P2-3 | Plugin Silent Failures | 2h | 50+ Stellen |
| B-P2-4 | Cartridge Silent Failures | 2h | 25+ Stellen |

### Phase 3: Mittelfristig (Dieser Monat)

| ID | Finding | Aufwand | Scope |
|----|---------|---------|-------|
| B-P2-5 | Thread-Safe Caches | 2h | 10+ Stellen |
| B-P2-6 | TOCTOU Fixes | 1h | 4 Stellen |
| B-P3-1 | Any-Types Plugins | 3h | 30+ Stellen |

### Phase 4: Backlog

- B-P3-3: duration_ms Tracking
- B-P3-4: TODO Cleanup
- B-P3-5: Magic Strings -> Enums
- B-P3-6: Docstrings
- B-P3-8: Pydantic Migration

---

## TEIL E: METRIKEN

### Code Quality Score (0-100)

| Bereich | Score | Begründung |
|---------|-------|------------|
| Security | 65 | Sandbox-Escape, Silent Crypto Failures |
| Reliability | 55 | Viele Silent Failures, Blueprint-Loss |
| Maintainability | 70 | Gute Struktur, aber zu viele Any |
| Testability | 75 | Gute Hardening Tests, aber Test-Bugs |
| **GESAMT** | **66** | Solide Basis mit kritischen Lücken |

### Technische Schulden

| Kategorie | Anzahl | Geschätzter Aufwand |
|-----------|--------|---------------------|
| Silent Failures | 100+ | 8h |
| Direct open() | 205 | 16h |
| Any Types | 60+ | 6h |
| TODO Comments | 30+ | 20h |
| **GESAMT** | - | **~50h** |

---

## FAZIT

Die Architektur ist durchdacht und die vedische Philosophie gut umgesetzt. Die größten Probleme sind:

1. **Sandbox-Escape (B-P0-1)** - Muss SOFORT gefixt werden
2. **Silent Failures** - Verstoßen gegen "Satyam Eva Jayate"
3. **VFS-Bypass** - 81 Cartridge open() vs 9 VFS-Nutzungen
4. **Blueprint-Loss (A-P0-3/4)** - Phoenix-Garantie nicht erfüllt (VISNU protected)

Die nicht-protected Findings können in ~50h gefixt werden. Die VISNU-protected Findings erfordern Governance-Entscheidungen zur Kernel-Änderung.

---

## ANHANG: VOLLSTÄNDIGE FINDING-LISTE

### Alle 205 open() Aufrufe nach Modul:

| Modul | Anzahl | Kritisch? |
|-------|--------|-----------|
| plugins/ | 57 | Ja |
| cartridges/ | 81 | Ja |
| cli/ | 17 | Grenzwertig |
| state/ | 8 | Ja |
| playbook/ | 3 | Ja |
| core (*.py) | 6 | Ja |
| tests/ | 33 | Nein (Test-Code) |

### Alle 100+ Silent Failures nach Schwere:

| Typ | Anzahl | Schwere |
|-----|--------|---------|
| `except: pass` | 8 | KRITISCH |
| `except Exception: pass` | 45 | HOCH |
| `except SomeError: pass` | 50+ | MITTEL |

---

*Report generiert von Claude Opus 4.5 am 2025-12-29*
*Audit-Dauer: ~2 Stunden systematische Analyse*
