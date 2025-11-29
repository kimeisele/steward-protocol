# 🏗️ OPERATIONS DASHBOARD

**Last Updated:** 2025-11-29T21:45:39.126308
**Status:** RUNNING

## 📊 Kernel Status
- Kernel: RUNNING
- Agents Registered: 26
- Queue Length: 0
- Completed Tasks: 0
- Total Events: 0

## 🤖 Agent Status

### steward
- agent_id: steward
- name: The Steward
- status: RUNNING
- capabilities: ['discovery', 'registration', 'governance']

### discoverer
- agent_id: discoverer
- name: DISCOVERER
- status: RUNNING
- capabilities: ['discovery', 'registration', 'governance']

### auditor
- agent_id: auditor
- name: AUDITOR
- status: RUNNING
- domain: SECURITY
- capabilities: ['verify_changes', 'auditing', 'constitutional_verdict']
- description: Quality gate: verifies code syntax and linting before commit

### herald
- agent_id: herald
- name: HERALD
- status: RUNNING
- domain: MEDIA
- capabilities: ['content_generation', 'broadcasting', 'research', 'strategy']
- broadcast_metrics: {'last_execution_id': None, 'total_events_recorded': 0, 'content_published_count': 0, 'content_generated_count': 0, 'content_rejected_count': 0, 'event_log_path': 'data/events/herald.jsonl', 'last_result_status': None}
- connectivity: {'twitter': False, 'reddit': False}
- governance: {'safe_mode': False, 'last_failure': None}

### oracle
- agent_id: oracle
- name: ORACLE
- status: RUNNING
- domain: INTROSPECTION
- capabilities: ['introspection', 'audit_trail', 'system_health']
- description: System introspection and explanation agent

### envoy
- agent_id: envoy
- name: ENVOY
- status: RUNNING
- domain: ORCHESTRATION
- capabilities: ['orchestration', 'governance', 'broadcasting', 'registry', 'auditing']
- orchestration_metrics: {'city_control_initialized': False, 'operations_logged_in_memory': 0, 'operations_logged_persistent': 0, 'kernel_injected': False, 'log_path': '/tmp/vibe_os/agents/envoy/logs/envoy_operations.jsonl', 'hil_assistant_active': True}

### science
- agent_id: science
- name: SCIENCE
- status: RUNNING
- capabilities: ['research', 'web_search', 'fact_synthesis']

### watchman
- agent_id: watchman
- name: WATCHMAN
- status: RUNNING
- domain: ENFORCEMENT
- capabilities: ['integrity_scanning', 'account_freezing', 'violation_detection']
- description: System integrity enforcer and governance enforcer

### archivist
- agent_id: archivist
- name: ARCHIVIST
- status: RUNNING
- domain: INFRASTRUCTURE
- capabilities: ['seal_history', 'ledger']
- description: History keeper: seals verified code into git history

### supreme_court
- agent_id: supreme_court
- name: SUPREME_COURT
- status: healthy
- domain: GOVERNANCE
- capabilities: ['appeals', 'precedent']

### scribe
- agent_id: scribe
- name: SCRIBE
- status: RUNNING
- capabilities: ['documentation', 'introspection', 'publishing']

### chronicle
- agent_id: chronicle
- name: CHRONICLE
- status: operational
- tasks_processed: 0
- tasks_successful: 0
- git_status: {'success': True, 'branch': 'claude/refactor-citizen-agents-yaml-01RRYtsFqZAZLBpEZcLwLqJr', 'dirty': True, 'files_changed': ['M OPERATIONS.md', '?? agent_city/registry/librarian/steward.json', '?? test_end_to_end.py']}

### civic
- agent_id: civic
- name: CIVIC
- status: RUNNING
- capabilities: ['registry', 'licensing', 'ledger', 'governance']

### engineer
- agent_id: engineer
- name: ENGINEER
- status: RUNNING
- domain: ENGINEERING
- capabilities: ['manifest_reality', 'agent_scaffolding', 'code_generation']
- description: Builder agent: manifests code and scaffolds new agents

### forum
- agent_id: forum
- name: FORUM
- status: RUNNING
- domain: GOVERNANCE
- capabilities: ['governance', 'voting', 'proposal_management']
- governance_metrics: {'total_proposals': 0, 'open_proposals': 0, 'approved_proposals': 0, 'executed_proposals': 0, 'rejected_proposals': 0, 'total_votes_recorded': 0, 'next_proposal_id': 1, 'proposals_path': '/tmp/vibe_os/agents/forum/governance/proposals', 'votes_ledger_path': '/tmp/vibe_os/agents/forum/governance/votes/votes.jsonl', 'executed_archive_path': '/tmp/vibe_os/agents/forum/governance/executed'}

### ping
- agent_id: ping
- name: PING
- status: RUNNING
- capabilities: ['ping', 'status']

### market
- agent_id: market
- name: MARKET
- status: RUNNING
- capabilities: ['trading']

### librarian
- agent_id: librarian
- name: LIBRARIAN
- status: RUNNING
- capabilities: []

### lens
- agent_id: lens
- name: LENS
- status: RUNNING
- capabilities: ['observation']

### temple
- agent_id: temple
- name: TEMPLE
- status: RUNNING
- capabilities: ['offerings']

### ambassador
- agent_id: ambassador
- name: AMBASSADOR
- status: RUNNING
- capabilities: ['outreach']

### dhruva
- agent_id: dhruva
- name: DHRUVA
- status: RUNNING
- capabilities: ['data_ethics', 'truth_verification']

### pulse
- agent_id: pulse
- name: PULSE
- status: RUNNING
- capabilities: ['twitter_api', 'engagement_tracking']

### artisan
- agent_id: artisan
- name: ARTISAN
- status: RUNNING
- capabilities: ['media_production']

### mechanic
- agent_id: mechanic
- name: MECHANIC
- status: RUNNING
- capabilities: ['maintenance']

### agora
- agent_id: agora
- name: AGORA
- status: RUNNING
- capabilities: ['community_management']

---
*This dashboard is auto-generated by the kernel heartbeat.*