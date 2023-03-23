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
    'list': List[str]
}

def create_cli_parameter(option):
    return Parameter(
        option['name'], 
        kind=Parameter.POSITIONAL_OR_KEYWORD, 
        default=typer.Option(... if option['required'] else option['default'], help=f"[CONFIG] {option['help']}"), 
        annotation=types.get(option['type'].lower(), str))

def add_dynamic_options(options: List[dict]):
    def inner(func: Callable):
        func_sig = signature(func)
        params = list(func_sig.parameters.values())
        for op in options[::-1]:
            params.insert(1, create_cli_parameter(op))
        new_sig = func_sig.replace(parameters=params)
        @wraps(func, new_sig=new_sig)
        def func_wrapper(*args, **kwargs):
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
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)