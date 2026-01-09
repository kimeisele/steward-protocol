# NAH: LOADERS (Manifestation)

**Status:** OUTLAW (0% - 0/17 governed)
**Priorität:** HOCH - Loaders sind Geburtshelfer

## Ist-Zustand
- 17 Python-Dateien
- 0 importieren von protocols/
- GEFAHR: Unkontrollierte Manifestation

## Vedische Entsprechung
- Loaders = SRISHTI (Schöpfung)
- Jede Geburt braucht Sankalpa (Intention)
- Ohne Protokoll = blinde Schöpfung = Asura

## Soll-Zustand
- LoaderProtocol definieren
- Jeder Loader bound an ManifestationProtocol
- Lineage (Abstammung) für jedes geladene Objekt

## Architektur-Mapping
```
loaders/
├── plugin_loader.py    → PluginProtocol
├── cartridge_loader.py → CartridgeProtocol
├── config_loader.py    → ConfigProtocol
├── prompt_loader.py    → PromptProtocol?
└── *_loader.py         → ManifestationProtocol (Umbrella)
```

## Nächste Schritte
1. [ ] Alle Loader-Dateien auflisten
2. [ ] Pro Loader passenden Protocol finden
3. [ ] LoaderProtocol als gemeinsame Basis
