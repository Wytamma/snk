from snk import Nest
from pathlib import Path


def test_init(bin_dir, snk_home):
    nest = Nest(snk_home, bin_dir=bin_dir)
    assert nest.snk_workflows_dir == Path(snk_home) / "workflows"
    for path in [nest.snk_workflows_dir, nest.bin_dir, nest.snk_home]:
        assert path.exists()


def test_download(nest: Nest):
    path = nest.download(
        "https://github.com/Wytamma/snk-basic-pipeline.git", "rna-seq-star-deseq2"
    )
    expected_location = nest.snk_workflows_dir / "rna-seq-star-deseq2"
    assert (expected_location).exists()
    assert path == expected_location


def test_create_package(nest: Nest):
    test_workflow_path = nest.snk_workflows_dir / "workflow-name"
    test_workflow_path.mkdir()
    path = nest.create_executable(
        workflow_path=test_workflow_path, name=test_workflow_path.name
    )
    assert path == nest.snk_home / "bin" / "workflow-name"


def test_install(nest: Nest):
    workflow = nest.install("tests/data/workflow")
    assert workflow.name == "workflow"
    assert len(nest.workflows) == 1
    assert (nest.snk_workflows_dir / "workflow").exists()
    assert (nest.snk_home / "bin" / "workflow").exists()

    with open(nest.snk_home / "bin" / "workflow") as f:
        contents = f.read()
        assert "from snk_cli import CLI" in contents
        assert "create_cli" in contents


def test_install_custom_name(nest: Nest):
    workflow = nest.install("tests/data/workflow", name="custom-name")
    assert workflow.name == "custom-name"


def test_link_workflow_executable_to_bin(nest: Nest):
    workflow_executable_path = Path("tests/data/bin/snk-basic-pipeline")
    executable_path = nest.link_workflow_executable_to_bin(workflow_executable_path)
    assert executable_path.exists() is True and executable_path.is_symlink() is True


def test_uninstall(nest: Nest):
    workflow = nest.install("tests/data/workflow")
    assert len(nest.workflows) == 1
    nest.uninstall(workflow.name, force=True)
    assert len(nest.workflows) == 0
    assert not (nest.snk_workflows_dir / "workflow").exists()
    assert not (nest.snk_home / "bin" / "workflow").exists()
