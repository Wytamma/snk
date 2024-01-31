from pathlib import Path
from typing import List, Optional
import snakemake
from dataclasses import dataclass, field
from snk.cli.config.utils import get_version_from_config
from snk.errors import InvalidSnkConfigError, MissingSnkConfigError
import yaml

@dataclass
class SnkConfig:
    """
    A dataclass for storing Snakemake workflow configuration.
    """

    art: str = None
    logo: str = None
    tagline: str = "A Snakemake workflow CLI generated with Snk"
    font: str = "small"
    version: Optional[str] = None
    conda: bool = True
    resources: List[Path] = field(default_factory=list)
    skip_missing: bool = False # skip any missing cli options (i.e. those not in the snk file)
    additional_snakemake_args: List[str] = field(default_factory=list)
    cli: dict = field(default_factory=dict)
    symlink_resources: bool = False
    _snk_config_path: Path = None

    @classmethod
    def from_path(cls, snk_config_path: Path):
        """
        Load and validate Snk config from file.
        Args:
          snk_config_path (Path): Path to the SNK config file.
        Returns:
          SnkConfig: A SnkConfig object.
        Raises:
          FileNotFoundError: If the SNK config file is not found.
        Examples:
          >>> SnkConfig.from_path(Path("snk.yaml"))
          SnkConfig(art=None, logo=None, tagline='A Snakemake workflow CLI generated with Snk', font='small', resources=[], annotations={}, symlink_resources=False, _snk_config_path=PosixPath('snk.yaml'))
        """
        if not snk_config_path.exists():
            raise MissingSnkConfigError(
                f"Could not find SNK config file: {snk_config_path}"
            ) from FileNotFoundError
        # raise error if file is empty
        if snk_config_path.stat().st_size == 0:
            raise InvalidSnkConfigError(f"SNK config file is empty: {snk_config_path}") from ValueError

        snk_config_dict = snakemake.load_configfile(snk_config_path)
        snk_config_dict["version"] = get_version_from_config(snk_config_path, snk_config_dict)
        if "annotations" in snk_config_dict:
            # TODO: remove annotations in the future
            snk_config_dict["cli"] = snk_config_dict["annotations"]
            del snk_config_dict["annotations"]
        if "conda_required" in snk_config_dict:
            # TODO: remove conda_required in the future
            snk_config_dict["conda"] = snk_config_dict["conda_required"]
            del snk_config_dict["conda_required"]
        snk_config = cls(**snk_config_dict)
        snk_config.resources = [
            snk_config_path.parent / resource for resource in snk_config.resources
        ]
        snk_config.validate_resources(snk_config.resources)
        snk_config._snk_config_path = snk_config_path
        return snk_config
  
    @classmethod
    def from_workflow_dir(
        cls, workflow_dir_path: Path, create_if_not_exists: bool = False
    ):
        """
        Load and validate SNK config from workflow directory.
        Args:
          workflow_dir_path (Path): Path to the workflow directory.
          create_if_not_exists (bool): Whether to create a SNK config file if one does not exist.
        Returns:
          SnkConfig: A SnkConfig object.
        Raises:
          FileNotFoundError: If the SNK config file is not found.
        Examples:
          >>> SnkConfig.from_workflow_dir(Path("workflow"))
          SnkConfig(art=None, logo=None, tagline='A Snakemake workflow CLI generated with Snk', font='small', resources=[], annotations={}, symlink_resources=False, _snk_config_path=PosixPath('workflow/snk.yaml'))
        """
        if (workflow_dir_path / "snk.yaml").exists():
            return cls.from_path(workflow_dir_path / "snk.yaml")
        elif (workflow_dir_path / ".snk").exists():
            import warnings

            warnings.warn(
                "Use of .snk will be deprecated in the future. Please use snk.yaml instead.",
                DeprecationWarning,
            )
            return cls.from_path(workflow_dir_path / ".snk")
        elif create_if_not_exists:
            snk_config = cls(_snk_config_path=workflow_dir_path / "snk.yaml")
            return snk_config
        else:
            raise FileNotFoundError(
                f"Could not find SNK config file in workflow directory: {workflow_dir_path}"
            )

    def validate_resources(self, resources):
        """
        Validate resources.
        Args:
          resources (List[Path]): List of resources to validate.
        Raises:
          FileNotFoundError: If a resource is not found.
        Notes:
          This function does not modify the resources list.
        Examples:
          >>> SnkConfig.validate_resources([Path("resource1.txt"), Path("resource2.txt")])
        """
        for resource in resources:
            if not resource.exists():
                raise FileNotFoundError(f"Could not find resource: {resource}")

    def add_resources(self, resources: List[Path], workflow_dir_path: Path = None):
        """
        Add resources to the SNK config.
        Args:
          resources (List[Path]): List of resources to add.
          workflow_dir_path (Path): Path to the workflow directory.
        Returns:
          None
        Side Effects:
          Adds the resources to the SNK config.
        Examples:
          >>> snk_config = SnkConfig()
          >>> snk_config.add_resources([Path("resource1.txt"), Path("resource2.txt")], Path("workflow"))
        """
        processed = []
        for resource in resources:
            if workflow_dir_path and not resource.is_absolute():
                resource = workflow_dir_path / resource
            processed.append(resource)
        self.validate_resources(processed)
        self.resources.extend(processed)

    def to_yaml(self, path: Path) -> None:
        """
        Write SNK config to YAML file.
        Args:
          path (Path): Path to write the YAML file to.
        Returns:
          None
        Side Effects:
          Writes the SNK config to the specified path.
        Examples:
          >>> snk_config = SnkConfig()
          >>> snk_config.to_yaml(Path("snk.yaml"))
        """
        config_dict = {k: v for k, v in vars(self).items() if not k.startswith("_")}
        with open(path, "w") as f:
            yaml.dump(config_dict, f)

    def save(self) -> None:
        """
        Save SNK config.
        Args:
          path (Path): Path to write the YAML file to.
        Returns:
          None
        Side Effects:
          Writes the SNK config to the path specified by _snk_config_path.
        Examples:
          >>> snk_config = SnkConfig()
          >>> snk_config.save()
        """
        self.to_yaml(self._snk_config_path)


def get_config_from_workflow_dir(workflow_dir_path: Path):
    """
    Get the config file from a workflow directory.
    Args:
      workflow_dir_path (Path): Path to the workflow directory.
    Returns:
      Path: Path to the config file, or None if not found.
    Examples:
      >>> get_config_from_workflow_dir(Path("workflow"))
      PosixPath('workflow/config.yaml')
    """
    for path in [
        Path("config") / "config.yaml",
        Path("config") / "config.yml",
        "config.yaml",
        "config.yml",
    ]:
        if (workflow_dir_path / path).exists():
            return workflow_dir_path / path
    return None


def load_workflow_snakemake_config(workflow_dir_path: Path):
    """
    Load the Snakemake config from a workflow directory.
    Args:
      workflow_dir_path (Path): Path to the workflow directory.
    Returns:
      dict: The Snakemake config.
    Examples:
      >>> load_workflow_snakemake_config(Path("workflow"))
      {'inputs': {'data': 'data.txt'}, 'outputs': {'results': 'results.txt'}}
    """
    workflow_config_path = get_config_from_workflow_dir(workflow_dir_path)
    if not workflow_config_path or not workflow_config_path.exists():
        return {}
    return snakemake.load_configfile(workflow_config_path)
