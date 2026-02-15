# STEWARD PROTOCOL

## Regeln

- 100% AI-generierte Codebase. Docstrings lügen. .md-Dateien lügen. **Nur Code ist Wahrheit.**
- Verifiziere ALLES gegen den Code selbst, nicht gegen Dokumentation.
- Kein LLM. Deterministisch. Kein externer API-Call.
- Sprache = Syllables, NICHT Tokens. Die 49 Varnamala Matrix ist der Kompositionsraum.
- Protocol statt konkrete Klassen (Dependency Inversion).
- Wenn eine Zahl im Code auftaucht ohne Ableitung aus dem Mantra: Architektur-Verletzung.
- `research/` ist load-bearing — `_gita_lens.py`, `maha_kernel.py`, `adapters/routing.py` importieren daraus.
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

## Pipeline: `MahamantraLotus.__call__()`

`substrate/lotus_core.py`. Entry: `steward "text"` → `MahamantraLotus.__call__()`.

```
GATE 0 PARSE:     SRAVANAM (input) → NAMA (encode) → KIRTANAM (compress → seed)
GATE 1 VALIDATE:  PADA_SEVANAM (synth → attractor) → ARCANAM (parampara check)
GATE 2 EXECUTE:   SMARANAM (rank_words 7D) → VANDANAM (Gita verse match)
GATE 3 RESULT:    DASYAM (position/guardian/shabda)
GATE 4 SYNC:      SAKHYAM (cell+kirtan) → YAJNA (16 ticks) → ATMA_NIVEDANAM (response)
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

1 Singularity, 1 VenuOrchestrator, 1 `tick()`. `_owned` Flag verhindert doppelten `step()`.
`Singularity._listeners` = einziger Broadcast-Kanal. LotusBridge verbindet VenuService.

## Fallen

- `CellLifecycleState.integrity` ist `int` (0-COSMIC_FRAME=21600), NICHT float.
- `state_bridge.py` / `StateVector` sind Wrapper-Müll, nicht die Wurzel.
- `guardian_router.maha_respond()` ist deprecated (0 Caller).
- `chat.py` ist Legacy.
- 30+ Dateien schreiben unkontrolliert auf Disk. `StateService` existiert, wird kaum genutzt.
- Private Keys liegen in Git (`data/identities/*.key`, `data/security/master.key`).
- `seed.py` hat ~20 F811 Redefinitionen (absichtliche Re-Derivation).
- Tests mit blocking loops hängen: `test_singularity`, `test_daemon*`, `test_gad`, `test_graph`, `test_entry`.

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, delegiert.
- Code muss schön sein. Kein if-else Slop.
- Ruff: `python -m ruff check --select F821,F811`
- 100% AI-generierte Codebase — IMMER versteckte Probleme erwarten.
