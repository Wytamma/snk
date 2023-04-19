import typer
from pathlib import Path
import os
from typing import Optional, List
from rich.pretty import pprint
from .nest import Nest
from .errors import PipelineExistsError, PipelineNotFoundError

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
            ..., help="Path, URL or Github name (user/repo) of the pipeline to install."
        ),
        name: Optional[str] = typer.Option(
            None, 
            help="Rename the pipeline (this name will be used to call the CLI.)"
        ),
        tag: Optional[str] = typer.Option(
            None,
            "--tag",
            "-t",
            help="Tag (version) of the pipeline to install. Can specify a branch name, or tag. If None the latest commit will be installed."
        ),
        config: Optional[Path] = typer.Option(
            None, 
            help="Specify a non-standard config location."
        ),
        resource: Optional[List[Path]] = typer.Option(
            [], 
            help="Specify a resource required to run the pipeline (copied to working dir at runtime)."
        ),
    ):
    """
    Install a pipeline.
    """
    nest = Nest(snk_home=SNK_HOME, bin_dir=SNK_BIN)
    if not Path(pipeline).exists() and not pipeline.startswith('http'):
        pipeline = f"https://github.com/{pipeline}.git"
    try:
        installed_pipeline = nest.install(pipeline, name=name, tag=tag, config=config, resources=resource)
    except PipelineExistsError as e:
        typer.secho(e, fg='red')
        raise typer.Exit()
    except PipelineNotFoundError as e:
        typer.secho(e, fg='red')
        raise typer.Exit()
    v = installed_pipeline.version
    v = v if v else 'latest'
    typer.secho(f"Successfully installed {installed_pipeline.name} ({v})!", fg='green')


@app.command()
def uninstall(
        name: str = typer.Argument(..., help="Name of the pipeline to uninstall."),
        force: Optional[bool] = typer.Option(False, '--force', '-f', help="Force uninstall without asking."),
    ):
    """
    Uninstall a pipeline.
    """
    nest = Nest(snk_home=SNK_HOME, bin_dir=SNK_BIN)
    try:
        uninstalled = nest.uninstall(name, force=force)
    except PipelineNotFoundError as e:
        typer.secho(e, fg='red')
        raise typer.Exit(1)
    if uninstalled:
        typer.secho(f"Successfully uninstalled {name}!", fg='green')
        

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
def run(        
        pipeline: str = typer.Argument(
            ..., help="URL or Github name (user/repo) of the pipeline to install."
        ),
    ):
    """
    Run the pipeline in a temporary environment.
    """
    raise NotImplementedError

@app.command()
def annotations(config: Path):
    """Generate annotations defaults from config file"""
    raise NotImplementedError

@app.command()
def create(name: str):
    """Create a default project that can be installed with snk"""
    raise NotImplementedError