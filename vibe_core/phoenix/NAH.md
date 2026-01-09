# NAH: PHOENIX (Wiedergeburt/Recovery)

**Status:** OUTLAW (2.5% - 1/40 governed)
**Priorität:** HOCH - Phoenix-Garantie ist Kern-Dharma

## Ist-Zustand
- 40 Python-Dateien
- Nur 1 importiert von protocols/
- GEFAHR: Recovery-System ohne klare Verträge

## Soll-Zustand
- PhoenixProtocol definieren in protocols/
- Alle config/sections unter Protokoll
- utils/ als Helpers markieren (dürfen protocol-frei sein)

## Architektur-Mapping
```
phoenix/
├── config.py        → protocols/substrate.py (bereits!)
├── sections/        → Braucht SectionProtocol
└── utils/           → Helpers (keine Protokoll-Pflicht)
```

## Nächste Schritte
1. [ ] SectionProtocol prüfen/erstellen
2. [ ] sections/*.py mit Protocol verbinden
3. [ ] Phoenix-Garantie in Tests verifizieren
