import os
import shutil
import subprocess
from pathlib import Path
import sys
from typing import List, Optional
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.workflow import create_workflow
from snk.pipeline import Pipeline
from rich.console import Console
from rich.syntax import Syntax
from snakemake.deployment.conda import Conda, Env, CreateCondaEnvironmentException
from snk.cli.config.config import get_config_from_pipeline_dir

class EnvApp(DynamicTyper):
    def __init__(self, pipeline: Pipeline, conda_prefix_dir: Path, snakemake_config, snakefile: Path):
        self.pipeline = pipeline
        self.conda_prefix_dir = conda_prefix_dir
        self.snakemake_config = snakemake_config
        self.snakefile = snakefile
        self.configfile = get_config_from_pipeline_dir(self.pipeline.path)
        self.workflow = create_workflow(
            self.snakefile,
            config=self.snakemake_config,
            configfiles=[self.configfile] if self.configfile else None,
            use_conda = True,
            conda_prefix=self.conda_prefix_dir.resolve(),
        )
        self.register_default_command(self.list)
        self.register_command(self.list, help="List the environments in the pipeline.")
        self.register_command(self.show, help="Show the environments config file contents.")
        self.register_command(self.run, help="Run a command in one of the pipeline environments.")
        self.register_command(self.activate, help="Activate a pipeline conda environment.")
        self.register_command(self.prune, help="Delete all conda environments.")
        self.register_command(self.create, help="Create all conda environments.")

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
    
    def _shellcmd(self, env_address: str, cmd: str) -> str:
        if sys.platform.lower().startswith("win"):
            return Conda().shellcmd_win(env_address, cmd)
        return Conda().shellcmd(env_address, cmd)

    def show(self, name: str = typer.Argument(..., help="The name of the environment.")):
        env_path = self._get_conda_env_path(name)
        with open(env_path) as f:
            code = f.read()
            syntax = Syntax(code, "yaml")
            console = Console()
            console.print(syntax)

    def run(
            self, 
            name: str = typer.Argument(..., help="The name of the environment."),
            cmd: List[str] = typer.Argument(..., help="The command to run in environment.")
        ):
        env_path = self._get_conda_env_path(name)
        env = Env(self.workflow, env_file=env_path.resolve())
        env.create()
        cmd = self._shellcmd(env.address, " ".join(cmd))
        subprocess.run(cmd, shell=True, env=os.environ.copy())

    def prune(self, force: bool = typer.Option(False, "--force", "-f", help="Force deletion of the environments.")):
        if force or input(f"Delete {self.conda_prefix_dir}? [y/N] ").lower() == "y":
            # delete self.conda_prefix_dir directory
            shutil.rmtree(self.conda_prefix_dir)
            self.log(f"Deleted {self.conda_prefix_dir}")
    
    def create(self):
        for env_path in self.pipeline.environments:
            env = Env(self.workflow, env_file=env_path.resolve())
            try:
                env.create()
            except CreateCondaEnvironmentException:
                self.error(f"Environment {env_path.name} could not be created!", exit=False)


    def activate(self, name: str = typer.Argument(..., help="The name of the environment.")):
        env_path = self._get_conda_env_path(name)
        self.log(f"Activating {name} environment... (type 'exit' to deactivate)")
        env = Env(self.workflow, env_file=env_path.resolve())
        env.create()
        user_shell = os.environ.get('SHELL', '/bin/sh')
        activate_cmd = self._shellcmd(env.address, user_shell)
        subprocess.run(activate_cmd, shell=True, env=os.environ.copy())
        self.log(f"Exiting {name} environment...")
        
    