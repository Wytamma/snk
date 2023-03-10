from snk import Nest
from pathlib import Path
import subprocess
from .utils import CLIRunner

def test_init(bin_dir, snk_home):
    nest = Nest(snk_home, bin_dir=bin_dir)
    assert nest.pipelines_dir == Path(snk_home) / 'pipelines'
    for path in [nest.pipelines_dir, nest.bin_dir, nest.snk_home]:
        assert path.exists()

def test_download(nest: Nest):
    repo = nest.download('https://github.com/snakemake-workflows/rna-seq-star-deseq2.git', 'rna-seq-star-deseq2')
    expected_location = nest.pipelines_dir / 'rna-seq-star-deseq2'
    assert (expected_location).exists()
    assert Path(repo.git_dir).parent == expected_location

def test_create_package(nest: Nest):
    test_pipeline_path = nest.pipelines_dir / 'pipeline-name'
    test_pipeline_path.mkdir()
    path = nest.create_package(pipeline_dir=test_pipeline_path)
    assert path == test_pipeline_path / 'bin' / 'pipeline-name'

def test_link_pipeline_executable_to_bin(nest: Nest):
    pipeline_executable_path = Path('tests/data/snk/pipelines/rna-seq-star-deseq2/bin/rna-seq-star-deseq2')
    executable_path = nest.link_pipeline_executable_to_bin(pipeline_executable_path)
    assert executable_path.exists() == True and executable_path.is_symlink() == True

def test_install(deseq2_runner):
    res = deseq2_runner(['--help'])
    assert 'Usage: rna-seq-star-deseq2' in res.stdout

def test_uninstall(nest:Nest):
    pass