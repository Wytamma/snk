import typer
from snk.cli.dynamic_typer import DynamicTyper
from snk.workflow import Workflow
from rich.console import Console
from rich.syntax import Syntax
from pathlib import Path


class ProfileApp(DynamicTyper):
    def __init__(
        self,
        workflow: Workflow,
    ):
        self.workflow = workflow
        self.register_command(self.list, help="List the profiles in the workflow.")
        self.register_command(
            self.show, help="Show the contents of a profile."
        )

    def list(
        self,
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show profiles as paths."), 
    ):
        from rich.console import Console
        from rich.table import Table
        table = Table("Name", "CMD", show_header=True, show_lines=True)
        if verbose:
            table.add_column("Path")
        for profile in self.workflow.profiles:
            if verbose:
                path = str(profile.resolve())
                table.add_row(profile.stem, f"{self.workflow.name} profile show {profile.stem}", path)
            else:
                table.add_row(profile.stem, f"{self.workflow.name} profile show {profile.stem}")
        console = Console()
        console.print(table)



    def _get_profile_path(self, name: str) -> Path:
        profile = [p for p in self.workflow.profiles if p.name == name or p.stem == name]
        if not profile:
            self.error(f"Profile {name} not found!")
        return profile[0] / "config.yaml"
    
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
