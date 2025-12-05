# GEMINI ANALYSIS REPORT


## 1. DEAD CODE FOUND
| File | Line | Type | Code |
|------|------|------|------|
| vibe_core/pulse.py | 199 | unused_function | function set_frequency |
| vibe_core/pulse.py | 204 | unused_function | function set_system_state |
| vibe_core/pulse.py | 209 | unused_function | function update_active_agents |
| vibe_core/pulse.py | 213 | unused_function | function update_queue_depth |
| vibe_core/pulse.py | 230 | unused_function | function get_last_packet |
| vibe_core/kernel_impl.py | 464 | unused_function | function get_vault |
| vibe_core/kernel_impl.py | 1411 | unused_function | function grant_capability |
| vibe_core/kernel_impl.py | 1446 | unused_function | function get_agent_capabilities |
| vibe_core/kernel_impl.py | 1621 | unused_function | function get_event_bus_status |
| vibe_core/kernel_impl.py | 1693 | unused_function | function dump_ledger |
| vibe_core/network_proxy.py | 70 | unused_function | function add_to_whitelist |
| vibe_core/network_proxy.py | 80 | unused_function | function remove_from_whitelist |
| vibe_core/network_proxy.py | 180 | unused_function | function get_request_log |
| vibe_core/network_proxy.py | 194 | unused_function | function clear_log |
| vibe_core/doc_renderer.py | 732 | unused_function | function render_kernel_docs |
| vibe_core/dependency_manager.py | 217 | unused_function | function get_version_constraint |
| vibe_core/capability_registry.py | 279 | unused_function | function get_original_capabilities |
| vibe_core/capability_registry.py | 335 | unused_function | function list_all_agents |
| vibe_core/ledger.py | 431 | unused_function | function get_top_hash |
| vibe_core/sarga.py | 159 | unused_function | function set_cycle |
| vibe_core/resource_manager.py | 204 | unused_function | function check_violations |
| vibe_core/io_service.py | 454 | unused_function | function create_io_service |
| vibe_core/io_service.py | 246 | unused_function | function extract_user_section |
| vibe_core/io_service.py | 427 | unused_function | function get_audit_stats |
| vibe_core/io_service.py | 442 | unused_function | function set_audit_enabled |
| vibe_core/event_bus.py | 96 | unused_function | function get_color |
| vibe_core/event_bus.py | 210 | unused_function | function clear_history |
| vibe_core/vfs.py | 153 | unused_function | function list_dir |
| vibe_core/agent_interface.py | 208 | unused_function | function file_exists |
| vibe_core/agent_interface.py | 212 | unused_function | function list_files |
| vibe_core/agent_interface.py | 261 | unused_function | function get_all_config |
| vibe_core/topology.py | 337 | unused_function | function distance_from_center |
| vibe_core/topology.py | 354 | unused_function | function can_override |
| vibe_core/boot_orchestrator.py | 296 | unused_function | function get_discoverer |
| vibe_core/lineage.py | 319 | unused_function | function get_agent_lineage |
| vibe_core/lineage.py | 329 | unused_function | function get_genesis_block |
| vibe_core/narasimha.py | 385 | unused_function | function activate_emergency_protocol |
| vibe_core/narasimha.py | 354 | unused_function | function is_active |
| vibe_core/identity.py | 96 | unused_function | function save_all_manifests |
| vibe_core/identity.py | 144 | unused_function | function get_agent_summary |
| vibe_core/operator_adapter.py | 472 | unused_function | function _select_best_operator |
| vibe_core/operator_adapter.py | 536 | unused_function | function hot_swap |
| vibe_core/cartridges/registry.py | 135 | unused_function | function register_cartridge |
| vibe_core/cartridges/system/civic/cartridge_main.py | 204 | unused_function | function agents_md_path |
| vibe_core/cartridges/system/civic/cartridge_main.py | 319 | unused_function | function _save_state |
| vibe_core/cartridges/system/civic/cartridge_main.py | 355 | unused_function | function get_matrix_config |
| vibe_core/cartridges/system/civic/tools/lifecycle_manager.py | 177 | unused_function | function register_new_agent |
| vibe_core/cartridges/system/civic/tools/lifecycle_manager.py | 304 | unused_function | function deprecate_to_vanaprastha |
| vibe_core/cartridges/system/civic/tools/lifecycle_manager.py | 350 | unused_function | function merge_to_sannyasa |
| vibe_core/cartridges/system/civic/tools/license_tool.py | 545 | unused_function | function add_restriction |

## 2. CIRCULAR DEPENDENCIES
- Cycle 1: vibe_core.kernel_impl -> vibe_core.cartridges.system.envoy.deterministic_executor -> vibe_core.cartridges.system.envoy.blueprint_generator -> vibe_core.semantic_syscalls -> vibe_core.kernel_impl
- Cycle 2: vibe_core.kernel_impl -> vibe_core.cartridges.system.envoy.deterministic_executor -> vibe_core.circuit_executor -> vibe_core.kernel_impl

## 3. MISSING IMPLEMENTATIONS
| File | Line | Issue |
|------|------|-------|
| vibe_core/kernel.py | 34 | `pass` stub detected |
| vibe_core/kernel.py | 39 | `pass` stub detected |
| vibe_core/kernel.py | 44 | `pass` stub detected |
| vibe_core/kernel.py | 62 | `pass` stub detected |
| vibe_core/kernel.py | 67 | `pass` stub detected |
| vibe_core/kernel.py | 72 | `pass` stub detected |
| vibe_core/kernel.py | 77 | `pass` stub detected |
| vibe_core/kernel.py | 82 | `pass` stub detected |
| vibe_core/kernel.py | 91 | `pass` stub detected |
| vibe_core/kernel.py | 96 | `pass` stub detected |
| vibe_core/kernel.py | 101 | `pass` stub detected |
| vibe_core/kernel.py | 106 | `pass` stub detected |
| vibe_core/kernel.py | 128 | `pass` stub detected |
| vibe_core/kernel.py | 134 | `pass` stub detected |
| vibe_core/kernel.py | 140 | `pass` stub detected |
| vibe_core/kernel.py | 146 | `pass` stub detected |
| vibe_core/kernel.py | 152 | `pass` stub detected |
| vibe_core/kernel.py | 157 | `pass` stub detected |
| vibe_core/kernel.py | 162 | `pass` stub detected |
| vibe_core/kernel.py | 167 | `pass` stub detected |
| vibe_core/kernel.py | 172 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 45 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 61 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 68 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 75 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 79 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 83 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 134 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 138 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 153 | `pass` stub detected |
| vibe_core/plugin_protocol.py | 246 | `pass` stub detected |
| vibe_core/ledger.py | 350 | `pass` stub detected |
| vibe_core/io_service.py | 332 | `pass` stub detected |
| vibe_core/circuit_executor.py | 288 | `pass` stub detected |
| vibe_core/process_manager.py | 194 | `pass` stub detected |
| vibe_core/tool_discovery.py | 21 | `pass` stub detected |
| vibe_core/boot_orchestrator.py | 345 | `pass` stub detected |
| vibe_core/narasimha.py | 317 | `pass` stub detected |
| vibe_core/cartridges/base.py | 24 | `pass` stub detected |
| vibe_core/cartridges/system/civic/tools/economy.py | 36 | `pass` stub detected |
| vibe_core/cartridges/system/civic/tools/vault.py | 75 | `pass` stub detected |
| vibe_core/cartridges/system/civic/tools/vault.py | 81 | `pass` stub detected |
| vibe_core/cartridges/system/civic/tools/vault.py | 87 | `pass` stub detected |
| vibe_core/cartridges/system/civic/tools/ledger_tool.py | 29 | `pass` stub detected |
| vibe_core/cartridges/system/archivist/tools/audit_tool.py | 78 | # TODO: Implement real verification with public_ke |
| vibe_core/cartridges/system/oracle/tools/introspection_tool.py | 31 | `pass` stub detected |
| vibe_core/cartridges/system/oracle/tools/introspection_tool.py | 326 | "description": "Placeholder or TODO implementation |
| vibe_core/cartridges/system/envoy/action_handlers.py | 33 | `pass` stub detected |
| vibe_core/cartridges/system/envoy/action_handlers.py | 53 | `pass` stub detected |
| vibe_core/cartridges/system/envoy/provider.py | 444 | `pass` stub detected |
| vibe_core/cartridges/system/envoy/deterministic_executor.py | 559 | `pass` stub detected |
| vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py | 221 | "# TODO.*implement": "MEDIUM", |
| vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py | 244 | # Templates (TODOs expected) |
| vibe_core/cartridges/system/forum/cartridge_main.py | 673 | `pass` stub detected |
| vibe_core/cartridges/system/watchman/cartridge_main.py | 64 | r"TODO.*implement", |
| vibe_core/cartridges/system/scribe/tools/project_introspector.py | 77 | `pass` stub detected |
| vibe_core/cartridges/system/scribe/tools/project_introspector.py | 177 | `pass` stub detected |
| vibe_core/cartridges/system/scribe/tools/introspector.py | 213 | `pass` stub detected |
| vibe_core/cartridges/system/scribe/tools/introspector.py | 233 | `pass` stub detected |
| vibe_core/cartridges/system/scribe/tools/base.py | 124 | `pass` stub detected |
| vibe_core/cartridges/system/scribe/tools/base.py | 127 | `pass` stub detected |
| vibe_core/cartridges/system/herald/cartridge_main.py | 693 | `pass` stub detected |
| vibe_core/cartridges/system/herald/governance/constitution.py | 55 | `pass` stub detected |
| vibe_core/cartridges/system/herald/governance/constitution.py | 60 | `pass` stub detected |
| vibe_core/cartridges/system/engineer/cartridge_main.py | 175 | `pass` stub detected |
| vibe_core/cartridges/system/engineer/templates/agent/cartridge_main.py | 101 | # TODO: Implement your capability |
| vibe_core/cartridges/system/engineer/templates/agent/cartridge_main.py | 106 | # TODO: Implement your capability |
| vibe_core/cartridges/agent_city/librarian/cartridge_main.py | 26 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py | 147 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py | 187 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py | 218 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py | 262 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/git_tool.py | 228 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py | 152 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py | 237 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py | 276 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/architecture_tool.py | 300 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 8 | - Technical debt indicators (TODO, FIXME, HACK) |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 176 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 179 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 198 | (r"\bTODO\b", "todo"), |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 199 | (r"\bFIXME\b", "fixme"), |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 234 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 314 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/code_tool.py | 317 | `pass` stub detected |
| vibe_core/cartridges/agent_city/analyst/tools/structure_tool.py | 152 | `pass` stub detected |
| vibe_core/settings/protocol.py | 86 | `pass` stub detected |
| vibe_core/settings/protocol.py | 117 | `pass` stub detected |
| vibe_core/settings/protocol.py | 130 | `pass` stub detected |
| vibe_core/settings/protocol.py | 145 | `pass` stub detected |
| vibe_core/cortex/engines/circuit_engine.py | 288 | `pass` stub detected |
| vibe_core/cortex/engines/__init__.py | 8 | - playbook_engine: DAG workflows (TODO: migrate) |
| vibe_core/cortex/protocols/__init__.py | 4 | TODO: Define CognitiveProcess, Intent, and other p |
| vibe_core/playbook/runner.py | 39 | `pass` stub detected |
| vibe_core/playbook/runner.py | 45 | `pass` stub detected |
| vibe_core/playbook/runner.py | 51 | `pass` stub detected |
| vibe_core/playbook/runner.py | 105 | `pass` stub detected |
| vibe_core/playbook/__init__.py | 22 | # TODO: Remove in v2.0 |
| vibe_core/playbook/loader.py | 35 | `pass` stub detected |
| vibe_core/playbook/loader.py | 41 | `pass` stub detected |
| vibe_core/playbook/router_bridge.py | 169 | `pass` stub detected |
| vibe_core/playbook/executor.py | 32 | `pass` stub detected |
| vibe_core/playbook/operations/kernel_spawn.py | 370 | `pass` stub detected |
| vibe_core/tools/tool_protocol.py | 128 | `pass` stub detected |
| vibe_core/tools/tool_protocol.py | 142 | `pass` stub detected |
| vibe_core/tools/tool_protocol.py | 162 | `pass` stub detected |
| vibe_core/tools/tool_protocol.py | 186 | `pass` stub detected |
| vibe_core/tools/tool_protocol.py | 218 | `pass` stub detected |
| vibe_core/llm/provider.py | 67 | `pass` stub detected |
| vibe_core/llm/provider.py | 92 | `pass` stub detected |
| vibe_core/llm/google_adapter.py | 180 | `pass` stub detected |
| vibe_core/task_management/metrics.py | 65 | `pass` stub detected |
| vibe_core/task_management/validator_registry.py | 11 | `pass` stub detected |
| vibe_core/task_management/file_lock.py | 61 | `pass` stub detected |
| vibe_core/config/__init__.py | 21 | # TODO: Remove in v2.0 |
| vibe_core/plugins/crypto/plugin_main.py | 113 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/git.py | 282 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/settings.py | 111 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/proof.py | 17 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/base.py | 18 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/base.py | 23 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/base.py | 41 | `pass` stub detected |
| vibe_core/plugins/interface/renderers/base.py | 66 | `pass` stub detected |
| vibe_core/plugins/steward_protocol/plugin_main.py | 307 | "signature_valid": None,  # TODO: implement |
| vibe_core/plugins/steward_protocol/plugin_main.py | 348 | "valid_until": None,  # TODO: implement expiry |
| vibe_core/plugins/vedic_governance/plugin_main.py | 64 | # TODO: Persist to Ledger (currently in-memory) |
| vibe_core/plugins/vedic_governance/plugin_main.py | 68 | # TODO: Persist to Ledger (currently in-memory) |
| vibe_core/runtime/prompt_composer.py | 237 | project_root = Path.cwd()  # TODO: Get from contex |
| vibe_core/runtime/prompt_registry.py | 75 | `pass` stub detected |
| vibe_core/runtime/prompt_registry.py | 81 | `pass` stub detected |
| vibe_core/runtime/prompt_registry.py | 87 | `pass` stub detected |
| vibe_core/runtime/prompt_context.py | 268 | `pass` stub detected |
| vibe_core/runtime/tool_safety_guard.py | 62 | `pass` stub detected |
| vibe_core/runtime/project_memory.py | 184 | `pass` stub detected |
| vibe_core/runtime/circuit_breaker.py | 45 | `pass` stub detected |
| vibe_core/runtime/circuit_breaker.py | 51 | `pass` stub detected |
| vibe_core/runtime/llm_client.py | 119 | `pass` stub detected |
| vibe_core/runtime/llm_client.py | 125 | `pass` stub detected |
| vibe_core/runtime/llm_client.py | 131 | `pass` stub detected |
| vibe_core/runtime/quota_manager.py | 45 | `pass` stub detected |
| vibe_core/runtime/hud.py | 63 | `pass` stub detected |
| vibe_core/runtime/hud.py | 81 | `pass` stub detected |
| vibe_core/runtime/hud.py | 265 | `pass` stub detected |
| vibe_core/runtime/prompt_runtime.py | 65 | `pass` stub detected |
| vibe_core/runtime/prompt_runtime.py | 71 | `pass` stub detected |
| vibe_core/runtime/prompt_runtime.py | 77 | `pass` stub detected |
| vibe_core/runtime/prompt_runtime.py | 83 | `pass` stub detected |
| vibe_core/runtime/prompt_runtime.py | 89 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 68 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 95 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 110 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 120 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 130 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 159 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 205 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 211 | `pass` stub detected |
| vibe_core/runtime/providers/base.py | 217 | `pass` stub detected |
| vibe_core/agents/llm_agent.py | 295 | `pass` stub detected |
| vibe_core/agents/llm_agent.py | 316 | `pass` stub detected |
| vibe_core/specialists/base_agent.py | 614 | `pass` stub detected |
| vibe_core/protocols/testable.py | 176 | `pass` stub detected |
| vibe_core/protocols/testable.py | 182 | `pass` stub detected |
| vibe_core/protocols/registry.py | 19 | `pass` stub detected |
| vibe_core/protocols/registry.py | 24 | `pass` stub detected |
| vibe_core/protocols/registry.py | 29 | `pass` stub detected |
| vibe_core/protocols/registry.py | 34 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 33 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 38 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 43 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 61 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 66 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 71 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 76 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 81 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 90 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 95 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 100 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 105 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 127 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 133 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 139 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 145 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 151 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 156 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 161 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 166 | `pass` stub detected |
| vibe_core/protocols/ledger.py | 171 | `pass` stub detected |
| vibe_core/protocols/testable_registry.py | 181 | `pass` stub detected |
| vibe_core/protocols/testable_registry.py | 298 | `pass` stub detected |
| vibe_core/protocols/agent.py | 373 | `pass` stub detected |
| vibe_core/protocols/agent.py | 388 | `pass` stub detected |
| vibe_core/protocols/agent.py | 491 | `pass` stub detected |
| vibe_core/protocols/scheduler.py | 19 | `pass` stub detected |
| vibe_core/protocols/scheduler.py | 24 | `pass` stub detected |
| vibe_core/protocols/scheduler.py | 29 | `pass` stub detected |
| vibe_core/store/sqlite_store.py | 10 | - TODO: Session narrative, artifacts, quality gate |
| vibe_core/store/sqlite_store.py | 1609 | `pass` stub detected |
| vibe_core/store/sqlite_store.py | 1619 | `pass` stub detected |
| vibe_core/store/sqlite_store.py | 1628 | `pass` stub detected |

## 4. ARCHITECTURE VIOLATIONS
| File | Line | Violation |
|------|------|-----------|
| vibe_core/kernel_impl.py | 190 | Hardcoded path to data/ |
| vibe_core/ledger.py | 116 | Hardcoded path to data/ |
| vibe_core/boot_orchestrator.py | 78 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/registry_agent.py | 38 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/economy_agent.py | 244 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/economy_agent.py | 245 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/vault_tool.py | 91 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/economy.py | 52 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/economy.py | 65 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/lifecycle_manager.py | 108 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/bank_tool.py | 51 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/vault.py | 113 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/license_tool.py | 145 | Hardcoded path to data/ |
| vibe_core/cartridges/system/civic/tools/ledger_tool.py | 64 | Hardcoded path to data/ |
| vibe_core/cartridges/system/archivist/tools/ledger_visualizer.py | 32 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/cartridge_main.py | 424 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/milk_ocean.py | 86 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/milk_ocean.py | 844 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/gap_report_tool.py | 38 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/gap_report_tool.py | 39 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/gap_report_tool.py | 40 | Hardcoded path to data/ |
| vibe_core/cartridges/system/envoy/tools/gap_report_tool.py | 464 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 71 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 79 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 81 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 84 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 92 | Hardcoded path to data/ |
| vibe_core/cartridges/system/watchman/tools/standards_inspection.py | 389 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/cartridge_main.py | 350 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/tools/scout_tool_legacy.py | 26 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/tools/scout_tool.py | 31 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/tools/identity_tool.py | 80 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/tools/identity_tool.py | 355 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/core/memory.py | 79 | Hardcoded path to data/ |
| vibe_core/cartridges/system/herald/core/agency_director.py | 107 | Hardcoded path to data/ |
| vibe_core/cartridges/system/auditor/tools/watchdog_tool.py | 37 | Hardcoded path to data/ |
| vibe_core/cartridges/system/auditor/tools/watchdog_tool.py | 40 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/librarian/tools/search_tool.py | 27 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/librarian/tools/recommend_tool.py | 27 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/librarian/tools/catalog_tool.py | 27 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/mechanic/tools/tidy_tool.py | 47 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/mechanic/tools/tidy_tool.py | 48 | Hardcoded path to data/ |
| vibe_core/cartridges/agent_city/mechanic/tools/tidy_tool.py | 49 | Hardcoded path to data/ |
| vibe_core/cortex/engines/semantic_engine.py | 57 | Hardcoded path to data/ |
| vibe_core/cortex/engines/semantic_engine.py | 58 | Hardcoded path to data/ |
| vibe_core/cortex/engines/semantic_engine.py | 61 | Hardcoded path to data/ |
| vibe_core/llm/local_llama_provider.py | 21 | Hardcoded path to data/ |
| vibe_core/config/schema.py | 156 | Hardcoded path to data/ |
| vibe_core/config/schema.py | 219 | Hardcoded path to data/ |
| vibe_core/plugins/interface/renderers/git.py | 42 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/city/section_main.py | 108 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/city/section_main.py | 233 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/test_governance/section_main.py | 58 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/test_governance/section_main.py | 104 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/test_governance/section_main.py | 120 | Hardcoded path to data/ |
| vibe_core/phoenix/sections/test_governance/section_main.py | 132 | Hardcoded path to data/ |

## 5. SECURITY ISSUES
| Severity | File | Issue |
|----------|------|-------|
| HIGH | vibe_core/cartridges/system/civic/registry_agent.py | Agent class `RegistryAgent` missing `OathMixin` |
| HIGH | vibe_core/cartridges/system/civic/lifecycle_agent.py | Agent class `LifecycleAgent` missing `OathMixin` |
| HIGH | vibe_core/cartridges/system/civic/economy_agent.py | Agent class `EconomyAgent` missing `OathMixin` |
| HIGH | vibe_core/cartridges/system/discoverer/agent.py | Agent class `Discoverer` missing `OathMixin` |
| HIGH | vibe_core/cartridges/system/discoverer/agent.py | Agent class `GenericAgent` missing `OathMixin` |
| HIGH | vibe_core/cartridges/agent_city/librarian/cartridge_main.py | Agent class `LibrarianCartridge` missing `OathMixin` |
| HIGH | vibe_core/cartridges/agent_city/analyst/cartridge_main.py | Agent class `AnalystCartridge` missing `OathMixin` |
| HIGH | vibe_core/agents/specialist_agent.py | Agent class `SpecialistAgent` missing `OathMixin` |
| HIGH | vibe_core/agents/specialist_factory.py | Agent class `SpecialistFactoryAgent` missing `OathMixin` |
| HIGH | vibe_core/agents/system_maintenance.py | Agent class `SystemMaintenanceAgent` missing `OathMixin` |
| HIGH | vibe_core/agents/llm_agent.py | Agent class `SimpleLLMAgent` missing `OathMixin` |
| HIGH | vibe_core/agents/context_aware_agent.py | Agent class `ContextAwareAgent` missing `OathMixin` |

## 6. RECOMMENDED DELETIONS
Files safe to delete (based on 0 imports - requires external validation):
- (Manual verification required based on Dead Code section)

## 7. PRIORITY FIX LIST
1. [HIGH] Fix Security Issues (Missing Oaths)
2. [MED] Resolve Circular Dependencies
3. [LOW] Clean up Dead Code
