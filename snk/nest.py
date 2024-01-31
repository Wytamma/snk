from pathlib import Path
from git import InvalidGitRepositoryError, Repo, GitCommandError
import sys
import stat
import inspect
import os
from typing import List
import shutil

from .errors import (
    WorkflowExistsError,
    WorkflowNotFoundError,
    InvalidWorkflowRepositoryError,
    InvalidWorkflowError
)
from .cli.config.config import SnkConfig
from .workflow import Workflow


class Nest:
    """
    Initializes a Nest object.
    Args:
      snk_home (Path, optional): The path to the SNK home directory. Defaults to None.
      bin_dir (Path, optional): The path to the bin directory. Defaults to None.
    Side Effects:
      Creates the SNK home and bin directories if they do not exist.
    Examples:
      >>> nest = Nest()
    """

    def __init__(self, snk_home: Path = None, bin_dir: Path = None) -> None:
        """
        Initializes a Nest object.
        Args:
          snk_home (Path, optional): The path to the SNK home directory. Defaults to None.
          bin_dir (Path, optional): The path to the bin directory. Defaults to None.
        Side Effects:
          Creates the SNK home and bin directories if they do not exist.
        Examples:
          >>> nest = Nest()
        """
        self.python_interpreter_path = Path(
            sys.executable
        )  # needs to be the same python that has snk

        if not snk_home:
            home_path = self.python_interpreter_path.parent.parent
            if not os.access(home_path, os.W_OK):
                user_home_path = Path("~").expanduser()
                snk_home = user_home_path / ".local" / "snk"
            else:
                snk_home = home_path / "snk"

        if not bin_dir:
            bin_dir = self.python_interpreter_path.parent
            if not os.access(bin_dir, os.W_OK):
                user_home_path = Path("~").expanduser()
                bin_dir = user_home_path / ".local" / "bin"

        self.bin_dir = Path(bin_dir).absolute()
        self.snk_home = Path(snk_home).absolute()
        self.snk_workflows_dir = self.snk_home / "workflows"
        self.snk_executable_dir = self.snk_home / "bin"

        # Create dirs
        self.snk_home.mkdir(parents=True, exist_ok=True)
        self.snk_workflows_dir.mkdir(parents=True, exist_ok=True)
        self.snk_executable_dir.mkdir(parents=True, exist_ok=True)
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def bin_dir_in_path(self) -> bool:
        path_dirs = os.environ["PATH"].split(os.pathsep)
        return str(self.bin_dir) in path_dirs

    def _format_repo_url(self, repo: str):
        """
        Checks that the given repo URL is valid.
        Args:
          repo (str): The URL of the repo.
        Raises:
          InvalidWorkflowRepositoryError: If the repo URL is not valid.
        Examples:
          >>> nest._check_repo_url_format('https://github.com/example/repo.git')
        """
        if not repo.endswith(".git"):
            repo += ".git"
        if not repo.startswith("http"):
            raise InvalidWorkflowRepositoryError("Repo url must start with http")
        return repo

    def install(
        self,
        workflow: str,
        editable=False,
        name=None,
        tag=None,
        commit=None,
        config: Path = None,
        force=False,
        additional_resources=[],
        conda: bool = None,
    ) -> Workflow:
        """
        Installs a Snakemake workflow as a CLI.
        Args:
          workflow (str): The URL of the repo or the path to the local workflow.
          editable (bool, optional): Whether to install the workflow in editable mode. Defaults to False.
          name (str, optional): The name of the workflow. Defaults to None.
          tag (str, optional): The tag of the workflow. Defaults to None.
          commit (str, optional): The commit SHA of the workflow. Defaults to None.
          config (Path, optional): The path to the config file. Defaults to None.
          force (bool, optional): Whether to force the installation. Defaults to False.
          additional_resources (list, optional): A list of resources additional to the resources folder to copy. Defaults to [].
          conda (bool, optional): Modify the snk config file to control conda use. If None, will not modify the config file. Defaults to None.
        Returns:
          Workflow: The installed workflow.
        Examples:
          >>> nest.install('https://github.com/example/repo.git', name='example', tag='v1.0.0')
          >>> nest.install('https://github.com/example/repo.git', name='example', commit='0123456')
        """

        def handle_force_installation(name: str):
            try:
                self.uninstall(name=name, force=True)
            except WorkflowNotFoundError:
                pass
        workflow = str(workflow) # ensure it is a string
        try:
            workflow = self._format_repo_url(workflow)
            if not name:
                name = self._get_name_from_git_url(workflow)
            if not force:
                self._check_workflow_name_available(name)
            else:
                handle_force_installation(name)
            workflow_path = self.download(workflow, name, tag_name=tag, commit=commit)
        except InvalidWorkflowRepositoryError:
            workflow_local_path = Path(workflow).resolve()
            if workflow_local_path.is_file():
                raise InvalidWorkflowError(
                    f"When installing a local workflow, the path must be a directory. Found: {workflow_local_path}"
                )
            if self.snk_workflows_dir.resolve().is_relative_to(workflow_local_path) and not editable:
                raise InvalidWorkflowError(
                    f"The workflow directory contains SNK_HOME!\nWORKFLOW: {workflow_local_path}\nSNK_HOME: {self.snk_workflows_dir.resolve()}.\n\nTry installing the workflow with --editable."
                )
            if not name:
                name = workflow_local_path.name
            if not force:
                self._check_workflow_name_available(name)
            else:
                handle_force_installation(name)
            workflow_path = self.local(workflow_local_path, name, editable)
        try:
            self.validate_SnakeMake_repo(workflow_path)
            workflow_executable_path = self.create_executable(workflow_path, name)
            self.link_workflow_executable_to_bin(workflow_executable_path)
            if config:
                self.copy_nonstandard_config(workflow_path, config)
            if additional_resources:
                self.additional_resources(workflow_path, additional_resources)
            if conda is not None:
                self.modify_snk_config(workflow_path, conda=conda)
            self._confirm_installation(name)
        except Exception as e:
            # remove any half completed steps
            to_remove = self.get_paths_to_delete(name)
            self.delete_paths(to_remove)
            raise e
        return Workflow(workflow_path)

    def modify_snk_config(self, workflow_path: Path, **kwargs):
        """
        Modify the snk config file.
        Args:
          workflow_path (Path): The path to the workflow directory.
        Examples:
          >>> nest.modify_snk_config(Path('/path/to/workflow'), logo=example)
        """
        snk_config = SnkConfig.from_workflow_dir(
            workflow_path, create_if_not_exists=True
        )
        modified = False
        for key, value in kwargs.items():
            if getattr(snk_config, key) != value:
                modified = True
                setattr(snk_config, key, value)
        if modified:
            snk_config.save()

    def additional_resources(self, workflow_path: Path, resources: List[Path]):
        """
        Modify the snk config file so that resources will be copied at runtime.
        Args:
          workflow_path (Path): The path to the workflow directory.
          resources (List[Path]): A list of additional resources to copy.
        Examples:
          >>> nest.additional_resources(Path('/path/to/workflow'), [Path('/path/to/resource1'), Path('/path/to/resource2')])
        """
        # validate_resources(resources)
        snk_config = SnkConfig.from_workflow_dir(
            workflow_path, create_if_not_exists=True
        )
        snk_config.add_resources(resources, workflow_path)
        snk_config.save()

    def copy_nonstandard_config(self, workflow_dir: Path, config_path: Path):
        """
        Copy a nonstandard config file to the workflow directory.
        Args:
          workflow_dir (Path): The path to the workflow directory.
          config_path (Path): The path to the config file.
        Examples:
          >>> nest.copy_nonstandard_config(Path('/path/to/workflow'), Path('/path/to/config.yaml'))
        """
        config_dir = workflow_dir / "config"
        config_dir.mkdir(exist_ok=True)
        shutil.copyfile(workflow_dir / config_path, config_dir / "config.yaml")

    def get_paths_to_delete(self, workflow_name: str) -> List[Path]:
        """
        Get the paths to delete when uninstalling a workflow.
        Args:
          workflow_name (str): The name of the workflow.
        Returns:
          List[Path]: A list of paths to delete.
        Examples:
          >>> nest.get_paths_to_delete('example')
          [Path('/path/to/workflows/example'), Path('/path/to/bin/example')]
        """
        to_delete = []

        # remove repo
        workflow_dir = self.snk_workflows_dir / workflow_name
        if workflow_dir.exists() and workflow_dir.is_dir():
            to_delete.append(workflow_dir)
        elif workflow_dir.is_symlink():
            # editable
            to_delete.append(workflow_dir)

        workflow_executable = self.snk_executable_dir / workflow_name
        if workflow_executable.exists():
            to_delete.append(workflow_executable)

        # remove link
        workflow_symlink_executable = self.bin_dir / workflow_name
        if workflow_symlink_executable.is_symlink():
            if str(os.readlink(workflow_symlink_executable)) == str(
                workflow_executable
            ):
                to_delete.append(workflow_symlink_executable)

        if not to_delete:
            raise WorkflowNotFoundError(f"Could not find workflow: {workflow_name}")

        return to_delete

    def delete_paths(self, files: List[Path]):
        """
        Delete the given paths.
        Args:
          files (List[Path]): A list of paths to delete.
        Side Effects:
          Deletes the given paths.
        Examples:
          >>> nest.delete_paths([Path('/path/to/workflows/example'), Path('/path/to/bin/example')])
        """
        # check that the files are in self.snk_workflows_dir
        # i.e. if it is a symlink read the link and check
        for path in files:
            if path.is_symlink():
                print("Unlinking:", path)
                path.unlink()
            elif path.is_file():
                print("Deleting:", path)
                assert str(self.snk_home) in str(
                    path
                ), "Cannot delete files outside of SNK_HOME"
                path.unlink()
            elif path.is_dir():
                print("Deleting:", path)
                assert str(self.snk_home) in str(
                    path
                ), "Cannot delete folders outside of SNK_HOME"
                shutil.rmtree(path)
            else:
                raise TypeError("Invalid file type")

    def uninstall(self, name: str, force: bool = False) -> bool:
        """
        Uninstalls a workflow.
        Args:
          name (str): The name of the workflow.
          force (bool, optional): Whether to force the uninstallation. Defaults to False.
        Returns:
          bool: Whether the uninstallation was successful.
        Examples:
          >>> nest.uninstall('example')
          True
        """
        to_remove = self.get_paths_to_delete(name)
        if force:
            proceed = True
        else:
            print(f"Uninstalling {name}")
            print("  Would remove:")
            for p in to_remove:
                print(f"    {p}{'/*' if p.is_dir() else ''}")
            ans = input("Proceed (Y/n)? ")
            proceed = ans.lower() in ["y", "yes"]
        if not proceed:
            return False
        self.delete_paths(to_remove)
        return True

    def _check_workflow_name_available(self, name: str):
        if not name:
            return None
        if name in os.listdir(self.snk_workflows_dir):
            raise WorkflowExistsError(
                f"Workflow '{name}' already exists in SNK_HOME ({self.snk_workflows_dir})"
            )

        if name in os.listdir(self.bin_dir):
            # check if orfan symlink
            def is_orfan_symlink(name):
                return (self.bin_dir / name).is_symlink() and str(
                    self.snk_home
                ) in os.readlink(self.bin_dir / name)

            if is_orfan_symlink(name):
                self.delete_paths([self.bin_dir / name])
            else:
                raise WorkflowExistsError(
                    f"File '{name}' already exists in SNK_BIN ({self.bin_dir})"
                )

    def _confirm_installation(self, name: str):
        """
        Confirms that the installation was successful.
        Args:
          name (str): The name of the workflow.
        Examples:
          >>> nest._confirm_installation('example')
        """
        workflow_dir = self.snk_workflows_dir / name
        assert workflow_dir.exists()
        workflows = [p.name.split(".")[0] for p in self.bin_dir.glob("*")]
        assert name in workflows

    def _get_name_from_git_url(self, git_url: str):
        """
        Gets the name of the workflow from the git URL.
        Args:
          git_url (str): The URL of the git repository.
        Returns:
          str: The name of the workflow.
        """
        return git_url.split("/")[-1].split(".")[0]

    @property
    def workflows(self):
        return [
            Workflow(workflow_dir.absolute())
            for workflow_dir in self.snk_workflows_dir.glob("*")
        ]

    def download(self, repo_url: str, name: str, tag_name: str = None, commit: str = None) -> Path:
        """
        Clone a workflow from a git repository.
        Args:
          url (str): The URL of the file to download.
        Returns:
          None
        Side Effects:
          Downloads the file from the given URL.
        Examples:
          >>> Nest.download('https://example.com/file.txt')
          None
        """
        location = self.snk_workflows_dir / name
        options = []
        if not commit:
            options.append(f"--depth 1")
        if tag_name:
            options.append(f"--single-branch")
            options.append(f"--branch {tag_name}")
        try:
            repo = Repo.clone_from(repo_url, location, multi_options=options)
            if commit:
                repo.git.checkout(commit)
            else:
                repo.git.checkout(tag_name)
        except GitCommandError as e:
            if "destination path" in e.stderr:
                raise WorkflowExistsError(
                    f"Workflow '{name}' already exists in {self.snk_workflows_dir}"
                )
            elif f"Remote branch {tag_name}" in e.stderr:
                raise WorkflowNotFoundError(f"Workflow tag '{tag_name}' not found")
            elif f"pathspec '{commit}' did not match" in e.stderr:
                if tag_name:
                    raise WorkflowNotFoundError(f"Workflow commit '{commit}' not found on branch {tag_name}")
                else:
                    raise WorkflowNotFoundError(f"Workflow commit '{commit}' not found")
            elif "not found" in e.stderr:
                raise WorkflowNotFoundError(
                    f"Workflow repository '{repo_url}' not found"
                )
            raise e
        return location

    def local(self, path: Path, name: str, editable=False) -> Path:
        """
        Install a local workflow.
        Args:
            path (Path): The path to the local workflow.
            name (str): The name of the workflow.
            editable (bool, optional): Whether to install the workflow in editable mode. Defaults to False.
        Returns:
            Path: The path to the installed workflow.
        Examples:
            >>> Nest.local(Path('/path/to/workflow'), 'example')
        """
        location = self.snk_workflows_dir / name
        if editable:
            os.symlink(path.absolute(), location, target_is_directory=True)
            return location
        shutil.copytree(path, location)
        try:
            Repo(location)
        except InvalidGitRepositoryError:
            Repo.init(location, mkdir=False)
        return location

    def create_executable(self, workflow_path: Path, name: str) -> Path:
        template = inspect.cleandoc(
            f"""
            #!/bin/sh
            '''exec' "{self.python_interpreter_path}" "$0" "$@"
            ' '''
            # -*- coding: utf-8 -*-
            import re
            import sys
            from snk import create_cli
            if __name__ == "__main__":
                sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
                sys.exit(create_cli("{workflow_path}"))
                
        """
        )

        if sys.platform.startswith("win"):
            name += ".exe"

        workflow_executable = self.snk_executable_dir / name

        with open(workflow_executable, "w") as f:
            f.write(template)

        workflow_executable.chmod(workflow_executable.stat().st_mode | stat.S_IEXEC)

        return workflow_executable

    def link_workflow_executable_to_bin(self, workflow_executable_path: Path):
        """
        Links a workflow executable to the bin directory.
        Args:
          executable_name (str): The name of the executable to link.
        Returns:
          None
        Side Effects:
          Links a workflow executable to the bin directory.
        Examples:
          >>> Nest.link_workflow_executable_to_bin('my_executable')
        """
        name = workflow_executable_path.name
        if (self.bin_dir / name).is_symlink() and os.readlink(
            self.bin_dir / name
        ) == str(workflow_executable_path):
            # skip if it's already there
            return self.bin_dir / name
        try:
            os.symlink(workflow_executable_path.absolute(), self.bin_dir / name)
        except FileExistsError:
            raise WorkflowExistsError(
                f"File '{name}' already exists in SNK_BIN ({self.bin_dir})"
            )
        return self.bin_dir / name

    def validate_SnakeMake_repo(self, repo: Repo):
        """
        Validates a SnakeMake repository.
        Args:
          repo_path (str): The path to the repository.
        Returns:
          bool: True if the repository is valid, False otherwise.
        Examples:
          >>> Nest.validate_SnakeMake_repo('/path/to/repo')
          True
        """
        # print("Skipping validation!")
        pass
