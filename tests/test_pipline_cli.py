from pathlib import Path
from snk.cli.utils import flatten, convert_key_to_snakemake_format
import snakemake
import pytest
from .utils import CLIRunner

def test_flatten(example_config: Path):
    config = snakemake.load_configfile(example_config)
    flat_config = flatten(config)
    assert flat_config['diffexp:contrasts:A-vs-B'] == ['A', 'B']


@pytest.mark.parametrize("key, value, expected", [
    ("a:b:c", 42, {"a": {"b": {"c": 42}}}),
    ("x:y:z", "hello", {"x": {"y": {"z": "hello"}}}),
    ("d:e", [1, 2, 3], {"d": {"e": [1, 2, 3]}}),
    ("h", "world", {"h": "world"}),
])
def test_convert_key_to_snakemake_format(key, value, expected):
    assert convert_key_to_snakemake_format(key, value) == expected

def test_help(local_runner: CLIRunner):
    res = local_runner(['--help'])
    assert res.code == 0, res.stderr
    assert 'Usage:' in res.stdout

def test_info(local_runner: CLIRunner):
    res = local_runner(['info'])
    assert res.code == 0, res.stderr
    assert 'pipeline' in res.stdout, res.stderr
    assert 'version' in res.stdout
    assert 'pipeline_dir_path' in res.stdout

def test_run_cli(local_runner: CLIRunner):
    res = local_runner(['run', '-h'])
    assert res.code == 0, res.stderr
    assert 'pipeline' in res.stdout, res.stderr
    assert 'times' in res.stdout
    assert 'text' in res.stdout

@pytest.mark.parametrize("filetype", ['pdf', 'svg', 'png'])
def test_dag(local_runner: CLIRunner, tmp_path, filetype):
    res = local_runner(['run', '--dag', f'{tmp_path}/dag.{filetype}'])
    assert res.code == 0, res.stderr
    assert 'DAG' in res.stderr, res.stderr
    assert Path(f'{tmp_path}/dag.{filetype}').exists()