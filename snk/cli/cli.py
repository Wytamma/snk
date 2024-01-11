import inspect
import platform

import typer
from pathlib import Path
from typing import Optional
import os


from snakemake import SNAKEFILE_CHOICES
from art import text2art

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.subcommands import EnvApp, ConfigApp, RunApp, ScriptApp, ProfileApp

from .config.config import (
    SnkConfig,
    load_pipeline_snakemake_config,
)
from .options.utils import build_dynamic_cli_options
from snk.pipeline import Pipeline


class CLI(DynamicTyper):
    """
    Constructor for the dynamic Snk CLI class.
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
            pipeline_dir_path = Path(calling_frame.f_globals["__file__"])
        if pipeline_dir_path.is_file():
            pipeline_dir_path = pipeline_dir_path.parent
        self.pipeline = Pipeline(path=pipeline_dir_path)
        self.snakemake_config = load_pipeline_snakemake_config(pipeline_dir_path)
        self.snk_config = SnkConfig.from_pipeline_dir(
            pipeline_dir_path, create_if_not_exists=True
        )
        if self.snk_config.version:
            self.version = self.snk_config.version
        else: 
            if self.pipeline.tag:
               self.version = self.pipeline.tag
            else:
                self.version = self.pipeline.commit
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
        if (
            platform.system() == "Darwin"
            and platform.processor() == "arm"
            and not os.environ.get("CONDA_SUBDIR")
        ):
            os.environ["CONDA_SUBDIR"] = "osx-64"

        # dynamically create the logo
        self.logo = self._create_logo(
            tagline=self.snk_config.tagline, font=self.snk_config.font
        )
        callback = self._create_callback()
        callback.__doc__ = self.logo

        # registration
        self.register_callback(
            callback,
            invoke_without_command=True,
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        self.register_command(self.info, help="Show information about the pipeline.")

        run_app = RunApp(
            conda_prefix_dir=self.conda_prefix_dir,
            snk_config=self.snk_config,
            singularity_prefix_dir=self.singularity_prefix_dir,
            snakefile=self.snakefile,
            pipeline=self.pipeline,
            verbose=self.verbose,
            logo=self.logo,
            dynamic_run_options=self.options,
        )
        # Subcommands
        self.register_command(
            run_app,
            name="run",
        )
        self.register_command(
            ConfigApp(
                pipeline=self.pipeline,
                options=self.options,
            ),
            name="config",
        )
        if self.pipeline.environments:
            self.register_group(
                EnvApp(
                    pipeline=self.pipeline,
                    conda_prefix_dir=self.conda_prefix_dir,
                    snakemake_config=self.snakemake_config,
                    snakefile=self.snakefile,
                ),
                name="env",
                help="Access the pipeline conda environments.",
            )
        if self.pipeline.scripts:
            self.register_group(
                ScriptApp(
                    pipeline=self.pipeline,
                    conda_prefix_dir=self.conda_prefix_dir,
                    snakemake_config=self.snakemake_config,
                    snakefile=self.snakefile,
                ),
                name="script",
                help="Access the pipeline scripts.",
            )
        if self.pipeline.profiles:
            self.register_group(
                ProfileApp(
                    pipeline=self.pipeline,
                ),
                name="profile",
                help="Access the pipeline profiles.",
            )

    def _print_pipline_version(self, ctx: typer.Context, value: bool):
        if value:
            typer.echo(self.version)
            raise typer.Exit()

    def _print_pipline_path(self, ctx: typer.Context, value: bool):
        if value:
            typer.echo(self.pipeline.path)
            raise typer.Exit()

    def _create_callback(self):
        def callback(
            ctx: typer.Context,
            version: Optional[bool] = typer.Option(
                None,
                "-v",
                "--version",
                help="Show the pipeline version and exit.",
                is_eager=True,
                callback=self._print_pipline_version,
                show_default=False,
            ),
            path: Optional[bool] = typer.Option(
                None,
                "-p",
                "--path",
                help="Show the pipeline path and exit.",
                is_eager=True,
                callback=self._print_pipline_path,
                show_default=False,
            ),
        ):
            if ctx.invoked_subcommand is None:
                typer.echo(f"{ctx.get_help()}")

        return callback

    def _create_logo(
        self, tagline="A Snakemake pipeline CLI generated with snk", font="small"
    ):
        """
        Create a logo for the CLI.
        Args:
          font (str): The font to use for the logo.
        Returns:
          str: The logo.
        Examples:
          >>> CLI._create_logo()
        """
        if self.snk_config.art:
            art = self.snk_config.art
        else:
            logo = self.snk_config.logo if self.snk_config.logo else self.name
            art = text2art(logo, font=font)
        doc = f"""\b{art}\b{tagline}"""
        return doc

    def _find_snakefile(self):
        """
        Search possible snakefile locations.
        Returns:
          Path: The path to the snakefile.
        Examples:
          >>> CLI._find_snakefile()
        """
        for path in SNAKEFILE_CHOICES:
            if (self.pipeline.path / path).exists():
                return self.pipeline.path / path
        raise FileNotFoundError("Snakefile not found!")

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
        info_dict["version"] = self.version
        info_dict["pipeline_dir_path"] = str(self.pipeline.path)
        typer.echo(json.dumps(info_dict, indent=2))

