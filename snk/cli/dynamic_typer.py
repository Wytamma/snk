from typing import Callable
import typer
from typing import List, Callable
from inspect import signature, Parameter
from makefun import with_signature
import typer

from snk.cli.options import Option


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

    def register_command(self, command: Callable, dynamic_options=None, **command_kwargs) -> None:
        """
        Register a command to the CLI.
        Args:
          command (Callable): The command to register.
        Side Effects:
          Registers the command to the CLI.
        Examples:
          >>> CLI.register_command(my_command)
        """
        if dynamic_options is not None:
            command = self.add_dynamic_options(command, dynamic_options)
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


    def _create_cli_parameter(self, option: Option):
        """
        Creates a parameter for a CLI option.
        Args:
          option (Option): An Option object containing the option's name, type, required status, default value, and help message.
        Returns:
          Parameter: A parameter object for the CLI option.
        Examples:
          >>> option = Option(name='foo', type='int', required=True, default=0, help='A number')
          >>> create_cli_parameter(option)
          Parameter('foo', kind=Parameter.POSITIONAL_OR_KEYWORD, default=typer.Option(..., help='[CONFIG] A number'), annotation=int)
        """        
        return Parameter(
            option.name,
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            default=typer.Option(
                ... if option.required else option.default,
                help=f"[CONFIG] {option.help}",
            ),
            annotation=option.type,
        )


    def add_dynamic_options(self, func: Callable, options: List[Option]):
        """
        Function to add dynamic options to a command.
        Args:
          command (Callable): The command to which the dynamic options should be added.
          options (List[dict]): A list of dictionaries containing the option's name, type, required status, default value, and help message.
        Returns:
          Callable: A function with the dynamic options added.
        Examples:
          >>> my_func = add_dynamic_options_to_function(my_func, [{'name': 'foo', 'type': 'int', 'required': True, 'default': 0, 'help': 'A number'}])
          >>> my_func
          <function my_func at 0x7f8f9f9f9f90>
        """
        func_sig = signature(func)
        params = list(func_sig.parameters.values())
        for op in options[::-1]:
            params.insert(1, self._create_cli_parameter(op))
        new_sig = func_sig.replace(parameters=params)

        @with_signature(func_signature=new_sig, func_name=func.__name__)
        def func_wrapper(*args, **kwargs):
            """
            Wraps a function with dynamic options.
            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.
            Returns:
                Callable: A wrapped function with the dynamic options added.
            Notes:
                This function is used in the `add_dynamic_options_to_function` function.
            """
            flat_config = None

            if kwargs.get("configfile"):
                import snakemake
                from .utils import flatten

                snakemake_config = snakemake.load_configfile(kwargs['configfile'])
                flat_config = flatten(snakemake_config)

            for option in options:
                # If no config file provided, or an option is updated, add it to the arguments
                if kwargs.get("configfile") is None or kwargs[option.name] != option.default:
                    kwargs["ctx"].args.extend([f"--{option.name}", kwargs[option.name]])
                # If a config file is provided and the option key isn't in it, add the option to the arguments
                elif flat_config and option.original_key not in flat_config:
                    kwargs["ctx"].args.extend([f"--{option.name}", kwargs[option.name]])

            kwargs = {
                k: v for k, v in kwargs.items() if k in func_sig.parameters.keys()
            }
            return func(*args, **kwargs)

        return func_wrapper


    def error(self, msg, exit=True):
        typer.secho(msg, fg="red")
        if exit:
          raise typer.Exit(1)
    
    def log(self, msg):
        typer.secho(msg, fg="yellow")