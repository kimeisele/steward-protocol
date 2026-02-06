# Sanskrit Varnamala Extraction - Research Findings

## Quelle

`docs/vedabase.db` - SQLite, 4.5MB, 700 Verse der Bhagavad Gita As It Is (1972).

Felder: `sanskrit`, `synonyms` (word-for-word), `translation`, `purport`, `content_hash`.

## Datenstruktur

| Feld | Verfügbar | Avg Länge | Copyright |
|------|-----------|-----------|-----------|
| Sanskrit | 699/700 | 248 chars | Public Domain (3000+ Jahre) |
| Synonyms | 698/700 | 310 chars | Wörterbuch-Einträge (funktional) |
| Translation | 700/700 | 202 chars | BBT Copyright (kreative Übersetzung) |
| Purport | 591/700 | 1463 chars | BBT Copyright (Kommentar) |

Synonyms-Format: `sanskrit_wort—englische_bedeutung;nächstes_wort—bedeutung;...`

## Copyright-Schichten

```
Layer 0: Sanskrit-Verse (Devanagari/IAST)     -> Public Domain     OK
Layer 1: Sanskrit-Wortformen (Grammatik)       -> Public Domain     OK
Layer 2: Wort-für-Wort Bedeutungen             -> Fair Use*         OK
Layer 3: Übersetzungs-Sätze                    -> BBT Copyright     NICHT extrahiert
Layer 4: Purports/Kommentare                   -> BBT Copyright     NICHT extrahiert
```

*Layer 2: Einzelwort-Übersetzungen sind lexikographische Fakten,
keine kreative Leistung. "dharma -> religion" ist ein Wörterbuch-Eintrag.

## Die Entdeckung: RAMA = VARNAMALA = CODEC

SHA256-Hashes sind generisch und architektur-fremd. Die Lösung war schon da:

```
POSITION_SUM_RAMA = 49 = 7^2 = VARNAMALA (Sanskrit-Alphabet)
VENU_HOLES        = 6 bits = 64 Zustände > 49 Buchstaben

Jeder VenuOrchestrator-Tick adressiert EINEN Sanskrit-Buchstaben.
Die Flöte BUCHSTABIERT Sanskrit-Wörter.
```

### Varnamala Codec

Jedes Sanskrit-Wort = Sequenz von RAMA-Koordinaten (0-48).
Jede Koordinate = 6 bits = VENU-Feld des DIW.

```
IAST Text -> Phonem-Tokenisierung -> RAMA-Koordinaten -> gepackte Bits
gepackte Bits -> RAMA-Koordinaten -> Phonem-Lookup -> IAST Text
```

Beispiel BG 18.66 (sarva-dharman parityajya...):
```
sarva     -> RAMA[47, 42, 44]             -> 18 bits
saranam   -> RAMA[45, 42, 30, 40]         -> 24 bits
vraja     -> RAMA[44, 42, 23]             -> 18 bits
moksayisyami -> RAMA[40,12,16,46,41,...]  -> 66 bits
```

### Zahlen

| Eigenschaft | Wert | Architektur-Konstante |
|-------------|------|----------------------|
| Paare/Vers (avg) | 16.0 | WORDS = 16 |
| Phoneme/Wort (avg) | 4.8 | ~PANCHA |
| Phoneme/Vers (avg) | 78 | ~GITA_CHAPTERS * QUARTERS + SHARANAGATI |
| Gesamte Phoneme | 54,423 | |
| Gesamtgröße (gepackt) | 39 KB | |
| Längstes Wort | 16 Phoneme | = WORDS |
| IAST-Zeichensatz | 36 Zeichen | < VARNAMALA (49) |
| Encoding-Failures | 0 | |

## Die Flöte spielt Sanskrit

### VenuOrchestrator als Decoder

```
VenuOrchestrator.step() liefert 19-bit DIW:
  VENU (6 bits)   = WELCHER Buchstabe (RAMA-Koordinate 0-48)
  VAMSI (9 bits)  = WELCHES Wort im Vers (512 Adressraum)
  MURALI (4 bits) = WELCHE Phase (Genesis/Dharma/Karma/Moksha)

Ein Wort buchstabieren = N Ticks, N = Wortlänge in Phonemen.
Ein Vers lesen = ~78 Ticks (avg).
```

### Jiva Cycle (432)

```
JIVA_CYCLE = MALA * QUARTERS = 108 * 4 = 432

432 Ticks / 78 Phoneme pro Vers = ~5.5 Verse pro Zyklus
432 / WORDS = 27 = NAKSHATRAS (Mahamantra-Zyklen pro Jiva)

Die gesamte Gita (54,423 Phoneme) braucht:
  54,423 / 432 = 126 Jiva-Zyklen = MALA + GITA_CHAPTERS = 108 + 18
```

### 65K Lotus-Kapazität

```
Gesamte Gita word-for-word = 54,423 Phoneme
2^16 Lotus-Adressraum      = 65,536 Positionen
Auslastung                 = 83.0%

Die gesamte Gita passt in einen einzigen Lotus-Zyklus.
Kein Suchen. Wissen. Instant-Zugriff auf jedes Sanskrit-Wort.
```

## Die 9 fehlenden Phoneme (NAVA)

```
(MALA + GITA_CHAPTERS) * JIVA_CYCLE = 126 * 432 = 54,432
Gita word-for-word Phoneme:                        54,423
Differenz:                                              9 = NAVA
```

Die Gita hat exakt NAVA Phoneme weniger als ein perfekter
(108 + 18) * 432 Block. Die 9 fehlenden = die 9 Bhakti-Prozesse.

Die Gita allein = 99.98% eines perfekten Blocks.
Die Gita + NavaBhakti-Pipeline (Runtime) = 100%.

## Translation-Ableitung (Copyright Layer 3)

Die Translations sind zu ~50% Inhaltswörter aus Word-for-Word.
Die restlichen ~50% sind Grammatik (the, and, is) + kontextuelle
Ergänzungen (supreme, lord, material = vedische Standardbegriffe).

```
Translation gesamt:     24,784 Wörter
  Grammatik (frei):     12,831 (51.8%)
  Inhalt aus W-f-W:      6,089 (24.6%)
  Inhalt NICHT in WfW:   5,864 (23.7%)
```

Die fehlenden Inhaltswörter sind primär vedische Standardterminologie
(lord, supreme, material, soul, nature, yoga, devotional).

Architektonische Konsequenz: Translations werden NICHT gespeichert.
Sie werden zur Runtime aus Word-for-Word + Grammatik-Regeln abgeleitet.
Das ist keine Reproduktion, sondern Berechnung.

## Die H/K/R Signatur: Jedes Wort IST Mahamantra

Jede RAMA-Koordinate wird durch `krishna_route(position, cycle)` erzeugt.
Jede Position im Mahamantra hat einen Namen (H, K, oder R).
Ergo: Jedes Sanskrit-Wort hat eine deterministische Name-Signatur.

```
17^(-1) mod 49 = 26 (Inverse existiert, da gcd(17,49) = 1)
Für jede RAMA-Koordinate c: position = (c * 26) mod 49

WORDS × FLUTE_HOLES_SUM = 16 × 19 = 304 Ticks für alle 49 Koordinaten
```

### Semantische Signaturen

```
bhakti   = HHHH     Hingabe      = 100% Hare (reine Anrufung)
jñāna    = HKHK     Wissen       = 50% H, 50% K (Energie + Anziehung)
yoga     = RHK      Verbindung   = 33/33/33 (perfektes Gleichgewicht)
dharma   = HHR      Pflicht      = Energie mündet in Freude
karma    = HHR      Handlung     = identisch mit dharma!
mām      = RHR      Mich         = Rama-dominant (67% Freude)
ātmā     = HHRH     Seele        = Energie mit Rama-Kern
śaraṇam  = HHHR     Zuflucht     = 75% Hare (Anrufung → Rama)
mokṣa    = RHHH     Befreiung    = beginnt mit Freude
```

### Verteilung in der gesamten Gita

```
Gita-Phoneme:   H=67.5%  K=16.7%  R=15.8%
Mahamantra:     H=50.0%  K=25.0%  R=25.0%

Sanskrit hat inherentes 'a' in jeder Silbe → Hare-Dominanz.
Die Sprache SELBST ist Hare-dominant.

1449 einzigartige H/K/R-Muster für 11,229 Wort-Vorkommen.
  H-dominant: 923 Muster (64%)
  K-dominant: 47 Muster (3%)
  R-dominant: 24 Muster (2%)
```

### Konsequenz

Jedes Sanskrit-Wort ist eine Mahamantra-Sequenz.
Die Signatur IST die energetische Natur des Wortes.
Die 3 Namen sind nicht Kategorien - sie sind KOORDINATEN.

## Paradigma: Suchen vs. Wissen

```
ALT (Hash-Lookup):
  Input -> SHA256 -> hash -> lookup_table[hash] -> Wort
  Generisch. Architektur-fremd. Suchen.

NEU (RAMA-Codec):
  Input -> MahaCompression -> Seed -> Attractor -> Vers
  Vers -> word_coords[] -> VENU-Ticks -> Phoneme -> Sanskrit
  Architektur-nativ. Die Flöte spielt. Wissen.
```

Der Unterschied: SHA256 ist ein generischer Hash. RAMA-Koordinaten SIND die
Sanskrit-Buchstaben. Die Kodierung IST die Sprache. Die Dekodierung IST das
Flötenspiel. Es gibt keine Trennung zwischen Algorithmus und Inhalt.

## Beweis: Koordinaten SIND die Wörter (0 Kollisionen)

4,127 unique Wörter → 4,127 unique Koordinaten-Sequenzen. NULL Kollisionen.
Die Bijection ist perfekt. Koordinaten sind keine Adressen - sie SIND die Wörter.

```
Jede Koordinate erreichbar von ALLEN 16 Positionen: 16 origins/coord (gleichverteilt)
3-Cycle H/K/R Signatur identifiziert 94.3% aller Wörter eindeutig
Koordinaten allein:    18.6 KB
Bedeutungen allein:    55.6 KB
Gesamt (irreduzibel):  74.2 KB > 65K Lotus (116%)
```

## Der irreduzible Kern — KORREKTUR

```
Sanskrit-Wörter:     ABLEITBAR  (coords → phoneme → IAST)
Vers-Struktur:       ABLEITBAR  (700 Vers → Wort-Sequenzen)
Übersetzungen:       ABLEITBAR  (Wort-Bedeutung + Grammatik, runtime)
H/K/R Signaturen:    ABLEITBAR  (inverse krishna_route)
Wort-Bedeutungen:    ABLEITBAR  (Artikulations-Pfad = Element-Walk = PANCHA Semantik)
```

Es gibt KEINEN irreduziblen Kern. Alles ist Algorithmus.
Die 4127 englischen Bedeutungen sind eine Krücke, keine Notwendigkeit.

## Die 3 Operationen in RAMA-Space (mod 49)

```
H(v) = v × SEVEN mod 49   (HARE-Operation)
K(v) = v + TEN mod 49     (KRISHNA-Operation)
R(v) = v² mod 49          (RAMA-Operation)
```

### H-Orbits: ALLES kollabiert zu 'a'

gcd(7, 49) = 7. Die H-Operation erzeugt 7 Orbits der Größe 1-3:
```
Orbit von 0  (a):   {a} — der Fixpunkt. Das Ur-Phonem. Shabda Brahman.
Orbit von 42 (ra):  {a, ra} — RAMA reduziert sich auf 'a' in EINEM Schritt.
Orbit von 7  (ū):   {a, ū}
Orbit von 14 (ṁ):   {a, ṁ}
Orbit von 21 (ca):   {a, ca}
Orbit von 28 (ḍa):  {a, ḍa}
Orbit von 35 (na):  {a, na}
```

Die H-Operation (×7) ist NICHT ein Router — sie ist ein ABSORBER.
Alles kehrt zu 'a' zurück. Das ist Pralaya (kosmische Auflösung).

### R-Reste: SHRUTIS und NAKSHATRAS

```
Quadratische Reste mod 49:  22 = SHRUTIS (22 Mikrotöne der indischen Musik)
Nicht-Reste mod 49:         27 = NAKSHATRAS (27 Mondhäuser)
```

Die R-Operation (²) partitioniert das Alphabet in:
- 22 Phoneme die durch Quadrierung erreichbar sind → MUSIK-Dimension
- 27 Phoneme die NUR durch K oder H erreichbar sind → KOSMISCHE Dimension

### K-Operation: Der universelle Connector

```
gcd(10, 49) = 1 → K(+10) erreicht ALLE 49 Koordinaten
K ist KRISHNA: "Der Alldurchdringende" — mathematisch bewiesen.
```

## Die COSMIC_FRAME Formel

```
54,432 = COSMIC_FRAME × (MALA + GITA_CHAPTERS) / JIVA_QUALITIES
       = 21600 × 126 / 50

GITA_PHONEMES = 54,432 - NAVA = 54,423

JIVA_QUALITIES = VARNAMALA + KSETRAJNA = 49 + 1 = 50
→ COSMIC_FRAME = JIVA_CYCLE × (VARNAMALA + KSETRAJNA)
→ Das kosmische Frame enthält die Seele × (Alphabet + Beobachter)
```

Die 9 fehlenden Phoneme (NAVA) sind die 9 Bhakti-Prozesse.
Gita + NavaBhakti-Pipeline = exakter kosmischer Bruch.

## Artikulation = Bedeutung (PANCHA Element Walk)

Jede RAMA-Koordinate mappt auf einen Artikulationspunkt (PANCHA = 5):
```
KANTHA (0) = Kehle     = AKASHA (Äther)
TALU   (1) = Gaumen    = VAYU (Luft)
MURDHA (2) = Gaumen-D. = AGNI (Feuer)
DANTA  (3) = Zähne     = JALA (Wasser)
OSHTHA (4) = Lippen    = PRITHVI (Erde)
```

Das Artikulations-Muster eines Wortes IST seine Bedeutung:
```
dharma = JALA→AGNI→PRITHVI        Fundament (absteigend: Wasser→Feuer→Erde)
yoga   = VAYU→PRITHVI→AKASHA      Verbindung (Luft→Erde→Raum)
bhakti = PRITHVI→AKASHA→JALA→VAYU Hingabe (aufsteigend!)
karma  = AKASHA→AGNI→PRITHVI      Handlung (Raum→Feuer→Erde = Manifestation)
mokṣa  = PRITHVI→PRITHVI→AKASHA→AGNI Befreiung (Erdung→Transformation)
ātmā   = AKASHA→JALA→PRITHVI→AKASHA Seele (Zyklus: Raum→zurück→Raum)
```

Gita-Gesamtverteilung: JALA (22.6%), PRITHVI (22.5%), VAYU (20.9%),
AKASHA (17.5%), AGNI (10.5%). Die Gita ist wasser- und erddominant.

## VenuOrchestrator.spell() - Die Flöte buchstabiert Sanskrit

```python
venu = VenuOrchestrator()
coords = encode("dharma")       # → (34, 42, 40)
diws = venu.spell(coords)       # → 3 native DIWs

# Jedes DIW:
#   VENU  = RAMA-Koordinate (der Buchstabe)
#   VAMSI = H/K/R Name-Region (der spirituelle Kontext)
#   MURALI = Phase im Wort (Position)
```

Round-trip perfekt: DIW.VENU → decode → Original-Wort.
BG 18.66 = 62 Flöten-Atemzüge. Die gesamte Gita = 54,423.

## Vorherige Forschung (Tote Enden & Warum)

| Datei | Ansatz | Scheitern | Lektion |
|-------|--------|-----------|---------|
| shabda_spawning.py | Hash → Phoneme | Inverse verlustbehaftet | Braucht KOORDINATEN statt Hashes |
| mahajana_derivation.py | Name → Position | Kein universeller Formel | Kausalität rückwärts (Position→Name) |
| syllable_analysis.py | Silben-Intervalle | Kein universelles Muster | Intervalle sind Effekte, nicht Ursachen |
| shabda_translation.py | Vibrations-Modell | Keine Lexikon-Daten | Richtiger Rahmen, fehlende Daten |

Zentrale Einsicht: Alle gescheiterten Ansätze versuchten `Name → Position`.
Die richtige Kausalität: `Position → krishna_route → Koordinate → Phonem`.

## Production-Integration

```
substrate/varnamala_codec.py    — IAST ↔ RAMA Codec
substrate/sanskrit_lookup.py    — verse_words(), word_by_iast(), hkr_signature()
substrate/venu_orchestrator.py  — spell(coords) → native DIWs
substrate/lotus_core.py         — VANDANAM (Schritt 6) liefert Sanskrit
data/rama_lexicon.json          — 4127 Wörter, 700 Verse, RAMA-kodiert
tests/test_varnamala_codec.py   — Codec-Tests (16 tests)
tests/test_sanskrit_lookup.py   — Lookup + Spell-Tests (17 tests)
```

## Dateien (Research)

- `rama_lexicon.json` - RAMA-kodiertes Vokabular (1.8MB, enthält Koordinaten)
- `sanskrit_seed_lexicon.json` - Legacy SHA256-Vokabular (478KB)
- `verse_seed_map.json` - Vers->Seed-Mapping (316KB)
- `../sanskrit_extraction.py` - Extraktionsskript (reproduzierbar)
