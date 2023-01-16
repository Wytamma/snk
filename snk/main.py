import typer
from pathlib import Path
import os
from typing import Optional
from rich.pretty import pprint
from .nest import Nest

app = typer.Typer()


@app.callback(context_settings={"help_option_names": ["-h", "--help"]})
def callback():
    """\b
        _            _             _        
       / /\         /\ \     _    /\_\      
      / /  \       /  \ \   /\_\ / / /  _   
     / / /\ \__   / /\ \ \_/ / // / /  /\_\ 
    / / /\ \___\ / / /\ \___/ // / /__/ / / 
    \ \ \ \/___// / /  \/____// /\_____/ /  
     \ \ \     / / /    / / // /\_______/   
 _    \ \ \   / / /    / / // / /\ \ \      
/_/\__/ / /  / / /    / / // / /  \ \ \     
\ \/___/ /  / / /    / / // / /    \ \ \    
 \_____\/   \/_/     \/_/ \/_/      \_\_\   
 \b
 \n
 Snakemake pipeline management system
    """


@app.command()
def install(
        pipeline: str = typer.Argument(..., help="URL or Github name (user/repo) of the pipeline to install."),
        name: Optional[str] = typer.Option(None, help="Rename the pipeline (this name will be used to call the CLI.)"),
        home: Optional[Path] = typer.Option(None, envvar="SNK_HOME", dir_okay=True, file_okay=False, exists=True, help="Overrides default snk location. Path to directory where all pipelines will be installed."),
        bin: Optional[Path] = typer.Option(None, envvar="SNK_BIN", dir_okay=True, file_okay=False, exists=True, help="Overrides location of pipeline installations. Path to folder in PATH where pipeline are symlinked."),
    ):
    """
    Install a pipeline.
    """
    nest = Nest(snk_home=home, bin_dir=bin)
    if not pipeline.startswith('http'):
        pipeline = f"https://github.com/{pipeline}.git"
        typer.echo(f'Installing Pipeline from Github: {pipeline}')
    cli = nest.install(repo_url=pipeline, name=name)
    typer.secho(f"Successfully installed {cli.name}!")

@app.command()
def uninstall(
        name: str = typer.Argument(..., help="Name of the pipeline to uninstall."),
        snk_home: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides default snk location. Path to directory where all pipelines will be installed."),
        bin_dir: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides location of pipeline installations. Path to folder in PATH where pipeline are symlinked."),
    ):
    """
    Uninstall a pipeline.
    """
    # snk ❯ snk uninstall micromamba
    # ==> Uninstalling Pipeline micromamba
    # ==> Unlinking Binary '/opt/homebrew/bin/micromamba'
    # ==> Purging files for version 1.1.0,0 of Cask micromamba
    nest = Nest(snk_home=snk_home, bin_dir=bin_dir)
    uninstalled = nest.uninstall(name)
    if uninstalled:
        typer.secho(f"Successfully uninstalled {name}!")
        


@app.command()
def update():
    """
    Update a pipeline.
    """
    raise NotImplementedError


@app.command()
def list():
    """
    List the installed pipelines.
    """
    nest = Nest()
    try:
        pipelines = os.listdir(nest.pipelines_dir)
    except FileNotFoundError:
        pipelines = []
    pprint(pipelines)


@app.command()
def run():
    """
    Run the pipeline in a temporary environment.
    """
    raise NotImplementedError

def annotations():
    """gen annotations defaults from config file"""

def create():
    """create a default project that can be installed with snk"""