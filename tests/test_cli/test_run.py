from pathlib import Path
from snk.cli.utils import flatten, convert_key_to_snakemake_format
from ..utils import CLIRunner


def test_config_override(local_runner: CLIRunner):
    res = local_runner(
        [
            "run",
            "--text",
            "passed from the cli to overwrite config",
            "--config",
            "tests/data/workflow/config.yaml",
            "-f",
        ]
    )
    assert res.code == 0, res.stderr
    assert "hello_world" in res.stderr
    assert "passed from the cli to overwrite config" in res.stdout


def test_exit_on_fail(local_runner: CLIRunner):
    res = local_runner(["run", "-f", "error"])
    assert res.code == 1, res.stderr


def test_config(print_config_runner: CLIRunner):
    res = print_config_runner(["run"])
    assert res.code == 0, res.stderr
    assert "snk" in res.stdout
    res = print_config_runner(["run", "--config", "tests/data/print_config/config.yaml"])
    assert res.code == 0, res.stderr
    assert "config" in res.stdout
    res = print_config_runner(
        ["run", "--config", "tests/data/print_config/config.yaml", "--value", "cli"]
    )
    assert res.code == 0, res.stderr
    assert "cli" in res.stdout
