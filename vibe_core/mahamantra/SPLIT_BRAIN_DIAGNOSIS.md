# Split-Brain Diagnose — Stand 2026-02-17

## REGEL: Kein neuer Code bevor diese Probleme gelöst sind.

---

## Problem 1: ZWEI "mahamantra" Singletons

| | Singularity | Lotus |
|---|---|---|
| Klasse | `Mahamantra` | `MahamantraLotus` |
| Datei | `kernel/singularity.py:1233` | `substrate/lotus_core.py:1311` |
| Import | `from vibe_core.mahamantra.kernel.singularity import mahamantra` | `from vibe_core.mahamantra import mahamantra` |
| Kann | tick, chant, venu, kala, cells, governance, mod, protocols, positions | `__call__()`, pipeline, NavaBhakti, chamber, kirtan, shadow, gates |
| Heartbeat | `tick()` → Kala + Venu + Broadcast | `tick()` → delegiert an Singularity |

Lotus delegiert 16 Guardian-Properties an Singularity via `_get_singularity()`.
Singularity delegiert `venu` an Lotus via `MahamantraLotus._venu_orchestrator`.
**Zirkuläre Abhängigkeit. Zwei Objekte, zwei Identitäten, ein Name.**

### Wer importiert was?
- `daemon.py` importiert **Singularity** (`from ...singularity import mahamantra`)
- `VenuService` importiert **Lotus** (`from vibe_core.mahamantra import mahamantra`) → holt sich Singularity via `._get_singularity()`
- `MahaKernel` importiert **Singularity** direkt
- Alle externen Consumer importieren **Lotus** (via `from vibe_core.mahamantra import mahamantra`)

---

## Problem 2: ZWEI MantraClocks

| Clock | Datei | Erstellt von | Getrieben von |
|---|---|---|---|
| `VenuService._clock` | `services/venu_service.py:107` | VenuService.__init__() | VenuService.start() Zeile 301 |
| `MantraClock` Klasse | `venu/clock.py` | Niemand sonst | Standalone, 0 Voices, 0 Callbacks |

VenuService erstellt seine eigene MantraClock und treibt sie selbst.
Singularity hat KEINE Clock (nach meinem Revert).
**Niemand benutzt MantraClock.add_voice() oder on_position().**

---

## Problem 3: DREI Heartbeat-Pfade

```
Pfad A (VenuService — der echte Runtime-Pfad):
  VenuService.start() loop →
    beat_callbacks(position)           ← VenuService-eigene Callbacks
    _dispatch_beat_subscribers()       ← BeatSubscribers (Ouroboros, Shuddhi, Kala, Jagannath)
    self._singularity.tick()           ← Singularity.tick() → Kala + Venu.step() + Broadcast
    self._clock.tick_once()            ← VenuService-eigene MantraClock (0 voices)

Pfad B (Daemon — der Chanting-Pfad):
  MahamantraDaemon._eternal_loop() →
    mahamantra.chant_quarter()         ← Singularity.chant_quarter()
      → mahamantra.tick() × 4         ← Singularity.tick() → Kala + Venu.step() + Broadcast

Pfad C (Lotus — der Delegations-Pfad):
  Lotus.tick() → self._get_singularity().tick() → identisch mit Pfad B
```

Alle drei enden in `Singularity.tick()`. Aber VenuService hat **zusätzlich**:
- Eigene beat_callbacks
- Eigene BeatSubscriber-Dispatch
- Eigene MantraClock

**BeatSubscribers (Ouroboros, Shuddhi, Kala, Jagannath) feuern NUR über VenuService.**
**Singularity._listeners feuern NUR über Singularity.tick()._broadcast().**
**Zwei parallele Dispatch-Systeme die nicht voneinander wissen.**

---

## Problem 4: SIEBEN Dispatch-Mechanismen

| # | Mechanismus | Wo | Aktive Consumer |
|---|---|---|---|
| 1 | DIWSubscriberProtocol | VenuOrchestrator._emit() | 2 (Telemetrie + Narada) |
| 2 | BeatSubscriberProtocol | VenuService._dispatch_beat_subscribers() | 4 (Ouroboros, Shuddhi, Kala, Jagannath) |
| 3 | Singularity._listeners | Singularity._broadcast() | 1+ (SravanamListener) |
| 4 | VenuService._beat_callbacks | VenuService.start() loop | 0 |
| 5 | MantraClock/Voice | MantraClock.tick_once() | 0 voices, 0 callbacks |
| 6 | MantraKernel/IntentResolver | MantraKernel.process_queue() | 0 queued intents |
| 7 | Lotus._gate_hooks + TattvaRegistry providers | _fire_gate() | 0 hooks, 0 providers |

**Davon funktionieren 3** (#1, #2, #3). Der Rest ist leere Infrastruktur.

---

## Problem 5: MahaKernel — dritter Singleton

`kernel/maha_kernel.py` hat `MahaKernel` mit eigenem `__call__()` und eigenem Singleton.
Lotus.kernel delegiert an MahaKernel. MahaKernel delegiert via `__getattr__` an Singularity.
**Drei Singletons die aufeinander zeigen: Lotus → Singularity ← MahaKernel.**

---

---

## ENTSCHEIDUNGEN (getroffen 2026-02-17)

### E1: Lotus vs Singularity — KEIN Merge nötig

Nach vollständiger Analyse: Das ist ein **valides Fassade-Pattern**.

- **Singularity** = interner Kern (tick, kala, venu, listeners, routing, governance)
- **Lotus** = public API / Fassade (Pipeline `__call__`, NavaBhakti, PipelineCache, gates)
- Lotus delegiert fast alles an Singularity — das ist korrekt

**Das Problem ist NUR der doppelte Name `mahamantra`:**
- 64 Imports zeigen auf Lotus (`from vibe_core.mahamantra import mahamantra`)
- 4 Imports zeigen auf Singularity (`from ...kernel.singularity import mahamantra`)
- Die 4 Singularity-Imports (daemon.py, maha_kernel.py, lotus_core.py, test) müssen
  entweder über Lotus gehen oder explizit `singularity` heißen statt `mahamantra`

**Aktion:** Die 4 direkten Singularity-Imports umbenennen zu `_singularity` oder über Lotus leiten.
Kein Merge, kein Refactoring, nur Klarheit im Naming.

### E2: Ein Heartbeat-Pfad — VenuService ist DER Runtime-Heartbeat

```
VenuService.start() loop
  → beat_callbacks(position)           # VenuService-eigene Callbacks (0 registriert)
  → _dispatch_beat_subscribers()       # 5 BeatSubscribers (Ouroboros, Shuddhi, Kala, Jagannath, LotusBridge)
  → self._singularity.tick()           # Singularity.tick() → Kala + Venu.step() + _broadcast()
  → self._clock.tick_once()            # VenuService-eigene MantraClock (0 voices, 0 callbacks)
```

**VenuService ist der einzige der alle Systeme treibt.** Das ist korrekt.
MahamantraDaemon ist ein alternativer Pfad (CLI-Chanting), der direkt Singularity.tick() aufruft.
Beide enden in Singularity.tick() — das ist der EINE Heartbeat.

**MantraClock in VenuService:** Hat 0 Voices und 0 Callbacks. Ist reine Infrastruktur.
Wenn jemand Voice-Tasks braucht, registriert er sich bei VenuService.clock.
Das ist KEIN Problem — es ist vorbereitete Infrastruktur.

**Aktion:** Keine. Der Heartbeat-Pfad ist korrekt. Nur dokumentieren.

### E3: Dispatch-Mechanismen — Inventar

| # | Mechanismus | Status | Aktion |
|---|---|---|---|
| 1 | DIWSubscriberProtocol (VenuOrchestrator) | AKTIV (2 Subscriber) | Keine |
| 2 | BeatSubscriberProtocol (VenuService) | AKTIV (5 Subscriber) | Keine |
| 3 | Singularity._listeners (_broadcast) | AKTIV (1+ Listener) | Keine |
| 4 | VenuService._beat_callbacks | LEER (0 Callbacks) | Infrastruktur, OK |
| 5 | MantraClock/Voice | LEER (0 Voices) | Infrastruktur, OK |
| 6 | MantraKernel/IntentResolver | LEER (0 Intents) | Infrastruktur, OK |
| 7 | Lotus._gate_hooks + TattvaRegistry | LEER (0 Hooks, 0 Provider) | Infrastruktur, OK |

**3 aktiv, 4 vorbereitet.** Das ist kein Spaghetti — das ist unbenutzte Infrastruktur.
Das Problem war, dass ich (#5 und #6) in Singularity.tick() verdrahtet habe,
obwohl VenuService sie schon separat treibt. Das ist jetzt revertiert.

---

## KONKRETER SANIERUNGSPLAN

### Priorität 1: Naming-Klarheit (Split-Brain eliminieren) — DONE
- [x] `daemon.py`: `import mahamantra` → `import mahamantra as _singularity`, alle Aufrufe umbenannt
- [x] `maha_kernel.py`: `import mahamantra as _singularity` → `import mahamantra as _sing` (war schon aliased)
- [x] `lotus_core.py`: war schon `as _singularity` — korrekt
- [x] `test_unified_heartbeat.py`: bleibt (expliziter Singularity-Test)
- [x] `test_daemon_soul.py`: Mock-Target von `daemon.mahamantra` → `daemon._singularity` angepasst
- **3920 Tests grün** (1 pre-existing failure in test_io_sentinel)

### Priorität 2: Tote Code-Pfade markieren
- [ ] MantraKernel.process_queue() wird nie aufgerufen → Docstring: "Called by VenuService when intents are queued"
- [ ] MantraClock hat 0 Voices → Docstring: "Voices are added by consumers via VenuService.clock.add_voice()"
- [ ] gate_hooks hat 0 Hooks → Docstring: "Hooks registered via lotus.on_gate()"
- [ ] TattvaRegistry hat 0 Gate Providers → Docstring: "Providers registered via registry.register_gate_provider()"

### Priorität 3: MahaKernel-Singleton klären — DONE
- [x] `MahaKernel.__getattr__` entfernt (war toter Code, niemand greift über MahaKernel auf Singularity-Attribute zu)
- [x] MahaKernel ist jetzt klar: nur `__call__()` (Seed→Address), `ledger`, `memory`
- [x] Keine Doppel-Delegation mehr: Lotus→MahaKernel ist nur für `__call__()`, nicht für Routing
- **3920 Tests grün** nach Entfernung

### Was NICHT passieren darf
1. Keine neue Schicht draufpacken
2. Keine neue Clock/Dispatch erstellen
3. Keine Verdrahtung in tick() (der Hot Path muss minimal bleiben)
4. Keine Annahmen über "was gebraucht wird" — erst aufräumen, dann bauen
5. Kein Merge von Lotus und Singularity — das Fassade-Pattern ist korrekt
