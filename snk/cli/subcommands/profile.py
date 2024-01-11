import typer
from snk.cli.dynamic_typer import DynamicTyper
from snk.pipeline import Pipeline
from rich.console import Console
from rich.syntax import Syntax
from pathlib import Path


class ProfileApp(DynamicTyper):
    def __init__(
        self,
        pipeline: Pipeline,
    ):
        self.pipeline = pipeline
        self.register_command(self.list, help="List the profiles in the pipeline.")
        self.register_command(
            self.show, help="Show the contents of a profile."
        )

    def list(
        self,
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show profiles as paths."), 
    ):
        number_of_profiles = len(self.pipeline.profiles)
        typer.echo(
            f"Found {number_of_profiles} profile{'' if number_of_profiles == 1 else 's'}:"
        )
        for profile in self.pipeline.profiles:
            if verbose:
                typer.echo(f"- {typer.style(profile, fg=typer.colors.YELLOW)}")
            else:
                typer.echo(f"- {profile.stem}")
    
    def _get_profile_path(self, name: str) -> Path:
        profile = [e for e in self.pipeline.profiles if e.name == name or e.stem == name]
        if not profile:
            self.error(f"Profile {name} not found!")
        return profile[0]
    
    def show(
        self, 
        name: str = typer.Argument(..., help="The name of the profile."),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print the profile."
        ),
    ):
        profile_path = self._get_profile_path(name)
        profile_file_text = profile_path.read_text()
        if pretty:
            syntax = Syntax(profile_file_text, "yaml")
            console = Console()
            console.print(syntax)
        else:
            typer.echo(profile_file_text)
