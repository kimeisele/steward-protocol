import os
from pathlib import Path

# BASIS-PFAD (Anpassen, falls nötig)
ROOT_DIR = Path("vibe_core")


def check_file(path, description):
    if path.exists():
        print(f"✅ [SHABDA/ARTHA] {description} gefunden: {path}")
        return True
    print(f"❌ [SHABDA/ARTHA] {description} FEHLT: {path}")
    return False


def check_method(file_path, method_name):
    with open(file_path, "r") as f:
        content = f.read()
        if f"def {method_name}(" in content:
            print(f"✅ [KARMA] Methode '{method_name}' in {file_path.name} gefunden.")
            return True
    print(f"❌ [KARMA] Methode '{method_name}' FEHLT in {file_path.name}.")
    return False


def verify_system():
    print("--- REALITÄTS-CHECK: VEDA-4 ARCHITEKTUR ---\n")

    # 1. PRATYAYA (Config System Check)
    config_path = ROOT_DIR / "phoenix/config.py"
    if check_file(config_path, "Phoenix Config Engine"):
        print("   -> Config-System (Validation Layer) ist aktiv.")

    print("\n--- CHECKING PLUGINS ---")
    plugins_dir = ROOT_DIR / "plugins"
    if plugins_dir.exists():
        for plugin in plugins_dir.iterdir():
            if plugin.is_dir() and not plugin.name.startswith("_"):
                # SHABDA Check
                manifest = plugin / "manifest.json"
                has_identity = check_file(manifest, f"Identität ({plugin.name})")

                # KARMA Check
                main_py = plugin / "plugin_main.py"
                has_execution = False
                if main_py.exists():
                    has_execution = check_method(main_py, "on_boot")

                if not (has_identity and has_execution):
                    print(f"⚠️  Plugin {plugin.name} ist unvollständig!")

    print("\n--- CHECKING CARTRIDGES ---")
    cartridges_dir = ROOT_DIR / "cartridges"
    # Rekursiv suchen, da System/User Cartridges verschachtelt sein können
    for root, dirs, files in os.walk(cartridges_dir):
        if "cartridge.yaml" in files:
            path = Path(root)
            name = path.name

            # SHABDA
            check_file(path / "cartridge.yaml", f"Identität ({name})")

            # ARTHA
            check_file(path / "steward.json", f"Capabilities ({name})")

            # KARMA
            main = path / "cartridge_main.py"
            if main.exists():
                check_method(main, "process")  # Die Arbeits-Methode


if __name__ == "__main__":
    verify_system()
