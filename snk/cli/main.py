import typer
from pathlib import Path
from typing import Optional, List, Callable
from datetime import datetime
import subprocess
import shutil
import os
from contextlib import contextmanager

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art



from .config import SnkConfig, get_config_from_pipeline_dir, load_pipeline_snakemake_config
from .utils import add_dynamic_options, flatten
from .pipeline import Pipeline


def convert_key_to_samkemake_format(key, value):
    """
    Covert key to a format that can be passed over the cli to snakemake
    """
    resultDict = dict()
    parts = key.split(":")
    d = resultDict
    for part in parts[:-1]:
        if part not in d:
            d[part] = dict()
        d = d[part]
    d[parts[-1]] = value
    return resultDict

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

def parse_config_args(args: List[str], options):
    """
    Parses a list of arguments and a list of options.
    Args:
      args (List[str]): A list of arguments.
      options (List[dict]): A list of options.
    Returns:
      (List[str], List[dict]): A tuple of parsed arguments and config.
    Examples:
      >>> parse_config_args(['-name', 'John', '-age', '20'], [{'name': 'name', 'default': '', 'help': '', 'type': 'str', 'required': True}, {'name': 'age', 'default': '', 'help': '', 'type': 'int', 'required': True}])
      (['John', '20'], [{'name': 'name', 'John'}, {'age': 20}])
    """
    names = [op['name'] for op in options]
    config = []
    parsed = []
    flag=None
    for arg in args:
        if flag:
            name = flag.lstrip('-')
            op = next(op for op in options if op['name'] == name)
            if op['default'] == serialise(arg):
                # skip args that don't change
                flag=None
                continue
            if ":" in op['original_key']:
                samkemake_format_config = convert_key_to_samkemake_format(op['original_key'], arg)
                name = list(samkemake_format_config.keys())[0]
                arg = samkemake_format_config[name]
            # config.append(f'{name}={serialise(arg)}')
            config.append({name: serialise(arg)})
            flag=None
            continue
        if arg.startswith('-') and arg.lstrip('-') in names:
            flag = arg
            continue
        parsed.append(arg)
    return parsed, config


def build_dynamic_cli_options(snakemake_config, snk_config: SnkConfig):
    """
    Builds a list of options from a snakemake config and a snk config.
    Args:
      snakemake_config (dict): A snakemake config.
      snk_config (SnkConfig): A snk config.
    Returns:
      List[dict]: A list of options.
    Examples:
      >>> build_dynamic_cli_options({'name': 'John', 'age': 20}, {'annotations': {'name:name': 'name', 'name:help': '', 'name:type': 'str', 'name:required': True, 'age:name': 'age', 'age:help': '', 'age:type': 'int', 'age:required': True}})
      [{'name': 'name', 'original_key': 'name', 'default': 'John', 'help': '', 'type': 'str', 'required': True}, {'name': 'age', 'original_key': 'age', 'default': 20, 'help': '', 'type': 'int', 'required': True}]
    """
    flat_config = flatten(snakemake_config)
    options = []
    flat_snk_annotations = flatten(snk_config.annotations)
    for op in flat_config:
        name = flat_snk_annotations.get(f"{op}:name", op.replace(':', '_'))
        help = flat_snk_annotations.get(f"{op}:help", "")
        # TODO be smarter here 
        # look up the List type e.g. if type == list then check the frist index type 
        # also can probably just pass the type around instead of the string?
        param_type = flat_snk_annotations.get(f"{op}:type", f"{type(flat_config[op]).__name__}")  # TODO refactor 
        required = flat_snk_annotations.get(f"{op}:required", False)
        options.append(
            {
                'name':name.replace('-', '_'),
                'original_key': op,
                'default': flat_config[op],
                'help': help,
                'type': param_type,
                'required': required
            }
        )
    # TODO: find annotations missing from config and add them to options
    return options


class CLI:
    """
    Constructor for the CLI class.
    Args:
      pipeline_dir_path (Path): Path to the pipeline directory.
    Side Effects:
      Initializes the CLI class.
    Examples:
      >>> CLI(Path('/path/to/pipeline'))
    """
    def __init__(self, pipeline_dir_path: Path) -> None:
        self.pipeline = Pipeline(path=pipeline_dir_path)
        self.app = typer.Typer()
        self.snakemake_config = load_pipeline_snakemake_config(pipeline_dir_path)
        self.snk_config: SnkConfig = SnkConfig.from_path(pipeline_dir_path / '.snk')
        self.options = build_dynamic_cli_options(self.snakemake_config, self.snk_config)
        self.snakefile = self._find_snakefile()
        self.conda_prefix_dir = pipeline_dir_path / '.conda'
        self.name = self.pipeline.name
        def _print_pipline_version(ctx: typer.Context, value: bool):
            if value:
                typer.echo(self.pipeline.version)
                raise typer.Exit()

        def _print_pipline_path(ctx: typer.Context, value: bool):
            if value:
                typer.echo(self.pipeline.path)
                raise typer.Exit()

        def callback(
            ctx: typer.Context, 
            version: Optional[bool] = typer.Option(None, '-v', '--version', help="Show the pipeline version.", is_eager=True, callback=_print_pipline_version, show_default=False),
            path: Optional[bool] = typer.Option(None, '-p', '--path', help="Show the pipeline path.", is_eager=True, callback=_print_pipline_path, show_default=False)
        ):
            if ctx.invoked_subcommand is None:
                typer.echo(f'{ctx.get_help()}')
        # dynamically create the logo
        callback.__doc__ = f"{self.create_logo()}"

        # registration 
        self.register_callback(callback, invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
        self.register_command(self.info, help="Display information about current pipeline install.")
        self.register_command(self.config, help="Access the pipeline configuration.")
        self.register_command(self.env, help="Access the pipeline conda environments.")
        self.register_command(self.script, help="Access the pipeline scripts.")
        self.register_command(
            add_dynamic_options(self.options)(self.run), 
            help="Run the pipeline. All unrecognized arguments are parsed onto Snakemake to be used by the pipeline.", 
            context_settings={
                "allow_extra_args": True, 
                "ignore_unknown_options": True, 
                "help_option_names": ["-h", "--help"]
            }
        )

    def __call__(self):
        """
    Invoke the CLI.
    Side Effects:
      Invokes the CLI.
    Examples:
      >>> CLI(Path('/path/to/pipeline'))()
    """
        self.app()

    def register_command(self, command: Callable, **command_kwargs) -> None:
        """
    Register a command to the CLI.
    Args:
      command (Callable): The command to register.
    Side Effects:
      Registers the command to the CLI.
    Examples:
      >>> CLI.register_command(my_command)
    """
        self.app.command(**command_kwargs)(command)

    def register_callback(self, command: Callable, **command_kwargs) -> None:
        """
    Register a callback to the CLI.
    Args:
      command (Callable): The callback to register.
    Side Effects:
      Registers the callback to the CLI.
    Examples:
      >>> CLI.register_callback(my_callback)
    """
        self.app.callback(**command_kwargs)(command)

    def create_logo(self, font="small"):
        """
    Create a logo for the CLI.
    Args:
      font (str): The font to use for the logo.
    Returns:
      str: The logo.
    Examples:
      >>> CLI.create_logo()
    """
        logo = text2art(self.name, font=font)        
        doc  = f"""\b{logo}\bA Snakemake pipeline CLI generated with snk"""
        return doc

    def _print_snakemake_help(value: bool):
        """
    Print the snakemake help and exit.
    Args:
      value (bool): If True, print the snakemake help and exit.
    Side Effects:
      Prints the snakemake help and exits.
    Examples:
      >>> CLI._print_snakemake_help(True)
    """
        if value:
            snakemake.main("-h")
    
    def _find_snakefile(self):
            """
    Search possible snakefile locations.
    Returns:
      Path: The path to the snakefile.
    Examples:
      >>> CLI._find_snakefile()
    """
            for path in snakemake.SNAKEFILE_CHOICES:
                if (self.pipeline.path / path).exists():
                    return self.pipeline.path / path 
            raise FileNotFoundError("Snakefile not found!")
    
    @contextmanager
    def copy_resources(self, resources: List[Path], cleanup: bool):
        """
    Copy resources to the current working directory.
    Args:
      resources (List[Path]): A list of paths to the resources to copy.
      cleanup (bool): If True, the resources will be removed after the function exits.
    Side Effects:
      Copies the resources to the current working directory.
    Returns:
      Generator: A generator object.
    Examples:
      >>> with CLI.copy_resources(resources, cleanup=True):
      ...     # do something
    """
        copied_resources = []

        def copy_resource(src, dst):
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

        def remove_resource(resource):
            if resource.is_dir():
                shutil.rmtree(resource)
            else:
                os.remove(resource)

        try:
            for resource in resources:
                abs_path = self.pipeline.path / resource
                destination = Path('.') / resource.name
                if not destination.exists(): 
                    # make sure you don't delete files that are already there...
                    copy_resource(abs_path, destination)
                    copied_resources.append(destination)
                else:
                    typer.secho(
                        f"Resource {resource.name} already exists... Skipping!", 
                        fg=typer.colors.YELLOW
                    )

            yield
        finally:
            if not cleanup:
                return 
            for copied_resource in copied_resources:
                if copied_resource.exists():
                    remove_resource(copied_resource)

    def run(
            self,
            ctx: typer.Context,
            target: str = typer.Argument(None, help="File to generate. If None will run the pipeline 'all' rule."),
            configfile: Path = typer.Option(None, help="Path to snakemake config file. Overrides existing config and defaults.", exists=True, dir_okay=False),
            resource: List[Path] = typer.Option([], help="Additional resources to copy to workdir at run time."),
            cleanup_resources: Optional[bool] = typer.Option(True, help="Delete resources once the pipeline sucessfully completes."),
            cleanup_snakemake: Optional[bool] = typer.Option(True, help="Delete .snakemake folder once the pipeline sucessfully completes."),
            cores:  int = typer.Option(None, help="Set the number of cores to use. If None will use all cores."),
            verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Run pipeline in verbose mode.",),
            help_snakemake: Optional[bool] = typer.Option(
                False, "--help-snakemake", "-hs", help="Print the snakemake help and exit.", is_eager=True, callback=_print_snakemake_help, show_default=False
            ),
        ):
        """
    Run the pipeline.
    Args:
      target (str): File to generate. If None will run the pipeline 'all' rule.
      configfile (Path): Path to snakemake config file. Overrides existing config and defaults.
      resource (List[Path]): Additional resources to copy to workdir at run time.
      cleanup_resources (bool): Delete resources once the pipeline sucessfully completes.
      cleanup_snakemake (bool): Delete .snakemake folder once the pipeline sucessfully completes.
      cores (int): Set the number of cores to use. If None will use all cores.
      verbose (bool): Run pipeline in verbose mode.
      help_snakemake (bool): Print the snakemake help and exit.
    Side Effects:
      Runs the pipeline.
    Examples:
      >>> CLI.run(target='my_target', configfile=Path('/path/to/config.yaml'), resource=[Path('/path/to/resource')], verbose=True)
    """
        args = []
        if not cores:
            cores = 'all'
        args.extend([
            "--use-conda",
            f"--conda-prefix={self.conda_prefix_dir}",
            f"--cores={cores}",
        ])
        if not self.snakefile.exists():
            raise ValueError('Could not find Snakefile') # this should occur at install
        else:
            args.append(f"--snakefile={self.snakefile}")
        
        if not configfile:
            configfile = get_config_from_pipeline_dir(self.pipeline.path)
        if configfile:
            args.append(f"--configfile={configfile}")

        
        # Set up conda frontend
        mamba_found = True
        try:
            subprocess.run(["mamba", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            typer.secho("Mamba not found! Install for speed up.", fg=typer.colors.YELLOW)
            mamba_found = False
        if not mamba_found:
            args.append("--conda-frontend=conda")
        
        typer.echo(self.create_logo())
        typer.echo()

        if verbose:
            args.insert(0, "--verbose")

        if target:
            args.append(target)
        targets_and_or_snakemake, config_dict_list = parse_config_args(ctx.args, options=self.options)

        args.extend(targets_and_or_snakemake)

        args.extend(["--config", *[f"{list(c.keys())[0]}={list(c.values())[0]}" for c in config_dict_list]])
        if verbose:
            typer.secho(f"snakemake {' '.join(args)}\n", fg=typer.colors.MAGENTA)
        
        self.snk_config.add_resources(resource, self.pipeline.path)
        with self.copy_resources(self.snk_config.resources, cleanup=cleanup_resources):
                snakemake.main(args)
        if cleanup_snakemake:
            shutil.rmtree(".snakemake")

    def info(self):
        """
    Display information about current pipeline install.
    Returns:
      str: A JSON string containing information about the current pipeline install.
    Examples:
      >>> CLI.info()
    """
        import json
        info_dict = {}
        info_dict['name'] = self.pipeline.path.name
        info_dict['version'] = self.pipeline.version
        info_dict['pipeline_dir_path'] = str(self.pipeline.path)
        typer.echo(json.dumps(info_dict, indent=2))

    def config(self):
        """
    Access the pipeline configuration.
    Side Effects:
      Prints the pipeline configuration.
    Examples:
      >>> CLI.config()
    """
        config_path = get_config_from_pipeline_dir(self.pipeline.path)
        if not config_path:
            typer.secho("Could not find config...", fg='red')
            raise typer.Exit(1)
        with open(config_path) as f:
            code = f.read()
            syntax = Syntax(code, 'yaml')
            console = Console()
            console.print(syntax)
    
    def env(
        name: Optional[str] = typer.Argument(None)
    ):
        """
    Access the pipeline conda environments.
    Args:
      name (str): The name of the environment.
    Examples:
      >>> CLI.env(name='my_env')
    """
        raise NotImplementedError

    def script(
        name: Optional[str] = typer.Argument(None)
    ):
        """
    Access the pipeline scripts.
    Args:
      name (str): The name of the script.
    Examples:
      >>> CLI.script(name='my_script')
    """
        raise NotImplementedError