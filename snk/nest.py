from pathlib import Path
from git import InvalidGitRepositoryError, Repo, GitCommandError
import sys
import stat
import inspect
import os
from typing import List
import shutil
import yaml

from .errors import PipelineExistsError, PipelineNotFoundError, InvalidPipelineRepositoryError
from .cli.config import SnkConfig
from .cli.pipeline import Pipeline


class Nest:
    """Class for managing Snk pipelines"""

    def __init__(self, snk_home: Path = None, bin_dir: Path = None) -> None:
        self.python_interpreter_path = Path(sys.executable) # needs to be the same python that has snk
        
        if not snk_home:
            home_path = self.python_interpreter_path.parent.parent
            if not os.access(home_path, os.W_OK):
                user_home_path = Path('~').expanduser()
                snk_home = user_home_path / ".local" / 'snk'
            else:
                snk_home = home_path / 'snk'

        if not bin_dir:
            bin_dir = self.python_interpreter_path.parent
            if not os.access(bin_dir, os.W_OK):
                user_home_path = Path('~').expanduser()
                bin_dir = user_home_path / ".local" / 'bin'

        self.snk_home = Path(snk_home).absolute()
        self.pipelines_dir = self.snk_home / "pipelines"
        self.bin_dir = Path(bin_dir).absolute()
        
        # Create dirs
        self.snk_home.mkdir(parents=True, exist_ok=True)
        self.pipelines_dir.mkdir(parents=True, exist_ok=True)
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def _check_repo_url_format(self, repo: str):
        if not repo.startswith('http'):
            raise InvalidPipelineRepositoryError('Repo url must start with http')
        if not repo.endswith('.git'):
            raise InvalidPipelineRepositoryError('Repo url must end in .git')

    def install(self, pipeline: str, editable = False, name = None, tag = None, config: Path = None, force = False, resources=[]) -> Pipeline:
        """
        Install a Snakemake pipeline as a CLI. 
        They must be standards compliant*, public, Snakemake workflows.
        https://snakemake.github.io/snakemake-workflow-catalog/
        """
        try:
            self._check_repo_url_format(pipeline)
            if not name:
                name = self._get_name_from_git_url(pipeline)
            if name in os.listdir(self.pipelines_dir):
                raise PipelineExistsError(f"Pipeline '{name}' already exists in {self.pipelines_dir}")
            if name in os.listdir(self.bin_dir):
                raise PipelineExistsError(f"Pipeline '{name}' already exists in {self.bin_dir}")
            repo = self.download(pipeline, name, tag_name=tag)
        except InvalidPipelineRepositoryError:
            pipeline = Path(pipeline)
            if pipeline.suffix == '.snk':
                pipeline = pipeline.parent
            if not name:
                name = pipeline.name
            repo = self.local(pipeline, name, editable)
        try:
            pipeline = Pipeline(path=Path(repo.git_dir).parent)
            pipeline_executable = self.create_package(pipeline.path)
            self.link_pipeline_executable_to_bin(pipeline_executable)
            if config:
                self.copy_nonstandard_config(pipeline.path, config)
            if resources:
                self.additional_resources(pipeline.path, resources)
            self._confirm_installation(name)
        except Exception as e:
            # remove any half completed steps 
            to_remove = self.get_paths_to_delete(name)
            self.delete_paths(to_remove)
            raise e
        return pipeline
    
    def additional_resources(self, pipeline_dir: Path, resources: List[Path]):
        """Modify the .snk file so that resources will be copied at runtime."""
        # validate_resources(resources)
        snk_config = SnkConfig.from_path(pipeline_dir / '.snk')
        snk_config.resources += [r for r in resources if r not in snk_config.resources]
        snk_config.to_yaml(pipeline_dir / '.snk')

    def copy_nonstandard_config(self, pipeline_dir: Path, config_path: Path):
        config_dir = pipeline_dir / 'config'
        config_dir.mkdir()
        shutil.copyfile(pipeline_dir / config_path, config_dir / 'config.yaml')

    def get_paths_to_delete(self, pipeline_name: str) -> List[Path]:
        to_delete = []
        
        # remove repo 
        pipeline_dir = self.pipelines_dir / pipeline_name
        if pipeline_dir.exists() and pipeline_dir.is_dir():
            to_delete.append(pipeline_dir)
        else:
            raise PipelineNotFoundError(f'Could not find pipeline: {pipeline_name}')

        # remove link
        pipeline_bin_executable = self.bin_dir / pipeline_name
        if pipeline_bin_executable.exists() and pipeline_bin_executable.is_symlink():
            if str(pipeline_dir) in str(os.readlink(pipeline_bin_executable)):
                to_delete.append(pipeline_bin_executable)
        
        return to_delete

    def delete_paths(self, files: List[Path]):
        # check that the files are in self.pipelines_dir
        # i.e. if it is a symlink read the link and check
        for path in files:
            if path.is_dir():
                assert str(self.snk_home) in str(path), "Cannot delete folders outside of SNK_HOME"
                shutil.rmtree(path)
            elif path.is_symlink():
                assert str(self.snk_home) in str(os.readlink(path)), "Cannot delete files outside of SNK_HOME"
                path.unlink()
            else:
                raise TypeError("Invalid file type")

    def uninstall(self, name: str, force: bool = False) -> bool:
        to_remove = self.get_paths_to_delete(name)
        if force:
            proceed = True
        else:
            print(f"Uninstalling {name}")
            print("  Would remove:")
            for p in to_remove:
                print(f"    {p}{'/*' if p.is_dir() else ''}")
            ans = input("Proceed (Y/n)? ")
            proceed = ans.lower() in ['y', 'yes']
        if not proceed:
            return False
        self.delete_paths(to_remove)
        return True 

    def _confirm_installation(self, name: str):
        pipeline_dir = self.pipelines_dir / name
        assert pipeline_dir.exists()
        pipelines = [p.name.split('.')[0] for p in self.bin_dir.glob('*')]
        assert name in pipelines

    def _get_name_from_git_url(self, git_url: str):
        return git_url.split('/')[-1].split('.')[0]

    @property
    def pipelines(self):
        return [Pipeline(pipeline_dir.resolve()) for pipeline_dir in self.pipelines_dir.glob('*') if pipeline_dir.is_dir()]

    def download(self, repo_url: str, name: str, tag_name: str = None) -> Repo:
        """Pull the repo"""
        location  = self.pipelines_dir / name
        options = ['--depth 1', '--single-branch']
        if tag_name:
            options.append(f'--branch {tag_name}')
        try:
            repo = Repo.clone_from(repo_url, location, multi_options=options)
            repo.git.checkout(tag_name)
        except GitCommandError as e:
            if "destination path" in e.stderr:
                raise PipelineExistsError(f"Pipeline '{name}' already exists in {self.pipelines_dir}")
            elif f"Remote branch {tag_name}" in e.stderr:
                raise PipelineNotFoundError(f"Pipeline tag '{tag_name}' not found")
            elif "not found" in e.stderr:
                raise PipelineNotFoundError(f"Pipeline repository '{repo_url}' not found")
            raise e
        return repo
    
    def local(self, path: Path, name: str, editable=False):
        location  = self.pipelines_dir / name
        if editable:
            os.symlink(path, location)
        else:
            shutil.copytree(path, location)
        try:
            return Repo(location)
        except InvalidGitRepositoryError:
            return Repo.init(location, mkdir=False)
        


    def create_package(self, pipeline_dir: Path) -> Path:
        """Convert a SnakeMake pipeline repo into a snk CLI"""
        self.validate_SnakeMake_repo(pipeline_dir)
        
        template = inspect.cleandoc(f"""
            #!/bin/sh
            '''exec' "{self.python_interpreter_path}" "$0" "$@"
            ' '''
            # -*- coding: utf-8 -*-
            import re
            import sys
            from snk import create_cli
            if __name__ == "__main__":
                sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
                sys.exit(create_cli("{pipeline_dir}"))
                
        """)

        pipeline_bin_dir = pipeline_dir / 'bin'
        pipeline_bin_dir.mkdir(exist_ok=True)

        name = pipeline_dir.name

        if sys.platform.startswith('win'):
            name += '.exe'
        
        pipeline_executable = pipeline_bin_dir / name

        with open(pipeline_executable, 'w') as f:
            f.write(template)

        pipeline_executable.chmod(pipeline_executable.stat().st_mode | stat.S_IEXEC)

        return pipeline_executable

    def link_pipeline_executable_to_bin(self, pipeline_executable_path: Path):
        name = pipeline_executable_path.name
        os.symlink(pipeline_executable_path.absolute(), self.bin_dir / name)
        return self.bin_dir / name

    def validate_SnakeMake_repo(self, repo: Repo):
        print("Skipping validation!")
        pass