from snk import Nest
from pathlib import Path

def test_init(bin_dir, snk_home):
    nest = Nest(snk_home, bin_dir=bin_dir)
    assert nest.snk_pipelines_dir == Path(snk_home) / 'pipelines'
    for path in [nest.snk_pipelines_dir, nest.bin_dir, nest.snk_home]:
        assert path.exists()

def test_download(nest: Nest):
    path = nest.download('https://github.com/Wytamma/snk-basic-pipeline.git', 'rna-seq-star-deseq2')
    expected_location = nest.snk_pipelines_dir / 'rna-seq-star-deseq2'
    assert (expected_location).exists()
    assert path == expected_location

def test_create_package(nest: Nest):
    test_pipeline_path = nest.snk_pipelines_dir / 'pipeline-name'
    test_pipeline_path.mkdir()
    path = nest.create_executable(pipeline_path=test_pipeline_path, name=test_pipeline_path.name)
    assert path == nest.snk_home / 'bin' / 'pipeline-name'

def test_install(nest: Nest):
    pipeline = nest.install('tests/data/pipeline')
    assert pipeline.name == 'pipeline'
    assert len(nest.pipelines) == 1

def test_install_custom_name(nest: Nest):
    pipeline = nest.install('tests/data/pipeline', name='custom-name')
    assert pipeline.name == 'custom-name'

def test_link_pipeline_executable_to_bin(nest: Nest):
    pipeline_executable_path = Path('tests/data/bin/snk-basic-pipeline')
    executable_path = nest.link_pipeline_executable_to_bin(pipeline_executable_path)
    assert executable_path.exists() is True and executable_path.is_symlink() is True

def test_uninstall(nest:Nest):
    pass
