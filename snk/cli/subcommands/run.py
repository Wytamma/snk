from typing import List, Optional
from pathlib import Path
import typer
from contextlib import contextmanager

from snk.cli.dynamic_typer import DynamicTyper
from snk.cli.options.option import Option
from snk.workflow import Workflow
from snk.cli.utils import (
    parse_config_args,
    dag_filetype_callback,
    check_command_available
)

from snk.cli.config.config import (
    SnkConfig,
    get_config_from_workflow_dir,
)


class RunApp(DynamicTyper):
    def __init__(
        self,
        conda_prefix_dir: Path,
        snk_config: SnkConfig,
        singularity_prefix_dir: Path,
        snakefile: Path,
        workflow: Workflow,
        logo: str,
        verbose: bool,
        dynamic_run_options: List[Option],
    ):
        self.conda_prefix_dir = conda_prefix_dir
        self.singularity_prefix_dir = singularity_prefix_dir
        self.snk_config = snk_config
        self.snakefile = snakefile
        self.workflow = workflow
        self.verbose = verbose
        self.logo = logo
        self.options = dynamic_run_options

        self.register_command(
            self.run,
            dynamic_options=self.options,
            help="Run the workflow.\n\nAll unrecognized arguments are passed onto Snakemake.",
            context_settings={
                "allow_extra_args": True,
                "ignore_unknown_options": True,
                "help_option_names": ["-h", "--help"],
            },
        )

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
            import snakemake

            snakemake.main("-h")

    def run(
        self,
        ctx: typer.Context,
        configfile: Path = typer.Option(
            None,
            "--config",
            help="Path to snakemake config file. Overrides existing workflow configuration.",
            exists=True,
            dir_okay=False,
        ),
        resource: List[Path] = typer.Option(
            [],
            "--resource",
            "-r",
            help="Additional resources to copy from workflow directory at run time.",
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
            help="Force the execution of workflow regardless of already created output.",
        ),
        dry: bool = typer.Option(
            False,
            "--dry",
            "-n",
            help="Do not execute anything, and display what would be done.",
        ),
        lock: bool = typer.Option(
            False, "--lock", "-l", help="Lock the working directory."
        ),
        dag: Optional[Path] = typer.Option(
            None,
            "--dag",
            "-d",
            help="Save directed acyclic graph to file. Must end in .pdf, .png or .svg",
            callback=dag_filetype_callback,
        ),
        cores: int = typer.Option(
            None,
            "--cores",
            "-c",
            help="Set the number of cores to use. If None will use all cores.",
        ),
        no_conda: bool = typer.Option(
            False,
            "--no-conda",
            help="Do not use conda environments.",
        ),
        keep_resources: bool = typer.Option(
            False,
            "--keep-resources",
            help="Keep resources after pipeline completes.",
        ),
        keep_snakemake: bool = typer.Option(
            False,
            "--keep-snakemake",
            help="Keep .snakemake folder after pipeline completes.",
        ),
        verbose: Optional[bool] = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Run workflow in verbose mode.",
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
        Run the workflow.
        Args:
          configfile (Path): Path to snakemake config file. Overrides existing config and defaults.
          resource (List[Path]): Additional resources to copy to workdir at run time.
          keep_resources (bool): Keep resources.
          cleanup_snakemake (bool): Keep .snakemake folder.
          cores (int): Set the number of cores to use. If None will use all cores.
          verbose (bool): Run workflow in verbose mode.
          help_snakemake (bool): Print the snakemake help and exit.
        Side Effects:
          Runs the workflow.
        Examples:
          >>> CLI.run(target='my_target', configfile=Path('/path/to/config.yaml'), resource=[Path('/path/to/resource')], verbose=True)
        """
        import snakemake
        import shutil
        import sys

        self.verbose = verbose
        args = []
        if self.snk_config.additional_snakemake_args:
            if verbose:
                self.log(
                    f"Using additional snakemake args: {' '.join(self.snk_config.additional_snakemake_args)}",
                    color=typer.colors.MAGENTA
                )
            args.extend(self.snk_config.additional_snakemake_args)
        if not cores:
            cores = "all"
        args.extend(
            [
                "--rerun-incomplete",
                f"--cores={cores}",
            ]
        )
        if self.singularity_prefix_dir and "--use-singularity" in ctx.args:
            # only set prefix if --use-singularity is explicitly called
            args.append(f"--singularity-prefix={self.singularity_prefix_dir}")
            if verbose:
                self.log(f"Using singularity prefix: {self.singularity_prefix_dir}", color=typer.colors.MAGENTA)
        if not self.snakefile.exists():
            raise ValueError("Could not find Snakefile")  # this should occur at install
        else:
            args.append(f"--snakefile={self.snakefile}")

        if not configfile:
            configfile = get_config_from_workflow_dir(self.workflow.path)
        if configfile:
            args.append(f"--configfile={configfile}")

        if profile:
            found_profile = [p for p in self.workflow.profiles if profile == p.name]
            if found_profile:
                profile = found_profile[0]
            args.append(f"--profile={profile}")

        # Set up conda frontend
        conda_found = check_command_available("conda")
        if not conda_found and verbose:
            typer.secho(
                "Conda not found! Install conda to use environments.\n",
                fg=typer.colors.MAGENTA,
                err=True,
            )

        if conda_found and self.snk_config.conda and not no_conda:
            args.extend(
                [
                    "--use-conda",
                    f"--conda-prefix={self.conda_prefix_dir}",
                ]
            )
            if not check_command_available("mamba"):
                if verbose:
                    typer.secho(
                        "Could not find mamba, using conda instead...",
                        fg=typer.colors.MAGENTA,
                        err=True,
                    )
                args.append("--conda-frontend=conda")
            else:
                args.append("--conda-frontend=mamba")

        if verbose:
            args.insert(0, "--verbose")

        if force:
            args.append("--forceall")

        if dry:
            args.append("--dryrun")

        if not lock:
            args.append("--nolock")

        targets_and_or_snakemake, config_dict_list = parse_config_args(
            ctx.args, options=self.options
        )
        targets_and_or_snakemake = [
            t.replace("--snake-", "-") for t in targets_and_or_snakemake
        ]
        args.extend(targets_and_or_snakemake)
        configs = []
        for config_dict in config_dict_list:
            for key, value in config_dict.items():
                configs.append(f"{key}={value}")

        if configs:
            args.extend(["--config", *configs])
        if verbose:
            typer.secho(f"snakemake {' '.join(args)}\n", fg=typer.colors.MAGENTA, err=True)
        if not keep_snakemake and Path(".snakemake").exists():
            keep_snakemake = True
        try:
            self.snk_config.add_resources(resource, self.workflow.path)
        except FileNotFoundError as e:
            self.error(str(e))
        with self._copy_resources(
            self.snk_config.resources,
            cleanup=not keep_resources,
            symlink_resources=self.snk_config.symlink_resources,
        ):
            if dag:
                return self._save_dag(snakemake_args=args, filename=dag)
            try:
                snakemake.parse_config = parse_config_monkeypatch
                snakemake.main(args)
            except SystemExit as e:
                status = int(str(e))
                if status:
                    sys.exit(status)
        if not keep_snakemake and Path(".snakemake").exists():
            if verbose:
                typer.secho("Deleting '.snakemake' folder...", fg=typer.colors.MAGENTA, err=True)
            shutil.rmtree(".snakemake")

    def _save_dag(self, snakemake_args: List[str], filename: Path):
        from contextlib import redirect_stdout
        import snakemake
        import subprocess
        import io

        snakemake_args.append("--dag")

        fileType = filename.suffix.lstrip(".")

        # Create a file-like object to redirect the stdout
        snakemake_output = io.StringIO()
        # Use redirect_stdout to redirect stdout to the file-like object
        with redirect_stdout(snakemake_output):
            # Capture the output of snakemake.main(args) using a try-except block
            try:
                snakemake.parse_config = parse_config_monkeypatch
                snakemake.main(snakemake_args)
            except SystemExit:  # Catch SystemExit exception to prevent termination
                pass
        try:
            snakemake_output = snakemake_output.getvalue()
            if "snakemake_dag" not in snakemake_output:
                self.error("Could not generate dag!", exit=True)
            # discard everything before digraph snakemake_dag
            filtered_lines = (
                "digraph snakemake_dag" + snakemake_output.split("snakemake_dag")[1]
            )
            echo_process = subprocess.Popen(
                ["echo", filtered_lines], stdout=subprocess.PIPE
            )
            dot_process = subprocess.Popen(
                ["dot", f"-T{fileType}"],
                stdin=echo_process.stdout,
                stdout=subprocess.PIPE,
            )
            with open(filename, "w") as output_file:
                if self.verbose:
                    typer.secho(f"Saving dag to {filename}", fg=typer.colors.MAGENTA, err=True)
                subprocess.run(["cat"], stdin=dot_process.stdout, stdout=output_file)
        except (subprocess.CalledProcessError, FileNotFoundError):
            typer.echo("dot command not found!", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    @contextmanager
    def _copy_resources(
        self, resources: List[Path], cleanup: bool, symlink_resources: bool = False
    ):
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
        import os
        import shutil

        copied_resources = []

        def copy_resource(src: Path, dst: Path, symlink: bool = False):
            if self.verbose:
                typer.secho(
                    f"  - Copying resource '{src}' to '{dst}'",
                    fg=typer.colors.MAGENTA,
                    err=True,
                )
            target_is_directory = src.is_dir()
            if symlink:
                os.symlink(src, dst, target_is_directory=target_is_directory)
            elif target_is_directory:
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

        def remove_resource(resource: Path):
            if resource.is_symlink():
                resource.unlink()
            elif resource.is_dir():
                shutil.rmtree(resource)
            else:
                os.remove(resource)

        resources_folder = self.workflow.path / "resources"
        if resources_folder.exists():
            resources.insert(0, Path("resources"))
        if self.verbose and resources:
            typer.secho(
                f"Copying {len(resources)} resources to working directory...",
                fg=typer.colors.MAGENTA,
                err=True,
            )
        try:
            for resource in resources:
                abs_path = self.workflow.path / resource
                destination = Path(".") / resource.name
                if not destination.exists():
                    # make sure you don't delete files that are already there...
                    copy_resource(abs_path, destination, symlink=symlink_resources)
                    copied_resources.append(destination)
                elif self.verbose:
                    typer.secho(
                        f"  - Resource '{resource.name}' already exists! Skipping...",
                        fg=typer.colors.MAGENTA,
                        err=True,
                    )
            yield
        finally:
            if not cleanup:
                return
            for copied_resource in copied_resources:
                if copied_resource.exists():
                    if self.verbose:
                        typer.secho(
                            f"Deleting '{copied_resource.name}' resource...",
                            fg=typer.colors.MAGENTA,
                            err=True,
                        )
                    remove_resource(copied_resource)


def parse_config_monkeypatch(args):
    """Monkeypatch the parse_config function from snakemake."""
    import yaml
    import snakemake
    import re

    class NoDatesSafeLoader(yaml.SafeLoader):
        @classmethod
        def remove_implicit_resolver(cls, tag_to_remove):
            """
            Remove implicit resolvers for a particular tag

            Takes care not to modify resolvers in super classes.

            We want to load datetimes as strings, not dates, because we
            go on to serialise as json which doesn't have the advanced types
            of yaml, and leads to incompatibilities down the track.
            """
            if "yaml_implicit_resolvers" not in cls.__dict__:
                cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()

            for first_letter, mappings in cls.yaml_implicit_resolvers.items():
                cls.yaml_implicit_resolvers[first_letter] = [
                    (tag, regexp) for tag, regexp in mappings if tag != tag_to_remove
                ]

    NoDatesSafeLoader.remove_implicit_resolver("tag:yaml.org,2002:timestamp")

    def _yaml_safe_load(s):
        """Load yaml string safely."""
        s = s.replace(": None", ": null")
        return yaml.load(s, Loader=NoDatesSafeLoader)

    parsers = [int, float, snakemake._bool_parser, _yaml_safe_load, str]
    config = dict()
    if args.config is not None:
        valid = re.compile(r"[a-zA-Z_]\w*$")
        for entry in args.config:
            key, val = snakemake.parse_key_value_arg(
                entry,
                errmsg="Invalid config definition: Config entries have to be defined as name=value pairs.",
            )
            if not valid.match(key):
                raise ValueError(
                    "Invalid config definition: Config entry must start with a valid identifier."
                )
            v = None
            if val == "" or val == "None":
                snakemake.update_config(config, {key: v})
                continue
            for parser in parsers:
                try:
                    v = parser(val)
                    # avoid accidental interpretation as function
                    if not callable(v):
                        break
                except:
                    pass
            assert v is not None
            snakemake.update_config(config, {key: v})
    return config
