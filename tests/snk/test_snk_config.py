import pytest
from snk.cli.config.config import SnkConfig

def test_snk_config_creation():
    snk_config = SnkConfig()
    assert snk_config.tagline == "A Snakemake pipeline CLI generated with Snk"
    assert snk_config.font == "small"
    assert snk_config.resources == []
    assert snk_config.annotations == {}
    assert snk_config.symlink_resources == False

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

def test_from_dir_with_existing_file(tmp_path):
    config_file = tmp_path / ".snk"
    config_file.touch()
    config_file.write_text("logo: test_logo")
    snk_config = SnkConfig.from_pipeline_dir(tmp_path)
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
