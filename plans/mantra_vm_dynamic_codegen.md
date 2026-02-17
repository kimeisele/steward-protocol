# Mantra VM: Dynamic Code Generation via DIW Engine

## Context

Die Codebase hat 34K Zeilen Substrate die eine fixe 9-Schritt-Pipeline (`__call__()`) implementieren.
Wartung ist unwirtschaftlich. Die Architektur hat aber schon 5 von 7 Teilen einer VM:

- DIW (19-bit Instruction Word) = Opcodes
- THE_FLUTE_CYCLE (16-entry LUT) = Instruction Stream
- VenuOrchestrator.step() = Fetch-Execute Cycle
- Antaranga (512 x 32 bytes) = Register File
- DIWSubscriberProtocol = I/O Peripherals

**Fehlt:** VAMSI-Dispatch-Table (Instruction Set) und Cycle-Generation (Compiler).

## Research-Ergebnisse: VENU/VAMSI/MURALI Kapazitaet

| Feld | Bits | Max | Genutzt | Frei |
|------|------|-----|---------|------|
| VAMSI | 9 | 512 | 16 (3.1%) | 496 |
| VENU | 6 | 64 | 16 | 48 |
| MURALI | 4 | 16 | 4 | 12 |
| 32-bit Bits 27-30 | 4 | 16 | 0 (komplett unbenutzt) | 16 |

- VAMSI IST schon die Antaranga-Slot-Adresse: `slot = (diw >> 6) & 0x1FF`
- pack_full() (32-bit) hat **0 Caller** in Production — dormante Infrastruktur
- COSMIC_FRAME = 21600, wrapped, maxed nie aus
- `.spell()` generiert schon dynamische Cycles beliebiger Laenge (nicht LUT-gebunden)

### VAMSI Collision Check

LUT belegt: `{1,3,7,8,9,11,15,16,172,174,175,176,350,352,353,354}`
NavaBhakti bei PARAMPARA(37)-Stride: `{37,74,111,148,185,222,259,296,333}`

**Null Kollisionen.** Beide Instruction Spaces koexistieren im selben 9-bit Raum.

## Plan: PoC in 3 neuen Dateien + 2 Modifikationen

### 1. `protocols/_navabhakti.py` (~80 Zeilen) — NEU

VAMSI Dispatch Table + Instruction Protocol:

```
NavaBhaktiOp(IntEnum):  SRAVANAM=0..SAKHYAM=8
NAVABHAKTI_DISPATCH:    {37: (SRAVANAM, PARSE, "sravanam"), 74: (NAMA, PARSE, "nama"), ...}
NAVABHAKTI_CYCLE:       (37, 74, 111, 148, 185, 222, 259, 296, 333)
```

Alle Adressen: `PARAMPARA * (i + KSETRAJNA)`. Jede Zahl Mantra-abgeleitet.

### 2. `substrate/execution_context.py` (~120 Zeilen) — NEU

Dual-Layer Context fuer die VM:
- Inner: Eigener 32-byte Buffer (NICHT die shared Antaranga) fuer Scalar-Register
- Outer: Python dict fuer komplexe Objekte (verse_result, resonant_words, etc.)

### 3. `substrate/mantra_vm.py` (~200 Zeilen) — NEU

Fetch-Decode-Execute Engine:
```python
for vamsi_addr in cycle:
    op, gate, method = DISPATCH[vamsi_addr]
    if gate != last_gate: fire_gate(gate, ctx)
    wrapper = STEP_WRAPPERS[op]  # Uniform ctx->ctx Interface
    wrapper(lotus, ctx)
```

### 4. `protocols/diw.py` (+15 Zeilen) — MODIFIKATION

Condition Bits (27-30): `COND_SKIP=1, COND_BRANCH=2, COND_REPEAT=4, COND_HALT=8`
Additiv — pack()/unpack() bleiben unveraendert.

### 5. `substrate/lotus_core.py` (~10 Zeilen) — MODIFIKATION

`__call__()` delegiert an MantraVM. NavaBhakti-Methoden bleiben als Instruction-Impls.

## BEKANNTE LOECHER IM PLAN

### Loch 1: Antaranga Register Conflict (KRITISCH)

Die Antaranga-Slots werden AKTUELL von chamber.dance() fuer Resonance-Collision benutzt.
`source` = Cell Identity, `target` = Cell Target, etc.
Wenn die VM dieselben Felder als `source=seed`, `target=attractor` uminterpretiert,
kollidiert das mit dem Resonance-System.

**Status:** Der Plan sagt "reinterpret fields" — das ist FALSCH.

**Loesung:** ExecutionContext benutzt einen eigenen 32-byte Buffer pro Call,
NICHT die shared Antaranga. Antaranga bleibt Resonance-Shadow. Die VM hat ihren
eigenen Mini-Registerfile. Spaeter kann man ueber eine dedizierte VM-Antaranga reden
(z.B. Slot 0 = VM, Slots 1-511 = Resonance), aber fuer den PoC: eigener Buffer.

### Loch 2: Step-Signaturen sind nicht uniform

Die 9 NavaBhakti-Methoden haben verschiedene Signaturen:
```
sravanam(input_data) -> (text, cell, seed)
nama(input_text) -> coords
kirtanam(input_text, seed) -> int
pada_sevanam(seed) -> (attractor, variance, raw_address)
arcanam(seed) -> dict
smaranam(coords, attractor) -> list
vandanam(attractor, seed) -> dict
dasyam(attractor, opcode) -> dict
sakhyam(seed, raw_address, position, input_text) -> cell
```

Der VM-Dispatch braucht uniform: `wrapper(lotus, ctx) -> None`.

**Status:** Der Plan erwaehnt keine Wrapper.

**Loesung:** 9 Wrapper-Funktionen die:
1. Args aus ctx.inner/ctx.outer lesen
2. Die originale Methode aufrufen
3. Ergebnisse in ctx.inner/ctx.outer schreiben

Das sind ~90 Zeilen (10 pro Wrapper). Muss in mantra_vm.py oder execution_context.py.

### Loch 3: Output-Dict Rekonstruktion

`__call__()` returned ein Dict mit 30+ Keys, teils verschachtelt (`vibration.seed`,
`diw.venu`, `cell.header_size`, `parampara.verified`, etc.).
`_build_result(ctx)` muss exakt dasselbe Dict bauen.

**Status:** Der Plan sagt "build_result" aber spezifiziert nicht WAS.

**Loesung:** _build_result() muss alle 30+ Keys aus den 9 Step-Ergebnissen zusammenbauen.
Das ist der aufwaendigste Teil (~80 Zeilen). Muss exakt gegen den aktuellen Output
getestet werden. Jeder Key einzeln.

### Loch 4: Condition Bits haben keine Evaluation-Logik

Der Plan fuegt COND_SKIP/BRANCH/REPEAT/HALT als Encoding hinzu, aber niemand
evaluiert sie. Eine BRANCH-Instruction braucht eine Ziel-Adresse — woher?

**Status:** Feature ohne Implementierung.

**Loesung:** Aus dem PoC streichen. Condition Bits sind Phase 2.
Fuer den PoC: Lineare Execution (kein Branching). Bits 27-30 definieren
aber noch nicht nutzen.

### Loch 5: CycleCompiler.compile_from_test() ist Magic Thinking

"Inspects what the test checks -> derives which steps are needed" hat keinen
konkreten Mechanismus. Wie soll das ohne LLM funktionieren?

**Status:** Handwaving.

**Loesung:** Aus dem PoC streichen. Phase 3. Fuer den PoC reicht
NAVABHAKTI_CYCLE als statischer Default + manuelle Custom Cycles.

### Loch 6: Concurrency

ExecutionContext an einem shared Antaranga-Slot: Mehrere parallele __call__()
Aufrufe clobbern sich gegenseitig.

**Status:** Nicht adressiert.

**Loesung:** Eigener Buffer pro Call (siehe Loch 1). Kein Shared State
in der VM-Execution. Thread-Safe by Construction.

## Bereinigter PoC-Scope

Was TATSAECHLICH gebaut werden muss:

| Datei | Zeilen | Inhalt |
|-------|--------|--------|
| `protocols/_navabhakti.py` | ~80 | NavaBhaktiOp, DISPATCH Table, CYCLE, Protocol |
| `substrate/execution_context.py` | ~150 | Eigener 32-byte Buffer + Python dict, Register-Accessors |
| `substrate/mantra_vm.py` | ~280 | Engine + 9 Step-Wrapper + _build_result() |
| `protocols/diw.py` (mod) | +15 | Condition Bit Definitionen (ohne Eval-Logik) |
| `substrate/lotus_core.py` (mod) | +10 | _vm Attribut, __call__ Delegation |
| `tests/test_mantra_vm.py` | ~100 | Aequivalenz-Test, Step-Isolation-Tests |
| **Total** | **~635** | |

Was NICHT im PoC ist:
- Condition Evaluation (Phase 2)
- CycleCompiler (Phase 3)
- Antaranga-Integration (Phase 4 — nach bewiesener Aequivalenz)
- Substrate-Reduktion (Phase 5 — erst wenn alles laeuft)

## Verifikation

```bash
# 1. Aequivalenz-Test
python -m pytest tests/test_mantra_vm.py -v

# 2. Bestehende Tests unveraendert
python -m pytest vibe_core/mahamantra/tests/ -x

# 3. Ruff clean
python -m ruff check --select F821,F811 vibe_core/mahamantra/protocols/_navabhakti.py \
    vibe_core/mahamantra/substrate/execution_context.py \
    vibe_core/mahamantra/substrate/mantra_vm.py
```

## Was sich NICHT aendert

- 7 Axiome, _seed.py, alle Ableitungen
- THE_FLUTE_CYCLE, VenuOrchestrator
- 5 TattvaGates, 5 Capability Protocols
- Antaranga Resonance-System
- 16 Guardians, SankirtanChamber
- Alle bestehenden Tests
