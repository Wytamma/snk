from typing import Callable
import typer

class DynamicTyper:
    app: typer.Typer

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.app = typer.Typer()

    def __call__(self):
        """
        Invoke the CLI.
        Side Effects:
          Invokes the CLI.
        Examples:
          >>> CLI(Path('/path/to/pipeline'))()
        """
        self.app()

    def register_default_command(self, command: Callable, **command_kwargs) -> None:
        """
        Register a default command to the CLI.
        Args:
          command (Callable): The command to register.
        Side Effects:
          Registers the command to the CLI.
        Examples:
          >>> CLI.register_default_command(my_command)
        """
        from makefun import with_signature
        from inspect import signature, Parameter

        command_signature = signature(command)
        params = list(command_signature.parameters.values())
        has_ctx = any([p.name == 'ctx' for p in params])
        if not has_ctx:
            params.insert(0, Parameter(
                'ctx', 
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=typer.Context
              )
            )
            command_signature = command_signature.replace(parameters=params)

        @with_signature(command_signature)
        def wrapper(ctx: typer.Context, *args, **kwargs):
            if ctx.invoked_subcommand is None:
                if has_ctx:
                    return command(ctx, *args, **kwargs)
                return command(*args, **kwargs)
  
        self.register_callback(wrapper, invoke_without_command=True, **command_kwargs)

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