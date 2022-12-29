import typer
from pathlib import Path
import os
from typing import Optional
from rich.pretty import pprint
from .nest import Nest

app = typer.Typer()


@app.callback()
def callback():
    """
    SNK
    """

@app.command()
def list():
    """
    List the installed pipelines
    """
    nest = Nest()
    try:
        pipelines = os.listdir(nest.pipelines_dir)
    except FileNotFoundError:
        pipelines = []
    pprint(pipelines)


@app.command()
def install(
        url: str = typer.Argument(..., help="URL of the repo to install (valid git url, see http://www.kernel.org/pub/software/scm/git/docs/git-clone.html#URLS)"),
        name: Optional[str] = typer.Option(None, help="Rename the pipeline (this name will be used to call the CLI.)"),
        snk_home: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides default snk location. Path to directory where all pipelines will be installed."),
        bin_dir: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides location of pipeline installations. Path to folder in PATH where pipeline are symlinked."),
    ):
    """
    Install a pipeline
    """
    nest = Nest(snk_home=snk_home, bin_dir=bin_dir)
    pipeline = nest.install(repo_url=url, name=name)
    typer.secho(f"Successfully installed {pipeline.name}!")

@app.command()
def uninstall(
        name: str = typer.Argument(..., help="Name of the pipeline to uninstall."),
        snk_home: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides default snk location. Path to directory where all pipelines will be installed."),
        bin_dir: Optional[Path] = typer.Option(None, dir_okay=True, file_okay=False, exists=True, help="Overrides location of pipeline installations. Path to folder in PATH where pipeline are symlinked."),
    ):
    """
    snk ❯ snk uninstall micromamba
    ==> Uninstalling Pipeline micromamba
    ==> Unlinking Binary '/opt/homebrew/bin/micromamba'
    ==> Purging files for version 1.1.0,0 of Cask micromamba
    """
    nest = Nest(snk_home=snk_home, bin_dir=bin_dir)
    nest.uninstall(name)
    typer.secho(f"Successfully uninstalled {name}!")


@app.command()
def update():
    """
    Update a pipeline
    """
    pass


@app.command()
def run():
    """
    Run the pipeline in a temporary environment.
    """
    pass