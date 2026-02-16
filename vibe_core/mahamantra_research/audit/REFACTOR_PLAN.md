# Mahamantra Refactor Plan (2026-02-16)

## Basisdaten (aus INVENTORY.json)

| Metrik | Wert |
|--------|------|
| Dateien | 495 |
| LOC | 111,958 |
| Avg Health | 96.4/100 |
| Smells | 226 total |
| Research | 139 files / 36,693 LOC (32.8%) |
| Substrate | 94 files / 28,260 LOC (25.2%) |
| Protocol | 71 files / 13,016 LOC (11.6%) |

## Die 3 Strukturprobleme

### 1. research/ ist 33% des Folders (139 files, 37K LOC)
Research-Code lebt neben Production-Code. Das verwirrt jeden Agenten.
Research hat eigene Tests, eigene Audits, eigene Experimente.
**Es gehört nicht in mahamantra/ — es ist ein Consumer, kein Teil des Kerns.**

**Aktion:** `research/` → `vibe_core/mahamantra_research/` (eigenes Package).
Imports bleiben gleich, nur der Pfad ändert sich. Null Breaking Changes.

### 2. 68 Dateien ohne Identity (__mahajana__/__position__)
29 in protocols/, 20 in substrate/, 12 in dharma/.
Dateien ohne Identity sind unsichtbar für Lotus Projection, Gate Routing, und Governance.

**Aktion:** Jede Production-Datei bekommt `__mahajana__` + `__position__`.
Das Inventar-Script prüft das automatisch.

### 3. 109 Dateien mit `Any` Type
Gift im typed Kingdom. `Any` bedeutet "ich weiß nicht was das ist".
29 in protocols/ (!!), 20 in substrate/, 25 in research/.

**Aktion:** `Any` → konkrete Typen. Priorität: protocols/ und substrate/.

---

## Die 5 Code-Smells (nach Priorität)

### SMELL A: 27 ungoverned I/O (Production Code)
Direkte `open()`, `write_text()`, `json.dump()` ohne `bridge.offer()` oder SYNC Gate.

**Top Offender:**
- `substrate/sankirtan.py` (1025 LOC, deprecated + ungoverned I/O)
- `substrate/gate_providers.py` (675 LOC)
- `substrate/maha_state.py`
- `substrate/memory.py`
- `substrate/lineage.py`
- `substrate/samskara.py`
- `kernel/phoenix.py`

**Aktion:** Route durch `bridge.offer()` oder markiere als SYNC-Gate-Consumer.

### SMELL B: 18 deprecated Pfade
Tote Code-Pfade die noch aufgerufen werden.

**Top Offender:**
- `substrate/sankirtan.py` — deprecated + 1025 LOC
- `reactor/shadow.py` — deprecated + 913 LOC
- `substrate/algorithm/maha.py` — deprecated + 700 LOC
- `substrate/guardian_router.py` — ganze Datei deprecated

**Aktion:** Entweder löschen oder in research/ verschieben.

### SMELL C: 3 Singleton-Bypasses (verbleibend)
`__init__.py` Docstring + `inventory_scan.py` (false positive) + 1 real.

**Status:** Fast komplett gefixt. Nur Kosmetik.

### SMELL D: 1 private Gate Call
`architecture_map.py` — Research, nicht Production. OK.

### SMELL E: Top 15 Biggest Files (>650 LOC)
Große Dateien sind schwer zu verstehen und zu warten.

| LOC | File | Problem |
|-----|------|---------|
| 1142 | research/maha_language_engine.py | Research, nicht Production |
| 1127 | substrate/lila_chronology.py | Zu groß für substrate/ |
| 1025 | substrate/sankirtan.py | Deprecated + ungoverned I/O |
| 958 | substrate/lotus_core.py | DAS Herz — muss pristine bleiben |
| 936 | cli/veda_explorer.py | CLI tool, OK |
| 913 | reactor/shadow.py | Deprecated |
| 883 | research/gita_verse_text.py | Data, nicht Code |
| 818 | kernel/singularity.py | DAS Gehirn — muss pristine bleiben |
| 768 | substrate/seed.py | SSOT — darf nicht angefasst werden |
| 700 | substrate/algorithm/maha.py | Deprecated |

---

## Refactor-Reihenfolge (Phasen)

### Phase R1: Research Isolation
- `research/` → `vibe_core/mahamantra_research/`
- 139 files, 37K LOC raus aus dem Kern
- mahamantra/ schrumpft auf 356 files, 75K LOC
- Sofort 33% weniger Noise

### Phase R2: Kill Dead Code
- `substrate/sankirtan.py` → research/ oder löschen (deprecated, 1025 LOC)
- `reactor/shadow.py` → research/ (deprecated, 913 LOC)
- `substrate/algorithm/maha.py` → research/ (deprecated, 700 LOC)
- `substrate/guardian_router.py` → research/ (deprecated shadow pipeline)
- ~3000 LOC weniger in Production

### Phase R3: Identity Compliance
- 68 Dateien ohne `__mahajana__`/`__position__` fixen
- Priorität: protocols/ (29) und substrate/ (20)
- Inventory-Script als CI-Check

### Phase R4: Type Hygiene
- 109x `Any` → konkrete Typen
- Priorität: protocols/ (29) und substrate/ (20)
- Research darf `Any` behalten (Experiment-Code)

### Phase R5: I/O Governance
- 27 ungoverned I/O Stellen durch `bridge.offer()` routen
- Oder als bewusste SYNC-Gate-Consumer markieren

---

## Erfolgsmetriken

| Metrik | Vorher | Ziel |
|--------|--------|------|
| Files in mahamantra/ | 495 | <360 |
| LOC in mahamantra/ | 112K | <80K |
| Smells | 226 | <50 |
| Any usage (prod) | 84 | 0 |
| Ungoverned I/O | 27 | 0 |
| No identity | 68 | 0 |
| Deprecated in prod | 18 | 0 |
| Avg Health | 96.4 | >98 |

---

## Werkzeuge

- `research/audit/inventory_scan.py` — Inventar-Scan (re-run nach jeder Phase)
- `research/audit/INVENTORY.json` — Maschinenlesbares Inventar
- `research/audit/GOVARDHAN_SMELLS.md` — Smell-Dokumentation
- `research/audit/REFACTOR_PLAN.md` — Dieser Plan
