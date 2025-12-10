"""
Doctor Plugin - Sanity Tests
==============================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_doctor_plugin_imports():
    """Verify DoctorPlugin can be imported."""
    from vibe_core.plugins.doctor.plugin_main import DoctorPlugin

    assert DoctorPlugin is not None
    assert hasattr(DoctorPlugin, "on_boot")
    assert hasattr(DoctorPlugin, "plugin_id")


def test_doctor_plugin_instantiation():
    """Verify DoctorPlugin can be instantiated."""
    from vibe_core.plugins.doctor.plugin_main import DoctorPlugin

    plugin = DoctorPlugin()
    assert plugin.plugin_id == "doctor"
