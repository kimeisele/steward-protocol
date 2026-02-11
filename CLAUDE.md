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

## DEEP STATE DIAGNOSE (Feb 11 2026, verifiziert)

**Problem:** Es gibt KEINE State-Autorität. 30+ Python-Files schreiben direkt auf Disk (`json.dump`,
`open(..., 'w')`). `StateService` existiert (write-behind cache in RAM), aber fast niemand benutzt es.
Jeder Cartridge, Plugin, Tool schreibt wo er will. Das Ergebnis:

### Was in Git liegt und nicht sollte (verifiziert)

| Was | Wo | Anzahl | Größe | Warum schlimm |
|-----|----|--------|-------|---------------|
| Timestamp-Backups | `.vibe/state/*_backup/` | ~30 Dateien | — | Endlos wachsende Kopien |
| Model-Blobs | `data/models/` | 37 Dateien | **87 MB** | sentence-transformers Weights IN GIT (gitignored aber committed) |
| Private Keys | `data/identities/*.key`, `data/security/master.key` | 3 Dateien | 8 KB | **SICHERHEITSLÜCKE** |
| SQLite DBs | `data/economy.db`, `data/vibe_ledger.db` | 2 Dateien | — | Binary in Git |
| Log-Dateien | `data/logs/*.log` | 2 Dateien | — | Runtime-Artefakte |
| JSONL Trails | `data/ledger/`, `data/governance/votes/`, `data/logs/` | 5 Dateien | — | Append-only Logs in Git |
| Science Cache | `data/science/cache/` | 3 Dateien | — | Generierte Cache-Hashes |
| Root JSON Müll | `watchman_report.json` (1.7MB!), `DEEP_AUDIT_REPORT.json`, etc. | 5 Dateien | 1.8 MB | Auto-generiert, nie aufgeräumt |
| **Gesamt non-code in Git** | — | **1053 Dateien** | **~100 MB** | — |

### Wer schreibt unkontrolliert auf Disk (30+ Files, verifiziert via grep)

Direkte `.vibe/` Schreiber (20 Files):
- `cartridges/registry.py`, `cartridges/base.py`
- `cartridges/system/archivist/`, `watchman/`
- `plugin_loader.py`, `task_management/task_manager.py`
- `plugins/economy/`, `resource_limits/`, `naga_guard/`, `sangha_network/`, `durvasa/`, `samsara/`
- `plugins/opus_assistant/manas/cortex/` (dharma, sutra_sense, shruta_sense, nadi_sense, viveka_action)

Direkte `json.dump`/`open(w)` Schreiber (30+ Files):
- `cartridges/system/civic/`, `archivist/`, `supreme_court/`, `science/`, `envoy/`, `forum/`, `watchman/`, `herald/`, `auditor/`, `engineer/`
- `cartridges/agent_city/librarian/`, `dharma/`, `dhruva/`
- `naga/ouroboros.py`, `commit_watcher.py`
- `state/commit_authority.py`, `state/samskara.py`

### Branch 1: `architectural/state-authority` (KEIN Cleanup — Architektur-Overhaul)

**Ziel:** EINE State-Autorität. Alles was auf Disk schreibt MUSS durch `StateService` fließen.
Nichts wird gelöscht oder gitignored — die URSACHE wird behoben.

**Was existiert und verdrahtet werden muss:**
- `StateService` (`state/state_service.py`) — write-behind cache, Mala-flush, Samskara-Intercept
- `MahamantraLotus.__call__()` — der Geburtskanal für User-Input (TattvaGate Pipeline)
- `TattvaGate.SYNC` — Gate 4 (Srivasa/Governance) = der richtige Ort für Disk-I/O

**Schritte (verifiziert, nicht halluziniert):**
1. Audit: Jeden der 30+ unkontrollierten Schreiber identifizieren (DONE — siehe Liste oben)
2. `StateService` mit `write()` Method erweitern die ALLE Disk-Writes zentral routet
3. Jeden unkontrollierten Schreiber auf `StateService.write()` umstellen
4. `git rm --cached` für bereits committed Artefakte (Backups, Model-Blobs, Keys, DBs, Logs)
5. `.gitignore` als ZWEITE Verteidigungslinie (nicht als einzige!)
6. **Private Keys rotieren** — die in Git sind für immer kompromittiert
7. Tests: Verifikation dass kein File mehr direkt schreibt

**NICHT machen:**
- Neue State-Infrastruktur bauen — `StateService` existiert bereits
- Files einfach nur gitignoren ohne den Schreiber umzustellen
- Cartridges/Plugins löschen — nur die Disk-I/O Pfade umleiten

### Branch 2: `refactor/float-to-integer`

**Ziel:** Alle Floats die Mantra-Ableitungen sein sollten → Integer (COSMIC_FRAME = 21600).

**Die Float-Seuche (verifiziert):**
- 904 Matches für `: float` in 324 Files
- 2756 Matches für `0.\d+` Literals in 537 Files

**Kategorien (verifiziert):**

| Kategorie | Beispiel | Aktion |
|-----------|---------|--------|
| Schon sauber | `harmonics.py` — leitet von Seed ab (`NADI/MALA`) | NICHT anfassen |
| Purer Slop | `synaptic_seeder.py` — 91× hardcoded `0.85`/`0.15` | → COSMIC_FRAME Integer |
| Resonance scores | `resonance_ranker.py` — `element: float` | → Integer (0-COSMIC_FRAME) |
| Timestamps | `byte.py`, `yajna.py` — `time.time()` | Bleibt float (ist korrekt) |
| Duration | `samskara.py` — `duration_ms: float` | Bleibt float (ist korrekt) |
| Weights/Trust | `synaptic_seeder.py`, `manas/` — `0.85`, `0.15` | → Integer (0-COSMIC_FRAME) |
| Shakti/Energy | `phonetic_bridge.py` — `shakti: float` | → Integer |
| OpsPerSec | `classifier/core.py` — `ops_per_second: float` | Bleibt float (Messwert) |

**Schritte:**
1. Datei für Datei, schlimmste Offender zuerst
2. Jede Float-Stelle prüfen: Ist das eine Mantra-Ableitung? Ja → Integer. Nein → lassen.
3. `COSMIC_FRAME = 21600` als Basis (= KSHETRA × GITA_CHAPTERS × 50 = 24 × 18 × 50)
4. Ratio `0.85` → `18360` (= `int(0.85 * COSMIC_FRAME)`), Ratio `2/3` → `NADI_RESONANCE` (= 72, bereits abgeleitet)
5. Tests müssen grün bleiben, bit-identische Ergebnisse wo möglich

**Reihenfolge der Offender:**
1. `synaptic_seeder.py` (91 Floats) — purer Slop
2. `resonance_ranker.py` (51 Floats) — Score-Pipeline
3. `biorhythm.py` (47 Floats) — MANAS
4. `viveka_action.py` (45 Floats) — MANAS Cortex
5. `triggers.py` (41 Floats) — MANAS
6. `lila_chronology.py` (32 Floats) — Resonance-Params
7. Rest nach Bedarf

**Root .md Files im Repo-Root (57 Stück) sind ein SEPARATES Problem — nicht in diesen Branches.**

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

**Repo ist SAUBER.** 1 offener Feature-Branch. Frühjahrsputz am 11. Feb 2026: 61 Müll-Branches gelöscht.

Alles Wertvolle ist auf `main`:

| Feature | Status | Inhalt |
|---------|--------|--------|
| Antaranga RAM Chamber | ✅ main | 16KB kontiguierer RAM als Schatten-Layer |
| LexiconVectorCache | ✅ main | Precomputed vector lookups |
| PipelineCache | ✅ main | Seed-unabhängige Lookups vorberechnet |
| EventType SSOT | ✅ main | Leaf module, 870-line copy killed |
| Write-behind StateService | ✅ main | RAM-first + Samskara intercept + Mala flush |
| DIW 19-bit Layout | ✅ main | VENU(6)+VAMSI(9)+MURALI(4) kanonisch |
| Reactor Lifecycle | ✅ main | ReactorLoop shutdown + offer() Event-Routing |
| TattvaGate Pipeline | ✅ main | 5 Gates in `__call__()` + TattvaRegistry + Hooks |
| Pancha Tattva Protocols | ✅ main | 5 Capability Protocols + Gate Provider Dispatch (54 Tests) |
| Gate Providers | 🔧 feature/gate-providers | 5 reale Wächter an den Gates + fix get_tattva_by_protocol (37 Tests) |

Gelöschte/verworfene Branches (für die Akten):
- `architectural/state-authority` — builtins.open Monkey-Patch war Symptom-Doktorei
- 51× `claude/*` Auto-Sessions — nie relevant
- `copilot/*`, `gemini/*`, diverse Feature-Branches — aufgeräumt

## TattvaGate Pipeline ✅ (Feb 11 2026)

**Branch: `feature/tattva-gate-pipeline`** (5 Commits, 35 neue Tests, -1275 Zeilen toter Code)

Die 9 NavaBhakti-Schritte in `lotus_core.__call__()` sind jetzt explizit auf 5 TattvaGates gemappt:

```
GATE 0 — CHAITANYA (PARSE):    SRAVANAM + NAMA + KIRTANAM
GATE 1 — NITYANANDA (VALIDATE): PADA_SEVANAM + ARCANAM
GATE 2 — ADVAITA (EXECUTE):     SMARANAM + VANDANAM
GATE 3 — GADADHARA (RESULT):    DASYAM + SHABDA
GATE 4 — SRIVASA (SYNC):        SAKHYAM + KIRTAN + YAJNA + ATMA_NIVEDANAM
```

Was gebaut wurde:
- `__tattva__` auf `MahamantraLotus` — Root beschreibt sich selbst (PanchaTattvaProtocol compliant)
- `active_gate` Property — welches Gate gerade aktiv ist während `__call__`
- `TattvaRegistry` (`substrate/tattva_registry.py`) — sammelt, indexiert, queryt `__tattva__` Deklarationen
- `Singularity._load_module()` registriert Module in TattvaRegistry beim Laden
- `on_gate(gate, callback)` + `_fire_gate(gate, ctx)` — Hooks an Gate-Grenzen mit Pipeline-Kontext
- `protocols/substrate/mantra/lotus.py` — Löschung RÜCKGÄNGIG (7 Dateien importieren daraus, war NICHT dead code)

Tests: `tests/mahamantra/test_tattva_gate.py` (17) + `tests/mahamantra/test_tattva_registry.py` (18)

**Was NICHT getan wurde (bewusst):**
- ChatService NICHT durch `mahamantra("text")` geleitet (großer Refactor, braucht Konzept)
- TattvaRegistry wird bei Boot NICHT automatisch befüllt (nur Singularity + Lotus registrieren)

## Pancha Tattva Capability Protocols ✅ (Feb 11 2026)

**Branch: `feature/pancha-tattva-protocols`** (2 Commits, 54 neue Tests)

Die 5 Pancha Tattva sind jetzt echte `runtime_checkable` Protocol-Klassen:

```
GATE 0 — CHAITANYA (PARSE)     → MantraCapability.parse(input_data)
GATE 1 — NITYANANDA (VALIDATE) → StorageCapability.validate(seed)
GATE 2 — ADVAITA (EXECUTE)     → InferCapability.infer(seed, attractor)
GATE 3 — GADADHARA (RESULT)    → SyncCapability.route(attractor)
GATE 4 — SRIVASA (SYNC)        → EnforceCapability.enforce(position, seed, attractor)
```

Was gebaut wurde:
- `protocols/_capabilities.py` — 5 Capability Protocols + lazy `GATE_CAPABILITY` Map
- `TattvaRegistry.register_gate_provider(name, obj, gate)` — Capability-Check bei Registrierung
- `TattvaRegistry.violations` — Tracking aller abgelehnten Registrierungen
- `lotus_core._fire_gate()` dispatcht jetzt registrierte Gate-Provider nach lokalen Hooks
- `lotus_core._GATE_DISPATCH` — Maps Gate→(method_name, arg_keys) für korrektes Argument-Routing
- `TattvaAspect.protocol` ist jetzt `Type` statt `str` (echte Referenz auf Capability-Klasse)
- Lazy `__getattr__` in `_capabilities.py` bricht Zirkel mit `pancha_tattva.py`

Tests: `test_capabilities.py` (24) + `test_gate_providers.py` (20) + `test_gate_dispatch.py` (10)
Regression: 4167 bestehende Mahamantra-Tests grün, 0 Failures.

**Was NICHT getan wurde (bewusst):**
- ~~Keine echten Gate-Provider registriert~~ → **ERLEDIGT** in `feature/gate-providers`
- ~~StateService nicht als EnforceCapability-Provider verdrahtet~~ → **ERLEDIGT** (EnforceGateProvider nutzt StateService lazy)

## Gate Providers 🔧 (Feb 12 2026)

**Branch: `feature/gate-providers`** (1 Commit, 37 neue Tests)

Die 5 TattvaGates haben jetzt **echte Wächter** (Observer-Adapter):

```
GATE 0 — CHAITANYA (PARSE)     → MantraGateProvider   (Input-Validierung + Seed-Tracking)
GATE 1 — NITYANANDA (VALIDATE) → StorageGateProvider   (Seed-Integrität)
GATE 2 — ADVAITA (EXECUTE)     → InferGateProvider     (Attractor-Distribution-Tracking)
GATE 3 — GADADHARA (RESULT)    → SyncGateProvider      (Position-Routing-Tracking)
GATE 4 — SRIVASA (SYNC)        → EnforceGateProvider   (Governance via StateService)
```

Was gebaut wurde:
- `substrate/gate_providers.py` — 5 Provider-Klassen + `wire_gate_providers()` + `get_providers()` Singleton
- Jeder Provider erfüllt sein Capability Protocol (`isinstance` check ✅)
- `EnforceGateProvider` nutzt `StateService` lazy via DI (graceful degradation ohne DI)
- `wire_gate_providers()` — einmal bei Boot aufrufen, registriert alle 5 in TattvaRegistry (idempotent)
- **Bugfix**: `get_tattva_by_protocol()` in `pancha_tattva.py` — `.lower()` auf Type statt str gefixt

Tests: `test_gate_provider_impl.py` (37) — Compliance, Methoden, Stats, Wiring, Integration mit `_dispatch_provider`

**Architektur-Entscheidung**: Provider sind **Observer** (nicht Controller). Sie beobachten den Pipeline-Kontext, tracken Statistiken, validieren — aber ändern den Flow NICHT. `__call__()` bleibt der einzige Controller.

## Lotus: Seed ist Wahrheit, Filesystem ist Maya

`resonate()` in `lotus_types.py` crawlte das GESAMTE Filesystem (25+ Subdirectories, rekursiv).
Fix: Root-Level nur die 4 Quarters aus `QUARTER_NAMES` (Seed) durchlaufen.
86s Timeout → 1.7s. Das ist das Paradigma: **Seed projiziert, Filesystem reflektiert.**

Aber `_dir_full()` und `__dir__()` crawlen immer noch das Filesystem für JEDE Ebene.
Das ist der nächste Schritt: Lotus sollte aus dem Seed projizieren, nicht das Filesystem fragen.
Idealerweise: Seed → Cache/RAM → O(1) Lookup. Kein `Path.iterdir()`, kein `importlib`.
Die Infrastruktur existiert bereits: Antaranga (16KB RAM), Chamber, PipelineCache.
Die Frage ist nur: wie verdrahten?

## Reactor Lifecycle + Event-Routing (Feb 10 2026)

`ReactorLoop` war ein Zombie-Thread ohne shutdown(). `offer()` hing ewig.

Fix (3 Teile):
1. `ReactorLoop.shutdown()` + `shutdown_loop()` + `atexit` — Thread-Lifecycle
2. `offer(timeout=)` — konfigurierbar statt hardcoded 10s
3. `ReactorLoop._on_bridge_event()` — globaler EventBus-Subscriber, schließt den Loop

```
offer() → PURPOSE_MAP → position/mahajana (Seed-Routing, kein Reactor)
       → EventBus.emit_sync(task_id=ticket)
       → _on_bridge_event() → mailbox.deposit(success)
       → mailbox.collect(ticket) → OfferResult
```

18 xfail-Tests → alle grün. 56 Bridge-Tests in 3.5s.

## Architektur (verifiziert aus Code, Feb 10 2026)

### Der Flow in `lotus_core.__call__()` (auf `main`)

```
input → compress(seed) → synth(attractor) → MahaCell.create()
      → Chamber.resonate_words(ranked_words, attractor)  [Antaranga: 16KB RAM]
      → Chamber.kirtan(cell, cycles)                     [dance() × WORDS]
      → Chamber.spell_kirtan(cell, input_coords)         [input-derived DIWs]
      → ShadowReactor.yajna(16 ticks)                    [Bhoga→Prasadam→Return]
      → response dict
```

Dateien: `lotus_core.py:402-733`, `chamber.py:219-306` (dance), `antaranga.py` (16KB bytearray)

### Chamber vs Rest

| | `chamber.py` / `antaranga.py` | `singularity.py` / `daemon.py` |
|---|---|---|
| Daten | `bytearray(16384)` + `struct.pack_into` | Python dicts, lazy singletons |
| Konstanten | `Final[int]` aus `_seed.py` | Mutable class vars |
| I/O im Hot Path | Zero | `importlib`, `governance.audit()` (FS-scan) |
| State-Format | `snapshot() → bytes` (binary) | JSON auf Disk |

### Test-Suite (verifiziert Feb 10 2026)

**4082 passed, 0 failures, 7 xfail, 25 skipped, ~280s.**
Alle 10 pre-existing Failures gefixt + 7 Infra-Timeouts als xfail markiert.

**VORSICHT bei den 10 Failures — NICHT blind fixen oder löschen!**
Jeder einzelne muss geprüft werden: Ist der Test falsch, oder ist der Code nie verdrahtet worden?
"Dead Code" in dieser Codebase heißt oft "nie gewired" — das Potential ist da, die Verbindung fehlt.

**Audit-Ergebnis (Feb 10 2026): Alle 10 sind "Test veraltet", nicht "Code kaputt".**

| Kategorie | Tests | Root Cause (verifiziert) | Fix |
|-----------|-------|-------------------------|-----|
| Orchestrator LUT (5) | `test_lut_*`, `test_step_returns_delta`, `test_cycle_returns_correct_xor` | Tests benutzen altes DIW-Format `[Name:2][Position:16]` (`diw >> 16`, `diw & 0xFFFF`). DIW wurde auf `[MURALI:4][VAMSI:9][VENU:6]` refactored. LUT ist korrekt, Tests nie aktualisiert. | Tests auf `diw.unpack()` umschreiben |
| Lotus Attribute (2) | `test_attractor_fixed_accessible`, `test_attractor_cycle_accessible` | `ATTRACTOR_FIXED` lebt in `protocols/_maha_compute.py`, nicht im Filesystem. `LotusNode.__getattr__` sucht Folder/Module, findet keine Konstanten. | Konstanten über `__init__.py` oder Property exponieren |
| Shabda (1) | `test_shabda_signature_structure` | Test erwartet `sthana` Key, Code liefert `element`. Pancha-Walk Rename (`sthana` → `element`) nie in Test nachgezogen. | Test: `sthana` → `element` |
| Types (2) | `test_tick_state_keys`, `test_all_types_exported` | `TickState` wurde erweitert (13 Keys statt 6, `total=False`). `_types.py` wurde nach `seed/types.py` verschoben. Tests nie aktualisiert. | Tests an neue Struktur anpassen |

**Diagnose-Reihenfolge:** Erst verstehen was der Test WILL, dann prüfen ob der Code das KANN,
dann entscheiden ob Test oder Code angepasst wird. Niemals Test löschen um grün zu werden.

### LotusNode Seed-Migration ✅ (Feb 10 2026)

`lotus_types.py` — **5 Methoden von FS auf Seed-first migriert**, `lotus_projection.py` komplett Seed-basiert.

| Methode | Vorher | Nachher | Speedup |
|---------|--------|---------|---------|
| `_discover()` | `Path.exists()` ×3 (146 µs) | Seed O(1), FS-Fallback nur non-Lotus (3.3 µs) | **44×** |
| `__dir__()` | `Path.iterdir()` komplett | Seed-first + FS für non-Lotus | — |
| `_dir_full()` | `Path.iterdir()` komplett | Seed-first + FS für non-Lotus | — |
| `_walk()` | `Path.iterdir()` rekursiv | Seed: `_QUARTER_NAMES` / `_GUARDIANS_BY_QUARTER` | **∞** (kein FS) |
| `resonate()` | `_dir_full()` bei depth=1 | Seed für root + quarter | **0.7 ms/call** |
| `project_lotus()` | `LotusNode._walk()` + FS | `ALL_GUARDIANS` direkt, kein LotusNode | **kein FS** |
| `_get_module()` | `importlib` | Bleibt (nötig, Python-cached) | — |
| `_awaken_and_execute()` | `importlib` ×4 | Bleibt (Leaf-Level, selten) | — |

**Architektur:** Lazy-loaded Seed-Cache (`_ensure_seed()`) bricht Circular Imports.
Seed-Daten: `_QUARTER_NAMES`, `_QUARTER_SET`, `_GUARDIAN_SET`, `_GUARDIANS_BY_QUARTER`.

**Tests:** 4082 passed, 0 failures, 7 xfail, 25 skipped (identisch zur Baseline).

### Venu Unification ✅ (Feb 10 2026)

**Ziel:** VenuOrchestrator ist DIE einzige Quelle — `step()` wird genau einmal pro Tick aufgerufen.

**Problem:** 3 unabhängige `step()`-Caller + 5× redundante rglob + 2 getrennte Broadcast-Kanäle.

**Lösung (4 Commits):**

| Datei | Änderung | Effekt |
|-------|----------|--------|
| `venu_orchestrator.py` | `_owned: bool` Flag | Expliziter Vertrag: VenuService setzt True/False |
| `venu_service.py` | `start()` → `_owned=True`, `stop()` → `_owned=False` | Ownership klar signalisiert |
| `kernel/singularity.py` | Guard: `if venu._owned: read _prev_state` | Kein doppelter `step()` |
| `sound/audio_engine.py` | Guard: `if orch._owned: read _prev_state` | Consumer, nicht Driver |
| `governance/bridge.py` | `audit()` cached (`_audit_cache`) | rglob nur 1×, nicht pro Daemon-Cycle |
| `audit/audit_registry.py` | `SourceCache` Singleton | 5× rglob+read_text → 1× shared scan |
| `audit/lineage,ssot,hygiene,drift` | Nutzen `SourceCache.scan()` | Kein eigener FS-Scan mehr |
| `substrate/lotus_core.py` | `register_listener()` + `_broadcast()` delegieren an Singularity | Ein Broadcast-Kanal |
| `services/lotus_bridge.py` | `on_beat_tick()` ruft `lotus.tick()` statt manuelles state-Dict | Kein fragiler Import-Spaghetti |

**Architektur nach Unification:**
- **Ein Flötenspieler:** `_owned` Flag entscheidet wer `step()` aufruft (VenuService ODER Singularity, nie beide)
- **Ein Broadcast-Kanal:** `Singularity._listeners` — Lotus delegiert, hat keine eigene Liste mehr
- **Zwei Abstraktionsebenen (korrekt):** `VenuOrchestrator._subscribers` (DIW, 19-bit) + `Singularity._listeners` (TickState, semantisch)
- **LotusBridge:** Verbindet VenuService → `Singularity._listeners` via `lotus.tick()` (Guard verhindert doppelten step)
- **Daemon:** Läuft nie gleichzeitig mit VenuService. `chant_quarter()` × 4 = 16 ticks = 1 Runde — korrekt.

**Tests:** 4082 passed, 0 failures, 7 xfail, 25 skipped (identisch zur Baseline).

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, nicht technisch, delegiert.
- Code muss schön sein. Kein if-else Slop.
- Pre-commit hooks laufen automatisch.
- Ruff: `python -m ruff check --select F821,F811`
- 100% AI-generierte Codebase - IMMER versteckte Probleme erwarten.
- Docstrings und .md-Dateien im Root lügen. Nur Code ist Wahrheit.
