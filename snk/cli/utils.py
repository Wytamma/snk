from typing import List, Callable
from inspect import signature, Parameter
from makefun import wraps
from pathlib import Path
import typer
import sys
import collections  # MutableMapping import hack
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


types = {
    'int': int,
    'integer': int,
    'str': str,
    'string': str,
    'path': Path,
    'bool': bool,
    'boolean': bool,
    'list': List[str],
    'list[path]': List[Path],
    'list[int]': List[int],
}

def create_cli_parameter(option):
    """
    Creates a parameter for a CLI option.
    Args:
      option (dict): A dictionary containing the option's name, type, required status, default value, and help message.
    Returns:
      Parameter: A parameter object for the CLI option.
    Examples:
      >>> option = {'name': 'foo', 'type': 'int', 'required': True, 'default': 0, 'help': 'A number'}
      >>> create_cli_parameter(option)
      Parameter('foo', kind=Parameter.POSITIONAL_OR_KEYWORD, default=typer.Option(..., help='[CONFIG] A number'), annotation=int)
    """
    return Parameter(
        option['name'], 
        kind=Parameter.POSITIONAL_OR_KEYWORD, 
        default=typer.Option(... if option['required'] else option['default'], help=f"[CONFIG] {option['help']}"), 
        annotation=types.get(option['type'].lower(), str))

def add_dynamic_options(options: List[dict]):
    """
    Decorator to add dynamic options to a function.
    Args:
      options (List[dict]): A list of dictionaries containing the option's name, type, required status, default value, and help message.
    Returns:
      Callable: A decorated function with the dynamic options added.
    Examples:
      >>> @add_dynamic_options([{'name': 'foo', 'type': 'int', 'required': True, 'default': 0, 'help': 'A number'}])
      ... def my_func(ctx):
      ...     pass
      >>> my_func
      <function my_func at 0x7f8f9f9f9f90>
    """
    def inner(func: Callable):
        """
    Wraps a function with dynamic options.
    Args:
      func (Callable): The function to wrap.
    Returns:
      Callable: A wrapped function with the dynamic options added.
    Notes:
      This function is used as an inner function in the `add_dynamic_options` decorator.
    """
        func_sig = signature(func)
        params = list(func_sig.parameters.values())
        for op in options[::-1]:
            params.insert(1, create_cli_parameter(op))
        new_sig = func_sig.replace(parameters=params)
        @wraps(func, new_sig=new_sig)
        def func_wrapper(*args, **kwargs):
            """
            Wraps a function with dynamic options.
            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
            Returns:
                Callable: A wrapped function with the dynamic options added.
            Notes:
                This function is used as an inner function in the `add_dynamic_options` decorator.
            """
            if kwargs['configfile']:
                # need to check if kwargs in options have changed
                # parse the new configfile and update the defautls
                raise NotImplementedError
            for op in options:
                kwargs['ctx'].args.extend([f"--{op['name']}", kwargs[op['name']]])
            kwargs= {k:v for k,v in kwargs.items() if k in func_sig.parameters.keys()}
            return func(*args, **kwargs)
        return func_wrapper
    return inner


def flatten(d, parent_key='', sep=':'):
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