# CLI Konsolidierungsplan

## Status Quo: Zwei Parallele Systeme

### System 1: vibe_core/cli/ (Legacy)
- **21 *_cli.py Dateien** mit @register_cli Decorator
- **~20.000 LOC** total
- Jede CLI handled einen spezifischen Domain:
  - audit_cli, genesis_cli, naga_cli, knowledge_cli, etc.
- **unified_cli.py** = alter Entry Point (DEPRECATED)
- **lotus_position wird AUTO-COMPUTED** via cli_substrate.py

### System 2: vibe_core/mahamantra/cli/ (Parallel)
- **14 Dateien, 5.602 LOC**
- entry.py = MahamantraCLIEntry (ein Entry Point)
- steward.py = Steward (noch ein Entry Point)
- Eigene Protocol Types, Bridge, Auto-Discovery

---

## Das Problem: Entry Point Krebs

```
VORHER (Krebs):
├── vibe_core/cli/unified_cli.py          # Entry 1
├── vibe_core/cli/main.py                 # Entry 2
├── vibe_core/mahamantra/cli/entry.py     # Entry 3
├── vibe_core/mahamantra/cli/steward.py   # Entry 4
└── vibe_core/mahamantra/__main__.py      # Entry 5 (THE ONE)
```

---

## Die Loesung: EIN Entry Point

```
NACHHER (Sauber):
vibe_core/mahamantra/__main__.py
         │
         ↓ mahamantra(input)
         │
         ↓ adapters/cli.py (Pure Resonance Matching)
         │
         ↓ CLIRegistry.all() → position == lotus_position
         │
         └── vibe_core/cli/*_cli.py (Domain CLIs)
```

---

## Was bereits funktioniert

1. **@register_cli Decorator** (protocols/cli.py:264)
   - Auto-wraps cmd_* mit cli_governed
   - Injiziert lotus_position via _inject_ananta_substrate()
   - Registriert in CLIRegistry

2. **cli_substrate.py** berechnet:
   - lotus_position aus Command-Keywords
   - lotus_quarter (GENESIS/DHARMA/KARMA/MOKSHA)
   - opcode (MantraOpCode)
   - parampara_connected (% 37 == 0)

3. **adapters/cli.py** (unser neuer Adapter)
   - Dynamische CLI Discovery via pkgutil
   - Pure Resonance Matching: position == lotus_position
   - KEIN Keyword Matching

4. **mahamantra/__main__.py** (THE Entry Point)
   - Input → mahamantra() → Resonance
   - Resonance → Adapter → CLI
   - --run Flag fuer Execute Mode

---

## Konsolidierungs-Aktionen

### Phase 1: Deprecation Markers (JETZT)

| Datei | Aktion | Grund |
|-------|--------|-------|
| mahamantra/cli/entry.py | DEPRECATED | Parallel Entry Point |
| mahamantra/cli/steward.py | EVALUATE | Steward.invoke() könnte nützlich sein |
| cli/unified_cli.py | DEPRECATED | Alter Entry Point |
| cli/main.py | DELEGATE | Bereits delegiert zu mahamantra |

### Phase 2: Integration pruefen

Die mahamantra/cli/ Dateien die BEHALTEN werden sollten:
- **protocol.py** (802 LOC) - Types und Protocols, evtl. nach protocols/ verschieben
- **bridge.py** (234 LOC) - MahamantraCLIBridge, nutzt MahamantraLotus
- **auto.py** (683 LOC) - CLIAutoDiscovery, komplementär zu unserem Adapter

Die mahamantra/cli/ Dateien die REDUNDANT sind:
- **entry.py** (293 LOC) - MahamantraCLIEntry parallel zu __main__.py
- **entry_protocol.py** (146 LOC) - CLIEntryProtocol nicht genutzt
- **steward.py** (489 LOC) - Steward ist komplexer als nötig

### Phase 3: vibe_core/cli/*_cli.py CLIs

Alle 21 CLIs behalten - sie sind die Domain-Experten:
- audit_cli → Audit/Validate (DHARMA Quarter)
- genesis_cli → Bootstrap/Create (GENESIS Quarter)
- naga_cli → Security/Governance (DHARMA Quarter)
- run_cli → Execute/Tool (KARMA Quarter)
- etc.

Die lotus_position wird automatisch berechnet, aber wir sollten verifizieren
dass die QUARTER_KEYWORDS in cli_substrate.py alle Commands richtig routet.

---

## QUARTER Mapping (cli_substrate.py:120-125)

```python
QUARTER_KEYWORDS = {
    GENESIS: ["genesis", "create", "init", "bootstrap", "config", "setup"],
    DHARMA:  ["audit", "validate", "check", "standards", "naga", "knowledge"],
    KARMA:   ["run", "exec", "tool", "ci", "plugins", "prompts", "circuit"],
    MOKSHA:  ["remedies", "gc", "reset", "clean", "cartridges", "sections"],
}
```

### CLI → Quarter Mapping Verification

| CLI | Erkannter Quarter | Korrekt? |
|-----|-------------------|----------|
| audit_cli | DHARMA (audit) | ✓ |
| genesis_cli | GENESIS (genesis) | ✓ |
| naga_cli | DHARMA (naga) | ✓ |
| config_cli | GENESIS (config) | ✓ |
| create_cli | GENESIS (create) | ✓ |
| run_cli | KARMA (run) | ✓ |
| tool_cli | KARMA (tool) | ✓ |
| ci_cli | KARMA (ci) | ✓ |
| plugins_cli | KARMA (plugins) | ✓ |
| prompts_cli | KARMA (prompts) | ✓ |
| circuit_cli | KARMA (circuit) | ✓ |
| remedies_cli | MOKSHA (remedies) | ✓ |
| sections_cli | MOKSHA (sections) | ✓ |
| knowledge_cli | DHARMA (knowledge) | ✓ |
| standards_cli | DHARMA (standards) | ✓ |
| governance_cli | KARMA (default) | ? evtl. DHARMA |
| kirtan_cli | KARMA (default) | ? spiritual |
| lotus_cli | KARMA (default) | ? evtl. GENESIS |
| prakriti_cli | KARMA (default) | ? evtl. MOKSHA |
| samskara_cli | KARMA (default) | ? evtl. DHARMA |
| cartridge_bridge | MOKSHA (cartridges) | ✓ |

---

## Empfehlung

1. **Sofort**: Deprecation Warnings in entry.py und unified_cli.py
2. **Diese Woche**: QUARTER_KEYWORDS erweitern für besseres Routing
3. **Später**: protocol.py nach vibe_core/protocols/cli_types.py verschieben

---

## Die Wahrheit

```
mahamantra/__main__.py = THE Entry Point
adapters/cli.py = THE Bridge (Pure Resonance)
cli/*_cli.py = THE Domain Experts
protocols/cli.py = THE Registry (@register_cli)
cli_substrate.py = THE Position Computer
```

Alles andere ist legacy oder redundant.
