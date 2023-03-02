import pytest
from pathlib import Path
from snk import Nest
from .utils import CLIRunner

@pytest.fixture()
def bin_dir(tmpdir: Path):
    return Path(tmpdir) / 'bin'

@pytest.fixture()
def snk_home(tmpdir: Path):
    return Path(tmpdir) / 'snk'

@pytest.fixture()
def nest(snk_home, bin_dir):
    return Nest(snk_home, bin_dir)

@pytest.fixture()
def example_config():
    return Path("tests/data/config.yaml")

@pytest.fixture()
def deseq2_runner(nest: Nest):
    deseq2 = nest.install('https://github.com/snakemake-workflows/rna-seq-star-deseq2.git')
    expected = nest.pipelines_dir / 'rna-seq-star-deseq2'
    assert expected.exists()
    print(deseq2.executable)
    runner = CLIRunner([deseq2.executable])
    return runner