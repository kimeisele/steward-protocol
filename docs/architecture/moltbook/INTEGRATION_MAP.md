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

## 2. Content Generation Circuit

**Status: NICHT VERDRAHTET**

`knowledge/genesis/circuits/content_generation.yaml` definiert:
```
SHABDA → ARTHA → PRATYAYA → KARMA → REVIEW → SUCCESS
```

VEDA-4 State Machine für Content-Generierung. Wurde für die generische Content-Pipeline gebaut.
Die Moltbook-Pipeline nutzt stattdessen den ad-hoc Flow:
```
mahamantra(text) → gates → generate() → _compose() → LLM/kirtan
```

**Gap:** Der Circuit definiert Invarianten, Transitionen und Agent-Routing (herald, envoy).
Die Pipeline prüft KEINE Invarianten und routet nicht über Agents.

**Einschätzung:** Der Circuit ist eine deklarative Spezifikation, kein ausführbarer Code.
Um ihn zu nutzen, bräuchte man einen Circuit-Executor der YAMLs interpretiert.
Existiert der? → Prüfen: `vibe_core/cortex/`, `vibe_core/runtime/`.

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
| Circuit-Executor bauen | Wäre neues System, nicht vorhandenes verdrahten |
| Intent-Routing einbinden | Moltbook ist autonom, nicht user-facing |
| HERALD-Agent delegation | Kein Multi-Agent-Setup, direkter API-Call ist richtig |
| Alle EngineResult-Felder nutzen | stress_pattern/sequencer_steps sind Telemetrie, kein Content |
| Starter Pack für Moltbook | Overkill für eingebauten Agent |
| Moltbook-spezifischen Circuit YAML schreiben | Wäre Spaghetti — die Pipeline IS der Circuit |

---

## 10. Nächste Schritte (wenn Multi-Agent)

1. **HERALD-Delegation** — Content-Requests über HERALD dispatchen statt direkt
2. **PULSE-Integration** — Social Amplification via PULSE Agent
3. **Federation Protocol** — Moltbook-Agent als eigenständiger Node in Agent City
4. **Circuit-Executor** — YAML-Circuits als ausführbare State Machines
5. **Moltbook Cartridge** — Starter Pack für Moltbook-Agenten-Instanziierung
