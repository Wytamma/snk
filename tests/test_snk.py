from pathlib import Path

from snk_cli.workflow import Workflow
from typer.testing import CliRunner

from snk.main import app

runner = CliRunner()


def test_snk_help():
    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "snk" in result.stdout
    assert "Usage" in result.stdout


def test_snk_install(snk_home: Path, bin_dir: Path):
    result = runner.invoke(
        app, ["--home", snk_home, "--bin", bin_dir, "install", "tests/data/workflow"]
    )
    assert result.exit_code == 0
    assert "Successfully installed" in result.stdout
    assert (snk_home / "workflows" / "workflow").exists()
    assert (bin_dir / "workflow").is_symlink()


def test_snk_install_no_conda(snk_home: Path, bin_dir: Path):
    result = runner.invoke(
        app,
        [
            "--home",
            snk_home,
            "--bin",
            bin_dir,
            "install",
            "tests/data/workflow",
            "--no-conda",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully installed" in result.stdout
    snk_config = snk_home / "workflows" / "workflow" / "snk.yaml"
    assert snk_config.exists()
    # read the snk.yaml file as dict
    import yaml

    with open(snk_config) as f:
        snk_config_dict = yaml.safe_load(f)
    assert snk_config_dict["conda"] is False


def test_snk_list(local_workflow: Workflow):
    snk_home = local_workflow.path.parent.parent
    bin_dir = local_workflow.path.parent.parent.parent / "bin"
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "list"])
    assert result.exit_code == 0
    assert "workflow" in result.stdout
    assert "editable" in result.stdout

def test_config_path_cli(local_workflow: Workflow):
    snk_home = local_workflow.path.parent.parent
    bin_dir = local_workflow.path.parent.parent.parent / "bin"
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "edit", "--path", "workflow"])
    assert result.exit_code == 0
    assert "/workflows/workflow/snk.yaml" in result.stdout  

def test_snk_uninstall(local_workflow: Workflow):
    snk_home = local_workflow.path.parent.parent
    bin_dir = local_workflow.path.parent.parent.parent / "bin"
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "uninstall", "workflow"])
    assert "(Y/n)" in result.stdout
    result = runner.invoke(
        app, ["--home", snk_home, "--bin", bin_dir, "uninstall", "workflow", "--force"]
    )
    assert result.exit_code == 0
    assert "Successfully uninstalled" in result.stdout

def test_snk_create(local_workflow: Workflow, tmp_path: Path):
    result = runner.invoke(app, ["create", str(tmp_path), "--force"])
    print(result.stdout)
    assert result.exit_code == 0
    assert (tmp_path / "snk.yaml").exists()
    assert (tmp_path / "Snakefile").exists()

def test_import_create_cli(capsys):
    from snk import create_cli

    assert callable(create_cli)
    assert create_cli.__module__ == "snk"
    assert create_cli.__name__ == "create_cli"

    import sys

    sys.argv = ["cli", "-h"]
    try:
        create_cli("tests/data/workflow")
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "Usage" in captured.out

