-- VIBE Agency SQLite Schema (v2)
-- VIMANA PERSISTENCE LAYER (GAD-3000)

-- ========================================================================
-- MISSIONS (Project Lifecycle Tracking)
-- ========================================================================
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_uuid TEXT NOT NULL UNIQUE,
    phase TEXT NOT NULL CHECK (phase IN ('PLANNING', 'CODING', 'TESTING', 'DEPLOYMENT', 'MAINTENANCE', 'PRODUCTION')),
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    created_at TEXT NOT NULL,
    completed_at TEXT,
    updated_at TEXT,
    planning_sub_state TEXT CHECK (planning_sub_state IN ('RESEARCH', 'BUSINESS_VALIDATION', 'FEATURE_SPECIFICATION')),
    max_cost_usd REAL,
    current_cost_usd REAL DEFAULT 0.0,
    alert_threshold REAL DEFAULT 0.80,
    cost_breakdown TEXT,
    owner TEXT,
    description TEXT,
    api_version TEXT DEFAULT 'agency.os/v1alpha1',
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_missions_uuid ON missions(mission_uuid);
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_phase ON missions(phase);

-- ========================================================================
-- TOOL CALLS (Audit Trail)
-- ========================================================================
CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    args TEXT NOT NULL,
    result TEXT,
    timestamp TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    success INTEGER NOT NULL,
    error_message TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_mission ON tool_calls(mission_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_timestamp ON tool_calls(timestamp);

-- ========================================================================
-- DECISIONS (Provenance)
-- ========================================================================
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    decision_type TEXT NOT NULL,
    rationale TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    context TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_decisions_mission ON decisions(mission_id);

-- ========================================================================
-- AGENT MEMORY (Key-Value Storage)
-- ========================================================================
CREATE TABLE IF NOT EXISTS agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    ttl INTEGER,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
    UNIQUE(mission_id, key)
);

CREATE INDEX IF NOT EXISTS idx_agent_memory_mission ON agent_memory(mission_id);

-- ========================================================================
-- PLAYBOOK RUNS (Metrics)
-- ========================================================================
CREATE TABLE IF NOT EXISTS playbook_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    playbook_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    success INTEGER,
    metrics TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_playbook_runs_mission ON playbook_runs(mission_id);

-- ========================================================================
-- TASKS (Hierarchical Task Tracking) - VIMANA CORE
-- ========================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    parent_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- ========================================================================
-- SESSION NARRATIVE (ProjectMemory)
-- ========================================================================
CREATE TABLE IF NOT EXISTS session_narrative (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    session_num INTEGER NOT NULL,
    summary TEXT NOT NULL,
    date TEXT NOT NULL,
    phase TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
    UNIQUE(mission_id, session_num)
);

CREATE INDEX IF NOT EXISTS idx_session_narrative_mission ON session_narrative(mission_id);

-- ========================================================================
-- ARTIFACTS (SDLC Tracking)
-- ========================================================================
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('planning', 'code', 'test', 'deployment')),
    artifact_name TEXT NOT NULL,
    ref TEXT,
    path TEXT,
    url TEXT,
    branch TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_artifacts_mission ON artifacts(mission_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);

-- ========================================================================
-- QUALITY GATES (GAD-004 Compliance)
-- ========================================================================
CREATE TABLE IF NOT EXISTS quality_gates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    gate_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'skipped')),
    details TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quality_gates_mission ON quality_gates(mission_id);

-- ========================================================================
-- DOMAIN CONCEPTS/CONCERNS (ProjectMemory)
-- ========================================================================
CREATE TABLE IF NOT EXISTS domain_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    concept TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
    UNIQUE(mission_id, concept)
);

CREATE TABLE IF NOT EXISTS domain_concerns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    concern TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
    UNIQUE(mission_id, concern)
);

-- ========================================================================
-- TRAJECTORY (ProjectMemory)
-- ========================================================================
CREATE TABLE IF NOT EXISTS trajectory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL UNIQUE,
    current_phase TEXT NOT NULL,
    current_focus TEXT,
    completed_phases TEXT,
    blockers TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

-- ========================================================================
-- ROADMAPS (High-Level Planning) - VIMANA EXTENSION
-- ========================================================================
CREATE TABLE IF NOT EXISTS roadmaps (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    missions TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_roadmaps_created ON roadmaps(created_at);
