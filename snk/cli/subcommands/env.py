import os
import shutil
import subprocess
from pathlib import Path
import sys
from typing import List, Optional
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.workflow import create_workflow
from snk.workflow import Workflow
from rich.console import Console
from rich.syntax import Syntax
from snakemake.deployment.conda import Conda, Env, CreateCondaEnvironmentException
from snk.cli.config.config import get_config_from_workflow_dir


class EnvApp(DynamicTyper):
    def __init__(
        self,
        workflow: Workflow,
        conda_prefix_dir: Path,
        snakemake_config,
        snakefile: Path,
    ):
        self.workflow = workflow
        self.conda_prefix_dir = conda_prefix_dir
        self.snakemake_config = snakemake_config
        self.snakefile = snakefile
        self.configfile = get_config_from_workflow_dir(self.workflow.path)
        self.workflow = create_workflow(
            self.snakefile,
            config=self.snakemake_config,
            configfiles=[self.configfile] if self.configfile else None,
            use_conda=True,
            conda_prefix=self.conda_prefix_dir.resolve(),
        )
        self.register_command(self.list, help="List the environments in the workflow.")
        self.register_command(
            self.show, help="Show the contents of an environment."
        )
        self.register_command(
            self.run, help="Run a command in one of the workflow environments."
        )
        self.register_command(
            self.activate, help="Activate a workflow conda environment."
        )
        self.register_command(self.prune, help="Delete all conda environments.")
        self.register_command(self.create, help="Create all conda environments.")

    def list(
            self,
            verbose: bool = typer.Option(False, "--verbose", "-v", help="Show profiles as paths."), 
        ):
        number_of_environments = len(self.workflow.environments)
        typer.echo(
            f"Found {number_of_environments} environment{'' if number_of_environments == 1 else 's'}:"
        )
        for env in self.workflow.environments:
            if verbose:
                typer.echo(f"- {typer.style(env, fg=typer.colors.YELLOW)}")
            else:
                typer.echo(f"- {env.stem}")

    def _get_conda_env_path(self, name: str) -> Path:
        env = [e for e in self.workflow.environments if e.stem == name]
        if not env:
            self.error(f"Environment {name} not found!")
        return env[0]

    def _shellcmd(self, env_address: str, cmd: str) -> str:
        if sys.platform.lower().startswith("win"):
            return Conda().shellcmd_win(env_address, cmd)
        return Conda().shellcmd(env_address, cmd)

    def show(
        self, 
        name: str = typer.Argument(..., help="The name of the environment."),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print the environment."
        ),
    ):
        env_path = self._get_conda_env_path(name)
        env_file_text = env_path.read_text()
        if pretty:
            syntax = Syntax(env_file_text, "yaml")
            console = Console()
            console.print(syntax)
        else:
            typer.echo(env_file_text)

    def run(
        self,
        name: str = typer.Argument(..., help="The name of the environment."),
        cmd: List[str] = typer.Argument(..., help="The command to run in environment."),
    ):
        env_path = self._get_conda_env_path(name)
        env = Env(self.workflow, env_file=env_path.resolve())
        env.create()
        cmd = self._shellcmd(env.address, " ".join(cmd))
        subprocess.run(cmd, shell=True, env=os.environ.copy())

    def prune(
        self,
        force: bool = typer.Option(
            False, "--force", "-f", help="Force deletion of the environments."
        ),
    ):
        if force or input(f"Delete {self.conda_prefix_dir}? [y/N] ").lower() == "y":
            # delete self.conda_prefix_dir directory
            shutil.rmtree(self.conda_prefix_dir)
            self.log(f"Deleted {self.conda_prefix_dir}")

    def create(self):
        for env_path in self.workflow.environments:
            env = Env(self.workflow, env_file=env_path.resolve())
            try:
                env.create()
            except CreateCondaEnvironmentException:
                self.error(
                    f"Environment {env_path.name} could not be created!", exit=False
                )

    def activate(
        self, name: str = typer.Argument(..., help="The name of the environment.")
    ):
        env_path = self._get_conda_env_path(name)
        self.log(f"Activating {name} environment... (type 'exit' to deactivate)")
        env = Env(self.workflow, env_file=env_path.resolve())
        env.create()
        user_shell = os.environ.get("SHELL", "/bin/sh")
        activate_cmd = self._shellcmd(env.address, user_shell)
        self.log(activate_cmd)
        subprocess.run(activate_cmd, shell=True, env=os.environ.copy())
        self.log(f"Exiting {name} environment...")
