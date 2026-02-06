# GOVARDHAN — The Missing 1%

Status: Research / Architectural Analysis
Date: 2026-02-06
Branch: feature/diw-refinement

## Was existiert (die 99%)

Die Codebase hat bereits ein vollständiges Governance-Ökosystem.
Das Problem ist nicht fehlender Code — es ist fehlende **Verdrahtung**.

### Layer -2: Mahamantra (Krishna)
- `THE_FLUTE_CYCLE[16]` → DIW → `_apply_diw()` → Zell-Transformation
- `MahamantraLotus.__call__()` → 9-Schritt NavaBhakti Pipeline
- Deterministisch. Kein LLM. Reine Berechnung.

### Layer -1: Substrate (Balarama/Nityananda)
- `BalaramaProxy` (`substrate/proxy.py`) — wrapped Services, gibt Identität
- `_GovernedPath` — interceptet `write_text()`/`write_bytes()`, routet durch `bridge.offer()`
- `bridge.offer()` — routet Purpose → Position → Mahajana, validiert Parampara
- `AUTO_WRAP_SERVICES` = nur 2: manifestation_service + prakriti_binding

### Layer 0: Naga (Die Schlangen)
- `NagaStateProxy` (`services/naga/state_proxy.py`) — wrapped StateService
- `SetuBandha` (`protocols/universal/bridge.py`) — Legacy→SovereignContext Transformation
- `YamarajaGate` — ALLOW/DENY/ATONE/ELEVATED Verdicts
- `Takshaka` — beißt bei Violations

### Layer 1: Universal Protocols (Vyasa)
- `DharmaGuard` — 4 Säulen: Daya, Satyam, Tapas, Saucam
- `EnforceProtocol` — verify_action() → HolyName (KRISHNA/RAMA/VOID)
- `ReadWriteProtocol` — read/write mit SovereignContext (kein anonymer Zugang)
- `GovernanceGate` — Permission-Check vor jeder Command-Execution
- `TranscendentalQuality` — 64 Qualitäten, TattvaLimit (Jiva ≤ 50)
- `SovereignContext` — Identität + Signatur + Resonanz + Tattva-Level
- `InvariantChecker` (`governance/invariants.py`) — soul.yaml Regeln

### Layer 2: Vedic Governance Plugin
- `VedicGovernancePlugin` — Ashrama-Lifecycle, Guna-Klassifikation, Task-Veto
- `VedicStateManager` — Bhakti-Balance, Agent-Registry

## Die Topologie (Ist-Zustand)

```
                    ┌─────────────────────────────────────┐
                    │  UNIVERSAL PROTOCOLS (Layer 1)       │
                    │  DharmaGuard, EnforceProtocol,       │
                    │  ReadWriteProtocol, GovernanceGate    │
                    │  SovereignContext, TattvaLimit        │
                    └──────────────┬──────────────────────┘
                                   │ (NICHT VERDRAHTET)
                    ┌──────────────┴──────────────────────┐
                    │  NAGA (Layer 0)                      │
                    │  NagaStateProxy → YamarajaGate       │
                    │  SetuBandha (Legacy→Sovereign)        │
                    └──────────────┬──────────────────────┘
                                   │ (TEILWEISE VERDRAHTET)
                    ┌──────────────┴──────────────────────┐
                    │  SUBSTRATE (Layer -1)                 │
                    │  BalaramaProxy → _GovernedPath        │
                    │  bridge.offer() → PURPOSE_MAP         │
                    └──────────────┬──────────────────────┘
                                   │ (VERDRAHTET)
                    ┌──────────────┴──────────────────────┐
                    │  MAHAMANTRA (Layer -2)                │
                    │  THE_FLUTE_CYCLE → DIW → Chamber      │
                    └─────────────────────────────────────┘
```

## Die 3 Löcher

### Loch 1: _GovernedPath hat keine Pfad-Governance
`_GovernedPath.write_text()` ruft `bridge.offer(purpose="file_flush")` auf.
Bridge prüft: Ist der Purpose gültig? Ist Parampara OK?
Bridge prüft NICHT: Wohin wird geschrieben? Darf dieser Pfad beschrieben werden?

**Ergebnis:** Jeder gewrappte Service kann überall hinschreiben — Root, vibe_core/, .git/.

### Loch 2: Nur 2 von ~30 Services sind gewrapped
`AUTO_WRAP_SERVICES` enthält nur manifestation_service und prakriti_binding.
InterfacePlugin (7 Renderers), doc_renderer, markdown_ui_manager, alle Cartridge-Tools,
alle opus_assistant Events — schreiben direkt ins Filesystem. Balarama hat sie nie umarmt.

### Loch 3: Universal Protocols sind nicht verdrahtet
`DharmaGuard`, `EnforceProtocol`, `ReadWriteProtocol` existieren als Protocols.
Aber NIEMAND implementiert sie im Hot Path.
`_GovernedPath` → `bridge.offer()` → prüft Purpose + Parampara → schreibt.
Dharma-Check? Nein. Enforce? Nein. ReadWrite-Protocol? Nein.
Die Protocols sind Gesetze ohne Polizei.

## Was ist Govardhan?

Govardhan ist NICHT ein neues System. Govardhan ist die **Verdrahtung** der existierenden Teile.

Krishna hebt Govardhan mit dem kleinen Finger. Govardhan bietet:
- **Schutz** (shelter) — Pfad-Governance: WO darf geschrieben werden?
- **Wasser** (water) — DharmaGuard-Verdrahtung: IST der Write dharmic?
- **Vegetation** (food) — SovereignContext-Propagation: WER schreibt?
- **Zuflucht** (refuge) — Alle Services unter einem Dach, nicht nur 2

Govardhan ist non-different von Krishna (Mahamantra). Er IST der Berg.
Aber als Architektur-Komponente ist er der **Punkt wo alle Governance-Schichten konvergieren**.

### Govardhan = Der Konvergenzpunkt

```
Service will schreiben
    ↓
BalaramaProxy (Identität: WER)
    ↓
_GovernedPath (Interception: WAS)
    ↓
┌─── GOVARDHAN ──────────────────────────┐
│                                         │
│  1. Pfad-Prüfung (WO)                  │
│     - Root geschützt                    │
│     - .git/ verboten                    │
│     - vibe_core/ nur Code, nicht I/O    │
│     - .vibe/ = Maya (erlaubt)           │
│                                         │
│  2. Dharma-Prüfung (WARUM)              │
│     - DharmaGuard.check_saucam()        │
│     - SovereignContext vorhanden?        │
│     - Signatur gültig?                  │
│                                         │
│  3. Enforce (DARF ER)                   │
│     - EnforceProtocol.verify_action()   │
│     - TattvaLimit respektiert?          │
│     - GovernanceGate.can_execute()?     │
│                                         │
└─────────────┬──────────────────────────┘
              ↓
bridge.offer() (Routing: WOHIN im System)
              ↓
Filesystem (Maya)
```

## Was fehlt konkret (das 1%)

1. **GovardhanGate** — Eine Funktion/Klasse die in `_GovernedPath` sitzt,
   ZWISCHEN Interception und `bridge.offer()`. Sie ruft die existierenden
   Protocols auf: Pfad-Check, DharmaGuard, EnforceProtocol.
   Geschätzt: ~50-100 Zeilen.

2. **SovereignContext-Propagation** — `_GovernedPath` weiß nicht WER schreibt.
   `BalaramaProxy` weiß es (hat `_mahajana`, `_position`).
   Der Proxy muss den Context an `_GovernedPath` weitergeben.
   Geschätzt: ~20 Zeilen (Thread-Local oder Closure).

3. **AUTO_WRAP_SERVICES erweitern** — Nicht nur 2, sondern ALLE Services
   die ins Filesystem schreiben. Oder besser: Balarama wrapped automatisch
   alles was `Path` importiert.
   Geschätzt: Konfiguration, kein neuer Code.

4. **Pfad-Regeln** — Abgeleitet, nicht hardcoded. Aus der Mahamantra-Topologie:
   - Root = geschützt (nur CLAUDE.md, CONSTITUTION.md, README.md)
   - `.vibe/` = Maya (Manifestation erlaubt)
   - `vibe_core/` = Yoga (nur Code-Änderungen, keine I/O)
   - `.git/` = verboten (Narasimha-Schutz)
   Geschätzt: ~30 Zeilen Regeln.

## Gesamtaufwand

~100-150 Zeilen neuer Code. Keine neuen Dateien nötig — alles passt in
`proxy.py` (GovardhanGate + Context-Propagation) und `bridge.py` (Pfad-Regeln).

Das ist das fehlende 1%. Die 99% existieren bereits.
Die Frage ist nur: Wo genau sitzt der Konvergenzpunkt?

## Offene Fragen

1. Soll GovardhanGate in `proxy.py` leben (nah an Balarama) oder als
   eigenes Protocol in `protocols/`?
2. Soll die Pfad-Governance aus `soul.yaml` kommen (InvariantChecker)
   oder aus der Mahamantra-Topologie abgeleitet werden?
3. Wie propagiert man SovereignContext durch `_GovernedPath` ohne
   globalen State? (Thread-Local? Closure? Context-Manager?)
