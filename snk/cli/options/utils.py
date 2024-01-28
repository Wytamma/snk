from typing import List, Any
from ..config.config import SnkConfig
from ..utils import get_default_type, flatten
from .option import Option
from pathlib import Path

types = {
    "int": int,
    "integer": int,
    "float": float,
    "str": str,
    "string": str,
    "path": Path,
    "bool": bool,
    "boolean": bool,
    "list": List[str],
    "list[str]": List[str],
    "list[path]": List[Path],
    "list[int]": List[int],
}

def get_keys_from_annotation(annotations):
    return {":".join(annotation.split(":")[:-1]) for annotation in annotations}

def create_option_from_annotation(
    annotation_key: str,
    annotation_values: dict,
    default_values: dict,
    from_annotation: bool = False,
) -> Option:
    """
    Create an Option object from a given annotation.
    Args:
      annotation_key: The key in the annotations.
      annotation_values: The dictionary of annotation values.
      default_values: default value from config.
    Returns:
      An Option object.
    """    
    config_default = default_values.get(annotation_key, None)

    default = annotation_values.get(f"{annotation_key}:default", config_default)
    updated = False
    if config_default is None or default != config_default:
        updated = True
    type = annotation_values.get(f"{annotation_key}:type", get_default_type(default))
    assert (
        type is not None
    ), f"Type for {annotation_key} should be one of {', '.join(types.keys())}."
    annotation_type = types.get(
        type.lower(), List[str] if "list" in type.lower() else str
    )
    name = annotation_values.get(
        f"{annotation_key}:name", annotation_key.replace(":", "_")
    ).replace("-", "_")
    short = annotation_values.get(f"{annotation_key}:short", None)
    hidden = annotation_values.get(f"{annotation_key}:hidden", False)
    return Option(
        name=name,
        original_key=annotation_key,
        default=annotation_values.get(f"{annotation_key}:default", default),
        updated=updated,
        help=annotation_values.get(f"{annotation_key}:help", ""),
        type=annotation_type,
        required=annotation_values.get(f"{annotation_key}:required", False),
        short=short,
        flag=f"--{name.replace('_', '-')}",
        short_flag=f"-{short}" if short else None,
        hidden=hidden,
        from_annotation=from_annotation,
    )


def build_dynamic_cli_options(
    snakemake_config: dict, snk_config: SnkConfig
) -> List[dict]:
    """
    Builds a list of options from a snakemake config and a snk config.
    Args:
      snakemake_config (dict): A snakemake config.
      snk_config (SnkConfig): A snk config.
    Returns:
      List[dict]: A list of options.
    """
    flat_config = flatten(snakemake_config)
    flat_annotations = flatten(snk_config.cli)
    annotation_keys = get_keys_from_annotation(flat_annotations)
    options = {}

    # For every parameter in the config, create an option from the corresponding annotation
    for parameter in flat_config:
        if parameter not in annotation_keys and snk_config.skip_missing:
            continue
        options[parameter] = create_option_from_annotation(
            parameter,
            flat_annotations,
            default_values=flat_config,
        )

    # For every annotation not in config, create an option with default values    
    for key in annotation_keys:
        if key not in options:
            # in annotation but not in config
            options[key] = create_option_from_annotation(
                key,
                flat_annotations,
                default_values={},
                from_annotation=True,
            )
    return list(options.values())
