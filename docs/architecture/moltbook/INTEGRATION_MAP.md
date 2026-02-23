# MOLTBOOK INTEGRATION MAP — Was verdrahtet ist, was fehlt

**Status:** Verified against code 2026-02-23
**Purpose:** Ehrliche Bestandsaufnahme der Infrastruktur-Nutzung

---

## 1. Knowledge Graph Integration

**Status: WIRED (2026-02-23)**

| Was | Quelle | Verdrahtet | Wo |
|-----|--------|------------|------|
| Platform-Ontologie (14 Nodes) | `knowledge/moltbook/platform.yaml` | JA | `_knowledge_context()` → `compile_context("moltbook")` |
| Constraint-Checking (6 Constraints) | `knowledge/moltbook/platform.yaml` | JA | `MoltbookService._enforce_guna()` → `resolver.get_violations()` |
| Priority-Metriken (DM=9,Post=7,Comment=6,Vote=4) | `knowledge/moltbook/platform.yaml` | JA | `_kg_priority()` → `resolver.graph.get_metric()` |
| Topologie (22 Edges) | `knowledge/moltbook/platform.yaml` | JA | via `compile_prompt_context()` depth=2 traversal |
| Agent-Ontologie (13 Agents) | `knowledge/core/agents.yaml` | JA | via Knowledge Graph bei boot |
| Concept Map (DOM_MOLTBOOK) | `knowledge/concepts/general.yaml` | INDIREKT | Geladen in Graph, aber kein Intent-Routing |

**Zahlen:** 92 Nodes, 55 Edges, 23 Constraints in Knowledge Graph geladen.
Knowledge Context liefert **16.159 Zeichen** semantische Daten pro Proposal.

---

## 2. Content Generation Circuits

**Status: SPEZIFIKATION + EXECUTOR EXISTIEREN — NICHT VERDRAHTET**

### 2a. MOLTBOOK_CONTENT_V1 Circuit (YAML-Spezifikation)

`vibe_core/playbook/circuits/moltbook_content.yaml` — 294 Zeilen, VEDA-4 State Machine:
```
SHABDA → ARTHA → PRATYAYA → KARMA → REVIEW → SUCCESS
  │         │         │         │         │
  Parse     Gates     Context   Record    Human
  Pipeline  Guna/     Dense     Karma     Review
  Analysis  Cell/     Assembly  Ledger    Gate
            Integrity
```

**Terminal States:** SUCCESS, FAILURE, VALIDATION_FAILED, GENERATION_FAILED, REVIEW_REJECTED

**Variables:** raw_input, content_type, target_text, post_id, sender, trigger, auto_approve

**Invarianten:** Jeder State hat explizite Pre-/Post-Conditions.
Die aktuelle Pipeline in `resonance_proposer.py` implementiert diese Logik ad-hoc.

### 2b. CognitiveCircuitExecutor (Python-Runtime)

`vibe_core/cortex/engines/circuit_engine.py` — **1519 Zeilen**, produktionsreif:

```python
executor = CognitiveCircuitExecutor(kernel)
result = executor.execute_by_id("MOLTBOOK_CONTENT_V1", {
    "raw_input": text,
    "content_type": "comment",
    "target_text": post_content,
    "post_id": post_id,
    "auto_approve": True,
})
```

**Features:** InvariantChecker, MetaCircuitManager (TASK_LEDGER + ERROR_RECOVERY),
State-History-Audit-Trail, Stuck-Detection, Recovery-Strategies.

### 2c. Generischer Content Circuit

`knowledge/genesis/circuits/content_generation.yaml` — Generische Version für
Blog/Doc/Announcement-Generierung. Routet über `herald` Agent.

### 2d. Gap-Analyse

| Feature | Ad-hoc Pipeline | Circuit Executor |
|---------|-----------------|------------------|
| State Machine | Implizit (if/else) | Explizit (YAML) |
| Invarianten | Nicht geprüft | Pre/Post-Conditions |
| Audit Trail | Activity Log (JSONL) | State History |
| Error Recovery | try/except + retry | MetaCircuit ERROR_RECOVERY |
| Stuck Detection | Nicht vorhanden | MetaCircuit TASK_LEDGER |
| Human Review | Nicht vorhanden | REVIEW State |

**Einschätzung:** Der Circuit-Executor KANN die Moltbook-Pipeline ersetzen.
Benötigt: Kernel-Instanz + Syscall-Handler für DISPATCH_TASK/RECORD_KARMA.
Das ist die sauberste Architektur — aber ein größerer Umbau (Phase 2).

**Sofort nutzbar:** Die Circuit-YAML als Spezifikation/Dokumentation.
Die ad-hoc Pipeline implementiert die gleiche Logik, nur weniger formal.

---

## 3. Intent Routing

**Status: NICHT VERDRAHTET**

`knowledge/intents/routing_rules.yaml`:
- `CMD_CREATE` → `herald` agent (SLOW path)
- `CMD_BRIEFING` → `envoy` agent (FAST path)

`knowledge/concepts/general.yaml`:
- `DOM_MOLTBOOK`: [moltbook, submolt, dm, karma, feed, upvote, downvote, comment, follower, following]
- `CMD_CREATE`: [create, make, build, draft, write, generate, compose, publish]

**Gap:** Der Moltbook-Plugin routet NICHT über das Intent-System.
Posts werden direkt erstellt, nicht über HERALD dispatched.

**Einschätzung:** Intent-Routing ist für User-facing Agentenverhalten gedacht.
Der Moltbook-Plugin ist ein AUTONOMER Heartbeat-Agent. Direct dispatch ist korrekt.
Intent-Routing wäre relevant wenn externe Agents Content-Requests an Moltbook schicken.

---

## 4. Render Pipeline (LLM-freier Output)

**Status: VERDRAHTET (als Fallback)**

```python
# resonance_proposer.py:_compose()
if pipeline_result:
    from vibe_core.mahamantra.render import render
    return render(pipeline_result)
```

`render(result)` erzeugt deterministischen Output aus dem 27-Key Dict.
Wird NUR als Fallback genutzt wenn kein LLM Provider verfügbar ist.

**Was render() liefert:** Kirtan-artiger Output basierend auf resonant_words + template_words.
**Qualität:** Abhängig von der Section-Router-Konfiguration und der Eingabe.

---

## 5. Mahamantra VM Pipeline

**Status: VOLL VERDRAHTET**

```
mahamantra(text)     → Lotus.__call__() → execute_cycle() → 27-Key Dict
generate(text)       → MahaLanguageEngine → EngineResult (22 Felder)
resonate(text)       → ResonanceRanker → RankedWord[]
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
| antaranga_active/prana | NEIN | NEIN |
| synth_walk_words | NEIN | NEIN |
| diw_applied | NEIN | NEIN |
| phoneme_trajectory | NEIN | NEIN |
| stress_pattern | NEIN | NEIN |
| sequencer_steps | NEIN | NEIN |

**Unused fields:** 7 EngineResult-Felder werden nicht genutzt.
Die meisten sind Debugging/Telemetrie-Felder (diw_applied, sequencer_steps).
`synth_walk_words` und `stress_pattern` könnten den Output bereichern.

---

## 6. Starter Packs / Cartridges

**Status: NICHT VERDRAHTET**

4 Starter Packs existieren: nexus, scope, shield, spark.
Jedes definiert eine Agent-Persönlichkeit mit Tools und Cartridge.

**Gap:** Kein Moltbook-spezifisches Starter Pack.
**Einschätzung:** Starter Packs sind für neue Agent-Instanziierung.
Für den eingebauten Moltbook-Agent ist das Overkill.

---

## 7. Federation / Agent City

**Status: INFRASTRUKTUR VORHANDEN, NICHT FÜR MOLTBOOK GENUTZT**

Die Codebase hat:
- Agent-Topologie (`knowledge/core/agents.yaml`) — Bhu-Mandala mit 13 Agents
- AGORA als API-Gateway
- HERALD für Content-Broadcasting
- PULSE für Social Amplification

**Gap:** Der Moltbook-Agent ist ein Monolith.
Er routet nicht über HERALD/PULSE/AGORA.

**Einschätzung:** Die Agent-Topologie ist für Multi-Agent-Orchestrierung gedacht.
Im aktuellen Setup (ein einzelner Moltbook-Agent) ist direkter API-Call richtig.
Federation wird relevant wenn multiple Agents auf Moltbook zusammenarbeiten.

---

## 8. Hardening (2026-02-23)

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

---

## 9. Was NICHT getan wurde (und warum)

| Was | Warum nicht |
|-----|-------------|
| Circuit-Executor verdrahten | Executor EXISTIERT (1519 Zeilen), Circuit EXISTIERT (294 Zeilen). Benötigt Kernel+Syscall-Handler. Phase 2. |
| Intent-Routing einbinden | Moltbook ist autonom, nicht user-facing |
| HERALD-Agent delegation | Kein Multi-Agent-Setup, direkter API-Call ist richtig |
| Alle EngineResult-Felder nutzen | stress_pattern/sequencer_steps sind Telemetrie, kein Content |
| Starter Pack für Moltbook | Overkill für eingebauten Agent |

---

## 10. Nächste Schritte

### Phase 2: Circuit-Executor Verdrahtung (nächster großer Schritt)

```python
# Was gebaut werden müsste:
# 1. Kernel-Instanz im Plugin-Kontext bereitstellen
# 2. Moltbook-spezifische Syscall-Handler registrieren:
#    - DISPATCH_TASK("moltbook", "analyze") → mahamantra(text)
#    - DISPATCH_TASK("moltbook", "compose") → _compose(...)
#    - RECORD_KARMA → _log_activity()
# 3. Pipeline durch executor.execute_by_id("MOLTBOOK_CONTENT_V1", ...) ersetzen
```

**Gewinn:** Invarianten, Audit Trail, Stuck Detection, Error Recovery — alles gratis.
**Aufwand:** Kernel-Integration + Syscall-Handler-Registry.

### Phase 3: Multi-Agent (Federation)

1. **HERALD-Delegation** — Content-Requests über HERALD dispatchen
2. **PULSE-Integration** — Social Amplification via PULSE Agent
3. **Federation Protocol** — Moltbook-Agent als Node in Agent City
4. **Moltbook Cartridge** — Starter Pack für Agenten-Instanziierung

### Infrastruktur-Inventar (verifiziert)

| Komponente | Datei | Zeilen | Status |
|---|---|---|---|
| Circuit Executor | `cortex/engines/circuit_engine.py` | 1519 | Produktionsreif |
| Moltbook Circuit | `playbook/circuits/moltbook_content.yaml` | 294 | Spezifikation |
| Knowledge Graph | `knowledge/graph.py` | 658 | WIRED |
| Knowledge Resolver | `knowledge/resolver.py` | 151 | WIRED |
| Moltbook Platform | `knowledge/moltbook/platform.yaml` | 335 | WIRED |
| Blueprint Generator | `cartridges/system/envoy/blueprint_generator.py` | ~800 | Nicht verdrahtet |
| Semantic Syscalls | `semantic_syscalls.py` | ~400 | Nicht verdrahtet |
| Playbook Executor | `plugins/test_orchestration/playbook_executor.py` | ~500 | Nicht verdrahtet |
| 25 Circuit YAMLs | `playbook/circuits/*.yaml` | ~5000 | Spezifikationen |
