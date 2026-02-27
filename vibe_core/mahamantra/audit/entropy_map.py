"""
ENTROPY MAP — Code-Verified Split-Brain Paths
==============================================

This module maps every entry point into the Mahamantra system and classifies
whether it flows through __call__() (the branchless pure computation core)
or bypasses it (split-brain).

RUN THIS:
    python -m vibe_core.mahamantra.audit.entropy_map

It will print the verified entropy map from live code inspection.
"""

from __future__ import annotations

__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"

from pathlib import Path
from typing import Dict, List

VIBE_CORE = Path(__file__).resolve().parent.parent.parent.parent


def _source_calls(module_path: str, target: str) -> bool:
    """Check if a module's source code contains a call pattern."""
    full = VIBE_CORE / module_path.replace(".", "/")
    candidates = [full.with_suffix(".py"), full / "__init__.py"]
    for p in candidates:
        if p.exists():
            src = p.read_text(encoding="utf-8", errors="replace")
            return target in src
    return False


def _file_calls(filepath: Path, target: str) -> bool:
    """Check if a file's source contains a call pattern."""
    if filepath.exists():
        src = filepath.read_text(encoding="utf-8", errors="replace")
        return target in src
    return False


def map_entry_points() -> Dict[str, List[dict]]:
    """
    Map all entry points and classify them.

    Returns dict with keys 'through_call' and 'bypass_call'.
    Each value is a list of dicts with 'file', 'function', 'evidence'.
    """
    through = []
    bypass = []

    mahamantra_dir = VIBE_CORE / "vibe_core" / "mahamantra"

    # === CORRECT PATHS (through __call__()) ===

    # 1. __main__.py
    main_py = mahamantra_dir / "__main__.py"
    if _file_calls(main_py, "mahamantra("):
        through.append(
            {
                "file": "mahamantra/__main__.py",
                "function": "main()",
                "evidence": "calls mahamantra(input_text) which is __call__()",
                "entry": "CLI: python -m vibe_core.mahamantra",
            }
        )

    # 2. MahamantraGateway
    gw = VIBE_CORE / "vibe_core" / "gateway" / "mahamantra_gateway.py"
    if _file_calls(gw, "mahamantra.execute("):
        through.append(
            {
                "file": "gateway/mahamantra_gateway.py",
                "function": "MahamantraGateway.receive()",
                "evidence": "calls mahamantra.execute() which fires gates then __call__()",
                "entry": "ALL: CLI, HTTP, CHAT, AGENT",
            }
        )

    # 3. Steward
    steward = mahamantra_dir / "cli" / "steward.py"
    if _file_calls(steward, "self.mahamantra("):
        through.append(
            {
                "file": "mahamantra/cli/steward.py",
                "function": "Steward.invoke()",
                "evidence": "calls self.mahamantra(input_text) which is __call__()",
                "entry": "CLI: steward command",
            }
        )

    # === BYPASS PATHS (split-brain) ===

    # 4. chat.py — MahajanaChat.respond()
    chat = mahamantra_dir / "chat.py"
    if chat.exists():
        src = chat.read_text(encoding="utf-8", errors="replace")
        has_respond = "def respond(" in src
        no_call = "mahamantra(" not in src and "mahamantra.execute" not in src
        if has_respond and no_call:
            bypass.append(
                {
                    "file": "mahamantra/chat.py",
                    "function": "MahajanaChat.respond()",
                    "evidence": "goes to LLM provider directly, never __call__()",
                    "entry": "CHAT: guardian_chat(), routed_chat()",
                    "size_bytes": chat.stat().st_size,
                    "severity": "HIGH — own routing via get_guardian_for_message()",
                }
            )

    # 5. commands.py — cli_chant()
    cmds = mahamantra_dir / "commands.py"
    if cmds.exists():
        src = cmds.read_text(encoding="utf-8", errors="replace")

        # cli_chant builds own Chamber + Reactor
        if "def cli_chant(" in src and "SankirtanChamber" in src:
            bypass.append(
                {
                    "file": "mahamantra/commands.py",
                    "function": "cli_chant()",
                    "evidence": "builds own SankirtanChamber + Reactor + Yajna cycles",
                    "entry": "CLI: steward chant",
                    "severity": "MEDIUM — parallel Yajna, but arguably different concern (ceremony vs computation)",
                }
            )

        # cli_serve goes to JanakaService directly
        if "def cli_serve(" in src and "JanakaService" in src:
            bypass.append(
                {
                    "file": "mahamantra/commands.py",
                    "function": "cli_serve()",
                    "evidence": "goes directly to JanakaService, never __call__()",
                    "entry": "CLI: steward serve",
                    "severity": "HIGH — task execution bypasses computation core",
                }
            )

        # cli_veda goes to VedaExplorer
        if "def cli_veda(" in src and "VedaExplorer" in src:
            bypass.append(
                {
                    "file": "mahamantra/commands.py",
                    "function": "cli_veda()",
                    "evidence": "goes to VedaExplorer or flooded_routed_chat",
                    "entry": "CLI: steward veda",
                    "severity": "HIGH — own routing, own LLM path",
                }
            )

    # 6. guardian_router.py — parallel 4D routing
    gr = mahamantra_dir / "substrate" / "guardian_router.py"
    if gr.exists():
        src = gr.read_text(encoding="utf-8", errors="replace")
        if "def route_input(" in src or "def match_guardian(" in src or "GuardianSignature" in src:
            bypass.append(
                {
                    "file": "mahamantra/substrate/guardian_router.py",
                    "function": "route_input() / match_guardian()",
                    "evidence": "own 4D coordinate routing, parallel to __call__() position routing",
                    "entry": "INTERNAL: used by chat routing and legacy paths",
                    "severity": "MEDIUM — useful as substrate, but duplicates __call__() routing logic",
                }
            )

    # 7. ModuleRouter / mahamantra.mod
    sing = mahamantra_dir / "kernel" / "singularity.py"
    if sing.exists():
        src = sing.read_text(encoding="utf-8", errors="replace")
        if "class ModuleRouter" in src:
            bypass.append(
                {
                    "file": "mahamantra/kernel/singularity.py",
                    "function": "ModuleRouter._load_module() / mahamantra.mod",
                    "evidence": "legacy dispatch to Mahajana folder stubs with execute() that return 'I am X' dicts",
                    "entry": "INTERNAL: mahamantra.mod.yamaraja etc.",
                    "severity": "LOW — exists but rarely used in production paths",
                }
            )

    # 8. Check for direct substrate access patterns outside mahamantra/
    direct_substrate = []
    for py_file in (VIBE_CORE / "vibe_core").rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(VIBE_CORE / "vibe_core")
        # Skip mahamantra internals and tests
        if str(rel).startswith("mahamantra/"):
            continue
        if "test" in str(rel).lower():
            continue
        try:
            src = py_file.read_text(encoding="utf-8", errors="replace")
            if "from vibe_core.mahamantra.substrate." in src:
                imports = [
                    line.strip()
                    for line in src.split("\n")
                    if line.strip().startswith("from vibe_core.mahamantra.substrate.")
                ]
                if imports:
                    direct_substrate.append(
                        {
                            "file": str(rel),
                            "imports": imports[:3],
                        }
                    )
        except Exception:
            continue

    return {
        "through_call": through,
        "bypass_call": bypass,
        "direct_substrate_access": direct_substrate,
    }


def count_mahajana_stubs() -> Dict[str, dict]:
    """Count Mahajana folders and classify as stub vs real."""
    mahamantra_dir = VIBE_CORE / "vibe_core" / "mahamantra"
    quarters = ["genesis", "dharma", "karma", "moksha"]
    result = {}

    for quarter in quarters:
        q_dir = mahamantra_dir / quarter
        if not q_dir.exists():
            continue
        for sub in q_dir.iterdir():
            if sub.is_dir() and sub.name != "__pycache__" and not sub.name.startswith("."):
                init = sub / "__init__.py"
                py_files = list(sub.rglob("*.py"))
                py_files = [f for f in py_files if "__pycache__" not in str(f)]
                total_bytes = sum(f.stat().st_size for f in py_files)

                # Classify: WIRED (delegates to real service), REAL (own code), or STUB
                status = "STUB"
                if init.exists():
                    src = init.read_text(encoding="utf-8", errors="replace")
                    if "def get_service(" in src:
                        status = "WIRED"
                    elif len(py_files) > 2 or total_bytes > 5000:
                        status = "REAL"

                result[f"{quarter}/{sub.name}"] = {
                    "files": len(py_files),
                    "bytes": total_bytes,
                    "status": status,
                    "has_execute": "def execute("
                    in (init.read_text(encoding="utf-8", errors="replace") if init.exists() else ""),
                }

    return result


def map_orchestration_chain() -> Dict[str, object]:
    """
    Verify the VenuService -> Singularity -> Listener chain from code.

    Returns dict with:
      - heartbeat_chain: list of verified links
      - orphaned: list of built-but-never-called infrastructure
      - unattached_services: services instantiated outside boot_orchestrator
    """
    vc = VIBE_CORE / "vibe_core"
    heartbeat_chain: List[dict] = []
    orphaned: List[dict] = []
    unattached: List[dict] = []

    # 1. VenuService.start() -> singularity.tick()
    venu_svc = vc / "services" / "venu_service.py"
    if venu_svc.exists():
        src = venu_svc.read_text(encoding="utf-8", errors="replace")
        has_sing_tick = "_singularity.tick()" in src
        has_start = "async def start(" in src
        heartbeat_chain.append(
            {
                "link": "VenuService.start() -> singularity.tick()",
                "file": "services/venu_service.py",
                "connected": has_sing_tick and has_start,
            }
        )

    # 2. singularity.tick() -> _broadcast()
    sing = vc / "mahamantra" / "kernel" / "singularity.py"
    if sing.exists():
        src = sing.read_text(encoding="utf-8", errors="replace")
        has_broadcast = "_broadcast(state)" in src or "self._broadcast(state)" in src
        heartbeat_chain.append(
            {
                "link": "singularity.tick() -> _broadcast(state)",
                "file": "mahamantra/kernel/singularity.py",
                "connected": has_broadcast,
            }
        )

    # 3. boot_orchestrator starts VenuService + wraps with BalaramaProxy
    boot = vc / "boot_orchestrator.py"
    if boot.exists():
        src = boot.read_text(encoding="utf-8", errors="replace")
        heartbeat_chain.append(
            {
                "link": "boot_orchestrator -> VenuService()",
                "file": "boot_orchestrator.py",
                "connected": "VenuService()" in src,
            }
        )
        heartbeat_chain.append(
            {
                "link": "boot_orchestrator -> wrap_service() -> BalaramaProxy",
                "file": "boot_orchestrator.py",
                "connected": "wrap_service(" in src,
            }
        )

    # 4. BalaramaProxy._attach_to_heartbeat() -> register_listener()
    proxy = vc / "mahamantra" / "substrate" / "proxy.py"
    if proxy.exists():
        src = proxy.read_text(encoding="utf-8", errors="replace")
        heartbeat_chain.append(
            {
                "link": "BalaramaProxy.__init__() -> _attach_to_heartbeat() -> register_listener()",
                "file": "mahamantra/substrate/proxy.py",
                "connected": "register_listener(" in src and "_attach_to_heartbeat" in src,
            }
        )

    # === ORPHANED INFRASTRUCTURE (built, 0 callers) ===
    # adopt_services()
    adoption = vc / "mahamantra" / "lila" / "adoption.py"
    if adoption.exists():
        callers = 0
        for py in vc.rglob("*.py"):
            if "__pycache__" in str(py) or py == adoption:
                continue
            try:
                if "adopt_services" in py.read_text(encoding="utf-8", errors="replace"):
                    callers += 1
            except Exception:
                continue
        if callers == 0:
            orphaned.append(
                {
                    "function": "adopt_services()",
                    "file": "mahamantra/lila/adoption.py",
                    "callers": 0,
                    "purpose": "OrbitalReactor mounting pipeline",
                }
            )

    # auto_wrap_services()
    if proxy.exists():
        callers = 0
        for py in vc.rglob("*.py"):
            if "__pycache__" in str(py) or py == proxy:
                continue
            try:
                if "auto_wrap_services" in py.read_text(encoding="utf-8", errors="replace"):
                    callers += 1
            except Exception:
                continue
        if callers == 0:
            orphaned.append(
                {
                    "function": "auto_wrap_services()",
                    "file": "mahamantra/substrate/proxy.py",
                    "callers": 0,
                    "purpose": "Lotus-driven BalaramaProxy wrapping",
                }
            )

    # ModuleRouter / mahamantra.mod runtime callers
    if sing.exists():
        mod_callers = 0
        for py in vc.rglob("*.py"):
            if "__pycache__" in str(py) or py == sing:
                continue
            try:
                src = py.read_text(encoding="utf-8", errors="replace")
                if ".mod." in src or "mahamantra.mod" in src:
                    # Exclude comments and docstrings (rough heuristic)
                    lines = [
                        l
                        for l in src.split("\n")
                        if (".mod." in l or "mahamantra.mod" in l)
                        and not l.strip().startswith("#")
                        and not l.strip().startswith('"""')
                        and not l.strip().startswith("'")
                    ]
                    if lines:
                        mod_callers += 1
            except Exception:
                continue
        orphaned.append(
            {
                "function": "ModuleRouter / mahamantra.mod",
                "file": "mahamantra/kernel/singularity.py",
                "callers": mod_callers,
                "purpose": "On-demand module/type access",
            }
        )

    # === UNATTACHED SERVICES (instantiated outside boot_orchestrator) ===
    # kernel_impl.py builds own MahamantraProxies
    kimpl = vc / "kernel_impl.py"
    if kimpl.exists():
        src = kimpl.read_text(encoding="utf-8", errors="replace")
        if "MahamantraProxy(" in src:
            proxy_lines = [
                l.strip() for l in src.split("\n") if "MahamantraProxy(" in l and not l.strip().startswith("#")
            ]
            unattached.append(
                {
                    "file": "kernel_impl.py",
                    "issue": "builds own MahamantraProxy with hardcoded positions",
                    "count": len(proxy_lines),
                    "examples": proxy_lines[:3],
                }
            )

    # Direct Service() instantiation outside boot_orchestrator
    service_pattern = "Service()"
    for py in vc.rglob("*.py"):
        if "__pycache__" in str(py):
            continue
        rel = str(py.relative_to(vc))
        # Skip boot_orchestrator (it's the canonical path), tests, and protocols
        if rel == "boot_orchestrator.py" or "test" in rel.lower() or "protocol" in rel.lower():
            continue
        # Skip service definitions themselves
        if rel.startswith("services/") or rel.startswith("protocols/mahajanas/"):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
            svc_lines = [
                l.strip()
                for l in src.split("\n")
                if service_pattern in l
                and not l.strip().startswith("#")
                and not l.strip().startswith("def ")
                and not l.strip().startswith('"""')
                and "Null" not in l
                and "= {" not in l
            ]
            if svc_lines:
                unattached.append(
                    {
                        "file": rel,
                        "issue": "direct Service() instantiation",
                        "count": len(svc_lines),
                        "examples": svc_lines[:2],
                    }
                )
        except Exception:
            continue

    return {
        "heartbeat_chain": heartbeat_chain,
        "orphaned": orphaned,
        "unattached_services": unattached,
    }


def main():
    """Print the verified entropy map."""
    print("=" * 70)
    print("MAHAMANTRA ENTROPY MAP — Verified from Code")
    print("=" * 70)

    entry_points = map_entry_points()

    print(f"\n{'=' * 70}")
    print(f"CORRECT PATHS (through __call__()): {len(entry_points['through_call'])}")
    print(f"{'=' * 70}")
    for ep in entry_points["through_call"]:
        print(f"  ✓ {ep['file']}")
        print(f"    {ep['function']} — {ep['entry']}")
        print(f"    Evidence: {ep['evidence']}")
        print()

    print(f"{'=' * 70}")
    print(f"SPLIT-BRAIN PATHS (bypass __call__()): {len(entry_points['bypass_call'])}")
    print(f"{'=' * 70}")
    for ep in entry_points["bypass_call"]:
        sev = ep.get("severity", "UNKNOWN")
        print(f"  ✗ {ep['file']} [{sev}]")
        print(f"    {ep['function']} — {ep.get('entry', '')}")
        print(f"    Evidence: {ep['evidence']}")
        print()

    print(f"{'=' * 70}")
    print(f"DIRECT SUBSTRATE ACCESS (outside mahamantra/): {len(entry_points['direct_substrate_access'])}")
    print(f"{'=' * 70}")
    for ds in entry_points["direct_substrate_access"][:10]:
        print(f"  → {ds['file']}")
        for imp in ds["imports"]:
            print(f"      {imp}")
    if len(entry_points["direct_substrate_access"]) > 10:
        print(f"  ... and {len(entry_points['direct_substrate_access']) - 10} more")

    print(f"\n{'=' * 70}")
    print("MAHAJANA FOLDER STATUS")
    print(f"{'=' * 70}")
    stubs = count_mahajana_stubs()
    wired_count = sum(1 for v in stubs.values() if v["status"] == "WIRED")
    real_count = sum(1 for v in stubs.values() if v["status"] == "REAL")
    stub_count = sum(1 for v in stubs.values() if v["status"] == "STUB")
    print(f"  Wired (delegates to Service): {wired_count}")
    print(f"  Real (own code >5KB):         {real_count}")
    print(f"  Stubs (identity only):        {stub_count}")
    for name, info in sorted(stubs.items()):
        print(f"    [{info['status']:5s}] {name:30s} {info['files']:2d} files, {info['bytes']:6d} bytes")

    # === ORCHESTRATION CHAIN ===
    print(f"\n{'=' * 70}")
    print("VENU ORCHESTRATION CHAIN (The Flute)")
    print(f"{'=' * 70}")
    orch = map_orchestration_chain()

    print("\n  HEARTBEAT CHAIN:")
    for link in orch["heartbeat_chain"]:
        status = "OK" if link["connected"] else "BROKEN"
        print(f"    [{status:6s}] {link['link']}")
        print(f"             {link['file']}")

    print("\n  ORPHANED INFRASTRUCTURE (built, never called):")
    for o in orch["orphaned"]:
        print(f"    [{o['callers']:2d} callers] {o['function']}")
        print(f"                {o['file']} — {o['purpose']}")

    print(f"\n  UNATTACHED SERVICES ({len(orch['unattached_services'])} files bypass boot_orchestrator):")
    for u in orch["unattached_services"][:15]:
        print(f"    {u['file']} ({u['count']}x)")
        for ex in u.get("examples", [])[:1]:
            print(f"      {ex[:100]}")
    remaining = len(orch["unattached_services"]) - 15
    if remaining > 0:
        print(f"    ... and {remaining} more")


if __name__ == "__main__":
    main()
