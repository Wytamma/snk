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
    expected = nest.pipelines_dir / 'snk-basic-pipeline'
    assert expected.exists()
    print(basic_pipeline.executable)
    runner = CLIRunner([basic_pipeline.executable])
    return runner