from types import SimpleNamespace
import typer
from pathlib import Path
from typing import Optional, List
from rich import print
from .nest import Nest
from .errors import PipelineExistsError, PipelineNotFoundError

app = typer.Typer()

SNK_HOME = None
SNK_BIN = None

# fmt: off
@app.callback(context_settings={"help_option_names": ["-h", "--help"]})
def callback(
    ctx: typer.Context,
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
    ctx.obj = SimpleNamespace(snk_home = home, snk_bin = bin)
# fmt: on


@app.command()
def install(
    ctx: typer.Context,
    pipeline: str = typer.Argument(
        ..., help="Path, URL or Github name (user/repo) of the pipeline to install."
    ),
    name: Optional[str] = typer.Option(
        None, 
        "--name",
        "-n",
        help="Rename the pipeline (this name will be used to call the CLI.)"
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Tag (version) of the pipeline to install. Can specify a branch name, or tag. If None the latest commit will be installed.",
    ),
    config: Optional[Path] = typer.Option(
        None, help="Specify a non-standard config location."
    ),
    resource: Optional[List[Path]] = typer.Option(
        [],
        help="Specify resources additional to the resources folder required by the pipeline (copied to working dir at runtime).",
    ),
    force: Optional[bool] = typer.Option(
        False, "--force", "-f", help="Force install (overwrites existing installs)."
    ),
    editable: Optional[bool] = typer.Option(
        False, "--editable", "-e", help="Whether to install the pipeline in editable mode."
    ),
):
    """
    Install a pipeline.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    if not nest.bin_dir_in_path():
        bin_dir_yellow = typer.style(nest.bin_dir, fg=typer.colors.YELLOW, bold=False)
        typer.echo(f"Please add SNK_BIN to your $PATH: {bin_dir_yellow}")
    if not Path(pipeline).exists() and not pipeline.startswith("http"):
        pipeline = f"https://github.com/{pipeline}.git"
    try:
        installed_pipeline = nest.install(
            pipeline,
            editable=editable,
            name=name,
            tag=tag,
            config=config,
            additional_resources=resource,
            force=force
        )
    except PipelineExistsError as e:
        typer.secho(e, fg="red")
        raise typer.Exit()
    except PipelineNotFoundError as e:
        typer.secho(e, fg="red")
        raise typer.Exit()
    v = installed_pipeline.version
    v = v if v else "latest"
    typer.secho(f"Successfully installed {installed_pipeline.name} ({v})!", fg="green")


@app.command()
def uninstall(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the pipeline to uninstall."),
    force: Optional[bool] = typer.Option(
        False, "--force", "-f", help="Force uninstall without asking."
    ),
):
    """
    Uninstall a pipeline.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    try:
        uninstalled = nest.uninstall(name, force=force)
    except PipelineNotFoundError as e:
        typer.secho(e, fg="red")
        raise typer.Exit(1)
    if uninstalled:
        typer.secho(f"Successfully uninstalled {name}!", fg="green")


# @app.command()
# def update():
#     """
#     Update a pipeline.
#     """
#     raise NotImplementedError


@app.command()
def list(
    ctx: typer.Context,
):
    """
    List the installed pipelines.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    try:
        pipelines = nest.pipelines
    except FileNotFoundError:
        pipelines = []
    pipeline_dir_yellow = typer.style(
        nest.snk_pipelines_dir, fg=typer.colors.YELLOW, bold=False
    )
    typer.echo(f"Found {len(pipelines)} pipelines in {pipeline_dir_yellow}")
    for pipeline in pipelines:
        if pipeline.editable:
            print(f'- {pipeline.name} ([bold green]editable[/bold green]) -> "{pipeline.path}"')
            continue
        v = pipeline.version
        v = v if v else "latest"
        print(f"- {pipeline.name} ([bold green]{v}[/bold green])")


# @app.command()
# def run(
#         pipeline: str = typer.Argument(
#             ..., help="URL or Github name (user/repo) of the pipeline to install."
#         ),
#     ):
#     """
#     Run the pipeline in a temporary environment.
#     """
#     raise NotImplementedError

# @app.command()
# def annotations(config: Path):
#     """Generate annotations defaults from config file"""
#     raise NotImplementedError

# @app.command()
# def create(name: str):
#     """Create a default project that can be installed with snk"""
#     raise NotImplementedError
