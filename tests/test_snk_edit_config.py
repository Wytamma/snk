import os  # noqa: F401
import platform  # noqa: F401
import subprocess
from pathlib import Path
from unittest.mock import call, patch

import pytest
import typer  # noqa: F401
from snk_cli.workflow import Workflow
from typer.testing import CliRunner

from snk.main import app

runner = CliRunner()


@pytest.fixture
def mock_platform_system():
    with patch('platform.system') as mock:
        yield mock


@pytest.fixture
def mock_os_startfile():
    # Only patch os.startfile if the platform is Windows
    if hasattr(os, 'startfile'):
        with patch('os.startfile') as mock:
            yield mock
    else:
        yield None


@pytest.fixture
def mock_subprocess_call():
    with patch('subprocess.call') as mock:
        yield mock


@pytest.mark.skipif(platform.system() != 'Windows', reason="Requires Windows")
def test_open_text_editor_windows(
    mock_platform_system, mock_os_startfile, local_workflow: Workflow
):
    mock_platform_system.return_value = 'Windows'
    file_path = local_workflow.path / "snk.yaml"
    
    snk_home = local_workflow.path.parent.parent
    bin_dir = local_workflow.path.parent.parent.parent / "bin"
    res = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "edit", "workflow"])
    
    assert res.exit_code == 0, res.stderr
    if mock_os_startfile:
        mock_os_startfile.assert_called_once_with(file_path)


def test_open_text_editor_mac(
    mock_platform_system, mock_subprocess_call, local_workflow: Workflow
):
    mock_platform_system.return_value = 'Darwin'
    file_path = local_workflow.path / "snk.yaml"

    snk_home = local_workflow.path.parent.parent
    bin_dir = local_workflow.path.parent.parent.parent / "bin"
    res = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "edit", "workflow"])
    
    assert res.exit_code == 0, res.stderr
    mock_subprocess_call.assert_called_once_with(('open', file_path))


def test_open_text_editor_linux(
    mock_platform_system, mock_subprocess_call, local_workflow: Workflow
):
    mock_platform_system.return_value = 'Linux'
    file_path = local_workflow.path / "snk.yaml"

    with patch('subprocess.call') as mock_call:
        mock_call.side_effect = [1, 1, 0, 0]  # Mocking 'which' command results: nano not found, vim not found, vi found

        snk_home = local_workflow.path.parent.parent
        bin_dir = local_workflow.path.parent.parent.parent / "bin"
        res = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "edit", "workflow"])
        assert res.exit_code == 0, res.stderr
        mock_call.assert_has_calls([
            call(['which', 'nano'], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(['which', 'vim'], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(['which', 'vi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(['vi', file_path])
        ])


def test_open_text_editor_no_editor_found(
    mock_platform_system, mock_subprocess_call, local_workflow: Workflow
):
    mock_platform_system.return_value = 'Linux'

    with patch('subprocess.call') as mock_call:
        mock_call.side_effect = [1, 1, 1]  # Mocking 'which' command results: none of the editors found

        with patch('typer.secho') as mock_print:
            snk_home = local_workflow.path.parent.parent
            bin_dir = local_workflow.path.parent.parent.parent / "bin"
            res = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "edit", "workflow"])
            assert res.exit_code == 1, res.stderr
            mock_print.assert_called_once_with(
                "No suitable text editor found. Please install nano or vim.", fg='red', err=True
            )
