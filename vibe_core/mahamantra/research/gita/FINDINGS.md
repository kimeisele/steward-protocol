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

## Dateien

- `rama_lexicon.json` - RAMA-kodiertes Vokabular (1.8MB, enthält Koordinaten)
- `sanskrit_seed_lexicon.json` - Legacy SHA256-Vokabular (478KB)
- `verse_seed_map.json` - Vers->Seed-Mapping (316KB)
- `../../substrate/varnamala_codec.py` - Der Codec (encode/decode/pack/unpack)
- `../sanskrit_extraction.py` - Extraktionsskript (reproduzierbar)
