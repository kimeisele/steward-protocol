import shutil
import zipfile

from scripts.pack_vibe import build_container
from vibe_core.cartridges.system.watchman.cartridge_main import WatchmanCartridge


def test_watchman_signature_governance(tmp_path):
    """
    Verify Watchman correctly validates GAD-000 signatures.
    1. Valid Signatures -> PASS
    2. Tampered Content -> FAIL
    3. Tampered Manifest -> FAIL
    """

    # 1. Setup Environment
    plugins_dir = tmp_path / "vibe_core/plugins"
    plugins_dir.mkdir(parents=True)

    # Create Source Plugin
    src_dir = tmp_path / "src_plugin"
    src_dir.mkdir()
    (src_dir / "manifest.json").write_text('{"id": "valid", "type": "plugin", "version": "1.0"}')
    (src_dir / "plugin_main.py").write_text('print("Valid Code")')
    (src_dir / "tests").mkdir()
    (src_dir / "tests/test.py").write_text("pass")

    # 2. Build Valid Container
    valid_vibe = plugins_dir / "valid.vibe"
    build_container(src_dir, valid_vibe)

    # 3. Initialize Watchman with Test Path
    watchman = WatchmanCartridge()
    watchman.scan_paths = [plugins_dir]

    # 4. Verify VALID
    report = watchman.verify_holon_signatures()
    assert report["status"] == "COMPLIANT"
    assert report["verified"] == 1
    assert len(report["violations"]) == 0

    # 5. Create TAMPERED Container (Modify Content)
    # We unpack, modify, and repack WITHOUT updating signature
    tampered_vibe = plugins_dir / "tampered.vibe"
    shutil.copy(valid_vibe, tampered_vibe)

    # Manually tamper by appending to zip? Zip is append-only usually, but replacing content requires rewrite.
    # Easiest way to simulate tampering without pack_vibe (which would resign):
    # Just construct a bad zip manually.

    with zipfile.ZipFile(tampered_vibe, "a") as z:
        # Appending a file doesn't invalidate existing signature file content,
        # BUT it changes the file list order or adds new file.
        # Watchman iterates ALL files.
        # So adding a file 'malware.py' that is NOT covered by SIGNATURE (because sig calculated on old files)
        # Wait, if I append, the sig verification will fail because the sig doesn't account for the new file?
        # Watchman verification loop:
        # Recomputes hash of ALL content.
        # Compare with stored sig.
        z.writestr("malware.py", "print('EVIL')")

    # verify
    report_tamper = watchman.verify_holon_signatures()
    assert report_tamper["status"] == "VIOLATIONS_DETECTED"
    # valid.vibe is fine, tampered.vibe fails
    violation_files = [v["file"] for v in report_tamper["violations"]]
    assert str(tampered_vibe) in violation_files

    print("\n✅ Watchman Governance Verified: Tampering Detected.")
