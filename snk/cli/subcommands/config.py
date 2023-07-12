from typing import List
import typer

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.options.option import Option
from snk.pipeline import Pipeline


class ConfigApp(DynamicTyper):
    def __init__(self, pipeline: Pipeline, options: List[Option]):
        """
        Initializes the ConfigApp class.
        Args:
            pipeline (Pipeline): The pipeline to configure.
        """ 
        self.options = options
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
        import yaml 
        from collections import defaultdict
        from rich.console import Console
        from rich.syntax import Syntax
        from snk.cli.utils import convert_key_to_snakemake_format
        
        def deep_update(source, overrides):
            for key, value in overrides.items():
                if isinstance(value, dict):
                    if not isinstance(source.get(key), dict):
                        # If the existing value is not a dictionary, replace it with one
                        source[key] = {}
                    # Now we are sure that source[key] is a dictionary, so we can update it
                    deep_update(source[key], value)
                else:
                    source[key] = value
            return source

        collapsed_data = defaultdict(dict)
        config_dict = [convert_key_to_snakemake_format(option.original_key, option.default) for option in self.options]
        for d in config_dict:
            deep_update(collapsed_data, d)
        yaml_str = yaml.dump(dict(collapsed_data))
        if pretty:
            syntax = Syntax(yaml_str, "yaml")
            console = Console()
            console.print(syntax)
        else:
            typer.echo(yaml_str)
