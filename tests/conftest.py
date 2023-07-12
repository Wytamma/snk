import pytest
from pathlib import Path
from snk import Nest
from .utils import CLIRunner

@pytest.fixture()
def bin_dir(tmp_path_factory: Path):
    return tmp_path_factory.mktemp("bin")

@pytest.fixture()
def snk_home(tmp_path_factory: Path):
    return tmp_path_factory.mktemp("snk")

@pytest.fixture()
def nest(snk_home, bin_dir):
    return Nest(snk_home, bin_dir)

@pytest.fixture()
def example_config():
    return Path("tests/data/config.yaml")


@pytest.fixture(scope='session')
def basic_runner(tmp_path_factory):
    nest = Nest(tmp_path_factory.mktemp("snk"), tmp_path_factory.mktemp("bin"))
    basic_pipeline = nest.install('https://github.com/Wytamma/snk-basic-pipeline.git')
    expected = nest.snk_pipelines_dir / 'snk-basic-pipeline'
    assert expected.exists()
    print(basic_pipeline.executable)
    runner = CLIRunner([basic_pipeline.executable])
    return runner

@pytest.fixture()
def local_pipeline(tmp_path_factory):
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / 'home').mkdir()
    (path / 'bin').mkdir()
    nest = Nest(path / 'home', path / 'bin')
    print(nest.bin_dir)
    print(nest.snk_home)
    local_pipeline = nest.install("tests/data/pipeline")
    expected = nest.snk_pipelines_dir / 'pipeline'
    assert expected.exists()
    return local_pipeline

@pytest.fixture()
def local_runner(tmp_path_factory):
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / 'home').mkdir()
    (path / 'bin').mkdir()
    nest = Nest(path / 'home', path / 'bin')
    local_pipeline = nest.install("tests/data/pipeline")
    runner = CLIRunner([local_pipeline.executable])
    return runner