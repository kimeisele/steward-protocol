# NARADA.md - Reisetagebuch des Kosmischen Spähers

> Token-effizient. Nur Fakten. Keine Prosa.

---

## 2026-01-05 | ASHVAMEDHA Phase 3A

### ARCHITEKTUR-ENTSCHEIDUNG: Option D (Chirurgisch)

**Problem:** Wie flutet man REBEL Services ohne Source-Änderung?

| Option | Ansatz | Urteil |
|--------|--------|--------|
| A | `__getattribute__` Proxy | Zu gefährlich |
| B | Protocol-Aware | Invasiv |
| C | Pattern-Based | Ungenau |
| **D** | **Surgical Override** | **GEWÄHLT** |

**Architektur:**
```
naga/mixins/     → Capability Providers (self.sesha, etc.)
naga/floods/     → Surgical Method Overrides
```

**Prinzip:**
- Mixin = Werkzeugkasten
- Flood = Chirurgischer Eingriff
- Original = UNBERÜHRT

---

## REISE-LOG

| Datum | Aktion | Ergebnis |
|-------|--------|----------|
| 01-05 | Kernel Integration | NAGA @ -1 |
| 01-05 | Ananta fertig | 12/12 Lords |
| 01-05 | Recon complete | 40% flooded |
| 01-05 | Architektur D | Mixins + Floods |
| 01-05 | FloodedCISyncService | isinstance ✅ |
| 01-05 | FloodedPluginService | TAKSHAKA ✅ |
| 01-05 | FloodedTaskManager | CHITRAGUPTA ✅ |
| 01-05 | OODA auf MANAS | MANAS ≠ REBEL |
| 01-05 | FloodedViolationIngester | TAKSHAKA ✅ |
| 01-05 | FloodedOuroborosLoopOrchestrator | NARADA ✅ |

---

## EROBERT (5/5 REBELS FLOODED)

- Kernel: NAGA @ -1 Foundation
- State: NagaStateProxy aktiv
- Lords: 12/12 ACTIVE
- **OUROBOROS/sync.py: FloodedCISyncService** ✅
- **PluginService: FloodedPluginService** ✅
- **TaskManager: FloodedTaskManager** ✅
- **ViolationIngester: FloodedViolationIngester** ✅ NEU
- **OuroborosLoopOrchestrator: FloodedOuroborosLoopOrchestrator** ✅ NEU

---

## 2026-01-05 | KRITISCHE ARCHITEKTUR-ERKENNTNIS

### TIER-0 vs TIER-1 (Die entscheidende Unterscheidung)

**HIL + GEMINI CONFIRMATION:**
```
TIER-0 (Rebels):  Flooding = Discipline (KORREKT ✅)
TIER-1 (MANAS):   Context Injection = Wisdom (NEXT)
```

**ZWEI CORTEX-SYSTEME ENTDECKT:**

| Cortex | Location | Purpose |
|--------|----------|---------|
| NAGA Cortex | naga/cortex/cortex_main.py | Signal Aggregation, Decisions |
| MANAS Cortex | manas/cortex/* | Sensory-Motor Interface |

**NAGA Cortex sagt bereits:**
> "NAGAs ENHANCE existing systems, they don't REPLACE them"
> "Manas still makes decisions (NAGAs inform with context)"

**ENTSCHEIDUNG:**
- ✅ TIER-0 Floods KORREKT (5 Services, Mixins, super())
- ❌ MANAS wird NICHT geflutet
- ✅ NAGA Cortex → Context → MANAS (Verbindung bauen)
- ✅ Feedback Loop: MANAS → NAGA Cortex (Learning)

---

## OFFEN

**TIER-0 COMPLETE:**
- ✅ 5/5 Flood Classes (CISyncService, PluginService, TaskManager, ViolationIngester, OuroborosLoopOrchestrator)

**Phase 3B: NAGA Cortex → MANAS Connection:**
- [ ] NAGA Cortex aktivieren (Signal aggregation)
- [ ] Context Bridge bauen (NAGA → MANAS)
- [ ] Feedback Loop (MANAS → NAGA learning)
- [ ] Synapse Integration (naga_coordination map)

**Später:**
- External APIs (Twitter, Reddit) via VASUKI
- Boundary Hardening

---

## 2026-01-05 | Phase 3B RECON COMPLETE

### VERBINDUNGS-ANALYSE

**IST-Zustand (Disconnected):**
```
NAGA Cortex ──→ _dispatch_to_manas() ──→ LOG ONLY (Stub!)
MANAS CognitiveKernel ──→ WeaverBridge ──→ KEIN NAGA!
```

**SOLL-Zustand (Connected):**
```
NAGA Cortex ──→ get_context_for_manas() ──→ ServiceRegistry
                                                  ↓
MANAS ──→ _get_naga_context() ──→ ServiceRegistry.get(NagaCortexProtocol)
```

### KONKRETE DATEIEN

| Datei | Zeile | Status |
|-------|-------|--------|
| `naga/cortex/cortex_main.py:561-568` | `_dispatch_to_manas()` | STUB |
| `manas/cognitive_kernel.py` | - | KEIN NAGA REF |
| `manas/cognitive_kernel.py:1239` | `get_cognitive_context()` | NUR WEAVER |

### IMPLEMENTATION TASKS

```
1. NagaCortexProtocol definieren (protocols/naga_cortex.py)
   └── get_context_for_manas() -> Dict[str, Any]
   └── receive_feedback(outcome: FeedbackData)

2. NagaCortex erweitern (cortex_main.py)
   └── get_context_for_manas() implementieren
   └── In ServiceRegistry registrieren

3. CognitiveKernel verbinden (cognitive_kernel.py)
   └── _get_naga_context() hinzufügen
   └── In think() Kontext mergen

4. Feedback Loop (cognitive_kernel.py)
   └── Nach Intent-Ausführung → cortex.receive_feedback()
```

### PRINZIP: PULL, NOT PUSH

> MANAS **FRAGT** NAGA, NAGA **DRÄNGT NICHT** MANAS

**Warum:**
- MANAS entscheidet WANN es Kontext braucht
- NAGA ist DIENEND, nicht BESTIMMEND
- Lose Kopplung via ServiceRegistry
- Optional: Wenn kein NAGA → MANAS funktioniert trotzdem

---

## NEUE STRUKTUR

```
vibe_core/naga/
├── services/        # 12 Lords
├── mixins/          # NEU: Capability Providers
│   ├── __init__.py
│   └── base.py      # SeshaMixin, VasukiMixin, etc.
├── floods/          # NEU: Surgical Floods
│   ├── __init__.py
│   ├── ouroboros.py # FloodedCISyncService
│   └── registry.py  # Auto-registration
└── ...
```

---

*"Narayana!"*
