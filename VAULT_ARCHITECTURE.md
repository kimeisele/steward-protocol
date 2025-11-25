# CIVIC VAULT: SECURITY ARCHITECTURE

**Status:** PHASE 4 - PRODUCTION READY
**Last Updated:** 2025-11-25
**Compliance:** GAD-000 (Operator Inversion & Radical Safety)

---

## PHILOSOPHY

API Keys are **not configuration**. They are **ASSETS** managed by the collective.

In Varnashrama terms:
- **Brahmane (Science):** The researcher who needs the key to perform work
- **Vaishya (Civic Vault):** The merchant who owns the keys and leases them
- **Kshatriya (Watchman):** The enforcer who audits access
- **Shudra (Archivist):** The record-keeper who preserves audit trails

**The Golden Rule:** Agents do NOT own secrets. They LEASE them using Credits.

---

## ARCHITECTURE

### 1. THE VAULT (`civic/tools/vault.py`)

The `CivicVault` class manages encrypted secret storage and leasing.

**Core Methods:**
```python
vault.store_secret(key_name: str, raw_value: str)
    # Encrypt a raw secret and store in database
    # Called ONCE during secure_ingest.py

vault.lease_secret(agent_id: str, key_name: str, bank) -> str
    # Lease a secret to an agent
    # Deducts fees from agent's credit balance
    # Returns decrypted secret (temporary use)
    # Logs transaction immutably

vault.get_secret(key_name: str) -> str
    # LOW-LEVEL: Retrieve and decrypt secret
    # Used internally by lease_secret
    # NEVER call directly from agents

vault.rotate_secret(key_name: str, new_value: str)
    # Update a secret (key rotation)
    # Updates timestamp, maintains audit trail
```

**Database Schema:**

```sql
-- Encrypted secrets (at rest)
CREATE TABLE vault_assets (
    key_name TEXT PRIMARY KEY,
    encrypted_value BLOB NOT NULL,
    created_at DATETIME,
    rotated_at DATETIME
);

-- Access audit trail (immutable)
CREATE TABLE vault_leases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT,
    key_name TEXT,
    lease_time DATETIME,
    credits_charged INTEGER,
    tx_id TEXT  -- Links to CivicBank.transactions
);
```

### 2. ENCRYPTION STRATEGY

**Algorithm:** Fernet (AES-128-CBC with HMAC)
**Key Management:** Single Master Key per deployment

**Master Key Location:**
```
data/security/master.key
```

**Master Key Properties:**
- Auto-generated on first run (if doesn't exist)
- Stored **outside** the codebase (in .gitignore)
- Protected with `chmod 600` (read-only by owner)
- **NEVER** committed to git
- **NEVER** shared in plaintext

**Key Rotation (Manual):**
```bash
# 1. Generate new master key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"

# 2. Backup old key
cp data/security/master.key data/security/master.key.backup.$(date +%s)

# 3. Replace with new key
echo "new_key_here" > data/security/master.key

# 4. Re-encrypt all secrets (manual for now)
# TODO: Implement vault.reencrypt_all() method
```

### 3. INGESTION FLOW

**Step 1: Set Environment Variable (CI/CD Secrets)**
```bash
# In GitHub Settings → Secrets:
TAVILY_API_KEY = "actual_key_value"

# In Replit Secrets:
TAVILY_API_KEY = "actual_key_value"
```

**Step 2: Run Ingestion Script**
```bash
# Reads TAVILY_API_KEY from environment
python3 scripts/secure_ingest.py --ingest

# Output:
# ✅ Secret stored in vault: tavily_api
# 🔒 Vault ASSETS
# ✅ INGESTION COMPLETE
```

**Step 3: Vault Contains Encrypted Secret**
- Master Key: `data/security/master.key`
- Encrypted Data: `data/economy.db` (vault_assets table)
- Both are .gitignore'd

### 4. LEASING PATTERN

When an agent needs an API key:

```python
# AGENT (Science)
from civic.tools.economy import CivicBank

bank = CivicBank()
vault = bank.vault

try:
    # Lease the secret (costs 5 Credits)
    api_key = vault.lease_secret(
        agent_id="science",
        key_name="tavily_api",
        bank=bank
    )

    # Use the key (temporarily in memory)
    client = TavilyClient(api_key=api_key)
    results = client.search("query")

    # Key is never stored, only held in RAM during use
    del api_key  # Explicitly clear from memory

except InsufficientFundsError:
    # Agent has no credits
    # Safe degradation: use cached data instead
    results = cache.get("previous_results")
```

**What Happens in the Vault:**
1. Check vault_assets for "tavily_api" → Found
2. Check agent's balance (science) → 50 Credits? YES
3. Deduct fee: science's balance -= 5
4. Create transaction record: `science → VAULT: 5 Credits (LEASE_SECRET_tavily_api)`
5. Decrypt secret from vault_assets
6. Return decrypted value
7. Log lease: insert into vault_leases

**Result:**
```
science: 50 Credits → 45 Credits ✅
VAULT: 0 Credits → 5 Credits ✅
vault_leases: 1 new record with timestamp, agent, cost ✅
```

### 5. SECURITY GUARANTEES

| Property | Guarantee | Verification |
|----------|-----------|---|
| **Encryption** | All secrets encrypted with Fernet before storage | `.encrypted_value` is BLOB, not TEXT |
| **Master Key Security** | Master key never in version control | .gitignore includes `data/security/master.key` |
| **Audit Trail** | Every access logged immutably | `vault_leases` appended-only table |
| **Economic Enforcement** | Agents must pay to use secrets | Credits deducted via CivicBank.transfer() |
| **Least Privilege** | Agents never own secrets, only borrow | Decrypted value exists only in RAM during use |
| **Atomicity** | Lease = deduction + logging (all-or-nothing) | SQLite transaction semantics |

---

## DEPLOYMENT GUIDE

### Local Development

```bash
# 1. Create environment file (NEVER COMMIT)
cat > .env << 'EOF'
TAVILY_API_KEY=sk_your_test_key_here
EOF

# 2. Run ingestion (encrypts key into vault)
python3 scripts/secure_ingest.py --ingest

# 3. Verify vault
python3 scripts/secure_ingest.py --list-assets

# 4. Clean up .env (key is now in vault)
rm .env
```

### CI/CD (GitHub Actions)

```yaml
name: Ingest Secrets on Deploy
on: [push]
jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Ingest Secrets into Vault
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
        run: |
          python3 scripts/secure_ingest.py --ingest

      - name: Run Research Yagya
        run: |
          python3 scripts/research_yagya.py
```

---

## EMERGENCY PROCEDURES

### Scenario 1: Lost Master Key

**Problem:** `data/security/master.key` deleted/corrupted
**Impact:** Cannot decrypt secrets in vault
**Recovery:**
1. Restore from backup: `cp data/security/master.key.backup.TIMESTAMP data/security/master.key`
2. If no backup: Regenerate key, re-ingest secrets from CI/CD
3. Implement key escrow (offline cold storage) for future

### Scenario 2: Secret Compromised

**Problem:** API key leaked/stolen
**Recovery:**
1. Rotate secret in upstream service (e.g., Tavily dashboard)
2. Get new key
3. Run: `python3 scripts/secure_ingest.py --ingest` with new key
4. Vault automatically overwrites old encrypted value

### Scenario 3: Audit Trail Needed

**Problem:** "Who accessed what and when?"
**Solution:**
```python
from civic.tools.economy import CivicBank

bank = CivicBank()
vault = bank.vault

# Full audit
leases = vault.lease_history(limit=100)
for lease in leases:
    print(f"{lease['agent_id']} accessed {lease['key_name']} at {lease['lease_time']}")
    print(f"  Cost: {lease['credits_charged']} Credits, TX: {lease['tx_id']}")
```

---

## FUTURE ENHANCEMENTS

- [ ] **Multi-Signature Approval:** Sensitive secrets require N approvals before lease
- [ ] **Rate Limiting:** Max leases per agent per hour
- [ ] **Secret Rotation:** Automatic key refresh on schedule
- [ ] **Vault Recovery:** Master key escrow (Shamir's Secret Sharing)
- [ ] **Per-Secret Permissions:** Different agents can access different secrets
- [ ] **Time-Limited Leases:** Secret auto-revoked after N seconds

---

## REFERENCES

- **GAD-000:** Operator Inversion & Radical Safety
- **Varnashrama:** Four-caste system in agent society
- **Fernet:** https://cryptography.io/hazmat/primitives/symmetric-encryption/#fernet
- **OWASP Secret Management:** https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

---

**Built by:** The Steward Protocol Collective
**Philosophy:** "Secrets are assets, not config."
