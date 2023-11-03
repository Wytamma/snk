import os
import subprocess
from pathlib import Path
import sys
from typing import List
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.workflow import create_workflow
from snk.pipeline import Pipeline
from rich.console import Console
from rich.syntax import Syntax
from snakemake.deployment.conda import Conda, Env
from snk.cli.config.config import get_config_from_pipeline_dir


class ScriptApp(DynamicTyper):
    def __init__(
        self,
        pipeline: Pipeline,
        conda_prefix_dir: Path,
        snakemake_config,
        snakefile: Path,
    ):
        self.pipeline = pipeline
        self.conda_prefix_dir = conda_prefix_dir
        self.snakemake_config = snakemake_config
        self.snakefile = snakefile
        self.configfile = get_config_from_pipeline_dir(self.pipeline.path)
        self.register_default_command(self.list)
        self.register_command(self.list, help="List the scripts in the pipeline.")
        self.register_command(
            self.show, help="Show the script file contents."
        )
        self.register_command(
            self.run, 
            help="""
            Run a script from the pipeline.
            \n\nThe executor for the script is inferred from the suffix.
            \n\nExample: snk script run --env=python script.py""",
            context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
        )

    def list(self):
        scripts_dir_yellow = typer.style(
            self.pipeline.path / "scripts", fg=typer.colors.YELLOW
        )
        number_of_scripts = len(self.pipeline.scripts)  
        typer.echo(
            f"Found {number_of_scripts} script{'s' if number_of_scripts > 1 else ''} in {scripts_dir_yellow}"
        )
        for env in self.pipeline.scripts:
            typer.echo(f"- {env.stem} ({env.name})")

    def _get_script_path(self, name: str) -> Path:
        env = [e for e in self.pipeline.scripts if e.name == name or e.stem == name]
        if not env:
            self.error(f"Script {name} not found!")
        return env[0]

    def _get_conda_env_path(self, name: str) -> Path:
        env = [e for e in self.pipeline.environments if e.stem == name]
        if not env:
            self.error(f"Environment {name} not found!")
        return env[0]

    def _shellcmd(self, env_address: str, cmd: str) -> str:
        if sys.platform.lower().startswith("win"):
            return Conda().shellcmd_win(env_address, cmd)
        return Conda().shellcmd(env_address, cmd)

    def show(
        self, 
        name: str = typer.Argument(..., help="The name of the script."),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print the script."
        ),
    ):
        env_path = self._get_script_path(name)
        with open(env_path) as f:
            code = f.read()
            if pretty:
                code = Syntax(code, env_path.suffix[1:])
            console = Console()
            console.print(code)

    def _get_executor(self, suffix: str) -> str:
        if suffix == "py":
            return "python"
        elif suffix == "R":
            return "Rscript"
        elif suffix == "sh":
            return "bash"
        elif suffix == "pl":
            return "perl"
        elif suffix == "Rmd" or suffix == "rmd" or suffix == "Rhtml":
            return "Rscript -e 'rmarkdown::render(\"{script_path}\")'"
        elif suffix == "ipynb":
            return "jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 {script_path}"
        elif suffix == "Rnw":
            return "Rscript -e 'knitr::knit(\"{script_path}\")'"        
        else:
            self.error(f"Unknown script suffix: {suffix}!")

    def run(
        self,
        env: str = typer.Option(None, help="The name of the environment to run script in."),
        name: str = typer.Argument(..., help="The name of the script."),
        args: List[str] = typer.Argument(None, help="Arguments to pass to the script."),
    ):
        script_path = self._get_script_path(name)
        executor = self._get_executor(script_path.suffix[1:])
        cmd = [executor, str(script_path)] + args
        if env:
            env_path = self._get_conda_env_path(env)
            workflow = create_workflow(
                self.snakefile,
                config=self.snakemake_config,
                configfiles=[self.configfile] if self.configfile else None,
                use_conda=True,
                conda_prefix=self.conda_prefix_dir.resolve(),
            )
            env = Env(workflow, env_file=env_path.resolve())
            env.create()
            cmd = self._shellcmd(env.address, " ".join(cmd))
        else:
            cmd = " ".join(cmd)
        subprocess.run(cmd, shell=True, env=os.environ.copy())


