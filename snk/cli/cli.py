import inspect
import sys
import typer
from pathlib import Path
from typing import Optional, List, Callable
import subprocess
import shutil
import os
from contextlib import contextmanager

import snakemake
from rich.console import Console
from rich.syntax import Syntax
from art import text2art


from .config import (
    SnkConfig,
    get_config_from_pipeline_dir,
    load_pipeline_snakemake_config,
)
from .utils import add_dynamic_options, build_dynamic_cli_options, parse_config_args
from snk.pipeline import Pipeline


class CLI:
    """
    Constructor for the CLI class.
    Args:
      pipeline_dir_path (Path): Path to the pipeline directory.
    Side Effects:
      Initializes the CLI class.
    Examples:
      >>> CLI(Path('/path/to/pipeline'))
    """

    def __init__(self, pipeline_dir_path: Path = None) -> None:
        if not pipeline_dir_path:
            # get the calling frame (the frame of the function that called this function)
            calling_frame = inspect.currentframe().f_back
            # get the file path from the calling frame
            pipeline_dir_path = Path(calling_frame.f_globals['__file__'])
        if pipeline_dir_path.is_file():
            pipeline_dir_path = pipeline_dir_path.parent
        self.pipeline = Pipeline(path=pipeline_dir_path)
        self.app = typer.Typer()
        self.snakemake_config = load_pipeline_snakemake_config(pipeline_dir_path)
        self.snk_config: SnkConfig = SnkConfig.from_path(pipeline_dir_path / ".snk")
        self.options = build_dynamic_cli_options(self.snakemake_config, self.snk_config)
        self.snakefile = self._find_snakefile()
        self.conda_prefix_dir = pipeline_dir_path / ".conda"
        if " " in str(pipeline_dir_path):
            # cannot have spaces!
            self.singularity_prefix_dir = None
        else:
            self.singularity_prefix_dir = pipeline_dir_path / ".singularity"
        self.name = self.pipeline.name
        self.verbose = False

        def _print_pipline_version(ctx: typer.Context, value: bool):
            if value:
                typer.echo(self.pipeline.version)
                raise typer.Exit()

        def _print_pipline_path(ctx: typer.Context, value: bool):
            if value:
                typer.echo(self.pipeline.path)
                raise typer.Exit()

        def callback(
            ctx: typer.Context,
            version: Optional[bool] = typer.Option(
                None,
                "-v",
                "--version",
                help="Show the pipeline version.",
                is_eager=True,
                callback=_print_pipline_version,
                show_default=False,
            ),
            path: Optional[bool] = typer.Option(
                None,
                "-p",
                "--path",
                help="Show the pipeline path.",
                is_eager=True,
                callback=_print_pipline_path,
                show_default=False,
            ),
        ):
            if ctx.invoked_subcommand is None:
                typer.echo(f"{ctx.get_help()}")

        # dynamically create the logo
        callback.__doc__ = f"{self.create_logo()}"

        # registration
        self.register_callback(
            callback,
            invoke_without_command=True,
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        self.register_command(
            self.info, help="Display information about current pipeline install."
        )
        self.register_command(self.config, help="Access the pipeline configuration.")
        self.register_command(self.env, help="Access the pipeline conda environments.")
        self.register_command(self.profile, help="Access the pipeline profiles.")
        # self.register_command(self.script, help="Access the pipeline scripts.")
        self.register_command(
            add_dynamic_options(self.options)(self.run),
            help="Run the dynamically generated pipeline CLI.\n\nAll unrecognized arguments are passed onto Snakemake.",
            context_settings={
                "allow_extra_args": True,
                "ignore_unknown_options": True,
                "help_option_names": ["-h", "--help"],
            },
        )

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

    def create_logo(self, font="small"):
        """
        Create a logo for the CLI.
        Args:
          font (str): The font to use for the logo.
        Returns:
          str: The logo.
        Examples:
          >>> CLI.create_logo()
        """
        logo = text2art(self.name, font=font)
        doc = f"""\b{logo}\bA Snakemake pipeline CLI generated with snk"""
        return doc

    def _print_snakemake_help(value: bool):
        """
        Print the snakemake help and exit.
        Args:
          value (bool): If True, print the snakemake help and exit.
        Side Effects:
          Prints the snakemake help and exits.
        Examples:
          >>> CLI._print_snakemake_help(True)
        """
        if value:
            snakemake.main("-h")

    def _find_snakefile(self):
        """
        Search possible snakefile locations.
        Returns:
          Path: The path to the snakefile.
        Examples:
          >>> CLI._find_snakefile()
        """
        for path in snakemake.SNAKEFILE_CHOICES:
            if (self.pipeline.path / path).exists():
                return self.pipeline.path / path
        raise FileNotFoundError("Snakefile not found!")

    @contextmanager
    def copy_resources(self, resources: List[Path], cleanup: bool):
        """
        Copy resources to the current working directory.
        Args:
          resources (List[Path]): A list of paths to the resources to copy.
          cleanup (bool): If True, the resources will be removed after the function exits.
        Side Effects:
          Copies the resources to the current working directory.
        Returns:
          Generator: A generator object.
        Examples:
          >>> with CLI.copy_resources(resources, cleanup=True):
          ...     # do something
        """
        copied_resources = []

        def copy_resource(src, dst):
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

        def remove_resource(resource):
            if resource.is_dir():
                shutil.rmtree(resource)
            else:
                os.remove(resource)

        try:
            for resource in resources:
                abs_path = self.pipeline.path / resource
                destination = Path(".") / resource.name
                if not destination.exists():
                    # make sure you don't delete files that are already there...
                    copy_resource(abs_path, destination)
                    copied_resources.append(destination)
                else:
                    raise FileExistsError(f"Resource '{resource.name}' already exists!")

            yield
        finally:
            if not cleanup:
                return
            for copied_resource in copied_resources:
                if copied_resource.exists():
                    if self.verbose:
                        typer.secho(
                            f"Deleting '{resource.name}' resource...",
                            fg=typer.colors.YELLOW,
                        )
                    remove_resource(copied_resource)

    def run(
        self,
        ctx: typer.Context,
        target: str = typer.Argument(
            None, help="File to generate. If None will run the pipeline 'all' rule."
        ),
        configfile: Path = typer.Option(
            None,
            "--config",
            help="Path to snakemake config file. Overrides existing config and defaults.",
            exists=True,
            dir_okay=False,
        ),
        resource: List[Path] = typer.Option(
            [],
            "--resource",
            "-r",
            help="Additional resources to copy to workdir at run time (relative to pipeline directory).",
        ),
        profile: Optional[str] = typer.Option(
            None,
            "--profile",
            "-p",
            help="Name of profile to use for configuring Snakemake.",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            "-f",
            help="Force the execution of pipeline regardless of already created output.",
        ),
        lock: bool = typer.Option(
            False, "--lock", "-l", help="Lock the working directory."
        ),
        keep_resources: bool = typer.Option(
            False,
            "--keep-resources",
            "-R",
            help="Keep resources after pipeline completes.",
        ),
        keep_snakemake: bool = typer.Option(
            False,
            "--keep-snakemake",
            "-S",
            help="Keep .snakemake folder after pipeline completes.",
        ),
        cores: int = typer.Option(
            None,
            "--cores",
            "-c",
            help="Set the number of cores to use. If None will use all cores.",
        ),
        verbose: Optional[bool] = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Run pipeline in verbose mode.",
        ),
        help_snakemake: Optional[bool] = typer.Option(
            False,
            "--help-snakemake",
            "-hs",
            help="Print the snakemake help and exit.",
            is_eager=True,
            callback=_print_snakemake_help,
            show_default=False,
        ),
    ):
        """
        Run the pipeline.
        Args:
          target (str): File to generate. If None will run the pipeline 'all' rule.
          configfile (Path): Path to snakemake config file. Overrides existing config and defaults.
          resource (List[Path]): Additional resources to copy to workdir at run time.
          keep_resources (bool): Keep resources.
          cleanup_snakemake (bool): Keep .snakemake folder.
          cores (int): Set the number of cores to use. If None will use all cores.
          verbose (bool): Run pipeline in verbose mode.
          help_snakemake (bool): Print the snakemake help and exit.
        Side Effects:
          Runs the pipeline.
        Examples:
          >>> CLI.run(target='my_target', configfile=Path('/path/to/config.yaml'), resource=[Path('/path/to/resource')], verbose=True)
        """
        self.verbose = verbose
        args = []
        if not cores:
            cores = "all"
        args.extend(
            [
                "--use-conda",
                f"--conda-prefix={self.conda_prefix_dir}",
                f"--cores={cores}",
            ]
        )
        if self.singularity_prefix_dir:
            args.append(f"--singularity-prefix={self.singularity_prefix_dir}")
        if not self.snakefile.exists():
            raise ValueError("Could not find Snakefile")  # this should occur at install
        else:
            args.append(f"--snakefile={self.snakefile}")

        if not configfile:
            configfile = get_config_from_pipeline_dir(self.pipeline.path)
        args.append(f"--configfile={configfile}")

        if profile:
            found_profile = [p for p in self.pipeline.profiles if profile == p.name]
            if found_profile:
                profile = found_profile[0]
            args.append(f"--profile={profile}")

        # Set up conda frontend
        mamba_found = True
        try:
            subprocess.run(["mamba", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            typer.secho(
                "Mamba not found! Install for speed up.", fg=typer.colors.YELLOW
            )
            mamba_found = False
        if not mamba_found:
            args.append("--conda-frontend=conda")

        typer.echo(self.create_logo())
        typer.echo()

        if verbose:
            args.insert(0, "--verbose")

        if force:
            args.append("--forceall")

        if not lock:
            args.append("--nolock")

        if target:
            args.append(target)
        targets_and_or_snakemake, config_dict_list = parse_config_args(
            ctx.args, options=self.options
        )

        args.extend(targets_and_or_snakemake)

        configs = [
            f"{list(c.keys())[0]}={list(c.values())[0]}" for c in config_dict_list
        ]
        if configs:
            args.extend(["--config", *configs])
        if verbose:
            typer.secho(f"snakemake {' '.join(args)}\n", fg=typer.colors.MAGENTA)

        self.snk_config.add_resources(resource, self.pipeline.path)

        with self.copy_resources(self.snk_config.resources, cleanup=not keep_resources):
            try:
                snakemake.main(args)
            except SystemExit as e:
                status = int(str(e))
                if status:
                    sys.exit(status)
        if not keep_snakemake and Path(".snakemake").exists():
            if verbose:
                typer.secho("Deleting '.snakemake' folder...", fg="yellow")
            shutil.rmtree(".snakemake")

    def info(self):
        """
        Display information about current pipeline install.
        Returns:
          str: A JSON string containing information about the current pipeline install.
        Examples:
          >>> CLI.info()
        """
        import json

        info_dict = {}
        info_dict["name"] = self.pipeline.path.name
        info_dict["version"] = self.pipeline.version
        info_dict["pipeline_dir_path"] = str(self.pipeline.path)
        typer.echo(json.dumps(info_dict, indent=2))

    def config(self):
        """
        Access the pipeline configuration.
        Side Effects:
          Prints the pipeline configuration.
        Examples:
          >>> CLI.config()
        """
        config_path = get_config_from_pipeline_dir(self.pipeline.path)
        if not config_path:
            typer.secho("Could not find config...", fg="red")
            raise typer.Exit(1)
        with open(config_path) as f:
            code = f.read()
            syntax = Syntax(code, "yaml")
            console = Console()
            console.print(syntax)

    def env(
        self,
        name: str = typer.Argument(None, help="The name of the environment."),
    ):
        """
        Access the pipeline conda environments.
        Args:
          name (str): The name of the environment.
        Examples:
          >>> CLI.env(name='my_env')
        """
        environments_dir_yellow = typer.style(
            self.pipeline.path / "envs", fg=typer.colors.YELLOW
        )
        typer.echo(
            f"Found {len(self.pipeline.environments)} environments in {environments_dir_yellow}"
        )
        for env in self.pipeline.environments:
            typer.echo(f"- {env}")

    def profile(
        self,
        name: str = typer.Argument(None, help="The name of the profile."),
    ):
        profiles_dir_yellow = typer.style(
            self.pipeline.path / "profiles", fg=typer.colors.YELLOW
        )
        typer.echo(
            f"Found {len(self.pipeline.profiles)} profiles in {profiles_dir_yellow}"
        )
        for profile in self.pipeline.profiles:
            typer.echo(f"- {profile.name}")

    # def script(
    #     self,
    #     name: Optional[str] = typer.Argument(None)
    # ):
    #     """
    #     Access the pipeline scripts.
    #     Args:
    #       name (str): The name of the script.
    #     Examples:
    #       >>> CLI.script(name='my_script')
    #     """
    #     raise NotImplementedError
