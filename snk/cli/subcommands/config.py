from typing import List
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.options.option import Option
from snk.pipeline import Pipeline
from rich.console import Console
from rich.syntax import Syntax
from snk.cli.config.config import get_config_from_pipeline_dir

class ConfigApp(DynamicTyper):
    def __init__(self, pipeline: Pipeline, options: List[Option]):
        """
        Initializes the ConfigApp class.
        Args:
            pipeline (Pipeline): The pipeline to configure.
        """ 
        self.pipeline = pipeline
        self.register_default_command(self.show)
        self.register_command(self.show, help="Show the pipeline configuration.")

    def show(self, ctx: typer.Context, pretty: bool = typer.Option(False, "--pretty", "-p")):
        """
        Prints the configuration for the pipeline.
        Args:
            pretty (bool, optional): Whether to print the configuration in a pretty format. Defaults to False.
        Returns:
            None
        Examples:
            >>> ConfigApp.show(pretty=True)
            # Pretty printed configuration
        """
        config_path = get_config_from_pipeline_dir(self.pipeline.path)
        if not config_path:
            typer.secho("Could not find config...", fg="red")
            raise typer.Exit(1)
        with open(config_path) as f:
            code = f.read()
            if pretty:
                syntax = Syntax(code, "yaml")
                console = Console()
                console.print(syntax)
            else:
                typer.echo(code)
    