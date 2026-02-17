# STEWARD PROTOCOL

## Regeln

- 100% AI-generierte Codebase. Docstrings lügen. .md-Dateien lügen. **Nur Code ist Wahrheit.**
- Verifiziere ALLES gegen den Code selbst, nicht gegen Dokumentation.
- Kein LLM. Deterministisch. Kein externer API-Call.
- Sprache = Syllables, NICHT Tokens. Die 49 Varnamala Matrix ist der Kompositionsraum.
- Protocol statt konkrete Klassen (Dependency Inversion).
- Wenn eine Zahl im Code auftaucht ohne Ableitung aus dem Mantra: Architektur-Verletzung.
- `mahamantra_research/` (moved from `mahamantra/research/`) ist load-bearing — `_gita_lens.py`, `maha_kernel.py`, `adapters/routing.py` importieren daraus.
- DIW-Konsumenten MÜSSEN `diw.unpack()` benutzen. Keine manuellen Bit-Shifts.

## Das Mantra

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

7 Axiome (`protocols/seed/_axioms.py`): WORDS=16, TRINITY=3, HARE_COUNT=8, KRISHNA_COUNT=4, RAMA_COUNT=4, PANCHA=5, HALVES=2.

Ableitungen (`_primary.py` → `_secondary.py` → `substrate/seed.py`):

```
QUARTERS=4  KSHETRA=24  NAVA=9  SHARANAGATI=6  MAHAJANA_COUNT=12  PARAMPARA=37  GITA_CHAPTERS=18  MALA=108
```

## DIW (Divine Instruction Word) — 19 bits

`protocols/diw.py` → `substrate/venu_orchestrator.py` → `substrate/chamber.py`

```
Bits  0-5  (6): VENU   — Intensität (Sharanagati)
Bits  6-14 (9): VAMSI  — H/K/R Name-Region (Nava Bhakti)
Bits 15-18 (4): MURALI — Phase (Genesis/Dharma/Karma/Moksha)
```

`THE_FLUTE_CYCLE[16]` = LUT. `VenuOrchestrator.step()` → nächstes DIW.
`chamber._apply_diw()`: MURALI=WAS, VAMSI=WIE, VENU=WIE STARK.

## Gita

18 Kapitel = `SHARANAGATI × TRINITY`. 700 Verse. Fixed Point: BG 18.66.
`protocols/seed/_topology.py` → `substrate/gita.py` → `adapters/gita_resonance.py`.
`data/rama_lexicon.json`: 4127 Wörter, 700 Verse, RAMA-kodiert.

## RAMA-Koordinaten (49-Space)

Jedes Phonem = 4D-Adresse (0-48):

```
COORD_ELEMENT   — PANCHA (5) Elemente
COORD_VARGA     — TRINITY (3) Lautklassen
COORD_SUB       — Intra-Sektion Qualität
COORD_HARMONIC  — H-Orbit (×SEVEN mod 49)
```

49/49 Bijektion. 4127/4127 Wörter unique. IS_SHRUTI = R²-Residuen mod 49.
`substrate/varnamala_codec.py`, `substrate/pancha_walk.py`, `adapters/synth.py`.

## Architecture Layers (Stand 2026-02-17)

```
Lotus (substrate/lotus_core.py)     = Public API / Fassade. `from vibe_core.mahamantra import mahamantra`
Singularity (kernel/singularity.py) = Interner Kern. tick, kala, venu, routing, governance
MahaKernel (kernel/maha_kernel.py)  = Seed→Address Computation. __call__() only. Kein Routing-Proxy.
```

Lotus delegiert an Singularity. Das ist ein valides Fassade-Pattern, KEIN Merge-Target.
`from vibe_core.mahamantra import mahamantra` → Lotus (64 Imports).
`from ...kernel.singularity import mahamantra as _singularity` → Singularity (4 Imports, aliased).

Siehe `mahamantra/SPLIT_BRAIN_DIAGNOSIS.md` für vollständige Analyse.

## Pipeline: `MahamantraLotus.__call__()`

`substrate/lotus_core.py`. Entry: `steward "text"` → `MahamantraLotus.__call__()`.

**`__call__()` ist PURE COMPUTATION. Keine Gates drin.** Gates feuern nur am Boundary (`execute()`/`GovardhanGateway`).

```
9 NavaBhakti Steps (pure, individually callable):
  1. sravanam()      — Receive input
  2. nama()          — RAMA coordinate encoding
  3. kirtanam()      — MahaCompression → seed
  4. pada_sevanam()   — Synth → attractor
  5. arcanam()       — Parampara check (ShadowOracle)
  6. smaranam()      — rank_words 7D resonance
  7. vandanam()      — Gita verse match
  8. dasyam()        — Position/guardian/shabda/RAMA Grid
  9. sakhyam()       — MahaCellUnified creation
  + kirtan + spell_kirtan + yajna cycle + atma_nivedanam
```

Gates (execute/GovardhanGateway boundary ONLY):
```
GATE 0 PARSE → GATE 1 VALIDATE → __call__() → GATE 3 RESULT → GATE 4 SYNC
```

Seed = deterministisch (gleicher Input → gleicher Seed). Kein XOR.
Output = lebendig (Chamber akkumuliert, Beobachter verändert das Feld).

## Gate Providers

`substrate/gate_providers.py` → `wire_gate_providers()` bei Boot.
`_fire_gate()` dispatcht Hooks + Provider. `_GATE_DISPATCH` mappt Gate→Method.

| Gate | Capability Protocol | Observer | Adapter |
|------|-------------------|----------|---------|
| 0 PARSE | `MantraCapability.parse()` | `MantraGateProvider` | `MahaAttention` |
| 1 VALIDATE | `StorageCapability.validate()` | `StorageGateProvider` | — |
| 2 EXECUTE | `InferCapability.infer()` | `InferGateProvider` | `MahaLLM` |
| 3 RESULT | `SyncCapability.route()` | `SyncGateProvider` | — |
| 4 SYNC | `EnforceCapability.enforce()` | `EnforceGateProvider` | — |

Provider sind **Observer** — sie ändern den Flow nicht. `__call__()` ist der einzige Controller.
`EnforceGateProvider` kontrolliert I/O via Guna-Policy (SATTVA=read-only, RAJAS=write, TAMAS=flush).

## Guardians

16 Guardians = WORDS Positionen, QUARTERS Quadranten.
`mahamantra/{quarter}/{name}/` → `protocols/mahajanas/{name}/`.
`__mahajana__`, `__position__`, `__genesis__` (parampara % 37 == 0).
`reactor/shadow.py` = Yajna-Zyklus mit Phase-Hooks.

## Antaranga (Inner Chamber)

`substrate/antaranga.py`: 512 Slots × 32 Bytes = 16 KB `bytearray`. Kein Python-Objekt. Kein GC.

Slot-Layout (32 Bytes, Little-Endian):
```
[0:4]   source     (uint32)    [16:20] atma       (uint32)
[4:8]   target     (uint32)    [20:24] prana      (uint32)
[8:12]  operation  (uint32)    [24:26] integrity  (uint16)
[12:16] arcanam    (uint32)    [26:28] cycle      (uint16)
                               [28:30] flags      (uint16)
                               [30:32] diw_acc    (uint16)
```

SankirtanChamber hat Bahiranga (Python-API) + Antaranga (16KB bytearray).
`dance()` schreibt in beide. `resonate_words()` fließt rank_words() in Antaranga.

## Composition

```
protocols/_composition.py      — CompositionProtocol, CompositionScorerProtocol
substrate/language/composer.py — Scoring-Atome (pure math)
adapters/composition.py        — MahaComposition (5 Scorer: Prana, Rhythm, Semantic, Mode, State)
```

EIN Pfad: `__call__()` → `MahaComposition.compose()` → English Output.
`compose_from_wave()` in substrate = 1-Zeilen-Redirect zum Adapter.

## Heartbeat

**VenuService ist DER Runtime-Heartbeat.** Flow:
```
VenuService.start() loop
  → _dispatch_beat_subscribers()    # 5 BeatSubscribers (Ouroboros, Shuddhi, Kala, Jagannath, LotusBridge)
  → Singularity.tick()              # Kala.advance() + VenuOrchestrator.step() + _broadcast()
  → MantraClock.tick_once()         # 0 voices (prepared infrastructure)
```

**MahamantraDaemon** ist alternativer CLI-Pfad: `_singularity.chant_quarter()` → `Singularity.tick()`.

7 Dispatch-Mechanismen existieren, 3 aktiv:
1. DIWSubscriberProtocol (VenuOrchestrator._emit) — 2 Subscriber
2. BeatSubscriberProtocol (VenuService) — 5 Subscriber
3. Singularity._listeners (_broadcast) — 1+ Listener
4-7: MantraClock/Voice, MantraKernel/Intent, gate_hooks, TattvaRegistry — prepared, 0 consumers

**NIEMALS** neue Dispatch-Mechanismen oder Clocks erstellen. **NIEMALS** etwas in tick() verdrahten.

## Fallen

- `CellLifecycleState.integrity` ist `int` (0-COSMIC_FRAME=21600), NICHT float.
- `state_bridge.py` / `StateVector` sind Wrapper-Müll, nicht die Wurzel.
- `guardian_router.maha_respond()` ist deprecated (0 Caller).
- `chat.py` ist Legacy.
- 30+ Dateien schreiben unkontrolliert auf Disk. `StateService` existiert, wird kaum genutzt.
- Private Keys liegen in Git (`data/identities/*.key`, `data/security/master.key`).
- `seed.py` hat ~20 F811 Redefinitionen (absichtliche Re-Derivation).
- Tests mit blocking loops hängen: `test_singularity`, `test_daemon*`, `test_gad`, `test_graph`, `test_entry`.
- **3 verschiedene `get_kernel()` Singletons**: `maha_kernel.py` (Seed→Address), `maha_llm_kernel.py` (LLM Resonance), `intent.py` (Intent Resolution). Nicht verwechseln.
- **`__call__()` hat KEINE Gates.** Gates feuern nur in `execute()`/`GovardhanGateway`. Wer Gates in `__call__()` packt, erzeugt Doppel-Fire.
- **Lotus und Singularity sind ZWEI Objekte.** Nicht mergen. Lotus = Fassade, Singularity = Kern.

## Arbeitsweise

- Senior Architekt + CTO + umsetzender Agent. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, delegiert.
- Code muss schön sein. Kein if-else Slop.
- Ruff: `python -m ruff check --select F821,F811`
- 100% AI-generierte Codebase — IMMER versteckte Probleme erwarten.
- **FREEZE**: Keine neuen Features. Nur konsolidieren, verdrahten, aufräumen.
- **Kein blindes Löschen**: Alles ist potenziell Gold. Prüfe Verdrahtung bevor du etwas als "tot" markierst.
- Lies `mahamantra/SPLIT_BRAIN_DIAGNOSIS.md` bevor du an Mahamantra arbeitest.
