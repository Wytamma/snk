from typing import List
from pathlib import Path
from datetime import datetime
import typer
import sys
import collections  # MutableMapping import hack
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
from snk.cli.options import Option


def flatten(d, parent_key="", sep=":"):
    """
    Flattens a nested dictionary.
    Args:
      d (dict): The dictionary to flatten.
      parent_key (str, optional): The parent key of the dictionary. Defaults to ''.
      sep (str, optional): The separator to use between keys. Defaults to ':'.
    Returns:
      dict: A flattened dictionary.
    Examples:
      >>> d = {'a': {'b': 1, 'c': 2}, 'd': 3}
      >>> flatten(d)
      {'a:b': 1, 'a:c': 2, 'd': 3}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def convert_key_to_snakemake_format(key, value, sep=":"):
    """
    Convert key to a format that can be passed over the cli to snakemake
    """
    result_dict = {}
    parts = key.split(sep)
    current_dict = result_dict

    for part in parts[:-1]:
        current_dict = current_dict.setdefault(part, {})

    current_dict[parts[-1]] = value

    return result_dict


def serialise(d):
    """
    Serialises a data structure into a string.
    Args:
      d (any): The data structure to serialise.
    Returns:
      any: The serialised data structure.
    Examples:
      >>> serialise({'a': 1, 'b': 2})
      {'a': '1', 'b': '2'}
    """
    if isinstance(d, Path) or isinstance(d, datetime):
        return str(d)

    if isinstance(d, list):
        return [serialise(x) for x in d]

    if isinstance(d, dict):
        for k, v in d.items():
            d.update({k: serialise(v)})

    # return anything else, like a string or number
    return d


def parse_config_args(args: List[str], options: List[Option]):
    """
    Parses a list of arguments and a list of options.
    Args:
      args (List[str]): A list of arguments.
      options (List[Option]): A list of options.
    Returns:
      (List[str], List[dict]): A tuple of parsed arguments and config.
    Examples:
      >>> parse_config_args(['-name', 'John', '-age', '20'], [{'name': 'name', 'default': '', 'help': '', 'type': 'str', 'required': True}, {'name': 'age', 'default': '', 'help': '', 'type': 'int', 'required': True}])
      (['John', '20'], [{'name': 'name', 'John'}, {'age': 20}])
    """
    names = [op.name for op in options]
    config = []
    parsed = []
    flag = None
    for arg in args:
        if flag:
            name = flag.lstrip("-")
            op = next(op for op in options if op.name == name)
            if op.updated is False and op.default == serialise(arg):
                # skip args that don't change
                flag = None
                continue
            if ":" in op.original_key:
                samkemake_format_config = convert_key_to_snakemake_format(
                    op.original_key, arg
                )
                name = list(samkemake_format_config.keys())[0]
                arg = samkemake_format_config[name]
            config.append({name: serialise(arg)})
            flag = None
            continue
        if arg.startswith("-") and arg.lstrip("-") in names:
            flag = arg
            continue
        parsed.append(arg)
    return parsed, config

def get_default_type(v):
    default_type = type(v)
    if default_type == list and len(v) > 0:
        return f"List[{type(v[0]).__name__}]"
    return str(default_type.__name__)


def dag_filetype_callback(ctx: typer.Context, file: Path):
    allowed=[".pdf", ".png", ".svg"]
    if ctx.resilient_parsing or not file:
        return
    if file.suffix not in allowed:
        raise typer.BadParameter(f"Dag file suffix must be one of {','.join(allowed)}!")
    return file
