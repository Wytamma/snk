import typer
from pathlib import Path
from typing import Optional, List
import sys
import json
import logging
from datetime import datetime

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art
import subprocess

from .utils import add_dynamic_options, flatten
from snk.nest import Pipeline

def _print_snakemake_help(value: bool):
    if value:
        snakemake.main("-h")

def create_logo(name):
    logo = text2art(name, font="small")        
    doc  = f"""\b{logo}\bA Snakemake pipeline CLI generated with snk"""
    return doc

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

def get_config_from_pipeline_dir(pipeline_dir_path: Path):
    """Search possible config locations"""
    for path in [Path('config') / 'config.yaml', Path('config') / 'config.yml', 'config.yaml', 'config.yml']:
        if (pipeline_dir_path / path).exists():
            return pipeline_dir_path / path 
    return None


def load_options(pipeline_dir_path: Path):
    pipeline_config_path = get_config_from_pipeline_dir(pipeline_dir_path)
    if not pipeline_config_path.exists():
        return []
    config = snakemake.load_configfile(pipeline_config_path)
    flat_config = flatten(config)
    options = []
    catalog_config_path = pipeline_dir_path / '.snakemake-workflow-catalog.yml'
    snk_config_path = pipeline_dir_path / '.snk'
    if snk_config_path.exists():
        snk_config = snakemake.load_configfile(snk_config_path)
    elif catalog_config_path.exists():
        catalog_config = snakemake.load_configfile(catalog_config_path)
        snk_config = catalog_config.get('snk', {})
    else:
        snk_config = {}
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

def snk_cli(pipeline_dir_path: Path):
    app = typer.Typer()
    options = load_options(pipeline_dir_path)
    pipeline = Pipeline(path=pipeline_dir_path)
    snakefile = pipeline_dir_path / 'workflow' / 'Snakefile'
    conda_prefix_dir = pipeline_dir_path / '.conda'

    def _print_pipline_version(value: bool):
        if value:
            typer.echo(pipeline.version)
            raise typer.Exit()

    def _print_pipline_path(value: bool):
        if value:
            typer.echo(pipeline.path)
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

    @app.command(
            help="Run the pipeline. All unrecognized arguments are parsed onto Snakemake to be used by the pipeline.", 
            context_settings={
                "allow_extra_args": True, 
                "ignore_unknown_options": True, 
                "help_option_names": ["-h", "--help"]
            })
    @add_dynamic_options(options)
    def run(
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
            f"--conda-prefix={conda_prefix_dir}",
            f"--cores={cores}",
        ])
        if not snakefile.exists():
            raise ValueError('Could not find Snakefile')
        else:
            args.append(f"--snakefile={snakefile}")
        
        if not configfile:
            configfile = get_config_from_pipeline_dir(pipeline_dir_path)
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
        
        typer.echo(create_logo(pipeline_dir_path.name))
        typer.echo()

        if verbose:
            args.insert(0, "--verbose")

        if target:
            args.append(target)
        targets_and_or_snakemake, config_dict_list = parse_config_args(ctx.args, options=options)

        args.extend(targets_and_or_snakemake)

        args.extend(["--config", *[f"{list(c.keys())[0]}={list(c.values())[0]}" for c in config_dict_list]])

        if verbose:
            typer.secho(f"snakemake {' '.join(args)}\n", fg=typer.colors.MAGENTA)
        if web_gui:
            launch_gui(
                snakefile,
                conda_prefix_dir,
                pipeline_dir_path,
                config={k: v for dct in config_dict_list for k, v in dct.items()}
            )
        else:
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
        info_dict['version'] = pipeline.version
        info_dict['pipeline_dir_path'] = str(pipeline_dir_path)
        typer.echo(json.dumps(info_dict, indent=2))
    
    @app.command(help="Access the pipeline conda environments.")
    def env(
        name: Optional[str] = typer.Argument(None)
    ):
        raise NotImplementedError

    @app.command(help="Access the pipeline scripts.")
    def script(
        name: Optional[str] = typer.Argument(None)
    ):
        raise NotImplementedError
    
    return app


def launch_gui(
        snakefile,
        conda_prefix_dir,
        pipeline_dir_path,
        config,
        host: Optional[str] = "127.0.0.1",
        port: Optional[int] = 8000,
        cluster: Optional[str] = None,
    ):
    try:
        import snakemake.gui as gui
        from functools import partial
        import webbrowser
        from threading import Timer
    except ImportError:
        typer.secho(
            "Error: GUI needs Flask to be installed. Install "
            "with easy_install or contact your administrator.",
            err=True)
        raise typer.Exit(1)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    _snakemake = partial(snakemake.snakemake, snakefile)

    gui.app.extensions["run_snakemake"] = _snakemake
    gui.app.extensions["args"] = dict(
        cluster=cluster,
        configfiles=[get_config_from_pipeline_dir(pipeline_dir_path)],
        targets=[],
        use_conda=True,
        conda_frontend="mamba",
        conda_prefix=conda_prefix_dir,
        config=config
    )
    gui.app.extensions["snakefilepath"] = snakefile
    target_rules = []
    def log_handler(msg):
        if msg["level"] == "rule_info":
            target_rules.append(msg["name"])
    gui.run_snakemake(list_target_rules=True, log_handler=[log_handler], config=config)
    gui.app.extensions["targets"] = target_rules

    resources = []
    def log_handler(msg):
        if msg["level"] == "info":
            resources.append(msg["msg"])

    gui.app.extensions["resources"] = resources
    gui.run_snakemake(list_resources=True, log_handler=[log_handler], config=config)
    url = "http://{}:{}".format(host, port)
    print("Listening on {}.".format(url), file=sys.stderr)

    def open_browser():
        try:
            webbrowser.open(url)
        except:
            pass

    print("Open this address in your browser to access the GUI.", file=sys.stderr)
    Timer(0.5, open_browser).start()
    success = True

    try:
        gui.app.run(debug=False, threaded=True, port=int(port), host=host)

    except (KeyboardInterrupt, SystemExit):
        # silently close
        pass



