from typing import Tuple
import pytest
from pathlib import Path
from snk import Nest
from .utils import CLIRunner
from snk_cli.config import SnkConfig
import yaml

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


@pytest.fixture(scope="session")
def basic_runner(tmp_path_factory):
    nest = Nest(tmp_path_factory.mktemp("snk"), tmp_path_factory.mktemp("bin"))
    basic_workflow = nest.install("https://github.com/Wytamma/snk-basic-pipeline.git")
    expected = nest.snk_workflows_dir / "snk-basic-pipeline"
    assert expected.exists()
    print(basic_workflow.executable)
    runner = CLIRunner([basic_workflow.executable])
    return runner


@pytest.fixture(scope="session")
def local_workflow(tmp_path_factory):
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / "home").mkdir()
    (path / "bin").mkdir()
    nest = Nest(path / "home", path / "bin")
    print(nest.bin_dir)
    print(nest.snk_home)
    local_workflow = nest.install("tests/data/workflow", editable=True)
    expected = nest.snk_workflows_dir / "workflow"
    assert expected.exists()
    return local_workflow


@pytest.fixture(scope="session")
def local_runner(tmp_path_factory):
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / "home").mkdir()
    (path / "bin").mkdir()
    nest = Nest(path / "home", path / "bin")
    local_workflow = nest.install("tests/data/workflow", editable=True)
    runner = CLIRunner([local_workflow.executable])
    return runner

class Request:
    param: Tuple[dict, SnkConfig]

@pytest.fixture
def dynamic_runner(tmp_path_factory, request: Request) -> CLIRunner:
    """Create a CLI Runner from a SNK and config file"""
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / "home").mkdir()
    (path / "bin").mkdir()
    nest = Nest(path / "home", path / "bin")
    config, snk, snakefile_text = request.param
    path = Path(tmp_path_factory.mktemp("workflow"))
    snk_path = path / "snk.yaml"
    config_path = path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    snk.to_yaml(snk_path)
    snakefile_path = path / "Snakefile"
    snakefile_path.write_text(snakefile_text)
    workflow = nest.install(path, editable=True)
    runner = CLIRunner([workflow.executable])
    return runner

@pytest.fixture(scope="session")
def print_config_runner(tmp_path_factory):
    path = Path(tmp_path_factory.mktemp("snk"))
    (path / "home").mkdir()
    (path / "bin").mkdir()
    nest = Nest(path / "home", path / "bin")
    local_workflow = nest.install("tests/data/print_config", editable=True)
    runner = CLIRunner([local_workflow.executable])
    return runner
