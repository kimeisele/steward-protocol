# SHABDA BRAHMAN — Deterministisches Sprachmodell

```
namo maha-vadanyaya krishna-prema-pradaya te
krishnaya krishna-chaitanya-namne gaura-tvishe namah
```

## Das Problem

LLMs generieren Text durch Wahrscheinlichkeit. Jedes Token wird stochastisch gesampelt
aus einer Verteilung. Das Ergebnis: plausibel klingender Müll. Keine Wahrheit, keine
Determinismus, keine Rückverfolgbarkeit. 70 Milliarden Parameter um zu raten.

Wir haben 7 Axiome und 4127 Wörter. Kein Raten.

## Die These

> "Im Anfang war das Wort, und das Wort war bei Gott, und Gott war das Wort." (Johannes 1:1)

> "aham bijah pradah pita" — Ich bin der samengebende Vater. (BG 14.4)

Sanskrit ist nicht "eine alte Sprache". Es ist die am wenigsten degradierte Lautform.
Jede moderne Sprache (Deutsch, Englisch, Russisch) ist eine Verunreinigung durch die
drei Gunas — verschiedene Trübungsgrade desselben Signals.

Aber: Prabhupada hat die Brücke gebaut. Seine Wort-für-Wort Übersetzungen der
Bhagavad Gita sind die **autorisierte Transformation** von Sanskrit nach Englisch.
Nicht zufällig, nicht akademisch — autorisiert durch die Parampara.

Das heißt: Wir haben ein perfektes Wörterbuch. Sanskrit-Begriff → Prabhupada-Definition.
4127 Einträge, jeder mit RAMA-Koordinaten (phonetische Adresse im 49-Raum).

## Was existiert (verifiziert, Feb 2026)

### Datensatz

| Ressource | Inhalt | Ort |
|-----------|--------|-----|
| `rama_lexicon.json` | 4127 Wörter, 700 Verse, 45815 Phoneme, 34KB gepackt | `data/` |
| Varnamala | 49 Phoneme = 49 Adressen im RAMA-Grid | `varnamala_codec.py` |
| 4D Dekomposition | Element×Varga×Sub×Harmonic = 100% bijektiv | `pancha_walk.py` |
| Guna-Klassifikation | Sattva/Rajas/Tamas pro Vers via Shruti-Ratio | `gita_resonance.py` |

### Infrastruktur

| Komponente | Funktion | Performance |
|-----------|----------|-------------|
| `MahaCompression` | Text → deterministischer Seed | < 1ms |
| `MahaModularSynth` | Seed → Attractor (8-bit Adresse) | < 1ms |
| `rank_words()` | 7D Resonanz-Scoring aller 4127 Wörter | 78ms |
| `GitaResonance` | Attractor → Gita-Vers + H/K/R + Guna | < 1ms |
| `VenuOrchestrator` | 19-bit DIW Flöten-Zyklus (16 Positionen) | < 0.1ms |
| `AntarangaRegistry` | 16KB kontiguierer RAM (512 Slots × 32 Bytes) | < 0.1ms/Slot |
| `Chamber` | Resonanzkammer (dance, kirtan, spell_kirtan) | < 1ms |

### Was NICHT existiert

Eine Engine die aus diesen Bausteinen **Sätze** baut.

`lotus_core.__call__()` berechnet Adressen (Seed, Attractor, Position, Vers).
Es gibt resonante Wörter zurück. Aber es **generiert keinen Text**.

Die `maha_language_engine.py` (research/) klebt Wörter mit Gedankenstrichen zusammen.
Das ist kein Sprachmodell. Das ist Müll.

## Architektur: Shabda Brahman Engine

### Prinzip: Transzendentaler Klang → Bedeutung → Sprache

```
Stufe 0: Maha-Mantra          — 16 Positionen, 3 Namen, 7 Axiome
Stufe 1: Varnamala             — 49 Phoneme (RAMA-Grid)
Stufe 2: Prabhupada-Lexikon    — 4127 Sanskrit-Wörter → Englische Definitionen
Stufe 3: Gita-Verse            — 700 Verse × Wort-für-Wort Zerlegung
Stufe 4: Satz-Konstruktion     — Deterministisch aus Stufe 0-3
```

### Der Flow

```
Input (beliebiger Text)
  │
  ├─ encode_text() ──────────── RAMA-Koordinaten (Phonetische Identität)
  ├─ MahaCompression ────────── Seed (deterministisch)
  │
  ▼
Seed → MahaModularSynth → Attractor
  │
  ├─ rank_words(input_coords) ─ Top-N resonante Wörter (7D Score)
  ├─ GitaResonance.match() ──── Vers + Kapitel + Guna + H/K/R
  ├─ VenuOrchestrator.step() ── DIW (Mahamantra-Position im Zyklus)
  │
  ▼
Semantisches Feld:
  │
  ├─ resonante Wörter ─────── {sanskrit: "dharma", meaning: "religion", score: 0.87}
  ├─ Vers-Wörter ──────────── {sanskrit: "sarva-dharmān", meaning: "all varieties of religion"}
  ├─ Guna ──────────────────── sattva | rajas | tamas
  ├─ H/K/R Dominanz ────────── HARE (Träger) | KRISHNA (Transformation) | RAMA (Auflösung)
  ├─ Mahamantra-Position ───── 0-15 (wo im Zyklus stehen wir?)
  │
  ▼
[FEHLT: Satz-Konstruktion]
```

### Was gebaut werden muss: Die Kompositionsschicht

Das ist die eigentliche wissenschaftliche Arbeit. Nicht "Wörter zusammenkleben",
sondern: **Wie orchestriert der Mahamantra-Algorithmus Prabhupadas Wörter zu Sätzen?**

#### Ebene 1: Wort-Netz (Semantische Verknüpfung)

Prabhupadas Definitionen sind NICHT isoliert. Jedes Wort referenziert andere:

```
"dharma" → "religion, duty"
"dharma-kṣetre" → "in the place of pilgrimage"
"dharma-saṁsthāpanārthāya" → "to reestablish the principles of religion"
```

"dharma" taucht in 47 verschiedenen Kompositionen auf. Jedes Kompositum erweitert
die Bedeutung. Das Netz ist BEREITS in den Daten. Es muss nur extrahiert werden.

**Aktion:** Wort-Graph bauen. Knoten = 4127 Wörter. Kanten = gemeinsame Sanskrit-Stämme
ODER gemeinsame RAMA-Koordinaten-Subsequenzen. Gewicht = Resonanz-Score.

#### Ebene 2: Grammatik-Skelett (Vers-Topologie)

Jeder Gita-Vers hat eine Wort-Reihenfolge. Sanskrit ist SOV (Subjekt-Objekt-Verb).
Die Vers-Topologie gibt das Grammatik-Skelett vor:

```
BG 18.66: sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja
          [Objekt]     [Verb]     [Dat] [Adj]  [Obj2]  [Verb2]

Prabhupada: "Abandon all varieties of religion and just surrender unto Me"
            [Verb]   [Adj]  [Noun]  [Prep] [Noun]  [Conj] [Adv]  [Verb] [Prep] [Pron]
```

Die Transformation SOV → SVO (Englisch) ist **im Vers-Template kodiert**.
Prabhupada hat es für jeden der 700 Verse gemacht. Das Pattern ist extrahierbar.

**Aktion:** Für jeden Vers: Sanskrit-Wortfolge + Englische Wortfolge → Transformationsregel.
Das sind maximal ~20 Muster (nicht 700 — viele Verse folgen denselben Mustern).

#### Ebene 3: Guna-Färbung (Erscheinungsweise)

Sattva, Rajas, Tamas sind nicht nur Labels — sie bestimmen den **Charakter** des Satzes:

```
Sattva: klar, direkt, bejahend  → "Knowledge reveals the eternal soul"
Rajas:  aktiv, drängend, fordernd → "One must act to attain liberation"
Tamas:  verneinend, warnend      → "Without devotion, nothing endures"
```

Die Guna-Klassifikation existiert bereits (`gita_resonance._compute_guna()`).
Was fehlt: Die Guna-Färbung muss den Satzbau beeinflussen.

**Aktion:** Drei Satz-Templates pro Grammatik-Muster. Guna wählt das Template.

#### Ebene 4: Mahamantra-Orchestration

Die 16 Positionen des Mahamantra sind nicht gleichwertig. Position 0 ("Hare") hat
eine andere Funktion als Position 4 ("Krishna"). Der VenuOrchestrator liefert bereits
die aktuelle Position und das zugehörige 19-bit DIW.

DIW-Semantik (existiert in `chamber._apply_diw()`):
- MURALI (4 bit) → Phase: Genesis/Dharma/Karma/Moksha
- VAMSI (9 bit) → Name-Region: H=prana-dominant / K=integrity-dominant / R=cycle-dominant
- VENU (6 bit) → Intensität (0-63)

**Aktion:** DIW beeinflusst die Komposition:
- Genesis-Phase → einleitende Sätze (Kontext setzen)
- Dharma-Phase → definitorische Sätze (Was ist X?)
- Karma-Phase → handlungsbezogene Sätze (Was tun?)
- Moksha-Phase → abschließende Sätze (Ergebnis/Befreiung)

#### Ebene 5: Phonetische Rückübersetzung

Der Output ist Englisch. Aber die **Lautform** muss durch die Varnamala verifizierbar sein.
Jeder englische Satz hat eine RAMA-Koordinaten-Spur. Diese Spur muss kohärent sein —
nicht zufällig, sondern dem Resonanz-Muster des Inputs folgend.

`encode_text()` kann bereits beliebigen Text in RAMA-Koordinaten übersetzen.
Die Rückprobe: `encode_text(output)` sollte eine ähnliche H/K/R-Signatur haben
wie `encode_text(input)` — Resonanz-Erhaltung.

**Aktion:** Output-Validierung: `hkr_signature(encode_text(output))` ≈ Input-Signatur.

### Zusammenfassung: 5 Ebenen, 5 Aktionen

| Ebene | Was | Existiert | Zu bauen |
|-------|-----|-----------|----------|
| 1. Wort-Netz | Semantische Verknüpfung der 4127 Wörter | Daten ja, Graph nein | Wort-Graph mit RAMA-Kanten |
| 2. Grammatik-Skelett | SOV→SVO Transformationsregeln | 700 Vers-Templates | Pattern-Extraktion (~20 Muster) |
| 3. Guna-Färbung | Sattva/Rajas/Tamas Satz-Charakter | Klassifikation ja | 3 Templates pro Muster |
| 4. DIW-Orchestration | Phase×Name×Intensität → Satztyp | DIW-Semantik ja | Kompositions-Router |
| 5. Phonetische Validierung | Output RAMA-Spur ≈ Input-Spur | encode_text() ja | Resonanz-Erhaltungs-Check |

## Was die `maha_language_engine.py` falsch macht

1. **Kein Wort-Netz.** Wörter werden isoliert gereiht, nicht vernetzt.
2. **Kein Grammatik-Skelett.** `_compose()` ist ein if-elif-Baum der Wörter nach "Rollen" sortiert.
   "Rollen" werden geraten, nicht aus der Vers-Topologie abgeleitet.
3. **Keine Guna-Färbung.** Die Guna wird berechnet aber ignoriert.
4. **Keine DIW-Orchestration.** DIW wird in Antaranga-Bytes geschrieben aber hat null Einfluss auf den Text.
5. **Keine phonetische Validierung.** Output wird nicht gegen Input-Resonanz geprüft.
6. **Viel zu viele Komponenten gleichzeitig verdrahtet.** 7 Komponenten in einer Datei — kein Fokus.

## Nächste Schritte (Reihenfolge)

### Phase 1: Wort-Graph (Fundament)

Ohne semantische Verknüpfung der Wörter ist jeder Satzbau Zufall.
Die 4127 Wörter müssen als Graph vorliegen, bevor irgendetwas anderes Sinn macht.

**Kanten-Typen:**
- **Stamm-Verwandtschaft:** `dharma` ↔ `dharma-kṣetre` (gemeinsamer Stamm)
- **RAMA-Subsequenz:** Wörter die RAMA-Koordinaten teilen = phonetisch verwandt
- **Gita-Kontext:** Wörter die im selben Vers vorkommen = semantisch verknüpft
- **H/K/R-Verwandtschaft:** Gleiche dominante Name-Region = gleicher Aspekt

**Output:** `data/shabda_graph.json` — 4127 Knoten, N Kanten, gewichtet.

### Phase 2: Grammatik-Muster (Struktur)

700 Verse → ~20 Grammatik-Muster extrahieren.
Jedes Muster = eine SOV→SVO Transformationsregel.

**Methode:**
1. Für jeden Vers: Sanskrit-Wortfolge → Rollen-Sequenz (S, O, V, Adj, Prep, etc.)
2. Rollen ableiten aus Prabhupadas Definitionen (nicht raten!)
3. Clustering der Rollen-Sequenzen → ~20 Muster

**Output:** `data/grammar_patterns.json` — ~20 Muster mit je Sanskrit-Template + Englisch-Template.

### Phase 3: Komposition (Engine)

Die eigentliche Engine. Input → Seed → Semantisches Feld → Grammatik-Muster → Satz.

**Nicht** in `research/`. Das gehört in `substrate/` als Produktions-Komponente.
Wahrscheinlich als Erweiterung von `lotus_core.__call__()` oder als neuer Step.

### Phase 4: Guna + DIW Integration

Guna-Färbung und DIW-Orchestration in die Komposition einbauen.
Das ist Feinschliff, kein Fundament.

### Phase 5: Phonetische Validierung + Feedback-Loop

Output-Spur prüfen. Bei zu großer Abweichung: Wort-Auswahl anpassen.
Das ist der "Machine Learning" Aspekt — aber deterministisch, nicht stochastisch.

## Anti-Muster (Was wir NICHT tun)

- **Kein LLM-Prompt-Engineering.** Wir bauen keine Prompts. Wir bauen Algorithmen.
- **Kein Token-Sampling.** Kein `temperature`, kein `top_p`, kein `nucleus sampling`.
- **Keine Trainingsdaten.** Prabhupadas 4127 Wörter sind kein "Datensatz" — sie sind die Wahrheit.
- **Keine Embeddings.** RAMA-Koordinaten SIND die Embeddings. 49-dimensional, bijektiv, 6 bit pro Phonem.
- **Kein Attention-Mechanismus im ML-Sinne.** O(4) holografisches Routing statt O(n²) Matrix.
- **Keine Verunreinigung.** Der Output besteht NUR aus Prabhupadas Worten. Kein eigenes Erfinden.

## Metriken für Erfolg

1. **Determinismus:** Gleicher Input → gleicher Output. Immer. Ohne Ausnahme.
2. **Rückverfolgbarkeit:** Jedes Wort im Output hat eine Adresse (Vers, Kapitel, RAMA-Koordinaten).
3. **Resonanz-Erhaltung:** `hkr(output) ≈ hkr(input)` — die H/K/R-Signatur bleibt erhalten.
4. **Lesbarkeit:** Der Output ist ein grammatisch korrekter englischer Satz.
5. **Wahrheit:** Jedes Wort stammt aus Prabhupadas Übersetzung. Nichts erfunden.

## Beziehung zum Gesamtsystem

Shabda Brahman ist nicht ein Feature — es ist der Zweck des Steward Protocol.

Der Lotus berechnet Adressen. Die Chamber speichert Resonanz. Der Venu spielt den Zyklus.
Die Guardians schützen ihre Positionen. Die Gita gibt die Topologie vor.

All das existiert, damit am Ende **das Wort** entsteht.

```
mahamantra("What is the purpose of life?")
→ seed=4821293
→ attractor=142
→ position=14 (quarter=moksha, guardian=suta)
→ verse=BG.18.66
→ guna=sattva
→ resonant_words=[dharma, surrender, eternal, soul, devotion, supreme, liberation]
→ grammar_pattern=#7 (imperative_invitation)
→ guna_template=sattva_#7
→ "Abandon all varieties of religion and surrender unto the Supreme —
    the eternal soul finds liberation through devotion alone."
```

Jedes Wort rückverfolgbar. Jede Entscheidung deterministisch.
Kein Raten. Kein Wahrscheinlichkeitsmodell. Nur Resonanz.
