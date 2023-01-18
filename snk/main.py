import typer
from pathlib import Path
import os
from typing import Optional
from rich.pretty import pprint
from .nest import Nest

app = typer.Typer()

SNK_HOME = None
SNK_BIN = None

@app.callback(context_settings={"help_option_names": ["-h", "--help"]})
def callback(
    home: Optional[Path] = typer.Option(
            None, 
            envvar="SNK_HOME", 
            dir_okay=True, 
            file_okay=False, 
            exists=True, 
            help="Overrides default snk location. Pipelines will be installed in $SNK_HOME/pipelines."
        ),
    bin: Optional[Path] = typer.Option(
            None, 
            envvar="SNK_BIN", 
            dir_okay=True, 
            file_okay=False, 
            exists=True, 
            help="Overrides location of pipeline installations. Pipelines are symlinked here."
        )
    ):
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
    global SNK_BIN, SNK_HOME
    SNK_BIN = bin
    SNK_HOME = home
    


@app.command()
def install(
        pipeline: str = typer.Argument(
            ..., help="URL or Github name (user/repo) of the pipeline to install."
        ),
        name: Optional[str] = typer.Option(
            None, 
            help="Rename the pipeline (this name will be used to call the CLI.)"
        ),
    ):
    """
    Install a pipeline.
    """
    
    nest = Nest(snk_home=SNK_HOME, bin_dir=SNK_BIN)
    if not pipeline.startswith('http'):
        pipeline = f"https://github.com/{pipeline}.git"
        typer.echo(f'Installing Pipeline from Github: {pipeline}')
    cli = nest.install(repo_url=pipeline, name=name)
    typer.secho(f"Successfully installed {cli.name}!")


@app.command()
def uninstall(
        name: str = typer.Argument(..., help="Name of the pipeline to uninstall."),
        force: Optional[bool] = typer.Option(False, '--force', '-f', help="Force uninstall without asking."),
    ):
    """
    Uninstall a pipeline.
    """
    nest = Nest(snk_home=SNK_HOME, bin_dir=SNK_BIN)
    uninstalled = nest.uninstall(name, force=force)
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