import os
import subprocess
from pathlib import Path
import sys
from typing import List
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.snakemake_workflow import create_snakemake_workflow
from snk.workflow import Workflow
from rich.console import Console
from rich.syntax import Syntax
from snakemake.deployment.conda import Conda, Env
from snk.cli.config.config import get_config_from_workflow_dir


class ScriptApp(DynamicTyper):
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
        self.register_command(self.list, help="List the scripts in the workflow.")
        self.register_command(
            self.show, help="Show the contents of a script."
        )
        self.register_command(
            self.run, 
            help=f"""
            Run a script from the workflow.
            \n\nThe executor for the script is inferred from the suffix.
            \n\nExample: {self.workflow.name} script run --env=python script.py
            \n\nTo pass help to the script, use `-- --help`.""",
            context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
        )

    def list(
            self, 
            verbose: bool = typer.Option(False, "--verbose", "-v", help="Show script as paths."), 
        ):
        from rich.console import Console
        from rich.table import Table
        table = Table("Name", "CMD", "File", show_header=True, show_lines=True)
        for script in self.workflow.scripts:
            # address relative to cwd
            table.add_row(script.stem, f"{self.workflow.name} script show {script.stem}", str(script.resolve()) if verbose else script.name)
        console = Console()
        console.print(table)

    def _get_script_path(self, name: str) -> Path:
        script = [e for e in self.workflow.scripts if e.name == name or e.stem == name]
        if not script:
            self.error(f"Script {name} not found!")
        return script[0]

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
        name: str = typer.Argument(..., help="The name of the script."),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print the script."
        ),
    ):
        script_path = self._get_script_path(name)
        code = script_path.read_text()
        if pretty:
            code = Syntax(code, script_path.suffix[1:])
            console = Console()
            console.print(code)
        else:
            typer.echo(code)

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
        cmd = [executor, f'"{script_path}"'] + args
        if env:
            env_path = self._get_conda_env_path(env)
            workflow = create_snakemake_workflow(
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
        user_shell = os.environ.get("SHELL", "/bin/bash")
        subprocess.run(cmd, shell=True, env=os.environ.copy(), executable=user_shell)


