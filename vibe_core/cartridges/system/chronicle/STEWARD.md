# 🗡️ CHRONICLE - The Keeper of Temporal Lines 🗡️

**Agent ID:** `chronicle`
**Version:** 1.0.0
**Domain:** INFRASTRUCTURE
**Status:** Operational

---

## 🎯 Mission

CHRONICLE is the **Vyasa** of Agent City - the historian, scribe, and keeper of temporal lines. It manages:

1. **Immutable Code History:** Git commits with cryptographic signatures
2. **Timeline Navigation:** Read git logs, query commit history
3. **Reality Forking:** Create branches for parallel development
4. **Code Manifestation:** Stage files and prepare commits

In the Vedic tradition, Vyasa composed the Mahabharata. CHRONICLE composes the narrative of your codebase.

---

## 🛠️ Architecture

### Components

```
chronicle/
├── tools/
│   └── git_tools.py          # Git operations library (subprocess-based)
├── cartridge_main.py          # VibeAgent implementation
├── cartridge.yaml             # Agent manifest
└── STEWARD.md                 # This file
```

### Git Tools (`git_tools.py`)

The **GitTools** class provides safe, deterministic Git operations:

- **seal_history(message, files, sign)** → Create signed commits
- **read_history(pattern, limit)** → Query git log
- **fork_reality(branch_name)** → Create branches
- **manifest_reality(files)** → Stage files
- **get_status()** → Get current git status
- **push_to_remote(remote, branch)** → Push commits

All operations:
- Use `subprocess` for maximum control
- Support cryptographic signing (via `-S` flag)
- Include comprehensive audit logging
- Return structured results (success, data, message)

### ChronicleCartridge (VibeAgent)

The CHRONICLE Agent is a full VibeAgent that:

- Implements the VibeOS protocol (`process()`, `get_manifest()`, `report_status()`)
- Receives tasks from the kernel scheduler
- Dispatches to git_tools for execution
- Records results in the kernel ledger
- Swears the Constitutional Oath for governance

---

## 📋 Actions

### 1. seal_history - Create Signed Commits

**Purpose:** Commit code changes with cryptographic signature (seals the timeline).

**Request:**
```json
{
  "action": "seal_history",
  "params": {
    "message": "feat: Add new feature",
    "files": ["src/module.py", "tests/test_module.py"],
    "sign": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "seal_history",
  "commit_hash": "a1b2c3d4e5f6...",
  "message": "feat: Add new feature",
  "timestamp": "2025-11-26T12:00:00Z"
}
```

**Notes:**
- If `files` is omitted, commits all staged changes
- `sign=true` creates a GPG-signed commit
- Message should follow conventional commit format

### 2. read_history - Query Git Log

**Purpose:** Read the timeline (query git commits).

**Request:**
```json
{
  "action": "read_history",
  "params": {
    "pattern": "src/",
    "limit": 20
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "read_history",
  "commits": [
    {
      "hash": "a1b2c3d4e5f6...",
      "hash_short": "a1b2c3d",
      "author": "Alice Engineer",
      "email": "alice@example.com",
      "timestamp": "2025-11-26T12:00:00Z",
      "subject": "feat: Add authentication"
    }
  ],
  "message": "Found 10 commits"
}
```

**Notes:**
- `pattern` filters commits that touched specific files
- Returns commits in reverse chronological order (newest first)
- Each commit includes full metadata

### 3. fork_reality - Create Branches

**Purpose:** Create new git branches (fork possible universes).

**Request:**
```json
{
  "action": "fork_reality",
  "params": {
    "branch_name": "feature/experimental"
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "fork_reality",
  "branch": "claude/feature/experimental",
  "message": "Branch created: claude/feature/experimental"
}
```

**Notes:**
- Branches are auto-prefixed with `claude/` for organization
- New branch is checked out immediately
- Safe: never overwrites existing branches

### 4. manifest_reality - Stage Files

**Purpose:** Stage files for commitment (prepare the timeline).

**Request:**
```json
{
  "action": "manifest_reality",
  "params": {
    "files": ["src/module.py", "README.md"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "manifest_reality",
  "staged_files": ["src/module.py", "README.md"],
  "message": "Staged 2 files"
}
```

**Notes:**
- Staging is non-destructive (doesn't modify files)
- Failed stages are logged but don't fail the whole action
- Subsequent `seal_history` will commit staged files

---

## 🔐 Constitutional Oath

CHRONICLE swears the Constitutional Oath at initialization:

```python
self.swear_constitutional_oath()
```

This binding ensures:
- All commits are recorded in the immutable ledger
- Operations are audited and traceable
- The agent is cryptographically bound to the system constitution

If oath swearing fails, CHRONICLE still boots (non-critical), but governance features are unavailable.

---

## 📊 Playbook Integration

CHRONICLE can be invoked from Playbooks via `CALL_AGENT`:

```yaml
- type: CALL_AGENT
  agent_id: chronicle
  method: seal_history
  params:
    message: "refactor: Simplify data pipeline"
    files:
      - src/pipeline.py
      - src/config.py
```

This enables deterministic code generation workflows where agents can:
1. Write code (file operations)
2. Stage changes (manifest_reality)
3. Commit with auditable messages (seal_history)
4. Push to remote (push_to_remote)

---

## 🛡️ Safety & Constraints

### What CHRONICLE Does NOT Do

- ❌ Does **not** delete branches or commits
- ❌ Does **not** force-push or rewrite history
- ❌ Does **not** modify `.git/` directly
- ❌ Does **not** auto-push without explicit request
- ❌ Does **not** execute arbitrary shell commands

### What CHRONICLE Does Safely

- ✅ Creates signed commits (via git -S)
- ✅ Creates branches from current HEAD
- ✅ Stages files for commitment
- ✅ Reads immutable history
- ✅ Logs all operations for audit

### Git Configuration

CHRONICLE uses the system git configuration:
- Signing key: `git config user.signingKey` (must be configured)
- Author: `git config user.name` and `git config user.email`

If signing is not configured, commits are unsigned (but still created).

---

## 🚀 Initialization

### Via Kernel Boot

CHRONICLE is registered in `run_server.py`:

```python
from chronicle.cartridge_main import ChronicleCartridge

cartridges = [
    # ... other agents ...
    ("chronicle", ChronicleCartridge(), "Temporal agent: git operations"),
]
```

At kernel boot:
1. ChronicleCartridge() is instantiated
2. Oath mixin is initialized
3. Constitutional Oath is sworn (if available)
4. Git tools are initialized (verifies repo)
5. Agent is registered with kernel
6. Manifest is recorded

### Standalone Usage

For testing or direct invocation:

```python
from chronicle.cartridge_main import ChronicleCartridge
from vibe_core import Task

agent = ChronicleCartridge()

task = Task(
    task_id="test_seal",
    agent_id="chronicle",
    input={
        "action": "seal_history",
        "params": {
            "message": "test: Initial commit",
            "files": ["test.txt"]
        }
    }
)

result = agent.process(task)
print(result)
```

---

## 📈 Metrics & Monitoring

CHRONICLE reports status via `report_status()`:

```json
{
  "agent_id": "chronicle",
  "name": "CHRONICLE",
  "status": "operational",
  "tasks_processed": 42,
  "tasks_successful": 40,
  "git_status": {
    "branch": "main",
    "dirty": false,
    "files_changed": []
  }
}
```

This is included in kernel heartbeats and the OPERATIONS.md dashboard.

---

## 🧠 Philosophy

> *"Every piece of code has a story. I am the keeper of that story."*

CHRONICLE operates on three principles:

1. **Immutability:** All commits are permanent. History cannot be erased.
2. **Transparency:** Every operation is logged and auditable.
3. **Integrity:** Cryptographic signatures bind commits to the constitution.

The system is self-healing: if CHRONICLE fails, the git repository remains intact. Future agents can read the history and continue the work.

---

## 🔗 Related Components

- **vibe_core/bridge.py** - Import bridge (constitutional oath access)
- **run_server.py** - Kernel bootloader (registers CHRONICLE)
- **envoy** - User interface (can request CHRONICLE actions via playbooks)
- **archivist** - Broadcast auditor (records CHRONICLE commits in ledger)

---

## 📝 Example Workflow

### Scenario: Refactor a Module

```
1. ENVOY receives user request: "Refactor the auth module"
2. ENVOY routes to appropriate playbook
3. ENGINEER makes code changes (file system)
4. ENGINEER requests CHRONICLE to seal changes:
   - manifest_reality([modified_files])
   - seal_history("refactor: Simplify auth module")
5. CHRONICLE creates signed commit, updates git log
6. Kernel records event in ledger
7. ARCHIVIST verifies commit was recorded
8. Playbook completes, user notified
```

---

## 🐛 Troubleshooting

### Git Repository Not Found

**Error:** "Not a git repository"

**Solution:**
- Verify you're running from the project root
- Ensure `.git/` directory exists
- Initialize repo if needed: `git init`

### Signing Key Not Configured

**Warning:** "Commit created but not signed"

**Solution:**
- Configure signing key: `git config user.signingkey <KEY_ID>`
- Or pass `sign=false` to seal_history

### Branch Already Exists

**Error:** "fatal: A branch named 'X' already exists"

**Solution:**
- Use a different branch name
- Delete old branch first: `git branch -d old_branch`

---

## 📚 Further Reading

- [Git Basics](https://git-scm.com/book/en/v2)
- [GPG Signing](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [VibeAgent Protocol](../vibe_core/agent_protocol.py)
- [Constitutional Oath](../steward/constitutional_oath.py)
