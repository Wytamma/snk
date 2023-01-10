import typer
from pathlib import Path
from typing import Optional, List
import sys
import collections
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art
import subprocess

from .utils import add_dynamic_options

def _print_snakemake_help(value: bool):
    if value:
        snakemake.main("-h")

def create_logo(name):
    logo = text2art(name, font="small")        
    doc  = f"""\b{logo}\bA Snakemake pipeline CLI generated with snk"""
    return doc

def convert_key_to_samkemake_format(key, value):
    resultDict = dict()
    parts = key.split(":")
    d = resultDict
    for part in parts[:-1]:
        if part not in d:
            d[part] = dict()
        d = d[part]
    d[parts[-1]] = value
    return resultDict

def parse_config_args(args: List[str], options):
    names = [op['name'] for op in options]
    config = []
    parsed = []
    flag=None
    for arg in args:
        if flag:
            name = flag.lstrip('-')
            op = next(op for op in options if op['name'] == name)
            if ":" in op['original_key']:
                samkemake_format_config = convert_key_to_samkemake_format(op['original_key'], arg)
                name = list(samkemake_format_config.keys())[0]
                arg = samkemake_format_config[name]
            config.append(f"{name}={arg}")
            flag=None
            continue
        if arg.startswith('-') and arg.lstrip('-') in names:
            flag = arg
            continue
        parsed.append(arg)
    parsed.extend(["--config", *config])
    return parsed

def get_config_from_pipeline_dir(pipeline_dir_path: Path):
    """"""
    config_path = pipeline_dir_path / 'config' / 'config.yaml'
    return config_path 

def flatten(d, parent_key='', sep=':'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def load_options(pipeline_dir_path: Path):
    config_path = get_config_from_pipeline_dir(pipeline_dir_path)
    config = snakemake.load_configfile(config_path)
    flat_config = flatten(config)
    options = []
    catalog_config_path = pipeline_dir_path / '.snakemake-workflow-catalog.yml'
    catalog_config = snakemake.load_configfile(catalog_config_path)
    snk_annotations = {}
    if 'snk' in catalog_config:
        snk_config = catalog_config['snk']
        if 'annotations' in snk_config:
            snk_annotations = flatten(snk_config['annotations'])
    for op in flat_config:
        name = op.replace(':', '_')
        help = snk_annotations.get(f"{op}:help")
        type = snk_annotations.get(f"{op}:type")
        options.append(
            {
                'name':name,
                'original_key': op,
                'default': str(flat_config[op]),
                'help': help if help else "",
                'type': type if type else "str"
            }
        )
    return options

def pipeline_cli_factory(pipeline_dir_path: Path):
    app = typer.Typer()
    options = load_options(pipeline_dir_path)

    def _print_pipline_version(value: bool):
        if value:
            typer.echo(None)
            raise typer.Exit()

    def _print_pipline_path(value: bool):
        if value:
            print(pipeline_dir_path)
            raise typer.Exit()

    @app.callback(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
    def callback(
            ctx: typer.Context, 
            version: Optional[bool] = typer.Option(None, '-v', '--version', help="Show the pipeline version.", is_eager=True, callback=_print_pipline_version, show_default=False),
            path: Optional[bool] = typer.Option(None, '-p', '--path', help="Show the pipeline path.", is_eager=True, callback=_print_pipline_path, show_default=False)
        ):
        if ctx.invoked_subcommand is None:
            typer.echo(f'{ctx.get_help()}')
    # dynamically create the logo
    callback.__doc__ = f"{create_logo(pipeline_dir_path.name)}"

    @app.command(help="Run the pipeline.", context_settings={"allow_extra_args": True, "ignore_unknown_options": True, "help_option_names": ["-h", "--help"]})
    @add_dynamic_options(options)
    def run(
            ctx: typer.Context,
            target: str = typer.Argument(None, help="File to generate. If None will run the pipeline 'all' rule."),
            configfile: Path = typer.Option(None, help="Path to config file. Overrides existing config and defaults.", exists=True, dir_okay=False),
            cores:  int = typer.Option(None, help="Set the number of cores to use. If None will use all cores."),
            help_snakemake: Optional[bool] = typer.Option(
                False, help="Print the snakemake help", is_eager=True, callback=_print_snakemake_help
            ),
            verbose: Optional[bool] = typer.Option(False, "--verbose"),
        ):
        args = []
        conda_prefix_dir = pipeline_dir_path / '.conda'
        if not cores:
            cores = 'all'
        args.extend([
            "--use-conda",
            f"--conda-prefix={conda_prefix_dir}",
            f"--cores={cores}",
        ])
        snakefile = pipeline_dir_path / 'workflow' / 'Snakefile'
        if not snakefile.exists():
            raise ValueError('Could not find Snakefile')
        else:
            args.append(f"--snakefile={snakefile}")
        
        if not configfile:
            configfile = get_config_from_pipeline_dir(pipeline_dir_path)
        args.append(f"--configfile={configfile}")

        
        # Set up conda frontend
        mamba_found = True
        try:
            subprocess.run(["mamba", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            mamba_found = False
        if not mamba_found:
            args.append("--conda-frontend=conda")
        
        typer.echo(create_logo(pipeline_dir_path.name))
        typer.echo()

        if verbose:
            args.insert(0, "--verbose")

        if target:
            args.append(target)
        args.extend(parse_config_args(ctx.args, options=options))

        if verbose:
            typer.secho(f"snakemake {' '.join(args)}\n", fg=typer.colors.MAGENTA)

        snakemake.main(args)
    
    @app.command(help="Access the pipeline configuration.")
    def config():
        config_path = pipeline_dir_path / 'config' / 'config.yaml'
        if not config_path.exists():
            typer.secho("Could not find config...", fg='red')
            raise typer.Exit(1)
        with open(config_path) as f:
            code = f.read()
            syntax = Syntax(code, 'yaml')
            console = Console()
            console.print(syntax)
    
    
    @app.command(help="Display information about current pipeline install.")
    def info():
        import json
        info_dict = {}
        info_dict['name'] = pipeline_dir_path.name
        info_dict['version'] = None
        info_dict['pipeline_dir_path'] = str(pipeline_dir_path)
        typer.echo(json.dumps(info_dict, indent=2))
    
    @app.command(help="Access the pipeline conda environments.")
    def env(
        activate: str = typer.Option(None, help="Activate a given environment"),
    ):
        raise NotImplementedError
    
            
    return app
 

