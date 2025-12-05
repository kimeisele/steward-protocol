# DER TOTALE KRIEG - Master Plan zur Fraktalen Konsolidierung

> **Codename:** Operation Phoenix Rising
> **Author:** Opus (Architect) + Gemini (Validator)
> **Date:** 2025-12-05
> **Status:** DRAFT - Awaiting Review

---

## 0. VISION

**Ein System, ein Pattern, unendliche Skalierung.**

Jede Komponente folgt dem gleichen fraktalen Muster:
- `manifest.json` - Identität und Metadaten
- `*_main.py` - Entry Point
- VEDA-4 Lifecycle: SHABDA → ARTHA → PRATYAYA → KARMA

Das Ziel: Von 572 Python-Dateien Chaos zu einem System wo ALLES ein Plugin ist.

---

## 1. IST-ZUSTAND (Das Chaos)

### 1.1 Top-Level Struktur (Wildwuchs)

```
steward-protocol/
├── vibe_core/          # Kernel - TEILWEISE fraktal
├── steward/            # Docs + System Agents - GEMISCHT
├── agent_city/         # Community Agents - EIGENES Pattern
├── provider/           # WILDWUCHS - gehört eliminiert
├── gateway/            # HTTP Entry - OK aber isoliert
├── services/           # WILDWUCHS - nur llm_engine.py
├── knowledge/          # DATEN - nicht fraktal
├── data/               # RUNTIME DATA - nicht strukturiert
├── prompts/            # EINE Datei - envoy.md
├── content/            # Posts - unklar
├── config/             # Unklar
└── ... (50+ weitere)
```

### 1.2 Import-Analyse (Wer braucht wen?)

```
vibe_core (Kernel):     94 interne imports, KERN des Systems
steward:                58 imports von vibe_core (Agents → Kernel)
agent_city:             25 imports von vibe_core (Agents → Kernel)
provider:                2 imports von vibe_core (NUR Gateway/CLI nutzen es!)
gateway:                 1 import von vibe_core (Entry Point)
```

**Erkenntnis:** `provider/` ist eine unnötige Zwischenschicht.

### 1.3 Bekannte Probleme

| Problem | Location | Impact |
|---------|----------|--------|
| Provider Wildwuchs | `provider/` | Spaghetti zwischen Entry und Kernel |
| Doppelte Agent-Locations | `steward/` vs `agent_city/` | Verwirrung, inkonsistente Patterns |
| Knowledge nicht fraktal | `knowledge/` | Nicht skalierbar |
| Circuits verstreut | `vibe_core/playbook/circuits/` | Nicht als Plugins |
| Tools verstreut | Multiple locations | Keine zentrale Registry |
| Circuit vs Playbook Confusion | `circuit_executor.py` vs `playbook/` | 3 verschiedene "Circuit" Konzepte |

---

## 2. SOLL-ZUSTAND (Die Fraktale Ordnung)

### 2.1 Die 7 Universen

```
steward-protocol/
│
├── vibe_core/                    # UNIVERSUM 1: KERNEL
│   ├── kernel_impl.py            # Der Kern (minimal)
│   ├── plugins/                  # Kernel Plugins (VEDA-4)
│   ├── cortex/                   # UNIVERSUM 2: CORTEX (NEU)
│   │   ├── engines/              # Cognitive Engines
│   │   ├── protocols/            # Interfaces
│   │   └── loaders/              # Engine Loader
│   ├── tools/                    # UNIVERSUM 5: TOOLS (refactored)
│   │   ├── registry.py           # Central Tool Registry
│   │   └── plugins/              # Tool Plugins (VEDA-4)
│   └── ...
│
├── agents/                       # UNIVERSUM 4: AGENTS (VEREINIGT)
│   ├── system/                   # Core System Agents (ex steward/)
│   │   ├── envoy/
│   │   ├── herald/
│   │   └── ...
│   ├── city/                     # Community Agents (ex agent_city/)
│   │   ├── ambassador/
│   │   └── ...
│   └── loader.py                 # Agent Loader (VEDA-4)
│
├── knowledge/                    # UNIVERSUM 3: KNOWLEDGE (FRAKTAL)
│   ├── manifest.json             # Knowledge Universe Manifest
│   ├── core/                     # System Knowledge
│   │   ├── concepts/             # Concept Maps (Plugins!)
│   │   ├── intents/              # Intent Rules (Plugins!)
│   │   └── circuits/             # Circuit Definitions (Plugins!)
│   ├── agents/                   # Agent-Specific Knowledge
│   │   ├── envoy/
│   │   └── herald/
│   └── loader.py                 # Knowledge Loader (VEDA-4)
│
├── data/                         # UNIVERSUM 6: DATA (STRUKTURIERT)
│   ├── ledger/                   # Immutable Records
│   ├── registry/                 # Agent Identities
│   ├── cache/                    # Temporary Data
│   └── models/                   # ML Models
│
├── interface/                    # UNIVERSUM 7: INTERFACE (VEREINIGT)
│   ├── gateway/                  # HTTP API (ex gateway/)
│   ├── cli/                      # CLI (ex vibe_core/cli.py)
│   └── websocket/                # Real-time
│
└── [GELÖSCHT: provider/, services/, prompts/, content/]
```

### 2.2 Das Fraktale Pattern (VEDA-4)

Jedes "Ding" im System folgt diesem Pattern:

```
thing/
├── manifest.json         # SHABDA: Deklaration
│   {
│     "type": "plugin|agent|circuit|knowledge|tool",
│     "id": "unique_id",
│     "name": "Human Name",
│     "version": "1.0.0",
│     "entry_point": "thing_main.py",
│     "entry_class": "ThingClass",
│     "dependencies": [],
│     "hooks": [],
│     ...
│   }
├── thing_main.py         # ARTHA: Implementation
└── [sub-things/]         # PRATYAYA: Nested Fractals
```

---

## 3. DIE 9 SCHLACHTEN

### Schlacht 1: CORTEX LIBRARY
**Status:** TODO
**Priority:** P0 (Blocker für Schlacht 7)

**Aktion:**
1. Erstelle `vibe_core/cortex/`
2. Verschiebe:
   - `vibe_core/circuit_executor.py` → `vibe_core/cortex/engines/circuit_executor.py`
   - `provider/semantic_router.py` → `vibe_core/cortex/engines/semantic_router.py`
   - `provider/reflex_engine.py` → `vibe_core/cortex/engines/reflex_engine.py`
3. Erstelle `vibe_core/cortex/protocols/intent.py`
4. Erstelle `vibe_core/cortex/__init__.py` mit exports

**Risiko:** Niedrig - Nur Code-Verschiebung + Import-Updates

---

### Schlacht 2: KNOWLEDGE UNIVERSE
**Status:** TODO
**Priority:** P1

**Aktion:**
1. Erstelle `knowledge/manifest.json`
2. Refactor `knowledge/` zu Plugin-Struktur:
   ```
   knowledge/
   ├── manifest.json
   ├── loader.py              # KnowledgeLoader (VEDA-4)
   ├── core/
   │   ├── concepts/
   │   │   ├── manifest.json
   │   │   ├── general.yaml   # ex concept_map.yaml
   │   │   └── domains/
   │   │       ├── coding.yaml
   │   │       └── philosophy.yaml
   │   ├── intents/
   │   │   ├── manifest.json
   │   │   └── routing_rules.yaml  # ex intent_rules.yaml
   │   └── circuits/
   │       ├── manifest.json
   │       └── [MOVED from vibe_core/playbook/circuits/]
   └── agents/
       ├── envoy/
       │   └── concepts.yaml  # Agent-specific knowledge
       └── herald/
           └── concepts.yaml
   ```
3. Update SemanticRouter um KnowledgeLoader zu nutzen

**Risiko:** Mittel - Viele Pfad-Updates nötig

---

### Schlacht 3: CIRCUIT MIGRATION
**Status:** TODO
**Priority:** P1 (Nach Schlacht 2)

**Aktion:**
1. Verschiebe `vibe_core/playbook/circuits/*.yaml` → `knowledge/core/circuits/`
2. Erstelle `manifest.json` für jeden Circuit
3. Update CircuitExecutor um CircuitLoader (VEDA-4) zu nutzen
4. LÖSCHE `vibe_core/phoenix/utils/circuits.py` (falsche Abstraktion)
5. LÖSCHE `vibe_core/phoenix/utils/routing.py` (gehört zu Knowledge)

**Risiko:** Mittel - CircuitExecutor muss angepasst werden

---

### Schlacht 4: AGENT VEREINIGUNG
**Status:** TODO
**Priority:** P2

**Aktion:**
1. Erstelle `agents/` auf Top-Level
2. Verschiebe:
   - `steward/system_agents/*` → `agents/system/`
   - `agent_city/registry/*` → `agents/city/`
3. Update AgentLoader Pfade
4. Behalte `steward/` NUR für Docs
5. Lösche `agent_city/registry/` (nur leere Wrapper)

**Risiko:** Hoch - Viele Import-Pfade ändern sich

---

### Schlacht 5: TOOL CONSOLIDATION
**Status:** PARTIAL
**Priority:** P2

**Aktion:**
1. Audit: Wo sind alle Tools definiert?
   - `vibe_core/tools/`
   - `steward/system_agents/*/tools/`
   - `agent_city/registry/*/tools/`
2. Entscheide: Zentral vs. Agent-lokal
3. Erstelle Tool Plugin Pattern falls nötig

**Risiko:** Mittel - Tools sind bereits teilweise strukturiert

---

### Schlacht 6: PROVIDER ELIMINATION
**Status:** TODO
**Priority:** P0 (Nach Schlacht 1)

**Aktion:**
1. Update `gateway/api.py`:
   - Statt `UniversalProvider` direkt `kernel.route_to_agent("envoy", input)`
2. Update `vibe_core/cli.py`:
   - Gleiche Änderung
3. Verschiebe Provider-Logik nach `agents/system/envoy/provider.py`
4. LÖSCHE `provider/` komplett

**Risiko:** Mittel - Entry Points müssen getestet werden

---

### Schlacht 7: SERVICES CLEANUP
**Status:** TODO
**Priority:** P3

**Aktion:**
1. `services/llm_engine.py` → prüfen ob noch genutzt
2. Wenn ja: → `vibe_core/llm/engine.py`
3. Wenn nein: → LÖSCHEN
4. LÖSCHE `services/` Ordner

**Risiko:** Niedrig

---

### Schlacht 8: DATA LAYER
**Status:** TODO
**Priority:** P3

**Aktion:**
1. Dokumentiere was in `data/` ist
2. Erstelle klare Struktur:
   ```
   data/
   ├── ledger/       # SQLite DBs (immutable)
   ├── registry/     # Agent manifests (runtime)
   ├── cache/        # Temporary (kann gelöscht werden)
   └── models/       # ML models (large files)
   ```
3. Erstelle `.gitignore` rules
4. Dokumentiere Backup-Strategie

**Risiko:** Niedrig - Nur Organisation

---

### Schlacht 9: INTERFACE LAYER
**Status:** TODO
**Priority:** P4 (Nice to have)

**Aktion:**
1. Erstelle `interface/` wenn sinnvoll
2. Oder behalte `gateway/` + CLI wo sie sind
3. Entscheide basierend auf Bedarf

**Risiko:** Niedrig - Optional

---

## 4. ABHÄNGIGKEITEN

```
Schlacht 1 (Cortex) ─────────────────────────────┐
                                                 │
Schlacht 2 (Knowledge) ──────────────────────────┤
         │                                       │
         └──► Schlacht 3 (Circuits) ─────────────┼──► Schlacht 6 (Provider Kill)
                                                 │
Schlacht 4 (Agents) ─────────────────────────────┤
                                                 │
Schlacht 5 (Tools) ──────────────────────────────┘

Schlacht 7 (Services) ─── unabhängig
Schlacht 8 (Data) ─────── unabhängig
Schlacht 9 (Interface) ── unabhängig (später)
```

**Kritischer Pfad:** 1 → 6 (Provider Kill braucht Cortex)

---

## 5. MIGRATIONS-STRATEGIE

### Phase 1: Foundation (Schlachten 1, 2, 3)
- Cortex Library erstellen
- Knowledge fraktalisieren
- Circuits migrieren
- **KEINE Breaking Changes** - alte Pfade bleiben als Aliases

### Phase 2: Consolidation (Schlachten 4, 5, 6)
- Agents vereinigen
- Tools konsolidieren
- Provider eliminieren
- **Breaking Changes** mit Migrations-Guide

### Phase 3: Cleanup (Schlachten 7, 8, 9)
- Services aufräumen
- Data strukturieren
- Interface optional
- **Polish**

---

## 6. VALIDIERUNG

### 6.1 Tests die GRÜN bleiben müssen

```bash
# Nach JEDER Schlacht:
python -m pytest tests/ -v --tb=short

# Speziell:
python -m pytest tests/test_unified_loader.py      # VEDA-4 Pattern
python -m pytest tests/integration/test_system_boot.py  # Boot
python -m pytest tests/integration/test_veda4_circuits.py  # Circuits
```

### 6.2 Import-Check

```bash
# Nach jeder Schlacht:
python -c "from vibe_core import RealVibeKernel; k = RealVibeKernel(); k.boot()"
python -c "from vibe_core.cortex import CircuitExecutor"  # Nach Schlacht 1
```

### 6.3 Invarianten

- [ ] Kernel bootet ohne Fehler
- [ ] Alle Agents laden
- [ ] Alle Plugins laden
- [ ] Alle Circuits laden
- [ ] CLI funktioniert
- [ ] Gateway funktioniert

---

## 7. RISIKEN UND MITIGATIONEN

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Import-Pfad-Chaos | Hoch | Mittel | Aliases während Migration |
| Test-Failures | Mittel | Hoch | Inkrementelle Änderungen |
| Vergessene Dependencies | Mittel | Mittel | grep -r vor jeder Löschung |
| Circular Imports | Niedrig | Hoch | TYPE_CHECKING Pattern |

---

## 8. OFFENE FRAGEN

1. **Agent Location:** `agents/` auf Top-Level oder in `vibe_core/agents/`?
2. **Knowledge Location:** Bleibt Top-Level oder wird Teil von `vibe_core/`?
3. **Playbook vs Circuit:** Brauchen wir beide Konzepte oder nur Circuits?
4. **Phoenix Config:** Wie passt das Section-System ins Fraktale?
5. **Nano City Spawning:** Wie spawnen Agents dynamisch Sub-Universen?

---

## 9. NÄCHSTE SCHRITTE

1. [ ] Gemini Review dieses Plans
2. [ ] Offene Fragen klären
3. [ ] Schlacht 1 (Cortex) starten
4. [ ] Nach jeder Schlacht: Validierung + Commit

---

## 10. APPENDIX

### A. Glossar

| Term | Definition |
|------|------------|
| VEDA-4 | 4-Phase Loader Pattern: SHABDA → ARTHA → PRATYAYA → KARMA |
| Fraktal | Selbstähnliche Struktur auf allen Ebenen |
| Universe | Ein eigenständiges Plugin-System |
| Cortex | Die "Gehirn" Schicht (Routing, Circuits, Semantik) |
| Kernel | Der minimale Kern (Scheduler, Hooks, Boot) |

### B. Dateien zum Löschen (Nach Migration)

```
provider/                     # Nach Schlacht 6
services/                     # Nach Schlacht 7
vibe_core/phoenix/utils/circuits.py   # Nach Schlacht 3
vibe_core/phoenix/utils/routing.py    # Nach Schlacht 3
```

### C. Referenz-Dokumente

- `docs/architecture/GEMINI_UNIVERSE_MAP.md` - Initiale Aufgabe
- `UNIVERSE_MAP_RESULTS.md` - Gemini's Audit
- `docs/reports/GEMINI_PRO_ANALYSE.md` - Cortex Refinement

---

*Erstellt von Opus. Zur Review durch Gemini.*
*Der Totale Krieg beginnt jetzt.*
