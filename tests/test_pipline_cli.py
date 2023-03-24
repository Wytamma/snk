from pathlib import Path
from snk.cli.utils import flatten
import snakemake

def test_flatten(example_config: Path):
    config = snakemake.load_configfile(example_config)
    flat_config = flatten(config)
    assert flat_config['diffexp:contrasts:A-vs-B'] == ['A', 'B']

def test_install(basic_runner):
    res = basic_runner(['--help'])
    assert 'Usage: snk-basic-pipeline' in res.stdout

def test_info(basic_runner):
    res = basic_runner(['info'])
    assert 'snk-basic-pipeline' in res.stdout, res.stderr
    assert 'version' in res.stdout
    assert 'pipeline_dir_path' in res.stdout

# def test_run(basic_runner):
#     res = basic_runner(['info'])
#     assert 'snk-basic-pipeline' in res.stdout, res.stderr
#     assert 'version' in res.stdout
#     assert 'pipeline_dir_path' in res.stdout