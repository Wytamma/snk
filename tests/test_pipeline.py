from pathlib import Path
from snk.pipeline.utils import flatten
import snakemake

def test_flatten(example_config: Path):
    config = snakemake.load_configfile(example_config)
    flat_config = flatten(config)
    assert flat_config['diffexp:contrasts:A-vs-B'] == ['A', 'B']