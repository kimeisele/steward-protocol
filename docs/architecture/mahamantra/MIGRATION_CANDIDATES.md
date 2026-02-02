# MIGRATION CANDIDATES

**95 Dateien** außerhalb von `vibe_core/mahamantra/` importieren von mahamantra.

---

## PRIORITÄT 1: DUPLIKATE ELIMINIEREN

### protocols/substrate/ → mahamantra/substrate/
```
vibe_core/protocols/substrate/mantra/varna.py
vibe_core/protocols/substrate/mantra/acintya.py
vibe_core/protocols/substrate/mantra/routing.py
vibe_core/protocols/substrate/tattva.py
vibe_core/protocols/substrate/samskara.py
vibe_core/protocols/substrate/byte.py
```
**Action:** Merge oder Delete. Eine Quelle der Wahrheit.

### protocols/mahajanas/ → mahamantra/mahajanas/
```
vibe_core/protocols/mahajanas/brahma/
vibe_core/protocols/mahajanas/narada/
vibe_core/protocols/mahajanas/prithu/
vibe_core/protocols/mahajanas/prahlada/
vibe_core/protocols/mahajanas/yamaraja/
... (12 total)
```
**Action:** Move to `vibe_core/mahamantra/mahajanas/`

---

## PRIORITÄT 2: SERVICES → MAHAMANTRA

### services/ → mahamantra/venu/ oder reactor/
```
vibe_core/services/venu_service.py      → mahamantra/venu/
vibe_core/services/brahma_service.py    → mahamantra/kernel/
vibe_core/services/maha_compute_service.py → mahamantra/reactor/
vibe_core/services/chat_*.py            → mahamantra/adapters/
```

---

## PRIORITÄT 3: CLI CONSOLIDATION

### cli/ → mahamantra/venu/cli/
```
vibe_core/cli/kirtan_cli.py
vibe_core/cli/lotus_cli.py
vibe_core/cli/unified_cli.py
vibe_core/cli/governance_cli.py
vibe_core/cli/gates.py
vibe_core/cli/main.py
vibe_core/cli/command_registry.py
vibe_core/cli/legacy.py
```
**Action:** Consolidate. Ein CLI entry point.

---

## PRIORITÄT 4: ROOT CLEANUP

### Root files → mahamantra/kernel/
```
./boot.py              → mahamantra/kernel/boot.py
./kernel_impl.py       → mahamantra/kernel/impl.py
./verify_*.py          → tests/ oder delete
```

---

## ZIEL-STRUKTUR

```
vibe_core/
├── mahamantra/           # DER KERN
│   ├── protocols/        # Position 15 - Yamaraja (Gesetz)
│   │   └── seed/         # 7 Axiome + Derivationen
│   ├── substrate/        # Position 4 - Prithu (Feld)
│   ├── adapters/         # Position 3 - Narada (Brücke)
│   ├── venu/             # Flöte - Orchestration
│   │   └── cli/          # Command Line Interface
│   ├── reactor/          # Position 9 - Prahlada (Transformation)
│   ├── kernel/           # Position 1 - Brahma (Schöpfung)
│   └── mahajanas/        # Die 12 Autoritäten
│       ├── brahma/       # 1. Creation
│       ├── narada/       # 2. Communication
│       ├── vyasa/        # 3. Compilation
│       ├── shambhu/      # 4. Destruction
│       ├── kumaras/      # 5. Purity
│       ├── kapila/       # 6. Analysis
│       ├── manu/         # 7. Law
│       ├── prahlada/     # 8. Devotion
│       ├── janaka/       # 9. Detachment
│       ├── bhishma/      # 10. Vows
│       ├── bali/         # 11. Surrender
│       └── yamaraja/     # 12. Justice
├── plugins/              # External extensions (bleiben)
├── cartridges/           # Loadable modules (bleiben)
└── gateway/              # External API (→ mahamantra/adapters/)
```

---

## ERSTER SCHRITT

**Migriere `vibe_core/protocols/mahajanas/` → `vibe_core/mahamantra/mahajanas/`**

Warum zuerst?
1. Klare Abgrenzung (12 Mahajanas = 12 Ordner)
2. Keine Duplikate - nur Verschieben
3. Mahamantra-aligned (12 ist MAHAJANA_COUNT)
4. Gibt uns Template für weitere Migration

---

## SANKIRTAN COMMAND

```bash
# Vorschau: Was würde migriert?
python -m vibe_core.mahamantra.tools.sankirtan preview protocols/mahajanas

# Ausführen:
python -m vibe_core.mahamantra.tools.sankirtan migrate protocols/mahajanas --to mahamantra/mahajanas
```

---

**Die Frage:** Soll ich mit Priorität 1 (mahajanas/) anfangen?
