def test_data_integrity():
    """Verify that export paths exist."""
    import pathlib

    assert pathlib.Path("circuits").exists()
