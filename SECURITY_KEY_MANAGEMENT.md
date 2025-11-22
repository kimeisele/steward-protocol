# 🔐 STEWARD Protocol - Private Key Management

## Zusammenfassung: Das "Key Paradoxon"

### Problem
- **Lokal:** Du hast den Private Key auf deinem Laptop, Hacker auch nicht.
- **GitHub Actions (Cloud):** Der Agent läuft jede Nacht auf Githubs Servern. Er muss den Key haben, um zu signieren.

### Lösung: Key Transfer via GitHub Secrets

```
Dein Laptop (sicher)
        ↓
    Private Key lokal generieren
        ↓
    Kopieren → GitHub Secrets (verschlüsselt)
        ↓
GitHub Actions (Ubuntu-Container)
        ↓
    Umgebungsvariable: $AGENT_PRIVATE_KEY
        ↓
    Agent signiert nachts um 4:00 Uhr
```

---

## ✅ Aktuelle Einrichtung

### 1️⃣ **Lokale Key-Struktur**
```
.steward/
└── keys/
    └── private.pem  ← Nur lokal, NIEMALS in Git
```

**In `.gitignore`:**
```
.steward/keys/private.pem
.steward/
```
✅ Schon korrekt konfiguriert!

### 2️⃣ **GitHub Secrets Konfiguration**

**Name:** `AGENT_PRIVATE_KEY`
**Wert:** Der gesamte Inhalt von `.steward/keys/private.pem`

**Ort:** Repository → Settings → Secrets and variables → Actions

**Eigenschaften:**
- ✅ GitHub verschlüsselt den Secret
- ✅ Nur Workflows können ihn lesen (via `${{ secrets.AGENT_PRIVATE_KEY }}`)
- ✅ Logs zeigen keine Secret-Werte
- ❌ Du kannst ihn nicht erneut lesen (nur überschreiben)

---

## 🛡️ Sicherheits-Architektur

### Szenario 1: Hacker hackt deinen GitHub-Account
```
Was der Hacker NICHT kann:
  ❌ Secret im UI auslesen
  ❌ Secret in alten Logs finden
  ✅ Secret in _neuen_ Workflows missbrauchen

Was du tun kannst:
  1. Repository-Secret rotieren (überschreiben)
  2. Neuen Private Key generieren
  3. Public Key in STEWARD.md updaten
  4. Alle alten Signaturen sind kryptographisch ungültig
```

### Szenario 2: Hacker kompromittiert GitHub Actions
```
Wenn Hacker den Container während der Ausführung kompromittiert:
  ✅ Dieser spezifische Lauf ist kompromittiert
  ✅ Zukünftige Läufe sind sicher (neuer Container)
```

### Szenario 3: Dein Laptop wird gestohlen
```
Local key ist verloren, aber:
  ✅ Der Secret in GitHub ist noch sicher (separat verschlüsselt)
  ✅ Der Hacker hat nur den Key, nicht die GitHub-Berechtigung
  ✅ Rotiere den Secret in GitHub → neuer Key generiert
```

---

## 🔄 Key Rotation (falls nötig)

### Falls du den Key kompromittiert verdächtigst:

**Step 1: Neuen Key generieren**
```bash
rm .steward/keys/private.pem
openssl genrsa -out .steward/keys/private.pem 2048
```

**Step 2: GitHub Secret updaten**
- Repository → Settings → Secrets → Edit `AGENT_PRIVATE_KEY`
- Neuen Inhalt einfügen

**Step 3: STEWARD.md updaten**
```bash
python -m steward.cli rotate-key STEWARD.md
```

**Step 4: Commit & Push**
```bash
git add .steward/keys/public.pem STEWARD.md
git commit -m "Security: Rotate STEWARD protocol keys"
git push
```

---

## 📊 Übersicht: Wer hat Zugriff auf was?

| Wer | Lokaler Private Key | GitHub Secret | Public Key (Repo) |
|-----|:--:|:--:|:--:|
| Du (Entwickler) | ✅ Read/Write | ❌ Write only | ✅ Read |
| GitHub Actions | ❌ | ✅ Read | ✅ Read |
| Hacker (Git-Zugriff) | ❌ | ❌ | ✅ Read |
| Hacker (GitHub Account) | ❌ | ⚠️ Nur neue Workflows | ✅ Read |

---

## 🚀 Workflow-Integration (Beispiel)

Falls du einen Signing-Workflow brauchst:

```yaml
jobs:
  sign-manifests:
    runs-on: ubuntu-latest
    env:
      AGENT_PRIVATE_KEY: ${{ secrets.AGENT_PRIVATE_KEY }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4

      - name: Install STEWARD
        run: pip install -e .

      - name: Save key to file
        run: |
          mkdir -p .steward/keys
          echo "$AGENT_PRIVATE_KEY" > .steward/keys/private.pem
          chmod 600 .steward/keys/private.pem

      - name: Sign manifests
        run: |
          python -m steward.cli sign STEWARD.md \
            --key .steward/keys/private.pem

      - name: Clean up
        run: rm .steward/keys/private.pem
```

---

## 🔍 Debugging

### Key-Datei überprüfen
```bash
# Ist die Datei da?
ls -la .steward/keys/private.pem

# Format überprüfen
file .steward/keys/private.pem

# Public Key extrahieren (zum Vergleich)
openssl rsa -in .steward/keys/private.pem -pubout
```

### GitHub Secret Zugang testen
```bash
# In einem Workflow
- name: Check if secret is available
  run: |
    if [ -z "${{ secrets.AGENT_PRIVATE_KEY }}" ]; then
      echo "❌ Secret nicht gefunden!"
      exit 1
    else
      echo "✅ Secret ist verfügbar (Länge: ${#AGENT_PRIVATE_KEY})"
    fi
```

---

## 📝 Checkliste

- [ ] Private Key lokal generiert: `.steward/keys/private.pem`
- [ ] `.steward/keys/private.pem` in `.gitignore`
- [ ] GitHub Secret `AGENT_PRIVATE_KEY` erstellt
- [ ] Secret-Wert überprüft (Länge ~1700 Zeichen)
- [ ] Workflow testet Secret-Zugang
- [ ] 2FA auf GitHub Account aktiviert
- [ ] SSH Key für Git konfiguriert

---

## ⚠️ Häufige Fehler

| Problem | Lösung |
|---------|--------|
| "File not found: private.pem" | `mkdir -p .steward/keys` und neu generieren |
| "Permission denied" | `chmod 600 .steward/keys/private.pem` |
| Secret in Logs sichtbar | GitHub maskiert Secrets automatisch |
| Workflow findet Secret nicht | Check: Secret existiert? Repo-Ebene oder Org-Ebene? |
| "Invalid key format" | PEM muss `-----BEGIN PRIVATE KEY-----` enthalten |

---

## 🔗 Weiterführende Infos

- [OpenSSL RSA Key Generation](https://www.openssl.org/docs/man3.0/man1/openssl-genrsa.html)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
