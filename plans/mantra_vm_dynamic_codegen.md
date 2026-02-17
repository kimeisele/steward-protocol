# Mantra VM: Dynamic Code Generation via DIW Engine

## Context

34K Zeilen Substrate implementieren eine fixe Pipeline (`__call__()`, 250 Zeilen).
Die Architektur hat 5 von 7 Teilen einer VM. Es fehlen 2:
VAMSI-Dispatch-Table und Cycle-Generation.

## Research: Ist das DIW-System ready?

| Feld | Bits | Kapazitaet | Belegt | Frei |
|------|------|------------|--------|------|
| VAMSI | 9 | 512 | 16 (3.1%) vom Flute Cycle | 496 |
| VENU | 6 | 64 | 16 | 48 |
| MURALI | 4 | 16 | 4 | 12 |
| Bits 27-30 (32-bit Word) | 4 | 16 | 0 | 16 |

- VAMSI IST schon die Antaranga-Adresse (`slot = (diw >> 6) & 0x1FF`)
- `pack_full()` (32-bit) hat 0 Caller in Production — dormante Infrastruktur
- COSMIC_FRAME = 21600, wrapped, maxed nie aus
- `.spell()` generiert schon dynamische Cycles beliebiger Laenge

### Collision Check

Flute LUT belegt VAMSI: `{1,3,7,8,9,11,15,16,172,174,175,176,350,352,353,354}`

VM-Instructions bei PARAMPARA(37)-Stride: `{37,74,111,148,185,222,259,296,333,370,407,444}`

**Null Kollisionen.** Verifiziert: Keiner der 16 LUT-Werte ist ein Vielfaches von 37.

## Architektur: 12 Instructions = MAHAJANA_COUNT

Die Pipeline hat 12 Schritte (nicht 9 wie im Docstring behauptet):

| # | Instruction | Gate | VAMSI-Addr | Quelle |
|---|-------------|------|------------|--------|
| 0 | SRAVANAM | PARSE (0) | 37 | `lotus.sravanam()` |
| 1 | NAMA | PARSE (0) | 74 | `lotus.nama()` |
| 2 | KIRTANAM | PARSE (0) | 111 | `lotus.kirtanam()` |
| 3 | PADA_SEVANAM | VALIDATE (1) | 148 | `lotus.pada_sevanam()` |
| 4 | ARCANAM | VALIDATE (1) | 185 | `lotus.arcanam()` |
| 5 | SMARANAM | EXECUTE (2) | 222 | `lotus.smaranam()` |
| 6 | VANDANAM | EXECUTE (2) | 259 | `lotus.vandanam()` |
| 7 | DASYAM | RESULT (3) | 296 | `lotus.dasyam()` |
| 8 | SAKHYAM | SYNC (4) | 333 | `lotus.sakhyam()` |
| 9 | KIRTAN | SYNC (4) | 370 | `chamber.resonate/kirtan/spell` |
| 10 | YAJNA | SYNC (4) | 407 | `reactor.tick()` x16 |
| 11 | ATMA_NIVEDANAM | SYNC (4) | 444 | akash update + return dict |

Adressen: `PARAMPARA * (i + KSETRAJNA)` fuer `i in range(MAHAJANA_COUNT)`.
12 = MAHAJANA_COUNT = KSHETRA / HALVES = 24 / 2. Jede Zahl Mantra-abgeleitet.

## Context: Eigener Buffer pro Call, kein Shared State

Kein Antaranga-Conflict. Jeder `execute_cycle()` Aufruf bekommt einen eigenen
Python-Dict als Context. Antaranga bleibt unberuehrt fuer Resonance.

```python
ctx = {
    # Von SRAVANAM gesetzt:
    "input_text": str, "cell": MahaCell|None, "seed": int|None,
    # Von NAMA:
    "input_coords": tuple,
    # Von KIRTANAM:
    "seed": int,  # ueberschreibt None von SRAVANAM
    # Von PADA_SEVANAM:
    "attractor": int, "variance": int, "raw_address": int,
    # Von ARCANAM:
    "parampara_verified": bool, "parampara_channel": int, "parampara_coherence": float,
    # Von SMARANAM:
    "resonant_words": list,
    # Von VANDANAM:
    "verse_result": obj, "verse_info": dict|None, "chapter": int,
    "chapter_significance": str, "gita_phase": str, "is_complete": bool,
    # Von DASYAM:
    "position": int, "diw": int, "diw_comp": namedtuple,
    "quarter": str, "guardian": str, "role": str,
    "quarter_head_name": str, "holy_name": str, "trinity_function": str,
    "rama_coord": int, "phoneme": str,
    "phoneme_element": int, "phoneme_varga": int, "phoneme_sub": int,
    "phoneme_harmonic": int, "phoneme_shruti": bool,
    "pipeline_opcode": MantraOpCode, "pipeline_guna": Guna,
    # Von SAKHYAM:
    "result_cell": MahaCellUnified,
    # Von KIRTAN:
    "result_cell": MahaCellUnified,  # transformiert
    "kirtan_cycles": int, "antaranga_collisions": int,
    # Von YAJNA:
    "shadow_state": dict, "guardian_result": obj|None,
    # Von ATMA_NIVEDANAM:
    -> return dict (27 Keys)
}
```

~35 benannte Werte. Alle scalar oder kleine Objekte. Kein GC-Problem.

## 12 Wrapper-Funktionen (exakte Signaturen)

Jeder Wrapper: liest aus ctx, ruft originale Methode, schreibt in ctx.

```python
# Wrapper 0: SRAVANAM — lotus_core.py:469
def _w_sravanam(lotus, ctx):
    text, cell, seed = lotus.sravanam(ctx["input_data"])
    ctx["input_text"] = text
    ctx["cell"] = cell
    ctx["seed"] = seed

# Wrapper 1: NAMA — lotus_core.py:482
def _w_nama(lotus, ctx):
    ctx["input_coords"] = lotus.nama(ctx["input_text"])

# Wrapper 2: KIRTANAM — lotus_core.py:487
def _w_kirtanam(lotus, ctx):
    ctx["seed"] = lotus.kirtanam(ctx["input_text"], ctx["seed"])

# Wrapper 3: PADA_SEVANAM — lotus_core.py:494
def _w_pada_sevanam(lotus, ctx):
    a, v, r = lotus.pada_sevanam(ctx["seed"])
    ctx["attractor"] = a
    ctx["variance"] = v
    ctx["raw_address"] = r

# Wrapper 4: ARCANAM — lotus_core.py:503
def _w_arcanam(lotus, ctx):
    ov = lotus.arcanam(ctx["seed"])
    ctx["parampara_verified"] = ov["parampara_validated"]
    ctx["parampara_channel"] = ov["parampara_channel"]
    ctx["parampara_coherence"] = ov["coherence"]

# Wrapper 5: SMARANAM — lotus_core.py:511
def _w_smaranam(lotus, ctx):
    ctx["resonant_words"] = lotus.smaranam(ctx["input_coords"], ctx["attractor"])

# Wrapper 6: VANDANAM — lotus_core.py:519
def _w_vandanam(lotus, ctx):
    v = lotus.vandanam(ctx["attractor"], ctx["seed"])
    ctx["verse_result"] = v["verse_result"]
    ctx["verse_info"] = v["verse_info"]
    ctx["chapter"] = v["chapter"]
    ctx["chapter_significance"] = v["chapter_significance"]
    ctx["gita_phase"] = v["gita_phase"]
    ctx["is_complete"] = v["is_complete"]

# Wrapper 7: DASYAM — lotus_core.py:556
def _w_dasyam(lotus, ctx):
    d = lotus.dasyam(ctx["attractor"], ctx.get("opcode"))
    ctx.update(d)  # alle 18 Keys direkt

# Wrapper 8: SAKHYAM — lotus_core.py:607
def _w_sakhyam(lotus, ctx):
    ctx["result_cell"] = lotus.sakhyam(
        ctx["seed"], ctx["raw_address"], ctx["position"], ctx["input_text"]
    )

# Wrapper 9: KIRTAN — lotus_core.py:756-777
def _w_kirtan(lotus, ctx):
    P = _get_pipeline()
    chamber = P.get_chamber()
    rw = ctx["resonant_words"]
    ctx["antaranga_collisions"] = chamber.resonate_words(rw, ctx["attractor"]) if rw else 0
    ctx["kirtan_cycles"] = min(
        P.KSETRAJNA + lotus._akash["total_rounds"] // P.WORDS,
        P.MAX_CYCLES,
    )
    ctx["result_cell"] = chamber.kirtan(ctx["result_cell"], cycles=ctx["kirtan_cycles"])
    if ctx["input_coords"]:
        ctx["result_cell"] = chamber.spell_kirtan(ctx["result_cell"], ctx["input_coords"])

# Wrapper 10: YAJNA — lotus_core.py:779-833
def _w_yajna(lotus, ctx):
    P = _get_pipeline()
    reactor = P.get_shadow_reactor_factory().spawn(
        auto_discover=False, initial_position=ctx["position"], forced_lagna=0,
    )
    reactor.chant(_THIS_MODULE)
    reactor.set_maha_cell(MahaCell(
        header=MahaHeader.create(
            source=ctx["seed"], target=ctx["raw_address"],
            operation=ctx["position"], link=0, intent=0,
            ttl=HEADER_DAILY_CYCLES, state=0,
        ),
        payload=ctx["input_text"].encode("utf-8"),
    ))
    shadow_state = None
    guardian_result = None
    base_tick = lotus._akash["total_beats"]
    for i in range(P.WORDS):
        tp = (ctx["position"] + i) % P.WORDS
        tw, to = P.MAHAMANTRA_SEQUENCE[tp]
        tick_input = {
            "tick": base_tick + i, "position": tp,
            "quarter": P.quarter_names[tp], "guardian": P.ALL_GUARDIANS[tp],
            "word": tw, "opcode": to.value,
        }
        shadow_state = reactor.tick(tick_input)
        tr = shadow_state.get("execution_result")
        if tr is not None:
            guardian_result = tr
    ctx["shadow_state"] = shadow_state
    ctx["guardian_result"] = guardian_result

# Wrapper 11: ATMA_NIVEDANAM — lotus_core.py:838-949
def _w_atma_nivedanam(lotus, ctx):
    P = _get_pipeline()
    WORDS = P.WORDS
    lotus._akash["total_beats"] += WORDS
    lotus._akash["total_rounds"] += 1
    lotus._akash["accumulated_value"] = (
        lotus._akash["accumulated_value"] + ctx["attractor"]
    ) % P.MAHA_QUANTUM
    lotus._akash["attractor_counts"][ctx["attractor"]] = (
        lotus._akash["attractor_counts"].get(ctx["attractor"], 0) + 1
    )
    lotus._akash["last_seed"] = ctx["seed"]
    lotus._akash["last_position"] = ctx["position"]
    lotus._akash["last_attractor"] = ctx["attractor"]
    ctx["_result"] = _build_result(ctx, lotus, P)
    # _build_result() konstruiert den 27-Key Dict identisch zu lotus_core.py:847-949
```

## Output Dict: 27 Keys, vollstaendig gemappt

`_build_result(ctx, lotus, P)` liest alle Werte aus ctx und baut:

```python
{
    "input":                ctx["input_text"],
    "tattva_gate":          "SRIVASA",
    "guna": {
        "mode":             ctx["pipeline_guna"].name,
        "opcode":           ctx["pipeline_opcode"].name,
        "opcode_value":     ctx["pipeline_opcode"].value,
        "source":           "caller" if ctx.get("opcode") is not None else "position",
    },
    "vibration": {
        "seed":             ctx["seed"],
        "attractor":        ctx["attractor"],
        "rama_index":       ctx["rama_coord"],
        "phoneme":          ctx["phoneme"],
        "signature": {
            "element":      P.ELEMENT_NAMES[ctx["phoneme_element"]],
            "varga":        ctx["phoneme_varga"],
            "sub":          ctx["phoneme_sub"],
            "harmonic":     ctx["phoneme_harmonic"],
            "shruti":       ctx["phoneme_shruti"],
            "frequency":    ctx["phoneme_harmonic"] * 3 + ctx["phoneme_element"] * 15,
        },
    },
    "parampara": {
        "verified":         ctx["parampara_verified"],
        "channel":          ctx["parampara_channel"],
        "coherence":        ctx["parampara_coherence"],
    },
    "chapter":              ctx["chapter"],
    "chapter_significance": ctx["chapter_significance"],
    "verse":                ctx["verse_info"],
    "matches":              len(ctx["verse_result"].matches),
    "gita_phase":           ctx["gita_phase"],
    "is_complete":          ctx["is_complete"],
    "position":             ctx["position"],
    "guardian":             ctx["guardian"],
    "quarter":              ctx["quarter"],
    "role":                 ctx["role"],
    "quarter_head":         ctx["quarter_head_name"],
    "holy_name":            ctx["holy_name"],
    "trinity_function":     ctx["trinity_function"],
    "diw": {
        "raw":              ctx["diw"],
        "venu":             ctx["diw_comp"].venu,
        "vamsi":            ctx["diw_comp"].vamsi,
        "murali":           ctx["diw_comp"].murali,
    },
    "cell": {
        "header_size":      HEADER_SIZE_BYTES,
        "payload_size":     len(ctx["input_text"].encode("utf-8")),
        "total_size":       HEADER_SIZE_BYTES + len(ctx["input_text"].encode("utf-8")),
        "valid":            True,
        "parampara_verified": ctx["parampara_verified"],
        "prana":            ctx["result_cell"].prana,
        "integrity":        ctx["result_cell"].membrane_integrity / P.COSMIC_FRAME,
        "is_alive":         ctx["result_cell"].is_alive,
        "cycle":            ctx["result_cell"].age,
    },
    "nama": {
        "coords":           ctx["input_coords"],
        "phoneme_count":    len(ctx["input_coords"]),
    },
    "smaranam":             tuple(
        {"sanskrit": rw.word.sanskrit, "meaning": rw.word.first_meaning, "score": rw.total_score}
        for rw in ctx["resonant_words"]
    ),
    "antaranga": {
        "active_slots":     P.get_chamber().antaranga.active_count(),
        "total_prana":      P.get_chamber().antaranga.total_prana(),
        "collisions":       ctx["antaranga_collisions"],
        "size_bytes":       P.get_chamber().antaranga.size_bytes,
    },
    "akash":                lotus._akash,
    "execution": {
        "success":          ctx["result_cell"].is_alive,
        "prana":            ctx["result_cell"].prana,
        "integrity":        ctx["result_cell"].membrane_integrity / P.COSMIC_FRAME,
        "kirtan_cycles":    ctx["kirtan_cycles"],
        "transformations":  ctx["kirtan_cycles"] * P.WORDS,
        "yajna_ticks":      P.WORDS,
        "cycles":           ctx["result_cell"].age,
        "guardian_acted":   ctx["guardian_result"] is not None,
        "guardian_result":  ctx["guardian_result"],
    },
    "yajna": {
        "phase":            ctx["shadow_state"].get("phase"),
        "cycle_count":      ctx["shadow_state"].get("cycle_count", 0),
        "switch_count":     ctx["shadow_state"].get("switch_count", 0),
        "return_count":     ctx["shadow_state"].get("return_count", 0),
        "dissonance":       ctx["shadow_state"].get("dissonance_report"),
    },
    "gate_trace": ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC"),
}
```

## Gate Firing: Automatisch bei Gate-Wechsel

Jede Instruction hat einen Gate-Index. Wenn der sich aendert, feuert die Engine
`_fire_gate()` mit den richtigen ctx-Keys:

```python
_GATE_CONTEXTS = {
    TattvaGate.PARSE:    lambda ctx: {"input_data": ctx["input_data"]},
    TattvaGate.VALIDATE: lambda ctx: {"input_text": ctx["input_text"],
                                       "seed": ctx["seed"],
                                       "input_coords": ctx["input_coords"]},
    TattvaGate.EXECUTE:  lambda ctx: {"seed": ctx["seed"],
                                       "attractor": ctx["attractor"],
                                       "parampara_verified": ctx["parampara_verified"]},
    TattvaGate.RESULT:   lambda ctx: {"attractor": ctx["attractor"],
                                       "resonant_words": ctx.get("resonant_words"),
                                       "verse_result": ctx.get("verse_result")},
    TattvaGate.SYNC:     lambda ctx: {"position": ctx["position"],
                                       "guardian": ctx["guardian"],
                                       "seed": ctx["seed"],
                                       "attractor": ctx["attractor"],
                                       "opcode": ctx.get("pipeline_opcode"),
                                       "guna": ctx.get("pipeline_guna")},
}
```

## Dateien

| Datei | Typ | Zeilen | Inhalt |
|-------|-----|--------|--------|
| `protocols/_navabhakti.py` | NEU | ~100 | NavaBhaktiOp(IntEnum), 12 VAMSI-Adressen, DISPATCH dict, CYCLE tuple, Protocol |
| `substrate/mantra_vm.py` | NEU | ~350 | Engine (execute_cycle) + 12 Wrapper + _build_result + _GATE_CONTEXTS |
| `protocols/diw.py` | MOD | +15 | CONDITION_SHIFT/MASK Konstanten, pack_instruction() |
| `substrate/lotus_core.py` | MOD | +10 | _vm Attribut, __call__ -> VM Delegation |
| `tests/test_mantra_vm.py` | NEU | ~120 | Aequivalenz-Test (Key-by-Key), Step-Isolation-Tests |
| **Summe** | | **~595** | |

## NICHT im PoC

- Condition-Evaluation (Bits 27-30 definiert, nicht implementiert) → Phase 2
- CycleCompiler (custom Cycles aus Protocol-Registrations) → Phase 3
- Antaranga als VM-Register (eigener Slot-Bereich) → Phase 4
- Substrate-Reduktion → Phase 5

## Verifikation

```bash
# 1. Aequivalenz — Jeder der 27 Output-Keys muss identisch sein
python -m pytest tests/test_mantra_vm.py::test_vm_equivalence -v

# 2. Bestehende Tests unberuehrt
python -m pytest vibe_core/mahamantra/tests/ -x

# 3. Ruff
python -m ruff check --select F821,F811 \
    vibe_core/mahamantra/protocols/_navabhakti.py \
    vibe_core/mahamantra/substrate/mantra_vm.py
```

## Was sich NICHT aendert

- 7 Axiome, _seed.py, alle Ableitungen
- THE_FLUTE_CYCLE, VenuOrchestrator
- 5 TattvaGates, 5 Capability Protocols
- Antaranga (bleibt Resonance-Shadow, kein Register-Conflict)
- 16 Guardians, SankirtanChamber
- Alle bestehenden Tests
- Die 9 NavaBhakti-Methoden auf MahamantraLotus (bleiben aufrufbar)
