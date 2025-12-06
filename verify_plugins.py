import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PLUGIN_VERIFIER")


def test_import(module_name, class_name):
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        logger.info(f"✅ Successfully imported {class_name} from {module_name}")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import {class_name} from {module_name}: {e}")
        return False
    except AttributeError as e:
        logger.error(f"❌ {class_name} not found in {module_name}: {e}")
        return False


def verify_all_plugins():
    results = []

    # Newly migrated
    results.append(test_import("vibe_core.plugins.sarga_cycle", "SargaCyclePlugin"))
    results.append(test_import("vibe_core.plugins.vedic_governance", "VedicGovernancePlugin"))

    # Existing folders
    results.append(test_import("vibe_core.plugins.test_mode", "TestModePlugin"))
    results.append(test_import("vibe_core.plugins.steward_protocol", "StewardProtocolPlugin"))

    # Interface renderers (replacing UI plugins)
    results.append(test_import("vibe_core.plugins.interface.renderers.git", "GitRenderer"))
    results.append(test_import("vibe_core.plugins.interface.renderers.envoy", "EnvoyRenderer"))
    results.append(test_import("vibe_core.plugins.interface.renderers.ephemeral", "EphemeralRenderer"))
    results.append(test_import("vibe_core.plugins.interface.renderers.settings", "SettingsRenderer"))

    if all(results):
        print("\n🎉 ALL PLUGINS VERIFIED!")
        sys.exit(0)
    else:
        print("\n❌ SOME PLUGINS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    verify_all_plugins()
