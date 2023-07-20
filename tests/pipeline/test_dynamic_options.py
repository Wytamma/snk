import pytest
from snk.cli.config import SnkConfig
from snk.cli.options import Option
from snk.cli.options.utils import create_option_from_annotation, build_dynamic_cli_options


@pytest.fixture
def default_annotation_values():
    return {
        "test:name": "Test",
        "test:default": "default_value",
        "test:type": "str",
        "test:help": "Test help",
        "test:required": True
    }

@pytest.fixture
def default_default_values():
    return {
        "test": "default_value"
    }

def test_create_option_from_annotation(default_annotation_values, default_default_values):
    option = create_option_from_annotation("test", default_annotation_values, default_default_values)
    
    assert isinstance(option, Option)
    assert option.name == "Test"
    assert option.default == "default_value"
    assert option.updated == False
    assert option.help == "Test help"
    assert option.type == str
    assert option.required == True

@pytest.fixture
def default_snakemake_config():
    return {
        "param1": "value1",
        "param2": "value2",
    }

@pytest.fixture
def default_snk_config():
    return SnkConfig({
        "annotations": {
            "param1:name": "Parameter 1",
            "param2:name": "Parameter 2",
        }
    })

def test_build_dynamic_cli_options(default_snakemake_config, default_snk_config):
    options = build_dynamic_cli_options(default_snakemake_config, default_snk_config)

    assert len(options) == 2
    assert all(isinstance(option, Option) for option in options)
    assert set([option.name for option in options]) == {"param1", "param2"}
