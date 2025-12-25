import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.test_orchestration.plugin_main import OrchestrationPlugin
from vibe_core.plugins.test_orchestration.test_guardian import Guardian


class TestTestGovernanceIntegration:
    @pytest.fixture
    def temp_dir(self):
        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_kernel(self, temp_dir):
        kernel = MagicMock()
        # Mock config
        config = MagicMock()

        # Mock the test_governance section config
        governance_config = MagicMock()
        # The Guardian expects config object to have attributes matching the fields
        # It seems it uses the config object directly.
        # Let's check TestGovernanceConfig definition.
        # It likely has fields like mutation_policy, baseline_path etc.

        governance_config.mutation_policy = "warn"
        governance_config.new_test_policy = "allow"
        governance_config.baseline_path = os.path.join(temp_dir, "test_hashes.json")
        governance_config.baseline_enforcement = True

        # Setup get_section to return our mock config
        def get_section(name):
            if name == "test_governance":
                return governance_config
            return None

        config.get_section.side_effect = get_section

        # ALSO set it as an attribute because Guardian uses getattr(config, "test_governance")
        config.test_governance = governance_config

        kernel.config = config
        return kernel

    def test_guardian_initialization(self, mock_kernel):
        """Test that the guardian initializes correctly."""
        plugin = OrchestrationPlugin()
        plugin.on_boot(mock_kernel)
        assert plugin.guardian is not None
        assert isinstance(plugin.guardian, Guardian)

    def test_mutation_detection(self, mock_kernel, temp_dir):
        """Test that mutations are detected."""
        plugin = OrchestrationPlugin()
        plugin.on_boot(mock_kernel)

        # Create a dummy test file
        test_file_path = os.path.join(temp_dir, "test_dummy.py")
        with open(test_file_path, "w") as f:
            f.write("def test_foo(): assert True")

        # 1. First run: Should record the hash (Birth)
        validation = plugin.validate_tests_before_run(test_path=temp_dir)

        assert validation["mutated"] == 0
        assert validation["new"] == 1

        # Verify hash file was created
        hash_file = os.path.join(temp_dir, "test_hashes.json")
        assert os.path.exists(hash_file)

        with open(hash_file, "r") as f:
            data = json.load(f)
            assert len(data["contracts"]) == 1

        # 2. Modify the file (Mutation)
        with open(test_file_path, "w") as f:
            f.write("def test_foo(): assert False # Mutated")

        # 3. Second run: Should detect mutation
        validation = plugin.validate_tests_before_run(test_path=temp_dir)

        assert validation["mutated"] == 1
        assert "test_dummy.py" in validation["errors"][0]

    def test_run_pytest_integration(self, mock_kernel, temp_dir):
        """Test that run_pytest calls validation."""
        plugin = OrchestrationPlugin()
        plugin.on_boot(mock_kernel)

        # Create a dummy test file
        test_file_path = os.path.join(temp_dir, "test_dummy_2.py")
        with open(test_file_path, "w") as f:
            f.write("def test_bar(): assert True")

        # Mock the actual pytest run to avoid running real tests
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="passed", stderr="")

            # Run pytest
            plugin.run_pytest(path=temp_dir)

            # Check if validation happened (hash file should exist)
            hash_file = os.path.join(temp_dir, "test_hashes.json")
            assert os.path.exists(hash_file)
