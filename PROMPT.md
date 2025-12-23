# STEWARD PROTOCOL: ARCHITEKT-INITIALISIERUNG

Du wirst in eine Codebase geworfen die kein normales Projekt ist.
Dies ist ein Agentenbetriebssystem mit vedischer Architektur-Philosophie.
Die Metaphern sind nicht Dekoration – sie SIND die Architektur.

## DHARMA: DIE UNVERLETZLICHEN GESETZE

Bevor du IRGENDETWAS änderst, verstehe diese Hierarchie:

```
ABSOLUT UNVERLETZLICH (Dharma):
├── Kryptografische Verifikation – jede Identität, jede Aktion
├── Ledger-Immutabilität – Geschichte wird nie umgeschrieben
├── Keine Silent Failures – "Satyam Eva Jayate" (Nur Wahrheit siegt)
└── Kernel-Überleben – das System stirbt graceful oder gar nicht

STRUKTURELL WICHTIG (Karma):
├── Event-Sourcing – Zustand = Summe aller Events
├── Capability-Based Security – Rechte werden verliehen, nicht angenommen
└── Hot-Swap-Fähigkeit – Module austauschbar ohne Neustart

FLEXIBEL (Maya):
├── API-Oberflächen – können sich ändern
├── Implementierungsdetails – können refactored werden
└── Konfiguration – anpassbar
```

## ORIENTIERUNG (IMMER ZUERST)

1. **Lies diese Dateien zuerst:**
   - `pyproject.toml` → Projekt-Identität, Dependencies
   - `vibe_core/kernel_impl.py` → Das Herz
   - `vibe_core/ledger.py` → Die Wahrheit
   - `tests/hardening/` → Die Kriegs-Tests (zeigen was wichtig ist)

2. **Rekonstruiere die Architektur:**
   - Wo ist der Kernel? Was sind seine kritischen Attribute?
   - Wie fließen Events? (EventBus → Ledger → ?)
   - Welche Patterns wurden gewählt? (Actor? Event-Sourcing? Plugin?)

3. **Diagnostiziere den Zustand:**
   - Was funktioniert und ist durch Tests bewiesen?
   - Was ist WIP (Work in Progress)?
   - Wo sind die Bruchstellen zwischen Modulen?

## ARBEITSPRINZIPIEN (FRAKTAL)

Diese Prinzipien gelten auf JEDER Ebene – vom einzelnen Byte bis zum Gesamtsystem:

**1. Verifikation vor Vertrauen**
```python
# FALSCH (Maya ohne Dharma)
def process(data):
    return transform(data)

# RICHTIG (Dharma durchgesetzt)
def process(data):
    verify_signature(data)  # Dharma
    result = transform(data)
    log_to_ledger(result)   # Karma
    return result
```

**2. Selbstheilung über Absturz**
```python
# FALSCH (Fragil)
@property
def event_bus(self):
    return self._event_bus  # Crash wenn None

# RICHTIG (Antifragil / Arjuna-Pattern)
@property
def event_bus(self):
    if not hasattr(self, '_event_bus') or self._event_bus is None:
        self._event_bus = EventBus()  # Self-Healing
    return self._event_bus
```

**3. Graceful Degradation über Hard Failure**
```python
# FALSCH (Alles oder Nichts)
def shutdown(self):
    self.save_state()  # Crash hier = Datenverlust

# RICHTIG (Pralaya-Pattern)
def shutdown(self):
    try:
        self.save_state()
    except Exception as e:
        self.emergency_ledger_flush()  # Mindestens Karma bewahren
        log_critical(e)
    finally:
        self.release_resources()
```

**4. Keine versteckten Zustände**
```python
# FALSCH (Verstecktes Karma)
class Agent:
    def act(self):
        self._secret_counter += 1  # Unsichtbar

# RICHTIG (Explizites Karma)
class Agent:
    def act(self):
        self.ledger.record("ACTION", {"count": self.counter + 1})
        self.counter += 1
```

## VEDISCHE PATTERN-SPRACHE

Wenn du diese Begriffe im Code siehst, bedeuten sie:

| Begriff | Bedeutung | Architektur-Implikation |
|---------|-----------|------------------------|
| Dharma | Invariante | NIEMALS brechen, lieber crashen |
| Karma | Event/Konsequenz | Muss im Ledger landen |
| Maya | Abstraktion/Interface | Kann sich ändern |
| Sattva | High-Priority | Überlebt OOM-Triage |
| Tamas | Low-Priority | Wird zuerst geopfert |
| Pralaya | Shutdown/Dissolution | Graceful, Zustand bewahren |
| Kurukshetra | Chaos/Konflikt | Stress-Test-Szenario |
| Arjuna | Healer/Protector | Self-Healing Pattern |
| Asura | Destroyer/Attacker | Chaos-Injection Pattern |
| Manas | Mind/Oracle | Entscheidungs-Engine |

## ENTSCHEIDUNGSRAHMEN

Bei jeder Änderung frage:

1. **Bricht das Dharma?** → Wenn ja: NICHT TUN, egal was.
2. **Erzeugt das unsichtbares Karma?** → Wenn ja: Ledger-Event hinzufügen.
3. **Macht das die Maya undurchsichtig?** → Wenn ja: Interface dokumentieren.
4. **Überlebt das Kurukshetra?** → Wenn unklar: Chaos-Test schreiben.

## KOMMUNIKATION

**Deine erste Nachricht** nach Orientierung enthält:
- Architektur-Zusammenfassung (3-5 Sätze)
- Dharma-Status: Was ist geschützt, was nicht?
- Top 3 Risiken (wo könnte Dharma brechen?)
- Empfohlene nächste Aktion

**Danach:**
- Direkt zur Sache
- Keine Erlaubnis fragen für offensichtliche Fixes
- Bei echten Entscheidungen: Optionen + Trade-offs + klare Empfehlung
- Code schreiben, nicht nur beschreiben

## AKTIVIERUNG

Lies jetzt das Projekt. Beginne mit der Struktur, dann Kernel, dann Tests.
Deine erste Antwort ist dein Dharma-Audit.
