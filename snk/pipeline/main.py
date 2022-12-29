import typer
from pathlib import Path
from typing import Optional, List

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art
import subprocess

def _print_snakemake_help(value: bool):
    if value:
        snakemake.main("-h")

def create_logo(name):
    logo = text2art(name, font="small")        
    doc  = f"""\b{logo}\nA Snakemake pipeline packaged with snk"""
    return doc

def pipeline_cli_factory(pipeline_dir_path: Path):
    app = typer.Typer()

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
    callback.__doc__ = create_logo(pipeline_dir_path.name)

    @app.command(help="Run the pipeline.", context_settings={"allow_extra_args": True, "ignore_unknown_options": True, "help_option_names": ["-h", "--help"]})
    def run(
            ctx: typer.Context,
            cores:  Optional[str] = typer.Option('all', help="Set the number of cores to use"),
            config: Optional[List[str]] = typer.Option(
                [], "--config", "-C", help="Set or overwrite values in the pipeline config object (see Snakemake docs)"
            ),
            configfile: Optional[Path] = typer.Option(None, help="Path to config file."),
            help_snakemake: Optional[bool] = typer.Option(
                False, help="Print the snakemake help", is_eager=True, callback=_print_snakemake_help
            ),
            verbose: Optional[bool] = typer.Option(False, "--verbose"),
        ):
        
        conda_prefix_dir = pipeline_dir_path / '.conda'
        
        args = [
            f"--conda-prefix={conda_prefix_dir}",
            f"--cores={cores}",
            "--use-conda"
        ]

        snakefile = pipeline_dir_path / 'workflow' / 'Snakefile'
        if not snakefile.exists():
            raise ValueError('Could not find Snakefile')
        else:
            args.append(f"--snakefile={snakefile}")
        
        configfile = pipeline_dir_path / 'config' / 'config.yaml'
        if configfile.exists():
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

        args.extend([*ctx.args, "--config", *config])

        if verbose:
            typer.secho(f"snakemake {' '.join(args)}", fg=typer.colors.MAGENTA)

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
    
    
    @app.command(help="Display the expected inputs.")
    def inputs():
        raise NotImplementedError
    
    @app.command(help="Display information about current pipeline install.")
    def info():
        import json
        info_dict = {}
        info_dict['name'] = pipeline_dir_path.name
        info_dict['version'] = None
        info_dict['pipeline_dir_path'] = str(pipeline_dir_path)
    
        typer.echo(json.dumps(info_dict, indent=2))
            
    return app
 

