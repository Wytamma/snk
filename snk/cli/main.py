import typer
from pathlib import Path
from typing import Optional, List, Callable
import sys
import json
import logging
from datetime import datetime

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art
import subprocess

from snk.cli.config import get_config_from_pipeline_dir, load_pipeline_snakemake_config, load_snk_config

from .utils import add_dynamic_options, flatten
from .gui import launch_gui
from snk.nest import Pipeline


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


def build_dynamic_cli_options(snakemake_config, snk_config):
    flat_config = flatten(snakemake_config)
    options = []
    snk_annotations = flatten(snk_config.get('annotations', {}))
    for op in flat_config:
        name = snk_annotations.get(f"{op}:name", op.replace(':', '_'))
        help = snk_annotations.get(f"{op}:help", "")
        # TODO be smarter here 
        # look up the List type e.g. if type == list then check the frist index type 
        # also can probably just pass the type around instead of the string?
        param_type = snk_annotations.get(f"{op}:type", f"{type(flat_config[op]).__name__}")  # TODO refactor 
        required = snk_annotations.get(f"{op}:required", False)
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
    def __init__(self, pipeline_dir_path: Path) -> None:
        self.pipeline_dir_path = pipeline_dir_path
        self.app = typer.Typer()
        self.snakemake_config = load_pipeline_snakemake_config(pipeline_dir_path)
        self.snk_config = load_snk_config(pipeline_dir_path)
        self.options = build_dynamic_cli_options(self.snakemake_config, self.snk_config)
        self.pipeline = Pipeline(path=pipeline_dir_path)
        self.snakefile = pipeline_dir_path / 'workflow' / 'Snakefile'
        self.conda_prefix_dir = pipeline_dir_path / '.conda'
        self.name = self.pipeline_dir_path.name
            
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
        self.app()

    def register_command(self, command: Callable, **command_kwargs) -> None:
        self.app.command(**command_kwargs)(command)

    def register_callback(self, command: Callable, **command_kwargs) -> None:
        self.app.callback(**command_kwargs)(command)

    def create_logo(self, font="small"):
        logo = text2art(self.name, font=font)        
        doc  = f"""\b{logo}\bA Snakemake pipeline CLI generated with snk"""
        return doc

    def _print_snakemake_help(value: bool):
        if value:
            snakemake.main("-h")

    def run(
            self,
            ctx: typer.Context,
            target: str = typer.Argument(None, help="File to generate. If None will run the pipeline 'all' rule."),
            configfile: Path = typer.Option(None, help="Path to snakemake config file. Overrides existing config and defaults.", exists=True, dir_okay=False),
            cores:  int = typer.Option(None, help="Set the number of cores to use. If None will use all cores."),
            verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Run pipeline in verbose mode.",),
            web_gui: Optional[bool] = typer.Option(False, "--gui", "-g", help="Lunch pipeline gui"),
            help_snakemake: Optional[bool] = typer.Option(
                False, "--help-snakemake", "-hs", help="Print the snakemake help and exit.", is_eager=True, callback=_print_snakemake_help, show_default=False
            ),
        ):
        args = []
        if not cores:
            cores = 'all'
        args.extend([
            "--use-conda",
            f"--conda-prefix={self.conda_prefix_dir}",
            f"--cores={cores}",
        ])
        if not self.snakefile.exists():
            raise ValueError('Could not find Snakefile')
        else:
            args.append(f"--snakefile={self.snakefile}")
        
        if not configfile:
            configfile = get_config_from_pipeline_dir(self.pipeline_dir_path)
        if configfile:
            args.append(f"--configfile={configfile}")

        
        # Set up conda frontend
        mamba_found = True
        try:
            subprocess.run(["mamba", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            typer.secho("Mamba not found! Install for speed up.")
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
        if web_gui:
            launch_gui(
                self.snakefile,
                self.conda_prefix_dir,
                self.pipeline_dir_path,
                config={k: v for dct in config_dict_list for k, v in dct.items()}
            )
        else:
            snakemake.main(args)

    def info(self):
        import json
        info_dict = {}
        info_dict['name'] = self.pipeline_dir_path.name
        info_dict['version'] = self.pipeline.version
        info_dict['pipeline_dir_path'] = str(self.pipeline_dir_path)
        typer.echo(json.dumps(info_dict, indent=2))

    def config(self):
        config_path = get_config_from_pipeline_dir(self.pipeline_dir_path)
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
        raise NotImplementedError

    def script(
        name: Optional[str] = typer.Argument(None)
    ):
        raise NotImplementedError