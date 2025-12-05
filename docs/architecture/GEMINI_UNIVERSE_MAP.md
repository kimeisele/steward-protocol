# GEMINI: Universe Map - Der Totale Krieg

> **For:** Gemini (Bulk Worker)
> **From:** Opus (Architect)
> **Date:** 2025-12-05
> **Mission:** Finde ALLE losen Kabel, ALLE Inkonsistenzen, ALLE nicht-fraktalen Patterns

---

## DEINE AUFGABE

Erstelle eine **komplette Bestandsaufnahme** des gesamten Systems:

1. **Was folgt dem fraktalen Pattern?** (manifest.json + *_main.py)
2. **Was folgt NICHT dem Pattern?** (lose Kabel)
3. **Was ist kaputt?** (Import-Fehler, tote Module)
4. **Was fehlt?** (fehlende __init__.py, fehlende exports)

---

## BEKANNTE PROBLEME (Startpunkt)

Diese Fehler wurden bereits entdeckt:

```
Failed to load section module circuits.py: No module named 'phoenix'
Failed to load section module routing.py: No module named 'phoenix'
```

**Wo sind diese Dateien? Was importieren sie falsch?**

---

## ZU SCANNENDE BEREICHE

### 1. Loaders (vibe_core/loaders/)
- [ ] Welche Loaders erben von UnifiedLoader?
- [ ] Welche haben ihr eigenes Pattern?
- [ ] Vollständige Liste mit Status

### 2. Plugins (vibe_core/plugins/)
- [ ] Welche folgen manifest.json Pattern?
- [ ] Welche sind alte .py Dateien?
- [ ] Import-Fehler?

### 3. Sections (vibe_core/phoenix/sections/)
- [ ] Welche haben manifest.json + section_main.py?
- [ ] Welche sind alte .py Dateien (circuits.py, routing.py)?
- [ ] Import-Fehler?

### 4. Agents (steward/system_agents/, agent_city/registry/)
- [ ] Alle mit manifest.json?
- [ ] Alle loadbar?

### 5. Tools (überall verstreut)
- [ ] Wo sind alle Tools definiert?
- [ ] Folgen sie einem Pattern?

### 6. Tests (tests/)
- [ ] Struktur konsistent?
- [ ] Alle importierbar?
- [ ] Hängende/blockierende Tests?

---

## OUTPUT FORMAT

Erstelle eine Tabelle für jeden Bereich:

```markdown
| Component | Location | Pattern | Status | Issue |
|-----------|----------|---------|--------|-------|
| PluginLoader | vibe_core/plugin_loader.py | UnifiedLoader | ✅ OK | - |
| circuits.py | vibe_core/phoenix/sections/circuits.py | OLD | ❌ BROKEN | No module 'phoenix' |
```

---

## PRIORITÄTEN

1. **P0 - BROKEN**: Import-Fehler, nicht ladbar
2. **P1 - LEGACY**: Altes Pattern, sollte migriert werden
3. **P2 - INCOMPLETE**: Fehlendes __init__.py, fehlende exports
4. **P3 - INCONSISTENT**: Funktioniert, aber anderes Pattern

---

## BEFEHLE ZUM SCANNEN

```bash
# Finde alle manifest.json
find vibe_core -name "manifest.json" -type f

# Finde alle *_main.py (fraktales Pattern)
find vibe_core -name "*_main.py" -type f

# Finde alle __init__.py
find vibe_core -name "__init__.py" -type f

# Teste alle Imports
python -c "from vibe_core.phoenix.sections import *" 2>&1

# Finde alle .py Dateien in sections/ die KEINE section_main.py sind
find vibe_core/phoenix/sections -maxdepth 2 -name "*.py" ! -name "__init__.py" ! -name "section_main.py"

# Teste Plugin Discovery
python -c "from vibe_core.plugin_loader import PluginLoader; p,m = PluginLoader.discover(); print(f'{len(p)} plugins')"

# Teste Section Discovery
python -c "from vibe_core.phoenix.section_loader import SectionLoader; s,m = SectionLoader.discover(); print(f'{len(s)} sections')"

# Teste Agent Discovery
python -c "from vibe_core.steward.loader import AgentLoader; a,m = AgentLoader.discover(); print(f'{len(a)} agents')"
```

---

## ERWARTETES ERGEBNIS

Eine vollständige `UNIVERSE_MAP_RESULTS.md` mit:

1. **Inventory Table**: Jede Komponente, ihr Status
2. **Broken List**: Was sofort gefixt werden muss
3. **Migration Plan**: Was nach fraktalem Pattern migriert werden sollte
4. **Recommended Order**: In welcher Reihenfolge fixen

---

## WICHTIG

- **Nicht fixen** - nur dokumentieren!
- **Vollständigkeit** vor Tiefe
- Jeder Import-Fehler ist ein loses Kabel
- Jede Datei ohne manifest.json ist verdächtig

---

*Erstellt von Opus für Gemini - Der totale Krieg gegen Chaos*
