from typing import Callable
import typer

class DynamicTyper:
    app: typer.Typer

    def __call__(self):
        """
        Invoke the CLI.
        Side Effects:
          Invokes the CLI.
        Examples:
          >>> CLI(Path('/path/to/pipeline'))()
        """
        self.app()

    def register_command(self, command: Callable, **command_kwargs) -> None:
        """
        Register a command to the CLI.
        Args:
          command (Callable): The command to register.
        Side Effects:
          Registers the command to the CLI.
        Examples:
          >>> CLI.register_command(my_command)
        """
        self.app.command(**command_kwargs)(command)

    def register_callback(self, command: Callable, **command_kwargs) -> None:
        """
        Register a callback to the CLI.
        Args:
          command (Callable): The callback to register.
        Side Effects:
          Registers the callback to the CLI.
        Examples:
          >>> CLI.register_callback(my_callback)
        """
        self.app.callback(**command_kwargs)(command)

    def register_group(self, group: "DynamicTyper", **command_kwargs) -> None:
        """
        Register a subcommand group group to the CLI.
        Args:
          group (DynamicTyper): The subcommand group to register.
        Side Effects:
          Registers the subcommand group to the CLI.
        Examples:
          >>> CLI.register_app(my_group)
        """
        self.app.add_typer(group.app, **command_kwargs)
    
    def error(self, msg, exit=True):
        typer.secho(msg, fg="red")
        if exit:
          raise typer.Exit(1)
    
    def log(self, msg):
        typer.secho(msg, fg="yellow")