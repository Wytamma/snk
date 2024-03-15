import pytest
from snk_cli.config.config import SnkConfig


def test_snk_config_creation():
    snk_config = SnkConfig()
    assert snk_config.tagline == "A Snakemake workflow CLI generated with Snk"
    assert snk_config.font == "small"
    assert snk_config.resources == []
    assert snk_config.cli == {}
    assert snk_config.symlink_resources is False
    assert snk_config.version is None
    assert snk_config.skip_missing is False


def test_validate_resources_with_existing_files(tmp_path):
    resources = [tmp_path / "file1", tmp_path / "file2"]
    for resource in resources:
        resource.touch()
    snk_config = SnkConfig()
    # Should not raise an exception
    snk_config.validate_resources(resources)


def test_validate_resources_with_missing_files(tmp_path):
    resources = [tmp_path / "file1", tmp_path / "missing_file"]
    resources[0].touch()
    snk_config = SnkConfig()
    with pytest.raises(FileNotFoundError):
        snk_config.validate_resources(resources)


def test_add_resources(tmp_path):
    resources = [tmp_path / "file1", tmp_path / "file2"]
    for resource in resources:
        resource.touch()
    snk_config = SnkConfig()
    snk_config.add_resources(resources)
    assert len(snk_config.resources) == 2


def test_from_path_with_existing_file(tmp_path):
    config_file = tmp_path / "snk.yaml"
    config_file.touch()
    config_file.write_text("logo: test_logo")
    snk_config = SnkConfig.from_path(config_file)
    assert snk_config._snk_config_path == config_file

def test_missing_file(tmp_path):
    config_file = tmp_path / "snk.yaml"
    with pytest.raises(FileNotFoundError):
        SnkConfig.from_path(config_file)

def test_empty_file(tmp_path):
    config_file = tmp_path / "snk.yaml"
    config_file.touch()
    with pytest.raises(ValueError):
        SnkConfig.from_path(config_file)

def test_invalid_yaml(tmp_path):
    config_file = tmp_path / "snk.yaml"
    config_file.touch()
    config_file.write_text("logo: test_logo\ninvalid_yaml")
    with pytest.raises(Exception):
        SnkConfig.from_path(config_file)

def test_from_dir_with_existing_file(tmp_path):
    config_file = tmp_path / ".snk"
    config_file.touch()
    config_file.write_text("logo: test_logo")
    # catch warning 
    with pytest.warns(DeprecationWarning):
        snk_config = SnkConfig.from_workflow_dir(tmp_path)
    assert snk_config._snk_config_path == config_file


def test_from_path_with_missing_file(tmp_path):
    config_file = tmp_path / "missing_file.yaml"
    # assert it raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        SnkConfig.from_path(config_file)


def test_to_yaml(tmp_path):
    snk_config = SnkConfig(art="test_art", logo="test_logo")
    yaml_file = tmp_path / "snk.yaml"
    snk_config.to_yaml(yaml_file)
    assert yaml_file.exists()


def test_save(tmp_path):
    config_file = tmp_path / "snk.yaml"
    snk_config = SnkConfig(_snk_config_path=config_file)
    snk_config.art = "new_art"
    snk_config.save()
    saved_snk_config = SnkConfig.from_path(config_file)
    assert saved_snk_config.art == "new_art"


def test_version_from_about_file(tmp_path):
    config_file = tmp_path / "snk.yaml"
    about_file = tmp_path / "__about__.py"
    about_file.touch()
    about_file.write_text("__version__ = '0.0.1'")
    config_file.write_text("version: __about__.py")
    snk_config = SnkConfig.from_path(config_file)
    assert snk_config.version == "0.0.1"

def test_version_from_about_file_with_missing_file(tmp_path):
    config_file = tmp_path / "snk.yaml"
    about_file = tmp_path / "__about__.py"
    config_file.write_text("version: __about__.py")
    with pytest.raises(FileNotFoundError):
        SnkConfig.from_path(config_file)