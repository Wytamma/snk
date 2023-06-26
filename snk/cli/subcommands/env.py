import subprocess
import sys
from pathlib import Path
from typing import Optional
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.pipeline import Pipeline
from rich.console import Console
from rich.syntax import Syntax
from snakemake.deployment.conda import Conda

class EnvApp(DynamicTyper):
    def __init__(self, pipeline: Pipeline, conda_prefix_dir: Path):
        self.pipeline = pipeline
        self.conda_prefix_dir = conda_prefix_dir
        self.app = typer.Typer()
        self.register_command(self.list, help="List the environments in the pipeline.")
        self.register_command(self.show, help="Show the environments config file contents.")
        self.register_command(self.run, help="Run a command in one of the pipeline environments.")
        self.register_command(self.activate, help="Activate a pipeline conda environment.")

    def list(self):
        environments_dir_yellow = typer.style(
            self.pipeline.path / "envs", fg=typer.colors.YELLOW
        )
        typer.echo(
            f"Found {len(self.pipeline.environments)} environments in {environments_dir_yellow}"
        )
        for env in self.pipeline.environments:
            typer.echo(f'- {env.stem}')
    
    def _get_conda_env_path(self, name: str) -> Path:
        env = [e for e in self.pipeline.environments if e.stem == name]
        if not env:
            self.error(f"Environment {name} not found!")
        return env[0]

    def show(self, name: str = typer.Argument(..., help="The name of the environment.")):
        env_path = self._get_conda_env_path(name)
        # typer.echo(f"{env}", err=True)
        with open(env_path) as f:
            code = f.read()
            syntax = Syntax(code, "yaml")
            console = Console()
            console.print(syntax)

    def create(self, name: Optional[str] = typer.Argument(..., help="The name of the environment.")):
        raise NotImplementedError


    def run(
            self, 
            name: str = typer.Argument(..., help="The name of the environment."),
            cmd: str = typer.Argument(..., help="The command to run.")
        ):
        raise NotImplementedError


    def activate(self, name: str = typer.Argument(..., help="The name of the environment.")):
        raise NotImplementedError
    