from unittest.mock import patch, MagicMock
from pathlib import Path
from snk import Nest
import pytest


@pytest.mark.parametrize("args", [
        {"snakemake_version":None, "dependencies":[]},
        {"snakemake_version":"7.0.0", "dependencies":[]},
        {"snakemake_version":None, "dependencies":["pandas", "numpy"]},
        {"snakemake_version":"7.0.0", "dependencies":["pandas", "numpy"]},
    ])
def test_install_snk_cli_in_venv(nest: Nest, args):
    # Define the virtual environment path
    venv_path = Path("/fake/path/to/venv")

    # Mock `exists` method for both the venv_path and the pip_path
    with patch.object(Path, 'exists', MagicMock(return_value=True)) as mock_exists:
        with patch("sys.platform", "linux"):
            # We assume a Linux platform for this example. Adjust if different OS handling is required
            pip_path = venv_path / "bin" / "pip"
            with patch.object(Path, '__truediv__', return_value=pip_path) as mock_truediv:
                with patch("subprocess.run") as mock_run:
                    # Assume subprocess.run does not raise an exception
                    mock_run.return_value = None

                    # Call the method under test
                    nest._install_snk_cli_in_venv(venv_path, **args)

                    # Check that subprocess.run was called with the correct arguments
                    if args["snakemake_version"] is None:
                        snakemake = "snakemake"
                    else:
                        snakemake = f"snakemake=={args['snakemake_version']}"
                    mock_run.assert_called_once_with(
                        [pip_path, 'install', snakemake, "snk_cli", "setuptools"] + args["dependencies"], 
                        check=True
                    )
                    # Verify that the Path.exists method was called on both venv_path and pip_path
                    mock_exists.assert_any_call()

