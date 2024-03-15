from types import SimpleNamespace
import typer
from pathlib import Path
from typing import Optional, List
from .nest import Nest
from .errors import WorkflowExistsError, WorkflowNotFoundError
from .__about__ import __version__
from snk_cli.config import SnkConfig

app = typer.Typer()

SNK_HOME = None
SNK_BIN = None

def _print_snk_version(self, ctx: typer.Context, value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()

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
            help="Overrides default snk location. Workflows will be installed in $SNK_HOME/workflows."
        ),
    bin: Optional[Path] = typer.Option(
            None, 
            envvar="SNK_BIN", 
            dir_okay=True, 
            file_okay=False, 
            exists=True, 
            help="Overrides location of workflow installations. Workflows are symlinked here."
        ),
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        help="Show the version and exit.",
        is_eager=True,
        callback=_print_snk_version,
        show_default=False,
        ),
    ):
    # suppress python warning 
    ctx.obj = SimpleNamespace(snk_home = home, snk_bin = bin)
# fmt: on

callback.__doc__ = "\b"
callback.__doc__ += r"""        _            _             _        
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
"""
callback.__doc__ += f"\b\n\nA Snakemake Workflow Management System ({__version__})"

@app.command()
def install(
    ctx: typer.Context,
    workflow: str = typer.Argument(
        ..., help="Path, URL or Github name (user/repo) of the workflow to install."
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Rename the workflow (this name will be used to call the CLI.)",
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Tag (version) of the workflow to install. Can specify a branch name, or tag. If None the latest commit will be installed.",
    ),
    commit: Optional[str] = typer.Option(
        None,
        "--commit",
        "-c",
        help="Commit (SHA) of the workflow to install. If None the latest commit will be installed.",
    ),
    config: Optional[Path] = typer.Option(
        None, help="Specify a non-standard config location."
    ),
    resource: Optional[List[Path]] = typer.Option(
        [],
        help="Specify resources additional to the resources folder required by the workflow (copied to working dir at runtime).",
    ),
    snakemake_version: Optional[str] = typer.Option(
        None,
        "--snakemake",
        help="Specify a specific version of snakemake to use.",
    ),
    no_conda: bool = typer.Option(
        False,
        "--no-conda",
        help="Do not use conda environments by default.",
    ),
    force: Optional[bool] = typer.Option(
        False, "--force", "-f", help="Force install (overwrites existing installs)."
    ),
    editable: Optional[bool] = typer.Option(
        False,
        "--editable",
        "-e",
        help="Whether to install the workflow in editable mode.",
    ),
):
    """
    Install a workflow.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    if not nest.bin_dir_in_path():
        bin_dir_yellow = typer.style(nest.bin_dir, fg=typer.colors.YELLOW, bold=False)
        typer.echo(f"Please add SNK_BIN to your $PATH: {bin_dir_yellow}")
    if not Path(workflow).exists() and not workflow.startswith("http"):
        workflow = f"https://github.com/{workflow}.git"
    try:
        installed_workflow = nest.install(
            workflow,
            editable=editable,
            name=name,
            tag=tag,
            commit=commit,
            config=config,
            additional_resources=resource,
            force=force,
            conda=not no_conda,
            snakemake_version=snakemake_version,
        )
    except WorkflowExistsError as e:
        typer.secho(str(e) + ". Use a different name (--name) or overwrite (--force).", fg="red", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(e, fg="red", err=True)
        raise typer.Exit(1)
    
    if editable:
        version = "editable"
    elif installed_workflow.version is None:
        snk_config = SnkConfig.from_workflow_dir(installed_workflow.path)
        version = snk_config.version
    else:
        version = installed_workflow.version

    typer.secho(f"Successfully installed {installed_workflow.name} ({version})!", fg="green")


@app.command()
def uninstall(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the workflow to uninstall."),
    force: Optional[bool] = typer.Option(
        False, "--force", "-f", help="Force uninstall without asking."
    ),
):
    """
    Uninstall a workflow.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    try:
        uninstalled = nest.uninstall(name, force=force)
    except WorkflowNotFoundError as e:
        typer.secho(e, fg="red")
        raise typer.Exit(1)
    if uninstalled:
        typer.secho(f"Successfully uninstalled {name}!", fg="green")


@app.command()
def list(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show the workflow paths."
    ),
):
    """
    List the installed workflows.
    """
    from rich.console import Console
    from rich.table import Table

    table = Table("Workflow", "Version", show_header=True, show_lines=True)
    if verbose:
        table.add_column("Path")
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    try:
        workflows = nest.workflows
    except FileNotFoundError:
        workflows = []
    for workflow in workflows:
        version = workflow.version
        if version is None:
            snk_config = SnkConfig.from_workflow_dir(workflow.path)
            version = snk_config.version
        version_str = "[green]editable[/green]" if workflow.editable else f"[blue]{version}[/blue]"
        if verbose:
            table.add_row(workflow.name, version_str, f"[yellow]{str(workflow.path.resolve())}[/yellow]")
        else:
            table.add_row(workflow.name, version_str)
    console = Console()
    console.print(table)

# @app.command()
# def run(
#         workflow: str = typer.Argument(
#             ..., help="URL or Github name (user/repo) of the workflow to install."
#         ),
#     ):
#     """
#     Run the workflow in a temporary environment.
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

# @app.command()
# def update():
#     """
#     Update a workflow.
#     """
#     raise NotImplementedError