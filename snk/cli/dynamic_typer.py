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

    def register_subcommand(self, app: typer.Typer, **command_kwargs) -> None:
        """
        Register a subcommand to the CLI.
        Args:
          command (Callable): The subcommand to register.
        Side Effects:
          Registers the subcommand to the CLI.
        Examples:
          >>> CLI.register_subcommand(my_subcommand)
        """
        self.app.add_typer(app, **command_kwargs)
    
    def error(self, msg):
        typer.secho(msg, fg="red")
        raise typer.Exit(1)