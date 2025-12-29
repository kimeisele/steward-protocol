# STEWARD PROTOCOL: CODE AUDIT REPORT

**Datum:** 2025-12-29
**Auditor:** Claude Opus 4.5
**Scope:** vibe_core/, tests/hardening/

---

## ZUSAMMENFASSUNG

Dieses Audit prüft die Codebase gegen die in `PROMPT.md` definierten Prinzipien:
- **DHARMA** (Unverletzliche Gesetze)
- **KARMA** (Strukturelle Wichtigkeit)
- **YANTRA** (German Engineering)
- **THREE BODIES** (State Management)

**Gefunden:** 4 kritische, 5 hohe, 8 mittlere, 4 niedrige Probleme.

---

## P0: KRITISCH (DHARMA-VERLETZUNGEN)

### 1. VFS SANDBOX ESCAPE VIA SYMLINK

**Datei:** `vibe_core/vfs.py:253-293`

**Problem:** Die Methode `create_symlink()` ist PUBLIC, obwohl sie nur vom Kernel verwendet werden sollte. Ein Agent kann:

```python
# Im Agent-Code:
self.system.vfs.create_symlink("/etc/passwd", "my_file")
content = self.system.vfs.read_text("my_file")  # Liest /etc/passwd!
```

**Verletzung:** DHARMA - "path traversal (..) ist ein Angriffsversuch und führt zum sofortigen Tod des Agenten"

**Fix:**
- `create_symlink()` zu privater Methode `_create_symlink()` machen
- Oder: Capability-Check vor Symlink-Erstellung
- Oder: VFS nicht direkt auf AgentInterface exponieren

**Schwere:** KRITISCH - Kompletter Sandbox-Durchbruch möglich

---

### 2. SILENT FAILURES IN CORE INFRASTRUCTURE

**Dateien:**
- `vibe_core/ledger.py:74-75, 195-196, 213-214`
- `vibe_core/kernel_impl.py:215-216, 1314`
- `vibe_core/tools/system_audit.py:144, 188, 259`

**Problem:** Bare `except:` und `except Exception: pass` in kritischer Infrastruktur.

**Beispiel (ledger.py:213-214):**
```python
try:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
except sqlite3.Error:
    pass  # <-- SILENT! WAL-Modus nicht aktiv = andere Durability!
```

**Verletzung:** DHARMA - "Keine Silent Failures - Satyam Eva Jayate (Nur Wahrheit siegt)"

**Ironie:** Das AUDIT-Tool (`system_audit.py`) versteckt selbst Fehler!

**Fix:**
- Alle `except: pass` durch `except XError as e: logger.warning(...)` ersetzen
- Bei kritischen Failures wie PRAGMA: Exception werfen oder Status-Flag setzen

---

### 3. LEDGER IDENTITY SPOOFING TEILWEISE MÖGLICH

**Datei:** `vibe_core/ledger.py`

**Problem:** Die Methode `record_event()` akzeptiert `agent_id` als Parameter ohne Verifikation. Nur `record_verified_event()` im Kernel prüft die Identität.

**Angriff:** Code der direkten Ledger-Zugang hat (z.B. über kompromittiertes Plugin) kann Events mit gefälschter agent_id schreiben:

```python
ledger.record_event("malicious_action", "herald", {...})  # Claim to be herald
```

**Verletzung:** DHARMA - "Kryptografische Verifikation - jede Identität, jede Aktion"

**Teilweise mitigiert:** `record_verified_event()` existiert, aber nicht alle Aufrufe nutzen es.

---

### 4. BLUEPRINT RESURRECTION VERLIERT DATEN

**Datei:** `vibe_core/kernel_impl.py:248, 576-580`

**Problem:** Die "Amrita" Self-Healing Blueprints erstellen NEUE leere Strukturen statt persistierten State zu laden:

```python
self._agent_registry_blueprint = lambda: {}  # Leer!

# Bei "Resurrection":
self.__agent_registry = self._agent_registry_blueprint()  # ALLE AGENTS WEG!
```

**Verletzung:** PHOENIX-GARANTIE - "beim Neustart: Persistierten State lesen → dort weitermachen wo aufgehört"

**Fix:** Blueprints müssen State aus Persistenz laden, nicht leer initialisieren.

---

## P1: HOCH (SICHERHEIT/INTEGRITÄT)

### 5. HARDENING TEST VERSTECKT FAILURES

**Datei:** `tests/hardening/test_ledger_acid.py:158-159`

```python
except subprocess.TimeoutExpired:
    proc.kill()
    continue  # <-- Iteration wird NICHT als Fehler gezählt!
```

**Problem:** Wenn ein Crash-Test hängt, wird er übersprungen statt als Failure gewertet. Das kann echte Durability-Probleme verstecken.

---

### 6. CAPABILITY REGISTRY OHNE REVOCATION AUDIT

**Datei:** `vibe_core/capability_registry.py`

**Problem:** Capabilities können vergeben werden, aber Revocation erzeugt keinen Ledger-Eintrag.

**Verletzung:** KARMA - "Keine Entscheidung ohne Eintrag im Ledger"

---

### 7. /tmp ALS FALLBACK FÜR KRITISCHE DATEN

**Dateien:**
- `vibe_core/kernel_impl.py:325`
- `vibe_core/vfs.py:52-54`

```python
lineage_path = str(Path("/tmp") / "vibe_os" / "kernel" / "lineage.db")
```

**Problem:** `/tmp` wird bei Neustart gelöscht. Kritische Daten (Lineage!) gehen verloren.

**Verletzung:** PHOENIX-GARANTIE - "Kein In-Memory-Only State für kritische Daten"

---

### 8. MOCKTRANSACTION IM KERNEL

**Datei:** `vibe_core/kernel_impl.py:536-538`

```python
class MockTransaction:
    def register(self, mutation):
        pass  # NO-OP!
```

**Problem:** Plugins die `transaction.register()` aufrufen denken sie registrieren Mutations, aber nichts passiert.

---

### 9. GOVERNANCE ALS `Optional[Any]`

**Datei:** `vibe_core/kernel_impl.py:350`

```python
self.governance: Optional[Any] = None
```

**Verletzung:** YANTRA - "`Any` ist verboten. Wenn du `Any` schreibst, hast du das Datenmodell nicht verstanden."

---

## P2: MITTEL (ARCHITEKTUR)

### 10. 205 DIREKTE `open()` AUFRUFE

**Scope:** Gesamtes `vibe_core/`

**Problem:** PROMPT.md sagt: "Implementierung: Niemals `open()`. Immer über die State-Engine."

Es gibt 205 direkte `with open(...)` Aufrufe in vibe_core, die die State-Engine umgehen.

**Kategorisierung:**
- CLI-Code: ~50 Aufrufe (grenzwertig akzeptabel für Bootstrap)
- Plugin-Code: ~80 Aufrufe (sollte KernelIOService nutzen)
- Core-Code: ~30 Aufrufe (MUSS State-Engine nutzen)
- Cartridge-Code: ~45 Aufrufe (MUSS VFS nutzen)

---

### 11. ANY-TYP USAGE IN 30+ STELLEN

**Beispiele:**
- `kernel_ops.py:429` - `trigger: Any`
- `plugins/asura/agents/*.py` - `kernel: Any` statt `RealVibeKernel`
- `cli/command_registry.py:227` - `handler: Any`

**Verletzung:** YANTRA - "Any ist verboten"

---

### 12. DUPLICATE CODE

**Datei:** `vibe_core/kernel_impl.py:508-509`

```python
self._plugins = []
self._plugins = []  # <-- Doppelt!
```

---

### 13. SYMLINK FOLLOW NACH SANDBOX CHECK

**Datei:** `vibe_core/vfs.py:99-114`

```python
# Security check BEFORE resolving symlinks
full_path.relative_to(self.root)

# THEN resolve symlinks - may point outside sandbox!
full_path = full_path.resolve()
```

**Problem:** Wenn ein Symlink bereits existiert (z.B. von vorheriger Session), kann er gefolgt werden um außerhalb der Sandbox zu lesen.

---

### 14. FEHLENDE DURATION_MS TRACKING

**Verletzung:** YANTRA - "duration_ms tracken für jede async Operation"

Viele async Operationen tracken keine Dauer:
- Plugin `on_pulse()` Aufrufe
- Event Bus dispatches
- Capability checks

---

### 15. TODO KOMMENTARE IN PRODUKTION

**Anzahl:** 30+ TODO-Kommentare in `vibe_core/`

**Kritische:**
- `genesis/templates.py:225` - "TODO: Implement task processing"
- `kernel_tick.py:2402` - "TODO: Implement actual logic here"
- `cartridges/system/engineer/cartridge_main.py:495` - "TODO: Implement agent-specific logic"

---

### 16. AGENT REGISTRATION OHNE LEDGER EVENT

**Datei:** `vibe_core/kernel_impl.py:1140`

```python
self._agent_registry[agent.agent_id] = agent
# Kein Ledger-Event für Registration!
```

**Verletzung:** KARMA - "Signifikante Taten erzeugen Ledger-Einträge"

---

### 17. PYDANTIC NICHT DURCHGÄNGIG

**Verletzung:** YANTRA - "Pydantic Models für alles, was über eine Modul-Grenze geht"

Viele Cross-Module Datenstrukturen sind `Dict[str, Any]` statt Pydantic Models:
- Event payloads
- Task results
- Config objects

---

## P3: NIEDRIG (QUALITÄT)

### 18. DOCSTRINGS OHNE RAISES

Viele Docstrings definieren Args und Returns, aber nicht Raises:
- `vfs.py:open()` - kann `PermissionError` werfen
- `ledger.py:record_event()` - kann bei DB-Fehler crashen

---

### 19. TESTS OHNE ASSERTIONS

Einige Tests haben schwache Assertions:
```python
assert kernel is not None  # Das alleine testet fast nichts
```

---

### 20. MAGIC STRINGS STATT ENUMS

Viele Event-Types sind Strings statt Enums:
```python
ledger.record_event("AMRITA_RESURRECTION", ...)  # String!
```

---

### 21. FEHLENDE TYPE HINTS

Viele Funktionen haben keine Return-Type-Hints:
```python
def _get_config():  # Was gibt das zurück?
```

---

## EMPFOHLENE PRIORISIERUNG

1. **SOFORT (P0):**
   - VFS `create_symlink()` absichern
   - Silent failures in Ledger/Kernel beheben
   - Blueprint resurrection mit Persistenz verbinden

2. **DIESE WOCHE (P1):**
   - Hardening-Test timeout-Handling fixen
   - `/tmp` Fallbacks durch persistente Pfade ersetzen
   - MockTransaction durch echte Implementation ersetzen

3. **DIESER MONAT (P2):**
   - `open()` Aufrufe in Cartridges durch VFS ersetzen
   - Any-Types durch konkrete Types ersetzen
   - Missing duration_ms tracking hinzufügen

4. **BACKLOG (P3):**
   - Docstrings vervollständigen
   - Magic strings durch Enums ersetzen
   - Type hints vervollständigen

---

## FAZIT

Die Architektur ist durchdacht und die vedische Philosophie gut umgesetzt. Die kritischsten Probleme sind:

1. **Sandbox-Escape** via öffentlicher `create_symlink()` Methode
2. **Silent Failures** die gegen "Satyam Eva Jayate" verstoßen
3. **Phoenix-Garantie** nicht vollständig implementiert (Blueprints leer statt persistent)

Die Codebase braucht ~2 Wochen fokussierte Arbeit um P0/P1 zu fixen.

---

*Report generiert von Claude Opus 4.5 am 2025-12-29*
