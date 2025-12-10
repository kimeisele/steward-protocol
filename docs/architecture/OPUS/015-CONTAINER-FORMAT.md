# OPUS-015: Vibe Container Format (v2.0 - The Holon)

> **Status:** PROPOSAL (Refined)
> **Architecture:** VEDA-4 Compliant
> **Format:** `.vibe` (Holonic Container)

<!-- @HARNESS
files:
  - path: vibe_core/loaders/container_loader.py
    required: true
  - path: scripts/pack_vibe.py
    required: true
  - path: vibe_core/loaders/base_loader.py
    required: false
tests:
  - tests/unit/test_container_loader.py
  - tests/integration/test_container_integrity.py
wiring:
  - pattern: "ContainerMounter"
    in: vibe_core/loaders/container_loader.py
  - pattern: "inspect|mount"
    in: vibe_core/loaders/container_loader.py
config:
  - section: opus.verification
-->

---

## Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| Loader | ✅ Implemented | `container_loader.py` |
| Packer | ✅ Implemented | `scripts/pack_vibe.py` |
| Hash Verification | ✅ Working | SHA256 content hash |
| Signature (Ed25519) | ❌ TODO | `container_loader.py:87` |
| Hollows Trust | ❌ TODO | No trust model yet |

## Implementation

## 1. The Holonic Structure

A container is not just a ZIP; it is a **Holon** – a whole that is part of a larger whole. It must be fractally structured.

**Physical Structure (.vibe = ZIP with Zero-Compression for Header):**

```text
my_plugin.vibe
│
├── manifest.json          ← [0] ALWAYS FIRST (execution.mode defines Isolation)
├── SIGNATURE.sig          ← [1] Cryptographic Proof (Author Identity)
│
├── content/               ← [2] The Payload (Code/Data)
│   ├── plugin_main.py     ← Entry Point
│   ├── config.yaml        ← Default Config
│   └── assets/
│
├── hollows/               ← [3] FRACTAL DIMENSION (Nested Containers)
│   ├── sub_agent_a.vibe   ← Plugins inside Plugins
│   └── sub_tool_b.vibe
│
└── tests/                 ← [4] QUALITY GATE (Must exist)
    ├── test_contracts.py  ← Defines behavior
    └── fixtures/
```

## 2. Technical Implementation Updates

### 2.1 Manifest Update: The "Physics" of Execution

To prevent **Namespace Pollution** (Dependency Hell), the manifest must define the container's weight and isolation needs.

```json
{
  "id": "my_agent",
  "type": "holon",
  "execution": {
    "mode": "process",  // Options: "thread" (shared) | "process" (isolated)
    "runtime": "python3.11"
  }
}
```

### 2.2 The Fractal Loader (`UnifiedLoader` Upgrade)

We must extend `_process_container` to handle both recursion (Lazy Extraction) and isolation (Execution Mode).

```python
# vibe_core/loaders/container_loader.py

class ContainerMounter:
    """Handles the physical reality of nested containers."""

    CACHE_DIR = Path("/tmp/vibe_cache/containers")

    @classmethod
    def mount_and_load(cls, container_path: Path) -> Any:
        """
        Mounts a container and loads it according to its defined physics (Mode).
        """
        # 1. Mount physical files (Unzip/Cache) via Lazy Extraction
        mount_point = cls._mount_fs(container_path)

        # 2. Read Shabda (Manifest)
        manifest = cls._read_manifest(mount_point)
        mode = manifest.get("execution", {}).get("mode", "thread")

        if mode == "process":
            # STRATEGY A: Isolated Reality (ProcessManager)
            # The Kernel spawns a Sub-Process.
            # Dependencies in container do NOT pollute Kernel namespace.
            return ProcessManager.spawn(
                entry_point=mount_point / "content" / "plugin_main.py",
                env_vars={"PYTHONPATH": str(mount_point / "content")}
            )

        elif mode == "thread":
            # STRATEGY B: Shared Reality (Fast but Risky)
            # We use physical mounting but shared memory.
            # RISK: Global namespace pollution.
            # REQUIRES: Strict adherence to Kernel pyproject.toml
            sys.path.insert(0, str(mount_point / "content"))
            try:
                ns = _import_module_from_path("plugin_main", mount_point / "content")
                return ns.PluginClass()
            finally:
                sys.path.pop(0) # Cleanup path, but modules remain in sys.modules
```

### 2.3 GAD-000 "Zero-Touch" Inspection

To comply with GAD-000, `steward` CLI must read metadata without "mounting" (avoiding code execution risk).

```python
def inspect_container(path: Path) -> Dict:
    """GAD-000: Read TRUTH without EXECUTION."""
    with zipfile.ZipFile(path) as z:
        # Read manifest directly from stream
        manifest_data = json.loads(z.read("manifest.json"))

        # Verify if tests exist (Compliance Check)
        has_tests = any(f.startswith("tests/") for f in z.namelist())

        return {
            "meta": manifest_data,
            "compliance": {
                "has_tests": has_tests,
                "signed": "SIGNATURE.sig" in z.namelist()
            }
        }
```

## 3. Decision Log

### Q1: Extension?
**Decision:** `.vibe`
**Reason:** It is the "Vibe OS". Short, branded, compliant.

### Q2: Signature Enforcement?
**Decision:** **Development: Warn | Production: STRICT**
**Reason:** Fast iteration in Dev (`zip -r`), Trust in Prod (Steward Protocol).

### Q3: Test Requirement?
**Decision:** **HARD FAIL**
**Reason:** A Holon without tests is "dead matter". Verification is part of identity.

### Q4: IDE Support?
**Decision:** **Hybrid Workflow**
- **Dev:** Folders (UnifiedLoader supports both).
- **Prod:** Containers (Immutable).

## 4. Next Steps

1.  **Refactor `base_loader.py`:** Implement `is_dir()` vs `is_zip()` and Lazy Extraction logic.
2.  **Create `scripts/pack_vibe.py`:** Build tool to convert Folder -> `.vibe` with Signature and correct structure.
3.  **Update `kernel_impl.py`:** Integrate `SignatureVerifier` into boot process.

---

## References
- [base_loader.py](file:///Users/ss/Downloads/steward-protocol/vibe_core/loaders/base_loader.py)
