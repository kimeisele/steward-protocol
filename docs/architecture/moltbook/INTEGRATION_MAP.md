# MOLTBOOK INTEGRATION MAP — Was verdrahtet ist

**Status:** Verified against code 2026-02-23
**Purpose:** Ehrliche Bestandsaufnahme der Infrastruktur-Nutzung

---

## 1. Knowledge Graph Integration

**Status: WIRED**

| Was | Quelle | Wo |
|-----|--------|------|
| Platform-Ontologie (14 Nodes) | `knowledge/moltbook/platform.yaml` | `_knowledge_context()` → `compile_context("moltbook")` |
| Constraint-Checking (6 Constraints) | `knowledge/moltbook/platform.yaml` | `MoltbookService._enforce_guna()` → `resolver.get_violations()` |
| Priority-Metriken (DM=9,Post=7,Comment=6,Vote=4) | `knowledge/moltbook/platform.yaml` | `_kg_priority()` → `resolver.graph.get_metric()` |
| Topologie (22 Edges) | `knowledge/moltbook/platform.yaml` | via `compile_prompt_context()` depth=2 traversal |
| Agent-Ontologie (13 Agents) | `knowledge/core/agents.yaml` | via Knowledge Graph bei boot |
| Concept Map (DOM_MOLTBOOK) | `knowledge/concepts/general.yaml` | Geladen in Graph; Intent-Routing für autonome Agents nicht nötig |

**Zahlen:** 92 Nodes, 55 Edges, 23 Constraints in Knowledge Graph geladen.
Knowledge Context liefert **16.159 Zeichen** semantische Daten pro Proposal.

---

## 2. Circuit Executor

**Status: WIRED**

### 2a. Wiring (plugin_main.py)

```python
# on_boot():
self._wire_circuit_executor(kernel)

# _wire_circuit_executor():
from vibe_core.cortex.engines.circuit_engine import create_circuit_executor_with_meta
executor, manager = create_circuit_executor_with_meta(kernel)
# → executor.circuits["MOLTBOOK_CONTENT_V1"] verfügbar
# → MetaCircuitManager (TASK_LEDGER + ERROR_RECOVERY) als Observer
```

### 2b. MOLTBOOK_CONTENT_V1 Circuit

`playbook/circuits/moltbook_content.yaml` — VEDA-4 State Machine:
```
SHABDA → ARTHA → PRATYAYA → KARMA → REVIEW → SUCCESS
  │         │         │         │         │
  Parse     Gates     Context   Record    Human
  Pipeline  Guna/     Dense     Karma     Review
  Analysis  Cell/     Assembly  Ledger    Gate
            Integrity
```

### 2c. execute_content_circuit() API

```python
# Callable from plugin API or other agents:
result = plugin.execute_content_circuit(
    raw_input=text,
    content_type="comment",
    post_id=post_id,
    auto_approve=True,
)
# Returns circuit output dict on success, None on filter/failure
```

### 2d. Was der Circuit Executor mitbringt (gratis)

| Feature | Status |
|---------|--------|
| InvariantChecker (pre/post conditions) | Active |
| MetaCircuitManager TASK_LEDGER | Active (observer) |
| MetaCircuitManager ERROR_RECOVERY | Active (observer) |
| State History Audit Trail | Active |
| Stuck Detection | Active (configurable threshold) |
| Recursion Depth Limit | Active (configurable) |
| SemanticSyscallExecutor | Active (DISPATCH_TASK, RECORD_KARMA) |

---

## 3. LLM-freier Output (Composition Pipeline)

**Status: WIRED (3-Stufen-Kaskade)**

```python
# resonance_proposer.py:_compose() — Absteigende Präferenz:
# 1. LLM Provider (wenn verfügbar → reichster Output)
# 2. MahaComposition.compose() → 5-Scorer ranked English (PRIMÄR LLM-frei)
# 3. render(result) → Kirtan-Rendering (Fallback)
```

### MahaComposition (adapters/composition.py)

5 pluggbare Scorer (CompositionScorerProtocol):

| Scorer | Was er tut |
|--------|-----------|
| PranaScorer | Antaranga standing wave prana an RAMA-Koordinaten |
| RhythmScorer | Syllable vector ↔ Grid Step Alignment |
| SemanticScorer | WordNet Graph-Distanz zum Input |
| ModeScorer | WordNet Mode ↔ Guna-Preferred Mode |
| StateScorer | System State Affinity (MahaState Vektor) |

**Pipeline:** CONTEXT → POOL → RANK → SELECT → ASSEMBLE → English

---

## 4. AGORA Federation Broadcasting

**Status: WIRED**

```python
# on_boot():
self._wire_agora(kernel)  # kernel.get_agent("agora")

# After every POST/COMMENT publish in _drain_content_queue():
self._broadcast_to_agora(content_type, content, metadata)
# → AGORA.publish_message(source="moltbook", message_type="narrative", ...)
```

**Broadcast-Empfänger:** PULSE, LENS, AMBASSADOR (und andere registrierte Listener)

**Degradation:** Kein AGORA = kein Broadcast, Content geht trotzdem raus.

---

## 5. Mahamantra VM Pipeline

**Status: VOLL VERDRAHTET**

```
mahamantra(text)     → Lotus.__call__() → execute_cycle() → 27-Key Dict
generate(text)       → MahaLanguageEngine → EngineResult (22 Felder)
resonate(text)       → ResonanceRanker → RankedWord[]
MahaComposition()    → 5-Scorer Pipeline → Ranked English Output
```

| EngineResult-Feld | Im Context | Im YAML Template |
|-------------------|------------|------------------|
| guardian_name | JA | JA |
| guardian_function | JA | JA |
| output | JA | JA (ANALYSE) |
| resonant_words | JA | JA (RESONANZ) |
| template_words | JA | JA (GRAMMATIK) |
| verse_ref | JA | JA |
| section_name/mode | JA | JA |
| derivation | JA | JA |
| intent_category | JA | JA |
| expanded_names | JA | JA (NAMEN) |
| syllable_count | JA | - |
| antaranga_active/prana | NEIN | NEIN (Telemetrie) |
| synth_walk_words | NEIN | NEIN (Telemetrie) |
| stress_pattern | NEIN | NEIN (Telemetrie) |

---

## 6. Hardening

| Fix | Status | Impact |
|-----|--------|--------|
| Exponential backoff (2^n s) | DONE | Retries bremsen statt zu spammen |
| Split-brain debounce (2s) | DONE | on_pulse + tick können nicht doppelt feuern |
| Configurable intervals | DONE | feed/post/reply/profile via config |
| Operation log trimming | DONE | 5000→2500 Einträge, kein Memory Leak |
| Pure context templates v4.0 | DONE | Zero LLM-Instruktionen in YAML |
| Stale retry state stripping | DONE | Queue restore entfernt _retry_after/_retries |
| KG constraint checking | DONE | 6 Constraints aus platform.yaml geprüft |
| KG priority metrics | DONE | DM=9 > Post=7 > Comment=6 > Vote=4 |
| Knowledge context enrichment | DONE | 16K Zeichen semantische Daten pro Proposal |
| Priority-sorted queue drain | DONE | ContentQueue.drain() sortiert nach priority desc |
| Pipeline/Engine result caching | DONE | Kein doppelter Pipeline-Run pro Heartbeat |
| MahaComposition als primärer LLM-freier Output | DONE | 5-Scorer ranked English statt nur Kirtan |
| Circuit Executor verdrahtet | DONE | MOLTBOOK_CONTENT_V1 + MetaCircuitManager |
| AGORA Broadcast verdrahtet | DONE | Posts/Comments → Federation Awareness |

---

## 7. Intent Routing

**Status: NICHT VERDRAHTET (by design)**

`knowledge/intents/routing_rules.yaml`:
- `CMD_CREATE` → `herald` agent (SLOW path)
- `CMD_BRIEFING` → `envoy` agent (FAST path)

**Einschätzung:** Intent-Routing ist für User-facing Agentenverhalten.
Moltbook ist ein AUTONOMER Heartbeat-Agent. Direct dispatch ist korrekt.
Intent-Routing wird relevant wenn externe Agents Content-Requests an Moltbook schicken.

---

## 8. Starter Packs / Cartridges

**Status: NICHT VERDRAHTET (by design)**

4 Starter Packs existieren: nexus, scope, shield, spark.
Starter Packs sind für neue Agent-Instanziierung.
Für den eingebauten Moltbook-Agent ist das nicht nötig.

---

## 9. Verdrahtungs-Architektur (Gesamtbild)

```
Moltbook Plugin (plugin_main.py)
│
├── on_boot(kernel)
│   ├── MoltbookClient (API Layer)
│   ├── MoltbookService (DI: MoltbookProtocol)
│   ├── ResonanceProposer (Content Intelligence)
│   │   ├── mahamantra(text) → 27-Key Pipeline
│   │   ├── generate(text) → EngineResult (22 Felder)
│   │   ├── MahaComposition.compose() → 5-Scorer English (LLM-frei)
│   │   ├── _knowledge_context() → KG 16K Zeichen
│   │   └── _kg_priority() → Graph-Metriken
│   ├── CognitiveCircuitExecutor + MetaCircuitManager
│   │   ├── MOLTBOOK_CONTENT_V1 State Machine
│   │   ├── SemanticSyscallExecutor (DISPATCH_TASK, RECORD_KARMA)
│   │   ├── InvariantChecker (pre/post conditions)
│   │   └── TASK_LEDGER + ERROR_RECOVERY (observers)
│   ├── AGORA (Federation Broadcast)
│   │   └── publish_message() → PULSE, LENS, AMBASSADOR
│   └── Mahamantra Tick Listener (heartbeat)
│
├── _do_heartbeat()
│   ├── DM Processing
│   ├── Feed Analysis → propose_comment/engage
│   ├── Post Creation → propose_post
│   └── _drain_content_queue()
│       ├── Execute via MoltbookService
│       ├── AGORA Broadcast (post/comment)
│       └── Exponential Backoff on failure
│
└── ContentQueue (priority-sorted, bounded, persistent)
    └── DM=9 > Post=7 > Comment=6 > Vote=4
```

---

## 10. Infrastruktur-Inventar

| Komponente | Datei | Zeilen | Status |
|---|---|---|---|
| Circuit Executor | `cortex/engines/circuit_engine.py` | 1519 | **WIRED** |
| Moltbook Circuit | `playbook/circuits/moltbook_content.yaml` | 294 | **WIRED** |
| Meta Circuit Manager | `cortex/engines/circuit_engine.py` | ~300 | **WIRED** |
| Semantic Syscalls | `semantic_syscalls.py` | ~400 | **WIRED** (via executor) |
| Knowledge Graph | `knowledge/graph.py` | 658 | **WIRED** |
| Knowledge Resolver | `knowledge/resolver.py` | 151 | **WIRED** |
| Moltbook Platform | `knowledge/moltbook/platform.yaml` | 335 | **WIRED** |
| MahaComposition | `mahamantra/adapters/composition.py` | 361 | **WIRED** |
| AGORA Cartridge | `cartridges/agent_city/agora/` | ~300 | **WIRED** |
| HERALD AgencyDirector | `cartridges/system/herald/core/` | ~400 | Available (not called) |
| Blueprint Generator | `cartridges/system/envoy/blueprint_generator.py` | ~800 | Available (via executor) |
| 25 Circuit YAMLs | `playbook/circuits/*.yaml` | ~5000 | Loaded by executor |
