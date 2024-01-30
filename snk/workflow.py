from pathlib import Path
import sys
from typing import Optional
from git import Repo, InvalidGitRepositoryError


class Workflow:
    """
    Represents a workflow.
    Attributes:
      path (Path): The path to the workflow.
      repo (Repo): The git repository of the workflow.
      name (str): The name of the workflow.
    """

    def __init__(self, path: Path) -> None:
        """
        Initializes a Workflow object.
        Args:
            path (Path): The path to the workflow.
        Returns:
            None
        Notes:
            Initializes the `repo` and `name` attributes.
        """
        self.path = path
        if path.is_symlink():  # editable mode
            self.repo = None
        else:
            try:
                self.repo = Repo(path)
            except InvalidGitRepositoryError:
                self.repo = None
        self.name = self.path.name


    @property
    def tag(self):
        """
        Gets the tag of the workflow.
        Returns:
            str: The tag of the workflow, or None if no tag is found.
        """
        try:
            tag = self.repo.git.describe(["--tags", "--exact-match"])
        except Exception:
            tag = None
        return tag
    
    @property
    def commit(self):
        """
        Gets the commit SHA of the workflow.
        Returns:
            str: The commit SHA of the workflow.
        """
        try:
            sha = self.repo.head.object.hexsha
            commit = self.repo.git.rev_parse(sha, short=8)
        except Exception:
           commit = None
        return commit

    @property
    def version(self):
        """
        Gets the version of the workflow.
        Returns:
            str: The version of the workflow, or None if no version is found.
        """
        version = None
        if version is None:
            if self.tag:
                version = self.tag
            else:
                version = self.commit
        return version

    @property
    def executable(self):
        """
        Gets the executable of the workflow.
        Returns:
            Path: The path to the workflow executable.
        """
        workflow_bin_dir = self.path.parent.parent / "bin"
        name = self.name
        if sys.platform.startswith("win"):
            name += ".exe"
        return workflow_bin_dir / name
    
    @property
    def conda_prefix_dir(self):
        """
        Gets the conda prefix directory of the workflow.
        Returns:
            Path: The path to the conda prefix directory.
        """
        return Path(".snakemake") / "conda" if self.editable else self.path / ".conda"

    @property
    def singularity_prefix_dir(self):
        """
        Gets the singularity prefix directory of the workflow.
        Returns:
            Path: The path to the singularity prefix directory.
        """
        if " " in str(self.path):
            # sigh, snakemake singularity does not support spaces in the path
            # https://github.com/snakemake/snakemake/blob/2ecb21ba04088b9e6850447760f713784cf8b775/snakemake/deployment/singularity.py#L130C1-L131C1
            return None
        return Path(".snakemake") / "singularity" if self.editable else self.path / ".singularity"

    @property
    def editable(self):
        """Is the workflow editable?"""
        return self.path.is_symlink()

    def _find_folder(self, name) -> Optional[Path]:
        """Search for folder"""
        if (self.path / name).exists():
            return self.path / name
        if (self.path / "workflow" / name).exists():
            return self.path / "workflow" / name
        return None

    @property
    def profiles(self):
        workflow_profile_dir = self._find_folder("profiles")
        if workflow_profile_dir:
            return [p for p in workflow_profile_dir.glob("*") if p.is_dir() and (p / "config.yaml").exists()]
        return []

    @property
    def environments(self):
        workflow_environments_dir = self._find_folder("envs")
        if workflow_environments_dir:
            return [e for e in workflow_environments_dir.glob("*.yaml")] + [
                e for e in workflow_environments_dir.glob("*.yml")
            ]
        return []

    @property
    def scripts(self):
        workflow_environments_dir = self._find_folder("scripts")
        if workflow_environments_dir:
            return [s for s in workflow_environments_dir.iterdir() if s.is_file()]
        return []
