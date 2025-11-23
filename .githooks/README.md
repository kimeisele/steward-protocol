# Git Hooks - Automated Quality Gates

Diese Hooks laufen AUTOMATISCH vor jedem Commit und verhindern broken Code in den Repo.

## Installation (neue Entwickler)

```bash
git clone <repo>
cd steward-protocol
git config core.hooksPath .githooks
```

Das ist es! Die Hooks sind jetzt aktiv.

## Was läuft automatisch?

### `pre-commit` Hook
- ✅ Läuft IMMER vor `git commit`
- ✅ Testet: Health Check, E2E Pipeline, Dependencies
- ✅ Blockiert Commit wenn Tests fehlschlagen
- ✅ Zeigt klare Fehlermeldungen

## Beispiel: Test fehlgeschlagen

```
🧪 Running HERALD E2E tests before commit...

[TEST] Health Check
❌ FAILED: Health Check
STDERR: Missing module: praw

🔴 COMMIT BLOCKED: E2E tests failed
Fix the issues above and try again
```

**Fix:** Dependencies installieren
```bash
pip install -r examples/herald/requirements.txt
```

Dann nochmal versuchen zu committen:
```bash
git commit -m "..."
```

## Bypass (wenn absolut nötig)

```bash
git commit --no-verify
```

⚠️ **NICHT verwenden!** Das ist für echte Notfälle. Nutze es nicht regelmäßig.
