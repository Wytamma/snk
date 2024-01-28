from pathlib import Path
from typing import Any, Dict, Union, List
from snk.cli.config import SnkConfig
from snk.cli.options.utils import types
import inspect

class ValidationError(Exception):
    """Base class for all validation exceptions"""


def validate_config(config: Dict[str, Any], snk_config_path: Path) -> None:
    """
    Validates the config against the snk config.
    Will convert values to the correct type if possible.
    Args:
        config (dict): The config to validate.
        snk_config_path (Path): The path to the snk config.
    """
    snk_config_path = Path(snk_config_path)
    # if relative path, make absolute to 
    if not snk_config_path.is_absolute():
        frame = inspect.currentframe().f_back
        workflow = frame.f_globals.get("workflow")
        snk_config_path = Path(workflow.current_basedir) / snk_config_path

    snk_config = SnkConfig.from_path(snk_config_path)
    validate_and_transform_in_place(config, snk_config.cli)

ValidationDict = Dict[str, Union["ValidationDict", Dict[str, str]]]

def validate_and_transform_in_place(config: Dict[str, Any], validation: ValidationDict, replace_none: bool = True) -> None:
    """
    Validates the config against the snk config.
    Will convert values to the correct type if possible.
    Args:
        config (dict): The config to validate.
        validation (dict): The validation dict.
        replace_none (bool): If True, replace 'None' with None.
    """
    for key, value in list(config.items()):
        if key not in validation:
            continue  # Optionally handle unexpected keys
        if value == 'None' and replace_none:
            config[key] = None
            continue
        if value is None:
            continue
        val_info = validation[key]
        if isinstance(val_info, dict) and 'type' in val_info:
            # Direct type validation
            val_type = types.get(val_info["type"], None)
            if val_type is None:
                raise ValueError(f"Unknown type '{val_info['type']}'")
            try:
                if getattr(val_type, "__origin__", None) == list:
                    val_type = val_type.__args__[0]
                    if not isinstance(value, list):
                        raise ValueError(f"Expected a list for key '{key}'")
                    config[key] = [val_type(v) for v in value]
                else:
                    config[key] = val_type(value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Type conversion error for key '{key}': {e}")
        elif isinstance(value, dict):
            # Nested dictionary validation
            validate_and_transform_in_place(value, val_info)