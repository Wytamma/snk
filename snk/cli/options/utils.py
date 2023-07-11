from typing import List
from ..config import SnkConfig
from ..utils import get_default_type, flatten
from .option import Option
 

def create_option_from_annotation(
        annotation_key: str, 
        annotation_values: dict, 
        default_values: dict
    ) -> Option:
    """
    Create an Option object from a given annotation.
    Args:
      annotation_key: The key in the annotations.
      annotation_values: The dictionary of annotation values.
      default_values: The dictionary of default values.
    Returns:
      An Option object.
    """
    default = default_values.get(annotation_key, None)
    return Option(
        name=annotation_values.get(
            f"{annotation_key}:name",
            annotation_key.replace(":", "_")
        ).replace("-", "_"),
        original_key=annotation_key,
        default=annotation_values.get(f"{annotation_key}:default", default),
        updated=default is not None,
        help=annotation_values.get(f"{annotation_key}:help", ""),
        type=annotation_values.get(f"{annotation_key}:type", get_default_type(default)),
        required=annotation_values.get(f"{annotation_key}:required", False),
    )


def build_dynamic_cli_options(
        snakemake_config: dict, 
        snk_config: SnkConfig
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
    flat_annotations = flatten(snk_config.annotations)
    options = {}

    # For every parameter in the config, create an option from the corresponding annotation
    for parameter in flat_config:
        options[parameter] = create_option_from_annotation(
            parameter, 
            flat_annotations, 
            flat_config
        )

    # For every annotation not in config, create an option with default values
    for annotation in flat_annotations:
        key = ":".join(annotation.split(":")[:-1])
        if key not in options:
            options[key] = create_option_from_annotation(key, flat_annotations, {})

    return list(options.values())
