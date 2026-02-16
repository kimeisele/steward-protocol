# CLI Vollstaendige Kartierung

**Datum**: 2026-02-03
**Research Lead**: Opus Agent
**Fokus**: 100% Identifikation ALLER CLI-Systeme

---

## 1. DAS ECHTE PROBLEM: ZWEI PARALLELE CLI-SYSTEME

```
┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM 1: vibe_core/cli/                                       │
│  ─────────────────────────────────────────────────────────────  │
│  69 Dateien | 19.349 LOC                                        │
│  "Fractal CLI System"                                           │
│                                                                 │
│  Entry Points:                                                  │
│  ├── main.py         → "MAHAMANTRA IS THE KING"                 │
│  │                      mahamantra(input) direkt                │
│  ├── unified_cli.py  → UnifiedCLI                               │
│  ├── legacy.py       → StewardCLI                               │
│  └── executor.py     → CLIExecutor                              │
│                                                                 │
│  Domain CLIs (69!):                                             │
│  ├── audit_cli.py, genesis_cli.py, governance_cli.py           │
│  ├── kirtan_cli.py, knowledge_cli.py, lotus_cli.py             │
│  ├── naga_cli.py (+ naga_commands/ mit 20+ Befehlen)           │
│  ├── prakriti_cli.py, prompts_cli.py, run_cli.py               │
│  └── ... und 50+ weitere                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM 2: vibe_core/mahamantra/cli/                            │
│  ─────────────────────────────────────────────────────────────  │
│  14 Dateien | 5.602 LOC                                         │
│  "CLI via Mahamantra" (Pancha Tattva basiert)                   │
│                                                                 │
│  Entry Points (Die 6 aus der Research):                         │
│  ├── entry.py        → MahamantraCLIEntry, cli_auto             │
│  ├── bridge.py       → MahamantraCLIBridge, Routing             │
│  ├── engine.py       → CLIEngine, manuelles Register            │
│  ├── steward.py      → Steward, Resonance Router                │
│  ├── veda_explorer.py→ VedaExplorer, Chat Interface             │
│  └── auto.py         → CLIAutoDiscovery, Protocol Introspection │
│                                                                 │
│  5 Gates = Pancha Tattva:                                       │
│  ├── Entry (Chaitanya)    - Parse/Entry                         │
│  ├── Bridge (Nityananda)  - Routing/Foundation                  │
│  ├── Engine (Advaita)     - Execution/Logic                     │
│  ├── Protocol (Gadadhara) - Results/Connection                  │
│  └── Auto (Srivasa)       - Discovery/Governance                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. VERBINDUNG ZWISCHEN DEN SYSTEMEN

**Nur 2 Import-Verbindungen gefunden:**

1. `mahamantra/cli/map.py` → importiert `UnifiedCLI` von `vibe_core.cli`
2. `vibe_core/cli/main.py` → importiert `map_command` von `mahamantra/cli`

**Die Systeme sind fast UNABHAENGIG!**

---

## 3. DIE 7+ ENTRY POINTS IM DETAIL

### System 1: vibe_core/cli/

| Datei | LOC | Ansatz | Ruft auf |
|-------|-----|--------|----------|
| `main.py` | ~200 | **RESONANZ-DIREKT** | `mahamantra(input)` |
| `unified_cli.py` | 1555 | Legacy manual wiring | Handler-Registry |
| `legacy.py` | ? | StewardCLI | ? |
| `executor.py` | ? | CLIExecutor | Handler |

### System 2: vibe_core/mahamantra/cli/

| Datei | LOC | Ansatz | Ruft auf |
|-------|-----|--------|----------|
| `entry.py` | 293 | **DISCOVERY-BASIERT** | `cli_auto.execute()` |
| `bridge.py` | 233 | Routing | `cli_auto._get_position()` |
| `engine.py` | 488 | Manuelles Register | Handler-Registry |
| `steward.py` | 489 | **RESONANZ-ROUTER** | `mahamantra()` via `_get_mahamantra()` |
| `veda_explorer.py` | 1261 | **VEDA-4 PIPELINE** | Commands + LLM |
| `auto.py` | 680 | Protocol Introspection | Protocol Methods |

---

## 4. DIE ZWEI HAUPTANSAETZE

### Ansatz A: RESONANZ-DIREKT (main.py, steward.py)

```python
# vibe_core/cli/main.py
from vibe_core.mahamantra import mahamantra
response = mahamantra(input_text)  # Direkt __call__
```

**Flow:**
```
Input → mahamantra() → 9 NavaBhakti → Response
                       ├─ SRAVANAM    (Receive)
                       ├─ KIRTANAM    (Compress)
                       ├─ SMARANAM    (Vibrate)
                       ├─ PADA_SEVANAM (Resonate)
                       ├─ ARCANAM     (Verify)
                       ├─ VANDANAM    (Match Gita)
                       ├─ DASYAM      (Position)
                       ├─ SAKHYAM     (Cell)
                       └─ ATMA_NIVEDANAM (Response)
```

**Eigenschaften:**
- Deterministisch
- Keine KI noetig
- Holographisch - Input bestimmt alles
- ZERO Hardcoding

### Ansatz B: DISCOVERY-BASIERT (entry.py, auto.py)

```python
# vibe_core/mahamantra/cli/entry.py
from vibe_core.mahamantra.cli.auto import cli_auto
result = cli_auto.execute(command, args)
```

**Flow:**
```
Input → cli_auto.discover_all() → Protocol Methods → execute()
```

**Eigenschaften:**
- Introspection von Protocol Klassen
- Automatische Capability Discovery
- Strukturierte Commands statt freier Text

### Ansatz C: VEDA-4 PIPELINE (veda_explorer.py)

```python
# VEDA-4:
#   SHABDA (Word)     → Intent parsing
#   ARTHA (Meaning)   → Parameter extraction
#   PRATYAYA (Trust)  → Validation
#   KARMA (Action)    → Execution
```

**Modes:**
- RESTRICTED → Deterministisch (kein LLM)
- ENHANCED → LLM fuer fuzzy matching
- CREATIVE → Full LLM generation

---

## 5. DAS PROBLEM VISUELL

```
USER INPUT: "steward analyze my code"
         │
         ├─────────────────────────────────────────────────────┐
         │                                                     │
         ▼                                                     ▼
┌─────────────────────┐                          ┌─────────────────────┐
│ vibe_core/cli/main.py│                          │ mahamantra/cli/     │
│                     │                          │                     │
│ mahamantra(input)   │                          │ ├── entry.py        │
│                     │                          │ ├── bridge.py       │
└─────────┬───────────┘                          │ ├── engine.py       │
          │                                      │ ├── steward.py      │
          ▼                                      │ ├── veda_explorer.py│
┌─────────────────────┐                          │ └── auto.py         │
│ MahamantraLotus     │                          └──────────┬──────────┘
│ .__call__()         │                                     │
└─────────────────────┘                                     │
                                                            ▼
                                              ??? WELCHER WIRD GENUTZT ???
```

---

## 6. ZUSAETZLICHE CLI-KOMPONENTEN

### Protokoll-Dateien

```
vibe_core/protocols/cli.py           - CLI Protocol Definition
vibe_core/protocols/cli_execution.py - CLI Execution Protocol
vibe_core/protocols/naga/cli_command.py - Naga CLI Commands
vibe_core/protocols/substrate/cli_loader.py - CLI Loader Protocol
vibe_core/protocols/substrate/cli_substrate.py - CLI Substrate
vibe_core/protocols/universal/cli.py - Universal CLI Protocol
```

### Hook Chain (ADR!)

```
vibe_core/naga/cli_hook_chain.py - HookChain Pattern (aus ADR_FRACTAL_CLI!)
```

---

## 7. WAS EXISTIERT VS WAS FEHLT

### EXISTIERT (99%!)

- [x] MahamantraLotus mit `__call__` (9 NavaBhakti)
- [x] MahaCompression (Intent Extraction)
- [x] MahaKirtan (Vibration Compute)
- [x] SankirtanChamber (Resonance Space)
- [x] VenuOrchestrator (DIW Routing)
- [x] GitaResonance (Chapter Matching)
- [x] CLIAutoDiscovery (Protocol Introspection)
- [x] Steward (Resonance Router)
- [x] VedaExplorer (Chat Interface)
- [x] HookChain Pattern (in naga/)
- [x] 69 Domain CLIs (audit, genesis, etc.)

### FEHLT (Integration!)

- [ ] **EIN klarer Entry Point** (aktuell 7+)
- [ ] **Hierarchie** (wer ruft wen?)
- [ ] **System 1 + System 2 Vereinigung**
- [ ] **HookChain statt parallele Pfade**

---

## 8. DER IDEALE FLOW (Vorschlag)

```
USER
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  EIN ENTRY POINT: steward <input>                               │
│  (vibe_core/cli/main.py oder mahamantra/cli/entry.py)          │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  MahamantraLotus.__call__(input)                                │
│                                                                 │
│  INTERN orchestriert:                                           │
│  ├── MahaCompression → seed                                     │
│  ├── MahaKirtan → attractor                                     │
│  ├── GitaResonance → chapter                                    │
│  ├── cli_auto.capabilities() → was kann ich?                   │
│  ├── bridge.route() → welcher Mahajana?                        │
│  └── engine/steward → execute                                   │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  16 Mahajanas / 69 Domain CLIs                                  │
│                                                                 │
│  Resonance-basiertes Routing zu:                                │
│  ├── kapila (Position 6) → analyze, sankhya                    │
│  ├── yamaraja (Position 15) → audit, judge                     │
│  ├── brahma (Position 1) → create, spawn                       │
│  └── ...                                                        │
└─────────────────────────────────────────────────────────────────┘
  │
  ▼
RESPONSE
```

---

## 9. NAECHSTE SCHRITTE

### Fragen fuer User-Entscheidung:

1. **Soll System 1 (vibe_core/cli/) zu System 2 (mahamantra/cli/) migriert werden?**
   - Oder umgekehrt?
   - Oder unified?

2. **Welcher Ansatz ist der Richtige?**
   - A) Resonanz-direkt (main.py) - `mahamantra(input)`
   - B) Discovery-basiert (entry.py) - `cli_auto.execute()`
   - C) Kombination

3. **Was passiert mit den 69 Domain CLIs?**
   - Migration zu Mahajana-Modules?
   - Oder als "Servants" unter mahamantra?

4. **HookChain Pattern (aus ADR) einsetzen?**
   - Statt paralleler Entry Points
   - Hook-basierte Erweiterung

---

## 10. ZUSAMMENFASSUNG

| Metrik | Wert |
|--------|------|
| CLI-Systeme | 2 (parallel, fast unverbunden) |
| Entry Points | 7+ |
| Dateien Total | 83 (69 + 14) |
| LOC Total | ~25.000 |
| Domain CLIs | 69 |
| Protokoll-Dateien | 6 |
| Verbindungen | 2 (!) |

**FAZIT:**
- Das Chaos ist REAL
- Die Loesungen EXISTIEREN aber sind nicht verbunden
- Es braucht EINEN Entry Point und EINE Hierarchie
- Der "Krebs" ist die PARALLELE Struktur, nicht fehlender Code
