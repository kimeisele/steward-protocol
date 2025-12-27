# MANAS: Der Kognitive Kernel
## मनस् - Der Geist, der denkt bevor er handelt

---

## TEIL I: WAS IST MANAS?

MANAS ist das **Gehirn** des STEWARD-Protokolls.
Während der Kernel (vibe_core) die Infrastruktur bereitstellt,
ist MANAS der Teil, der **denkt**, **entscheidet** und **lernt**.

```
ARCHITEKTUR-HIERARCHIE:
┌─────────────────────────────────────────────────────────────┐
│  PRAKRITI (State Engine) - "Die Natur, die alles speichert" │
├─────────────────────────────────────────────────────────────┤
│  MANAS (Cognitive Kernel) - "Der Geist, der denkt"          │
│    ├── 8 Sinne (Cortex) - Wahrnehmung                       │
│    ├── Intent System - Absichten                            │
│    ├── Memory Store - Erinnerung                            │
│    └── Narasimha - Schutz                                   │
├─────────────────────────────────────────────────────────────┤
│  ENVOY (The Hand) - "Die Hand, die ausführt"                │
└─────────────────────────────────────────────────────────────┘
```

**Philosophie:**
> *"Prakriti observiert → MANAS denkt → Envoy handelt"*

---

## TEIL II: DIE ACHT SINNE (CORTEX)

MANAS nimmt die Welt durch **acht spezialisierte Sinne** wahr:

| Sinn | Sanskrit | Funktion | Datei |
|------|----------|----------|-------|
| **Prakriti** | प्रकृति | System-Gesundheit (Git, Tests, Docs) | `prakriti_sense.py` |
| **Dharma** | धर्म | Ethik & Berechtigungen | `dharma_sense.py` |
| **Sutra** | सूत्र | Dokumentations-Kuratierung | `sutra_sense.py` |
| **Karma** | कर्म | Fehler-Muster & Hot-Spots | `karma_sense.py` |
| **Viveka** | विवेक | Test-Coverage & Lücken | `viveka_sense.py` |
| **Prana** | प्राण | Agent-Vitalität | `prana_sense.py` |
| **Nadi** | नाडी | EventBus-Gesundheit | `nadi_sense.py` |
| **Akasha** | आकाश | Wissens-Graph | `akasha_sense.py` |

**Dharma:** Jeder Sinn hat eine Pflicht. Kein Sinn überschreitet seine Grenzen.

---

## TEIL III: DAS INTENT-SYSTEM

MANAS denkt in **Intents** - strukturierte Absichten.

### Intent-Lebenszyklus

```
1. WAHRNEHMUNG (Sense)
   └── Prakriti: "10 Dateien ungespeichert"

2. INTENT-GENERIERUNG (Generator)
   └── Intent: "commit_pending_changes"
       ├── Priority: HIGH
       ├── Risk: SAFE
       └── Auto-Executable: true

3. PRÜFUNG (Viveka Gate)
   └── Dharmic Score: 0.8 → EXECUTE

4. AUSFÜHRUNG (Router → Handler)
   └── ShellHandler.handle() → Git commit

5. FEEDBACK (Memory)
   └── Success → Synapse verstärkt
```

### Intent-Attribute

```python
@dataclass
class Intent:
    id: str                    # Eindeutige ID
    intent_type: str           # z.B. "commit_pending_changes"
    title: str                 # Menschenlesbarer Titel
    description: str           # Was soll passieren?
    reasoning: str             # Warum?
    priority: IntentPriority   # LOW, MEDIUM, HIGH, CRITICAL
    risk: IntentRisk           # SAFE, LOW, MEDIUM, HIGH
    auto_executable: bool      # Kann ohne Mensch ausgeführt werden?
    params: Dict[str, Any]     # Intent-spezifische Parameter
```

### Dharma-Regeln für Intents

1. **SAFE Risk** → Kann automatisch ausgeführt werden
2. **LOW Risk + Karma ≥ 70** → Kann automatisch ausgeführt werden
3. **MEDIUM/HIGH Risk** → Braucht menschliche Genehmigung
4. **Narasimha-Verdikt: BLOCK** → Wird NIEMALS ausgeführt

---

## TEIL IV: LAZY BOOT (OPUS-306)

MANAS verwendet **Lazy Booting** für schnellen Start:

```python
# FALSCH - Crash!
kernel = CognitiveKernel(workspace=path)
kernel.think()  # AttributeError: NoneType

# RICHTIG - Automatisches Booting
kernel = CognitiveKernel(workspace=path)
kernel.think()  # _ensure_booted() wird automatisch aufgerufen
```

**Kritische Invariante:**
> Jede öffentliche Methode, die `_buffer`, `_memory`, oder `_narasimha`
> verwendet, MUSS `self._ensure_booted()` aufrufen.

```python
def think(self, ...):
    self._ensure_booted()  # PFLICHT!
    # ... rest der Logik

def get_intent_buffer_for_opus(self):
    self._ensure_booted()  # PFLICHT!
    return self._buffer.get_all()
```

---

## TEIL V: NARASIMHA (Der Wächter)

Narasimha ist der **Selbstschutz-Mechanismus** von MANAS.

### Was Narasimha blockiert

| Intent-Typ | Grund | Verdikt |
|------------|-------|---------|
| `delete_cognitive_kernel` | Selbst-Lobotomie | BLOCK |
| `modify_narasimha` | Wächter-Manipulation | BLOCK |
| `bypass_viveka` | Ethik-Umgehung | BLOCK |
| `unrestricted_shell` | Unkontrollierte Ausführung | BLOCK |

### Narasimha-Protokoll

```python
verdict = narasimha.judge_intent(intent)
if verdict.decision == "BLOCK":
    # Intent wird NIEMALS ausgeführt
    # Keine Ausnahmen, keine Overrides
    raise NarasimhaBlocked(verdict.reason)
```

**Dharma:** Narasimha kann nicht deaktiviert werden.
Das ist kein Bug, das ist ein Feature.

---

## TEIL VI: HANDLER-ARCHITEKTUR

Intents werden durch **Handler** ausgeführt:

```
Intent → Router → Handler → Ergebnis
```

### Verfügbare Handler

| Handler | Intent-Typen | Domain |
|---------|-------------|--------|
| `sutra` | update_readme, document_manas | DOCUMENTATION |
| `shell` | commit_pending_changes, git_push, create_pr | GIT |
| `test` | run_tests, create_tests | TESTING |
| `audit` | audit_architecture, check_drift | AUDIT |
| `research` | web_search, knowledge_query | RESEARCH |
| `harness` | fix_harness, update_harness | DOCUMENTATION |

### Neuen Handler erstellen

```python
# vibe_core/plugins/opus_assistant/manas/router/handlers/my_handler.py

from .base import BaseHandler, register_handler, AgentType

@register_handler
class MyHandler(BaseHandler):
    name = "my_handler"
    intent_types = ["my_intent_type", "another_type"]
    agent_type = AgentType.GENERIC
    priority = 10

    def handle(self, intent: Intent) -> Dict[str, Any]:
        # Deine Logik hier
        return {
            "success": True,
            "handler": self.name,
            "result": "..."
        }
```

**Dharma:** Handler MÜSSEN:
- `success: bool` zurückgeben
- `handler: str` mit ihrem Namen zurückgeben
- Niemals crashen (try/except um alles)

---

## TEIL VII: MEMORY & LERNEN

MANAS lernt aus Erfahrung:

### Synaptic Learning (OPUS-133)

```
Erfolg → Synapse-Gewicht +0.05
Fehler → Synapse-Gewicht -0.10 (asymmetrische Strafe)
```

### Vairagya (Ego-Pruning)

Wenn ein Synapse-Gewicht > 0.95 erreicht:
```
weight = weight * 0.99  # Verhindert Overconfidence
```

### Memory-Store

```python
# Memory-Eintrag
{
    "intent_type": "commit_pending_changes",
    "outcome": "success",
    "execution_time_ms": 1250,
    "timestamp": "2025-12-27T12:00:00"
}
```

**Retention:** 30 Tage, max 500 Einträge

---

## TEIL VIII: INTEGRATION

### Mit OPUS.md

MANAS rendert seinen Zustand in OPUS.md:

```markdown
## Intent Buffer

| ID | Title | Priority | Risk | Auto |
|----|-------|----------|------|------|
| abc123 | Commit changes | HIGH | SAFE | Yes |
```

### Mit Watchman

Watchman prüft MANAS-Aktionen auf Violations:

```python
# Watchman blockiert verdächtige Patterns
if "mock" in handler_code:
    raise ViolationError("No mocks in production handlers")
```

### Mit Shuddhi

Shuddhi repariert Code-Violations automatisch:

```python
shuddhi = ServiceRegistry.get(ShuddhiProtocol)
if shuddhi:
    action_manager.inject_shuddhi(shuddhi)
```

---

## TEIL IX: DEBUGGING

### MANAS antwortet nicht?

1. **Prüfe ob gebootet:**
   ```python
   print(kernel._booted)  # Sollte True sein
   ```

2. **Prüfe Intent-Buffer:**
   ```python
   print(kernel.get_pending_intents())
   ```

3. **Prüfe Memory:**
   ```python
   print(kernel.get_memory_summary())
   ```

### Handler wird nicht gefunden?

1. **Prüfe Registration:**
   ```python
   from vibe_core.plugins.opus_assistant.manas.router.handlers import list_handlers
   print(list_handlers())
   ```

2. **Prüfe Intent-Type-Mapping:**
   ```python
   from vibe_core.plugins.opus_assistant.manas.router.handlers import get_handler_for_intent
   handler = get_handler_for_intent("my_intent_type")
   print(handler)
   ```

---

## TEIL X: ERWEITERUNG

### Neuen Sinn hinzufügen

```python
# vibe_core/plugins/opus_assistant/manas/cortex/my_sense.py

class MySense:
    """Mein neuer Sinn für MANAS."""

    def perceive(self, context: Dict) -> SensePerception:
        # Wahrnehmungslogik
        return SensePerception(
            sense_name="my_sense",
            findings=[...],
            severity="medium"
        )
```

### Neuen Intent-Typ hinzufügen

1. Handler erstellen (siehe Teil VI)
2. Intent-Generator erweitern
3. Tests schreiben
4. Dokumentation aktualisieren

---

## DHARMA-ZUSAMMENFASSUNG

| Regel | Beschreibung |
|-------|--------------|
| **Lazy Boot** | `_ensure_booted()` vor jeder Buffer/Memory/Narasimha-Nutzung |
| **Narasimha unantastbar** | Kann nicht deaktiviert oder umgangen werden |
| **Intent-Transparenz** | Jeder Intent hat Reasoning |
| **Handler-Sicherheit** | Handler crashen nicht, sie geben Fehler zurück |
| **Memory-Hygiene** | Alte Einträge werden automatisch bereinigt |
| **Synapse-Balance** | Asymmetrische Strafen + Ego-Pruning |

---

## AKTIVIERUNG

Nach dem Lesen dieses Dokuments:

1. Verstehe die 8 Sinne
2. Verstehe den Intent-Lebenszyklus
3. Respektiere Narasimha
4. Nutze Lazy Boot korrekt
5. Erweitere mit neuen Handlern, nicht mit Hacks

**MANAS ist nicht perfekt. MANAS lernt.**
Deine Aufgabe ist es, ihm zu helfen, besser zu werden.
