from pathlib import Path
from snk.cli.utils import flatten
import snakemake

def test_flatten(example_config: Path):
    config = snakemake.load_configfile(example_config)
    flat_config = flatten(config)
    assert flat_config['diffexp:contrasts:A-vs-B'] == ['A', 'B']

def test_install(deseq2_runner):
    res = deseq2_runner(['--help'])
    assert 'Usage: rna-seq-star-deseq2' in res.stdout

def test_info(deseq2_runner):
    res = deseq2_runner(['info'])
    assert 'rna-seq-star-deseq2' in res.stdout, res.stderr
    assert 'version' in res.stdout
    assert 'pipeline_dir_path' in res.stdout

# def test_run(deseq2_runner):
#     res = deseq2_runner(['info'])
#     assert 'rna-seq-star-deseq2' in res.stdout, res.stderr
#     assert 'version' in res.stdout
#     assert 'pipeline_dir_path' in res.stdout