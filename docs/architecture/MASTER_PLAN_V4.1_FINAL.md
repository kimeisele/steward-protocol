# DER TOTALE KRIEG - Master Plan V4.1 (FINAL)

> **Codename:** Operation Unified Field
> **Author:** Opus (Architect) - Final Decision after Gemini Review
> **Date:** 2025-12-05
> **Status:** APPROVED FOR EXECUTION

---

## 0. DIE DREI WAHRHEITEN

Nach 4+ Iterationen und kritischer Prüfung durch Gemini:

| Kategorie | Location | Git? | Beschreibung |
|-----------|----------|------|--------------|
| **CODE** | `vibe_core/` | ✓ JA | Python das AUSGEFÜHRT wird |
| **CONFIG** | `knowledge/` | ✓ JA | YAML/JSON das GELADEN wird (Source!) |
| **RUNTIME** | `data/` | ✗ NEIN | DBs, Cache, Models (generiert) |

**Das ist das fraktale Pattern.** Es gilt auf JEDER Ebene.

---

## 1. ZIEL-ARCHITEKTUR

```
steward-protocol/
│
├── vibe_core/                       # ══════════ CODE ══════════
│   │
│   ├── kernel_impl.py               # The Kernel
│   │
│   ├── loaders/                     # VEDA-4 Loader Framework
│   │   ├── base_loader.py           # UnifiedLoader
│   │   └── schema.py                # Manifest Validation
│   │
│   ├── plugins/                     # Kernel Plugins
│   │   ├── sarga_cycle/
│   │   ├── vedic_governance/
│   │   └── ...
│   │
│   ├── cortex/                      # Cognitive Engines
│   │   ├── engines/
│   │   │   ├── circuit_engine.py    # State Machine Executor
│   │   │   ├── playbook_engine.py   # DAG Executor
│   │   │   ├── semantic_engine.py   # Embedding + Routing
│   │   │   └── reflex_engine.py     # Fast Deterministic
│   │   ├── protocols/
│   │   │   └── cognitive.py
│   │   └── loader.py
│   │
│   ├── cartridges/                  # Agent Plugins
│   │   ├── loader.py                # CartridgeLoader (VEDA-4)
│   │   ├── system/                  # Core Agents (ex steward/)
│   │   │   ├── envoy/
│   │   │   │   ├── manifest.json
│   │   │   │   ├── cartridge_main.py
│   │   │   │   └── prompts/         # Agent-specific prompts
│   │   │   ├── herald/
│   │   │   ├── watchman/
│   │   │   ├── auditor/
│   │   │   └── ... (15 system agents)
│   │   └── agent_city/              # Community Agents (NAME BLEIBT!)
│   │       ├── ambassador/
│   │       ├── analyst/
│   │       └── ... (14 city agents)
│   │
│   ├── tools/                       # Tool System
│   │   ├── tool_registry.py
│   │   └── tool_protocol.py
│   │
│   ├── phoenix/                     # Config System
│   │   └── sections/
│   │
│   └── runtime/                     # Runtime Services
│       ├── io_service.py
│       ├── oracle.py
│       └── llm_engine.py            # ex services/
│
├── knowledge/                       # ══════════ CONFIG ══════════
│   │                                # (IN GIT - Source Code!)
│   ├── manifest.json
│   │
│   ├── concepts/                    # Semantic Maps
│   │   ├── manifest.json
│   │   ├── general.yaml             # ex concept_map.yaml
│   │   └── domains/
│   │       ├── coding.yaml
│   │       └── philosophy.yaml
│   │
│   ├── intents/                     # Routing Rules
│   │   ├── manifest.json
│   │   └── routing_rules.yaml       # ex intent_rules.yaml
│   │
│   └── circuits/                    # Circuit Definitions
│       ├── manifest.json
│       ├── agent_birth.yaml
│       ├── debug_fix.yaml
│       ├── philosophical_debate.yaml
│       └── ... (16 circuits)
│
├── data/                            # ══════════ RUNTIME ══════════
│   │                                # (GITIGNORED!)
│   ├── ledger/                      # Immutable Records
│   │   └── vibe_ledger.db
│   ├── registry/                    # Runtime State
│   ├── cache/                       # Temporary
│   └── models/                      # ML Models
│
├── gateway/                         # HTTP Entry Point
│   └── api.py
│
├── tests/                           # Test Suite
│
├── docs/                            # Documentation
│
├── scripts/                         # Utility Scripts
│
└── [ELIMINATED]
    ├── provider/                    # → vibe_core/cortex/ + envoy
    ├── services/                    # → vibe_core/runtime/
    ├── steward/system_agents/       # → vibe_core/cartridges/system/
    ├── agent_city/registry/         # → vibe_core/cartridges/agent_city/
    ├── prompts/                     # → in cartridges
    ├── content/                     # → DELETE
    ├── diplomatic_bag/              # → DELETE or data/
    ├── intelligence/                # → DELETE or data/
    ├── sandbox/                     # → DELETE
    ├── starter-packs/               # → knowledge/ or DELETE
    ├── migration/                   # → DELETE after migration
    ├── archive/                     # → DELETE
    ├── MagicMock/                   # → DELETE
    ├── workspace/                   # → data/
    └── workspaces/                  # → data/
```

---

## 2. DAS FRAKTALE PATTERN

Das Pattern gilt auf JEDER Ebene:

### System Level:
```
steward-protocol/
├── vibe_core/      # CODE
├── knowledge/      # CONFIG
└── data/           # RUNTIME
```

### Cartridge Level:
```
vibe_core/cartridges/system/envoy/
├── cartridge_main.py   # CODE
├── prompts/            # CONFIG (agent-specific)
└── (runtime in data/)  # RUNTIME
```

### Plugin Level:
```
vibe_core/plugins/sarga_cycle/
├── plugin_main.py      # CODE
├── manifest.json       # CONFIG
└── (state in data/)    # RUNTIME
```

---

## 3. DIE 7 SCHLACHTEN

### Schlacht 1: CORTEX FOUNDATION
**Ziel:** `vibe_core/cortex/` etablieren
**Risiko:** Niedrig
**Dauer:** 1 Tag

```bash
# Aktionen:
mkdir -p vibe_core/cortex/{engines,protocols}

# Verschieben (COPY first, DELETE after tests green):
cp provider/semantic_router.py    vibe_core/cortex/engines/semantic_engine.py
cp provider/reflex_engine.py      vibe_core/cortex/engines/reflex_engine.py
cp vibe_core/circuit_executor.py  vibe_core/cortex/engines/circuit_engine.py
cp vibe_core/playbook/executor.py vibe_core/cortex/engines/playbook_engine.py
```

**Validierung:**
```bash
python -c "from vibe_core.cortex.engines import semantic_engine"
pytest tests/integration/test_veda4_circuits.py -v
```

---

### Schlacht 2: KNOWLEDGE FRAKTALISIERUNG
**Ziel:** `knowledge/` als CONFIG strukturieren
**Risiko:** Mittel
**Dauer:** 1 Tag

```bash
# Aktionen:
mkdir -p knowledge/{concepts/domains,intents,circuits}

# Verschieben:
mv knowledge/concept_map.yaml     knowledge/concepts/general.yaml
mv knowledge/intent_rules.yaml    knowledge/intents/routing_rules.yaml
mv vibe_core/playbook/circuits/*  knowledge/circuits/

# Manifests erstellen für jeden Ordner
```

**Validierung:**
```bash
python -c "from vibe_core.cortex import KnowledgeLoader; KnowledgeLoader.discover()"
```

---

### Schlacht 3: CARTRIDGE CONSOLIDATION
**Ziel:** Alle Agents unter `vibe_core/cartridges/`
**Risiko:** HOCH (viele Import-Änderungen)
**Dauer:** 2-3 Tage

```bash
# Aktionen:
mkdir -p vibe_core/cartridges/{system,agent_city}

# System Agents (15):
mv steward/system_agents/envoy     vibe_core/cartridges/system/
mv steward/system_agents/herald    vibe_core/cartridges/system/
# ... alle anderen

# Agent City (14):
mv agent_city/registry/ambassador  vibe_core/cartridges/agent_city/
mv agent_city/registry/analyst     vibe_core/cartridges/agent_city/
# ... alle anderen

# Import-Refactor Script nötig!
```

**Validierung:**
```bash
python -c "from vibe_core.cartridges.system.envoy import EnvoyCartridge"
pytest tests/integration/test_system_boot.py -v
```

---

### Schlacht 4: PROVIDER ELIMINATION
**Ziel:** `provider/` eliminieren
**Risiko:** Mittel
**Dauer:** 1 Tag

```bash
# Aktionen:
# 1. Provider-Logik nach Envoy:
mv provider/universal_provider.py vibe_core/cartridges/system/envoy/provider.py

# 2. Gateway updaten:
# gateway/api.py: UniversalProvider → kernel.route_to_agent("envoy", ...)

# 3. DELETE:
rm -rf provider/
```

**Validierung:**
```bash
python gateway/api.py &
curl localhost:8000/health
```

---

### Schlacht 5: SERVICES CLEANUP
**Ziel:** `services/` eliminieren
**Risiko:** Niedrig
**Dauer:** 0.5 Tag

```bash
# Aktionen:
mv services/llm_engine.py vibe_core/runtime/llm_engine.py
rm -rf services/
```

---

### Schlacht 6: LEGACY CLEANUP
**Ziel:** Alle Legacy-Ordner entfernen
**Risiko:** Niedrig
**Dauer:** 0.5 Tag

```bash
# Zu löschen:
rm -rf steward/system_agents/  # (nur noch Docs bleiben)
rm -rf agent_city/registry/
rm -rf prompts/
rm -rf content/
rm -rf archive/
rm -rf MagicMock/
rm -rf sandbox/
mv workspace/ data/workspace/
mv workspaces/ data/workspaces/

# steward/ Docs nach docs/ verschieben
mv steward/*.md docs/steward/
```

---

### Schlacht 7: FINAL INTEGRATION
**Ziel:** System komplett verifizieren
**Risiko:** Niedrig
**Dauer:** 1 Tag

```bash
# Full Test Suite:
pytest tests/ -v

# Boot Test:
python boot.py

# Gateway Test:
python -m gateway.api &
curl localhost:8000/api/chat -d '{"message": "hello"}'
```

---

## 4. GITIGNORE UPDATE (KRITISCH!)

Nach Gemini's Review - diese .gitignore ist PFLICHT:

```gitignore
# ══════════ RUNTIME (data/) ══════════
data/*
!data/.gitkeep

# ══════════ ABER NICHT KNOWLEDGE! ══════════
# knowledge/ ist SOURCE, bleibt im Repo

# ══════════ Python ══════════
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/

# ══════════ Temp State ══════════
.playbook_state/
*.db
*.db-wal
*.db-shm
```

---

## 5. MIGRATIONS-STRATEGIE

**Phase A (Schlachten 1-2): Foundation**
- Parallel zum alten Code
- Keine Breaking Changes
- Aliases für alte Import-Pfade

**Phase B (Schlacht 3): The Big Move**
- Import-Refactor Script
- Kurzzeitig instabil
- Sofort alle Tests fixen

**Phase C (Schlachten 4-5): Cleanup**
- Entry Points updaten
- Legacy löschen

**Phase D (Schlachten 6-7): Polish**
- Aufräumen
- Dokumentation
- Final Verification

---

## 6. ERFOLGS-KRITERIEN

Nach Abschluss:

- [ ] Nur 3 Hauptkategorien: `vibe_core/`, `knowledge/`, `data/`
- [ ] `agent_city` lebt weiter als `vibe_core/cartridges/agent_city/`
- [ ] Alle Konzepte erhalten (Semantic Router, Circuits, Playbooks, etc.)
- [ ] Alle Tests grün
- [ ] Kernel bootet in < 2 Sekunden
- [ ] `grep -r "from provider\|from services\|from steward.system_agents\|from agent_city.registry"` = leer

---

## 7. ROLLBACK

Vor JEDER Schlacht:
```bash
git checkout -b battle-X-$(date +%Y%m%d)
git add -A && git commit -m "backup before battle X"
```

---

## 8. ZUSAMMENFASSUNG

**Die 3 Wahrheiten:**
- **CODE** (`vibe_core/`) - Python
- **CONFIG** (`knowledge/`) - YAML/JSON (Source!)
- **RUNTIME** (`data/`) - Generiert (Gitignored)

**Was überlebt (transformiert):**
- Agent City → `vibe_core/cartridges/agent_city/`
- Provider Konzepte → `vibe_core/cortex/` + Envoy
- Knowledge → `knowledge/` (bleibt Top-Level!)
- Alle Circuits, Playbooks, Concepts → erhalten

**Was stirbt (Ordner, nicht Konzepte):**
- `provider/`
- `services/`
- `steward/system_agents/`
- `agent_city/registry/`
- Diverse Legacy-Ordner

---

**APPROVED FOR EXECUTION**

*Der Totale Krieg beginnt mit Schlacht 1: CORTEX FOUNDATION*

---

## APPENDIX: Quick Reference

```
# Nach dem Krieg - Import Examples:

# Cortex Engines
from vibe_core.cortex.engines import CircuitEngine, SemanticEngine

# Cartridges
from vibe_core.cartridges.system.envoy import EnvoyCartridge
from vibe_core.cartridges.agent_city.ambassador import AmbassadorCartridge

# Plugins
from vibe_core.plugins.sarga_cycle import SargaCyclePlugin

# Knowledge (loaded, not imported)
knowledge = KnowledgeLoader.discover("knowledge/")
```
