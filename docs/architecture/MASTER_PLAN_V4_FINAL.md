# DER TOTALE KRIEG - Master Plan V4 (FINAL)

> **Codename:** Operation Unified Field
> **Author:** Opus (Architect) - Final Decision
> **Date:** 2025-12-05
> **Status:** APPROVED FOR EXECUTION
> **Philosophy:** CODE vs DATA. Nothing else.

---

## 0. THE TWO TRUTHS

Nach 4 Iterationen (V1-V3) ist die Wahrheit kristallklar:

**Es gibt nur ZWEI Konzepte:**

| Konzept | Location | Inhalt |
|---------|----------|--------|
| **CODE** | `vibe_core/` | Alles was AUSGEFÜHRT wird |
| **DATA** | `data/` | Alles was GELADEN wird |

Alles andere ist entweder Entry Point (`boot.py`, `gateway/`) oder Legacy-Müll.

---

## 1. ZIEL-ARCHITEKTUR

```
steward-protocol/
│
├── boot.py                          # Single Entry Point
│
├── vibe_core/                       # ══════ CODE ══════
│   │
│   ├── kernel_impl.py               # The Kernel (Scheduler, Hooks)
│   │
│   ├── loaders/                     # VEDA-4 Loader Framework
│   │   ├── base_loader.py           # UnifiedLoader (bereits fertig!)
│   │   └── schema.py                # Manifest Validation
│   │
│   ├── plugins/                     # Kernel Plugins
│   │   ├── sarga_cycle/             # Task Gating
│   │   ├── vedic_governance/        # Permissions
│   │   ├── interface/               # MD Sync
│   │   └── ...
│   │
│   ├── cortex/                      # Cognitive Engines (NEU)
│   │   ├── __init__.py
│   │   ├── engines/
│   │   │   ├── circuit_engine.py    # State Machine Executor
│   │   │   ├── playbook_engine.py   # DAG Executor
│   │   │   ├── semantic_engine.py   # Embedding + Routing
│   │   │   └── reflex_engine.py     # Fast Deterministic
│   │   ├── protocols/
│   │   │   └── cognitive.py         # Intent, CognitiveProcess
│   │   └── loader.py                # CortexLoader (VEDA-4)
│   │
│   ├── cartridges/                  # Agent Plugins (VEREINIGT)
│   │   ├── __init__.py
│   │   ├── loader.py                # CartridgeLoader (VEDA-4)
│   │   ├── system/                  # Core Agents (ex steward/)
│   │   │   ├── envoy/
│   │   │   │   ├── manifest.json
│   │   │   │   └── cartridge_main.py
│   │   │   ├── herald/
│   │   │   ├── watchman/
│   │   │   ├── auditor/
│   │   │   ├── scribe/
│   │   │   └── ...
│   │   └── community/               # Optional Agents (ex agent_city/)
│   │       ├── ambassador/
│   │       ├── analyst/
│   │       ├── artisan/
│   │       └── ...
│   │
│   ├── tools/                       # Tool System
│   │   ├── tool_registry.py
│   │   ├── tool_protocol.py
│   │   └── core/                    # Built-in Tools
│   │
│   ├── phoenix/                     # Config System (bereits fertig!)
│   │   ├── config.py
│   │   └── sections/
│   │
│   └── runtime/                     # Runtime Services
│       ├── io_service.py
│       ├── oracle.py
│       └── playbook_router.py
│
├── data/                            # ══════ DATA ══════
│   │
│   ├── knowledge/                   # Semantic Data (ex knowledge/)
│   │   ├── manifest.json            # Knowledge Universe Manifest
│   │   ├── concepts/
│   │   │   ├── manifest.json
│   │   │   ├── general.yaml         # ex concept_map.yaml
│   │   │   └── domains/
│   │   │       ├── coding.yaml
│   │   │       └── philosophy.yaml
│   │   ├── intents/
│   │   │   ├── manifest.json
│   │   │   └── routing_rules.yaml   # ex intent_rules.yaml
│   │   └── circuits/
│   │       ├── manifest.json
│   │       ├── agent_birth.yaml
│   │       ├── debug_fix.yaml
│   │       └── ...                  # ex vibe_core/playbook/circuits/
│   │
│   ├── ledger/                      # Immutable Records
│   │   └── vibe_ledger.db
│   │
│   ├── registry/                    # Runtime State
│   │   ├── agents/
│   │   └── sessions/
│   │
│   ├── models/                      # ML Models
│   │   └── sentence-transformers/
│   │
│   └── cache/                       # Temporary (gitignored)
│
├── gateway/                         # HTTP Entry Point (bleibt)
│   ├── api.py
│   └── static/
│
├── tests/                           # Test Suite (bleibt)
│
├── docs/                            # Documentation (bleibt)
│
└── [GELÖSCHT]
    ├── provider/                    # → vibe_core/cortex/ + envoy
    ├── services/                    # → vibe_core/runtime/
    ├── steward/system_agents/       # → vibe_core/cartridges/system/
    ├── agent_city/registry/         # → vibe_core/cartridges/community/
    ├── knowledge/                   # → data/knowledge/
    ├── prompts/                     # → in jeweilige Cartridge
    └── content/                     # → data/ oder löschen
```

---

## 2. DIE 4 PRINZIPIEN

### Prinzip 1: CODE vs DATA Trennung
- `vibe_core/` = Python Code, wird importiert
- `data/` = YAML/JSON/DB, wird geladen
- **Keine .py Dateien in data/**
- **Keine .yaml Configs in vibe_core/** (außer test fixtures)

### Prinzip 2: EIN Loader-Pattern für ALLES
Jedes "Ding" das geladen wird nutzt VEDA-4:
```
thing/
├── manifest.json    # Identität
└── thing_main.py    # (oder .yaml für Data)
```

| Was | Loader | Location |
|-----|--------|----------|
| Kernel Plugins | PluginLoader | `vibe_core/plugins/` |
| Cartridges | CartridgeLoader | `vibe_core/cartridges/` |
| Cortex Engines | CortexLoader | `vibe_core/cortex/engines/` |
| Knowledge | KnowledgeLoader | `data/knowledge/` |
| Circuits | CircuitLoader | `data/knowledge/circuits/` |

### Prinzip 3: Cartridges = Agents
- Kein Unterschied zwischen "System Agent" und "City Agent" im Code
- Unterschied nur in LOCATION und PERMISSIONS (manifest.json)
- `system/` = mit Kernel ausgeliefert, höhere Privilegien
- `community/` = installierbar, sandboxed

### Prinzip 4: Graceful Degradation
- System funktioniert OHNE community cartridges
- System funktioniert OHNE ML models (fallback to rules)
- System funktioniert OHNE gateway (CLI only)

---

## 3. DIE 7 SCHLACHTEN

### Schlacht 1: CORTEX FOUNDATION
**Ziel:** Cognitive Engines in `vibe_core/cortex/` etablieren
**Abhängigkeiten:** Keine
**Risiko:** Niedrig

**Aktionen:**
1. Erstelle `vibe_core/cortex/` Struktur
2. Verschiebe und refactore:
   ```
   provider/semantic_router.py    → vibe_core/cortex/engines/semantic_engine.py
   provider/reflex_engine.py      → vibe_core/cortex/engines/reflex_engine.py
   vibe_core/circuit_executor.py  → vibe_core/cortex/engines/circuit_engine.py
   vibe_core/playbook/executor.py → vibe_core/cortex/engines/playbook_engine.py
   ```
3. Erstelle `vibe_core/cortex/protocols/cognitive.py`
4. Erstelle `vibe_core/cortex/__init__.py` mit exports
5. Update imports in allen Consumern

**Validierung:**
```bash
python -c "from vibe_core.cortex.engines import CircuitEngine, SemanticEngine"
pytest tests/integration/test_veda4_circuits.py
```

---

### Schlacht 2: KNOWLEDGE MIGRATION
**Ziel:** Knowledge-Dateien nach `data/knowledge/` verschieben
**Abhängigkeiten:** Schlacht 1 (Cortex muss Knowledge laden können)
**Risiko:** Mittel

**Aktionen:**
1. Erstelle `data/knowledge/` Struktur
2. Verschiebe:
   ```
   knowledge/concept_map.yaml     → data/knowledge/concepts/general.yaml
   knowledge/intent_rules.yaml    → data/knowledge/intents/routing_rules.yaml
   vibe_core/playbook/circuits/*  → data/knowledge/circuits/
   ```
3. Erstelle manifest.json für jeden Ordner
4. Erstelle `vibe_core/cortex/knowledge_loader.py` (VEDA-4)
5. Update SemanticEngine um KnowledgeLoader zu nutzen
6. LÖSCHE altes `knowledge/` auf Top-Level

**Validierung:**
```bash
python -c "from vibe_core.cortex import KnowledgeLoader; k = KnowledgeLoader.discover()"
pytest tests/test_playbook_system.py
```

---

### Schlacht 3: CARTRIDGE CONSOLIDATION
**Ziel:** Alle Agents unter `vibe_core/cartridges/` vereinigen
**Abhängigkeiten:** Keine (kann parallel zu 1+2)
**Risiko:** HOCH (viele Import-Änderungen)

**Aktionen:**
1. Erstelle `vibe_core/cartridges/{system,community}/`
2. Verschiebe System Agents:
   ```
   steward/system_agents/envoy/    → vibe_core/cartridges/system/envoy/
   steward/system_agents/herald/   → vibe_core/cartridges/system/herald/
   steward/system_agents/watchman/ → vibe_core/cartridges/system/watchman/
   ... (alle 15 system agents)
   ```
3. Verschiebe Community Agents:
   ```
   agent_city/registry/ambassador/ → vibe_core/cartridges/community/ambassador/
   agent_city/registry/analyst/    → vibe_core/cartridges/community/analyst/
   ... (alle 14 city agents)
   ```
4. Update `CartridgeLoader` Pfade
5. Update ALLE imports (`from vibe_core.cartridges.system...` → `from vibe_core.cartridges.system...`)
6. LÖSCHE `steward/system_agents/` und `agent_city/registry/`

**Validierung:**
```bash
python -c "from vibe_core.cartridges.system.envoy import EnvoyCartridge"
pytest tests/integration/test_system_boot.py
```

---

### Schlacht 4: PROVIDER ELIMINATION
**Ziel:** `provider/` Ordner eliminieren
**Abhängigkeiten:** Schlacht 1 (Cortex), Schlacht 3 (Envoy in Cartridges)
**Risiko:** Mittel

**Aktionen:**
1. Verschiebe Provider-Logik nach Envoy:
   ```
   provider/universal_provider.py → vibe_core/cartridges/system/envoy/provider.py
   ```
2. Update `gateway/api.py`:
   - Statt `UniversalProvider` nutze `kernel.route_to_agent("envoy", input)`
3. Update `vibe_core/cli.py` analog
4. LÖSCHE `provider/`

**Validierung:**
```bash
python gateway/api.py &  # Start gateway
curl localhost:8000/health
pytest tests/test_phase3_integration.py
```

---

### Schlacht 5: SERVICES CLEANUP
**Ziel:** `services/` eliminieren
**Abhängigkeiten:** Schlacht 1 (falls llm_engine nach Cortex)
**Risiko:** Niedrig

**Aktionen:**
1. Prüfe ob `services/llm_engine.py` noch genutzt wird
2. Wenn ja: Verschiebe nach `vibe_core/runtime/llm_engine.py`
3. Wenn nein: LÖSCHE
4. LÖSCHE `services/`

**Validierung:**
```bash
grep -r "from services" --include="*.py" .  # Sollte leer sein
```

---

### Schlacht 6: LEGACY CLEANUP
**Ziel:** Alle Legacy-Ordner entfernen
**Abhängigkeiten:** Schlachten 1-5 abgeschlossen
**Risiko:** Niedrig

**Aktionen:**
1. LÖSCHE leere Ordner:
   - `steward/` (nur noch Docs → nach `docs/`)
   - `agent_city/` (komplett)
   - `prompts/` (nach jeweilige Cartridge)
   - `content/` (nach `data/` oder löschen)
2. Update `.gitignore`
3. Update `pyproject.toml` / `setup.py` falls vorhanden

**Validierung:**
```bash
ls -la  # Nur erlaubte Top-Level Ordner
```

---

### Schlacht 7: FINAL INTEGRATION
**Ziel:** System komplett verifizieren
**Abhängigkeiten:** Alle vorherigen
**Risiko:** Niedrig

**Aktionen:**
1. Full Boot Test:
   ```bash
   python boot.py
   ```
2. Full Test Suite:
   ```bash
   pytest tests/ -v
   ```
3. Gateway Test:
   ```bash
   python -m gateway.api &
   curl localhost:8000/api/chat -d '{"message": "hello"}'
   ```
4. Update Dokumentation:
   - `README.md`
   - `ARCHITECTURE.md`
   - `docs/architecture/ARCHITECTURE_MAP.md`

---

## 4. MIGRATIONS-REIHENFOLGE

```
Woche 1: Foundation
├── Schlacht 1: Cortex Foundation
└── Schlacht 2: Knowledge Migration

Woche 2: Consolidation
├── Schlacht 3: Cartridge Consolidation (BIGGEST)
└── Schlacht 4: Provider Elimination

Woche 3: Cleanup
├── Schlacht 5: Services Cleanup
├── Schlacht 6: Legacy Cleanup
└── Schlacht 7: Final Integration
```

**Kritischer Pfad:** 1 → 4 (Provider braucht Cortex + Envoy)

---

## 5. ROLLBACK STRATEGIE

Vor JEDER Schlacht:
```bash
git checkout -b battle-X-backup
git add -A && git commit -m "backup before battle X"
```

Bei Problemen:
```bash
git checkout main
git branch -D battle-X-broken
```

---

## 6. ERFOLGS-KRITERIEN

Nach Abschluss aller Schlachten:

- [ ] `vibe_core/` ist das EINZIGE Python Package
- [ ] `data/` enthält NUR Daten (keine .py)
- [ ] Keine Top-Level Ordner außer: `vibe_core/`, `data/`, `gateway/`, `tests/`, `docs/`
- [ ] Alle 572 Python-Dateien sind in `vibe_core/` oder `tests/`
- [ ] Kernel bootet in < 2 Sekunden
- [ ] Alle Tests grün
- [ ] `grep -r "from provider\|from services\|from steward\|from agent_city"` = leer

---

## 7. APPENDIX: WAS WIRD GELÖSCHT

| Ordner | Schicksal | Schlacht |
|--------|-----------|----------|
| `provider/` | → `vibe_core/cortex/` + `envoy/` | 1, 4 |
| `services/` | → `vibe_core/runtime/` oder DELETE | 5 |
| `steward/system_agents/` | → `vibe_core/cartridges/system/` | 3 |
| `steward/` (rest) | → `docs/` | 6 |
| `agent_city/registry/` | → `vibe_core/cartridges/community/` | 3 |
| `agent_city/` (rest) | DELETE | 6 |
| `knowledge/` | → `data/knowledge/` | 2 |
| `prompts/` | → in Cartridges | 6 |
| `content/` | → `data/` oder DELETE | 6 |

---

## 8. SIGNATUR

**Dieses Dokument repräsentiert die FINALE Architektur-Entscheidung.**

Nach Review durch:
- Opus (V1 Concept)
- Gemini (V2/V3 Refinement)
- Opus (V4 Final Decision)

**Approved for Execution.**

---

*Der Totale Krieg beginnt mit Schlacht 1: CORTEX FOUNDATION*
