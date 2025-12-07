import pytest


@pytest.mark.integration
@pytest.mark.slow
def test_minimal_boot(test_kernel):
    """Verify minimal kernel boots."""
    assert test_kernel is not None


@pytest.mark.integration
@pytest.mark.slow
def test_permissive_boot(permissive_kernel):
    """Verify permissive kernel boots."""
    assert permissive_kernel is not None


@pytest.mark.integration
@pytest.mark.slow
def test_governance_boot(governance_kernel):
    """Verify governance kernel boots."""
    assert governance_kernel is not None
