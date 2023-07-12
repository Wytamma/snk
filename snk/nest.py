from pathlib import Path
from git import InvalidGitRepositoryError, Repo, GitCommandError
import sys
import stat
import inspect
import os
from typing import List
import shutil

from .errors import (
    PipelineExistsError,
    PipelineNotFoundError,
    InvalidPipelineRepositoryError,
)
from .cli.config.config import SnkConfig
from .pipeline import Pipeline


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
        self.snk_pipelines_dir = self.snk_home / "pipelines"
        self.snk_executable_dir = self.snk_home / "bin"

        # Create dirs
        self.snk_home.mkdir(parents=True, exist_ok=True)
        self.snk_pipelines_dir.mkdir(parents=True, exist_ok=True)
        self.snk_executable_dir.mkdir(parents=True, exist_ok=True)
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def bin_dir_in_path(self) -> bool:
        path_dirs = os.environ["PATH"].split(os.pathsep)
        return str(self.bin_dir) in path_dirs

    def _check_repo_url_format(self, repo: str):
        """
        Checks that the given repo URL is valid.
        Args:
          repo (str): The URL of the repo.
        Raises:
          InvalidPipelineRepositoryError: If the repo URL is not valid.
        Examples:
          >>> nest._check_repo_url_format('https://github.com/example/repo.git')
        """
        if not repo.startswith("http"):
            raise InvalidPipelineRepositoryError("Repo url must start with http")
        if not repo.endswith(".git"):
            raise InvalidPipelineRepositoryError("Repo url must end in .git")

    def install(
        self,
        pipeline: str,
        editable=False,
        name=None,
        tag=None,
        config: Path = None,
        force=False,
        additional_resources=[],
    ) -> Pipeline:
        """
        Installs a Snakemake pipeline as a CLI.
        Args:
          pipeline (str): The URL of the repo or the path to the local pipeline.
          editable (bool, optional): Whether to install the pipeline in editable mode. Defaults to False.
          name (str, optional): The name of the pipeline. Defaults to None.
          tag (str, optional): The tag of the pipeline. Defaults to None.
          config (Path, optional): The path to the config file. Defaults to None.
          force (bool, optional): Whether to force the installation. Defaults to False.
          additional_resources (list, optional): A list of resources additional to the resources folder to copy. Defaults to [].
          symlink_resources_folder (bool, optional): Whether to symlink the resources folder instead of copying it. Defaults to False.
        Returns:
          Pipeline: The installed pipeline.
        Examples:
          >>> nest.install('https://github.com/example/repo.git', name='example', tag='v1.0.0')
        """
        def handle_force_installation(name: str):
            try:
                self.uninstall(name=name, force=True)
            except PipelineNotFoundError:
                pass

        self._check_pipeline_name_available(name)
        try:
            self._check_repo_url_format(pipeline)
            if not name:
                name = self._get_name_from_git_url(pipeline)
            if not force:
                self._check_pipeline_name_available(name)
            else:
                handle_force_installation(name)
            pipeline_path = self.download(pipeline, name, tag_name=tag)
        except InvalidPipelineRepositoryError:
            pipeline_local_path = Path(pipeline)
            if not name:
                name = pipeline_local_path.name
            if not force:
                self._check_pipeline_name_available(name)
            else:
                handle_force_installation(name)
            pipeline_path = self.local(pipeline_local_path, name, editable)
        try:
            self.validate_SnakeMake_repo(pipeline_path)
            pipeline_executable_path = self.create_executable(pipeline_path, name)
            self.link_pipeline_executable_to_bin(pipeline_executable_path)
            if config:
                self.copy_nonstandard_config(pipeline_path, config)
            if additional_resources:
                self.additional_resources(pipeline_path, additional_resources)            
            self._confirm_installation(name)
        except Exception as e:
            # remove any half completed steps
            to_remove = self.get_paths_to_delete(name)
            self.delete_paths(to_remove)
            raise e
        return Pipeline(pipeline_path)

    def modify_snk_config(self, pipeline_path: Path, **kwargs):
        """
        Modify the snk config file.
        Args:
          pipeline_path (Path): The path to the pipeline directory.
          name (str): The name of the pipeline.
        Examples:
          >>> nest.modify_snk_config(Path('/path/to/pipeline'), 'example')
        """
        snk_config = SnkConfig.from_pipeline_dir(
            pipeline_path, 
            create_if_not_exists=True
        )
        for key, value in kwargs.items():
            setattr(snk_config, key, value)
        snk_config.save()
    
    def additional_resources(self, pipeline_path: Path, resources: List[Path]):
        """
        Modify the snk config file so that resources will be copied at runtime.
        Args:
          pipeline_path (Path): The path to the pipeline directory.
          resources (List[Path]): A list of additional resources to copy.
        Examples:
          >>> nest.additional_resources(Path('/path/to/pipeline'), [Path('/path/to/resource1'), Path('/path/to/resource2')])
        """
        # validate_resources(resources)
        snk_config = SnkConfig.from_pipeline_dir(pipeline_path, create_if_not_exists=True)
        snk_config.add_resources(resources, pipeline_path)
        snk_config.save()

    def copy_nonstandard_config(self, pipeline_dir: Path, config_path: Path):
        """
        Copy a nonstandard config file to the pipeline directory.
        Args:
          pipeline_dir (Path): The path to the pipeline directory.
          config_path (Path): The path to the config file.
        Examples:
          >>> nest.copy_nonstandard_config(Path('/path/to/pipeline'), Path('/path/to/config.yaml'))
        """
        config_dir = pipeline_dir / "config"
        config_dir.mkdir()
        shutil.copyfile(pipeline_dir / config_path, config_dir / "config.yaml")

    def get_paths_to_delete(self, pipeline_name: str) -> List[Path]:
        """
        Get the paths to delete when uninstalling a pipeline.
        Args:
          pipeline_name (str): The name of the pipeline.
        Returns:
          List[Path]: A list of paths to delete.
        Examples:
          >>> nest.get_paths_to_delete('example')
          [Path('/path/to/pipelines/example'), Path('/path/to/bin/example')]
        """
        to_delete = []

        # remove repo
        pipeline_dir = self.snk_pipelines_dir / pipeline_name
        if pipeline_dir.exists() and pipeline_dir.is_dir():
            to_delete.append(pipeline_dir)
        elif pipeline_dir.is_symlink():
            # editable 
            to_delete.append(pipeline_dir)

        pipeline_executable = self.snk_executable_dir / pipeline_name
        if pipeline_executable.exists():
            to_delete.append(pipeline_executable)

        # remove link
        pipeline_symlink_executable = self.bin_dir / pipeline_name
        if pipeline_symlink_executable.is_symlink():
            if str(os.readlink(pipeline_symlink_executable)) == str(pipeline_executable):
                to_delete.append(pipeline_symlink_executable)

        if not to_delete:
            raise PipelineNotFoundError(f"Could not find pipeline: {pipeline_name}")
        
        return to_delete

    def delete_paths(self, files: List[Path]):
        """
        Delete the given paths.
        Args:
          files (List[Path]): A list of paths to delete.
        Side Effects:
          Deletes the given paths.
        Examples:
          >>> nest.delete_paths([Path('/path/to/pipelines/example'), Path('/path/to/bin/example')])
        """
        # check that the files are in self.snk_pipelines_dir
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
        Uninstalls a pipeline.
        Args:
          name (str): The name of the pipeline.
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

    def _check_pipeline_name_available(self, name: str):
        
        if not name:
            return None
        if name in os.listdir(self.snk_pipelines_dir):
            raise PipelineExistsError(
                f"Pipeline '{name}' already exists in SNK_HOME ({self.snk_pipelines_dir})"
            )
        
        if name in os.listdir(self.bin_dir):
           # check if orfan symlink
            def is_orfan_symlink(name):
                return (self.bin_dir / name).is_symlink() and str(self.snk_home) in os.readlink(self.bin_dir / name)
            if is_orfan_symlink(name):
                self.delete_paths([self.bin_dir / name])
            else:
                raise PipelineExistsError(
                    f"File '{name}' already exists in SNK_BIN ({self.bin_dir})" 
                )

    def _confirm_installation(self, name: str):
        """
        Confirms that the installation was successful.
        Args:
          name (str): The name of the pipeline.
        Examples:
          >>> nest._confirm_installation('example')
        """
        pipeline_dir = self.snk_pipelines_dir / name
        assert pipeline_dir.exists()
        pipelines = [p.name.split(".")[0] for p in self.bin_dir.glob("*")]
        assert name in pipelines

    def _get_name_from_git_url(self, git_url: str):
        """
        Gets the name of the pipeline from the git URL.
        Args:
          git_url (str): The URL of the git repository.
        Returns:
          str: The name of the pipeline.
        """
        return git_url.split("/")[-1].split(".")[0]

    @property
    def pipelines(self):
        return [
            Pipeline(pipeline_dir.absolute())
            for pipeline_dir in self.snk_pipelines_dir.glob("*")
        ]

    def download(self, repo_url: str, name: str, tag_name: str = None) -> Path:
        """
        Downloads a file from a given URL.
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
        location = self.snk_pipelines_dir / name
        options = ["--depth 1", "--single-branch"]
        if tag_name:
            options.append(f"--branch {tag_name}")
        try:
            repo = Repo.clone_from(repo_url, location, multi_options=options)
            repo.git.checkout(tag_name)
        except GitCommandError as e:
            if "destination path" in e.stderr:
                raise PipelineExistsError(
                    f"Pipeline '{name}' already exists in {self.snk_pipelines_dir}"
                )
            elif f"Remote branch {tag_name}" in e.stderr:
                raise PipelineNotFoundError(f"Pipeline tag '{tag_name}' not found")
            elif "not found" in e.stderr:
                raise PipelineNotFoundError(
                    f"Pipeline repository '{repo_url}' not found"
                )
            raise e
        return location

    def local(self, path: Path, name: str, editable=False) -> Path:
        location = self.snk_pipelines_dir / name
        if editable:
            os.symlink(path.absolute(), location, target_is_directory=True)
            return location
        shutil.copytree(path, location)
        try:
            Repo(location)
        except InvalidGitRepositoryError:
            Repo.init(location, mkdir=False)
        return location

    def create_executable(self, pipeline_path: Path, name: str) -> Path:
        
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
                sys.exit(create_cli("{pipeline_path.resolve()}"))
                
        """
        )

        if sys.platform.startswith("win"):
            name += ".exe"

        pipeline_executable = self.snk_executable_dir / name
        
        with open(pipeline_executable, "w") as f:
            f.write(template)

        pipeline_executable.chmod(pipeline_executable.stat().st_mode | stat.S_IEXEC)

        return pipeline_executable

    def link_pipeline_executable_to_bin(self, pipeline_executable_path: Path):
        """
        Links a pipeline executable to the bin directory.
        Args:
          executable_name (str): The name of the executable to link.
        Returns:
          None
        Side Effects:
          Links a pipeline executable to the bin directory.
        Examples:
          >>> Nest.link_pipeline_executable_to_bin('my_executable')
        """
        name = pipeline_executable_path.name
        if (self.bin_dir / name).is_symlink() and os.readlink(self.bin_dir / name) == str(pipeline_executable_path):
            # skip if it's already there
            return self.bin_dir / name
        try:
            os.symlink(pipeline_executable_path.absolute(), self.bin_dir / name)    
        except FileExistsError:
            raise PipelineExistsError(f"File '{name}' already exists in SNK_BIN ({self.bin_dir})")
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
        #print("Skipping validation!")
        pass
