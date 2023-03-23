from pathlib import Path
import sys
from git import Repo, GitCommandError

class Pipeline:
    def __init__(self, path:Path) -> None:
        """
        This function takes a path and returns a repository object
        
        :param path: The path to the repository
        :type path: Path
        """
        self.path = path
        self.repo = Repo(path)
        self.name = self.path.name
    
    @property
    def version(self):
        try:
            # TODO: default to commit
            version = self.repo.git.describe(['--tags','--exact-match']) 
        except GitCommandError:
            version = None
        return version

    @property
    def executable(self):
        pipeline_bin_dir = self.path / 'bin'
        name = self.name
        if sys.platform.startswith('win'):
            name += '.exe'
        return pipeline_bin_dir / name
        
