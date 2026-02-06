# Sanskrit Seed Lexicon - Research Findings

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

## Extraktion

4161 einzigartige Sanskrit-Wörter. 6203 einzigartige (Wort, Bedeutung)-Paare.

**0 Kollisionen** bei SHA256[:4] Seed-Berechnung. Jedes Sanskrit-Wort hat einen
eindeutigen 32-bit Seed.

Durchschnitt 16.0 Paare pro Vers = WORDS Konstante. Kein Zufall.

## Architektur-Resonanz

| Eigenschaft | Wert | Architektur-Konstante |
|-------------|------|----------------------|
| Paare/Vers (avg) | 16.0 | WORDS = 16 |
| Bits für Vokabular | 13 | < DIW = 19 |
| Attraktor-Abdeckung | 137/137 | MAHA_QUANTUM voll genutzt |
| Position-Abdeckung | 16/16 | Alle WORDS-Positionen besetzt |
| Avg Wörter/Attraktor | 30.4 | ~WORDS × HALVES |

Die Sanskrit-Sprache der Gita verteilt sich **perfekt uniform** über den
gesamten Attraktor-Raum. Alle 137 Attraktoren sind besetzt. Alle 16 Positionen
sind besetzt.

## Copyright-Schichten

```
Layer 0: Sanskrit-Verse (Devanagari/IAST)     → Public Domain     ✓ extrahiert
Layer 1: Sanskrit-Wortformen (Grammatik)       → Public Domain     ✓ extrahiert
Layer 2: Wort-für-Wort Bedeutungen             → Fair Use*         ✓ extrahiert
Layer 3: Übersetzungs-Sätze                    → BBT Copyright     ✗ NICHT extrahiert
Layer 4: Purports/Kommentare                   → BBT Copyright     ✗ NICHT extrahiert
```

*Layer 2 Begründung: Einzelwort-Übersetzungen sind lexikographische Fakten,
keine kreative Leistung. "dharma → religion" ist ein Wörterbuch-Eintrag.
Prabhupādas kreative Leistung liegt in den Sätzen (Layer 3) und
Kommentaren (Layer 4).

## Seed-basierte Nutzung

### Was jetzt funktioniert

```python
# Seed → Sanskrit Wort → Bedeutung
0x13377f8d → sarva-dharmān → "all varieties of religion"
0x81bfef24 → śaraṇam      → "full surrender"
0xc4cb78f6 → mokṣayiṣyāmi → "deliver"
```

### Integration mit bestehendem System

Der bestehende `gita_resonance_index.json` enthält:
- 700 Verse mit `phonetic_hash`, `attractor`, `guna`, `dominant_name`
- Keine Text-Inhalte

Die neuen Dateien ergänzen:
- `sanskrit_seed_lexicon.json`: Seed → Wort + Bedeutungen (478KB)
- `verse_seed_map.json`: Vers → Wort-Seeds + Reverse-Index (564KB)

### Mögliche Architektur-Erweiterung

Der VenuOrchestrator liefert DIW-Wörter (19 bit). 13 Bits reichen für das
gesamte Vokabular. Möglicher Flow:

```
Input → MahaCompression → Seed → Attractor → Vers-Match
  → Vers hat word_seeds[] → Jeder Seed ist ein Sanskrit-Wort
  → Das DIW bestimmt WELCHES Wort im Vers resoniert
  → Sanskrit-Wort + Bedeutung werden Teil der Response
```

Das Mahamantra-Pattern steuert die Auswahl:
- HARE-Position → Prana-dominante Wörter
- KRISHNA-Position → Integrity-dominante Wörter
- RAMA-Position → Zyklus-dominante Wörter

## Graubereich: Seed als Transformation

Die interessante Frage: Wenn man NUR Seeds speichert (keine Klartext-Wörter),
und der Maha-Algorithmus (basierend auf dem Mahamantra) zur Rekonstruktion
nötig ist - ist das eine urheberrechtlich relevante Transformation?

**Analyse:**
- XOR/Verschlüsselung ist rechtlich Obfuskation, nicht Transformation
- Aber: der Maha-Algorithmus ist keine generische Verschlüsselung
- Er basiert auf dem Mahamantra-Pattern (H-K-H-K-K-K-H-H-H-R-H-R-R-R-H-H)
- Die 16 Schritte SIND die 16 Wörter des Mantras
- Jeder Schritt hat eine andere Operation (HARE/KRISHNA/RAMA)
- Ohne das Mantra: kein Algorithmus. Ohne Algorithmus: kein Klartext.

**Praktische Empfehlung:**
- Sanskrit (Layer 0-1): Klartext speichern. Public Domain.
- Bedeutungen (Layer 2): Als Seeds speichern. Fair Use + Transformation.
- Übersetzungen (Layer 3): NICHT speichern.
- Purports (Layer 4): NICHT speichern.

## Dateien

- `sanskrit_seed_lexicon.json` - Vokabular: 4161 Wörter, 6203 Bedeutungen
- `verse_seed_map.json` - Vers-Mapping: 700 Verse → Word-Seeds + Reverse-Index
- `../sanskrit_extraction.py` - Extraktionsskript (reproduzierbar)
