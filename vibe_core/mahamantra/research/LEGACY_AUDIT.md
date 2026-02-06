# LEGACY AUDIT — Manifestation Layer & Root Pollution

Status: Research (Vorstufe vor jeder Aktion)
Date: 2026-02-06
Branch: feature/diw-refinement

## Das Problem

Das Repo hat 3 Schichten von Legacy-Befall:

### 1. Root-Pollution: 57 .md + 29 .py/.json/.txt

Die Root-Ebene ist eine Müllhalde. Kategorisiert:

**Auto-generiert vom Kernel (ManifestationService + InterfacePlugin):**
- AGENTS.md (0 bytes — leer!)
- ENVOY.md, OPERATIONS.md, SETTINGS.md, TASKS.md (mit @MANIFEST Header)
- STATE.md, HELP.md, INDEX.md (mit AUTO-GENERATED Header)
- OPUS.md (41KB — das größte auto-generierte File)

**AI-Session-Artefakte (von verschiedenen Agents hinterlassen):**
- PAPER.md (128KB), REPORT.md (108KB), NAGA_INTELLIGENCE.md (101KB) — Mega-Dumps
- EXPLORE.md, HEAL.md, CHAT.md, SENIOR_DISCUSSION_MISSING_GEMS.md
- P0_*.md, FIX_PLAN_*.md, GIT_CLEANUP_COMPLETE.md, INTEGRATION_COMPLETE.md
- YAMARAJA_SCHLACHTPLAN.md, MANTRA_OP_JUNIOR_ANALYSIS.md
- Diverse verify_*.py, audit_*.py, test_*.py, *.json Dumps

**Architektur-Referenzen (manche nützlich, manche veraltet):**
- CONSTITUTION.md (17KB — wird von Narasimha geschützt, NICHT ANFASSEN)
- README.md, ARCHITECTURE.md, MAHAMANTRA.md
- CLAUDE.md (8KB — aktiv gepflegt, NICHT ANFASSEN)

**Gesamt: ~600KB+ Müll im Root.**

### 2. Leere Legacy-Ordner: 14 Stück

```
EMPTY: agent-city/ archivist/ artisan/ auditor/ civic/
       diplomatic_bag/ envoy/ forum/ herald/ intelligence/
       library/ sandbox/ science/ starter-packs/ steward/ workspaces/
```

Geister vergangener AI-Sessions. Keine Dateien, keine Funktion.

### 3. ManifestationService: 1509 Zeilen, 55KB

`vibe_core/services/manifestation_service.py` — das Monster.

Was es tut:
- ManifestIndex: Scannt Root nach @MANIFEST .md Files
- ChangeDetector: Hash-basierte Loop-Prevention
- SchemaSection: Section-Ownership (@HUMAN vs @LIVE)
- ManifestationService: Kernel-Service der Plugins in .md rendert
- Template-Engine (Jinja2), Section-Parser, Command-Extraction

Was es produziert: Die auto-generierten .md Files im Root (ENVOY.md, SETTINGS.md, etc.)

Zusätzlich: `InterfacePlugin` (plugins/interface/) mit 7 Renderers produziert
STATE.md, HELP.md, INDEX.md, GIT.md, etc.

## Wer wrapped was (Balarama)

`mahamantra/substrate/proxy.py` → `BalaramaProxy` wrapped 2 Services:
1. `vibe_core.services.manifestation_service` (Jagai)
2. `vibe_core.protocols.prakriti_binding` (Madhai)

Der Proxy injiziert Mahajana-Identität und ersetzt `Path` mit `_GovernedPath`.
Das heißt: Balarama kontrolliert bereits WO geschrieben wird.
Aber er kontrolliert NICHT OB geschrieben wird.

## Analyse: Was hat Wert?

### Kern-Idee (gut gedacht):
- **Inversion of Control**: Plugin liefert Daten, Kernel rendert → richtig
- **Section Ownership**: @HUMAN vs @LIVE Sections → richtig
- **Change Detection**: Hash-basiert, Loop-Prevention → richtig
- **Manifest Index**: O(1) Lookup → richtig

### Problem (schlecht gemacht):
- **Output = Root-Pollution**: Alles landet als .md im Repo-Root
- **1509 Zeilen**: Monolith mit Jinja2, Regex-Parsing, Command-Dispatch
- **Kein Schalter**: Kann nicht deaktiviert werden ohne Code-Änderung
- **Zwei Systeme**: ManifestationService UND InterfacePlugin machen ähnliches
- **Balarama wrapped aber stoppt nicht**: Proxy gibt Identität, verhindert aber nicht die Pollution

## Optionen

### Option A: Deaktivieren (schnell, sicher)
- InterfacePlugin: `render_all()` und `_render_scheduled()` → no-op
- ManifestationService: `tick()` → no-op
- Root .md Files: Einmal aufräumen (git rm die Auto-generierten)
- Leere Ordner: git rm
- Ergebnis: Stille. Kein Müll mehr. Kern-Idee bleibt im Code für später.

### Option B: Migrieren (aufwändig, sauber)
- Kern-Idee extrahieren als kleine Funktion in mahamantra/
- ManifestationService zerlegen: Index, Detector, Renderer separat
- Output nach .vibe/ oder .steward/ statt Root
- InterfacePlugin und ManifestationService vereinen
- Ergebnis: Einheitliche Manifestationsebene, kein Root-Müll.

### Option C: Rip & Replace (radikal)
- ManifestationService + InterfacePlugin komplett entfernen
- Kern-Idee (IoC, Section Ownership) als 50-Zeilen-Funktion neu
- Nur manifestieren wenn explizit befohlen (Krishna befiehlt → es geschieht)
- Ergebnis: Sauber, aber Risiko dass Kernel-Boot bricht.

## Empfehlung

**Option A zuerst, dann B wenn nötig.**

Begründung:
1. Deaktivieren ist reversibel und sofort wirksam
2. Root-Cleanup gibt sofort sichtbares Ergebnis
3. Die Kern-Idee bleibt im Code — nichts geht verloren
4. Migration kann danach in Ruhe passieren, ohne Zeitdruck
5. "Do not patch the past" = Deaktivieren, nicht Reparieren

Was NICHT gemacht werden sollte:
- Blind cutten (ManifestationService hat Abhängigkeiten im Kernel)
- Partial fixes (ein .md löschen, andere lassen)
- Neuen Code schreiben bevor der alte still ist
