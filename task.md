# System Verification Protocol - Phoenix Test v3.0

## 1. Kernel Boot & Recovery
- [x] **1.1 Clean Slate Boot** <!-- id: 0 -->
    - [x] Delete artifacts (`data/`, `__pycache__`, `*.db`) <!-- id: 1 -->
    - [x] Run `boot.py` & verify auto-install/detection <!-- id: 2 -->
    - [x] Verify agent discovery (19 agents) <!-- id: 3 -->
- [x] **1.2 Crash & Recovery** <!-- id: 4 -->
    - [x] Record event, kill process, restart <!-- id: 5 -->
    - [x] Verify event restoration <!-- id: 6 -->
- [x] **1.3 Dependency Hell** <!-- id: 7 -->
    - [x] Corrupt `pyproject.toml` & verify graceful error <!-- id: 8 -->

## 2. Governance Gate
- [x] **2.1 Oath Bypass** <!-- id: 9 -->
    - [x] Register agent without oath <!-- id: 10 -->
- [x] **2.2 Fake Oath Signature** <!-- id: 11 -->
    - [x] Register agent with invalid signature <!-- id: 12 -->
- [x] **2.3 Sybil Attack** <!-- id: 13 -->
    - [x] Register 50 fake agents <!-- id: 14 -->

## 3. Ledger Integrity
- [x] **3.1 Concurrent Writes** <!-- id: 15 -->
    - [x] 10 threads writing simultaneously <!-- id: 16 -->
- [x] **3.2 Ledger Hammer** <!-- id: 17 -->
    - [x] 10,000 writes throughput test <!-- id: 18 -->
- [x] **3.3 Partial Write Recovery** <!-- id: 19 -->
    - [x] Kill process during write <!-- id: 20 -->

## 4. Cryptographic Identity
- [x] **4.1 Key Theft & Reuse** <!-- id: 21 -->
    - [x] Impersonate agent with stolen key <!-- id: 22 -->
- [x] **4.2 Signature Forgery** <!-- id: 23 -->
    - [x] Insert forged event in DB <!-- id: 24 -->

## 5. Playbook Engine
- [x] **5.1 Phase Crash Recovery** <!-- id: 25 -->
    - [x] Resume after crash <!-- id: 26 -->
- [x] **5.2 Stack Overflow** <!-- id: 27 -->
    - [x] Recursive playbook test <!-- id: 28 -->
- [x] **5.3 State Pollution** <!-- id: 29 -->
    - [x] Concurrent playbook execution <!-- id: 30 -->

## 6. Self-Healing
- [x] **6.1 Missing Dependency** <!-- id: 31 -->
    - [x] Uninstall dep & bootstrap <!-- id: 32 -->
- [x] **6.2 Corrupt Config** <!-- id: 33 -->
    - [x] Corrupt `matrix.yaml` <!-- id: 34 -->
- [x] **6.3 Git Branch Conflict** <!-- id: 35 -->
    - [x] Create conflict & bootstrap <!-- id: 36 -->

## 7. Agent Discovery
- [x] **7.1 Hot Reload** <!-- id: 37 -->
    - [x] Add agent at runtime <!-- id: 38 -->
- [x] **7.2 Malformed Manifest** <!-- id: 39 -->
    - [x] Test broken manifest handling <!-- id: 40 -->
- [x] **7.3 Duplicate Agent ID** <!-- id: 41 -->
    - [x] Test duplicate handling <!-- id: 42 -->

## 8. Single-Process Integrity
- [x] **8.1 State Pollution** <!-- id: 43 -->
    - [x] Modify other agent attributes <!-- id: 44 -->
- [x] **8.2 Kernel Hijacking** <!-- id: 45 -->
    - [x] Replace kernel registry <!-- id: 46 -->
- [x] **8.3 Memory Leak** <!-- id: 47 -->
    - [x] Leak memory & verify detection <!-- id: 48 -->

## 9. Constitutional Enforcement
- [x] **9.1 Content Violation** <!-- id: 49 -->
    - [x] Enforce banned phrases <!-- id: 50 -->
- [x] **9.2 Vote Manipulation** <!-- id: 51 -->
    - [x] Detect ledger corruption <!-- id: 52 -->

## 10. Platform Agnosticism
- [x] **10.1 Path Hardcoding** <!-- id: 53 -->
    - [x] Grep for hardcoded paths <!-- id: 54 -->
- [x] **10.2 Cross-Platform Boot** <!-- id: 55 -->
    - [x] Verify path handling <!-- id: 56 -->

## 11. Developer Experience
- [x] **11.1 Hello World Agent** <!-- id: 57 -->
    - [x] Scaffold & verify <!-- id: 58 -->
- [x] **11.2 Tool Development** <!-- id: 59 -->
    - [x] Custom tool discovery <!-- id: 60 -->
- [x] **11.3 Config Management** <!-- id: 61 -->
    - [x] Config propagation <!-- id: 62 -->

## 12. Stress & Chaos
- [x] **12.1 Task Queue Flood** <!-- id: 63 -->
    - [x] 10,000 tasks flood <!-- id: 64 -->
- [x] **12.2 Disk Full** <!-- id: 65 -->
    - [x] Simulate disk full <!-- id: 66 -->
- [x] **12.3 Interrupt Safety** <!-- id: 67 -->
    - [x] Ctrl+C resilience <!-- id: 68 -->

## 13. Real-World Scenarios
- [x] **13.1 Content Pipeline** <!-- id: 69 -->
    - [x] End-to-end workflow <!-- id: 70 -->
- [x] **13.2 Governance Proposal** <!-- id: 71 -->
    - [x] Proposal to execution flow <!-- id: 72 -->
