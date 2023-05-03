
from pathlib import Path
from typer.testing import CliRunner

from snk.main import app
from snk.pipeline import Pipeline

runner = CliRunner()

def test_snk_help():
    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "snk" in result.stdout
    assert "Usage" in result.stdout

def test_snk_install(snk_home: Path, bin_dir: Path):
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "install", "tests/data/pipeline"])
    assert result.exit_code == 0
    assert "Successfully installed" in result.stdout
    assert (snk_home / 'pipelines' / 'pipeline').exists()
    assert (bin_dir / 'pipeline').is_symlink()

def test_snk_list(local_pipeline: Pipeline):
    snk_home = local_pipeline.path.parent.parent
    bin_dir = local_pipeline.path.parent.parent.parent / 'bin'
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "list"])
    assert result.exit_code == 0
    assert "Found 1 pipelines" in result.stdout

def test_snk_uninstall(local_pipeline: Pipeline):
    snk_home = local_pipeline.path.parent.parent
    bin_dir = local_pipeline.path.parent.parent.parent / 'bin'
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "uninstall", "pipeline"])
    assert "(Y/n)" in result.stdout
    result = runner.invoke(app, ["--home", snk_home, "--bin", bin_dir, "uninstall", "pipeline", "--force"])
    assert result.exit_code == 0
    assert "Successfully uninstalled" in result.stdout