from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from snk_cli.config import SnkConfig

from .__about__ import __version__
from .errors import WorkflowExistsError, WorkflowNotFoundError
from .nest import Nest
from .utils import open_text_editor

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
    isolate: Optional[bool] = typer.Option(
        False,
        "--isolate",
        "-i",
        help="Install the workflow in a isolated environment.",
    ),
    snakemake_version: Optional[str] = typer.Option(
        None,
        "--snakemake",
        "-s",
        help="Snakemake version to install with the isolated workflow. Default is the latest version.",
    ),
    dependencies: Optional[List[str]] = typer.Option(
        [],
        "--dependency",
        "-d",
        help="Additional pip dependencies to install with the workflow.",
    ),
    config: Optional[Path] = typer.Option(None, help="Specify a non-standard config location."),
    snakefile: Optional[Path] = typer.Option(
        None, help="Specify a non-standard Snakefile location."
    ),
    resource: Optional[List[Path]] = typer.Option(
        [],
        help="Specify resources additional to the resources folder required by the workflow (copied to working dir at runtime).",
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
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Installing...", total=None)
            installed_workflow = nest.install(
                workflow,
                editable=editable,
                name=name,
                tag=tag,
                commit=commit,
                config=config,
                snakefile=snakefile,
                additional_resources=resource,
                force=force,
                conda=not no_conda,
                snakemake_version=snakemake_version,
                dependencies=dependencies,
                isolate=isolate,
            )
    except WorkflowExistsError as e:
        typer.secho(
            str(e) + ". Use a different name (--name) or overwrite (--force).",
            fg="red",
            err=True,
        )
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(e, fg="red", err=True)
        raise typer.Exit(1)

    snk_config = SnkConfig.from_workflow_dir(installed_workflow.path, create_if_not_exists=True)
    version = snk_config.version
    version_str = f" ({version})" if version else ""
    typer.secho(f"Successfully installed {installed_workflow.name}{version_str}!", fg="green")


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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show the workflow paths."),
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
        snk_config = SnkConfig.from_workflow_dir(workflow.path, create_if_not_exists=True)
        if snk_config.version == "editable":
            version_str = "[green]editable[/green]"
        else:
            version_str = f"[blue]{snk_config.version}[/blue]"
        if verbose:
            table.add_row(
                workflow.name,
                version_str,
                f"[yellow]{str(workflow.path.resolve())}[/yellow]",
            )
        else:
            table.add_row(workflow.name, version_str)
    console = Console()
    console.print(table)

@app.command()
def create(path: Path, force: bool = typer.Option(False, "--force", "-f")):
    """Create a default snk.yaml project that can be installed with snk"""
    if path.exists():
        if not force:
            typer.secho(f"Directory '{path}' already exists! Use --force to overwrite.", fg="red", err=True)
            raise typer.Exit(1)
        else:
            typer.secho(f"Overwriting existing directory '{path}'.", fg="yellow", err=True)
            import shutil
            shutil.rmtree(path)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        typer.secho(f"Directory '{path}' already exists! Use --force to overwrite.", fg="red", err=True)
        raise typer.Exit(1)
    snk_config = SnkConfig.from_workflow_dir(path, create_if_not_exists=True)
    snk_config.cli["msg"] = {
        "help": "Print a help message.",
        "default": "Hello, World!",
        "required": False,
        "short": "m",
    }
    snk_config.save()
    typer.echo(f"Created snk.yaml at {snk_config._snk_config_path}")
    with open(path / "Snakefile", "w") as f:
        f.write("""rule all:\n    shell: f"echo {config['msg']}"\n""")

@app.command()
def edit(
    ctx: typer.Context,
    workflow_name: str = typer.Argument(
        ..., help="Name of the workflow to configure."
    ),
    path: bool = typer.Option(
        False, "--path", "-p", help="Show the path to the snk.yaml file."
    ),
):
    """
    Access the snk.yaml configuration file for a workflow.
    """
    nest = Nest(snk_home=ctx.obj.snk_home, bin_dir=ctx.obj.snk_bin)
    try:
        workflows = nest.workflows
    except FileNotFoundError:   
        workflows = []
    workflow = next((w for w in workflows if w.name == workflow_name), None) 
    if not workflow:
        typer.secho(f"Workflow '{workflow_name}' not found!", fg="red", err=True)
        raise typer.Exit(1)
    snk_config = SnkConfig.from_workflow_dir(workflow.path, create_if_not_exists=True)
    snk_config.save()
    if path:
        typer.echo(snk_config._snk_config_path)
    else:
        try:
            open_text_editor(snk_config._snk_config_path)
        except Exception as e:
            typer.secho(str(e), fg="red", err=True)
            raise typer.Exit(1)

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
# def update():
#     """
#     Update a workflow.
#     """
#     raise NotImplementedError
