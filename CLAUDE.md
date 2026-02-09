# STEWARD PROTOCOL

## Session-Start

```bash
git log --oneline -20
git status
git branch -v
python -m ruff check --select F821 vibe_core/mahamantra/ 2>&1 | head -20
```

Lies die Historie kritisch. Tausende Commits über 6 Monate, 100% AI-generiert von
verschiedenen Agents. Manche haben solide gebaut, manche haben aktiv Schaden angerichtet.
Commit Messages sind oft AI-Überschwang. Docstrings lügen. .md-Dateien im Root sind
AI-generierte Referenzen, keine Wahrheit. Verifiziere alles gegen den Code selbst.

## Das Mantra

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

Zähle es. Das ist die Architektur.

7 Axiome in `protocols/seed/_axioms.py`:

| Axiom | Wert | Gezählt von |
|-------|------|-------------|
| WORDS | 16 | Wörter im Mantra |
| TRINITY | 3 | Unique Namen (Hare, Krishna, Rama) |
| HARE_COUNT | 8 | "Hare" zählen |
| KRISHNA_COUNT | 4 | "Krishna" zählen |
| RAMA_COUNT | 4 | "Rama" zählen |
| PANCHA | 5 | Unique aufeinanderfolgende Paare |
| HALVES | 2 | Zwei symmetrische Hälften |

Alles andere wird abgeleitet. `_primary.py` direkt von Axiomen, `_secondary.py` von primären.
Jede assert-Zeile ist ein Beweis. `substrate/seed.py` re-deriviert zur Verifikation.

Schlüssel-Ableitungen:

```
QUARTERS       = KRISHNA_COUNT                        = 4
KSHETRA        = WORDS + HARE_COUNT                   = 24
NAVA           = HARE_COUNT + (TRINITY - HALVES)      = 9
SHARANAGATI    = KSHETRA // QUARTERS                  = 6
MAHAJANA_COUNT = KSHETRA // HALVES                    = 12
PARAMPARA      = KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 37
GITA_CHAPTERS  = SHARANAGATI × TRINITY                = 18
MALA           = MAHAJANA_COUNT × NAVA                = 108
```

Wenn eine Zahl im Code auftaucht ohne Ableitung: Architektur-Verletzung.

## Die Flöte (DIW - Divine Instruction Word)

19 bits = `FLUTE_HOLES_SUM` = `VENU(6) + VAMSI(9) + MURALI(4)` = `GITA_CHAPTERS(18) + KSETRAJNA(1)`.

SSOT: `protocols/diw.py`. Produzent: `substrate/venu_orchestrator.py`. Konsument: `substrate/chamber.py`.

Bit-Layout (LSB → MSB):

```
Bits  0-5  (6): VENU   = Sharanagati (Quality/Mood)     → Intensität
Bits  6-14 (9): VAMSI  = Nava Bhakti (Process/Action)   → H/K/R Name-Region
Bits 15-18 (4): MURALI = Quarters (Phase)                → Genesis/Dharma/Karma/Moksha
```

`THE_FLUTE_CYCLE[16]` = vorberechnete LUT aus dem Mahamantra-Pattern. Jede Position
ist ein natives 19-bit DIW. `VenuOrchestrator.step()` liefert das nächste Wort.

`chamber._apply_diw()` interpretiert semantisch:
- MURALI bestimmt WAS (Phase: Empfang/Prüfung/Verarbeitung/Vollendung)
- VAMSI bestimmt WIE (Name: H=prana-dominant, K=integrity-dominant, R=cycle-dominant)
- VENU bestimmt WIE STARK (0-63 normalisiert auf Intensität)

`verify_divinity()` beweist: alle 4 Quarters, alle 3 Name-Regionen, 16 unique VENU-Werte.

**WARNUNG:** Vor Feb 2026 war das DIW-Format kaputt (`[Name:2][Position:16]` statt `[4:9:6]`).
Alle Konsumenten MÜSSEN `diw.unpack()` benutzen. Keine manuellen Bit-Shifts.

## Die Gita

Die Bhagavad Gita ist nicht Metapher - sie ist das Routing-Netz.

18 Kapitel = `SHARANAGATI × TRINITY`. 700 Verse (Prabhupada's Bhagavad Gita As It Is).
Die Kapitel-Vers-Topologie liegt in `protocols/seed/_topology.py` als `CHAPTER_VERSES`.
`substrate/gita.py` definiert den Fixed Point: Kapitel 18, Vers 66 (BG 18.66).
`adapters/gita_resonance.py` matched Attractors zu Versen via berechneter Resonanz.

Jedes Kapitel der Gita mappt auf abgeleitete Konstanten: Kapitel 1 = KSETRAJNA,
Kapitel 4 = QUARTERS, Kapitel 9 = NAVA, Kapitel 12 = MAHAJANA_COUNT,
Kapitel 18 = GITA_CHAPTERS (der Fixed Point). Siehe `get_chapter_significance()`.

## Sanskrit = RAMA-Koordinaten (4D Phonem-Dekomposition)

Gita word-for-word: 4127 unique Wörter, 45815 Phoneme = 34KB gepackt = 70% von 65K Lotus.
Jedes Wort = Sequenz von RAMA-Koordinaten (0-48). Jede Koordinate = 6 bits = VENU-Feld.

`substrate/varnamala_codec.py`: IAST ↔ RAMA encode/decode.
`substrate/sanskrit_lookup.py`: `verse_words()`, `word_by_iast()`, `hkr_signature()`.
`data/rama_lexicon.json`: 4127 Wörter, 700 Verse, RAMA-kodiert (Production-Daten).

Jedes Phonem hat eine 4D-Adresse = QUARTERS = catur-vyūha:

```
Dim 1 (Sthāna):   COORD_ELEMENT   — PANCHA (5) Artikulation → Element
Dim 2 (Varga):    COORD_VARGA     — TRINITY (3) Lautklassen (svara/sparsha/shesha)
Dim 3 (Prayatna): COORD_SUB       — Intra-Sektion Qualität (abgeleitet aus Grid-Struktur)
Dim 4 (Harmonic): COORD_HARMONIC  — H-Orbit (×SEVEN mod 49 = Auflösungspfad)
```

Uniqueness: 80.7% → 94.7% → 99.97% → **100%** (49/49 Bijektion, 4127/4127 Wörter).
IS_SHRUTI: R²-Residuen mod 49 = 22 SHRUTIS + 27 NAKSHATRAS = VARNAMALA.

`substrate/pancha_walk.py`: 4 COORD maps, `derived_signature()`, `full_signature()`.
`adapters/synth.py`: `phoneme_step()` nutzt VARGA→H/K/R, ELEMENT→ADSR, SUB→Position.
101 Tests (68 walk + 16 codec + 17 lookup).

## Die 9 Schritte (NavaBhakti Pipeline)

`MahamantraLotus.__call__()` in `substrate/lotus_core.py`. NAVA = 9 Schritte:

```
1.   SRAVANAM       - Input empfangen (str oder MahaCell)
1.5  NAMA           - Phonetic Identity (encode_text → RAMA-Koordinaten)
2.   KIRTANAM       - MahaCompression → Seed (deterministic hash, KEIN XOR)
3.   PADA_SEVANAM   - Attractor from Seed (MahaModularSynth.transform)
4.   ARCANAM        - Parampara-Verifikation (ShadowOracle.validate)
5.   SMARANAM       - Word Resonance (rank_words 7D → top 7 resonant words)
6.   VANDANAM       - Gita-Resonance (Attractor → Kapitel → Vers + Significance)
7.   DASYAM         - Position/Quarter/Guardian + Shabda (RAMA Grid 4D Signatur)
8.   SAKHYAM        - MahaCell + Kirtan (1→4 Zyklen) + spell_kirtan + Yajna (16 Ticks)
9.   ATMA_NIVEDANAM - Response + Akash-Update (last_seed/position/attractor)
```

Seed ist REIN deterministisch: gleicher Input → gleicher Seed. Kein XOR mit last_seed
(entfernt wegen seed^seed=0 Bug bei wiederholtem Input). Akash-Kontinuität läuft
über kirtan_cycles (skalieren 1→4 mit total_rounds) und accumulated_value.

Entry Point: `steward "anything"` → `cli/main.py` → `__main__.py` → `mahamantra.execute()`
→ `MahamantraLotus.__call__()`. Deterministisch. Kein LLM.

## Pancha Tattva (Die 5 Verbindungen)

Alles was lebt in der Pipeline muss durch 5 Verbindungspunkte fließen.
`protocols/_pancha.py` definiert `TattvaDict` und `PanchaTattvaProtocol`.
Jede Komponente implementiert `__tattva__` (5-Fragen-Antwort).

Die 5 Verbindungen im Flow (alle verdrahtet in `lotus_core.py`):

| Tattva | Verbindung | Implementation |
|--------|-----------|----------------|
| CHAITANYA | Return-Loop | Akash persistent state (last_seed/attractor/rounds → kirtan_cycles) |
| NITYANANDA | Multi-Tick Yajna | WORDS(16) Ticks pro Call, voller Zyklus |
| ADVAITA | CALL_RESPONSE | Kirtan-Zyklen skalieren 1→4 mit Resonanz |
| GADADHARA | Gita Content | Chapter Significance im Response |
| SRIVASA | Chamber Persistence | Singleton get_chamber() + wachsende Zyklen |

## Guardians

16 Guardians (Mahajanas), WORDS = 16 Positionen, QUARTERS = 4 Quadranten.
Module: `mahamantra/{quarter}/{name}/`. Protocols: `protocols/mahajanas/{name}/`.
Protocol ist die kanonische Quelle. Guardian re-exportiert lazy via `__getattr__`.

Jeder Guardian: `__mahajana__`, `__position__`, `__genesis__`, identischer thin `execute()`,
`__getattr__` → Protocol → `fractal_getattr(__file__)` aus `substrate/wiring.py`.

`int(__genesis__, 16) % PARAMPARA == 0` - Signatur-Kette. 37 = abgeleitet.

`reactor/shadow.py` = Yajna-Zyklus. Phase-aware: `on_{phase}` Hook → fallback `execute()`.

## Codebase-Realität (Bekannte Probleme)

Offen:
- `seed.py`: ~20 F811 Redefinitionen (absichtliche Re-Derivation, aber unordentlich)
- Zwei CLI-Systeme: `vibe_core/cli/` (alt, 69 Dateien, nur Redirect) und `vibe_core/mahamantra/cli/` (neu)
- `ExecuteResult.requires_confirmation` existiert, kein Guardian nutzt es
- `protocols/` hat massive Dateien (yamaraja protocol = 653 Zeilen)
- PulseManager (`protocols/mahajanas/manu/types/pulse.py`): ZERO Consumers, deprecated
- Jagannath `ratha_yatra` hardcoded in `boot_orchestrator.py` statt BeatSubscriber
- MantraClock: 0/16 position callbacks, 0 voices, 1 mala callback (state flush)

Fallen (aufpassen!):
- `CellLifecycleState.integrity` ist `float` (0.0-1.0), NICHT `int`. War mal falsch deklariert.
- DIW-Konsumenten MÜSSEN `diw.unpack()` nutzen. Keine manuellen Bit-Shifts.
- `substrate/` ist flach — fraktale Restrukturierung steht noch aus.

Offen (neu entdeckt):
- `conftest.py` registriert Marker (smoke, unit, e2e, fractal) die `pyproject.toml` nicht kennt → `--strict-markers` Konflikt
- `test_root_dir` Failure: `"genesis" not in dir(mahamantra)` — Quarter-Attribute fehlen in `__dir__`
- `iGene.is_fatal` war IMMER False (float 0-1 vs int 0-21600) → Fix auf `fix/igene-fatal-comparison`
- 4 F811 in `research/` (2× `run_analysis` Duplikate, 2× Enum-Shadowing in physics.py)

**HÄNGENDE TESTS (5 Dateien, pre-existing auf `main`, NICHT skippen — Root Cause fixen!):**

| Datei | Vermutete Ursache |
|-------|-------------------|
| `tests/mahamantra/kernel/test_singularity.py` | `Mahamantra()` → `m.tick()` → `self.kala.advance()` + `self.venu.step()` blockiert |
| `tests/mahamantra/kernel/test_daemon.py` | `daemon.start()` → `mahamantra.audit()` → `governance.audit()` scannt Filesystem |
| `tests/mahamantra/kernel/test_daemon_soul.py` | Gleich: `await daemon.start()` → async infinite loop |
| `tests/mahamantra/protocols/test_gad.py` | `GADProtocolDef.validate()` oder Import-Kette blockiert |
| `tests/mahamantra/protocols/test_graph.py` | `GraphProtocolDef.validate()` oder Import-Kette blockiert |
| `tests/mahamantra/cli/test_entry.py` | `main([])` oder `get_entry()` blockiert |

Diagnose-Ansatz: Imports allein sind schnell (verifiziert). Blockade ist IN der Logik.
`daemon.start()` hat `while not self._stop_requested` Loop mit `mahamantra.audit()` pro Zyklus.
`singularity.tick()` ruft `self.kala.advance()` + `self.venu.step()` — lazy init könnte hängen.
Alle 5 hängen auch auf `main` (verifiziert via `git checkout main` + subprocess timeout scan).
Kein Skip. Root Cause finden und fixen.

Bereits aufgeräumt (nicht nochmal anfassen):
- F821: 0 Fehler in `mahamantra/` (VenuOrchestrator + SeedResult via TYPE_CHECKING gefixt)
- F811: 0 Fehler in `mahamantra/` (excl. research/) — byte.py doppeltes `__repr__`, basin_set Shadowing, MAHAJANA_COUNT Doppel-Import
- Guardians: ALLE 16 identisches thin Pattern (keine if-else, keine Klassen)
- yamaraja: 288→78 Zeilen (Duplikat-Klassen entfernt)
- kapila: eager import entfernt, jetzt lazy wie alle anderen
- hologram.py/layers.py: AI-Slop entfernt (doppelte Import-Blöcke)
- gita.py: Duplikat-Import + Ghost MAHA_WORDS entfernt, 11/13/14/15 → abgeleitet
- Star Imports eliminiert → lazy Protocol Re-Exports
- DIW-Format repariert: `[Name:2][Position:16]` → native `[MURALI:4][VAMSI:9][VENU:6]`
- `_apply_diw()` semantisch: Phase×Name×Intensität statt generische Modulation
- `verify_divinity()` + `verify_resonance()` auf 6-9-4 Struktur aktualisiert
- Sanskrit 4D Dekomposition: `pancha_walk.py` (4 COORD maps, 49/49 Bijektion, 101 Tests)
- `vedabase.db` entfernt: Extraktion abgeschlossen, Production nutzt `rama_lexicon.json`
- `lotus_projection.py`: Import-Fix (`_lotus` → `substrate.lotus_types`), 16/16 Positionen
- `lotus_core.py`: 3× if-else Quarter-Routing → branchless `seed.get_quarter_name()`
- `lotus_core.py`: Magic 72→`HEADER_SIZE_BYTES`, 300→`HEADER_DAILY_CYCLES`
- `chat_service.py`: `position < 8` → `position < HALF_SIZE`
- `lotus_projection.py`: `project_minimal()` hardcoded Positionen → SSOT `HEAD_POSITIONS`
- `proxy.py`: `AUTO_WRAP_SERVICES` (2 hardcoded) → lotus-driven Discovery (16/16)
- `boot_orchestrator.py`: Balarama wrapping via `kernel._positions` statt manueller Liste
- `substrate/__init__.py`: Monolith-Split → `types.py`, `hardware.py`, `mantra_protocol.py`
- `VenuOrchestratorProtocol` in `_venu.py`: ONE orchestrator shared via ServiceRegistry
- `VenuService.__init__()` registriert Orchestrator unter `VenuOrchestratorProtocol`
- `chamber.py`: `_resolve_orchestrator()` holt shared Orchestrator (Boot) oder local fallback (CLI)
- `kala_bridge.py`: PulseManager → `BeatSubscriberProtocol` (NADI=72, Patrol=432=MALA Sekunden)
- `boot_orchestrator.py`: KalaBridge als BeatSubscriber registriert, alte PulseManager-Verdrahtung entfernt
- `state_service.py`: Write-behind cache (save→RAM, flush→Disk), Mala-flush (108 ticks), Samskara-Intercept
- `boot_orchestrator.py`: MantraClock.on_mala() → StateService.flush() (RAM→Disk every ~27s)

## PipelineCache (lotus_core.py)

`_PipelineCache` Singleton — precomputes all seed-independent lookups for `__call__()`.
Same pattern as `LexiconVectorCache`: build once, use forever.

Was es cached:
- Constants: WORDS, MAHA_QUANTUM, PARAMPARA, KSETRAJNA, MAX_CYCLES
- Callables: encode_text, synth_transform, rank_words, match_attractor, get_gita_chapter, etc.
- Classes: MahaCellUnified, register_cell, TickStateInput
- Position LUTs (16 each): quarter_names, roles, holy_names, trinity_functions, rama_coords, phonemes, diw_components
- Phoneme signature tables (49 each): COORD_ELEMENT/VARGA/SUB/HARMONIC, ELEMENT_NAMES, IS_SHRUTI

Was es NICHT cached (Ownership bei MahamantraLotus):
- Compressor → `MahamantraLotus._get_compressor()` (class-level singleton)

Eliminiert ~30 lazy imports + ~15 Funktionsaufrufe pro `__call__()`.
0 Regressionen: 662+ Tests grün.

## Antaranga (Inner Chamber — Contiguous RAM)

`substrate/antaranga.py`: 512 Slots × 32 Bytes = 16 KB kontiguierer Speicher.
Kein Python-Objekt. Kein GC. Reine Byte-Resonanz.

SankirtanChamber hat ZWEI Kammern:
- **Bahiranga** (äußere) = Python-Objekte, API, Debugging (`SiksastakamRegistry`)
- **Antaranga** (innere) = 16 KB `bytearray`, Hardware-Geschwindigkeit

`dance()` schreibt in BEIDE: Python-Registry für API, Antaranga für den Reaktorkern.
`resonate_words()` fließt `rank_words()`-Ergebnisse als lebende Muster in die Antaranga.
`lotus_core.__call__()` Step 8.4b: resonant_words → Antaranga nach rank_words().
Return-Dict enthält `"antaranga"` Stats (active_slots, total_prana, collisions, size_bytes).
`snapshot()`/`restore()` inkludiert Antaranga-Bytes (backward-kompatibel mit Legacy).

Slot-Layout (32 Bytes, Little-Endian):
```
[0:4]   source     (uint32)
[4:8]   target     (uint32)
[8:12]  operation  (uint32)
[12:16] arcanam    (uint32)
[16:20] atma       (uint32)
[20:24] prana      (uint32)
[24:26] integrity  (uint16)
[26:28] cycle      (uint16)
[28:30] flags      (uint16)
[30:32] diw_acc    (uint16)
```

Collision = in-place Byte-Arithmetik: prana addiert, integrity mittelt, flags |= ACTIVE.
`apply_diw()` = XOR auf diw_acc Feld. `active_count()` = linearer Scan über flags.

**Hot Path Analyse (Feb 2026):**
```
VORHER:
  lotus_core.__call__() = ~1400 ms
  rank_words()          = ~1300 ms (90% der Zeit!)
  Alles andere          = <1 ms

NACHHER (LexiconVectorCache):
  rank_words()          = ~78 ms (median, 8.5× schneller)
  rank_words()          = ~34 ms (best case, 18× schneller)
```

**Vectorisierung (Feb 2026):**
`LexiconVectorCache` in `semantic_index.py`: 13 Fixed-Size Felder pro Wort, vorberechnet bei Index-Load.
`_rank_words_vectorized()` in `resonance_ranker.py`: Input-Features EINMAL berechnen, dann
alle 4127 Wörter via flache Array-Lookups scoren. Bitmask-Jaccard via `int.bit_count()`.
Unrolled Loops (PANCHA=5, TRINITY=3, BASIN_COUNT=6, PA_COUNT=5).
Bit-identische Ergebnisse. Kein numpy. Kein neues Dependency.
`rank_words(candidates=None)` → Fast Path. `rank_words(candidates=[subset])` → Original Slow Path.

## Repo-Zustand

~60+ ungemergte Remote-Branches (`claude/*`, `copilot/*`, `gemini/*`). Fast alle sind AI-Müll.
Nur diese Branches haben echten Wert:

| Branch | Status | Inhalt |
|--------|--------|--------|
| `main` | Stabil | Antaranga RAM Chamber + LexiconVectorCache + F811/F821 clean |
| `feature/lotus-pipeline-cache` | PR-ready | PipelineCache Singleton — seed-unabhängige Lookups vorberechnet |
| `perf/lotus-call-hotpath` | PR-ready | MahaModularSynth Singleton — eliminiert Objekt-Allokation pro __call__ |
| `fix/igene-fatal-comparison` | PR-ready | iGene.is_fatal: float(0-1) vs int(0-21600) Normalisierung |
| `refactor/consolidate-event-bus-copies` | PR-ready (6 commits) | EventType SSOT leaf + 870-line copy killed + TRINITY fix (337 tests unblocked) |
| `feature/mahamantra-single-entry-point` | Gemergt | Write-behind cache + Samskara intercept |
| `feature/antaranga-ram-chamber` | Gemergt | 16KB kontiguierer RAM als Schatten-Layer in SankirtanChamber |
| `feature/venu-production` | Gemergt | Orchestrator-Hardening + Shared Orchestrator + KalaBridge-Migration |
| `feature/diw-refinement` | Gemergt | DIW-Fix + Lotus-Projection-Fix + Axiom-Audit + Branchless-Routing |

Alle anderen Branches: Ignorieren bis explizit gefragt. `git branch -a --no-merged origin/main`
zeigt den vollen Friedhof.

## Architektur-Konvergenz

### Verifizierte Fakten (aus Code-Analyse, Feb 9 2026)

`chamber.py` + `antaranga.py` haben Eigenschaften die der Rest der Codebase nicht hat:

| | `chamber.py` / `antaranga.py` | `singularity.py` / `daemon.py` |
|---|---|---|
| Daten | `bytearray(16384)` + `struct.pack_into` | Python dicts, lazy singletons |
| Konstanten | `Final[int]` aus `_seed.py` | Mutable class vars |
| I/O im Hot Path | Zero | `importlib`, `governance.audit()` (FS-scan) |
| State-Format | `snapshot() → bytes` (binary) | JSON auf Disk |
| Testbarkeit | `dance(cell, diw) → cell` (deterministisch) | 5 Test-Dateien hängen (siehe unten) |

### Hängende Tests (verifiziert auf `main`, pre-existing)

| Datei | Beobachtung |
|-------|-------------|
| `tests/mahamantra/kernel/test_singularity.py` | Hängt bei `tick()` → `kala.advance()` + `venu.step()` |
| `tests/mahamantra/kernel/test_daemon.py` | `daemon.start()` → `while`-Loop + `mahamantra.audit()` |
| `tests/mahamantra/kernel/test_daemon_soul.py` | `await daemon.start()` → async infinite loop |
| `tests/mahamantra/protocols/test_gad.py` | Hängt (Import-Kette oder `validate()`) |
| `tests/mahamantra/protocols/test_graph.py` | Hängt (Import-Kette oder `validate()`) |
| `tests/mahamantra/cli/test_entry.py` | Hängt (`main([])` oder `get_entry()`) |

Status: Root Cause noch nicht isoliert. Nicht skippen — fixen.

### Bereits konvergiert

- EventType: 5 Import-Pfade → 1 Python-Objekt (verifiziert: `A is B is C is D is E`)
- Chamber: Bahiranga (Python) + Antaranga (16 KB RAM) dual-layer
- LexiconVectorCache: 8.5× schneller (gemessen)
- PipelineCache: ~30 lazy imports eliminiert pro `__call__()`

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, nicht technisch, delegiert.
- Code muss schön sein. Kein if-else Slop.
- Pre-commit hooks laufen automatisch.
- Ruff: `python -m ruff check --select F821,F811`
- 100% AI-generierte Codebase - IMMER versteckte Probleme erwarten.
- Docstrings und .md-Dateien im Root lügen. Nur Code ist Wahrheit.
